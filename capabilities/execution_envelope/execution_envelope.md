# Bounded execution envelope

`capabilities/execution_envelope/execution_envelope.py` defines the Slice 2 Body boundary. Task inputs,
role returns, and command receipts have fixed fields, canonical JSON, UTF-8 byte
limits, short-string limits, and verified repository-relative artifact references.
Large plans, reports, source, diffs, transcripts, reasoning, and command output
remain in referenced files.

The limits are 8,192 bytes for task input, 4,096 bytes for role returns, and
4,096 bytes for command receipts. Artifact references reuse Slice 1's exact
`reference_id`, `repository_relative_path`, `sha256`, `byte_size`,
`artifact_type`, `description`, and `read_condition` fields.

`run_command` executes exactly one command and writes complete stdout and stderr
to the requested log before returning metadata. A failed command is `FAILED`
with its original exit code; a preflight mismatch is `BLOCKED` and the command
is not started. Mutations require an exact repository root, worktree, branch,
HEAD, clean state, and `mutation_authorized: true`.
