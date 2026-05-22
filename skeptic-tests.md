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
- Fundamental Scan changes must test ownership, source of truth, interface, consumer, and failure-signal gaps.
- Map changes must test detect-only behavior and assumption/evidence separation.
- Thinker changes must test all required Thinkers and NOT_APPLICABLE behavior.
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

## 9. Test Before Merge Rule

Before merging a Skeptic change:

1. Run targeted tests for the changed area.
2. Run full unittest discovery if tests exist.
3. Show git status.
4. Show diff.
5. Report unresolved conflicts and missing evidence.

