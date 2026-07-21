# Agent Instructions

Entry map. Load only the artifact needed for the current use:

- Review an artifact or decision (including "RunSkeptic" or Skeptic review)
  -> `skeptic.md`
- Construct or gate an agent prompt
  -> `agents/lead-agent-prompt.md`
- Execute serious multi-phase work through terminal DONE
  -> `agents/task-prompt.md`
- Create an execution Task Prompt from a user objective or verified plan
  -> `agents/task-prompt-builder.md`
  - Aliases (text after the alias is the objective): `TP: <objective>`, `Create task prompt for: <objective>`, `Create a task prompt for: <objective>`, `Task prompt for: <objective>`
  - These four aliases route here first; they take precedence over the generic prompt-construction route above, which remains the fallback for other prompt architecture or gating work.

Ownership:

- `skeptic.md` is authoritative for RunSkeptic behavior and output categories.
- `agents/lead-agent-prompt.md` is authoritative for the Lead role, prompt architecture, and prompt gating.
- `agents/task-prompt.md` is authoritative for Task Prompt construction, execution control, and closure.
- `agents/task-prompt-builder.md` is authoritative for the objective/verified-plan-to-Task-Prompt build operation and its four aliases.
- Editing `skeptic.md` requires explicit authority. Do not edit "skeptic.md" unless explicitly authorized.

Architectural boundary:

This repository is a reusable, normally read-only prompt and review library. It defines portable execution contracts; it does not own runtime state, workflow storage, or task workspaces. Task-specific state is selected and owned by the invoking runtime or actual task environment, not by this checkout.
