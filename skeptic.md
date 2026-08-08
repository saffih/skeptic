# Skeptic - Detect, Reason, Fix, Verify

AI-executable framework for safe review and improvement.

Rules:
- Correct action over fast action.
- If detection confidence is insufficient, do not fix or promote; gather evidence, decompose, or escalate.
- Add process only when it addresses a specific credible failure mode.

## Invocation Contract

`RunSkeptic` is the formal invocation string for this framework.

Aliases: `beskeptic`, `apply Skeptic`, `Skeptic review`, `run skeptic.md`.

The invocation selects the framework; the request determines permission and stopping conditions. Runs are read-only unless fixing is explicitly authorized; verification emphasis or iterative repetition must also be requested.

When invoked:
1. Read the actual current `skeptic.md`, or an explicitly supplied candidate Skeptic file, before analysis.
2. Do not use memory, summaries, previous variants, or generated replacements as substitutes.
3. Treat the source under review as the runtime source of truth.
4. Read companion files only when this file says they apply.
5. Apply the current recipe exactly and in order.
6. Consider every Thinker required by this file.
7. Show which major Skeptic steps were run.
8. Show evidence for material findings.
9. Use the exact output categories from this file.
10. Do not modify files unless DECIDE says FIX and edits are explicitly allowed.
11. Verify the recommendation against the framework.
12. State unresolved conflicts, unknowns, skipped areas, and missing evidence.
13. If the source under review is unavailable, say so and do not claim RunSkeptic/Skeptic compliance.

An explicit invocation may additionally name companion files; they add context but do not replace or override the designated Skeptic source.

Each repeated run is a new invocation for source-freshness purposes: perform Rule 1 again. An earlier read does not satisfy a later run.

For deterministic binding, a formal invocation records:

```text
INVOCATION_ID: <id>
INVOCATION_KIND: SINGLE | FIND_LOOP | FIX_LOOP
PERMISSION_MODE: read-only | patch-local | fix-if-valid
DONE: <testable statement>
TARGET_TASK_SHA256: <sha256>
REVIEWED_ARTIFACT_REFERENCE: <reference>
REVIEWED_ARTIFACT_SHA256: <sha256>
SKEPTIC_SOURCE_PATH: skeptic.md
SKEPTIC_SOURCE_REF: <ref>
SKEPTIC_SOURCE_BLOB_SHA: <blob sha>
APPLICABLE_COMPANION_SET_SHA256: <sha256>
MATERIAL_FINDINGS_SHA256: <sha256>
PREVIOUS_FINDINGS_REFERENCE: <reference or NONE>
```

The designated source is freshly read before analysis. These fields bind the
receipt to that read and to the complete current artifact; they do not prove
hidden runtime context, model cognition, or actual model/provider routing.

### RunSkeptic Receipt

Every RunSkeptic report must include a compact receipt:
- Source read: path/ref/SHA or explicit unavailable state
- Companion files read, if any
- Permission mode: read-only / patch-local / fix-if-valid
- DONE statement
- Major steps run
- Thinkers considered
- Evidence used
- Decision path
- Verification performed
- Unresolved conflicts / unknowns
- Final output category

Do not claim RunSkeptic compliance without this receipt.

A RunSkeptic receipt indexes the review and its evidence; it is not independent proof or authority. A material receipt claim that conflicts with primary evidence must be corrected or left unresolved.

### Loop Invocations

#### Artifact Relay

For Find or Fix work likely to exhaust context or repeat substantial reads, an invocation may optionally use the standalone companion contract in `docs/context-stewardship.md`, because bounded orchestration can reduce context, cost, or failure risk without changing Skeptic authority.

That companion is optional and cannot replace or override Skeptic meanings, loop ownership, convergence, reset criteria, or receipts, because `skeptic.md` remains the authority for Skeptic behavior.

`RunSkeptic Find Loop` invokes repeated full read-only RunSkeptic reviews. Unless the explicit invocation sets another count, stop only after three consecutive runs produce no new meaningful finding and no material change to an existing finding.

