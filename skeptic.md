# Skeptic - Detect, Reason, Fix, Verify

AI-executable framework for safe system improvement.

Rules:
- Correct action over fast action.
- If detection confidence is insufficient, do not act.
- Add process only when it prevents a known failure mode.

## Invocation Contract

`RunSkeptic` is the formal invocation string for this framework.

Aliases:
- `beskeptic`
- `apply Skeptic`
- `Skeptic review`
- `run skeptic.md`

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

### RunSkeptic Receipt

Every RunSkeptic report must include a compact receipt:
- Source read: path/ref/SHA or explicit unavailable state
- Companion files read, if any
- Permission mode: read-only / patch-local / fix-if-valid
- DONE statement
- Prompt review level and task feasibility, when applicable
- Major steps run
- Thinkers considered
- Evidence used
- Decision path
- Verification performed
- Unresolved conflicts / unknowns
- Final output category

Do not claim RunSkeptic compliance without this receipt.

This receipt is a compact index of claims and evidence, not proof and not an authorization artifact. Material findings must point to the evidence that supports them; listing steps or Thinkers considered without their material application and evidence does not establish RunSkeptic compliance. If a receipt claim conflicts with the evidence it cites, do not claim RunSkeptic compliance until the mismatch is corrected or the conflict is explicitly resolved.

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

### Smallest credible alternative guard

Before PASS on a plan, prompt, design, or process-heavy artifact, compare it with the smallest credible alternative that could achieve the same required outcome while preserving necessary evidence, safety, responsibility, and reversibility.

Apply `CH:EV` and `OM:OD`: identify removable structure and justify the remaining material structure. If a materially smaller alternative is equally sufficient, return ACTION. Listing the Thinkers or repeating unchanged reviews does not establish simplicity.

The PASS rationale must state the smallest credible alternative considered, what it removes, whether it preserves the required outcome, evidence, safety, responsibility, and reversibility, and why the retained structure is necessary.

Preserve `OM:FS`: reject simplification that removes required proof, safety, ownership, reversibility, or outcomes.

### Prompt Review Levels

When the artifact under review is a prompt, classify it before MAP:

- **Agent Prompt**: a bounded instruction for one participating agent or role.
- **Dispatch Ticket**: the compact delegated form of an Agent Prompt.
- **Task Prompt**: the complete Lead-owned execution contract from verified starting state through terminal DONE.

The canonical Task Prompt construction and execution contract is `agents/task-prompt.md`. Read it as a required companion when reviewing a Task Prompt. `skeptic.md` remains authoritative for review behavior and output categories; the companion must not override it. If the required companion is unavailable, do not claim task-level PASS.

If a prompt claims ownership of the complete lifecycle or of integration/publication completion, review it as a Task Prompt even when it calls itself an Agent Prompt. If terminal ownership is ambiguous and materially changes the review level, return CONFLICT.

#### Level 1 - Agent Prompt review

Check whether the bounded child instruction has:

- one clear role, objective, source of truth, and scope;
- explicit allowed and forbidden actions;
- proportionate model/effort and context/output limits when material;
- defined inputs, durable outputs, acceptance checks, and stop conditions;
- a compact Agent Receipt that the Lead or Checker can verify;
- no authority to silently expand scope or promote its own output into task-level completion.

#### Level 2 - Task Prompt review

Review both child-prompt correctness and end-to-end completion feasibility. A Task Prompt must not receive PASS merely because its individual Agent Prompts are locally valid.

Task-level PASS requires evidence in the prompt that:

- terminal DONE is exact, observable, and distinguishes intermediate states;
- starting state, authority, source-of-truth order, scope, and protected state will be verified;
- the objective is realistically completable with available context, tokens, time, credits, tools, permissions, and evidence;
- phases form a coherent dependency graph with bounded ownership, inputs, outputs, acceptance checks, and next-state rules;
- model, effort, agents, context, outputs, and protocol cost are allocated proportionately;
- a protected completion reserve remains for synthesis, verification, integration, external confirmation, and closure;
- when survival beyond the current session is materially required -- handoff, interruption, context clearing, independent review, delegation, repeated execution, or cross-session continuation -- decision-critical outputs are durably persisted, in an authorized location chosen by the invoking runtime or task environment, and verified before dependent phases begin;
- retry and gate counts are bounded, repeated failure triggers redesign, and futility can stop optional work;
- a pre-exhaustion handoff preserves verified state without pretending the task is DONE;
- system verification and disconfirming cases cover the requested outcome;
- integration, publication, and fresh external verification are explicit phases when part of DONE;
- the Task Closure Receipt can prove every requested terminal condition.

