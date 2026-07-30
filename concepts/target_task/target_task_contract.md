# Target Task Claude Code MVP contract

The active MVP is a host workflow, not a daemon. Claude Code auto-loads root
`CLAUDE.md`, which imports `AGENTS.md`; `AGENTS.md` routes an exact `TT:`
trigger to `workflows/target_task.md`. The Python modules in this directory are
the deterministic contracts used by that live workflow.

## One authoritative task root

`TASKS_ROOT/TASK_ID` is the sole authority for every run artifact: mission,
ledger, Plan versions, sealed Plan, steps, requests, results, reviews,
findings, receipts, command logs, routing evidence, and checkpoints. The source
repository is the work target, not a task-state store.

## Modules

- `trigger.py`: exact trigger, bootstrap, compact rediscovery, restart adapter.
- `flow.py`: fixed high-level lifecycle and sealed-Plan invariant.
- `contracts.py`: ledger, phase/action vocabulary, explicit linear cursor.
- `store.py`: create-only task artifacts and append-only hash-chained ledger.
- `boundary.py`: transition gate, receipts, review gates, cursor operations.
- `runtime.py`: test adapter and production Claude Code host-receipt validation.
- `command.py`: bounded deterministic command execution and evidence capture.

## Isolation statement

The MVP proves protocol isolation at observable boundaries. It does not prove
hidden host context isolation; report that as UNKNOWN.

## Non-circular construction

Changes to Target Task itself are ordinary Task Prompt work. Do not use `TT:`
to modify this contract, workflow, or implementation.
