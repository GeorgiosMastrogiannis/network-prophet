import json
from pathlib import Path
import subprocess
import sys


def test_cli_reports_no_overlaps():
    path = Path(__file__).parents[1] / "fixtures/subnet-change.json"

    result = subprocess.run(
        [sys.executable, "-m", "network_guardian.cli", str(path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "before": [],
        "after": [],
        "incomplete": [],
    }


def test_cli_missing_file_is_input_error(tmp_path):
    result = subprocess.run([sys.executable, "-m", "network_guardian.cli", str(tmp_path / "missing.json")], capture_output=True, text=True)
    assert result.returncode == 2
    assert "error:" in result.stderr

def test_cli_reports_overlap(tmp_path):
    fixture = Path(__file__).parents[1] / "fixtures/subnet-change.json"

    plan = json.loads(fixture.read_text(encoding="utf-8"))

    second_subnet = {
        "address": "oci_core_subnet.database",
        "mode": "managed",
        "type": "oci_core_subnet",
        "values": {
            "id": "ocid1.subnet.database",
            "vcn_id": "ocid1.vcn.example",
            "cidr_block": "10.0.2.128/25",
        },
    }

    plan["planned_values"]["root_module"]["resources"].append(second_subnet)

    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "network_guardian.cli", str(plan_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1

    output = json.loads(result.stdout)

    assert output["before"] == []
    assert output["after"] == [
        ["oci_core_subnet.app", "oci_core_subnet.database"]
    ]
    assert output["incomplete"] == []

def test_cli_reports_incomplete(tmp_path):
    fixture = Path(__file__).parents[1] / "fixtures/subnet-change.json"
    plan = json.loads(fixture.read_text(encoding="utf-8"))

    subnet = plan["planned_values"]["root_module"]["resources"][0]
    subnet["values"].pop("cidr_block")

    change = plan["resource_changes"][0]["change"]
    change["after_unknown"]["cidr_block"] = True

    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "network_guardian.cli", str(plan_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 3

    output = json.loads(result.stdout)

    assert output["before"] == []
    assert output["after"] == []
    assert len(output["incomplete"]) == 1
    assert output["incomplete"][0]["snapshot"] == "after"
    assert output["incomplete"][0]["address"] == "oci_core_subnet.app"

def test_cli_overlap_and_incomplete(tmp_path):
    fixture = Path(__file__).parents[1] / "fixtures/subnet-change.json"
    plan = json.loads(fixture.read_text(encoding="utf-8"))

    # Existing app subnet: 10.0.2.0/24
    # Add a second known subnet that overlaps with it.
    second_subnet = {
        "address": "oci_core_subnet.database",
        "mode": "managed",
        "type": "oci_core_subnet",
        "values": {
            "id": "ocid1.subnet.database",
            "vcn_id": "ocid1.vcn.example",
            "cidr_block": "10.0.2.128/25",
        },
    }

    # Third subnet: CIDR unknown until Terraform apply.
    third_subnet = {
        "address": "oci_core_subnet.cache",
        "mode": "managed",
        "type": "oci_core_subnet",
        "values": {
            "vcn_id": "ocid1.vcn.example",
        },
    }

    resources = plan["planned_values"]["root_module"]["resources"]
    resources.append(second_subnet)
    resources.append(third_subnet)

    # Tell the parser that cache's CIDR is unknown.
    plan["resource_changes"].append({
        "address": "oci_core_subnet.cache",
        "mode": "managed",
        "type": "oci_core_subnet",
        "change": {
            "actions": ["create"],
            "before": None,
            "after": {
                "vcn_id": "ocid1.vcn.example",
            },
            "after_unknown": {
                "cidr_block": True,
            },
        },
    })

    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "network_guardian.cli", str(plan_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 3

    output = json.loads(result.stdout)

    assert output["before"] == []
    assert output["after"] == [
        ["oci_core_subnet.app", "oci_core_subnet.database"]
    ]

    assert len(output["incomplete"]) == 1
    assert output["incomplete"][0]["snapshot"] == "after"
    assert output["incomplete"][0]["address"] == "oci_core_subnet.cache"