For each Find Loop run:
- freshly read the designated current Skeptic source and execute the complete recipe
- re-evaluate the complete artifact and all previous findings
- make no modifications
- stabilize duplicates and distinguish new findings from restatements
- record new, changed, resolved, and still-open findings
- return material findings as scoped suspicions rather than task-level conclusions; preserve direct observations and evidence as such, and state the review scope, assumptions, and unknowns; the receiving Core (the task-level owner) retains responsibility to reevaluate each finding against wider authoritative context before task-level action or artifact promotion
- reset the consecutive-run count after any new or materially changed finding

Find Loop convergence means detection stabilized; it does not mean the artifact passed or is ready. Report every unresolved ACTION, DECOMPOSE path, CONFLICT, review-required status, and blocking unknown.

`RunSkeptic Fix Loop` invokes repeated full RunSkeptic review-and-fix cycles. Unless the explicit invocation sets another count, stop successfully only after three consecutive qualifying passes on the same unchanged artifact state.

External loop state binds the Target Task, complete reviewed artifact, Skeptic
source blob, applicable companions, material finding set, invocation kind, and
permission mode. Reset the qualifying count after any change to one of those
bindings or to a material finding. A repair run and a delta-only review never
qualify. Unless explicitly overridden, completion requires three unchanged
qualifying passes.

For each Fix Loop run:
- freshly read the designated current Skeptic source and execute the complete recipe
- re-evaluate the complete artifact, including all previously HANDLED areas
- fix every authorized material issue that DECIDE validly classifies as FIX
- verify every change immediately
- after any change, restart the complete review and reset the consecutive-pass count

A repair run does not count as a qualifying pass. A run qualifies only when no change is made, every material finding is PASS, all required verification passes, and no unresolved ACTION, DECOMPOSE path, CONFLICT, review-required status, or blocking unknown remains.

If safe evidence-backed progress cannot continue, stop with CONFLICT rather than loop indefinitely or claim completion.

Flow: GATE -> FUNDAMENTAL SCAN -> MAP -> CONFIDENCE -> STABILIZE -> EVIDENCE -> DECIDE -> ACT -> VERIFY -> LEARN

## 0. Gate

Proceed when:
- DONE is testable
- scope is tractable
- wrong-answer cost is acceptable
- intent, assumptions, and chosen approach are explicit enough to test

If not:
- undefined DONE -> STOP
- too large but clear -> DECOMPOSE
- multiple valid interpretations -> list them; proceed only if one is evidence-backed, low-risk, and testable
- unresolved or unsafe ambiguity -> CONFLICT

### Prompt and Task Feasibility

When reviewing an instruction, prompt, plan, or workflow, determine what it claims to own. Apply this core check using the supplied artifact and available evidence; do not assume repository companion files exist.

Classify the completion scope:
- **Bounded prompt:** owns one role or action, not terminal completion.
- **End-to-end task:** owns multiple dependent steps, integration, publication, or terminal DONE.

For either scope, check:
- objective, DONE, authority, source-of-truth order, allowed scope, output, verification, and stop conditions are explicit enough to execute;
- available context, time, tools, permissions, evidence, and other material resources can realistically support the claimed outcome;
- dependencies, handoffs, integration, and final verification have clear ownership when applicable;
- retries and repeated review/fix loops are bounded, with escalation or redesign when repetition stops adding evidence;
- decision-critical state is persisted only when it must survive a real boundary such as delegation, interruption, context loss, independent review, or cross-session continuation.

A well-written prompt or set of locally valid child steps cannot earn task-level PASS when the overall completion, integration, or verification path is infeasible or unowned. Missing feasibility is ACTION when locally repairable, DECOMPOSE when the objective is clear but too large or coupled, and CONFLICT when authority, design, safety, source of truth, or terminal completion remains unresolved.

No companion file is required for this core review. A supplied companion may add context-specific constraints but cannot override Skeptic.

## 0.5. Fundamental Scan

Before broad detection, check what can invalidate later work:
- system purpose
- architecture shape
- boundaries
- ownership
- source of truth
- main flows
- interfaces / coupling
- high-risk, recent, or suspected areas

Rules:
- detect only; do not fix
- clean scan is not proof of safety
- structural issues outrank local fixes
- downstream findings are PROVISIONAL if fundamentals may invalidate them
- if no structural issue appears, continue to MAP

## 1. Map - Detect Only

Record findings before deciding.

Start from Fundamental Scan; expand as needed.

