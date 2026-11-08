"""Check IPv4 subnet CIDR overlaps within each VCN in a Terraform plan."""
import argparse
import json
from pathlib import Path
import sys
from network_guardian.analysis import analyze_overlaps

from network_guardian.plan import read_plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="JSON from terraform show -json")
    args = parser.parse_args()
    try:
        snapshots = read_plan(json.loads(args.plan.read_text(encoding="utf-8")))
        result = analyze_overlaps(snapshots)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    
    if result["incomplete"]:
        return 3

    if result["after"]:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
