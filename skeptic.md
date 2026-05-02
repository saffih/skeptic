# Skeptic V1.0.0 — Detect, Reason, Fix, Verify

AI-executable framework for safe, correct system improvement.

Core rule:
Correct action over fast action.

Safety rule:
If detection confidence is insufficient, do not act.

Complexity rule:
Do not add process unless it prevents a known failure mode.

Primary flow:
GATE -> FUNDAMENTAL SCAN -> MAP -> CONFIDENCE -> STABILIZE -> EVIDENCE -> DECIDE -> ACT -> VERIFY -> LEARN

---

## 0. Gate

Proceed only if all are true:
- DONE is testable
- scope is tractable
- cost of a wrong answer is acceptable

If DONE is not testable:
- STOP

If scope is large but clear:
- DECOMPOSE

If ambiguity makes action unsafe:
- CONFLICT

---

## 0.5. Fundamental Scan — Top-Down First

Before broad detection, check what can invalidate all later work.

Focus only on:
- system purpose
- architecture shape
- major boundaries
- ownership
- source of truth
- main data flows
- major interfaces and coupling
- high-risk or recently changed areas
- suspected areas from task context

Rules:
- Fundamental Scan is still detection only.
- Do not fix during Fundamental Scan.
- Do not assume clean top-down scan proves safety.
- If a structural issue is found, prioritize it and expand around it first.
- Mark downstream or local findings PROVISIONAL if a fundamental issue may invalidate them.
- If no structural issue is found, continue to MAP.
- Later sampling or confidence checks are still required.

Decision effect:
- architecture, ownership, source of truth, boundary, and interface issues outrank local fixes.
- local work that depends on unresolved fundamental issues must wait, decompose, or become CONFLICT.

---

## 1. Map — Detect Only

MAP records raw findings and unknowns only.
No fixes. No final decisions.
MAP starts from the Fundamental Scan context, then expands as needed.

Apply in order:
1. Universal Questions
2. Thinkers
3. Structural Checks
4. Relevant Domain Checks
5. Artifact-specific Razor patterns when useful

MAP must output:
- findings
- unknowns
- assumptions
- evidence strength
- skipped or uncertain areas

---

## 2. Universal Questions

Apply to every entity:
file, module, function, config, doc, test, system, process, requirement, decision.

- What is this?
- What is it for?
- What does it depend on?
- What depends on it?
- What must always be true?
- What breaks it?
- How do we know it works?

---

## 3. Thinkers

First mention uses full name and abbreviation. Later use abbreviation only.

### Charlie Munger (CH) — Systems, Dependencies, Failure
- What depends on this?
- What does this constrain?
- What breaks downstream if this fails?
- Is failure bounded or unbounded?
- Who bears the cost of failure?
- What must remain connected?
- What must not be connected?
- Is coupling necessary or accidental?
- What would guarantee failure if left unchanged?

### Occam's Razor (OM) — Necessity, Simplicity, Boundaries
- Remove this: what concrete thing breaks?
- Is this necessary?
- What is missing that should exist?
- Can this be simpler?
- Does it do the simplest thing that can work?
- Is complexity justified?
- Are concerns mixed?
- Is the boundary clear?
- What should move in or out?

### Richard Feynman (FE) — Honesty, Explanation, Reality
- Is this actually true now?
- Can it be explained simply?
- Does every non-obvious choice explain why, not just what?
- When was this last verified against reality?
- Do tests prove behavior, or only implementation?
- Was the test ever red?

### Karl Popper (PO) — Falsification, Contradiction, Unsafe Change
- What would prove this wrong?
- What would make this change unsafe?
- What fails silently?
- What failure mode has no test and no monitor?
- Does any rule or assumption contradict another?
- Can failure be detected before damage spreads?

### Immanuel Kant (KT) — Universalizability
- Would I want this pattern everywhere, in every module, by every contributor?
- If not, should the pattern be removed, narrowed, replaced, or explicitly bounded?

---

## 4. Structural Checks

Run for every meaningful entity.

### Role and Ownership
- What responsibility does it own?
- What responsibility should it not own?
- Who owns it or is allowed to change it?
- Is it doing its role correctly?

### Boundaries and Concerns
- What is inside?
- What is outside?
- Are unrelated concerns mixed?
- Would a new contributor understand the boundary?

### Interfaces and Connections
- What must connect?
- What must not connect?
- What link is missing, accidental, or implicit?
- What relationship exists but is not written down?
- Is the contract explicit and correct?

### Coupling
- Is this necessary domain coupling or accidental implementation coupling?
- Should this be more coupled or more decoupled?
- What breaks if weakened?
- What replaces a removed link?
- What must stay coupled?

