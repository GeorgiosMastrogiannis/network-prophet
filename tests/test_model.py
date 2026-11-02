import pytest
import ipaddress

from dataclasses import FrozenInstanceError
from network_guardian.model import Subnet

def test_subnet_creation():
    subnet = Subnet(
        address="oci_core_subnet.production",
        vcn_id="vcn-123",
        cidr=ipaddress.ip_network("10.0.1.0/24")
    )

    assert subnet.address == "oci_core_subnet.production"
    assert subnet.vcn_id == "vcn-123"
    assert subnet.cidr == ipaddress.ip_network("10.0.1.0/24")

def test_frozen_error():
    subnet = Subnet(
        address="oci_core_subnet.production",
        vcn_id="vcn-123",
        cidr=ipaddress.ip_network("10.0.1.0/24")
    )
    
    with pytest.raises(FrozenInstanceError):
        subnet.vcn_id = "vcn-345" 
