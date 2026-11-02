from dataclasses import dataclass
import ipaddress

@dataclass(frozen=True)
class Subnet:
    address: str
    vcn_id: str
    cidr: ipaddress.IPv4Network
