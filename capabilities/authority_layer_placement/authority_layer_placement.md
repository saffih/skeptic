# Authority layer placement

`capabilities/authority_layer_placement/authority_layer_placement.py` prepares and validates a bounded authority-placement review packet using one fixed chain profile, `STANDARD_6`.

The capability is read-only over admitted source documents. It never edits authority documents, never delegates, and never substitutes Artifact Relay or Luna.

It exposes exactly two actions:

- `prepare --request REQUEST.json --output PACKET.json`
- `validate --packet PACKET.json --result RESULT.json --output REPORT.json`

`prepare` accepts `AuthorityPlacementRequest@1`, validates fixed-chain identity, repository-relative paths, file hashes, bounded limits, duplicate document IDs, optional line selectors, and the admitted output path beneath `output_dir`. It emits a canonical `AuthorityPlacementPacket@1` containing:

- request identity
- repository root binding
- fixed `STANDARD_6` chain bytes and hash
- admitted document records
- deterministic source units
- admitted `output_dir`
- frozen limits
- packet hash

When `item_selectors` is null, one source unit is emitted for each non-empty physical line in source order. Unit kinds are:

- `CODE` inside fenced code blocks
- `TABLE` for Markdown table rows or separators
- `STRUCTURE` for headings and list markers
- `PROSE` otherwise

`prepare` also emits `AuthorityPlacementPrepareReport@1` with `PREPARED` or `PREPARE_REJECTED`.

`validate` accepts one packet and one `AuthorityPlacementResult@1` and performs deterministic structural checks only. It verifies:

- packet and request binding
- exact quote hashes against packet source coverage
- one-time coverage of every packet source unit, or valid parent/child split coverage
- `RETURN_UPSTREAM` targets restricted to `GOVERNING_INPUTS`, `ARCHITECTURE`, or `SOFTWARE_DESIGN`
- `MOVE_DOWNSTREAM` targets restricted to `IMPLEMENTATION_PLAN`, `REALIZATION`, or `VERIFICATION_EVIDENCE`
- complete `CONFLICT` objects
- summary counts
- retry-policy counters
- deterministic evidence when the one allowed schema-correction retry is used
- semantic-byte ceiling and decomposition-depth bounds
- explicit routing observation gating with separate host evidence; self-declared observed routing is not qualifying by itself
- declared output-path admission

The validation report schema is `AuthorityPlacementValidationReport@1` with:

- `status: VALID | INVALID`
- field-level `errors`
- `mutation_scope: EXTERNAL_MUTATION_UNKNOWN`
- `qualification_blockers`

Validation is fail-closed. `execution.routing_observation = UNOBSERVED` produces a report but blocks qualification. `execution.routing_observation = OBSERVED` still blocks qualification unless admitted host evidence is present.
