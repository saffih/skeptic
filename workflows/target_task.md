# Target Task — Claude Code MVP

This is the authoritative runtime workflow for a user message whose first
meaningful token is exactly `TT:`. Claude Code auto-loads root `CLAUDE.md`,
which imports `AGENTS.md`; `AGENTS.md` routes the trigger here.

The previous Target Task prototype is removed. Historical files under
`plans/`, `docs/`, and `experiments/` are evidence only unless this workflow
explicitly names them as current authority.

## MVP boundary

The MVP is sequential: one repository, one task ID, one sealed linear Plan,
one current step, and one unresolved operation. It uses Claude Code's actual
subagent/command mechanisms and the deterministic contracts under
`concepts/target_task/`.

The isolation claim is protocol-level and observable:

- a child role receives bounded file references and routing metadata;
- its complete substantive output is written to a task artifact;
- it returns only a compact validated receipt;
- Boundary rejects body-bearing, oversized, mismatched, or synthetic
  production receipts;
- Luna holds compact references and status only.

Do not claim hard platform isolation. Report
`HIDDEN_HOST_CONTEXT_ISOLATION: UNKNOWN`.

## Trigger and one authoritative task root

1. Ignore whitespace before the exact `TT:` token.
2. The mission is the exact host-provided Unicode suffix after `TT:`. Do not
   trim, normalize, summarize, or rewrite it. Reject only when the suffix has
   no non-whitespace character.
3. Resolve one external `TASKS_ROOT`, create one `TASK_ID`, and use
   `TASKS_ROOT/TASK_ID` as the sole authority for mission, ledger, Plan
   versions, sealed Plan, steps, requests, results, reviews, findings,
   receipts, command logs, routing evidence, and checkpoints.
4. Call `concepts.target_task.trigger.bootstrap_task` before the durable Lead
   receives control.
5. Never commit task-run artifacts or a task-specific sealed Plan into the
   source repository.

A fresh session uses `rediscover_task(TASKS_ROOT, TASK_ID)` and does not depend
on previous conversation state.

## Models and routing evidence

Persist a role-by-role routing manifest containing requested and observed model
and effort. If the host does not expose an observed value, record `UNKNOWN`.

- Durable Lead: Claude Sonnet 5, smallest reliable effort for compact control.
- Planner: Claude Opus 4.8 XHIGH; fallback Sonnet 5 XHIGH.
- Plan Skeptic: Claude Opus 4.8 XHIGH; fallback Sonnet 5 XHIGH.
- Final Skeptic: Claude Opus 4.8 XHIGH; fallback Sonnet 5 XHIGH.
- Workers: sealed-Plan choice; default Sonnet 5 MEDIUM or HIGH.

Every Plan Fix Loop pass and final Find Loop pass uses a fresh reviewer
subagent/context. Pass only validated references, prior finding-set reference,
and compact binding metadata through Luna.

## Mandatory lifecycle

```text
mission persisted
-> independent Planner creates complete Plan
-> RunSkeptic Fix Loop on complete Plan
-> three consecutive qualifying unchanged passes
-> exact Plan accepted and sealed
-> execute sealed linear Plan
-> final open execution step runs bounded real-host smoke + negative probe
-> deterministic validation of execution and smoke evidence
-> candidate commit/tree frozen
-> read-only RunSkeptic Find Loop over exact frozen candidate
-> integrate only when clean and mechanically possible
-> compact terminal receipt
```

## Plan gate

Before implementation:

1. Dispatch an independent Planner using references to the mission, repository
   identity/evidence, authority, and applicable contracts.
2. Persist every complete Plan version under the task root.
3. For every RunSkeptic Fix Loop invocation, freshly read current
   `skeptic.md`, apply its complete recipe, consider every required Thinker,
   persist the full review and compact receipt, and bind it to exact
   Plan/source hashes.
4. A material finding requires a new complete Planner-produced Plan version.
   Reset the qualifying count after every material change. Repair runs and
   delta reviews never count.