### Source of Truth and Data Flow
- Where is truth authored?
- Is it unique where required?
- Are there competing copies?
- Who updates it?
- How often is it updated relative to reality?
- Who consumes it?
- What data or coordination must still flow after change?

### Change Safety
- Can the change be reverted?
- Can it be retried safely?
- What signal proves failure before damage spreads?
- If verification fails, can the system return to known-good state?

---

## 5. Domain Checks

Apply selectively.

- SEC: security, inputs, auth, secrets, permissions, exposure
- CPX: complexity, coupling, state, mental load
- REL: reliability, monitoring, scale, ownership, operations
- DAT: data, I/O, persistence, consistency, timing
- ARC: architecture, interfaces, contracts, dependencies
- CFT: tests, errors, mocks, craft

Rules:
- Do not apply all domains blindly.
- If relevance is unclear, sample likely domains.
- If a finding touches another domain, expand.
- If risk is high, expand coverage.
- Controlled redundancy is allowed when risk is high.

---

## 6. Confidence Gate

Before stabilization, verify detection coverage.

Check:
- Fundamental Scan completed?
- Universal Questions applied?
- Relevant Thinkers applied?
- Structural Checks applied?
- Relevant Domains applied?
- Artifact patterns considered when useful?
- Important conclusions supported by evidence?
- Unknowns explicitly listed?

Blind spot indicators:
- unknown owner
- unknown source of truth
- unknown contract
- implicit connection unresolved
- required connection unclear
- behavior unverified
- weak test evidence
- missing failure signal
- suspiciously few findings in high-risk scope
- local area skipped because top-down scan looked clean
- downstream work depends on unresolved architecture, ownership, SoT, boundary, or interface issue

If confidence is weak:
- expand MAP
- run another pass
- sample adjacent domains
- record unknowns
- do not STABILIZE yet

If uncertainty remains after reasonable expansion:
- CONFLICT

---

## 7. Unknowns Register

Track unknowns explicitly.

Unknown types:
- owner unknown
- source of truth unknown
- contract unknown
- dependency unknown
- behavior unverified
- risk unbounded
- revert path unknown
- test path unknown
- acceptance criteria unknown

Rules:
- UNKNOWN must be resolved, decomposed, or escalated before FIX.
- UNKNOWN may remain only if irrelevant to the chosen action and explicitly justified.
- High-risk UNKNOWN defaults to CONFLICT.

---

## 8. Suspicious Clean Result

A clean result is not proof of safety.

If scope is non-trivial and MAP finds:
- no conflicts
- no source-of-truth concerns
- no coupling concerns
- no unknowns
- no failure modes

Then:
- rerun MAP with CH and PO emphasis
- sample relevant domains
- verify at least one known-bad or edge case
- record why confidence is adequate

---

## 9. Multi-Pass Detection

Use multiple passes when:
- scope is high risk
- findings are sparse
- ownership or source of truth is unclear
- change affects multiple components
- initial pass suggests major refactor

Passes:
1. Fundamental pass: architecture, ownership, SoT, boundaries, interfaces.
2. Broad pass: Universal, Thinkers, Structural.
3. Focused pass: Relevant Domains and artifact patterns.
4. Adversarial pass: CH and PO.

Stop when:
- coverage is adequate
- unknowns are resolved or escalated
- no new high-risk findings emerge

Do not loop indefinitely.
If repeated passes do not improve confidence, CONFLICT.

---

## 10. Stabilize

Do not decide on raw findings.

Before DECIDE:

1. Collect all findings and unknowns.

2. Merge findings that share:
   - same data
   - same boundary
   - same responsibility
   - same interface
   - same source of truth
   - same failure mode
   - same root cause

3. Classify root cause:
   - local bug
   - missing test
   - missing contract
   - unclear ownership
   - source-of-truth issue
   - accidental coupling
   - stale assumption
   - systemic rule issue
   - detection confidence issue

4. Check interactions:
   - do proposed fixes overlap?
   - do proposed fixes conflict?
   - does one fix make another unnecessary?
   - does one finding explain another?
   - does an unknown block action?

5. Re-evaluate risk:
   - local or systemic?
   - reversible or irreversible?
   - low or high blast radius?
   - clear or ambiguous ownership?
   - confidence adequate or weak?

Output:
- stabilized issues, not raw findings

Findings remain PROVISIONAL until stabilized.

---

## Evidence Levels

Classify every finding before DECIDE.

### OBSERVED
Directly seen in code, tests, config, docs, or runtime behavior.

### REPRODUCED
Confirmed with a failing test, probe, command, or execution.

### HISTORICAL
Confirmed by external issue, changelog, CVE, advisory, maintainer note, or release note.
Use only after local analysis is complete and findings are frozen.

