# Target Task provider-neutral contract

Target Task is a provider-neutral deterministic lifecycle. A host adapter is
replaceable and maps provider roles/events to the four canonical roles:
`planner`, `reviewer`, `worker`, and `command`. No provider CLI, event schema,
configuration, permission mechanism, agent name, or transcript format is part
of the canonical protocol.

`CLAUDE.md` is only one host entry point; another host may read this contract
and `workflows/target_task.md`, invoke canonical roles through an adapter, and
write the same task-root artifacts.

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
- `runtime.py`: canonical requests, result manifests, and compact host receipts.
- `host_adapter.py`: minimal provider adapter interface and invocation evidence.
- `command.py`: clean-preflight, timeout-bounded deterministic commands with immutable logs.

## Isolation boundary

The initial mission may be visible to a host during bootstrap. After bootstrap,
the durable Lead carries only compact references and status. Protocol isolation
and provider-evidence correlation are testable; hidden host context isolation
remains `UNKNOWN` unless independently proved. Qualification of one adapter
does not qualify another, and no adapter is mandatory for the core.

Changes to this lifecycle are ordinary Task Prompt work, never a Target Task.
