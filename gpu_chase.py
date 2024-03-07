import uuid
from google.cloud import compute_v1
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import time
import subprocess

credentials = GoogleCredentials.get_application_default()
service = discovery.build('compute', 'v1', credentials=credentials)


random_id = uuid.uuid4()  # Generate a random UUID.
short_id = str(random_id)[:8]

project_id = "core-verbena-328218"
gpu_type = "nvidia-tesla-t4"
instance_name = "bm3291-trial-gpu" + short_id


def list_available_zones(gpu_type: str):
    """Tests if given gpu type is available in the zones and returns information.

    Returns:
        A list of dictionaries containing zone information where the given gpu type was available.
    """
    accelerator_client = compute_v1.AcceleratorTypesClient()
    zone_client = compute_v1.ZonesClient()
    zones = zone_client.list(project=project_id)

    available_zones = []

    for zone in zones:
        zone_name = zone.name
        accelerators = accelerator_client.list(
            project=project_id, zone=zone_name)
        for accelerator_type in accelerators:
            if accelerator_type.name == gpu_type:
                available_zones.append(zone_name)

    return available_zones

# available_zones = list_available_gpus(gpu_type)
# print(available_zones)


def create_instance_with_gpu(project_id, zone, name, machine_type, image_name, image_project, disk_size, gpu_type, gpu_count):
    """
    Create a VM instance with an attached GPU in Google Cloud Platform.

    Args:
    - project_id: Your GCP project ID.
    - zone: The zone to deploy the VM instance in.
    - name: Name of the VM instance.
    - machine_type: Type of machine to use (e.g., "n1-standard-4").
    - image_name: Name of the image for the VM's boot disk.
    - image_project: Project that the boot disk image belongs to.
    - disk_size: Size of the boot disk (in GB).
    - gpu_type: Type of GPU to attach (e.g., "nvidia-tesla-t4").
    - gpu_count: Number of GPUs to attach.
    """

    # Initialize the Compute Engine client
    compute_client = compute_v1.InstancesClient()

    # Configure the boot disk
    disk = compute_v1.AttachedDisk()
    disk.initialize_params.source_image = f"projects/{image_project}/global/images/{image_name}"
    disk.auto_delete = True
    disk.boot = True
    disk.initialize_params.disk_size_gb = disk_size

    # Configure the machine type
    machine_type_full_path = f"projects/{project_id}/zones/{zone}/machineTypes/{machine_type}"

    # Configure the network interface
    # network_interface = compute_v1.NetworkInterface()
    # network_interface.network = "global/networks/default"

    # Configure the GPU
    guest_accelerator = compute_v1.AcceleratorConfig()
    guest_accelerator.accelerator_count = gpu_count
    guest_accelerator.accelerator_type = f"projects/{project_id}/zones/{zone}/acceleratorTypes/{gpu_type}"

    # Configure instance scheduling
    scheduling = compute_v1.Scheduling()
    scheduling.on_host_maintenance = "TERMINATE"
    scheduling.automatic_restart = True

    access_config = compute_v1.AccessConfig()
    access_config.name = "External NAT"
    access_config.type = "ONE_TO_ONE_NAT"
    access_config.network_tier = "STANDARD"

    network_interface = compute_v1.NetworkInterface()
    network_interface.network = "global/networks/default"
    network_interface.access_configs = [access_config]

    # Assemble the instance configuration
    instance = compute_v1.Instance()
    instance.name = name
    instance.disks = [disk]
    instance.machine_type = machine_type_full_path
    instance.network_interfaces = [network_interface]
    instance.guest_accelerators = [guest_accelerator]
    instance.scheduling = scheduling
    instance.metadata = {
        "items": [{"key": "install-nvidia-driver", "value": "True"}]}

    # Execute the request to create the VM
    operation = compute_client.insert(
        project=project_id, zone=zone, instance_resource=instance)

    return operation.name


def test_vm_running(project_id, zone, name):
    """Test whether a VM created is running"""
    operation_name = create_instance_with_gpu(project_id=project_id,
                                              zone=zone,
                                              name=instance_name,
                                              machine_type="n1-standard-4",
                                              image_name="tf2-2-7-cu113-v20211202-debian-10",
                                              image_project="deeplearning-platform-release",
                                              disk_size=100,
                                              gpu_type="nvidia-tesla-t4",
                                              gpu_count=1)

    print(f"Operation to create VM {name} started: {operation_name}")

    while True:
        result = service.zoneOperations().get(project=project_id, zone=zone,
                                              operation=operation_name).execute()

        if result['status'] == 'DONE':
            print("The VM creation operation is completed.")
            if 'error' in result:
                print("But with errors:", result['error'])
                return result['error']['errors'][0]['code']
            break
        else:
            print("Waiting for the operation to complete...")
            # Sleep for a bit before checking the operation status again
            time.sleep(10)


def check_vm_for_all_zones():
    """Iterate through all zones to check which in which zone we can able to create VM with GPU"""
    zone_counter = 0
    available_zones = list_available_zones(gpu_type)
    for zone in available_zones:
        if zone_counter >= 10:
            print(f"VM {instance_name} creation unsuccessful")
            break
        status = test_vm_running(project_id, zone, instance_name)
        if status == 'ZONE_RESOURCE_POOL_EXHAUSTED' or status == 'QUOTA_EXCEEDED':
            zone_counter += 1
        else:
            print(f"VM {instance_name} up and running in {zone}")
            break


check_vm_for_all_zones()
