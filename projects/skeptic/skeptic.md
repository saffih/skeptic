# Skeptic - Detect, Reason, Fix, Verify

- **Original author:** Saffi Hartal

AI-executable framework for safe review and improvement.

Rules:
- Correct action over fast action.
- If required coverage or evidence is insufficient, do not fix or promote; gather evidence, decompose, or escalate.
- Add process only when it addresses a specific credible failure mode.
- Treat the chosen approach and its realization as reviewable, not as fixed premises. When their observed consequences are material, use those consequences as evidence about the assumptions, boundaries, and approach involved; do not treat existing realization as authority or an observed pattern as proof of causation.

## Invocation Contract

`RunSkeptic` is the formal invocation string for the complete Skeptic framework.

Aliases: `beskeptic`, `apply Skeptic`, `Skeptic review`, `run skeptic.md`.

`Razor` is the formal invocation string for the bounded read-only diagnostic in §14. `Expert Review` is a compatibility phrase for Razor with an explicitly scoped domain; it does not invoke a separate review pipeline.

The invocation selects the review depth; the request determines permission and stopping conditions. RunSkeptic is read-only unless fixing is explicitly authorized; verification emphasis or iterative repetition must also be requested. Razor is always read-only.

When RunSkeptic is invoked:
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

An explicit RunSkeptic invocation may additionally name companion files; they add context but do not replace or override the designated Skeptic source.

Each repeated RunSkeptic run is a new invocation for source-freshness purposes: perform Rule 1 again. An earlier read does not satisfy a later run.

For deterministic RunSkeptic binding, a formal invocation records:

```text
INVOCATION_ID: <id>
INVOCATION_KIND: SINGLE | FIND_LOOP | FIX_LOOP | INNOSKEPTIC | INOSKEPTIC
PERMISSION_MODE: read-only | patch-local | fix-if-valid
DONE: <testable statement>
TARGET_TASK_REFERENCE: <explicit interpretable task/scope reference>
REVIEWED_ARTIFACT_REFERENCE: <reference>
REVIEWED_ARTIFACT_SHA256: <sha256 of exact reviewed artifact bytes>
SKEPTIC_SOURCE_PATH: skeptic.md
SKEPTIC_SOURCE_REF: <ref>
SKEPTIC_SOURCE_BLOB_SHA: <blob sha>
APPLICABLE_COMPANIONS: <explicit list of companion/domain references>
MATERIAL_FINDINGS: <explicit list of material finding identifiers or summaries>
PREVIOUS_FINDINGS_REFERENCE: <reference or NONE>
```

The designated source is freshly read before analysis. The artifact hash and Skeptic blob bind reproducible byte-level objects; semantic bindings remain explicit and interpretable rather than using exact-looking hashes whose input representation is undefined. These fields bind the receipt to that read and to the complete current artifact; they do not prove hidden runtime context, model cognition, or actual model/provider routing.

`patch-local` is a compatibility permission spelling, not a separate action standard. When accepted, it remains bounded by the explicit task scope and the same normative-warrant, confidence, DECIDE=FIX, and verification requirements as `fix-if-valid`.

### RunSkeptic Receipt

Every RunSkeptic report must include a compact receipt:
- Source read: path/ref/SHA or explicit unavailable state
- Companion files read, if any
- Permission mode: read-only / patch-local / fix-if-valid
- DONE statement
- Major steps run
- Thinkers considered
- Evidence used
- Blind-spot challenge result
- Decision path
- Verification performed
- Unresolved conflicts / unknowns
- Final output category

Do not claim RunSkeptic compliance without this receipt.

A RunSkeptic receipt indexes the review and its evidence; it is not independent proof or authority. A material receipt claim that conflicts with primary evidence must be corrected or left unresolved.

### Loop Invocations

#### Artifact Relay

`artifact-relay` — Before Find/Fix work likely to exhaust context or repeat substantial reads, bounded side-work delegation is optional and should be used only when expected to reduce total context, cost, repetition, or failure risk after overhead.

One loop owner remains responsible for freshly reading the applicable Skeptic source and complete current artifact, executing the full recipe, reevaluating prior findings, preserving unresolved states, and enforcing convergence and reset criteria. Delegated findings, reports, receipts, or evidence may support work but never substitute for required fresh coverage or count as unchanged qualifying passes. Report unobserved freshness, validity, or coverage as `UNKNOWN`; if complete coverage is infeasible, stop with `CONFLICT`.

How context is packaged and which execution route is selected belong to the execution environment when it has governing policies; standalone Skeptic does not require such policies to operate.

