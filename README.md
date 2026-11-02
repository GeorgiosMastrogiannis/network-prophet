# Network Change Guardian

A learning project for an Oracle Principal Network Developer interview on
November 12, 2026 at 09:00. Target a small working analyzer by November 8;
reserve November 9–11 for Python and Terraform coding practice.

## Current milestone

Implemented: saved-plan reader, nested modules, before/after snapshots,
unknown-marker preservation, inspection CLI, pytest suite, and GitHub Actions configuration.
The CIDR function is implemented and tested. Network findings are not implemented.
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

## Completed exercise: CIDR overlap

Implemented by Georgios with AI review; all 21 current tests pass locally.
The instructions below document the original assignment.

### Original assignment (15–25 minutes)

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

## Contribution history and AI assistance

The GitHub repository is named `network-prophet`; the Python package and CLI
retain their initial Network Change Guardian names.

Commit prefixes describe contribution provenance:

- `scaffold:` AI-generated project foundations.
- `exercise:` implementations written by Georgios; the commit body records AI assistance.
- `docs:` documentation changes, with assistance recorded in the commit body.

The initial scaffold and first exercise were reconstructed as separate commits
from the saved scaffold and completed working files. They are retrospective
records, not the original edit-time history. The existing GitHub initial commit
is preserved. Git author metadata uses the configured committer identity;
these messages describe code provenance, rather than claiming separate human
and AI Git accounts.

Georgios implemented CIDR overlap and simplified it after AI feedback. Codex
supplied the corrected inside/outside /32 test example. Future exercises should
start from a committed scaffold so their changes can be recorded directly.
