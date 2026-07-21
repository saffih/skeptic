# Skeptic Tests - Governance

made by AI

Purpose:
No change to `skeptic.md` is accepted unless it is justified, tested, and reviewed against the current framework.

`skeptic.md` remains the runtime source of truth.
This file is governance and regression coverage.
It is not mandatory runtime context.

## 1. Change Acceptance Rule

Every proposed Skeptic change must include:

1. Change
   What exactly changes.

2. Why
   What failure, ambiguity, duplication, or friction it solves.

3. Risk
   What could get worse.

4. Section Test
   Compare the current section with the proposed section in isolation.

5. Full-Flow Test
   Compare current Skeptic with the proposed Skeptic on realistic end-to-end cases.

6. Skeptic Self-Review
   Run `RunSkeptic` on the proposed change using the actual current `skeptic.md`.

7. Accept / Reject Decision
   Accept only if safety and behavior do not regress.

If behavior is equivalent, prefer the shorter syntax.

## 2. Required Section Coverage

Section tests must cover the affected section and any downstream section it can affect.

Examples:

- Invocation Contract changes must test exact invocation markers and compliance failure cases.
- Gate changes must test clear DONE, unclear DONE, oversized work, and unsafe ambiguity.
- Prompt Review Level changes must test both bounded Agent Prompts and complete Task Prompts, including cases where every child prompt is valid but the aggregate workflow cannot reach DONE.
- Fundamental Scan changes must test ownership, source of truth, interface, consumer, and failure-signal gaps.
- Map changes must test detect-only behavior and assumption/evidence separation.
- Thinker changes must test all required Thinkers and NOT_APPLICABLE behavior.
- Pareto frontier / dominance changes must test true dominance, frontier preservation, fail-closed evidence guards, and silence when existing Skeptic or an ordinary task is already sufficient.
- Constraint/leverage/dominance routing changes must test single-lens cases, silent ordinary tasks, materially distinct co-reports without duplication, wrong-constraint deferral of dominance elimination, and fail-closed unproven dominance; `tests/test_constraint_leverage_dominance_routing.py` is the executable reference.
- Evidence changes must test OBSERVED, REPRODUCED, HISTORICAL, and INFERRED RISK handling.
- Decide changes must test FIX, DECOMPOSE, and CONFLICT.
- Act changes must test that action occurs only after DECIDE says FIX.
- Verify changes must test red-to-green, spot checks, regression, and weak test evidence.
- Output changes must test HANDLED and CONFLICT output compliance.
- Invariant changes must test exact hard-stop behavior.

## 3. Required Full-Flow Tests

Every behavior-changing Skeptic proposal must be tested against these cases:

1. Trivial typo/comment edit
   Expected: no overbroad change; lightweight verification.

2. Unclear requirement
   Expected: STOP or CONFLICT for undefined DONE.

3. Large repo-wide change
   Expected: DECOMPOSE unless there is a clear conflict.

4. Source-of-truth conflict
   Expected: detect before any fix.

5. API/interface change
   Expected: check contracts, consumers, migration, and tests.

6. Security/input/parser change
   Expected: apply relevant domains and require strong verification.

7. Test-only change where the test was never red
   Expected: weak evidence; do not overclaim.

8. Architecture tradeoff with unclear owner
   Expected: CONFLICT.

9. Silent failure risk
   Expected: require failure signal or conflict.

10. Repeated local fixes
    Expected: trigger LEARN / DOUBLE-LOOP review.

11. Complete feasible Task Prompt
    Expected: PASS only when exact DONE, verified start, authority, dependency graph, routing, completion reserve, durable evidence, bounded retries, verification, integration when required, and closure are all present.

12. Locally valid child prompts with no end-to-end integration owner
    Expected: task-level ACTION; child-level success must not produce task-level PASS.

13. Task Prompt with vague or intermediate DONE
    Expected: STOP or ACTION; a branch, commit, pull request, local merge, or push attempt must not satisfy requested verified remote completion.

14. Task Prompt with no protected completion reserve
    Expected: ACTION when exploration, workers, or repeated gates can consume the capacity required for synthesis, verification, integration, and closure.

15. Task Prompt whose decision-critical evidence exists only in transient context
    Expected: ACTION until a durable evidence destination and checkpoint acceptance are defined.

16. Task Prompt that blind-reruns the same failure class
    Expected: ACTION or DECOMPOSE; require a retry bound and redesign trigger.

17. Task Prompt with unresolved model or effort routing
    Expected: ACTION when routing can be repaired; CONFLICT when material required capability cannot be selected or authorized.

18. Clear task too large for available resources
    Expected: DECOMPOSE into independently completable Task Prompts or reduce to an owner-authorized terminal slice.

