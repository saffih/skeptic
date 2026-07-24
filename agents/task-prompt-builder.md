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
6. For substantive prompts, check routing and return conformance before describing the prompt as execution-ready.

The conformance check asks whether deterministic work was identified where appropriate; delegation is justified and roles are bounded; requested model class and reasoning effort are proportionate; delegated roles do not inherit the Lead model implicitly; strongest-model use or escalation is justified; acceptance and deterministic validation are sufficient without duplication; every delegated model role has a dispatch ID and Agent Completion Envelope; envelope validation is followed by independent work acceptance; every RunSkeptic invocation is followed by receipt validation; and frozen benchmark variables remain controlled.

For a substantive build, use the proportional planning and RunSkeptic guidance in `agents/task-prompt.md`. A materially changed plan is reviewed again; harmless wording changes are not.

## Output

Return the Task Prompt unexecuted.

For a substantive Task Prompt, append one compact status:

- `PROMPT_CONFORMANCE_READY`
- `PROMPT_CONFORMANCE_ACTION_REQUIRED`
- `PROMPT_CONFORMANCE_UNVERIFIABLE`

Briefly identify any material assumption or unresolved blocker. Do not add delegation, receipt, persistence, review, or state machinery unless it materially improves correctness, safety, continuity, or verification for the specific task.
