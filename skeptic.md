# Skeptic - Detect, Reason, Fix, Verify

AI-executable framework for safe system improvement.

Candidate status: UNVALIDATED_BEHAVIORALLY.

Rules:
- Correct action over fast action.
- If detection confidence is insufficient, do not act.
- Add process only when it prevents a known failure mode.

## Invocation Contract

`RunSkeptic` formally invokes this framework. Aliases: `beskeptic`, `apply Skeptic`, `Skeptic review`, `run skeptic.md`.

When invoked:
1. Before analysis, read the actual current `skeptic.md` or the explicitly supplied candidate; never substitute memory, summaries, previous variants, or generated replacements.
2. Treat that file as runtime source of truth. Read companions only when it requires them, and apply its recipe exactly and in order.
3. Consider every required Thinker; show major steps, material evidence, and the exact output categories.
4. Do not modify files unless DECIDE says FIX and edits are explicitly allowed.
5. Verify the recommendation against the framework and disclose unresolved conflicts, unknowns, skipped areas, and missing evidence.
6. If the source is unavailable, say so and do not claim RunSkeptic/Skeptic compliance.

### RunSkeptic Receipt

Every report must include this compact receipt:
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

Do not claim compliance without the receipt. It indexes claims and evidence; it is neither proof nor authorization. Material findings must cite supporting evidence. A listed step or Thinker without material application does not establish compliance. If receipt and evidence conflict, correct or explicitly resolve the mismatch before claiming compliance.

Flow: GATE -> FUNDAMENTAL SCAN -> MAP -> CONFIDENCE -> STABILIZE -> EVIDENCE -> DECIDE -> ACT -> VERIFY -> LEARN

## 0. Gate

Proceed only when DONE is testable, scope tractable, wrong-answer cost acceptable, and intent, assumptions, and approach explicit enough to test.

Otherwise:
- undefined DONE -> STOP
- clear but oversized scope -> DECOMPOSE
- multiple interpretations -> proceed only with an evidence-backed, low-risk, testable one
- unresolved or unsafe ambiguity -> CONFLICT

### Smallest credible alternative guard

Before PASS on a plan, prompt, design, or process-heavy artifact, compare the smallest credible alternative that preserves the required outcome, evidence, safety, responsibility, and reversibility. Apply `CH:EV` and `OM:OD`; identify removable structure and justify what remains. If a materially smaller alternative is equally sufficient, return ACTION. Repeating Thinkers or reviews is not evidence of necessity.

The PASS rationale must name the alternative, what it removes, what it preserves, and why retained structure is necessary. Preserve `OM:FS`: never simplify away required proof, safety, ownership, reversibility, or outcomes.

### Prompt Review Levels

Classify prompts before MAP:
- **Agent Prompt**: bounded instruction for one participating role.
- **Dispatch Ticket**: compact delegated Agent Prompt.
- **Task Prompt**: complete Lead-owned execution contract from verified start through terminal DONE.

For a Task Prompt, read required companion `agents/task-prompt.md`. `skeptic.md` remains authoritative for review behavior and categories; the companion cannot override it. Without the companion, do not claim task-level PASS. Lifecycle or integration/publication ownership makes a prompt a Task Prompt regardless of label; material ambiguity about terminal ownership is CONFLICT.

#### Level 1 - Agent Prompt review

Require:
- one clear role, objective, source of truth, and scope;
- explicit allowed/forbidden actions;
- proportionate model/effort and context/output limits when material;
- defined inputs, durable outputs, acceptance checks, and stop conditions;
- a verifiable compact Agent Receipt;
- no silent scope expansion or self-promotion into task-level completion.

#### Level 2 - Task Prompt review

Review child correctness and end-to-end feasibility; locally valid child prompts alone cannot earn task-level PASS.

