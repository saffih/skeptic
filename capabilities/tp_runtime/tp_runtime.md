# Minimal TP runtime

`capabilities/tp_runtime/tp_runtime.py` is the mechanical owner for a normal
Task Prompt run.  It creates a host-owned external run root, persists the
mission and repository identity, appends controller events, validates compact
`TP_RESULT` envelopes, and calls an injected host adapter.

It has no semantic authority.  The adapter supplies a fresh Brain or Block
invocation; the runtime only follows a valid Brain sequence and binds each
Block's returned `block_ref` to the exact reference it assigned.  Every
cross-invocation semantic item is an existing file below `artifacts/`: Brain
Block assignments, Block results, and terminal Brain reports.  The runtime
resolves those references mechanically but never reads their contents.  A
malformed return, an unresolvable result reference, an interrupted return, or
an admission failure is retained as mechanical evidence and sent back to Brain.
It never retries a Block, selects a successor, interprets an artifact, or
declares completion.

The default root is the host temporary directory under `skeptic-tp/`.  Each
run stores `mission.md`, `events.jsonl`, `artifacts/`, and `repository.json`.
The latter records the resolved target repository path and, when available,
its current Git HEAD so run references remain resolvable without placing
bookkeeping in the repository.
