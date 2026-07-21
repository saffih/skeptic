# Agent Instructions

Entry map. Load only the artifact needed for the current use:

- Review an artifact or decision (including "RunSkeptic" or Skeptic review)
  -> `skeptic.md`
- Construct or gate an agent prompt
  -> `agents/lead-agent-prompt.md`
- Execute serious multi-phase work through terminal DONE
  -> `agents/task-prompt.md`

Ownership:

- `skeptic.md` is authoritative for RunSkeptic behavior and output categories.
- `agents/lead-agent-prompt.md` is authoritative for the Lead role, prompt architecture, and prompt gating.
- `agents/task-prompt.md` is authoritative for Task Prompt construction, execution control, and closure.
- Editing `skeptic.md` requires explicit authority. Do not edit "skeptic.md" unless explicitly authorized.

Architectural boundary:

This repository is a reusable, normally read-only prompt and review library. It defines portable execution contracts; it does not own runtime state, workflow storage, or task workspaces. Task-specific state is selected and owned by the invoking runtime or actual task environment, not by this checkout.