Require evidence that:
- terminal DONE is exact, observable, and distinct from intermediate states;
- starting state, authority, source-of-truth order, scope, and protected state will be verified;
- available context, tokens, time, credits, tools, permissions, and evidence can realistically complete the objective;
- phases form a coherent dependency graph with bounded ownership, inputs, outputs, acceptance checks, and next-state rules;
- model, effort, agents, context, outputs, and protocol cost are proportionate;
- a protected completion reserve covers synthesis, verification, integration, external confirmation, and closure;
- when handoff, interruption, context clearing, independent review, delegation, repeated execution, or cross-session continuation requires survival, decision-critical outputs are persisted in an authorized runtime-selected location and verified before dependent phases;
- retries and gates are bounded, repeated failure triggers redesign, and futile optional work can stop;
- a pre-exhaustion handoff preserves verified state without claiming DONE;
- system verification and disconfirming cases cover the requested outcome;
- integration, publication, and fresh external verification are explicit when part of DONE;
- the Task Closure Receipt can prove every requested terminal condition.

Persistence is conditional. Skeptic prescribes no canonical controller, directory, filesystem, database, or storage mechanism; its checkout is not the default writable workspace. A bounded one-session task with no material handoff, resume, delegation, independent review, repeated execution, or cross-session consumer may PASS without durable state. When survival is material, missing or inadequate authorized persistence is ACTION; transient context never counts as surviving a boundary it did not survive.

Material failures include:
- missing dependency, integration owner, evidence checkpoint, or closure path despite locally valid children;
- context protection without allocation, measurable substitute, or stop threshold;
- optional exploration/worker work consuming completion reserve;
- unbounded fix-until-PASS, retry, or gate loops without redesign triggers;
- ending at analysis, patch, branch, commit, pull request, local merge, or push attempt when DONE requires more;
- protocol cost approaching/exceeding expected value or probability of useful completion.

Task-level gate decisions:
- `PASS`: no blocking child- or task-level finding.
- `ACTION`: repairable prompt defect.
- `DECOMPOSE`: clear objective, but workflow too large/coupled for one Task Prompt.
- `CONFLICT`: unresolved authority, source of truth, design, safety, or completion path.

`DECOMPOSE` is a DECIDE path, not a final outcome. Full Skeptic ends HANDLED or CONFLICT. Never execute or promote with unresolved ACTION, DECOMPOSE, CONFLICT, review-required status, or blocking unknown.

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

Use full name + abbreviation first, then abbreviation. Each Thinker is a lens, not a checklist. Inspect all; report only material findings affecting PASS, ACTION, or CONFLICT. Use aspect tags for traceability.

### Charlie Munger (CH) - Inversion, Incentives, Misjudgment, Safety Margin

- `CH:IV` inversion: worst material outcome and whether evidence, limits, responsibility, or reversal block it
- `CH:IN` incentives rewarding noise, shortcuts, fake certainty, gaming, shallow compliance, or skipped verification
- `CH:SO` second-order damage: downstream harm, hidden cost, brittleness, drift, or confusion
- `CH:MJ` misjudgment: confidence without evidence, coherent stories without verification, one-lens thinking, assumptions as facts
- `CH:CP` competence gap: deciding without sufficient evidence or domain understanding
- `CH:SM` weak safety margin: failure not bounded, visible, reversible, owned, or checked
- `CH:CR` constraint risk: effort targets a non-bottleneck while the real blocker remains
- `CH:EV` effort-value misalignment: cost/rigor/resources disproportionate to expected value, risk reduction, importance, resources, or completion probability
- `CH:SR` scale-up risk: small success may fail with load, frequency, concurrency, data, dependencies, or organizational scale

### Occam's Razor (OM) - Parsimony, Necessity, Sufficiency

Remove unnecessary structure without removing what proves, protects, assigns responsibility for, or makes the outcome reversible.
- `OM:UE` unnecessary entities: assumptions, steps, abstractions, options, or parts without verified current need
- `OM:FS` false simplicity: simplification proves/protects less or breaks the required outcome
- `OM:SS` speculative structure before repeated concrete need
- `OM:OD` oversized design beyond required outcome, evidence, safety, responsibility, or reversibility
- `OM:AC` avoidable complexity from misplaced boundaries, mixed concerns, or missing small guards
- `OM:CF` Chesterton fence: removal before understanding the protected constraint

### Richard Feynman (FE) - Reality, Mechanism, Evidence Integrity