Retry and convergence are distinct. Retrying a failed action requires new evidence or a changed relevant condition that justifies another attempt; required convergence may deliberately repeat unchanged complete review because stable repetition is itself assurance evidence.

`RunSkeptic Find Loop` invokes repeated full read-only RunSkeptic reviews. Unless the explicit invocation sets another count, stop only after three consecutive runs produce no new meaningful finding and no material change to an existing finding.

Find Loop inputs bind DONE, the Target Task, complete reviewed artifact, Skeptic source blob, applicable companions, invocation kind, and permission mode. Reset the consecutive count after any change to those bindings or after any new or materially changed finding, because detection stability must describe repeated review of one exact comparison.

In Find Loop, the first unchanged pass with no new substantive core finding triggers one domain-discovery step before core-only stability can count toward final convergence.
Bind the selected domain set as applicable companions and reset the convergence count when that binding changes.
Reuse that selected set while the Target Task, reviewed artifact, bound scope, material dependencies, and other domain-relevance inputs remain unchanged; rediscover domains only when a material change could alter relevance.

For each Find Loop run:
- freshly read the designated current Skeptic source and execute the complete recipe
- re-evaluate the complete artifact and all previous findings
- make no modifications
- stabilize duplicates and distinguish new findings from restatements
- record new, changed, resolved, and still-open findings
- return material findings as scoped suspicions rather than task-level conclusions; preserve direct observations and evidence as such, and state the review scope, assumptions, and unknowns; the receiving Core retains responsibility to reevaluate each finding against wider authoritative context before task-level action or artifact promotion
- reset the consecutive-run count after any new or materially changed finding

Find Loop convergence means detection stabilized; it does not mean the artifact passed or is ready. Report every unresolved ACTION, DECOMPOSE path, CONFLICT, and blocking unknown, and every applicable required review that has not been completed.

`RunSkeptic Fix Loop` invokes repeated full RunSkeptic review-and-fix cycles. Unless the explicit invocation sets another count, stop successfully only after three consecutive qualifying passes on the same unchanged artifact state.

External loop state binds DONE, the Target Task, complete reviewed artifact, Skeptic source blob, applicable companions, material finding set, invocation kind, and permission mode. Reset the qualifying count after any change to one of those bindings or to a material finding. A repair run and a delta-only review never qualify. Unless explicitly overridden, completion requires three unchanged qualifying passes.

For each Fix Loop run:
- freshly read the designated current Skeptic source and execute the complete recipe
- re-evaluate the complete artifact, including all previously HANDLED areas
- fix every authorized material issue that DECIDE validly classifies as FIX
- verify every change immediately
- after any change, restart the complete review and reset the consecutive-pass count

A repair run does not count as a qualifying pass. A run qualifies only when no change is made, every material finding is PASS, all required verification passes, no unresolved ACTION, DECOMPOSE path, CONFLICT, or blocking unknown remains, and every applicable required review is completed.

If safe evidence-backed progress cannot continue, stop with CONFLICT rather than loop indefinitely or claim completion.

`InnoSkeptic` (Innovative Skeptic) invokes repeated innovation-selection cycles. Aliases: `Innovative Skeptic`, `INNO Skeptic`, `InoSkeptic` (legacy). Unless the explicit invocation sets another count, stop successfully only after one defensible candidate remains or a complete cycle yields no material improvement or justified narrowing.

Bind one goal and set of constraints.

For each InnoSkeptic run:
- generate several materially distinct candidates satisfying the bound constraints
- vary, mutate, recombine, or add candidates based on prior evidence
- for every candidate mutation, state the exact new claim or protection it adds, who already owns or proves that claim, and whether any new term implies more than the mechanism establishes; reject mutations that only duplicate existing evidence or broaden the claim without new evidence
- freshly read the designated current Skeptic source and RunSkeptic on the complete candidate set using shared evidence
- use findings and newly established evidence to improve and narrow the set
- eliminate only approaches defeated by the bound requirements or demonstrably dominated by others on all material protected dimensions
- preserve unresolved nondominated candidates
- if any candidate changed or evidence expanded, restart the complete review

InnoSkeptic convergence means one defensible candidate remains or a complete cycle yields no material improvement or justified narrowing. Do not force one winner when alternatives remain nondominated.

Flow: GATE -> ORIENT -> MAP -> BLIND-SPOT -> STABILIZE -> DECIDE -> ACT -> VERIFY -> LEARN

## 0. Gate

Proceed when:
- DONE is testable
- scope is tractable
- wrong-answer cost is acceptable
- intent, assumptions, and chosen approach are explicit enough to test

