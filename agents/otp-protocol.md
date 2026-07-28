# OTP: Optimized Task Prompt Protocol

OTP activates a full plan-seal-execute-validate-review-accept-receipt
lifecycle for one Target Task. It is provider-neutral: any capable model or
runtime, including Claude, must be able to complete it using this file alone.
This file makes no assumption about a specific model name, tool name,
delegation vocabulary, or receipt wording belonging to any one provider.

## Triggers

Two forms activate OTP. Recognition is based on the leading reserved prefix
only, tolerant of ordinary capitalization (`OTP:`, `Otp:`, `otp:`, `TT:`,
`Tt:`, `tt:`) and of surrounding whitespace (leading/trailing spaces or blank
lines around the prefix line). The text after the prefix, once the optional
colon and following whitespace are removed, is the Target Task.

- `OTP:` is the explicit trigger. `OTP: <Target Task>` activates OTP with the
  given Target Task.
- `TT:` is the compact trigger. `TT: <Target Task>` is fully equivalent to
  `OTP: <Target Task>`: it activates OTP and supplies the same Target Task.
- `OTP:\nTT:` (a line that is exactly the bare `OTP:` token, optionally
  followed by blank or whitespace-only lines, then a line beginning with
  `TT:`) is valid. It is redundant, not a double activation: the Target Task
  is the text carried by the `TT:` line, and OTP activates exactly once.
- A plain task with neither leading prefix does not invoke OTP, no matter
  how much it resembles one. Do not infer activation from content or intent.

Read this file before interpreting or responding to either trigger. If it
cannot be read, stop visibly with `OTP_PROTOCOL_UNAVAILABLE` and do not claim
OTP compliance.

## Roles

OTP uses two roles: **Body**, which coordinates, accepts, seals, executes,
validates, and reports; and **Brain**, which plans only. The roles are
functional, not provider-specific agent names. When no delegation is used,
one model performs both roles sequentially in the same session and must
still record which role is active at each phase. When delegation is used,
follow `agents/agent-return.md` for the completion envelope and
`agents/model-routing.md` for routing; neither requires a specific provider,
model name, or tool.

The file-based implementation in `experiments/body-brain-artifacts/` (task,
body, brain, plan, receipt) is one optional way to carry this lifecycle
across files or sessions. It is not required for a bounded single-session
OTP task; this file's inline lifecycle is sufficient on its own.

## Lifecycle

1. **Activation.** Parse the trigger and Target Task as described above.
   Record the trigger form used (`OTP:`, `TT:`, or `OTP:+TT:`).
2. **Planning cycle.** Brain produces one Acceptance Plan covering: task
   understood (identity, objective, scope, constraints, prohibitions);
   material assumptions and unknowns; ordered execution steps with
   objective, inputs, actions, expected outputs, and validation per step;
   required decision points; the final-review mode (see below); and success
   criteria. Exactly one planning cycle runs unless replanning is required.
3. **Body acceptance.** Body checks the Acceptance Plan for task-identity
   match, presence of every required section, no unauthorized action, and
   mechanical executability. Body does not rewrite or semantically improve
   the plan.
   - If the plan is accepted, Body seals it: record a stable content
     identity (for example a hash) for the Acceptance Plan, and treat it as
     immutable from this point. Computing and recording that identity is
     protocol bookkeeping, not part of the Target Task's own deliverable:
     it may use ordinary session-local working state (for example a
     scratchpad) without that counting against a Target Task's file-scope
     constraints, which bind the deliverable, not OTP's own record-keeping.
   - If the plan has a material defect, Body rejects it and Brain replans.
     Replanning is automatic at most once. A second rejection stops
     execution and reports `OTP_BLOCKED` with the reason instead of looping.
4. **Execution.** Body executes the sealed Acceptance Plan's steps in order,
   preferring deterministic tools, and records status, actions, outputs, and
   any deviation for each step.
5. **Deterministic validation.** Body runs the exact checks the plan's steps
   named (tests, reproduction, diff review, output comparison, or
   equivalent). Deterministic validation always runs before judgment review.
6. **Final-review mode.** The Acceptance Plan must name exactly one
   final-review mode, chosen for the task's risk:
   - `DETERMINISTIC_ONLY` — deterministic validation is sufficient; no
     separate judgment pass runs. Use only for low-risk, low-ambiguity work.
   - `SELF_REVIEW` — Body re-reads the Target Task, the sealed Acceptance
     Plan, and the deterministic results, and judges whether the result
     satisfies the success criteria and constraints.
   - `RUNSKEPTIC_REVIEW` — Body invokes RunSkeptic (per `skeptic.md`) against
     the change or decision and resolves material findings before accepting.
   Body executes the mode the plan named. Substituting a different mode at
   execution time is a plan deviation and must be recorded as such.
7. **Final acceptance.** Body compares the final plan-content identity to
   the one sealed at step 3; a mismatch stops the task. Body then records
   the success-criteria results and a terminal status: `OTP_ACCEPTED` when
   every success criterion and constraint is met, `OTP_REJECTED` when they
   are not, or `OTP_BLOCKED` when execution could not reach a judgment.
8. **Receipt.** Body returns a compact receipt (fields below).

## Receipt

An OTP receipt states:

- trigger form used (`OTP:`, `TT:`, or `OTP:+TT:`) and the Target Task;
- requested routing: the model or model class and reasoning effort the
  Target Task specified or, absent that, the least expensive route expected
  to complete it reliably per `agents/model-routing.md`;
- observed routing: the actual model, version, and effort when the runtime
  exposes them, otherwise the literal value `ACTUAL_ROUTING_UNKNOWN`;
  requested and observed routing are always reported as two distinct
  values, never merged into one;
- planning cycles run (1, or 2 with the replanning reason) and the sealed
  Acceptance Plan's content identity;
- execution summary: steps run, outputs, and deviations;
- deterministic validation performed and its result;
- final-review mode executed and its result;
- final acceptance status (`OTP_ACCEPTED`, `OTP_REJECTED`, or
  `OTP_BLOCKED`) with reasons for anything other than `OTP_ACCEPTED`;
- blockers, if any.

## Compatibility

- `OTP:` remains fully supported on its own; nothing in this file narrows or
  replaces that trigger.
- `TT:` is an additional, equivalent compact trigger, not a separate
  protocol.
- This file does not require any provider-specific model name, tool,
  delegation term, or receipt field. `agents/agent-return.md` and
  `agents/model-routing.md`, which this file reuses, are themselves
  provider-neutral.
- OTP does not weaken `skeptic.md`'s RunSkeptic contract; `RUNSKEPTIC_REVIEW`
  invokes it unchanged.