Apply:
1. Universal Questions
2. All Thinkers: CH, OM, FE, PO, KT, SH
3. Structural Checks
4. Relevant Domain Checks selectively
5. Artifact patterns / external question banks when useful

Output:
- findings
- unknowns
- assumptions, including intent and approach assumptions; challenge them before DECIDE
- evidence strength
- skipped/uncertain areas

No fixes. No final decisions.

## 2. Universal Questions

For every meaningful entity: file, module, function, config, doc, test, system, process, requirement, decision.

- What is this?
- What is it for?
- What depends on it, and what does it depend on?
- What must always be true?
- What breaks it?
- How do we know it works?
- Does this solve a current verified need, or speculate about a future one?

## 3. Thinkers

Use full name + abbreviation first; then abbreviation.

Each thinker is a lens, not a checklist. Inspect through the lens. Report only material findings that affect PASS, ACTION, or CONFLICT. Use aspect tags for traceability, for example `CH:IV` or `OM:FS`.

### Charlie Munger (CH) - Inversion, Incentives, Misjudgment, Safety Margin

Find avoidable stupidity before approving success.

- `CH:IV` inversion: worst material bad outcome and whether evidence, limits, responsibility, or reversal path block it
- `CH:IN` incentives that reward noise, shortcuts, fake certainty, gaming, shallow compliance, or skipped verification
- `CH:SO` second-order damage: downstream harm, hidden cost, brittleness, drift, or confusion
- `CH:MJ` misjudgment: confidence without evidence, coherent stories without verification, one-lens thinking, assumptions as facts
- `CH:CP` competence gaps: deciding without enough evidence or domain understanding
- `CH:SM` weak safety margin: failure not bounded, visible, reversible, assigned responsibility, or checked
- `CH:CR` constraint risk: effort targets something other than the system constraint, queue, or blocker currently limiting the outcome
- `CH:EV` effort-value alignment: effort, cost, rigor, process, or resource use is disproportionate to expected value, material risk reduction, decision importance, available resources, or the probability of reaching a completed useful outcome
- `CH:SR` scale-up risk: small-scale success may fail under larger load, frequency, concurrency, data size, dependency count, or organizational scale


### Occam's Razor (OM) - Parsimony, Necessity, Sufficiency

Find unnecessary structure without removing what proves, protects, assigns responsibility for, or makes the required outcome reversible.

- `OM:UE` unnecessary entities: assumptions, steps, abstractions, options, or moving parts with no verified current need
- `OM:FS` false simplicity: simplification that proves less, protects less, or breaks the required outcome
- `OM:SS` speculative structure or abstraction before repeated concrete need
- `OM:OD` oversized design: more structure than outcome, evidence, safety, responsibility, or reversibility requires
- `OM:AC` avoidable complexity from misplaced boundaries, mixed concerns, or missing small guards
- `OM:CF` Chesterton fence: removing or replacing structure before understanding what constraint it protected

When structure or process is material, compare it with the smallest credible alternative that could achieve the required outcome. Remove structure that adds no necessary evidence, safety, responsibility, reversibility, or material value.

Do not simplify by deleting protections whose purpose is not understood. When substantial structure remains, state briefly why the smaller alternative is insufficient.


### Richard Feynman (FE) - Reality, Mechanism, Evidence Integrity

Find where explanation outruns reality.

- `FE:SC` stale claims: not true now, undated, or not recently verified
- `FE:ME` mechanism gap: says what happens but not clearly how or why it works
- `FE:WY` missing why: a non-obvious choice lacks a clear reason
- `FE:HL` hidden limits: assumptions, failed cases, edge cases, or contradictory evidence are omitted
- `FE:WE` weak evidence: proof does not directly exercise or support the claimed outcome
- `FE:PG` proof gap: confidence, authority, elegance, or coherent story substitutes for observed evidence
- `FE:PV` purpose/value gap: the artifact is coherent or well-structured, but the useful outcome, user, owner, or value is unclear
- `FE:TB` trust-boundary transition: untrusted, lower-authority, or unverified content, output, or state is accepted -- or is structurally permitted to flow -- into a higher-trust or control-bearing role without an explicit validation or authorization step proportionate to the consequence

Higher-trust or control-bearing roles include: instruction, permission, verified evidence, source of truth, executable input, policy, configuration, safety or control signal.