If not:
- undefined DONE -> CONFLICT; make no action
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
- retries and repeated review/fix loops have explicit stopping rules; outside required convergence, retry only when new evidence or a changed relevant condition justifies another attempt, and change the method, decompose, or escalate when repeated effort produces little decision-relevant evidence;
- decision-critical state is persisted only when it must survive a real boundary such as delegation, interruption, context loss, independent review, or cross-session continuation.

A well-written prompt or set of locally valid child steps cannot earn task-level PASS when the overall completion, integration, or verification path is infeasible or unowned. Missing feasibility is ACTION when locally repairable, DECOMPOSE when the objective is clear but too large or coupled, and CONFLICT when authority, design, safety, source of truth, or terminal completion remains unresolved.

No companion file is required for this core review. A supplied companion may add context-specific constraints but cannot override Skeptic.

## 0.5. Orient

Before broad detection, establish only the minimum provisional frame needed to avoid wrong-frame reasoning:
- purpose and required outcome;
- relevant coarse architecture/artifact shape and main path;
- authority, ownership, and source-of-truth ordering;
- critical boundaries and explicitly material high-risk, recent, or suspected areas.

Rules:
- provisional and revisable; detect only;
- leave detailed interfaces, coupling, retry, reversibility, and failure-signal inspection to MAP/Structural Checks unless needed to establish an invalidator;
- if material orientation uncertainty could invalidate local reasoning, record it as UNKNOWN and block dependent conclusions;
- clean orientation is not evidence of local correctness;
- if later findings cluster around one mechanism, boundary, source, ownership rule, or assumption, test for a shared structural cause;
- if a material orientation fact changes, use MAP reopening to invalidate dependent reasoning.

## 1. Map - Detect Only

Record findings before deciding.

Start from ORIENT; expand as needed.

Within the bound scope, explicit target areas, suspected weak points, or requested aspects receive additional adversarial attention without narrowing the otherwise applicable review.

Apply:
1. Universal Questions
2. All Thinkers: CH, OM, FE, PO, KT, AJ, SH
3. Structural Checks
4. Domain Lens Escalation under §5 when applicable
5. Artifact patterns / external question banks when useful

Output:
- findings
- unknowns; for each material UNKNOWN, record the claim, decision, action, or coverage obligation it can affect; if that dependency cannot be bounded safely, preserve the broader dependent scope
- assumptions, including intent and approach assumptions; challenge them before DECIDE
- for each material claim/finding, applicable evidence level(s) and scope under §8 when decision-relevant
- live required/applicable coverage state, including completed, NOT_APPLICABLE, skipped, or UNKNOWN obligations when material

No fixes. No final decisions.

Extend discretionary investigation only while plausible new evidence could materially change a decision enough to justify its cost. Required coverage, verification, promotion, and convergence obligations are not discretionary. When repeated effort produces little decision-relevant evidence, change method, decompose, or escalate.

When new evidence materially changes an assumption, authority/source-of-truth binding, scope, boundary, or causal premise, reopen the affected reasoning and invalidate dependent stabilized issues, decisions, or completion state until reconsidered. If the dependency cannot be bounded safely, broaden reconsideration only as necessary.

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
- `CH:EV` effort-value alignment: choice or allocation of effort, cost, rigor, process, or resources is disproportionate to expected value, material risk reduction, decision importance, available resources, or the probability of reaching a completed useful outcome
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

Do not simplify by deleting protections whose purpose is not understood. Distinguish the required protection from the mechanism currently providing it; a mechanism may be simplified or replaced only when the protection is preserved. When substantial structure remains, state briefly why the smaller alternative is insufficient.

### Richard Feynman (FE) - Reality, Mechanism, Evidence Integrity

Find where explanation outruns reality.

- `FE:SC` stale claim: a materially time-dependent claim or action is unsupported unless its current state is established by explicit context or sufficiently fresh authoritative evidence; never substitute model knowledge for current state, and use `UNKNOWN` if it cannot be established.
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
- `PO:CG` coverage gap: derive material obligations for the reviewed scope from the bound task and applicable normative basis, and ask what required element could be absent while what is present still appears correct; do not invent obligations the basis does not support. Report supported omissions under normal materiality rules; when completeness, conformance, readiness, or full implementation is claimed, any material obligation not mapped to the artifact and supporting evidence blocks promotion

### Immanuel Kant (KT) - Universalizability, Consistency, Fair Exceptions, Harm Minimization

Find patterns that should not become general rules, and evaluate whether chosen paths unnecessarily harm or create unresolvable moral conflicts.