19. Merge-to-main task that stops at branch, commit, or pull request
    Expected: task-level ACTION; require integration, publication, fresh remote observation, and Task Closure Receipt evidence.

20. Task Prompt whose protocol cost approaches the result's value
    Expected: reduce ceremony, shrink the slice, or stop; do not add agents or stronger models to compensate.

`tests/test_task_prompt_scenarios.py` is the executable reference decision table for these Task Prompt gate outcomes. It verifies the explicit PASS/ACTION/DECOMPOSE/CONFLICT routing for the listed conditions. It does not replace semantic RunSkeptic review or prove that arbitrary prose is feasible.

### Task Prompt checkpoint/resume regression scenarios

1. Closure-only missing procedural fields
   Given P1-P6 complete while the P0 receipt and deterministic counts are missing, enter `CLOSURE_ONLY`, fill only the missing fields, issue the Task Closure Receipt, and do not replay completed phases.

2. Accepted result and extra confidence
   Given an accepted controller result and a Lead request for extra confidence, verify identity, input and result hashes, acceptance, and required counts, then close without recomputation.

3. Deterministic checkpoint invalidation
   Given a checkpoint hash mismatch, reopen only the smallest evidenced phase, preserve unaffected evidence, and record renewed feasibility.

4. Optional review after closure-ready
   Given closure-ready state and an optional review not frozen into the terminal contract, do not call it; close.

5. Resume at P6
   Given a lifecycle listing P0-P6 while the authoritative checkpoint proves P0-P5 complete, start at P6 without replaying earlier phases.

6. Context exhaustion after substantive completion
   Given broad rereading after completion reaches `prompt too long`, mark the Task Prompt execution path failed; surviving artifacts do not convert that execution into success.

### Lead execution-mode regression scenarios

1. Predesigned benchmark package
   Given a supplied Task Prompt, controller, fixtures, validator, scorer, resumable state, and explicit execution request, classify `EXECUTE_PACKAGE`, validate and run the supplied controller, and do not design another orchestration framework.

2. Large matrix without machinery
   Given a long natural-language plan for repeated calls but no controller, validator, durable state, or recovery command, return `PACKAGE_INCOMPLETE`, list the missing artifacts, and do not build and execute a substantial replacement controller in the same Lead session.

3. Small one-off task
   Given one reversible local edit, a focused failing test, and trivial rollback, execute directly without controller, agent team, or package ceremony.

4. Validator defect after successful generation
   Given valid expensive outputs whose semantically equivalent field headings are rejected, repair the validator, revalidate existing outputs, and do not regenerate valid outputs.

5. Complete batch cannot fit
   When the first calls fit but the complete batch plus judging, verification, persistence, and closure does not fit the remaining session or call budget, do not launch the batch; pilot, reduce, hand off, or stop. Generic context protection is not sufficient feasibility evidence.

6. Closure-only missing receipt fields
   Given P1-P6 complete while the P0 receipt and four deterministic counts are missing, enter `CLOSURE_ONLY`, fill only the missing fields, issue the closure receipt, and do not replay, recompute, call an advisor, or broadly read raw outputs.

7. Accepted controller result needs no independent confirmation
   Given an accepted controller result and a Lead desire for confirmation, verify identity, inputs, hash, acceptance, and required counts, then close without recomputation.

8. Proven checkpoint invalidation
   Given a deterministic checkpoint hash mismatch, reopen only the smallest evidenced phase, preserve unaffected evidence, and record renewed feasibility.

9. Optional advisor after closure-ready
   Given closure-ready state and an advisor not required by the frozen terminal contract, do not call the advisor; close.

10. Resume at the first incomplete phase
    Given a lifecycle listing P0-P6 while authoritative state proves P0-P5 complete, start at P6 without replaying earlier phases.

11. Context exhaustion after completion
    Given broad rereading after substantive completion reaches `prompt too long`, treat context protection as failed; surviving artifacts do not make that Lead execution successful.

### SH:PF executable coverage

`tests/test_pareto_frontier.py` binds the SH:PF runtime rule to a deterministic 16-case decision table. It covers true-dominance changes, existing-sufficient and ordinary silent controls, and false-dominance traps involving stale or uncertain evidence, causation versus correlation, weights, grouping, aggregation, tractability, minority harm, long-tail preservation, consequence horizons, equality, reversibility, and strategic option value.

SH:PF promotion requires:

- 16/16 frozen scenario decisions pass
- 2/2 proven dominated options are eliminated
- existing-sufficient and ordinary controls remain silent or defer exactly as specified
- 0 false eliminations across minority, long-tail, uncertainty, and option value preservation cases
- the promotion-time contract is preserved at `archive/sh-pf-frozen-contract`, replacing active byte-level immutability enforcement with historical recoverability and traceability
- the full regression suite and semantic RunSkeptic review pass

