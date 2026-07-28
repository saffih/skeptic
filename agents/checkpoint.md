# Immutable compact checkpoint

`harness/checkpoint.py` creates one canonical, create-only checkpoint from one
exact, fully validated metadata-only Body state. The request and checkpoint
are canonical UTF-8 JSON with one final LF. The request binds a safe path,
SHA-256, and byte size inside a task-owned external workspace; the helper
reads the Body state once, validates all repository-relative artifacts through
`harness/body_state.py`, and embeds the parsed state once.

The checkpoint contains the Body origin provenance, one complete Body snapshot,
sealed-plan identity, and a PASS receipt. It is written to a same-directory
exclusive temporary file, file-fsynced, structurally checked, atomically
published only when the final target is absent, directory-fsynced when
supported, reread, and verified. Existing targets are never overwritten.

Structural validation checks canonical bytes, limits, snapshot structure,
cross-references, identity, provenance, and receipt without opening the origin
file. Full validation additionally checks every embedded artifact against the
separately supplied repository root. Moving, changing, or deleting the origin
after publication does not change the embedded snapshot; later artifact
changes make full validation fail.

The success receipt reports the observed atomic publication and durability
mode. It makes no universal crash, power-loss, storage-device, or network
filesystem durability claim. This slice creates and validates checkpoints
only; it does not resume execution, execute `NEXT_AUTHORIZED_ACTION`, replace
or supersede checkpoints, maintain a latest pointer, or coordinate writers.
