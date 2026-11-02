# Network Change Guardian

A learning project for an Oracle Principal Network Developer interview on
November 12, 2026 at 09:00. Target a small working analyzer by November 8;
reserve November 9–11 for Python and Terraform coding practice.

## Current milestone

Implemented: saved-plan reader, nested modules, before/after snapshots,
unknown-marker preservation, inspection CLI, pytest suite, and GitHub Actions configuration.
The CIDR function is an explicit exercise. Network findings are not implemented.
An inspection exit code of 0 means the input was read, not that the network is safe.
CI is configured but has not been run on GitHub.

## Run locally

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
python -m pytest -q
network-guardian fixtures/subnet-change.json
```

Python 3.9+; runtime dependencies are standard library only. No OCI account is
needed for these synthetic tests. Never commit a real plan containing secrets.

## First exercise: CIDR overlap (15–25 minutes)

1. Read `network_guardian/plan.py` and `tests/test_plan.py`. Explain why an unknown
   security-list association must survive parsing.
2. Implement `cidrs_overlap` in `network_guardian/cidr.py` with `ipaddress.ip_network`.
   Parse strictly, compare address families, then check overlap. Explain why
   checking whether two strings share a prefix is wrong.
3. Remove the two `xfail` decorators in `tests/test_cidr.py` and run pytest.
   They are strict: implementation makes them fail as unexpected passes until removed.
4. Add a test of your choice (for example a /32 inside a subnet). Explain the
   algorithm and its complexity aloud, then bring the change back for review.

No solution is hidden elsewhere. Expected failures are exercises, not completed checks.

## Small delivery plan

| Date | Deliverable and practice |
| --- | --- |
| Nov 2 | Review parser; implement and explain CIDR overlap |
| Nov 3 | Normalize OCI subnets and security-list TCP rules; reject ambiguity |
| Nov 4 | Detect subnet overlaps within each VCN; public IPv4 ingress rule findings |
| Nov 5 | Named TCP probes between two private IPv4 endpoints in one subnet; before/after verdicts |
| Nov 6 | Add OCI HCL examples and representative JSON; negative and unknown tests |
| Nov 7 | CLI findings, deterministic output, exit codes; rehearse explaining limitations |
| Nov 8 | Freeze scope, run checks, rehearse a five-minute demo |
| Nov 9–11 | Timed Python and Terraform exercises; fix only essential project bugs |

If time is tight, reduce features before reducing interview coding practice.

## Input contract

One JSON document from `terraform show -json saved.tfplan`, not two plan files.
It contains both prior state and proposed values. This avoids comparing unrelated
plans. A separate two-file comparison is outside the initial scope.
See `DESIGN.md` for the intended model and exclusions.

References: [Terraform JSON format](https://developer.hashicorp.com/terraform/internals/json-format)
and [OCI security-list resource](https://docs.oracle.com/en-us/iaas/tools/terraform-provider-oci/latest/docs/r/core_security_list.html).
