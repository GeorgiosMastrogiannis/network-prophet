import copy
import json
from pathlib import Path

import pytest

from network_guardian.plan import PlanError, read_plan


@pytest.fixture
def plan():
    return json.loads((Path(__file__).parents[1] / "fixtures/subnet-change.json").read_text())


def test_extracts_both_snapshots_and_preserves_unknowns(plan):
    snapshots = read_plan(plan)
    assert snapshots.before[0].values["cidr_block"] == "10.0.1.0/24"
    assert snapshots.after[0].values["cidr_block"] == "10.0.2.0/24"
    assert snapshots.after[0].unknown == {"security_list_ids": True}
    assert snapshots.before[0].unknown == {}


def test_nested_modules_and_data_sources(plan):
    resource = copy.deepcopy(plan["planned_values"]["root_module"]["resources"][0])
    resource["address"] = "module.network.oci_core_subnet.app"
    root = plan["planned_values"]["root_module"]
    root["child_modules"] = [{"resources": [resource]}]
    root["resources"].append({"mode": "data"})
    assert [r.address for r in read_plan(plan).after] == [
        "module.network.oci_core_subnet.app", "oci_core_subnet.app"
    ]


def test_empty_prior_is_valid_for_creation(plan):
    del plan["prior_state"]
    assert read_plan(plan).before == ()


def test_delete_is_absent_from_planned_snapshot(plan):
    plan["planned_values"]["root_module"]["resources"] = []
    plan["resource_changes"][0]["change"] = {
        "actions": ["delete"], "before": {}, "after": None, "after_unknown": {}
    }
    snapshots = read_plan(plan)
    assert len(snapshots.before) == 1
    assert snapshots.after == ()


@pytest.mark.parametrize("version", [None, "2.0", 1])
def test_rejects_unsupported_format(plan, version):
    plan["format_version"] = version
    with pytest.raises(PlanError):
        read_plan(plan)


def test_rejects_missing_proposed_snapshot(plan):
    del plan["planned_values"]
    with pytest.raises(PlanError, match="planned_values"):
        read_plan(plan)


def test_rejects_duplicate_addresses(plan):
    root = plan["planned_values"]["root_module"]
    root["resources"] *= 2
    with pytest.raises(PlanError, match="duplicate"):
        read_plan(plan)


def test_rejects_malformed_resource_values(plan):
    plan["planned_values"]["root_module"]["resources"][0]["values"] = None
    with pytest.raises(PlanError, match="values"):
        read_plan(plan)