5. Seal only after three qualifying passes on the same unchanged Plan with no
   unresolved ACTION, DECOMPOSE path, CONFLICT, review-required status, or
   blocking unknown.

Once sealed, the Plan never changes in that run. If it cannot be completed
safely, stop; do not replan.

## Sequential execution

Use `StepCursor` and Boundary's functions:

- `new_step_cursor`
- `admit_operation`
- `record_validated_host_outcome`
- `retry_operation`
- `recover_operation`
- `advance_step`

Required semantics:

- one current step and one unresolved operation;
- admission creates a new operation ID and increments attempt;
- COMPLETE becomes `STEP_AWAITING_ADVANCE`, not automatic advancement;
- Luna requests `ADVANCE`, consuming exactly that successful operation;
- duplicate `ADVANCE` fails closed;
- FAILED permits bounded `RETRY` or `STOP`;
- UNKNOWN permits `RECOVER` or `STOP`, never blind retry;
- execution completes only after every sealed Plan step is accepted.

Every operation writes an immutable request, full result, dispatch evidence,
and compact host receipt under the task root. Production always calls
`validate_host_role_receipt(..., allow_test_synthetic=False)` through
`record_validated_host_outcome`.

Synthetic receipts are legal only through explicit unit-test injection with
`allow_test_synthetic=True`. They must never advance a production Fix Loop,
Find Loop, step cursor, validation gate, or integration gate.

## Final open execution step: real-host smoke

The sealed Plan makes the real-host smoke and body-bearing-return negative
probe its final open execution step. A smoke defect may be repaired only
within that already-sealed step before execution completes; the Plan itself
never changes.

`scripts/target_task_smoke.sh` runs only with explicit owner authorization. It
uses a disposable local clone with remotes removed, bounded turns, explicit
allowed/disallowed tools, no `--dangerously-skip-permissions`, and before/after
proof that the original repository and refs did not change.

The smoke proves the candidate clone auto-loads `CLAUDE.md`, routes `TT:`,
persists the exact mission, performs at least one real Planner,
Skeptic/Reviewer, and Worker dispatch, advances two distinct steps explicitly,
rediscovers state from task root in a fresh context, and rejects a body-bearing
or oversized return without durable advancement.

Test-only deterministic loop receipts may reduce repeated smoke cost, but
production must reject them and one real dispatch of each required role class
remains mandatory.

## Deterministic validation and freeze

After every Plan step including smoke is accepted, verify sealed Plan identity,
exactly-once step acceptance, no unresolved operation, artifact identities,
protected paths, direct Lead bypass rejection, focused/full tests, original
repository/ref preservation, and candidate commit/tree identity. Persist the
validation receipt, then freeze the exact candidate. No code, test, Plan, or
candidate change is legal after freeze.

## Final RunSkeptic Find Loop

Run complete fresh read-only reviews of the exact unchanged candidate. Re-read
current `skeptic.md` every pass, re-evaluate accumulated findings, and persist
full reviews plus compact receipts. Stop after three consecutive complete
reviews add no meaningful finding and make no material change to an existing
finding.

- stable with no material findings -> `VERIFIED_CLEAN`;
- stable with findings -> `QUALITY_FINDINGS_REPORTED`, integration blocked.

Convergence is not cleanliness. Do not repair after freeze; repair requires a
new run and Plan.

## Integration and public evidence

Integrate only when the exact reviewed candidate is verified clean and a
non-force fast-forward preserves its tree. Push success alone is insufficient;
fetch and verify remote commit and tree.

Before merge, update the PR title/body so it no longer claims a reference-only
runtime or treats historical `plan-002` as qualified. Identify the accepted
MVP Plan, deterministic tests, smoke evidence, final Find Loop result, and the
protocol-isolation limitation.

The terminal receipt includes `ROUTING_EVIDENCE_REF`, pointing to the per-role
requested-versus-observed routing manifest.
