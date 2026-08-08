# Agent Instructions

This repository is a portable prompt and review library. Its capabilities validate metadata-only Body state and related bounded receipts. Route only to the minimum named artifact required for the current action; never load directories recursively.

## Entry map

- Context crossing any model or delegation boundary: read `docs/context-stewardship.md` `## Core`; additionally read and apply `## Orchestration` when the invocation acts as a control plane or produces semantic continuation, successor, or orchestration handoff state, because fixed section-scoped loading makes stewardship operative without making its own contract a repeated context tax.
- Review an artifact, decision, or RunSkeptic: read and follow the actual current `skeptic.md`; formal RunSkeptic semantics are owned there.
- Write or review a design, architecture, or software design document (SDD): use `docs/well.md` as the authority pointer.
- Lead execution: read `agents/lead_agent.md`. Routing uses `agents/model_routing_policy.md`; delegated returns use `agents/agent_return_contract.md`.
- A top-level user instruction beginning `TP:` activates the Task Prompt workflow: the text after the prefix is the governing task input, and that invocation acts as the Lead. Before task-specific repository inspection or command execution, load `agents/lead_agent.md`, `workflows/task_prompt.md`, and Context Stewardship `## Orchestration`, then follow those authorities without restating their rules here.
- Substantive plan construction or repair: use `agents/planner.md`.
- Define or execute a substantive workflow: read `workflows/task_prompt.md`.
- Build a Task Prompt: use `workflows/task_prompt_builder.md`.
- Select model class -> `agents/model_routing_policy.md`
- Boundary processing: use `agents/boundary_agent.md` when required by governing control state.
- Operate a capability: read only its contract, invoke its same-stem executable, and consume its bounded result. Do not read implementation source, tests, examples, sibling capabilities, or directories recursively.
- Modify, debug, or review a capability: read its contract, same-stem implementation, mirrored test, and only required examples or direct dependencies.

## Concept ownership

- Actual model roles live under `agents/`; policies end in `_policy`; interfaces and receipts end in `_contract`.
- Workflows live under `workflows/` and are not agents.
- Each deterministic capability owns one directory under `capabilities/`, with a same-stem `.md` contract and `.py` executable plus optional `examples/`.
- Tests mirror ownership under `tests/capabilities/<capability>/`.
- Runtime artifacts are not tracked repository authority; authorized ignored repository-local storage is permitted, and hosts may place them where execution or receiver reachability requires.

## Selective loading

Ordinary operation is contract -> executable -> bounded result. It does not authorize recursive loading or implementation/test/example inspection. Actual model reading is unobservable unless runtime evidence proves it; report hidden runtime context as `UNKNOWN`.

## Ownership

`skeptic.md` is authoritative for Skeptic behavior and receipts and must not be edited without explicit authority. `agents/model_routing_policy.md` is authoritative for portable cost-aware model routing. `agents/` owns model roles and policies; `workflows/` owns task workflows; each capability contract owns its public behavior and its same-stem implementation. No compatibility shim is active.

## Portability

Standalone `skeptic.md` remains independently usable and must not depend on this checkout. Preserve invocation aliases and authority boundaries when changing references.
