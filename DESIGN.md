# Design and explicit boundaries

## Architecture

`plan.py` → normalized network model → pure checks → CLI presentation.
Only the first stage exists today. Keep Terraform dictionaries at the boundary;
use small dataclasses and `ipaddress` objects in the model. Keep network checks
free of file access so pytest can exercise them directly.

A plan supplies `prior_state.values` and `planned_values`. Recurse through child
modules and preserve full Terraform addresses. Skip data sources. Retain
`resource_changes[].change.after_unknown`, including nested lists and booleans.
Missing prior state represents a new deployment. Missing planned values is an
input error. Only JSON format major version 1 is accepted.

The reader validates the envelope, not every provider attribute. Downstream
normalization must check required fields and unknown masks before making claims.
Frozen resource records contain mutable JSON dictionaries: treat these as read-only.

## Intended MVP checks (not yet implemented)

* CIDR overlaps: compare distinct subnet CIDRs within the same known VCN.
  Exclude VCN-to-subnet containment, which is expected. Include evidence addresses.
* Public ingress: flag a security-list ingress rule permitting TCP from
  `0.0.0.0/0` (or all protocols). Describe this as a rule exposure, never proof
  of Internet reachability. Report before/after findings and distinguish new from existing.
* Connectivity regression: evaluate user-supplied named TCP probes with source
  IP, source port, destination IP, and destination port. Limit version one to
  private IPv4 addresses in the same known subnet, stateful security lists,
  known associations, and no NSGs. Evaluate forward source egress and destination
  ingress against the union of attached security-list rules, including source
  port constraints. A probe is allowed, blocked, or unknown within this model.
  A regression requires allowed before and blocked after.

Default security-list attachments, unresolved IDs, stateless rules, NSGs,
unsupported protocol/source types, ambiguous endpoint membership, or unknown
required fields produce an unknown result for affected probes. Do not silently
ignore unsupported rules when deciding a blocked verdict. Known sufficient
allow evidence can establish allowed only after model prerequisites hold.
No matching modeled rule is blocked only when the rule set is complete and known.

Unknown or missing CIDRs and VCN identities also produce explicit incomplete
analysis diagnostics for overlap checks. Unresolved ingress rules cannot produce
an all-clear result. Unknown is never converted to blocked or safe.

## Exclusions

No cross-subnet routing in version one; therefore no route-table simulator,
DRGs, peering, NAT, Internet gateways, service gateways, or longest-prefix match.
No DNS, host firewalls, running instance state, actual packet delivery, automatic
Terraform execution, OCI API calls, deployment, or web dashboard. IPv6 CIDR
arithmetic can be tested independently; connectivity is IPv4-only.

Even an allowed probe is modeled connectivity, not full OCI behavior. Endpoint
and security attachment completeness must be established explicitly by the input
contract; absence of managed NSGs alone does not prove no out-of-band NSGs exist.
The future probe schema must require a modeled attachment declaration and print
that assumption in evidence.

## Intended CLI contract

Today: inspection JSON, exit 0 for successful parsing and 2 for input errors.
Later: 0 for complete analysis with no selected findings, 1 for findings,
2 for invalid input, 3 for incomplete analysis. Incompleteness takes precedence
in the exit code while JSON still includes all known findings. Sort output for
repeatable demos and CI. Do not claim this contract is implemented yet.

## Verification

Unit tests cover nested snapshots, creation/deletion, unknown preservation,
unsupported formats, invalid envelopes, and CLI behavior. Each future check
needs positive, negative, and unknown cases; a regression requires two snapshots.
Hand-authored JSON fixtures must remain labeled synthetic. OCI HCL examples
will be added incrementally and checked with Terraform formatting and validation;
provider-backed exports require a separate explicit provenance record.