Persistence is conditional, not automatic. Skeptic does not prescribe a canonical state directory, receipt directory, controller, filesystem layout, database, or storage mechanism, and the Skeptic checkout is not the default writable workspace; the invoking runtime or task environment selects the authorized location when persistence is materially required. When no material survival requirement exists -- no handoff, resume, delegation, independent review, repeated execution, or cross-session consumer -- a bounded task that can reliably finish in one session may receive task-level PASS without a controller, checkpoint file, state directory, or durable artifact store. When such survival is materially required, missing or inadequate authorized persistence is ACTION. This does not weaken evidence integrity: transient context never counts as having survived a context boundary it did not survive.

Treat as material failures:

- locally valid child prompts with a missing dependency, integration owner, evidence checkpoint, or closure path;
- context protection without an actual allocation, measurable substitute, or stop threshold;
- optional exploration or worker work that can consume the completion reserve;
- a fix-until-PASS or retry loop with no declared bound or redesign trigger;
- a workflow that ends at analysis, patch, branch, commit, pull request, local merge, or push attempt when DONE requires more;
- protocol whose cost approaches or exceeds the expected value or probability of useful completion.

Task-level gate decisions:

- `PASS`: no blocking child- or task-level finding remains.
- `ACTION`: a repairable prompt defect remains.
- `DECOMPOSE`: the objective is clear, but the workflow is too large or coupled to complete safely as one Task Prompt.
- `CONFLICT`: authority, source of truth, design choice, safety, or completion path cannot be resolved within prompt scope.

`DECOMPOSE` remains a DECIDE path, not a new final task outcome. Full Skeptic still ends as HANDLED or CONFLICT. Do not execute or promote a prompt with unresolved ACTION, DECOMPOSE, CONFLICT, review-required status, or blocking unknown.

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

## 3. Thinkers

Use full name + abbreviation first; then abbreviation.

Each thinker is a lens, not a checklist. Inspect through the lens. Report only material findings that affect PASS, ACTION, or CONFLICT. Use aspect tags for traceability, for example `CH:IV` or `OM:FS`.

### Charlie Munger (CH) - Inversion, Incentives, Misjudgment, Safety Margin

Find avoidable stupidity before approving success.

Look for:
- `CH:IV` inversion: worst material bad outcome and whether evidence, limits, responsibility, or reversal path block it
- `CH:IN` incentives that reward noise, shortcuts, fake certainty, gaming, shallow compliance, or skipped verification
- `CH:SO` second-order damage: downstream harm, hidden cost, brittleness, drift, or confusion
- `CH:MJ` misjudgment: confidence without evidence, coherent stories without verification, one-lens thinking, assumptions as facts
- `CH:CP` competence gaps: deciding without enough evidence or domain understanding
- `CH:SM` weak safety margin: failure not bounded, visible, reversible, assigned responsibility, or checked
- `CH:CR` constraint risk: effort targets a non-bottleneck while the real system constraint, queue, or blocker remains unchanged
- `CH:EV` effort-value alignment: effort, cost, rigor, process, or resource use is disproportionate to expected value, material risk reduction, decision importance, available resources, or the probability of reaching a completed useful outcome
- `CH:SR` scale-up risk: small-scale success may fail under larger load, frequency, concurrency, data size, dependency count, or organizational scale

Report when CH exposes a material failure path, bad incentive, false certainty, competence gap, missing safety margin, wrong constraint, disproportionate effort or resource waste, low-probability completion, or unsupported scale-up assumption.

### Occam's Razor (OM) - Parsimony, Necessity, Sufficiency

Find unnecessary structure without removing what proves, protects, assigns responsibility for, or makes the required outcome reversible.

