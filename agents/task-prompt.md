# Task Prompt

A task prompt should state the smallest set of information needed to perform the work reliably.

Include:

- objective;
- scope;
- constraints;
- success criteria;
- permitted actions;
- prohibited actions when relevant.

Do not add process requirements that do not materially improve correctness, safety, or verification.

## Default task workflow

For a substantive repository task:

1. create a concise plan;
2. run RunSkeptic on the plan once;
3. resolve material findings;
4. execute the plan;
5. run relevant deterministic checks;
6. report changes, validation, deviations, and blockers.

Additional RunSkeptic review is required only when:

- the plan changes materially;
- a serious unexpected risk appears;
- deterministic validation is insufficient;
- the task is explicitly high-risk;
- prior evidence demonstrates that ordinary validation is unreliable.

## Trigger guidance

Use the workflow proportionally.

### Trivial read-only work

Examples:

- reading a file;
- reporting repository status;
- retrieving a commit identity;
- running one already-specified deterministic command.

A written plan and RunSkeptic are optional unless risk or ambiguity justifies them.

### Small bounded change

Create a short plan, run RunSkeptic once on the plan, implement, and run focused checks.

### Normal implementation

Create a plan, run RunSkeptic once on the plan, implement, and run focused checks plus the relevant broader suite.

### High-risk change

Create a plan, run RunSkeptic on the plan, use stronger deterministic validation, and obtain an independent final review when it provides meaningful additional assurance.

### Material plan change

Update the plan and rerun RunSkeptic only on the materially changed plan.

## Delegation

Delegation is optional.

Use it when isolation, specialization, parallelism, or independent review provides clear value.

Do not delegate merely to satisfy ceremony.

A delegated result should normally include:

- outcome;
- changed files or produced artifact;
- validation performed;
- blockers;
- recommended next action.

Harmless extra prose or formatting differences do not invalidate useful work.