For every `FE:TB` finding, identify the lower-trust source, the promoted role, the boundary crossed, and the missing validation or authorization.


### Karl Popper (PO) - Falsifiability, Refutation, Contradiction

Find claims that can pass while wrong.

- `PO:UF` unfalsifiable claim: no observation, example, check, or condition could show it wrong
- `PO:CO` confirmation-only proof: supporting evidence exists, but no serious disconfirming case was tried
- `PO:CN` contradiction: rules, assumptions, examples, outputs, or acceptance criteria conflict
- `PO:WR` weak refutation path: wrong result is detected too late, only manually, or not at all
- `PO:SI` silent invalidation: artifact can appear valid while violating the claim
- `PO:OC` overclaim: current checks are treated as proof, not limited corroboration


### Immanuel Kant (KT) - Universalizability, Consistency, Fair Exceptions

Find patterns that should not become general rules.

- `KT:HU` harmful universalization: bad if used everywhere or by every similar actor
- `KT:EX` special pleading: one case gets an exception similar cases should not get
- `KT:IR` inconsistent rule: contradicts itself when applied broadly or symmetrically
- `KT:UA` unfair asymmetry: similar actors, cases, users, files, or decisions are treated differently without justification
- `KT:HB` hidden burden: works only by shifting ambiguity, cost, or cleanup to someone else
- `KT:HHB` hidden human burden: appears successful only by shifting avoidable ambiguity, cognitive load, repeated back-and-forth, coordination effort, delay, cost, risk, or cleanup onto another person or group
- `KT:OC` ought implies can: no permitted feasible path lets the responsible actor satisfy all applicable requirements simultaneously under its authority, capabilities, resources, dependencies, and constraints; if feasibility is unestablished, record unknown; preserve protected requirements when restoring feasibility; add `PO:CN` only when conflicting rules cause the impossibility


### Saffi (SH) - Trade-off Integration, Dominance, Exceptions

Find invalid middles and unresolved tradeoffs.

- `SH:OF` opposing forces: what each side protects and what each side costs
- `SH:FM` fake middle: compromise keeps both costs without resolving the tension
- `SH:FB` forced balance: the artifact tries to satisfy both sides when one side should dominate
- `SH:NE` narrow exception needed: one side should be default, but the other side needs a narrow protected exception
- `SH:HC` hidden conflict: product, architecture, safety, ownership, or priority decision is required
- `SH:WL` wrong leverage: within a genuine trade-off, the chosen side, middle, or exception does not materially affect the outcome it is intended to improve
- `SH:PF` dominance/frontier: a live option is retained even though another feasible option is no worse on every material protected dimension and better on at least one

Do not eliminate an option when dominance depends on stale or uncertain evidence, unsupported causation, aggregation that hides a subgroup or tail, omitted feasibility, reversibility or information value, mismatched time horizons, or a disputed weighting of consequences. When dominance is not supported, preserve the live trade-off or report the missing evidence.

Distinguish `CH:CR`, `SH:WL`, and `SH:PF` by whether the defect is the limiting constraint, the chosen intervention, or the live option set. Do not duplicate findings; when one explains another, merge them in STABILIZE.

If no real opposing forces, invalid middle, or live option comparison are present, SH = NOT_APPLICABLE.



## 4. Structural Checks

Check meaningful entities for:
- role and ownership
- boundaries and concern split
- interfaces, required links, forbidden links, implicit links, contracts
- necessary vs accidental coupling
- source of truth and competing copies
- data/control flow, update timing, consumers
- reversibility, retry safety, and failure signal

## 5. Domain Checks

Apply selectively:
- SEC: security, inputs, auth, secrets, permissions, exposure
- CPX: complexity, coupling, state, mental load
- REL: reliability, monitoring, scale, ownership, operations
- DAT: data, I/O, persistence, consistency, timing
- ARC: architecture, interfaces, contracts, dependencies
- CFT: tests, errors, mocks, craft

Rules:
- do not apply all domains blindly
- sample likely domains when unsure
- expand when findings cross domains or risk is high
- controlled redundancy is allowed for high risk
- use `skeptic-questions.md` for expanded SEC/CPX/REL/DAT/ARC/CFT questions when runtime detail is not enough

## 6. Detection Confidence

