# Agent Instructions

This repository is a portable prompt and review library. Route only to the
minimum named artifact required for the current action; never load directories
recursively. Its capabilities validate metadata-only Body state and related
bounded receipts.

## Entry map

- Review an artifact, decision, or RunSkeptic: read `skeptic.md` and only
  explicitly applicable companions.
- Lead execution: read `agents/lead_agent.md`; add the routing policy and
  return contract only when the action requires them.
- STT (`STT: <mission>`): read and follow the complete canonical contract in
  `workflows/target_task.md`. The runtime is `concepts/stt/`; the public CLI
  is `scripts/stt.py`.
- Target Task planning remains advisory: any bounded Planner return requires
  Lead validation and acceptance through the canonical STT Boundary contract.
- Build a Task Prompt (`TP: <objective>`, `Create task prompt for: <objective>`, `Create a task prompt for: <objective>`, or `Task prompt for: <objective>`): first read `workflows/task_prompt_builder.md` before interpreting or responding, then process the complete user request according to it. If the file cannot be read, stop visibly with `TASK_PROMPT_BUILDER_UNAVAILABLE`. Do not route an alias directly to `workflows/task_prompt.md`.
- Select a model class: read `agents/model_routing_policy.md`.
- Boundary processing for ordinary non-STT work: read
  `agents/boundary_agent.md` only when a material trust-boundary reduction is
  needed.
- Operate a capability: read its contract, invoke its same-stem executable,
  and consume its bounded result. Do not read implementation source, tests,
  examples, sibling capabilities, or directories recursively.
- Modify, debug, or review a capability: read its contract, same-stem
  implementation, mirrored test, and only required direct dependencies.

## STT ownership

- The active host handles semantic dispatch: Codex uses
  `STT_PROVIDER=codex`; Claude Code uses `STT_PROVIDER=claude-code`. Neither
  launches the other, and the target is the current Git repository.
- Boundary is mandatory for every substantive STT ingress and egress.
- Planner, Reviewer, and Worker are semantic model roles; Command is
  deterministic local execution.
- The durable Lead carries references and compact receipts, not substantive
  bodies. `ledger.jsonl` is the sole lifecycle authority and one reducer
  derives state from it.
- STT state defaults to `<repo>/.stt/tasks` and may be overridden by
  `STT_TASKS_ROOT`. Linked Git worktrees are not STT capsules.
- STT executes sequentially in the current shared workspace. Workers use sparse
  capsules, frozen admission identities, durable mutation intents, and scoped
  direct deltas. Provider-authored staging is frozen before acceptance. STT
  does not provide checkpoints, snapshots, preservation copies, cutover,
  rollback, restoration, operation replay, or whole-Task transactions. Linux
  is the only eligible contained Command backend; macOS fails closed as
  unavailable. Sandbox failure never falls back silently to unconfined
  execution.

The complete STT product, lifecycle, delivery, Boundary, recovery, and
sandbox contract is `workflows/target_task.md`; this file intentionally does
not duplicate it.

## Concept ownership

- Actual model roles live under `agents/`; policies end in `_policy`; interfaces
  and receipts end in `_contract`.
- Workflows live under `workflows/` and are not agents.
- Each deterministic capability owns one directory under `capabilities/`, with
  a same-stem `.md` contract and `.py` executable plus optional `examples/`.
- Tests mirror ownership under `tests/capabilities/<capability>/`.
- Runtime state, plans, capsules, logs, receipts, and validation evidence remain
  outside this repository.

## Selective loading

Ordinary operation is contract -> executable -> bounded result. Actual model
reading is unobservable unless runtime evidence proves it; report hidden
runtime context as `UNKNOWN`.

## Ownership and portability

`skeptic.md` is authoritative for Skeptic behavior and receipts and must not be
edited without explicit authority. `agents/model_routing_policy.md` is authoritative for portable cost-aware model routing. Standalone `skeptic.md`
remains independently usable and must not depend on this checkout.