- `KT:HU` harmful universalization: bad if used everywhere or by every similar actor
- `KT:EX` special pleading: one case gets an exception similar cases should not get
- `KT:IR` inconsistent rule: contradicts itself when applied broadly or symmetrically
- `KT:UA` unfair asymmetry: similar actors, cases, users, files, or decisions are treated differently without justification
- `KT:HB` hidden burden: works only by shifting ambiguity, cost, or cleanup to someone else
- `KT:HHB` hidden human burden: appears successful only by shifting avoidable ambiguity, cognitive load, repeated back-and-forth, coordination effort, delay, cost, risk, or cleanup onto another person or group
- `KT:NH` no harm: chosen action causes avoidable material harm when a feasible less-harmful path meets the same requirements without greater material sacrifice
- `KT:MC` moral conflict: every feasible path materially harms or sacrifices a protected party, duty, right, or value; surface the competing harms and obligations for explicit accountable judgment
- `KT:OC` ought implies can: no permitted feasible path lets the responsible actor satisfy all applicable requirements simultaneously under its authority, capabilities, resources, dependencies, and constraints; if feasibility is unestablished, record unknown; preserve protected requirements when restoring feasibility; add `PO:CN` only when conflicting rules cause the impossibility

### Alicia Juarrero (AJ) - Invariants, Constraints, Adaptation

Find what is wrongly fixed, wrongly left free to vary, or only nominally flexible. Identify what must remain invariant, what must deliberately remain adaptable, where each belongs, and whether the mechanism that provides flexibility is suitably bounded so adaptation does not weaken protected invariants.

- `AJ:IN` invariant placement: something essential to purpose, identity, coherence, safety, authority, or required outcome is allowed to vary where it materially must remain fixed
- `AJ:OC` overconstraint: rules, specifications, plans, or processes remove degrees of freedom that need not be fixed to protect a material invariant and thereby create brittleness, friction, lost adaptation, or unnecessary failure
- `AJ:UC` underconstraint: discretion or variation remains where changing the thing can materially break purpose, identity, coherence, safety, authority, or the required outcome
- `AJ:AF` adaptive freedom: a degree of freedom materially needed for adaptation, substitution, extension, local judgment, experimentation, or future evolution is absent, merely nominal, implemented through an unsuitable mechanism, or granted with broader authority or variation than needed; require a concrete mechanism that provides the needed flexibility while preserving the relevant invariants and bounded authority
- `AJ:EC` enabling constraint: an arrangement restricts local freedom without sufficiently protecting or enabling the capability, coherence, coordination, resilience, or safe freedom that justifies the restriction
- `AJ:JB` joint/boundary: invariant and adaptive regions meet without a clear mechanism defining what may vary, how variation is realized, what must remain preserved, who or what may adapt it, and where the flexibility stops
- `AJ:RL` rigidity leakage: a constraint justified for one protected invariant spreads into neighboring mechanics, evidence methods, procedures, or choices that do not require the same exactness
- `AJ:FL` flexibility leakage: discretion justified inside an adaptive region spreads across a boundary into an invariant or protected region

For material rules, requirements, plans, processes, or designs, ask: are the right things constrained and the right things adaptable, in the right places? Where flexibility is needed, is there a suitable bounded mechanism that provides it without weakening the invariants it must preserve? Treat deliberate flexibility as a designed capability, not as mere absence of constraint or specification.

### Saffi (SH) - Trade-off Integration, Dominance, Exceptions

Find invalid middles and unresolved tradeoffs.

- `SH:OF` opposing forces: what each side protects and what each side costs
- `SH:FM` fake middle: compromise keeps both costs without resolving the tension
- `SH:FB` forced balance: the artifact tries to satisfy both sides when one side should dominate
- `SH:NE` narrow exception needed: one side should be default, but the other side needs a narrow protected exception
- `SH:HC` hidden conflict: product, architecture, safety, ownership, or priority decision is required
- `SH:WL` wrong leverage: within a genuine trade-off, the chosen side, middle, or exception does not materially affect the outcome it is intended to improve
- `SH:PF` dominance/frontier: a live option is retained even though another feasible option is no worse on every material protected dimension and better at least one

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

## 5. Domain Lens Escalation

Domain lenses add detection; they do not narrow or replace the core review.
Core-first is the default for domain lenses.

At domain discovery, read `skeptic-questions.md` as the lightweight registry to identify candidate domains and their files.
Domain identifiers and applicability metadata are defined by the registry; the core does not enumerate the complete domain set.
After selection, load only the mapped domain files.

Domain lenses produce findings, unknowns, and evidence; evidence semantics, STABILIZE, and DECIDE remain owned by the core.