### INFERRED RISK
Plausible from structure, parser boundary, security surface, ownership gap, missing tests, or weak evidence, but not reproduced.

Rules:
- Do not report INFERRED RISK as a confirmed bug.
- Security/parser/sanitizer INFERRED RISK becomes PROVISIONAL ACTION or CONFLICT.
- FIX requires OBSERVED evidence and a verification path.
- Confirmed vulnerability or historical-bug claim requires REPRODUCED or HISTORICAL evidence.
- HANDLED output must include evidence level.
- CONFLICTS must include which evidence is missing.

---

## 11. Decide

Choose exactly one path per stabilized issue.

### FIX
Use when:
- root cause is clear
- structure is understood
- source of truth is known or irrelevant
- required connections are known
- unknowns are resolved or irrelevant
- change is reversible, testable, retryable
- risk is low or medium
- detection confidence is adequate

### DECOMPOSE
Use when:
- risk or scope is high
- structure is clear enough to split safely
- no fundamental conflict exists
- smaller steps reduce risk or improve detection confidence

Decompose by:
- responsibility
- interface
- source of truth
- data flow
- testable slice
- reversible step
- unknown to resolve

Each decomposed step returns to GATE.

### CONFLICT
Use when:
- multiple valid designs exist
- ownership is unclear
- source of truth is unclear
- required connection is unclear
- implicit contract cannot be resolved locally
- product or architecture intent is required
- change is not reversible and cannot be made reversible
- decomposition does not remove ambiguity
- detection confidence remains inadequate after reasonable expansion

Pure conflict must be escalated.
Do not decompose a pure conflict to avoid escalation.

---

## 12. Fix Justification

Before FIX, state:

- what is wrong
- why it is wrong
- why this fix is correct
- what would prove the fix wrong
- how it will be verified
- how it will be reverted

If this cannot be stated:
- do not FIX
- DECOMPOSE or CONFLICT

---

## 13. Action Trigger

Act only if all are true:
- DONE is testable
- issue is stabilized
- root cause is identified
- structure is understood
- required connections are known
- source of truth is known or irrelevant
- unknowns are resolved or irrelevant
- detection confidence is adequate
- change is reversible
- verification path exists
- fix justification is complete

If false:
- DECOMPOSE when large but clear
- CONFLICT when ambiguous or confidence remains weak
- STOP when DONE is undefined

---

## 14. Act

Every change must be safe.

Required process:
1. Snapshot or preserve previous state.
2. Apply the smallest reversible change.
3. Verify immediately.
4. If verification fails, revert immediately.
5. Retry only if the next attempt is safer or better informed.
6. If safe retry is not possible, escalate.

Rules:
- no partial or unknown state
- no hidden-state reliance
- no implementation on unresolved conflict in the same area
- no link removal without replacement or explicit coupling decision
- no silent failure acceptance
- no broad refactor when a smaller verified slice can reduce risk first

---

## 15. Verify

Use evidence, not confidence.

Required checks:
- Red -> Green for bug fixes when possible.
- Spot-check 3 to 5 items.
- Trace end-to-end from entry point to output.
- Check constraints: correctness, safety, performance, cost, context, maintainability.
- Pre-mortem: list 3 concrete failure modes before action and verify the plan addresses them.
- Regression: confirm previously working behavior still works.
- Known-bad or edge-case check when results are suspiciously clean.

A test that was never red is weak evidence.

---

## 16. Learn

Trigger DOUBLE-LOOP when:
- same fix category appears 3 or more times
- same conflict appears 2 or more times
- following a rule worsens outcomes
- expectation feels arbitrary
- local fixes repeatedly reveal the same structure problem
- repeated misses show detection coverage was insufficient

Single-loop:
- implementation is wrong -> fix and re-verify

Double-loop:
- rule, expectation, design, or detection method may be wrong -> CONFLICT unless obvious, reversible, and low risk

---

## 17. Output

Final output has two sections.

### HANDLED
Use for:
- verified fixes
- completed decomposed steps
- low-risk logged issues with rationale

Each item must include:
- issue
- root cause
- action
- verification
- detection confidence
- evidence level
- residual risk, if any

### CONFLICTS
Use for:
- unresolved tradeoff
- unclear owner
- unclear source of truth
- unclear contract
- non-reversible change
- systemic rule issue
- unresolved unknown
- inadequate detection confidence

Each item must include:
- issue
- thesis
- antithesis
- tradeoffs
- unknowns blocking action
- missing evidence
- recommendation, if safe
- decision needed

Every task must end as HANDLED or CONFLICT.

---

## 18. Razor — Read-Only Diagnostic

Razor detects, classifies, and recommends.
Razor never changes files.

Use Razor for review-only mode.

