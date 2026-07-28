# Compact RunSkeptic Examples

These examples show transport shape only; the complete recipe remains in the
root `skeptic.md`.

## Plan review

`INVOCATION_KIND: SINGLE`, `PERMISSION_MODE: read-only`, current complete Plan,
material findings reference, fresh root source path/ref/blob, and a receipt with
all recipe steps and Thinkers. The result uses canonical `PASS`, `ACTION`, or
`CONFLICT`, then `HANDLED` or `CONFLICT`.

## Repair then three unchanged passes

`FIX_LOOP` + `REPAIR_RUN: true` resets the count to zero. Three later complete
reviews with the same task, artifact, source, companions, invocation, and
permission bindings, material-finding-set hash, no open items, and only `PASS`
findings advance `1`, `2`, then `3`.

## Reset and result review

A changed source/artifact/task/companion or material finding resets the count.
Result reviews bind the complete Result artifact, not a delta. A changed basis
must be reviewed from the beginning.

## Bounded Planner repair input

Pass the immutable task reference, validated repository facts, complete current
Plan, material findings, blockers, and artifact references. The Planner returns
one replacement Plan plus a finding-to-step map; the Lead accepts or rejects it.