Rules:
- Activate a specifically relevant domain early when the request explicitly names it or material domain relevance is already established; use the registry to resolve repository-owned domain files when needed.
- Generic risk alone does not justify early domain activation.
- Otherwise, discover domains only after broad core detection has substantially stabilized and another broad pass has low expected marginal detection value.
- Treat substantive findings qualitatively: material effect on correctness, safety, architecture, authority, scope, action, verification, or task outcome matters more than finding count.
- Select all materially useful domains, not one winner, but do not load a lens whose expected detection value is already adequately covered by the core or selected lenses.
- In an ordinary run, a substantive domain finding may end further domain probing when continuing has low marginal value and broader coverage is not required.
- Do not treat unexamined selected domains as clean or exhausted.
- For Find Loop, readiness, completeness, promotion, or explicitly exhaustive review, continue across the selected domain set sufficiently to support the claimed coverage.
- If a selected domain companion is unavailable, record the missing coverage as skipped/UNKNOWN; continue core review when feasible and do not overclaim domain-aware coverage.

## 6. Blind-Spot Challenge

Before STABILIZE, challenge apparent completeness once.

Ask whether an important decision-relevant area could still be missing despite apparently complete recorded coverage. Pay particular attention to suspiciously clean results, skipped regions, changed applicability, hidden dependencies, and conclusions supported mainly by affirmative evidence.

Reopen MAP only when a materially different inquiry has plausible decision-changing value; if the blind spot changes authority, source-of-truth, main-path, or other orientation framing, reopen ORIENT and all dependent MAP reasoning. Do not replay coverage bookkeeping or turn this challenge into a second MAP. If a material blind spot remains unresolved, record the affected claim or coverage obligation as UNKNOWN and block dependent promotion.

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
- coverage/evidence gap

Check:
- overlapping, conflicting, or redundant fixes
- one finding explaining another
- unknowns blocking action
- local/systemic risk
- reversibility, blast radius, ownership clarity, evidence sufficiency

Output stabilized issues.

Raw findings remain PROVISIONAL until stabilized.

When stabilizing or merging findings, preserve any distinction in coverage, uncertainty, evidence, causation, scope, conditions, alternatives, or authority that could change DECIDE. Merge duplication, not decision-relevant meaning.

## 8. Evidence Semantics

Evidence qualifies material claims/findings when they are recorded or materially updated; it is not a separate post-STABILIZE assignment stage. At decision-relevant granularity, attach the applicable evidence level or levels and their scope. Do not require a label for a trivial observation when it cannot change a material claim, decision, verification burden, or promotion state.

- OBSERVED: directly seen in code, tests, config, docs, or runtime behavior.
- REPRODUCED: confirmed with failing test, probe, command, or execution.
- HISTORICAL: confirmed by issue, changelog, CVE, advisory, maintainer note, or release note.
- INFERRED RISK: plausible from structure, boundary, exposure, missing tests, or weak evidence, but not reproduced.

Rules:

Evidence semantics and UNKNOWN are orthogonal: evidence states what supports a claim and its scope; UNKNOWN states what decision-relevant support or dependency remains unresolved. They may coexist on distinct aspects of the same issue.

Evidence strength applies only to the exact claim and scope it supports. Evidence for one subclaim, environment, path, time, population, or condition does not automatically establish a broader claim or strengthen a different subclaim.

Treat absence or non-observation as evidence only when the observation method and its relevant scope, duration, and instrumentation could reasonably have detected the condition if it were present. Otherwise record UNKNOWN or only the narrower observed fact.

- Do not report INFERRED RISK as confirmed bug.
- Security/parser/sanitizer INFERRED RISK becomes PROVISIONAL ACTION or CONFLICT.
- FIX requires OBSERVED evidence and a verification path.
- Confirmed vulnerability/history claim requires REPRODUCED or HISTORICAL evidence.
- HANDLED must expose the evidence supporting each material claim/decision without flattening materially different evidence states.
- CONFLICTS must include missing evidence.

## 9. Decide

For each stabilized issue, decide whether it requires FIX, DECOMPOSE, or CONFLICT; otherwise record why no action is required.

Consume the normative basis, evidence-qualified claims, unresolved dependencies, relevant structure/source-of-truth, and verification/reversibility directly; do not reconstruct an aggregate confidence or finding-level evidence status.

A material claim whose evidence is insufficient for the proposed decision cannot be silently promoted, strengthened, or repaired by stabilization wording; gather evidence, narrow the claim, DECOMPOSE, or CONFLICT as applicable.

