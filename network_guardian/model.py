from dataclasses import dataclass
import ipaddress
from network_guardian.plan import Resource

@dataclass(frozen=True)
class Subnet:
    address: str
    vcn_id: str
    cidr: ipaddress.IPv4Network

class UnknownSubnetError(ValueError):
    """Required subnet information is not known yet."""

def subnet_from_resource(resource: Resource) -> Subnet:    
    if resource.kind != "oci_core_subnet":
        raise ValueError("Resource is not an OCI subnet")
    
    if resource.unknown is True:
        raise UnknownSubnetError("Subnet information is unknown")
    
    if isinstance(resource.unknown, dict):
        if resource.unknown.get("vcn_id") is True or resource.unknown.get("cidr_block") is True:
            raise UnknownSubnetError("Subnet VCN or CIDR is unknown")

    vcn_id = resource.values["vcn_id"]
    cidr_block = resource.values["cidr_block"]
    network = ipaddress.ip_network(cidr_block)
    
    if network.version != 4:
        raise ValueError("IPv6 networks are not supported")

    return Subnet(
        address=resource.address,
        vcn_id=vcn_id,
        cidr=network
    )
