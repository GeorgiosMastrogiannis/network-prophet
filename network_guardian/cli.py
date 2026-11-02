"""Milestone 1 CLI: inspect snapshots; no safety verdict yet."""
import argparse
import json
from pathlib import Path
import sys

from network_guardian.plan import read_plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="JSON from terraform show -json")
    args = parser.parse_args()
    try:
        snapshots = read_plan(json.loads(args.plan.read_text(encoding="utf-8")))
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps({
        "status": "inspection_only",
        "before_resources": len(snapshots.before),
        "after_resources": len(snapshots.after),
        "unknown_resource_addresses": [r.address for r in snapshots.after if r.unknown],
        "message": "Network checks are not implemented yet; this is not a safety verdict.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
