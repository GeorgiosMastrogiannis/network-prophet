"""Read snapshots without confusing absent attributes with known values.

The analyzer will consume Resource objects rather than raw Terraform JSON.
Unknown markers are retained for later field-level interpretation.
"""
from dataclasses import dataclass
from typing import Any, Dict, Tuple


class PlanError(ValueError):
    """The input is outside our supported Terraform plan envelope."""


@dataclass(frozen=True)
class Resource:
    address: str
    kind: str
    values: Dict[str, Any]
    unknown: Any


@dataclass(frozen=True)
class Snapshots:
    before: Tuple[Resource, ...]
    after: Tuple[Resource, ...]


def _object(value: Any, label: str) -> dict:
    if not isinstance(value, dict):
        raise PlanError(f"{label} must be an object")
    return value


def _walk(module: dict, unknowns: dict) -> Tuple[Resource, ...]:
    result = []
    resources = module.get("resources", [])
    children = module.get("child_modules", [])
    if not isinstance(resources, list) or not isinstance(children, list):
        raise PlanError("module resources and child_modules must be arrays")
    for item in resources:
        item = _object(item, "resource")
        if item.get("mode") == "data":
            continue
        address, kind = item.get("address"), item.get("type")
        if not isinstance(address, str) or not isinstance(kind, str):
            raise PlanError("resource needs string address and type")
        values = _object(item.get("values"), f"{address}.values")
        result.append(Resource(address, kind, values, unknowns.get(address, {})))
    for child in children:
        result.extend(_walk(_object(child, "child module"), unknowns))
    return tuple(result)


def _snapshot(values: dict, unknowns: dict) -> Tuple[Resource, ...]:
    root = _object(values.get("root_module", {}), "root_module")
    resources = _walk(root, unknowns)
    addresses = [resource.address for resource in resources]
    if len(addresses) != len(set(addresses)):
        raise PlanError("duplicate resource address")
    return tuple(sorted(resources, key=lambda resource: resource.address))


def read_plan(document: Any) -> Snapshots:
    """Extract prior and proposed managed resources from one saved plan.

    Missing prior_state is valid for a new deployment. Missing planned_values
    is rejected: an incomplete input must not look like deletion of everything.
    """
    document = _object(document, "plan")
    version = document.get("format_version")
    if not isinstance(version, str) or version.split(".")[0] != "1":
        raise PlanError("supported Terraform JSON format major version is 1")
    planned = _object(document.get("planned_values"), "planned_values")
    prior = _object(document.get("prior_state", {}), "prior_state")
    before = _object(prior.get("values", {}), "prior_state.values")
    changes = document.get("resource_changes", [])
    if not isinstance(changes, list):
        raise PlanError("resource_changes must be an array")
    unknowns = {}
    for entry in changes:
        entry = _object(entry, "resource change")
        address = entry.get("address")
        if not isinstance(address, str):
            raise PlanError("resource change needs a string address")
        change = _object(entry.get("change"), "change")
        unknowns[address] = change.get("after_unknown", {})
    return Snapshots(_snapshot(before, {}), _snapshot(planned, unknowns))
