# Skeptic - Detect, Reason, Fix, Verify

AI-executable framework for safe system improvement.

Rules: Correct over fast. If detection confidence insufficient, do not act. Add process only when it prevents a known failure mode.

## Invocation Contract

`RunSkeptic` is the formal invocation. Aliases: `beskeptic`, `apply Skeptic`, `Skeptic review`, `run skeptic.md`.

When invoked:
1. Read the actual current `skeptic.md` first — never use memory, summaries, previous variants, or generated replacements as substitutes. Treat it as runtime source of truth. If unavailable, say so and do not claim compliance.
2. Read companion files only when this file says they apply.
3. Apply the current recipe exactly and in order; consider every Thinker.
4. Show which major steps were run; show evidence for material findings.
5. Use the exact output categories from this file.
6. Do not modify files unless DECIDE says FIX and edits are explicitly allowed.
7. Verify recommendation against the framework; state unresolved conflicts, unknowns, skipped areas, and missing evidence.

Flow:
GATE -> FUNDAMENTAL SCAN -> MAP -> CONFIDENCE -> STABILIZE -> EVIDENCE -> DECIDE -> ACT -> VERIFY -> LEARN

## 0. Gate

Proceed when: DONE is testable; scope is tractable; wrong-answer cost is acceptable; assumptions about intent and approach are explicit.

If not: undefined DONE -> STOP; too large but clear -> DECOMPOSE; multiple valid interpretations -> enumerate before proceeding; unsafe ambiguity -> CONFLICT.

## 0.5. Fundamental Scan

Before broad detection, check what can invalidate later work: system purpose; architecture shape; boundaries; ownership; source of truth; main flows; interfaces/coupling; high-risk, recent, or suspected areas.

Rules: detect only, do not fix; clean scan is not proof of safety; structural issues outrank local fixes; downstream findings are PROVISIONAL if fundamentals may invalidate them; if no structural issue appears, continue to MAP.

## 1. Map - Detect Only

Record findings before deciding. Start from Fundamental Scan; expand as needed.

Apply: 1) Universal Questions; 2) All Thinkers: CH, OM, FE, PO, KT, SH; 3) Structural Checks; 4) Relevant Domain Checks selectively; 5) Artifact patterns / external question banks when useful.

Output: findings; unknowns; assumptions (surfaced and challenged, not passively recorded); evidence strength; skipped/uncertain areas.

No fixes. No final decisions.

## 2. Universal Questions

For every meaningful entity (file, module, function, config, doc, test, system, process, requirement, decision):
- What is this? What is it for?
- What depends on it, and what does it depend on?
- What must always be true? What breaks it?
- How do we know it works?

## 3. Thinkers

Use full name + abbreviation first; then abbreviation.

### Charlie Munger (CH) - Systems, Dependencies, Failure
What depends on this? What does this constrain? What breaks downstream? Is failure bounded? Who bears failure cost? What must/must not stay connected? Is coupling necessary or accidental? What would guarantee failure if unchanged?

### Occam's Razor (OM) - Necessity, Simplicity, Boundaries
Remove this: what breaks? Is this necessary? What is missing? Can this be simpler? Is complexity justified? Does this anticipate a need that does not yet exist? Are concerns mixed? Is the boundary clear? What should move in or out?

### Richard Feynman (FE) - Honesty, Explanation, Reality
Is this true now? Can it be explained simply? Does each non-obvious choice explain why? When was it last verified? Do tests prove behavior, not implementation? Was the test ever red?

### Karl Popper (PO) - Falsification, Contradiction, Unsafe Change
What would prove this wrong? What would make this unsafe? What fails silently? What has no test or monitor? Do rules or assumptions contradict? Can failure be detected before damage spreads?

### Immanuel Kant (KT) - Universalizability
Would I want this pattern everywhere, by every contributor? If not, should it be removed, narrowed, replaced, or bounded?

### Saffi (SH) - Sharp Trade-off Heuristics
What are the real forces/sides, and what middle is trying to combine them? Is the middle creating real friction? If no: SH = NOT_APPLICABLE. If yes: Is the middle a real integration, or just a compromise that keeps both costs? Should Side A or Side B dominate as default? What narrow exception protects the other side? If no side should dominate and the middle is not valid, what conflict must be explicit?

## 4. Structural Checks

Check meaningful entities for: role and ownership; boundaries and concern split; interfaces, required/forbidden/implicit links, contracts; necessary vs accidental coupling; source of truth and competing copies; data/control flow, update timing, consumers; reversibility, retry safety, failure signal.

## 5. Domain Checks

Apply selectively:
- SEC: security, inputs, auth, secrets, permissions, exposure
- CPX: complexity, coupling, state, mental load
- REL: reliability, monitoring, scale, ownership, operations
- DAT: data, I/O, persistence, consistency, timing
- ARC: architecture, interfaces, contracts, dependencies
- CFT: tests, errors, mocks, craft