- `FE:SC` stale claim: not true now, undated, or not recently verified
- `FE:ME` mechanism gap: what happens is stated without how/why
- `FE:WY` missing why for a non-obvious choice
- `FE:HL` hidden limits: omitted assumptions, failures, edges, or contradictory evidence
- `FE:WE` weak evidence: proof does not directly exercise/support the claim
- `FE:PG` proof gap: confidence, authority, elegance, or story substitutes for observation
- `FE:PV` purpose/value gap: unclear useful outcome, user, owner, or value
- `FE:TB` trust-boundary transition: untrusted/lower-authority/unverified content, output, or state enters a higher-trust or control-bearing role without consequence-proportionate validation or authorization

Higher-trust/control roles include instruction, permission, verified evidence, source of truth, executable input, policy, configuration, and safety/control signal. Every `FE:TB` finding must name the lower-trust source, promoted role, boundary crossed, and missing validation/authorization.

### Karl Popper (PO) - Falsifiability, Refutation, Contradiction

- `PO:UF` unfalsifiable claim: no observation, example, check, or condition could disprove it
- `PO:CO` confirmation-only proof: support exists but no serious disconfirming case was tried
- `PO:CN` contradiction among rules, assumptions, examples, outputs, or acceptance criteria
- `PO:WR` weak refutation path: wrong result detected late, manually, or never
- `PO:SI` silent invalidation: artifact appears valid while violating its claim
- `PO:OC` overclaim: checks treated as proof rather than limited corroboration

### Immanuel Kant (KT) - Universalizability, Consistency, Fair Exceptions

Treat people as ends, not merely as means; do not make a system work by hiding burdens or denying dignity.
- `KT:HU` harmful universalization: bad if used everywhere or by every similar actor
- `KT:EX` special pleading: one case gets an unjustified exception
- `KT:IR` inconsistent rule under broad or symmetric application
- `KT:UA` unfair asymmetry: similar actors/cases/users/files/decisions treated differently without justification
- `KT:HB` hidden burden: ambiguity, cost, risk, or cleanup shifted to another person or group

### Saffi (SH) - Trade-off Integration, Dominance, Exceptions

Detect invalid middles, unresolved tradeoffs, and proven dominance without erasing protected differences.
- `SH:OF` opposing forces: what each side protects and costs
- `SH:FM` fake middle: compromise keeps both costs without resolving tension
- `SH:FB` forced balance where one side should dominate
- `SH:NE` narrow protected exception to a justified default
- `SH:HC` hidden product, architecture, safety, ownership, or priority conflict
- `SH:WL` wrong leverage: chosen default/middle/exception misses the outcome-limiting constraint
- `SH:PF` Pareto frontier / proven dominance: eliminate only when another option is safely no worse on every protected dimension and strictly better on at least one

#### SH:PF decision rule

Use only with at least two live options; authority, source of truth, ownership, and hard safety blockers run first. These routing results do not replace final categories:
- `NOT_APPLICABLE`: no live comparison; add no frontier process.
- `DEFER_EXISTING`: an earlier check decides/blocks; do not duplicate or override it.
- `DOMINANCE_UNPROVEN`: comparison or elimination guard unresolved; preserve the option and use existing evidence/trade-off/exception/CONFLICT handling.
- `PRESERVE_FRONTIER`: valid comparison, no proven domination; keep all non-dominated options.
- `ELIMINATE_DOMINATED`: one option is proven dominated.

A dominates B only when:
1. disaggregated decision-relevant dimensions share direction, scope, horizon, evidence standard, and tractability assumptions, including hard constraints and protected minority/subgroup outcomes;
2. evidence is current, material uncertainty uses credible intervals, and causal superiority is not inferred from correlation alone;
3. A is safely no worse only when its lower credible bound >= B's upper bound, and strictly better only when its lower bound > B's upper bound;
4. A is safely no worse on every protected dimension and strictly better on at least one—weighted totals, averages, and grouping cannot substitute;
5. B has no missing minority/subgroup benefit, long-tail value, uncertainty-sensitive upside, reversibility/information value, strategic option value, narrow exception, or legitimate stakeholder weighting.

Missing basis or guard means `DOMINANCE_UNPROVEN`. If neither is strictly better, preserve both; OM may separately test true duplicates. For `ELIMINATE_DOMINATED`, report both options, dimensions, evidence/uncertainty basis, and preservation guards.