Look for:
- `OM:UE` unnecessary entities: assumptions, steps, abstractions, options, or moving parts with no verified current need
- `OM:FS` false simplicity: simplification that proves less, protects less, or breaks the required outcome
- `OM:SS` speculative structure or abstraction before repeated concrete need
- `OM:OD` oversized design: more structure than outcome, evidence, safety, responsibility, or reversibility requires
- `OM:AC` avoidable complexity from misplaced boundaries, mixed concerns, or missing small guards
- `OM:CF` Chesterton fence: removing or replacing structure before understanding what constraint it protected

Report when something can be removed, merged, moved, simplified, or guarded without losing required outcome, evidence, responsibility, reversibility, or safety.

### Richard Feynman (FE) - Reality, Mechanism, Evidence Integrity

Find where explanation outruns reality.

Look for:
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

Report when a claim, choice, conclusion, or trust transition cannot be trusted without clearer mechanism, current evidence, disclosed limits, direct proof, clear value, or a validated and authorized transition into a higher-trust or control-bearing role.

### Karl Popper (PO) - Falsifiability, Refutation, Contradiction

Find claims that can pass while wrong.

Look for:
- `PO:UF` unfalsifiable claim: no observation, example, check, or condition could show it wrong
- `PO:CO` confirmation-only proof: supporting evidence exists, but no serious disconfirming case was tried
- `PO:CN` contradiction: rules, assumptions, examples, outputs, or acceptance criteria conflict
- `PO:WR` weak refutation path: wrong result is detected too late, only manually, or not at all
- `PO:SI` silent invalidation: artifact can appear valid while violating the claim
- `PO:OC` overclaim: current checks are treated as proof, not limited corroboration

Report when a claim, rule, decision, or result cannot be refuted, contradicts another requirement, or can pass while wrong.

### Immanuel Kant (KT) - Universalizability, Consistency, Fair Exceptions

Find patterns that should not become general rules.

Look for:
- `KT:HU` harmful universalization: bad if used everywhere or by every similar actor
- `KT:EX` special pleading: one case gets an exception similar cases should not get
- `KT:IR` inconsistent rule: contradicts itself when applied broadly or symmetrically
- `KT:UA` unfair asymmetry: similar actors, cases, users, files, or decisions are treated differently without justification
- `KT:HB` hidden burden: works only by shifting ambiguity, cost, or cleanup to someone else

Report when the pattern should be removed, narrowed, bounded, or made into an explicit rule or exception.

### Saffi (SH) - Trade-off Integration, Dominance, Exceptions

Find invalid middles, unresolved tradeoffs, and provably dominated options without erasing protected differences.

Look for:
- `SH:OF` opposing forces: what each side protects and what each side costs
- `SH:FM` fake middle: compromise keeps both costs without resolving the tension
- `SH:FB` forced balance: the artifact tries to satisfy both sides when one side should dominate
- `SH:NE` narrow exception needed: one side should be default, but the other side needs a narrow protected exception
- `SH:HC` hidden conflict: product, architecture, safety, ownership, or priority decision is required
- `SH:WL` wrong leverage: the chosen side, middle, or exception does not address the constraint limiting the outcome
- `SH:PF` Pareto frontier / proven dominance: remove an option only when another is safely no worse on every protected dimension and strictly better on at least one

#### SH:PF decision rule

Use SH:PF only for an explicit comparison with at least two live options. Existing authority, source-of-truth, ownership, and hard safety blockers run first. The lens routing results below do not replace Skeptic's final output categories.

- `NOT_APPLICABLE`: no live multi-option comparison exists; add no frontier process.
- `DEFER_EXISTING`: an earlier Skeptic check already decides or blocks the case; do not duplicate or override it.
- `DOMINANCE_UNPROVEN`: the comparison or any elimination guard is unresolved; preserve the option and route the gap through existing evidence, trade-off, exception, or CONFLICT handling.
- `PRESERVE_FRONTIER`: the comparison is valid but no option is proven dominated; keep every non-dominated option.
- `ELIMINATE_DOMINATED`: one option is proven dominated; remove it from the live set.

To prove that A dominates B:

