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

1. Read the current `AGENTS.md`, `agents/lead_agent.md`, `workflows/task_prompt.md`, and only the additional evidence needed for the objective.
2. Identify the objective, scope, constraints, success criteria, permitted actions, and relevant prohibited actions.
3. Ask for clarification only when a material ambiguity would make the result unsafe, unverifiable, or outside authority.
4. Produce the smallest Task Prompt that preserves the required outcome, safety boundaries, and verification.
5. Check the result for fidelity to the objective, internal contradictions, unnecessary process, and a realistic validation path.
6. For substantive prompts, check routing and return conformance before describing the prompt as execution-ready.

The conformance check asks whether deterministic work was identified where appropriate; delegation is justified and roles are bounded; requested model class and reasoning effort are proportionate; delegated roles do not inherit the Lead model implicitly; strongest-model use or escalation is justified; acceptance and deterministic validation are sufficient without duplication; every delegated model role has a dispatch ID and Agent Completion Envelope; envelope validation is followed by independent work acceptance; material Boundary Agent use is conditional and routed at the lowest reliable cost; substantial reusable context is artifact-backed when practical; context-isolation claims are evidence-based; recursive delegation carries transitive subtree obligations and compact upward reporting; every RunSkeptic invocation is followed by receipt validation; and frozen benchmark variables remain controlled.

For a prompt that designates or executes a Target Task, conformance additionally
requires the ordered lifecycle: distinct bounded Planner dispatch, envelope
validation, complete Planner-produced plan, RunSkeptic review and receipt
validation, Planner repair after every material plan change, final unchanged-plan
Lead acceptance, and execution exactly once. supplied plans are Planner input only; Lead and
same-runtime planning cannot substitute. The Planner cannot recurse or authorize
execution. Missing the mandatory stage is `PROMPT_CONFORMANCE_ACTION_REQUIRED`
or `PROMPT_CONFORMANCE_UNVERIFIABLE`, never ready. A Target Task prompt whose
lifecycle omits execution exactly once is missing the mandatory stage and must
not receive `PROMPT_CONFORMANCE_READY`. Ordinary non-Target work
remains proportional.

For substantive prompts where model cost may be material, also check that the
prompt selects the least expensive reliable starting route, requires the
`EXECUTION_ROUTING_NOTICE`, identifies likely premium roles early, and either
pre-authorizes each premium stage with the exact bounded fields required by
`agents/model_routing_policy.md` or stops for explicit owner authorization at a
`MODEL_ESCALATION_CHECKPOINT`. Require zero automatic premium retries by
default, a minimum escalation package, no repetition of completed economical
work, and return to an economical route after premium judgment.

For a substantive build, use the proportional planning and RunSkeptic guidance in `workflows/task_prompt.md`. A materially changed plan is reviewed again; harmless wording changes are not.

## Output

Return the Task Prompt unexecuted.

For a substantive Task Prompt, append one compact status:

- `PROMPT_CONFORMANCE_READY`
- `PROMPT_CONFORMANCE_ACTION_REQUIRED`
- `PROMPT_CONFORMANCE_UNVERIFIABLE`

Briefly identify any material assumption or unresolved blocker. Do not add delegation, receipt, persistence, review, or state machinery unless it materially improves correctness, safety, continuity, or verification for the specific task.

When model cost may be material, append a compact launch recommendation after
the unexecuted Task Prompt: recommended starting model or class, recommended
effort, potential later premium role, whether that role is pre-authorized, and
confirmation that execution will stop before unapproved premium work. Do not
add this cost machinery to trivial read-only prompts or one-command
deterministic work.
