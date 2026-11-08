from network_guardian.plan import Snapshots
from network_guardian.model import subnet_from_resource, UnknownSubnetError
from network_guardian.checks import find_subnet_overlaps

def analyze_overlaps(snapshots: Snapshots) -> dict:
    incomplete = []
    results = {}

    for snapshot_name, resources in(
        ("before", snapshots.before),
        ("after", snapshots.after),
    ):
        subnets = []
        for resource in resources:
            if resource.kind != "oci_core_subnet":
                continue
            
            try:
                subnet = subnet_from_resource(resource)
                subnets.append(subnet)
            except UnknownSubnetError as exc:
                incomplete.append({
                    "snapshot": snapshot_name, 
                    "address": resource.address, 
                    "reason": str(exc)
                })

        results[snapshot_name] = find_subnet_overlaps(subnets)

    return {
        "before": results["before"],
        "after": results["after"],
        "incomplete": incomplete,
    }