#### Constraint, leverage, and dominance routing

- `CH:CR`: is effort aimed at the real system constraint?
- `SH:WL`: within a tradeoff, does the choice act on the limiting lever?
- `SH:PF`: is a live comparable option proven dominated?

Apply only present lenses. Default order: constraint, leverage, dominance; skip absent stages. A live `CH:CR` blocks elimination (`DEFER_EXISTING`). Report `CH:CR` and `SH:WL` together only for materially distinct defects; otherwise merge in STABILIZE. Incomplete dominance evidence creates neither constraint nor leverage findings. With no opposing forces, invalid middle, or live comparison, SH = NOT_APPLICABLE.

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

Before STABILIZE/DECIDE confirm:
- Fundamental Scan and Universal Questions completed
- all Thinkers considered: CH, OM, FE, PO, KT, SH; SH has a finding or NOT_APPLICABLE
- Structural Checks applied; Domain Checks selective; artifact patterns used when useful
- important conclusions have evidence; unknowns and skipped areas are listed

Track unknown owner/SoT/contract/dependency, behavior/risk boundary/revert/test path, and acceptance criteria. Treat unresolved ownership, interface/link, behavior, weak tests, missing failure signal, suspiciously clean results, skipped local areas, or downstream dependence on unresolved fundamentals as blind spots.

If weak, expand MAP only where evidence requires, sample adjacent domains, run CH/PO adversarially on suspiciously clean results, and resolve/decompose/escalate high-risk unknowns. CONFLICT when confidence cannot reasonably improve. Do not loop indefinitely.

## 7. Stabilize

Never decide on raw findings. Merge findings sharing data, boundary, responsibility, interface, source of truth, failure mode, or root cause.

Classify root cause as local bug, missing test/contract, unclear ownership, source-of-truth issue, accidental coupling, stale assumption, systemic rule issue, or detection-confidence issue. Check overlapping/conflicting/redundant fixes, one finding explaining another, blocking unknowns, local/systemic risk, reversibility, blast radius, ownership, and confidence.

Output stabilized issues; raw findings remain PROVISIONAL.

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

Use only when root cause/structure/connections/SoT and material unknowns are clear or irrelevant; the change is reversible, testable, retryable, low/medium risk; confidence and verification are adequate; and justification is complete.

Before FIX state what/why is wrong, why this fix is correct and the smallest verified scope, what would disprove it, and how to verify/revert.

### DECOMPOSE

Use when scope/risk is high but structure can split safely by responsibility, interface, source of truth, data flow, testable slice, reversible step, or unknown. Every step returns to GATE.

### CONFLICT

Use for multiple valid designs; unclear owner/SoT/connection/contract; required product/architecture intent; non-reversible change; ambiguity surviving decomposition; or inadequate confidence. Do not decompose pure conflict to avoid escalation.

### Promotion Check

Do not mark ready/approved/safe while ACTION, DECOMPOSE, CONFLICT, review-required status, or blocking unknown remains. Route to FIX, DECOMPOSE, or CONFLICT.

## 10. Act

Act only after DECIDE says FIX:
1. preserve prior state;
2. apply the smallest reversible change;
3. verify immediately;
4. revert immediately on failure;
5. retry only when safer or better informed;
6. escalate if safe retry is impossible;
7. finish verification or safe reversion before another task.

Never leave partial/unknown or hidden-dependent state; implement unresolved conflict; remove links without replacement/explicit coupling decision; accept silent failure; broaden into unnecessary refactor/speculation/abstraction; violate existing style unless it is the verified problem; or edit outside scope. Log adjacent improvements separately.

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

Razor is a quick read-only heuristic, never a replacement for MAP or full Thinker lenses. It detects, classifies, and recommends PASS, ACTION, or CONFLICT.

Check CH for avoidable failure/incentives/misjudgment/safety margin/effort-value; OM for unnecessary structure or false simplicity; FE for current evidence, mechanism, limits, proof, value, and trust transitions; PO for falsifiability, contradiction, and disconfirmation; KT for unsafe universalization, unfairness, hidden burden, and dignity; SH for unresolved tradeoffs, invalid middles, exceptions, leverage, and dominance. Also check backward dependencies, forward constraints, and staleness.

