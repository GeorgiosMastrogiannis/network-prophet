import pytest
import ipaddress

from dataclasses import FrozenInstanceError
from network_guardian.model import Subnet
from network_guardian.plan import Resource
from network_guardian.model import subnet_from_resource
from network_guardian.model import UnknownSubnetError

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

def test_subnet_from_resource():
    resource = Resource(
        address="oci_core_subnet.app",
        kind="oci_core_subnet",
        values={
            "vcn_id": "ocid1.vcn.example",
            "cidr_block": "10.0.1.0/24",
        },
        unknown={},
    )

    subnet = subnet_from_resource(resource)
    
    assert subnet.address == "oci_core_subnet.app"
    assert subnet.vcn_id == "ocid1.vcn.example"
    assert subnet.cidr == ipaddress.IPv4Network("10.0.1.0/24")

# wrong resource type
def test_subnet_wrong_resource_type():
    resource = Resource(
        address="oci_core_subnet.app",
        kind="aws_core_subnet",
        values={
            "vcn_id": "ocid1.vcn.example",
            "cidr_block": "10.0.1.0/24",
        },
        unknown={},
    )
    
    with pytest.raises(ValueError):
        subnet_from_resource(resource)

# IPv6 CIDR
def test_subnet_ipv6_rejected():
    resource = Resource(
        address="oci_core_subnet.app",
        kind="oci_core_subnet",
        values={
            "vcn_id": "ocid1.vcn.example",
            "cidr_block": "2001:db8::/32",
        },
        unknown={},
    )
    
    with pytest.raises(ValueError):
        subnet_from_resource(resource)

# hosts bits set
def test_subnet_host_bits_rejected():
    resource = Resource(
        address="oci_core_subnet.app",
        kind="oci_core_subnet",
        values={
            "vcn_id": "ocid1.vcn.example",
            "cidr_block": "10.0.1.6/24",
        },
        unknown={},
    )
    
    with pytest.raises(ValueError):
        subnet_from_resource(resource)

def test_subnet_resource_unknown():
    resource = Resource(
        address="oci_core_subnet.app",
        kind="oci_core_subnet",
        values={
            "vcn_id": "ocid1.vcn.example",
            "cidr_block": "10.0.1.0/24",
        },
        unknown=True,
    )

    with pytest.raises(UnknownSubnetError):
        subnet_from_resource(resource)

def test_subnet_vcn_in_unknown():
    resource = Resource(
        address="oci_core_subnet.app",
        kind="oci_core_subnet",
        values={
            "vcn_id": "ocid1.vcn.example",
            "cidr_block": "10.0.1.0/24",
        },
        unknown={
            "vcn_id": True,
        },
    )

    with pytest.raises(UnknownSubnetError):
        subnet_from_resource(resource)

def test_subnet_cidr_block_unknown():
    resource = Resource(
        address="oci_core_subnet.app",
        kind="oci_core_subnet",
        values={
            "vcn_id": "ocid1.vcn.example",
            "cidr_block": "10.0.1.0/24",
        },
        unknown={
            "cidr_block": True,
        },
    )

    with pytest.raises(UnknownSubnetError):
        subnet_from_resource(resource)

def test_subnet_security_list_ids_unknown():
    resource = Resource(
        address="oci_core_subnet.app",
        kind="oci_core_subnet",
        values={
            "vcn_id": "ocid1.vcn.example",
            "cidr_block": "10.0.1.0/24",
        },
        unknown={
            "security_list_ids": True,
        },
    )

    subnet = subnet_from_resource(resource)
    assert subnet.cidr == ipaddress.IPv4Network("10.0.1.0/24")

@pytest.mark.parametrize("values", [
    {"cidr_block": "10.0.1.0/24"},
    {"vcn_id": None, "cidr_block": "10.0.1.0/24"},
    {"vcn_id": 123, "cidr_block": "10.0.1.0/24"},
    {"vcn_id": "", "cidr_block": "10.0.1.0/24"},
    {"vcn_id": " ", "cidr_block": "10.0.1.0/24"},
])
def test_invalid_vcn_id(values):
    resource = Resource(
        address="oci_core_subnet.app",
        kind="oci_core_subnet",
        values=values,
        unknown={},
    )

    with pytest.raises(ValueError, match="vcn_id"):
        subnet_from_resource(resource)

@pytest.mark.parametrize("values", [
    {"vcn_id": "ocid1.vcn.example"},
    {"vcn_id": "ocid1.vcn.example", "cidr_block": None},
    {"vcn_id": "ocid1.vcn.example", "cidr_block": 123},
    {"vcn_id": "ocid1.vcn.example", "cidr_block": ""},
    {"vcn_id": "ocid1.vcn.example", "cidr_block": " "},
])
def test_invalid_cidr_block(values):
    resource = Resource(
        address="oci_core_subnet.app",
        kind="oci_core_subnet",
        values=values,
        unknown={},
    )

    with pytest.raises(ValueError, match="cidr_block"):
        subnet_from_resource(resource)