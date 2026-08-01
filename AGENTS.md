# Agent Instructions

This repository is a portable prompt and review library. Its capabilities validate metadata-only Body state and related bounded receipts. Route only to the minimum named artifact required for the current action; never load directories recursively.

## Entry map

- Review an artifact, decision, or RunSkeptic: read `skeptic.md` and only explicitly applicable companions.
- Lead execution: read `agents/lead_agent.md`; add `agents/model_routing_policy.md` when routing is needed and `agents/agent_return_contract.md` for delegated returns.
- Target Task (`TT: <mission>`) execution in Claude Code: `CLAUDE.md` loads this file, then this route requires a complete read of `workflows/target_task.md`. That workflow owns the trigger, Planner/Fix-Loop/seal/execute/validate/Find-Loop/integrate lifecycle and the compact reference-only protocol. `concepts/stt/` contains the deterministic runtime used by that live host workflow; `scripts/stt.py` is the public CLI and `scripts/target_task.py` is the single thin compatibility alias.
- Target Task planning: dispatch the bounded Planner in `agents/planner.md` before execution; its return is advisory and requires Lead validation and acceptance through the RunSkeptic Fix Loop and seal. Supplied drafts are Planner input only.
- Substantive bounded plan construction or repair for ordinary work: use the bounded Planner in `agents/planner.md` when focused construction materially helps; its output is not execution authority.
- Define or execute a substantive workflow: read `workflows/task_prompt.md`.
- Build a Task Prompt (`TP: <objective>`, `Create task prompt for: <objective>`, `Create a task prompt for: <objective>`, or `Task prompt for: <objective>`): first read `workflows/task_prompt_builder.md` before interpreting or responding, then process the complete user request according to it. If the file cannot be read, stop visibly with `TASK_PROMPT_BUILDER_UNAVAILABLE`. Do not route an alias directly to `workflows/task_prompt.md`.
- Select model class -> `agents/model_routing_policy.md`
- Boundary processing for ordinary non-Target work: read `agents/boundary_agent.md` only when a material context or trust-boundary reduction is needed.
- Target Task Boundary processing: the deterministic Boundary gates required by `workflows/target_task.md` and implemented in `concepts/stt/` are mandatory for every Target Task semantic dispatch, return, artifact admission, checkpoint promotion, and cutover transition.
- Operate a capability: read only its contract, invoke its same-stem executable, and consume its bounded result. Do not read implementation source, tests, examples, sibling capabilities, or directories recursively.
- Modify, debug, or review a capability: read its contract, same-stem implementation, mirrored test, and only required examples or direct dependencies.

## STT ownership

- When the first meaningful token is exactly `STT:`, the active host performs semantic dispatch: Codex sets `STT_PROVIDER=codex`, Claude Code sets `STT_PROVIDER=claude-code`, and both invoke `python3 scripts/stt.py` from the current Git root. Neither host launches the other, and the repository is resolved from the current session rather than a fixed user path.
- STT semantic roles use disposable filesystem capsules admitted by Boundary; linked Git worktrees are not STT capsules. Task state defaults to `<repo>/.stt/tasks`, is ignored by Git, and may be overridden with `STT_TASKS_ROOT`.

- Planner, Reviewer, and Worker are the only semantic STT roles.
- Commands are deterministic local operations and are never model roles.
- Substantial bodies live in immutable files outside the repository; the durable Lead receives compact receipts only.
- `ledger.jsonl` is the sole lifecycle authority; no phase or cursor file competes with it.
- Semantic work occurs in sparse disposable capsules and immutable checkpoints.
- The owner workspace is read-only until one reviewed deterministic cutover.
- Runtime state, locks, backups, and validation evidence are local to the checkout-adjacent private STT root.
- No commit, stage, checkout, reset, merge, rebase, push, PR, or publication is part of STT authority.

## Concept ownership

- Actual model roles live under `agents/`; policies end in `_policy`; interfaces and receipts end in `_contract`.
- Workflows live under `workflows/` and are not agents.
- Each deterministic capability owns one directory under `capabilities/`, with a same-stem `.md` contract and `.py` executable plus optional `examples/`.
- Tests mirror ownership under `tests/capabilities/<capability>/`.
- Runtime state, plans, checkpoints, logs, receipts, and validation evidence remain outside this repository.

## Selective loading

Ordinary operation is contract -> executable -> bounded result. It does not authorize recursive loading or implementation/test/example inspection. Actual model reading is unobservable unless runtime evidence proves it; report hidden runtime context as `UNKNOWN`.

## Ownership

`skeptic.md` is authoritative for Skeptic behavior and receipts and must not be edited without explicit authority. `agents/model_routing_policy.md` is authoritative for portable cost-aware model routing. `agents/` owns model roles and policies; `workflows/` owns task workflows; each capability contract owns its public behavior and its same-stem implementation. Exactly one thin Target Task compatibility alias is active at `scripts/target_task.py`.

## Portability

Standalone `skeptic.md` remains independently usable and must not depend on this checkout. Preserve invocation aliases and authority boundaries when changing references.
