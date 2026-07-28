# Agent Instructions

Entry map. Load only the artifact needed for the current use:

- Review an artifact or decision (including "RunSkeptic" or Skeptic review)
  -> `skeptic.md`
- Lead task execution with proportional planning, delegation, and validation
  -> `agents/lead-agent-prompt.md`
- Define or execute a substantive task workflow
  -> `agents/task-prompt.md`
- Create a Task Prompt from a user objective or plan
  -> `agents/task-prompt-builder.md`
  - Aliases (text after the alias is the objective): `TP: <objective>`, `Create task prompt for: <objective>`, `Create a task prompt for: <objective>`, `Task prompt for: <objective>`
  - For any alias, first read `agents/task-prompt-builder.md` before interpreting or responding, then process the complete user request according to it. If the file cannot be read, stop visibly with `TASK_PROMPT_BUILDER_UNAVAILABLE`. Do not route an alias directly to `agents/task-prompt.md`.
- Activate the Optimized Task Prompt protocol for a Target Task (plan, seal, execute, validate, review, accept, receipt)
  -> `agents/target-task.md`
  -> `agents/otp-protocol.md` (legacy compatibility surface)
  - Triggers (text after the trigger is the Target Task): `OTP: <Target Task>` (explicit) and `TT: <Target Task>` (compact, fully equivalent). `OTP:` alone followed by a `TT:` line supplying the Target Task is valid and redundant, not a double activation. A plain task with neither leading trigger does not invoke OTP.
  - For `TT:`, first read `agents/target-task.md`; for legacy `OTP:`, first read `agents/otp-protocol.md` before interpreting or responding, then process the complete Target Task according to the canonical contract. If the required file cannot be read, stop visibly with `TARGET_TASK_PROTOCOL_UNAVAILABLE` or `OTP_PROTOCOL_UNAVAILABLE` respectively.
  - The legacy compatibility path must first read `agents/otp-protocol.md` before interpreting or responding, then process the complete Target Task according to it. If the file cannot be read, stop visibly with `OTP_PROTOCOL_UNAVAILABLE`.
- Select model class, reasoning effort, delegation, or escalation
  -> `agents/model-routing.md`
- Define or validate a delegated model-agent return
  -> `agents/agent-return.md`
- Select or operate a conditional context-processing boundary around delegation
  -> `agents/boundary-agent.md`

Usage modes:

Standalone or externally supplied Skeptic:
- A user may supply `skeptic.md` directly and ask an agent to read and apply it outside this repository.
- `skeptic.md` must therefore remain independently usable and must not assume that this checkout, its agent framework, or companion files are available.
- Apply the portable prompt/task-feasibility checks contained in `skeptic.md`.
- Read optional supplied extensions such as `skeptic-questions.md` or another domain/task question file only when provided or explicitly referenced.
- Extensions may expand detection but must not weaken, replace, or override the core.

Repository-integrated Skeptic:
- Use the entry map above to load the applicable agent or question companions.
- `skeptic.md` remains authoritative for reasoning, evidence, decisions, safe action, verification, and RunSkeptic output.
- Files under `agents/` govern repository-specific orchestration, role boundaries, delegation, persistence, handoffs, completion reserves, integration, and closure.
- Repository-specific orchestration machinery should not be copied into every standalone Skeptic invocation.

Ownership:

- `skeptic.md` is authoritative for RunSkeptic behavior, its specialized receipt, and output categories.
- `agents/lead-agent-prompt.md` is authoritative for the lightweight Lead role, including direct execution, optional delegation, downstream acceptance, and deterministic validation.
- `agents/task-prompt.md` is authoritative for proportional Task Prompt content and workflow guidance.
- `agents/task-prompt-builder.md` is authoritative for the objective-or-plan-to-Task-Prompt build operation and its four aliases.
- `agents/target-task.md` is authoritative for the canonical Target Task lifecycle, context protection, and Sufficient Handoff contract.
- `agents/otp-protocol.md` remains the compatibility surface for the legacy `OTP:` name and must delegate to the canonical Target Task contract without weakening it.
- `agents/otp-protocol.md` is authoritative for the `OTP:`/`TT:` triggers and the compatibility plan-seal-execute-validate-review-accept-receipt vocabulary; canonical semantics remain in `agents/target-task.md`.
- `agents/model-routing.md` is authoritative for portable cost-aware model routing and escalation guidance.
- `agents/agent-return.md` is authoritative for the universal delegated model-agent completion envelope.
- `agents/boundary-agent.md` is authoritative for conditional boundary processing, artifact-first context discipline, and truthful context-isolation status.
- Editing `skeptic.md` requires explicit authority. Do not edit "skeptic.md" unless explicitly authorized.

Architectural boundary:

This repository is a reusable, normally read-only prompt and review library. It defines portable guidance; it does not own runtime state, workflow storage, or task workspaces. Task-specific state is selected and owned by the invoking runtime or actual task environment, not by this checkout.
