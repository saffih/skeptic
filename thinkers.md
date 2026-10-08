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
- `FE:TB` trust-boundary transition: untrusted, lower-authority, or unverified content, output, or state is accepted -- or is structurally permitted to flow -- into a higher-trust or control-bearing role without an explicit validation or authorization step proportionate to the consequence; or an actor is granted control-bearing capability, privileged access, broader source access, or external-effect authority that materially widens its established trust/control role without evidence that the capability belongs there and without proportionate authorization and containment

Higher-trust or control-bearing roles include: instruction, permission, verified evidence, source of truth, executable input, policy, configuration, safety or control signal.

For every `FE:TB` finding, identify the direction of the transition (information/state promoted into a higher-trust role or an actor's privilege/authority materially widened), the source/actor, the promoted role/capability, the boundary crossed, and the missing or insufficient validation, authorization, containment, or placement rationale. If unblocking one capability repeatedly requires materially independent privilege increases, treat that pattern as evidence to test capability placement before further widening; it is not itself proof of misplacement.

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