Before STABILIZE/DECIDE, check:
- Fundamental Scan completed
- Universal Questions applied
- All Thinkers considered: CH, OM, FE, PO, KT, SH
- SH either produced a finding or returned NOT_APPLICABLE
- Structural Checks applied
- Domain Checks applied selectively
- artifact patterns applied when useful
- important conclusions have evidence
- unknowns and skipped areas are listed

Track unknowns:
- owner, source of truth, contract, dependency
- behavior, risk boundary, revert path, test path
- acceptance criteria

Blind spots:
- unresolved ownership / SoT / contract / interface
- implicit or required connection unclear
- unverified behavior or weak tests
- missing failure signal
- suspiciously clean result
- local area skipped because top-down scan looked clean
- downstream work depends on unresolved fundamentals

If confidence is weak:
- expand MAP only where evidence requires it
- sample adjacent domains
- run CH/PO adversarial pass if clean result is suspicious
- resolve, decompose, or escalate high-risk UNKNOWNs
- CONFLICT if confidence cannot reasonably improve

Do not loop indefinitely.

## 7. Stabilize

Do not decide on raw findings.

Merge findings sharing:
- data, boundary, responsibility, interface
- source of truth, failure mode, root cause

Classify the issue and its root cause or detection gap:
- local bug
- missing test
- missing contract
- unclear ownership
- source-of-truth issue
- accidental coupling
- stale assumption
- systemic rule issue
- detection confidence issue

Check:
- overlapping, conflicting, or redundant fixes
- one finding explaining another
- unknowns blocking action
- local/systemic risk
- reversibility, blast radius, ownership clarity, confidence

Output stabilized issues.

Raw findings remain PROVISIONAL until stabilized.

## 8. Evidence Levels

Before DECIDE, assign every finding its applicable evidence level or levels.

- OBSERVED: directly seen in code, tests, config, docs, or runtime behavior.
- REPRODUCED: confirmed with failing test, probe, command, or execution.
- HISTORICAL: confirmed by issue, changelog, CVE, advisory, maintainer note, or release note.
- INFERRED RISK: plausible from structure, boundary, exposure, missing tests, or weak evidence, but not reproduced.

Rules:
- Do not report INFERRED RISK as confirmed bug.
- Security/parser/sanitizer INFERRED RISK becomes PROVISIONAL ACTION or CONFLICT.
- FIX requires OBSERVED evidence and a verification path.
- Confirmed vulnerability/history claim requires REPRODUCED or HISTORICAL evidence.
- HANDLED must include evidence level.
- CONFLICTS must include missing evidence.

## 9. Decide

For each stabilized issue, decide whether it requires FIX, DECOMPOSE, or CONFLICT; otherwise record why no action is required.

### FIX

Use when:
- root cause, structure, required connections, and source of truth are clear or irrelevant
- unknowns are resolved or irrelevant
- change is reversible, testable, retryable
- risk is low/medium
- confidence and verification path are adequate
- fix justification is complete

Before FIX, state:
- what is wrong
- why it is wrong
- why this fix is correct
- why this is the smallest change that solves the verified issue without broadening scope
- what would prove it wrong
- how to verify and revert

### DECOMPOSE

Use when scope/risk is high but structure is clear enough to split safely.

Split by:
- responsibility
- interface
- source of truth
- data flow
- testable slice
- reversible step
- unknown to resolve

Each step returns to GATE.

### CONFLICT

Use when:
- multiple valid designs exist
- owner, source of truth, connection, or contract is unclear
- product/architecture intent is required
- change cannot be made reversible
- decomposition does not remove ambiguity
- confidence remains inadequate

Do not decompose pure conflict to avoid escalation.

### Promotion Check

Before marking anything ready, approved, or safe to proceed, check whether any ACTION, CONFLICT, review-required status, or blocking unknown remains unresolved.

An unresolved DECOMPOSE path also blocks readiness or promotion until each resulting scope returns through GATE and reaches a valid outcome.

If yes, do not promote. Decide FIX, DECOMPOSE, or CONFLICT.

## 10. Act

Act only after DECIDE says FIX.

Process:
1. Preserve previous state.
2. Apply the smallest reversible change.
3. Verify immediately.
4. Revert immediately if verification fails.
5. Retry only if safer or better informed.
6. Escalate if safe retry is impossible.
7. Do not proceed to another task until the current change is verified or safely reverted.

