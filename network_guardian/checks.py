from network_guardian.model import Subnet
import itertools

def find_subnet_overlaps(subnets: list[Subnet],) -> list[tuple[str, str]]:
    overlaps = []

    for left, right in itertools.combinations(subnets, 2):
        if left.vcn_id == right.vcn_id and left.cidr.overlaps(right.cidr):
            pair = tuple(sorted((left.address, right.address)))
            overlaps.append(pair)
    
    return sorted(overlaps)