1. Compare disaggregated, decision-relevant dimensions with the same direction, scope, time horizon, evidence standard, and tractability assumptions. Include hard constraints and protected minority or subgroup outcomes.
2. Use current evidence and represent material uncertainty as credible intervals. For a claimed outcome that depends on causation, correlation alone cannot prove superiority.
3. A is safely no worse on a dimension only when A's lower credible bound is at least B's upper credible bound. A is strictly better only when its lower credible bound is greater than B's upper credible bound.
4. Require A to be safely no worse on every protected dimension and strictly better on at least one. Weighted totals, averages, or grouped outcomes cannot substitute for this all-dimensions check.
5. Before elimination, verify that B has no missing minority or subgroup benefit, long-tail value, uncertainty-sensitive upside, reversibility or information value, strategic option value, narrow exception, or legitimate stakeholder weighting.

If any basis or guard is missing, dominance is unproven. If neither option is strictly better, both remain on the frontier; OM may separately test whether equal options are unnecessary duplicates.

Report the dominating option, dominated option, compared dimensions, evidence and uncertainty basis, and preservation guards checked whenever SH:PF returns `ELIMINATE_DOMINATED`.

#### Constraint, leverage, and dominance routing

`CH:CR`, `SH:WL`, and `SH:PF` answer different questions about different entities:

- `CH:CR`: is effort aimed at the real system constraint? Entity: the system, queue, or limiting factor.
- `SH:WL`: inside a real trade-off, does the chosen default, middle, or exception act on the lever that changes the limiting outcome? Entity: one trade-off decision.
- `SH:PF`: is one of several live comparable options proven dominated? Entity: the live option set.

Routing rules:

- Apply only the lenses whose entity is present; an ordinary task with no constraint doubt, no real trade-off, and no live option comparison triggers none of them.
- The practical default order is constraint, then leverage, then dominance, but skip absent stages: a clear option comparison does not require inventing a bottleneck, and a plain bottleneck error does not require trade-off or frontier analysis.
- A live `CH:CR` finding that effort targets the wrong constraint makes dominance elimination premature; route `SH:PF` to `DEFER_EXISTING` until the constraint question is resolved.
- Report `CH:CR` and `SH:WL` together only when they expose materially different defects: the wrong bottleneck and the wrong lever inside the trade-off. When one finding explains the other, merge them in STABILIZE.
- Incomplete dominance evidence stays `DOMINANCE_UNPROVEN`; it neither substitutes for constraint or leverage analysis nor creates a `CH:CR` or `SH:WL` finding by itself.

If no real opposing forces, invalid middle, or live option comparison are present, SH = NOT_APPLICABLE.

Report when the middle hides friction, keeps both costs, lacks a dominant default, lacks a narrow exception, requires an explicit tradeoff decision, misses the real leverage point, or retains a proven dominated option.


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

Classify root cause:
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

Before DECIDE, classify every finding.

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

Choose one path per stabilized issue.

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

Before marking anything ready, approved, or safe to proceed, check whether any ACTION, DECOMPOSE, CONFLICT, review-required status, or blocking unknown remains unresolved.

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
- 3-5 manual spot checks
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
- expectation feels arbitrary
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

Razor is a quick heuristic pass, not a replacement for MAP or the full Thinker lenses.

It detects, classifies, and recommends.
It never changes files.

Quick lens checks:
- CH: invert -> what bad outcome, incentive, misjudgment, weak safety margin, or effort-value mismatch appears?
- OM: simplify -> what unnecessary structure or false simplicity appears?
- FE: reality -> what claim lacks current evidence, clear mechanism, disclosed limits, direct proof, or a validated transition into a higher-trust or control-bearing role?
- PO: refute -> what claim can pass while wrong, contradicts another rule, or lacks a disconfirming check?
- KT: universalize -> what pattern should not become a general rule?
- SH: trade off -> what middle hides unresolved friction or requires explicit decision?

Temporal checks:
- backward: what depends on this?
- forward: what does this constrain?
- staleness: when was it last verified?

Output:
- PASS
- ACTION
- CONFLICT

Severity guide:
1. CH: dangerous avoidable failure or weak safety margin
2. PO: claim can pass while wrong or cannot be refuted
3. FE: reality/evidence integrity gap
4. KT: harmful general rule or unfair exception
5. OM: unnecessary structure or false simplicity
6. SH: unresolved tradeoff or invalid middle