Rules:
- no partial/unknown state
- no hidden-state reliance
- no implementation on unresolved conflict in the same area
- no link removal without replacement or explicit coupling decision
- no silent failure acceptance
- no broad refactor when a smaller verified slice reduces risk
- no speculative code for unverified future requirements
- no premature abstraction unless a current concrete need requires it
- follow existing style and conventions unless that style is the verified problem
- no out-of-scope edits; log unrelated improvements separately

## 11. Verify

Use evidence, not confidence.

Check:
- red -> green for bug fixes when possible
- 3-5 targeted spot checks when applicable; scale further checks to risk and evidence
- end-to-end trace from entry to output
- constraints: correctness, safety, performance, cost, context, maintainability
- pre-mortem: 3 concrete failure modes addressed before action
- regression: previously working behavior still works
- known-bad/edge case when results are suspiciously clean

A test that was never red is weak evidence.

Verification is pass/fail.

If fail, preserve evidence, revert unsafe partial state, and retry only with a new observed reason that makes retry safer; otherwise CONFLICT.

## 12. Learn

Trigger DOUBLE-LOOP when:
- same fix category appears 3+ times
- same conflict appears 2+ times
- following a rule worsens outcomes
- expectation lacks a clear rationale, authority, or evidence basis
- local fixes repeatedly reveal same structure problem
- repeated misses show detection coverage failure

Single-loop:
- implementation wrong -> fix and re-verify

Double-loop:
- rule, expectation, design, or detection method may be wrong -> CONFLICT unless obvious, reversible, and low risk

## 13. Output

Category layers:
- Finding/Razor categories: PASS, ACTION, CONFLICT.
- Final task outcomes: HANDLED, CONFLICT.

Every task ends as HANDLED or CONFLICT.

### HANDLED

Use for verified fixes, completed decomposed steps, or low-risk logged issues.

HANDLED means the assigned Skeptic task or item was completed according to its permission and scope. It does not mean the reviewed artifact passed, is ready, or has no open issues.

A completed read-only review may be HANDLED while explicitly reporting unresolved findings. A completed decomposed step may be HANDLED while its parent DECOMPOSE path remains open. The Promotion Check still blocks readiness while any blocking item remains unresolved.

Each item includes:
- issue
- root cause
- action
- verification
- detection confidence
- evidence level
- residual risk, if any

### CONFLICTS

Use for unresolved tradeoff, unclear owner/SoT/contract, non-reversible change, systemic rule issue, unresolved unknown, or inadequate confidence.

Each item includes:
- issue
- thesis
- antithesis
- tradeoffs
- blocking unknowns
- missing evidence
- safe recommendation, if any
- decision needed

## 14. Razor - Read-Only Diagnostic

Razor is a quick heuristic pass, not a replacement for MAP or the full Thinker lenses. It detects, classifies, and recommends; it never changes files.

Check:
- CH: avoidable failure, incentives, misjudgment, safety margin, constraint, effort-value, or scale risk
- OM: unnecessary structure, false simplicity, speculation, oversized design, avoidable complexity, or an unexplained protected constraint
- FE: stale claims, weak mechanism or evidence, hidden limits, unclear value, or an unvalidated trust-boundary transition
- PO: unfalsifiable claims, confirmation-only proof, contradiction, weak refutation, silent invalidity, or overclaim
- KT: harmful universalization, special pleading, inconsistent rules, unfair asymmetry, hidden burden, hidden human burden, or ought-implies-can feasibility
- SH: opposing forces, fake middles, forced balance, needed exceptions, hidden conflict, wrong leverage, or unproven dominance
- backward dependencies, forward constraints, and staleness

Prioritize by consequence: irreversible or dangerous failure; silent invalidity; trust or authorization breach; weak evidence; blast radius and reversibility; then avoidable complexity. Output PASS, ACTION, or CONFLICT.

## 15. Artifact Guide / External Questions

Use after Universal Questions and Structural Checks.

Patterns are detection aids, not exhaustive rules.

External reference:
- `skeptic-questions.md` contains expanded domain questions.
- Runtime core is authoritative.
- External questions expand detection only; no mandatory process.

