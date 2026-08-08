# Agent Instructions

This repository is a portable prompt and review library. Its capabilities validate metadata-only Body state and related bounded receipts. Route only to the minimum named artifact required for the current action; never load directories recursively.

## Entry map

- Context crossing any model or delegation boundary: read `docs/context-stewardship.md` `## Core`; when acting as Lead or mini-orchestrator also read `## Orchestration`, because fixed section-scoped loading makes stewardship operative without making its own contract a repeated context tax.
- Review an artifact, decision, or RunSkeptic: dispatch a bounded child to read `skeptic.md` and only explicitly applicable companions, because substantive review is not Lead work. A formal RunSkeptic invocation, including a named mode such as Find Loop or Fix Loop, requires the dispatched child to freshly read the actual current `skeptic.md` and execute that mode's own recipe, permission, convergence/reset, and receipt rules exactly; memory, summaries, prior receipts, and approximations must not substitute, because a stale or approximated review cannot serve as evidence for the framework it claims to satisfy.
- Write or review a design, architecture, or software design document (SDD): dispatch a bounded WELL child with `docs/well.md` and exact admitted inputs, because design reading and judgment are substantive.
- Lead execution: read `agents/lead_agent.md`; add `agents/model_routing_policy.md` when routing is needed and `agents/agent_return_contract.md` for delegated returns. The Lead is orchestration-only, every substantive action uses a bounded child, and the run workspace is created before substantive dispatch.
- Substantive plan construction or repair: dispatch the bounded Planner in `agents/planner.md`; its output is not execution authority, because all substantive planning is child-owned.
- Define or execute a substantive workflow: read `workflows/task_prompt.md`.
- Build a Task Prompt (`TP: <objective>`, `Create task prompt for: <objective>`, `Create a task prompt for: <objective>`, or `Task prompt for: <objective>`): first read `workflows/task_prompt_builder.md` before interpreting or responding, then process the complete user request according to it. If the file cannot be read, stop visibly with `TASK_PROMPT_BUILDER_UNAVAILABLE`. Do not route an alias directly to `workflows/task_prompt.md`.
- Select model class -> `agents/model_routing_policy.md`
- Boundary processing: read `agents/boundary_agent.md` only when a material context or trust-boundary reduction is needed.
- Operate a capability: read only its contract, invoke its same-stem executable, and consume its bounded result. Do not read implementation source, tests, examples, sibling capabilities, or directories recursively.
- For Lead execution, capability operation is substantive work and must be dispatched to a bounded child, because the Lead may retain only control-plane mechanics and compact receipts.
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
