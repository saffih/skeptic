# Target Task artifacts

These are optional templates for a task that must cross a real handoff or
session boundary. They are not runtime state and are not required for a
bounded single-session task.

The approved design source of truth is
`architecture/target-task-architecture.md`; these templates are only durable
artifact examples.

`task.md` identifies the task and authoritative inputs. `brain.md` plans only.
`body.md` accepts, seals, executes, validates, and checkpoints. `plan.md` is
immutable after acceptance. `checkpoint.md` records resumable compact state.
`receipt.md` records the compact execution result. `handoff.md` contains the
Sufficient Handoff fields.

Large sources remain at their authoritative paths. The artifacts carry paths,
hashes, statuses, and next actions rather than copied content.