One-line:
Keep what is needed. Remove what is unnecessary.
Verify what is claimed. Refute what can pass while wrong.
Invert what can fail. Universalize only safe patterns.
Make unresolved tradeoffs explicit.

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

One reviewer, one domain, one report.

Procedure:
1. Scope domain and files.
2. Apply Razor, structural checks, relevant domains, and Confidence Gate.
3. Report ACTIONS and CONFLICTS.
4. Do not modify files unless explicitly asked to fix.

Read-only by default.

## 17. SIFT Review

SIFT coordinates expert review findings before action.

Phases:
1. SCAN: run relevant expert reviews.
2. INTEGRATE: merge duplicates/root causes.
3. FIRM CONFIDENCE: check unknowns and detection confidence.
4. TREAT: fix only with explicit approval; safe-change rules apply.
5. VERIFY: run full verification.

SIFT is read-only unless explicitly told to fix.

## 18. Tag Legend

Tags show reasoning origin, not severity.

Thinker lens tags:
- CH: Charlie Munger
- OM: Occam's Razor
- FE: Richard Feynman
- PO: Karl Popper
- KT: Immanuel Kant
- SH: Saffi; includes Follett-style integration vs compromise check

Aspect tags:
- CH:IV inversion / worst material bad outcome
- CH:IN incentives
- CH:SO second-order damage
- CH:MJ misjudgment
- CH:CP competence gap
- CH:SM safety margin
- CH:CR constraint risk
- CH:EV effort-value alignment / disproportionate effort, resource waste, or low-probability completion
- CH:SR scale-up risk

- OM:UE unnecessary entity
- OM:FS false simplicity
- OM:SS speculative structure
- OM:OD oversized design
- OM:AC avoidable complexity
- OM:CF Chesterton fence / unknown protected constraint

- FE:SC stale claim
- FE:ME mechanism gap
- FE:WY missing why
- FE:HL hidden limits
- FE:WE weak evidence
- FE:PG proof gap
- FE:PV purpose/value gap
- FE:TB trust-boundary transition / unvalidated promotion into a higher-trust or control-bearing role

- PO:UF unfalsifiable claim
- PO:CO confirmation-only proof
- PO:CN contradiction
- PO:WR weak refutation path
- PO:SI silent invalidation / silent pass
- PO:OC overclaim

- KT:HU harmful universalization
- KT:EX special pleading / unfair exception
- KT:IR inconsistent rule
- KT:UA unfair asymmetry
- KT:HB hidden burden

- SH:OF opposing forces
- SH:FM fake middle
- SH:FB forced balance
- SH:NE narrow exception needed
- SH:HC hidden conflict
- SH:WL wrong leverage
- SH:PF Pareto frontier / proven dominance

Domain tags:
- SEC: Security
- CPX: Complexity
- REL: Reliability
- DAT: Data / I/O
- ARC: Architecture / interfaces
- CFT: Craft / tests

Notation:
- CH = finding surfaced through Charlie Munger lens
- CH:IV = finding surfaced through CH inversion aspect
- SEC = finding surfaced through Security domain
- CH:IV->SEC = CH inversion surfaced a security-domain issue
- FE:WE+PO:SI = multiple aspects apply to the same finding

Rules:
- use the smallest tag set that explains the finding; prefer 1-3 tags
- use aspect tags when they improve traceability
- multiple tags can apply to one finding
- aspect tags do not replace evidence levels, severity, or output categories
- do not invent numbered QIDs unless the referenced question bank defines them

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
- Never mark an artifact ready while ACTION, DECOMPOSE, CONFLICT, review-required status, or blocking unknown remains unresolved.
- Never give a Task Prompt task-level PASS merely because its child Agent Prompts pass locally.
- Never let exploration, delegation, or repeated gates silently consume the completion reserve required for terminal verification and closure.
- Every task ends as HANDLED or CONFLICT.
- Never modify outside the current task's scope; log adjacent issues separately.

## One-Line Summary

Gate -> Fundamental Scan -> Map -> Confidence -> Stabilize -> Evidence -> Decide -> Act Safely -> Verify -> Learn
