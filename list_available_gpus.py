from google.cloud import compute_v1
project_id = "core-verbena-328218"

def list_available_gpus():
    """Tests for available GPU in at least 10 zones and returns information.

    Returns:
        A list of dictionaries containing GPU type name and zone information.
    """
    accelerator_client = compute_v1.AcceleratorTypesClient()
    zone_client = compute_v1.ZonesClient()
    zones = zone_client.list(project=project_id)

    available_gpus = []
    for zone_counter, zone in enumerate(zones):
        if zone_counter >= 10:
            break
        zone_name = zone.name
        accelerators = accelerator_client.list(project=project_id, zone=zone_name)
        for accelerator_type in accelerators:
            available_gpus.append({"name": accelerator_type.name, "zone": zone_name})

    return available_gpus

available_gpus = list_available_gpus()
print(available_gpus)
