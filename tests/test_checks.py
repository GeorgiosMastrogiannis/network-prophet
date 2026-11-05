import ipaddress
from network_guardian.checks import find_subnet_overlaps
from network_guardian.model import Subnet

def test_subnet_overlaps():
    subnet_a = Subnet(
        address="oci_core_subnet.a",
        vcn_id="vcn-123",
        cidr=ipaddress.ip_network("10.0.0.0/16"),
    )

    subnet_b = Subnet(
        address="oci_core_subnet.b",
        vcn_id="vcn-123",
        cidr=ipaddress.ip_network("10.0.1.0/24"),
    )

    assert find_subnet_overlaps([subnet_a, subnet_b]) == [
        ("oci_core_subnet.a", "oci_core_subnet.b")
    ]

    assert find_subnet_overlaps([subnet_b, subnet_a]) == [
    ("oci_core_subnet.a", "oci_core_subnet.b")
    ]

def test_subnet_disjoint_cidrs():
    subnet_a = Subnet(
        address="oci_core_subnet.a",
        vcn_id="vcn-123",
        cidr=ipaddress.ip_network("10.1.0.0/16"),
    )

    subnet_b = Subnet(
        address="oci_core_subnet.b",
        vcn_id="vcn-123",
        cidr=ipaddress.ip_network("10.0.1.0/24"),
    )

    assert find_subnet_overlaps([subnet_a, subnet_b]) == []

def test_subnet_overlaps_different_vcn():
    subnet_a = Subnet(
        address="oci_core_subnet.a",
        vcn_id="vcn-123",
        cidr=ipaddress.ip_network("10.0.1.0/24"),
    )

    subnet_b = Subnet(
        address="oci_core_subnet.b",
        vcn_id="vcn-456",
        cidr=ipaddress.ip_network("10.0.1.0/24"),
    )

    assert find_subnet_overlaps([subnet_a, subnet_b]) == []

def test_subnet_overlaps_empty_input():
    assert find_subnet_overlaps([]) == []

def test_subnet_overlaps_one_subnet():
    subnet_a = Subnet(
        address="oci_core_subnet.a",
        vcn_id="vcn-123",
        cidr=ipaddress.ip_network("10.0.1.0/24"),
    )

    assert find_subnet_overlaps([subnet_a]) == []