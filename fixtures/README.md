# Fixture provenance

`subnet-change.json` is a hand-authored, minimal Terraform plan-shaped fixture.
It is not an actual OCI provider export and does not establish provider compatibility.
It contains a changed subnet CIDR and an unresolved security-list association.
Realistic security-list, route-table, unknown-value, and nested-module fixtures
will be added with the corresponding checks. No OCI resources are deployed.
