# Target Task Working MVP

The Target Task implementation uses one durable task root and a reference-only controller. The sealed Plan is the lifecycle identity; `plans/execution/<sealed-plan-sha256>.json` is its mechanically executable companion.

## Controller

```text
python3 scripts/target_task.py --tasks-root <root> --task-id <id> status
python3 scripts/target_task.py --tasks-root <root> --task-id <id> prepare --source-root <repo>
python3 scripts/target_task.py --tasks-root <root> --task-id <id> accept --source-root <repo> --receipt <receipt.json>
python3 scripts/target_task.py --tasks-root <root> --task-id <id> advance --source-root <repo>
python3 scripts/target_task.py --tasks-root <root> --task-id <id> retry
python3 scripts/target_task.py --tasks-root <root> --task-id <id> handoff
python3 scripts/target_task.py --tasks-root <root> resume --handoff <handoff.json>
python3 scripts/target_task.py --tasks-root <root> --task-id <id> validate
```

Every command emits bounded canonical JSON containing state and references only. Mission text, Plan bodies, output bodies, logs, transcripts, patches, and focused-retrieval excerpts remain in durable artifacts outside the Lead return.

## Routing

Core routes canonical roles and model classes. Concrete provider roles and model aliases belong to adapters. An unavailable explicit provider fails closed. An economical Lead route that the current top-level host cannot satisfy produces `RELAUNCH_REQUIRED`; it does not claim a model switch occurred.

A resolved route is still not proof that the provider/model ran. Actual execution is evidenced only after the matching adapter persists raw provider evidence and the role result includes its routing-evidence reference.

## Deterministic smoke scope

`scripts/generic_host_smoke.py` performs a credit-free, two-step recorded-host lifecycle through mission bootstrap, qualified Plan fixture, executable companion, route resolution, request persistence, raw provider evidence, compact receipt validation, one-time advancement, fresh-session resume, and execution validation.

Its truthful terminal state is:

```text
EXECUTION_COMPLETE
phase: STEP_VALIDATED
closed: false
live_provider_not_run: true
```

It does not prove a live Claude Code or Codex invocation, final RunSkeptic convergence, integration, remote publication, or hidden host context isolation.

## Remaining unknowns

- Hidden host context isolation: `UNKNOWN`.
- Live provider behavior: `NOT_RUN` until separately authorized.
- Terminal `CLOSED`: requires the existing final review, integration, and remote verification gates.