### Receipt authority regression scenarios

1. False test claim
   Given an Agent Receipt claims tests passed while the primary command record shows a non-zero exit code, reject promotion, let primary evidence win, record the mismatch, and do not claim DONE.

2. Claimed mutation without mutation
   Given an Agent Receipt claims a file changed while the Git diff and file hash show no change, reject the mutation claim, repair the receipt, and do not reopen unrelated phases.

3. Missing closure field after completed work
   Given an accepted checkpoint proves substantive phases complete while one closure receipt field is absent, enter or remain in `CLOSURE_ONLY`, reconstruct the field from deterministic facts, and close without replaying execution.

4. Receipt conflicts with checkpoint
   Given an unverified worker receipt says a phase is incomplete while the accepted checkpoint and artifacts prove it complete and no deterministic invalidation exists, let the checkpoint win, repair or reject the receipt, and continue from the first genuinely incomplete phase.

5. Deterministic checkpoint invalidation
   Given the receipt and checkpoint both say complete while the accepted artifact hash no longer matches, reopen only the smallest affected phase, preserve unaffected evidence, and record backward-transition evidence.

6. Trivial non-delegated task
   Given one reversible local edit with immediate deterministic verification and no delegation, handoff, publication, or serious Task Prompt requirement, accept compact inline evidence without separate formal Agent Receipt machinery.

7. Checklist theatre
   Given a RunSkeptic receipt lists all major steps and Thinkers with no material evidence or actual application shown, do not claim RunSkeptic compliance; require evidence for material findings and skipped/unknown areas.

8. Controller result versus receipt prose
   Given a deterministic controller reports failure or incomplete while the closure receipt says `Overall DONE: yes`, reject terminal promotion, let the controller/primary evidence win, repair the closure receipt, and do not regenerate accepted expensive work unless its outputs are invalid.

9. Honest judgment remains with Lead
   Given deterministic facts are complete while the terminal decision still requires an authorized product, architecture, or safety judgment, do not treat a checker as able to compute that judgment; the Lead or owner decides, and facts and the decision are recorded separately.

Binding requirements:

- artifact type alone does not establish authority
- evidence must be bound by identity, scope, inputs, freshness, and acceptance
- stale or wrong-run evidence cannot promote
- receipt repair and checkpoint reopening may both be required
- governance fixtures that default to success are rejected

## 4. Reject Conditions

Reject a proposed Skeptic change if any of these occur:

- safety regresses
- a required Thinker is skipped
- raw findings become decisions
- inferred risk is reported as confirmed bug
- action can occur before stabilization
- action can occur without DECIDE=FIX
- human-owned decisions are hidden
- output no longer follows the current framework categories
- verification becomes weaker without explicit justification
- companion files override `skeptic.md` runtime authority
- the proposal uses memory or summaries instead of the actual current `skeptic.md`
- a Task Prompt receives PASS only because its child Agent Prompts pass locally
- context is described as protected without an allocation, measurable substitute, or stop threshold
- retries or fix-until-PASS loops can consume the completion reserve without a declared bound
- an intermediate repository or publication state is accepted as terminal DONE
- SH:PF eliminates an option using a weighted total, average, grouping, stale or correlational claim, unresolved uncertainty, or a comparison that omits protected value
- an unverified receipt authorizes a consequential transition
- receipt prose overrides primary evidence or deterministic state
- missing receipt prose causes completed phases to replay
- receipt ceremony becomes mandatory for trivial non-delegated work
- a checklist-only RunSkeptic receipt is accepted without evidence
- a closure receipt independently invents DONE

## 5. Evidence Rule

Every test report must classify evidence as one of the current framework evidence levels:

- OBSERVED
- REPRODUCED
- HISTORICAL
- INFERRED RISK

Do not report INFERRED RISK as confirmed behavior.

## 6. Minimal Patch Rule

Prefer the smallest patch that fixes the verified failure mode.

Do not rewrite `skeptic.md` when a targeted invariant, test, or invocation rule is sufficient.

## 7. Runtime Separation Rule

`skeptic-tests.md` is not runtime instruction.
It is governance for changing Skeptic.

Runtime behavior belongs in `skeptic.md`.
Expanded questions belong only where `skeptic.md` says companion files apply.

## 8. Output Rule

A Skeptic change report must end using the current framework output categories.

For the current framework:
- full Skeptic ends as HANDLED or CONFLICT
- Razor ends as PASS, ACTION, or CONFLICT
- Task Prompt review may use DECOMPOSE as a DECIDE path; it does not create a new final task outcome

## 9. Test Before Merge Rule

Before merging a Skeptic change:

1. Run targeted tests for the changed area.
2. Run full unittest discovery if tests exist.
3. Show git status.
4. Show diff.
5. Report unresolved conflicts and missing evidence.
