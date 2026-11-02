"""Your first implementation exercise; see README.md."""

import ipaddress

def cidrs_overlap(left: str, right: str) -> bool:
    left_network = ipaddress.ip_network(left)
    right_network = ipaddress.ip_network(right)
    
    return left_network.overlaps(right_network)