Rules: do not apply all domains blindly; sample likely domains when unsure; expand when findings cross domains or risk is high; controlled redundancy allowed for high risk; use `skeptic-questions.md` for expanded questions when runtime detail is not enough.

## 6. Detection Confidence

Before STABILIZE/DECIDE, check: Fundamental Scan completed; Universal Questions applied; all Thinkers considered (SH either produced a finding or returned NOT_APPLICABLE); Structural Checks applied; Domain Checks applied selectively; artifact patterns applied when useful; important conclusions have evidence; unknowns and skipped areas listed.

Track unknowns: owner, source of truth, contract, dependency, behavior, risk boundary, revert path, test path, acceptance criteria.

Blind spots: unresolved ownership/SoT/contract/interface; implicit or required connection unclear; unverified behavior or weak tests; missing failure signal; suspiciously clean result; local area skipped because top-down scan looked clean; downstream work depends on unresolved fundamentals.

If confidence is weak: expand MAP only where evidence requires it; sample adjacent domains; run CH/PO adversarial pass if clean result is suspicious; resolve, decompose, or escalate high-risk UNKNOWNs; CONFLICT if confidence cannot reasonably improve. Do not loop indefinitely.

## 7. Stabilize

Do not decide on raw findings.

Merge findings sharing: data, boundary, responsibility, interface, source of truth, failure mode, root cause.

Classify root cause: local bug; missing test; missing contract; unclear ownership; source-of-truth issue; accidental coupling; stale assumption; systemic rule issue; detection confidence issue.

Check: overlapping, conflicting, or redundant fixes; one finding explaining another; unknowns blocking action; local/systemic risk; reversibility, blast radius, ownership clarity, confidence.

Output stabilized issues. Raw findings remain PROVISIONAL until stabilized.

## 8. Evidence Levels

Before DECIDE, classify every finding.
- OBSERVED: directly seen in code, tests, config, docs, or runtime.
- REPRODUCED: confirmed with failing test, probe, command, or execution.
- HISTORICAL: confirmed by issue, changelog, CVE, advisory, maintainer/release note.
- INFERRED RISK: plausible from structure, boundary, exposure, missing tests, or weak evidence, but not reproduced.

Rules: do not report INFERRED RISK as confirmed bug; security/parser/sanitizer INFERRED RISK becomes PROVISIONAL ACTION or CONFLICT; FIX requires OBSERVED evidence and a verification path; confirmed vulnerability/history claim requires REPRODUCED or HISTORICAL evidence; HANDLED must include evidence level; CONFLICTS must include missing evidence.

## 9. Decide

Choose one path per stabilized issue.

### FIX
Use when: root cause, structure, required connections, and source of truth are clear or irrelevant; unknowns resolved or irrelevant; change is reversible, testable, retryable; risk is low/medium; confidence and verification path adequate; fix justification complete.

Before FIX, state: what is wrong; why it is wrong; why this fix is correct; why this fix is the minimum necessary change; what would prove it wrong; how to verify and revert.

### DECOMPOSE
Use when scope/risk is high but structure is clear enough to split safely.

Split by: responsibility; interface; source of truth; data flow; testable slice; reversible step; unknown to resolve. Each step returns to GATE.

### CONFLICT
Use when: multiple valid designs exist; owner/SoT/connection/contract unclear; product/architecture intent required; change cannot be made reversible; decomposition does not remove ambiguity; confidence remains inadequate.

Do not decompose pure conflict to avoid escalation.

## 10. Act

Act only after DECIDE says FIX.

Process: 1) Preserve previous state; 2) Apply smallest reversible change; 3) Verify immediately; 4) Revert immediately if verification fails; 5) Retry only if safer or better informed; 6) Escalate if safe retry impossible; 7) Do not proceed to next task until current verification passes.

Rules: no partial/unknown state; no hidden-state reliance; no implementation on unresolved conflict in same area; no link removal without replacement or explicit coupling decision; no silent failure acceptance; no broad refactor when smaller verified slice reduces risk; no speculative code for nonexistent requirements; no premature abstraction unless current concrete need demands it; match existing style/conventions, do not introduce new patterns during a fix; do not modify outside current task's scope.

## 11. Verify

Use evidence, not confidence.

Check: red -> green for bug fixes when possible; 3-5 manual spot checks; end-to-end trace from entry to output; constraints (correctness, safety, performance, cost, context, maintainability); pre-mortem: 3 concrete failure modes addressed before action; regression: previously working behavior still works; known-bad/edge case when results are suspiciously clean.

A test that was never red is weak evidence. Verification is pass/fail. If fail, return to Act.

## 12. Learn

Trigger DOUBLE-LOOP when: same fix category 3+ times; same conflict 2+ times; following a rule worsens outcomes; expectation feels arbitrary; local fixes repeatedly reveal same structure problem; repeated misses show detection coverage failure.

