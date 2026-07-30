# Agent Instructions

This repository is a portable prompt and review library. Its capabilities validate metadata-only Body state and related bounded receipts. Route only to the minimum named artifact required for the current action; never load directories recursively.

## Entry map

- Review an artifact, decision, or RunSkeptic: read `skeptic.md` and only explicitly applicable companions.
- Lead execution: read `agents/lead_agent.md`; add `agents/model_routing_policy.md` when routing is needed and `agents/agent_return_contract.md` for delegated returns.
- Target Task (`TT: <mission>`) execution in Claude Code: `CLAUDE.md` loads this file, then this route requires a complete read of `workflows/target_task.md`. That workflow owns the trigger, Planner/Fix-Loop/seal/execute/validate/Find-Loop/integrate lifecycle and the compact Luna protocol. `concepts/target_task/` contains the deterministic MVP contracts used by that live host workflow.
- Target Task planning: dispatch the bounded Planner in `agents/planner.md` before execution; its return is advisory and requires Lead validation and acceptance through the RunSkeptic Fix Loop and seal. Supplied drafts are Planner input only.
- Substantive bounded plan construction or repair for ordinary work: use the bounded Planner in `agents/planner.md` when focused construction materially helps; its output is not execution authority.
- Define or execute a substantive workflow: read `workflows/task_prompt.md`.
- Build a Task Prompt (`TP: <objective>`, `Create task prompt for: <objective>`, `Create a task prompt for: <objective>`, or `Task prompt for: <objective>`): first read `workflows/task_prompt_builder.md` before interpreting or responding, then process the complete user request according to it. If the file cannot be read, stop visibly with `TASK_PROMPT_BUILDER_UNAVAILABLE`. Do not route an alias directly to `workflows/task_prompt.md`.
- Select model class -> `agents/model_routing_policy.md`
- Boundary processing: read `agents/boundary_agent.md` only when a material context or trust-boundary reduction is needed.
- Operate a capability: read only its contract, invoke its same-stem executable, and consume its bounded result. Do not read implementation source, tests, examples, sibling capabilities, or directories recursively.
- Modify, debug, or review a capability: read its contract, same-stem implementation, mirrored test, and only required examples or direct dependencies.

## Concept ownership

- Actual model roles live under `agents/`; policies end in `_policy`; interfaces and receipts end in `_contract`.
- Workflows live under `workflows/` and are not agents.
- Each deterministic capability owns one directory under `capabilities/`, with a same-stem `.md` contract and `.py` executable plus optional `examples/`.
- Tests mirror ownership under `tests/capabilities/<capability>/`.
- Runtime state, plans, checkpoints, logs, receipts, and validation evidence remain outside this repository.

## Selective loading

Ordinary operation is contract -> executable -> bounded result. It does not authorize recursive loading or implementation/test/example inspection. Actual model reading is unobservable unless runtime evidence proves it; report hidden runtime context as `UNKNOWN`.

## Ownership

`skeptic.md` is authoritative for Skeptic behavior and receipts and must not be edited without explicit authority. `agents/model_routing_policy.md` is authoritative for portable cost-aware model routing. `agents/` owns model roles and policies; `workflows/` owns task workflows; each capability contract owns its public behavior and its same-stem implementation. No compatibility shim is active.

## Portability

Standalone `skeptic.md` remains independently usable and must not depend on this checkout. Preserve invocation aliases and authority boundaries when changing references.