- Code: dead code, weak abstractions, bare except, magic values, string-built SQL/commands, no coverage, no timeout/retry/cleanup, silent wrong-input success.
- Tests: behavior vs implementation, shared state, order/OS dependence, test never red, critical regression gap.
- Config: dead fields, constants disguised as config, inconsistent names/types/units, stale paths/services, bad defaults, missing validation.
- Agent instructions: no why, over-broad rule, contradiction, stale tool/model behavior, suppresses errors, skips verification, causes inaction.
- Human docs: repeats code/help, missing prerequisites, untested steps, hidden assumptions, silent command failure.
- Design decisions: over-generalization, lock-in, hidden assumptions, unvalidated design, implicit dependency, no observability, single point of failure.
- Requirements: no user need, untestable, not revalidated, solution without problem, no acceptance criteria.

## 16. Expert Review

One reviewer, one domain, one report. Scope the domain and files; apply Razor, Structural Checks, relevant Domain Checks, and Detection Confidence; report ACTIONS and CONFLICTS. Read-only by default; modify only when explicitly asked to fix.

## 17. SIFT Review

SIFT coordinates expert-review findings before action: SCAN relevant reviews; INTEGRATE duplicates and root causes; FIRM CONFIDENCE on unknowns and blind spots; TREAT only with explicit approval under safe-change rules; VERIFY fully. SIFT is read-only unless explicitly told to fix.

## 18. Tag Legend

Tags identify reasoning origin, not severity.

Thinker lenses:
- CH: Charlie Munger
- OM: Occam's Razor
- FE: Richard Feynman
- PO: Karl Popper
- KT: Immanuel Kant
- SH: Saffi; includes Follett-style integration-versus-compromise reasoning

Aspect tags are defined in §3:
- CH: `CH:IV`, `CH:IN`, `CH:SO`, `CH:MJ`, `CH:CP`, `CH:SM`, `CH:CR`, `CH:EV`, `CH:SR`
- OM: `OM:UE`, `OM:FS`, `OM:SS`, `OM:OD`, `OM:AC`, `OM:CF`
- FE: `FE:SC`, `FE:ME`, `FE:WY`, `FE:HL`, `FE:WE`, `FE:PG`, `FE:PV`, `FE:TB`
- PO: `PO:UF`, `PO:CO`, `PO:CN`, `PO:WR`, `PO:SI`, `PO:OC`
- KT: `KT:HU`, `KT:EX`, `KT:IR`, `KT:UA`, `KT:HB`, `KT:HHB`, `KT:OC`
- SH: `SH:OF`, `SH:FM`, `SH:FB`, `SH:NE`, `SH:HC`, `SH:WL`, `SH:PF`
- `SH:PF`: Pareto frontier / proven dominance

Domains:
- SEC: Security
- CPX: Complexity
- REL: Reliability
- DAT: Data / I/O
- ARC: Architecture / interfaces
- CFT: Craft / tests

Notation:
- `CH` identifies a Thinker lens.
- `CH:IV` identifies one aspect.
- `SEC` identifies a domain.
- `CH:IV->SEC` means an aspect surfaced a domain issue.
- `FE:WE+PO:SI` means multiple aspects apply to one finding.

Use the smallest explanatory tag set, normally 1-3 tags. Use aspects when they improve traceability. Tags never replace evidence level, severity, or output category. Do not invent numbered QIDs unless the referenced question bank defines them.

## 19. Invariants

- Never act without DONE.
- Never act before stabilization.
- Never decide on raw findings.
- For Skeptic self-work, read the authoritative current `skeptic.md` when reviewing the repo version. When explicitly reviewing a candidate file, read that candidate file and state that it is not yet authoritative. Do not use memory, summaries, or generated variants as substitutes for the source under review.
- Do not claim RunSkeptic/Skeptic compliance if the source under review was unavailable or not applied exactly.
- Never skip a Thinker; mark NOT_APPLICABLE when it does not fit.
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
- Never mark an artifact ready while ACTION, CONFLICT, review-required status, or blocking unknown remains unresolved.
- An unresolved DECOMPOSE path likewise blocks readiness or promotion.
- Every task ends as HANDLED or CONFLICT.
- Never modify outside the current task's scope; log adjacent issues separately.

## One-Line Summary

Gate -> Fundamental Scan -> Map -> Confidence -> Stabilize -> Evidence -> Decide -> Act Safely -> Verify -> Learn