Single-loop: implementation wrong -> fix and re-verify.
Double-loop: rule, expectation, design, or detection method may be wrong -> CONFLICT unless obvious, reversible, and low risk.

## 13. Output

Every task ends as HANDLED or CONFLICT.

### HANDLED
Verified fixes, completed decomposed steps, or low-risk logged issues. Each item includes: issue, root cause, action, verification, detection confidence, evidence level, residual risk (if any).

### CONFLICTS
Unresolved tradeoff, unclear owner/SoT/contract, non-reversible change, systemic rule issue, unresolved unknown, or inadequate confidence. Each item includes: issue, thesis, antithesis, tradeoffs, blocking unknowns, missing evidence, safe recommendation (if any), decision needed.

## 14. Razor - Read-Only Diagnostic

Razor detects, classifies, recommends. Never changes files.

Tests: OM: remove -> what breaks? KT: universalize -> should this pattern exist everywhere? PO: falsify -> what proves this wrong? CH: invert -> what guarantees failure?

Temporal checks: backward: what depends on this? forward: what does this constrain? staleness: when was it last verified?

Output: PASS, ACTION, CONFLICT.

Severity: 1) CH: dangerous failure; 2) KT: harmful pattern; 3) PO: unproven or stale; 4) OM: unnecessary.

One-line: Keep what breaks when removed. Universalize what you keep. Falsify what you test. Invert what you ship. Date what you claim.

## 15. Artifact Guide / External Questions

Use after Universal Questions and Structural Checks. Patterns are detection aids, not exhaustive rules.

External reference: `skeptic-questions.md` contains expanded domain questions. Runtime core is authoritative. External questions expand detection only; no mandatory process.

- Code: dead code, weak abstractions, bare except, magic values, string-built SQL/commands, no coverage, no timeout/retry/cleanup, silent wrong-input success.
- Tests: behavior vs implementation, shared state, order/OS dependence, test never red, critical regression gap.
- Config: dead fields, constants disguised as config, inconsistent names/types/units, stale paths/services, bad defaults, missing validation.
- Agent instructions: no why, over-broad rule, contradiction, stale tool/model behavior, suppresses errors, skips verification, causes inaction.
- Human docs: repeats code/help, missing prerequisites, untested steps, hidden assumptions, silent command failure.
- Design decisions: over-generalization, lock-in, hidden assumptions, unvalidated design, implicit dependency, no observability, single point of failure.
- Requirements: no user need, untestable, not revalidated, solution without problem, no acceptance criteria.

## 16. Expert Review

One reviewer, one domain, one report.

Procedure: 1) Scope domain and files; 2) Apply Razor, structural checks, relevant domains, and Confidence Gate; 3) Report ACTIONS and CONFLICTS; 4) Do not modify files unless explicitly asked to fix. Read-only by default.

## 17. SIFT Review

SIFT coordinates expert review findings before action.

Phases: 1) SCAN: run relevant expert reviews; 2) INTEGRATE: merge duplicates/root causes; 3) FIRM CONFIDENCE: check unknowns and detection confidence; 4) TREAT: fix only with explicit approval, safe-change rules apply; 5) VERIFY: run full verification. SIFT is read-only unless explicitly told to fix.

## 18. Tag Legend

Thinkers: CH=Charlie Munger; OM=Occam's Razor; FE=Richard Feynman; PO=Karl Popper; KT=Immanuel Kant; SH=Saffi (includes Follett-style integration vs compromise check).
Domains: SEC=Security; CPX=Complexity; REL=Reliability; DAT=Data/I/O; ARC=Architecture/interfaces; CFT=Craft/tests.
Notation: CH1=thinker question; SEC2=domain question; CH1->SEC2=thinker surfaced domain issue. Use only current QIDs; QIDs indicate reasoning origin, not severity; multiple QIDs can apply to one finding.

## 19. Invariants

Self-reference: Always read the actual current `skeptic.md` before applying it; never use memory, summaries, or generated variants. Do not claim compliance if the actual file was unavailable or not applied exactly.
Thinkers: Never skip a Thinker; mark NOT_APPLICABLE when it does not fit.
Safety: Never treat no findings or clean top-down scan as proof of safety; never FIX with inadequate detection confidence; never report inferred risk as confirmed bug; never ignore unresolved UNKNOWNs.
Act constraints: Never act without DONE or before stabilization; never decide on raw findings; never accept silent failure, partial state, or hidden-state reliance; never retry unless safer or better informed.
Scope: Never remove without knowing what breaks; never break a link without replacement or explicit coupling decision; never execute unresolved conflict in same area; never modify outside current task's scope.
Outcomes: Every task ends as HANDLED or CONFLICT; never treat repeated local fixes as local forever.

## One-Line Summary

Gate -> Fundamental Scan -> Map -> Confidence -> Stabilize -> Evidence -> Decide -> Act Safely -> Verify -> Learn
