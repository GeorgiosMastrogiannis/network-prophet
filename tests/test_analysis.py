from network_guardian.plan import Resource, Snapshots
from network_guardian.analysis import analyze_overlaps

def test_new_subnet_overlap():
    subnet_a = Resource(
        address="subnet.A",
        kind="oci_core_subnet",
        values={
            "vcn_id": "vcn-1",
            "cidr_block": "10.0.1.0/24",
        },
        unknown=False,
    )

    subnet_b = Resource(
        address="subnet.B",
        kind="oci_core_subnet",
        values={
            "vcn_id": "vcn-1",
            "cidr_block": "10.0.2.0/24",
        },
        unknown=False,
    )

    # overlaps with b
    subnet_c = Resource(
        address="subnet.C",
        kind="oci_core_subnet",
        values={
            "vcn_id": "vcn-1",
            "cidr_block": "10.0.2.128/25",
        },
        unknown=False,
    )

    snapshots = Snapshots(
        before=(subnet_a, subnet_b),
        after=(subnet_a, subnet_b, subnet_c)
    )

    result = analyze_overlaps(snapshots)

    assert result["before"] == []
    assert result["after"] == [("subnet.B", "subnet.C")]
    assert result["incomplete"] == []

def test_unknown_subnet_is_incomplete():
    subnet_a = Resource(
        address="subnet.A",
        kind="oci_core_subnet",
        values={
            "vcn_id": "vcn-1",
            "cidr_block": "10.0.1.0/24",
        },
        unknown=False,
    )

    subnet_b = Resource(
        address="subnet.B",
        kind="oci_core_subnet",
        values={
            "vcn_id": "vcn-1",
        },
        unknown={"cidr_block": True},
    )

    snapshots = Snapshots(
        before=(),
        after=(subnet_a, subnet_b)
    )

    result = analyze_overlaps(snapshots)

    assert result["before"] == []
    assert result["after"] == []
    assert len(result["incomplete"]) == 1
    assert result["incomplete"][0]["snapshot"] == "after"
    assert result["incomplete"][0]["address"] == "subnet.B"

def test_known_overlap_with_unknown_subnet():
    subnet_a = Resource(
        address="subnet.A",
        kind="oci_core_subnet",
        values={
            "vcn_id": "vcn-1",
            "cidr_block": "10.0.2.0/24",
        },
        unknown=False,
    )

    subnet_b = Resource(
        address="subnet.B",
        kind="oci_core_subnet",
        values={
            "vcn_id": "vcn-1",
            "cidr_block": "10.0.2.128/25",
        },
        unknown=False,
    )

    subnet_c = Resource(
        address="subnet.C",
        kind="oci_core_subnet",
        values={
            "vcn_id": "vcn-1",
        },
        unknown={"cidr_block": True},
    )

    snapshots = Snapshots(
        before=(),
        after=(subnet_a, subnet_b, subnet_c),
    )

    result = analyze_overlaps(snapshots)

    assert result["before"] == []
    assert result["after"] == [("subnet.A", "subnet.B")]

    assert len(result["incomplete"]) == 1
    assert result["incomplete"][0]["snapshot"] == "after"
    assert result["incomplete"][0]["address"] == "subnet.C"
    assert result["incomplete"][0]["reason"] == "Subnet VCN or CIDR is unknown"