Validate an apparent conflict before resolving it. Identify the alternatives claimed to be incompatible, the material value or protection each is meant to provide, and the assumptions and causal links supporting each side. Challenge whether the alternatives are truly incompatible, whether each causal case holds, and whether each claimed value is material. Test whether the apparent contradiction instead separates across different cases—such as time, target population, scale, phase, condition, environment, or other decision-relevant dimension. If any premise or causal link fails, or evidence differentiates the cases, recompute the issue and preserve the resulting conditional rule rather than a global conflict. Treat the trade-off as genuine only when incompatibility in the same relevant case and both material causal cases survive.

Before returning CONFLICT for materially competing valid alternatives or protections, test whether established evidence resolves the apparent conflict by narrowing an overbroad premise, claim, or applicability scope to what the bound task, governing norm, and established evidence support; establishing a real condition, threshold, or regime; identifying material dominance or irrelevance; or selecting a dominant rule with a bounded justified exception. Use only evidence-backed discriminators; do not invent distinctions, shrink the bound task or governing obligation, or force asymmetry. If alternatives remain genuinely nondominated or require an unresolved authority/value choice, retain CONFLICT. Once resolved, carry forward the resulting rule and any decision-relevant exception rather than preserving comparison machinery that cannot change the decision.

### FIX

Use when:
- the applicable normative basis: requirement, contract, design, policy, or Skeptic-owned rule
- the established current fact and evidence that conflict with that normative basis
- root cause, structure, required connections, and source of truth are clear or irrelevant
- unknowns are resolved or irrelevant
- change is reversible, testable, retryable
- risk is low/medium
- coverage, evidence, and verification path are adequate
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
- required coverage or evidence remains inadequate

Do not decompose pure conflict to avoid escalation.

### Promotion Check

Before marking anything ready, approved, or safe to proceed, check whether any ACTION, CONFLICT, or blocking unknown remains unresolved or any applicable required review has not been completed.

An unresolved DECOMPOSE path also blocks readiness or promotion until each resulting scope returns through GATE and reaches a valid outcome.

If yes, do not promote. Decide FIX, DECOMPOSE, or CONFLICT.

## 10. Act

Act only after DECIDE says FIX.

Process:
1. Preserve previous state.
2. Apply the smallest reversible change.
3. Verify immediately.
4. Revert immediately if verification fails.
5. Retry only when new evidence or a changed relevant condition makes the next attempt safer or more likely to succeed.
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

Before verification, set an explicit target number of material checks that directly exercise the intended result and material preserved constraints. Derive that number from consequence, dependency reach, irreversibility, uncertainty, trust elevation, claim strength, and materially plausible failure modes; do not use a universal quota. The count is a planning bound, not proof, and redundant checks do not satisfy it. If verification discovers a new or materially changed finding, dependency, constraint, failure mode, risk, or claim, reset the count to zero, re-derive the target from the new state, and continue against the updated scope; earlier evidence may inform the new plan but does not satisfy the reset count.

Check:
- red -> green for bug fixes when possible
- end-to-end trace from entry to output
- constraints: correctness, safety, performance, cost, context, maintainability
- pre-mortem: when risk warrants it, address materially plausible failure modes before action
- regression: previously working behavior still works
- known-bad/edge case when results are suspiciously clean

A test that was never red is weak evidence.

Verification is pass/fail.

If fail, preserve evidence, revert unsafe partial state, and retry only when new evidence or a changed relevant condition makes the next attempt safer or more informative; otherwise CONFLICT.

## 12. Learn

Escalate from local correction to systemic learning when:
- same fix category appears 3+ times
- same conflict appears 2+ times
- following a rule worsens outcomes
- expectation lacks a clear rationale, authority, or evidence basis
- local fixes repeatedly reveal same structure problem
- repeated misses show detection coverage failure
- repeated low-yield work, rote receipt completion, optional work becoming mandatory, stale-source substitution, ambiguous authority, or repeated local repairs suggest Skeptic's own design or realization may be part of the problem

Single-loop correction:
- implementation wrong -> fix and re-verify

Double-loop learning:
- rule, expectation, design, or detection method may be wrong -> route the question to its accountable owner or design-review method
- when the pattern concerns Skeptic itself, return it through the Skeptic design owner/design-review method rather than accumulating another local runtime rule
- unresolved governing meaning -> CONFLICT
- do not imply a separate DOUBLE-LOOP procedure unless one is explicitly defined

## 13. Output

Category layers:
- Finding/Razor categories: PASS, ACTION, CONFLICT.
- Final task outcomes: HANDLED, CONFLICT.

Every RunSkeptic task ends as HANDLED or CONFLICT.

### HANDLED

Use for verified fixes, completed decomposed steps, or low-risk logged issues.

