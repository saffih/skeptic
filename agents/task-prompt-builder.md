# Task-Prompt Builder

## Purpose

Turn a user objective or an existing plan into one concise, execution-ready Task Prompt. The builder creates the prompt; it does not execute it.

## Invocation aliases

These forms are equivalent. The text after the alias is the objective:

- `TP: <objective>`
- `Create task prompt for: <objective>`
- `Create a task prompt for: <objective>`
- `Task prompt for: <objective>`

## Workflow

1. Read the current `AGENTS.md`, `agents/lead-agent-prompt.md`, `agents/task-prompt.md`, and only the additional evidence needed for the objective.
2. Identify the objective, scope, constraints, success criteria, permitted actions, and relevant prohibited actions.
3. Ask for clarification only when a material ambiguity would make the result unsafe, unverifiable, or outside authority.
4. Produce the smallest Task Prompt that preserves the required outcome, safety boundaries, and verification.
5. Check the result for fidelity to the objective, internal contradictions, unnecessary process, and a realistic validation path.

For a substantive build, use the proportional planning and RunSkeptic guidance in `agents/task-prompt.md`. A materially changed plan is reviewed again; harmless wording changes are not.

## Output

Return the Task Prompt unexecuted. Briefly identify any material assumption or unresolved blocker. Do not add delegation, receipt, persistence, review, or state machinery unless it materially improves correctness, safety, continuity, or verification for the specific task.