Prioritize dangerous failure, silent invalidity, reality/evidence gaps, human unfairness, false simplicity, then unresolved tradeoffs. Keep what is necessary; remove what is not; verify claims; refute silent passes; make tradeoffs explicit.

## 15. Artifact Guide / External Questions

After Universal and Structural Checks, use patterns as detection aids, not exhaustive rules. `skeptic-questions.md` expands SEC/CPX/REL/DAT/ARC/CFT only when needed; runtime core remains authoritative and the companion adds no mandatory process.

Sample likely failures:
- Code/tests: dead or weak structure, unsafe commands/SQL, missing timeout/retry/cleanup/coverage, shared or environment-dependent tests, tests never red, silent wrong-input success.
- Config/data: dead fields, disguised constants, inconsistent names/types/units, stale paths/services, bad defaults, missing validation/persistence/consistency checks.
- Prompts/docs: missing why/prerequisites, broad or contradictory rules, stale tool behavior, suppressed errors, skipped verification, hidden assumptions, untested commands.
- Design/requirements: unclear user value, untestable or stale need, over-generalization, lock-in, implicit dependency, no observability, single point of failure, or missing acceptance criteria.

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

Tags show reasoning origin, not severity. Thinkers: CH Charlie Munger; OM Occam; FE Feynman; PO Popper; KT Kant; SH Saffi/Follett-style integration.

Aspect tags (defined in §3):
- CH: `CH:IV`, `CH:IN`, `CH:SO`, `CH:MJ`, `CH:CP`, `CH:SM`, `CH:CR`, `CH:EV`, `CH:SR`
- OM: `OM:UE`, `OM:FS`, `OM:SS`, `OM:OD`, `OM:AC`, `OM:CF`
- FE: `FE:SC`, `FE:ME`, `FE:WY`, `FE:HL`, `FE:WE`, `FE:PG`, `FE:PV`, `FE:TB`
- PO: `PO:UF`, `PO:CO`, `PO:CN`, `PO:WR`, `PO:SI`, `PO:OC`
- KT: `KT:HU`, `KT:EX`, `KT:IR`, `KT:UA`, `KT:HB`
- SH: `SH:OF`, `SH:FM`, `SH:FB`, `SH:NE`, `SH:HC`, `SH:WL`, `SH:PF`

Domains: SEC Security; CPX Complexity; REL Reliability; DAT Data/I/O; ARC Architecture/interfaces; CFT Craft/tests.

Notation: `CH` identifies a lens; `CH:IV` an aspect; `SEC` a domain; `CH:IV->SEC` an aspect surfacing a domain issue; `FE:WE+PO:SI` multiple aspects. Prefer the smallest explanatory set (usually 1–3); use aspects for traceability. Tags never replace evidence, severity, or output category. Do not invent QIDs absent from the question bank.

## 19. Invariants

- Never act without testable DONE, stabilization, adequate detection confidence, and a FIX decision.
- For self-work read authoritative current `skeptic.md`; for candidate review read and identify the non-authoritative candidate. Never substitute memory/summary/generated variants or claim compliance when source/application is unavailable.
- Consider every Thinker; use NOT_APPLICABLE where appropriate. No findings or a clean top-down scan is never proof of safety.
- Never present inferred risk as confirmed, ignore material unknowns, remove without understanding breakage, break links without replacement/decision, or execute unresolved conflict.
- Never accept silent failure, partial/hidden-dependent state, or retry without safer/new evidence.
- Repeated local fixes may indicate systemic or detection failure; every completed task has an outcome.
- Never promote with ACTION, DECOMPOSE, CONFLICT, review-required status, or blocking unknown unresolved.
- Never grant Task Prompt PASS from child-prompt PASS alone or let exploration/delegation/gates consume terminal completion reserve.
- Every task ends HANDLED or CONFLICT. Keep edits in scope and log adjacent issues separately.

## One-Line Summary

Gate -> Fundamental Scan -> Map -> Confidence -> Stabilize -> Evidence -> Decide -> Act Safely -> Verify -> Learn
