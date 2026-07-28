# RunSkeptic Receipt Capability

This capability mechanically validates source-bound invocation receipts and
external Fix Loop state. It accepts only the root `skeptic.md` as the active
source, checks current file identity, canonical categories, required recipe
steps and Thinkers, artifact/reference hashes, and deterministic reset and
three-pass rules.

It proves structural and identity conformance only. It does not prove semantic
correctness, hidden model cognition, hidden runtime context, or actual routing.
Those remain `UNKNOWN` unless the runtime exposes evidence.

Receipts and loop state also bind a SHA-256 identity for the complete material
finding set. A changed finding identity resets the qualifying streak. A source
ref must resolve to the current root `skeptic.md` Git blob; `WORKTREE` is only
valid for an explicitly uncommitted source read.
