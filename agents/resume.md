# Validated restart admission

`harness/resume.py` admits one exact Slice 4 checkpoint for a fresh Body
process. The request binds the checkpoint path, SHA-256, and byte size plus task
and sealed-plan identity. Admission reads the checkpoint once, performs full
checkpoint and referenced-artifact validation, rejects duplicate completed
steps and a completed current step, and writes the exact canonical nested Body
snapshot to a new create-only path in an external runtime workspace.

The helper returns canonical `READY`, `BLOCKED`, or nonzero `INVALID` output.
`READY` exposes the current step and bounded next-action text for later
Body-controlled revalidation; `BLOCKED` exposes only the blocking state and is
never execution authority. No action is parsed as executable or run here.

Consumers must validate the receipt and immediately revalidate the materialized
state's exact hash, size, artifacts, execution envelope, and mutation preflight
before any later authorized action. The receipt is point-in-time admission, not
exactly-once side-effect protection.