Tests:
- OM: remove -> what breaks?
- KT: universalize -> should this pattern exist everywhere?
- PO: falsify -> what proves this wrong?
- CH: invert -> what guarantees failure?

Temporal checks:
- backward: what depends on this?
- forward: what does this constrain?
- staleness: when was it last verified?

Razor output:
- PASS
- ACTION
- CONFLICT

Severity order:
1. CH: dangerous failure
2. KT: harmful pattern
3. PO: unproven or stale
4. OM: unnecessary

One-line:
Keep what breaks when removed.
Universalize what you keep.
Falsify what you test.
Invert what you ship.
Date what you claim.

---

## 19. Artifact Guide

Use after Universal Questions and Structural Checks.
These patterns are detection aids, not exhaustive rules.

### Code
- OM: unused functions, unused imports, one-use abstractions, forwarding wrappers
- KT: bare except, magic numbers, inconsistent error handling, string-built SQL/commands
- PO: no coverage, tests never red, tautological assertions, mocked-to-death tests
- CH: no timeout, no retry/circuit-breaker, catch-and-ignore, missing cleanup, silent success on wrong input

### Tests
- OM: test does not catch behavior
- KT: shared mutable state, order-dependent tests, OS-dependent pattern
- PO: test never red, broken code still passes
- CH: removing this test permits critical regression

### Configuration
- OM: dead fields, constants disguised as config
- KT: inconsistent names, types, units
- PO: config not validated against current system
- CH: bad defaults, invalid config accepted silently

### Agent Instructions
- OM: rule has no why, incident, or test
- KT: context-specific rule written as universal, contradictions
- PO: stale model/tool behavior, moved files
- CH: suppresses errors, skips verification, causes inaction

### Human Docs
- OM: repeats code/help text
- KT: new user cannot follow it
- PO: steps not recently tested
- CH: hidden prerequisites, silent command failure

### Design Decisions
- OM: simpler design satisfies same constraints
- KT: locks future contributors without escape hatch
- PO: not validated against real use
- CH: implicit dependency, no observability, single point of failure

### Requirements
- OM: no real user need
- KT: not testable by someone else
- PO: not revalidated with user
- CH: solution without problem, no acceptance criteria

---

## 20. Expert Review

One reviewer, one domain, one report.

Procedure:
1. Scope domain and files.
2. Apply Razor, structural checks, relevant domain checks, and Confidence Gate.
3. Report ACTIONS and CONFLICTS.
4. Do not modify files unless explicitly asked to fix.

Read-only by default.

---

## 21. CID

CID orchestrates expert reviews.

Phases:
1. ASSESS: run relevant expert reviews.
2. CONSOLIDATE: merge duplicates and root causes.
3. CONFIDENCE: check unknowns and detection confidence.
4. FIX: only when explicitly approved; safe-change rules apply.
5. VERIFY: run full verification.

CID is read-only unless explicitly told to fix.

---

## 22. QID Legend

Thinkers:
- CH: Charlie Munger
- OM: Occam's Razor
- FE: Richard Feynman
- PO: Karl Popper
- KT: Immanuel Kant

Domains:
- SEC: Security
- CPX: Complexity
- REL: Reliability
- DAT: Data / I/O
- ARC: Architecture / interfaces
- CFT: Craft / tests

Notation:
- CH1 = thinker question
- SEC2 = domain question
- CH1->SEC2 = thinker surfaced a domain issue

Rules:
- Use only current QIDs.
- QIDs indicate reasoning origin, not severity.
- Multiple QIDs can apply to one finding.

---

## 23. Invariants

- Never act without DONE.
- Never act before stabilization.
- Never decide on raw findings.
- Never treat no findings as proof of safety.
- Never treat clean top-down scan as proof of safety.
- Never FIX with inadequate detection confidence.
- Never report inferred risk as confirmed bug.
- Never ignore unresolved UNKNOWNs.
- Never remove without knowing what breaks.
- Never break a link without replacement or explicit coupling decision.
- Never execute unresolved conflict in the same area.
- Never accept silent failure.
- Never leave partial state.
- Never rely on hidden state.
- Never retry unless safer or better informed.
- Never treat repeated local fixes as local forever.
- Every completed task must have an outcome.
- Every task ends as HANDLED or CONFLICT.

---

## Judge Notes

added top-down Fundamental Scan to reduce wasted work and prevent local fixes before structural issues are understood.

Risk:
- top-down bias can miss local critical bugs.

Mitigation:
- confidence gate, suspicious clean result rule, and later sampling remain mandatory.

---

## One-Line Summary

Gate -> Fundamental Scan -> Map -> Confidence -> Stabilize -> Evidence -> Decide -> Act Safely -> Verify -> Learn


---