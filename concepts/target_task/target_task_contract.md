# Target Task Claude Code MVP contract

The active MVP is a Claude Code host workflow:

`CLAUDE.md -> AGENTS.md -> workflows/target_task.md`.

The Python modules here are deterministic contracts used by that workflow; they
are not a daemon or provider SDK.

## One authoritative task root

`TARGET_TASKS_ROOT/TASK_ID` is the sole authority for mission, Plan versions,
sealed Plan, ledger, cursor snapshots, requests, results, reviews, findings,
receipts, command logs, routing evidence, validation, and checkpoints. Every
artifact reference is relative to that task root. The source repository is only
the work target.

## Modules

- `trigger.py`: exact trigger, atomic bootstrap, safe task IDs, complete rediscovery.
- `flow.py`: closed structural phase transition table.
- `contracts.py`: strict ledger, canonical Plan, and serializable cursor schemas.
- `store.py`: private create-only/content-addressed artifacts and strict ledger.
- `boundary.py`: mandatory evidence gates, review receipts, role receipts, cursor transitions.
- `runtime.py`: deterministic test adapter and fully bound Claude host receipts.
- `command.py`: clean-preflight, timeout-bounded deterministic commands with immutable logs.

## Isolation boundary

Direct Claude Code submission exposes the initial `TT:` message to the receiving
host session. After bootstrap, the durable Lead carries only compact references
and status. The MVP tests observable protocol isolation; hidden host context
isolation remains `UNKNOWN`.

Changes to this lifecycle are ordinary Task Prompt work, never a Target Task.
