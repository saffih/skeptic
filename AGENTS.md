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
  - These four aliases route here first; Task Prompt construction is `agents/task-prompt-builder.md`'s job.

Ownership:

- `skeptic.md` is authoritative for RunSkeptic behavior and output categories.
- `agents/lead-agent-prompt.md` is authoritative for the lightweight Lead role, including direct execution, optional delegation, and deterministic validation.
- `agents/task-prompt.md` is authoritative for proportional Task Prompt content and workflow guidance.
- `agents/task-prompt-builder.md` is authoritative for the objective-or-plan-to-Task-Prompt build operation and its four aliases.
- Editing `skeptic.md` requires explicit authority. Do not edit "skeptic.md" unless explicitly authorized.

Architectural boundary:

This repository is a reusable, normally read-only prompt and review library. It defines portable guidance; it does not own runtime state, workflow storage, or task workspaces. Task-specific state is selected and owned by the invoking runtime or actual task environment, not by this checkout.