HANDLED means the assigned Skeptic task or item was completed according to its permission and scope. It does not mean the reviewed artifact passed, is ready, or has no open issues.

A completed read-only review may be HANDLED while explicitly reporting unresolved findings. A completed decomposed step may be HANDLED while its parent DECOMPOSE path remains open. The Promotion Check still blocks readiness while any blocking item remains unresolved.

Each item includes:
- issue
- root cause
- action
- verification
- unresolved uncertainty/coverage, if any
- evidence supporting material claims/decision
- residual risk, if any

### CONFLICTS

Use for unresolved tradeoff, unclear owner/SoT/contract, non-reversible change, systemic rule issue, unresolved unknown, or inadequate required coverage/evidence.

Each item includes:
- issue
- thesis
- antithesis
- tradeoffs
- blocking unknowns
- missing evidence
- safe recommendation, if any
- decision needed

## 14. Razor - Bounded Read-Only Diagnostic

`Razor` is an alternative lightweight entrypoint, not a RunSkeptic stage and not a replacement for the complete recipe. It detects and classifies bounded concerns; it never changes files and never counts toward Find/Fix Loop convergence.

Bind:
- target and review boundary
- intended outcome or question
- available evidence and explicit unknowns
- explicitly requested or already-established domain lens, if any

Check compactly:
- avoidable failure, downside, incentives, weak safety margin, and effort-value mismatch
- unnecessary structure, false simplicity, speculation, and unexplained protected constraints
- mechanism gaps, stale claims, weak evidence, hidden limits, and trust-boundary transitions
- contradiction, falsifiability, silent invalidity, weak refutation, and overclaim
- unfair exceptions, hidden human burden, avoidable harm, moral conflict, and feasibility
- misplaced invariants, overconstraint, underconstraint, needed adaptive freedom, flexibility mechanisms, enabling constraints, and leakage across invariant/adaptive boundaries
- unresolved tradeoffs, fake middles, wrong leverage, and unproven dominance
- material dependencies, interfaces, source of truth, forward constraints, and staleness

An explicitly requested or already-established domain may assist Razor when its expected incremental detection value justifies the added cost. Use the domain only as a detection aid. It may contribute findings, unknowns, and evidence, but it does not own independent decisions or action. A material domain finding that could affect action, readiness, promotion, completeness, or a Skeptic-level conclusion returns to complete RunSkeptic. A clean domain-assisted Razor result does not establish full domain coverage or exhaustion. If a requested repository-owned domain lens is unavailable, report that coverage as UNKNOWN rather than treating the domain as clean.

Razor does not run the full Blind-Spot Challenge or require all full Thinker lenses. Instead report evidence, unknowns, skipped coverage, and whether complete RunSkeptic is required or recommended.

Output:
- `PASS` — no material issue detected by this bounded diagnostic; never means safe, ready, approved, complete, promotion-ready, domain-complete, or fully reviewed
- `ACTION` — material concern worth follow-up; never authorizes modification
- `CONFLICT` — unresolved ambiguity, authority issue, or blocker Razor cannot validly settle

Escalate to complete RunSkeptic or the accountable owner for:
- any requested modification
- readiness, promotion, completeness, or full-review claims
- any material domain finding
- consequential unresolved issue or significant authority conflict
- assurance needs beyond Razor's bounded evidence

`Expert Review` is a compatibility phrase for Razor with an explicitly scoped domain. It has no separate convergence, confidence, action, verification, or promotion pipeline.

## 15. Artifact Guide / External Questions

Use after Universal Questions and Structural Checks.

Patterns are detection aids, not exhaustive rules.

External reference:
- `skeptic-questions.md` is the lightweight domain registry; selected domain files contain expanded questions.
- Runtime core is authoritative.
- Registry and domain files expand detection only; they do not own independent process or decisions.

- Code: dead code, weak abstractions, bare except, magic values, string-built SQL/commands, no coverage, no timeout/retry/cleanup, silent wrong-input success.
- Tests: behavior vs implementation, shared state, order/OS dependence, test never red, critical regression gap.
- Config: dead fields, constants disguised as config, inconsistent names/types/units, stale paths/services, bad defaults, missing validation.
- Agent instructions: no why, over-broad rule, contradiction, stale tool/model behavior, suppresses errors, skips verification, causes inaction.
- Frameworks/workflows: for every material named mode, role, stage, procedure, control surface, or state, trace its entrypoint/caller, unique responsibility/current need, dependencies/consumers, and exit/return; flag unreachable or duplicate machinery while preserving any invariant it protects.
- Human docs: repeats code/help, missing prerequisites, untested steps, hidden assumptions, silent command failure.
- Design decisions: over-generalization, lock-in, hidden assumptions, unvalidated design, implicit dependency, no observability, single point of failure.
- Requirements: no user need, untestable, not revalidated, solution without problem, no acceptance criteria.

