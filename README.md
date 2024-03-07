## Cloud and Machine Learning HW: gpu-chase
This Python script automates the process of creating and deploying a Virtual Machine (VM) instance with an attached GPU on Google Cloud Platform (GCP). The script generates a unique identifier for each VM instance to ensure a distinct name, leveraging the universally unique identifier (UUID) for this purpose. 

It defines functions for listing available zones where the specified GPU type is available, creating a VM instance with the desired specifications, and checking the operational status of the VM. 

The create_instance_with_gpu function is central to this script, allowing users to specify details such as the project ID, zone, instance name, machine type, boot disk image, GPU type, and the number of GPUs to attach. It configures the boot disk, machine type, network interface, GPU, scheduling options, and metadata to automatically install NVIDIA drivers on the VM instance. The script utilizes the Google Cloud Python client library (google-cloud-compute) for interaction with the Compute Engine API, facilitating the creation and management of VM instances programmatically. 

After attempting to create a VM instance in each available zone until success or a specified limit is reached, the script concludes by reporting the outcome of the VM creation process, including the operational status and any encountered errors. This automation streamlines the deployment of GPU-accelerated VM instances for computational tasks, making it an invaluable tool for developers and researchers working in cloud-based environments. 

After running gpu_chase.py, run these commands in the cloud shell:
```
gcloud compute ssh {instance_name} --zone {zone} --project {project_id}
nvidia-smi
gcloud compute instances delete {instance_name} --zone {zone} --project {project_id}

```