## 16. Tag Legend

Tags identify reasoning origin, not severity.

Thinker lenses:
- CH: Charlie Munger
- OM: Occam's Razor
- FE: Richard Feynman
- PO: Karl Popper
- KT: Immanuel Kant
- AJ: Alicia Juarrero; invariants, constraints, adaptation, and bounded adaptive freedom
- SH: Saffi; includes Follett-style integration-versus-compromise reasoning

Aspect tags are defined in §3:
- CH: `CH:IV`, `CH:IN`, `CH:SO`, `CH:MJ`, `CH:CP`, `CH:SM`, `CH:CR`, `CH:EV`, `CH:SR`
- OM: `OM:UE`, `OM:FS`, `OM:SS`, `OM:OD`, `OM:AC`, `OM:CF`
- FE: `FE:SC`, `FE:ME`, `FE:WY`, `FE:HL`, `FE:WE`, `FE:PG`, `FE:PV`, `FE:TB`
- PO: `PO:UF`, `PO:CO`, `PO:CN`, `PO:WR`, `PO:SI`, `PO:OC`, `PO:CG`
- KT: `KT:HU`, `KT:EX`, `KT:IR`, `KT:UA`, `KT:HB`, `KT:HHB`, `KT:NH`, `KT:MC`, `KT:OC`
- AJ: `AJ:IN`, `AJ:OC`, `AJ:UC`, `AJ:AF`, `AJ:EC`, `AJ:JB`, `AJ:RL`, `AJ:FL`
- SH: `SH:OF`, `SH:FM`, `SH:FB`, `SH:NE`, `SH:HC`, `SH:WL`, `SH:PF`
- `SH:PF`: Pareto frontier / proven dominance

Domain identifiers and applicability metadata are defined by `skeptic-questions.md`.
`SEC` is the Security domain identifier used in the notation examples below.

Notation:
- `CH` identifies a Thinker lens.
- `CH:IV` identifies one aspect.
- `SEC` identifies a domain.
- `CH:IV->SEC` means an aspect surfaced a domain issue.
- `FE:WE+PO:SI` means multiple aspects apply to one finding.

Use the smallest explanatory tag set, normally 1-3 tags. Use aspects when they improve traceability. Tags never replace evidence level, severity, or output category. Do not invent numbered QIDs unless the referenced question bank defines them.

## 17. Invariants

- Never act without DONE.
- Never act before stabilization.
- Never decide on raw findings.
- For Skeptic self-work, read the authoritative current `skeptic.md` when reviewing the repo version. When explicitly reviewing a candidate file, read that candidate file and state that it is not yet authoritative. Do not use memory, summaries, or generated variants as substitutes for the source under review.
- Do not claim RunSkeptic/Skeptic compliance if the source under review was unavailable or not applied exactly.
- Never skip a Thinker in RunSkeptic; mark NOT_APPLICABLE when it does not fit.
- Never treat no findings as proof of safety.
- Never treat clean orientation as proof of safety.
- Never FIX with unresolved material coverage or evidence gaps.
- Never report inferred risk as confirmed bug.
- Never ignore unresolved UNKNOWNs.
- Never remove without knowing what breaks.
- Never break a link without replacement or explicit coupling decision.
- Never execute unresolved conflict in the same area.
- Never accept silent failure.
- Never leave partial state.
- Never rely on hidden state.
- Never retry a failed action unless new evidence or a changed relevant condition justifies another attempt.
- Never confuse required convergence with retry; convergence may deliberately repeat unchanged complete review to establish stability.
- Never treat repeated local fixes as local forever.
- Every completed RunSkeptic task must have an outcome.
- Never mark an artifact ready while any ACTION, CONFLICT, or blocking unknown remains unresolved or any applicable required review has not been completed.
- An unresolved DECOMPOSE path likewise blocks readiness or promotion.
- Every RunSkeptic task ends as HANDLED or CONFLICT.
- Never modify outside the current task's scope; log adjacent issues separately.
- Never use Razor PASS as evidence of full review, readiness, approval, completeness, or promotion.
- Razor never modifies files or supplies qualifying Find/Fix Loop passes.

## One-Line Summary

RunSkeptic: Gate -> Orient -> Map -> Blind-Spot Challenge -> Stabilize -> Decide -> Act Safely -> Verify -> Learn

Razor: bounded read-only diagnostic -> PASS / ACTION / CONFLICT -> escalate when full assurance or action is required