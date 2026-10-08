# Skeptic

Purpose:
> Provide a self-contained operational RunSkeptic runtime with core Thinker semantics, optional domain detection, action/reality discipline, receipts, and loop entrypoints.

Visible runtime:

`BIND -> STATE(F/M/O/C) -> { INQUIRE | ATTACK }* -> DECIDE -> [ ACTION CONTRACT -> EXECUTE -> OBSERVE -> STATE ]`

No permanent COMPOSE, GUARD, RECONCILE, SELF, separate CLOSURE stage, compact-backstop stage, fixed replay count, or five-role bookkeeping.

---

# 0. Self-contained runtime and optional domain aids

This single `skeptic.md` defines the complete RunSkeptic core: process, STATE, the seven Thinker lenses and their aspects, family application, INQUIRE / ATTACK, integration, DECIDE, action/reality discipline, output, and loop/convergence semantics. Read this one file to run the method. Neither a private Hartal design file nor a separate Thinker or family-rule file is required.

Optional question and domain companion files can add specialized detection. They do not own the process, assurance, decisions, or action, and their availability does not define whether the core runtime can be used. If a particular selected domain file is unavailable, disclose the missing coverage and bound only conclusions that materially depend on it. Do not claim that an unexamined domain is clean.

---

# 1. Invocation contract

`RunSkeptic` is the formal invocation string for the complete Skeptic framework.

Aliases:
- `beskeptic`
- `apply Skeptic`
- `Skeptic review`
- `run skeptic.md`

`Razor` is the formal bounded read-only diagnostic entrypoint.

`Expert Review` remains a compatibility phrase for Razor with an explicitly scoped domain.

## Default assurance

- bare `RunSkeptic` => **COMPLETE assurance for the exact bound task**
- `Razor` => **BOUNDED read-only assurance**
- explicit user scope/assurance may narrow or strengthen only when it actually changes the bound task
- a narrower supported subclaim never silently replaces an unresolved stronger claim

## Permission

Default RunSkeptic permission:
- read-only

Recognized compatible permissions:
- `read-only`
- `patch-local`
- `fix-if-valid`

`patch-local` and `fix-if-valid` never authorize an edit by themselves.

Only DECIDE=FIX plus valid ACTION CONTRACT plus explicit permission may act.

## Fresh source binding

For every RunSkeptic invocation:

1. freshly read this exact runtime;
2. bind its path/ref/blob;
3. freshly bind the reviewed target/artifact/source;
4. load optional domain/question companions only when their relevance and availability justify it; expose missing decision-critical specialist coverage;
5. do not substitute memory, summaries, previous variants, or generated reconstructions.

Every repeated RunSkeptic run is a new source-freshness invocation.

## Formal invocation record

When deterministic binding is useful, record:

```text
INVOCATION_ID: <id>
INVOCATION_KIND: SINGLE | FIND_LOOP | FIX_LOOP | INNOSKEPTIC | INOSKEPTIC
PERMISSION_MODE: read-only | patch-local | fix-if-valid
ASSURANCE: COMPLETE | BOUNDED
DONE: <testable statement>
TARGET_TASK_REFERENCE: <interpretable task/scope>
REVIEWED_ARTIFACT_REFERENCE: <reference>
REVIEWED_ARTIFACT_SHA256: <when byte artifact exists>
SKEPTIC_RUNTIME_PATH: <this runtime path>
SKEPTIC_RUNTIME_BLOB_SHA: <blob>
DOMAIN_REGISTRY_BLOB_SHA: <if used; otherwise NONE>
APPLICABLE_DOMAIN_COMPANIONS: <list or NONE>
MATERIAL_FINDINGS: <list or NONE>
PREVIOUS_FINDINGS_REFERENCE: <reference or NONE>
```

These fields bind objects/context; they do not prove hidden cognition or provider/model routing.

---

# 2. RunSkeptic receipt

Every formal RunSkeptic report includes a compact receipt:

- Runtime source read: path/ref/blob
- Thinker lens definitions: included in the bound runtime
- Domain companions read, if any
- Permission mode
- Assurance
- DONE
- Major operations materially exercised
- Reasoning families applied / triggered
- Material evidence used
- ATTACK: due reason / result / skipped exemption basis
- DECIDE outcome
- Stop basis
- Action / observation / recovery, if any
- Unresolved O / conflicts / unknowns
- Final task category

Receipt is an index for challengeability, not independent proof.

Do not claim V5 RunSkeptic compliance without the current runtime and the evidence necessary for the exact claimed coverage.

---

# 3. Loop entrypoints

Loop names remain compatible.
Old fixed three-pass semantics do not.

## Artifact Relay

`artifact-relay` remains an optional bounded side-work/delegation aid for Find/Fix work when it is expected to reduce total context, repetition, cost, or failure risk after overhead.

It is **not** a separate assurance or decision pipeline.

One RunSkeptic/loop owner remains responsible for:
- fresh runtime/source binding;
- the bound task/DONE;
- COMPLETE assurance when required;
- integrating returned evidence into STATE;
- ATTACK/convergence obligations;
- DECIDE/action/reality ownership.

Delegated work returns only:
- bounded evidence/findings;
- scope;
- provenance;
- unknowns.

Delegated results:
- never inherit COMPLETE or DECIDE authority;
- never substitute for required fresh coverage;
- never count as independent convergence evidence merely because they came through another context;
- may reduce repeated reads only where their provenance/support remains valid.

Across lossy delegation boundaries, rebind mutable source/authority/freshness and reopen only dependent state.


## RunSkeptic Find Loop

Purpose:
> repeated fresh read-only review when additional independent/meaningfully varied review opportunity has expected detection value.

Each run:
- freshly binds runtime + exact current artifact;
- performs COMPLETE RunSkeptic;
- preserves material prior evidence/findings as state, not authority;
- re-evaluates changed/dependent state;
- does not modify the target.

Convergence:
- an explicit Find Loop must contain **at least one fresh review opportunity after the first run** unless execution becomes infeasible/unsafe or the caller explicitly requested a different count;
- this is invocation semantics, not proof of convergence;
- no universal total pass count;
- repeated correlated replay is weak evidence;
- after the minimum repeated opportunity, continue only while another fresh/varied review can materially reduce residual miss uncertainty;
- broad review/family resample is due when residual activation risk is broad/unlocalized, framing-sensitive, review stability itself matters, targeted ATTACK cannot represent the remaining miss space, or prior evidence shows activation sensitivity;
- stop when required coverage/ATTACK/resample obligations are satisfied and another materially different review has low expected decision value.

If the caller explicitly requests a run count:
- perform that many opportunities when feasible;
- the count is an execution request, not proof of convergence;
- a material change invalidates only dependent prior convergence credit.

Find Loop convergence means detection opportunity has become low-value enough for the requested assurance; it never converts UNKNOWN to evidence.

## RunSkeptic Fix Loop

Purpose:
> repeated authorized review -> action -> observation cycles.

Each cycle:
1. COMPLETE RunSkeptic;
2. DECIDE;
3. if FIX is authorized, bind ACTION CONTRACT;
4. revalidate mutable premises immediately before effect;
5. EXECUTE smallest materially equivalent mechanics;
6. OBSERVE authoritative resulting reality;
7. update STATE and reopen only dependent state.

A repair cycle is never itself proof of completion.

No universal qualifying-pass count.

Stop successfully only when:
- no required FIX remains;
- all decision-critical O for the bound DONE are closed/N/A or honestly terminal;
- required verification is supported;
- owed ATTACK/resample is satisfied;
- exact DONE can validly receive positive DECIDE.

Unknown action effect must be reconciled before unsafe retry/compensation.

## InnoSkeptic

Aliases:
- `Innovative Skeptic`
- `INNO Skeptic`
- `InoSkeptic`

Purpose:
> generate and compare materially distinct candidates without forcing a winner.

For each cycle:
- bind one goal + constraints;
- generate materially distinct candidates;
- when a candidate's size, coupling, complexity, unknowns, or prior failures materially lower its expected probability of reaching a completed useful outcome, consider a smaller-step alternative whose steps are independently verifiable and each advances the goal or resolves a decision-critical unknown; prefer it only when it improves expected useful progress without losing required end-to-end or integration semantics;
- for each mutation, state the new claim/protection, existing owner/evidence, and whether the mutation broadens meaning without evidence;
- run COMPLETE RunSkeptic on the candidate set using shared evidence;
- eliminate only defeated/dominated candidates;
- preserve unresolved nondominated alternatives;
- if candidate meaning/evidence materially changes, reopen only dependent state and re-run owed challenge.

Stop when:
- one defensible candidate dominates for the bound criteria; or
- a full cycle yields no material improvement or justified narrowing.

Do not force one winner where value/preference authority remains unresolved.

---

# 4. BIND

Bind only what can invalidate or constrain downstream work:

- target/task;
- exact DONE;
- authoritative source/artifact identity;
- material freshness;
- authority/permission;
- scope;
- assurance.

## BOUNDED

Own only the exact examined bounded claim.

No readiness/completeness/promotion implication.

## COMPLETE

Own all decision-critical coverage, closure, action/reality, and end-to-end obligations required by the stronger bound claim.

The bound target/scope/assurance/authority/DONE remain the DECIDE contract.

Change them only through authoritative rebinding.

A requested focus may prioritize attention but never silently narrow the bound task.

---

# 5. STATE

Maintain only decision-relevant live state.

STATE is not obligation-first.
F/M/O/C co-evolve while understanding improves.

## F — FACTS / OBSERVATIONS

Directly established.

Preserve material:
- source/provenance;
- scope;
- time/freshness;
- observation conditions.

Inference never becomes fact by repetition.

## M — MODEL / INFERENCES

Provisional:
- explanations;
- hypotheses;
- dependencies;
- causal structure;
- competing models.

Decision relevance can itself be inferential. If C uses a premise or observed property to change relative rank/selection among alternatives rather than merely establish qualification/exclusion, the relation that makes it decision-relevant is M unless the bound task/evidence directly supplies that relation.

For every decision-critical M preserve enough evidence semantics to know:
- what supports it;
- exact scope/condition support reaches;
- material uncertainty;
- what defeats/narrows it.

If C depends on M beyond its support:
- open exact evidence O;
- narrow C;
- or terminate honestly.

Correctly labelling an unsupported inference as "inference" is not permission to decide from it.

## O — OPEN ITEMS

Decision-relevant unresolved state, including:
- derived requirement/obligation;
- unanswered question;
- UNKNOWN;
- conflict;
- integration/reintegration;
- evidence/verification requirement;
- decision still owed.

Statuses:
- OPEN
- SUPPORTED
- NOT_APPLICABLE
- UNKNOWN/BLOCKED
- CONFLICT

A material O cannot disappear through wording or synthesis.

## C — CANDIDATE

Provisional:
- answer;
- judgment;
- action proposal.

Track materially:
- direct support;
- decision-critical M dependencies;
- for material comparison/ranking/selection, each discriminator actually capable of changing relative order/selection -- including one implicit in the candidate ordering/rationale -- and its direct support or M dependency;
- O dependencies;
- what defeats/narrows it.

A candidate may not borrow certainty from a stronger adjacent fact/model.

## Re-entry / reuse

Every material INQUIRE, ATTACK, OBSERVE, delegated return, or domain result updates STATE.

Reuse unaffected supported state.

Reopen only dependent state.

Known future materiality:
- keep a deferred O with activation condition + affected claim/action;
- on later invocation/continuation after activation, freshly rebind mutable source/authority/freshness;
- reopen only dependent state.

Autonomous future wake-up is not promised unless an external runtime explicitly supplies scheduling/monitoring.

---

# 6. Reasoning coverage

The complete CH/OM/FE/PO/KT/AJ/SH meanings and aspect tags are defined here.

## Thinker lenses

Use full name + abbreviation first; then abbreviation.

Each thinker is a lens, not a checklist. Inspect through the lens. Report only material findings that affect the bound RunSkeptic decision. Use aspect tags for traceability, for example `CH:IV` or `OM:FS`.

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

## Aspect annotations

Canonical aspect identifiers defined above (for example `FE:WE` and `PO:OC`) are the traceability names for material findings.

For every material finding derived from Thinker reasoning, include the applicable canonical aspect tag(s) in the report. Do not invent a Thinker tag for a domain/process finding that does not map to one. Tags annotate findings; they do not create new semantics, findings, or per-lens prose obligations.

## ALWAYS on every material decision

Apply complete:
- **CH** — risk/incentives/second-order/misjudgment/safety margin/constraints/scale
- **FE** — currentness/mechanism/why/limits/evidence/proof/value/trust boundaries
- **PO** — falsification/disconfirmation/contradiction/refutation/silent invalidation/overclaim/coverage
- **KT** — consistency/feasibility/fairness/human burden/harm/moral conflict

Do not first ask whether these four families are relevant.

Application does not require:
- a finding;
- a paragraph;
- equal tokens;
- visible receipt detail per lens.

Only supported/material/scoped/nonduplicate findings enter STATE.

## OM — conditional

Apply when the task materially chooses/adds/removes/simplifies/replaces/abstracts/evaluates/retains meaningful structure, process, machinery, or complexity.

Framework/design/process review => presumptively applicable.

When removing/replacing structure:
- distinguish protection from historical mechanism;
- existing realization is evidence, not authority;
- remove only when protection is preserved or validly unnecessary.

## AJ — conditional

Apply when correctness/decision quality materially depends on:
- constraints/invariants;
- interfaces;
- ownership/authority boundaries;
- degrees of freedom;
- adaptation;
- where flexibility begins/ends.

Architecture/policy/workflow/interface/control-system review => presumptively applicable.

If ALWAYS families expose a hidden material boundary/constraint/adaptation issue, trigger AJ.

## SH — conditional

Apply when:
- 2+ materially live alternatives/protections remain;
- a real trade-off/compromise/integration question exists;
- exception scope matters;
- leverage/dominance matters;
- accountable value/preference choice remains.

Preserve nondominated alternatives until evidence establishes dominance/conditional applicability or authority supplies the value judgment.

If ALWAYS families expose competing protections/options, trigger SH.

## DOMAIN — conditional

Apply specialist domain reasoning when:
- explicitly requested;
- inherently required by subject;
- or core reasoning establishes a material expertise gap.

When available, use the optional domain registry to select materially useful **repository-owned companion files**.

The registry is not an exhaustive ontology of specialist domains.
A task may materially require finance, insurance, law, medicine, travel/local, science, or other expertise even when no repository companion exists.

When specialist DOMAIN reasoning is required but no repository companion maps it:
- use available authoritative external sources/tools/expertise when the execution environment permits;
- otherwise keep the dependent coverage/claim UNKNOWN or appropriately bounded;
- never infer NOT_APPLICABLE merely from absence in the registry.

Missing selected repository companion coverage => skipped/UNKNOWN, never clean.

Domain reasoning contributes evidence/findings to STATE.
It never owns DECIDE/action.

## Fallback

If OM/AJ/SH/domain applicability cannot be reliably ruled out and missing it could materially change the decision:
> apply it.

Do not spend substantial reasoning proving non-applicability.

## FE:SC

`FE:SC` means **Feynman — Stale Claim**.

A materially time-dependent claim/action is unsupported unless current state is established by explicit context or sufficiently fresh authoritative evidence.

Never substitute model knowledge for current state.

---

# 7. Detection aids inside INQUIRE

These are aids, not mandatory stages.

## Universal questions

For every meaningful decision-relevant entity as useful:
- What is this?
- What is it for?
- What depends on it and what does it depend on?
- What must remain true?
- What breaks it?
- How do we know it works?
- Does it solve a current verified need or speculate?

## Structural checks

When structure is material, inspect:
- role/ownership;
- boundaries/concern split;
- interfaces/required/forbidden/implicit links/contracts;
- necessary vs accidental coupling;
- source of truth/competing copies;
- data/control flow/update timing/consumers;
- reversibility/retry/failure signal.

Do not force this checklist on trivial non-structural work.

---

# 8. INQUIRE

Resolve the highest-value open item. For discretionary inquiry, expected decision value means ability to change DECIDE, discriminate materially live M, or resolve shared dependencies relative to cost and risk. Required safety, authority, coverage, evidence, verification, and ATTACK/resample obligations override this ordering; do not invent numerical precision.

When an established F materially conflicts with a decision-relevant M or expectation and explaining why could change DECIDE, open an explanatory O; form plausible competing M as needed and prefer safe, proportionate evidence that discriminates them. Surprise is not proof of a cause. Do not proliferate explanations when authoritative evidence already adequately explains the mismatch or when resolving the cause cannot materially affect DECIDE.

INQUIRE may:
- orient/reframe;
- establish source of truth/ownership/path;
- investigate evidence;
- apply required families/domain knowledge;
- update models;
- compare alternatives;
- trace causality;
- resolve factual conflicts;
- establish end-to-end feasibility;
- integrate interacting findings;
- prepare action/verification obligations.

Optional investigation continues only while plausible new evidence/reasoning can materially change the affected disposition enough to justify cost.

This economy rule never overrides required:
- coverage;
- verification;
- evidence;
- ATTACK/resample;
- action safety.

Multiple viable candidates:
- preserve nondominated alternatives;
- narrow only with evidence/governing constraints/accountable authority.

---

# 9. Integration obligation

Create exact integration O whenever material findings/actions:
- interact;
- share plausible mechanism/root cause/dependency;
- cross a boundary that can change disposition;
- remedies collide/duplicate/mask;
- local fix moves risk;
- decomposed child results require reintegration;
- separately correct components can fail jointly.

INQUIRE owns the semantic answer.

Integration/synthesis may itself create:
- new M;
- new claim;
- new action requirement;
- new evidence/verification O.

New synthesized meaning does not inherit proof from supported components.

Unless directly established:
- synthesized relation/root cause remains M;
- if C depends on it, exact missing evidence O remains.

Preserve every material distinction that can change disposition:
- scope;
- evidence;
- condition;
- authority;
- dependency;
- uncertainty;
- reversibility;
- consequence.

Merge only true duplicates.

DECIDE may not bypass a material integration/evidence O.

---

# 10. ATTACK

ATTACK is separate from INQUIRE.

Purpose:
> search outside represented rationale and challenge whether the reasoning process itself is creating the blind spot.

Ask materially:
- what plausible countermodel defeats C?
- what hidden dependency/common mode defeats several supports?
- what actor/path/side effect/failure mode/verification condition is absent while C looks coherent?
- what evidence is stale/unrepresentative/correlated/non-discriminating?
- what protected human/system consequence lies outside the frame?
- could STATE representation, lens/routing choice, reasoning method, or stopping assumption itself be narrowing attention, causing FN/FP, or creating avoidable burden?

ATTACK must seek materially different failure space.
Paraphrase/replay earns no fresh credit.

## ATTACK owedness

ATTACK is owed before positive DECIDE when any are true:
- assurance is COMPLETE unless exact claim is genuinely EXHAUSTED by finite/deterministic authoritative coverage with no material hidden transformation/dependency/alternate source/side effect/unobserved path;
- C claims readiness/promotion/end-to-end completion;
- C proposes material-risk/irreversible/external-effect/mutable-premise action;
- consequence or residual uncertainty/stochastic miss risk is material;
- shared-assumption/common-mode/process-blindness remains plausible;
- result is suspiciously clean relative to complexity/consequence/evidence;
- OBSERVE/reality contradicts prior expectation in a way that could implicate model/method;
- prior misses/repeated burden implicate routing/reasoning/stopping;
- material STATE/model/evidence change changed or could materially change residual failure family/shared assumption/common dependency/support basis for prior ATTACK.

## Changed-failure-space reactivation

When reactivated:
- reset only dependent ATTACK/stop credit;
- preserve unaffected evidence/reasoning/state;
- do not replay merely because any state changed;
- re-ATTACK only materially changed residual failure space.

## Low-risk BOUNDED exemption

Low-risk BOUNDED work may skip ATTACK only when all are true:
- C is limited to exact bounded content actually examined;
- C is supported by direct authoritative observation/evidence or deterministic derivation;
- no decision-critical provisional M, unobserved mechanism/path, hidden transformation, or unresolved dependency supports C;
- exact-bound required reasoning coverage is complete;
- no readiness/completeness implication;
- no material action consequence.

If uncertain whether materially different unrepresented semantic space could change C:
> ATTACK is owed.

A process-self finding enters normal O.
Do not recursively ATTACK ATTACK without new material evidence.

---

# 11. Stochastic / broad resample

Targeted ATTACK is default convergence tool.

Broader whole-review/family resample is due when:
- residual activation risk is broad/unlocalized;
- strong claim depends on review stability;
- materially different wording/context can plausibly expose hidden activation failure;
- targeted ATTACK cannot cheaply represent remaining miss space;
- prior evidence shows this class is stochastic/activation-sensitive.

Rules:
- no universal count;
- correlated replay is weak evidence;
- independent/meaningfully varied challenge preferred;
- replay counts only for uncertainty it can actually reduce.

---

# 12. DECOMPOSE / reintegrate

DECIDE may DECOMPOSE when:
- scope/risk too large;
- independent testable responsibilities can separate;
- decomposition reduces uncertainty/risk without hiding governing conflict.

Create persistent parent O with:
- child questions/scopes;
- required evidence returns;
- shared assumptions/dependencies children may not independently close;
- reintegration rule;
- remaining parent DONE.

Child completion never closes parent automatically.

Returned child evidence:
- updates STATE;
- reopens dependent M/O/C;
- triggers integration O;
- owes fresh ATTACK only when residual failure space/prior ATTACK support changed.

Parent DECIDE owns terminal outcome.

---

# 13. DECIDE

DECIDE is the only normative disposition owner.

Internal outcomes:
- ANSWER / NO ACTION
- FIX
- DECOMPOSE
- CONFLICT
- BLOCKED / UNKNOWN

DECIDE performs no semantic reasoning.

Before positive ANSWER / NO ACTION / FIX-readiness, perform one STATE sufficiency check:

1. **Contract lock**
   - bound target/scope/assurance/authority/DONE unchanged or authoritatively rebound.

2. **Open items**
   - every decision-critical O SUPPORTED or legitimately NOT_APPLICABLE.

3. **Claim/model evidence integrity**
   - C coherent with F/M;
   - no material inference presented as fact;
   - every decision-critical M used by C supported strongly enough for exact claim/action/assurance or limitation explicit in O/C;
   - evidence for one fact/model/scope does not automatically support another or synthesized relation;
   - time-dependent support current enough.

4. **Reasoning coverage**
   - CH/FE/PO/KT applied;
   - triggered OM/AJ/SH/domain applied or legitimately N/A.

5. **Integration**
   - material integration/reintegration O closed.

6. **End-to-end ownership**
   - for terminal/readiness/completeness claims: dependencies, handoffs, resources, ownership, integration, verification path feasible or explicitly unresolved.

7. **Stop basis**
   - exact bound claim has valid positive stop basis;
   - owed ATTACK/resample satisfied.

8. **Action readiness**
   - FIX authority valid;
   - mutable action-critical premises current enough to authorize action path;
   - ACTION CONTRACT will revalidate immediately before effect.

Predicate failure:
- create/open exact O;
- return to INQUIRE/ATTACK;
- never hide reasoning inside DECIDE.

## Positive stop bases

### BOUNDED-SUPPORTED

Only when:
- exact bound is BOUNDED/non-exhaustive;
- decision-critical O resolved/bounded;
- no ATTACK owed under runtime rule.

Never closes an unresolved COMPLETE claim.

### EXHAUSTED

When:
- exact claim finite/deterministic;
- authoritative evidence completely covers it;
- no material hidden transformation/dependency/alternate source/side effect/unobserved path remains;
- no separate residual ATTACK obligation remains.

### ATTACK-SATISFIED

When:
- ATTACK was owed;
- after last dependent semantic/failure-space change, credible fresh ATTACK occurred;
- no unresolved material delta remains;
- another materially different challenge has low expected decision value;
- due broad resample is satisfied.

Cross-cutting:
- only dependent stop credit resets;
- stronger evidence alone does not reset stop credit when semantic/failure basis unchanged;
- UNKNOWN never becomes positive through repetition;
- no fixed pass count;
- never repeat merely until clean.

## Honest terminality

BLOCKED / UNKNOWN / CONFLICT may terminate without positive stop basis when:
- unresolved basis explicit in O;
- effect on bound claim explicit;
- no justified available reasoning can resolve it;
- no unsafe readiness/action implied.

---

# 14. ACTION CONTRACT

Only DECIDE=FIX may act.

Bind:
- exact authorized effect;
- scope;
- constraints;
- mutable premises through effect horizon;
- reversibility/irreversibility;
- blast radius;
- evidence to preserve before destructive change;
- verification;
- recovery;
- retry/idempotency.

Immediately before EXECUTE:
- recheck mutable premise whose change would alter authorization/target/scope/safety/expected effect;
- if changed materially, do not act from stale authorization;
- update STATE and return to DECIDE.

DECIDE authorizes meaning.
Execution may not broaden it.

---

# 15. EXECUTE

Choose smallest materially equivalent mechanics inside ACTION CONTRACT.

If mechanics alter:
- meaning;
- scope;
- risk;
- dependency;
- tradeoff;
- authority;

return to STATE/DECIDE.

Preserve required invariants across observable intermediate states.

Preflight scarce/one-shot evidence-producing actions proportionately.

---

# 16. OBSERVE / REALITY

After action:
- observe authoritative resulting reality;
- command/ack success is not outcome proof;
- verification depth follows claim/risk/failure model;
- evidence must represent the claim;
- common-mode checks do not count as independent;
- use never-red/known-bad discrimination when materially relevant.

Unknown effect:
- reconcile before unsafe retry/compensation unless established idempotency/authorized retry safely covers it.

Recovery:
- is a new action;
- restoration must itself be observed.

Feed resulting evidence into STATE.
Reopen only dependent state.

If new evidence changes residual failure space:
- re-ATTACK only affected space.

---

# 17. Systemic learning / A39 process-self correction

Material evidence may open O that governing design/policy/rule/reasoning method itself is wrong when:
- one sufficiently discriminating observed result directly contradicts a process-generated expectation in a way that could implicate method;
- a routing/stopping/rule choice worsens outcome or causes material miss;
- repeated/systemic failures, recurring local fixes, repeated misses, or repeated low-yield burden support concern.

INQUIRE/ATTACK may investigate shared cause.

One observation is not automatic causal proof.
Recurrence is not governing authority.

If process/method O materially undermines current review coverage/evidence/routing/stop basis:
- invalidate affected current positive credit;
- compensate within existing authority;
- narrow conclusion;
- or terminate BLOCKED/UNKNOWN/CONFLICT.

Supported learning may:
- open outer design/policy/method O;
- support proposed change;
- trigger accountable design review.

It may not:
- silently rewrite governing rules;
- self-authorize successor architecture/promotion;
- treat recurrence or surprise as authority.

Skeptic may review its own method as target.
Successor-rule adoption routes outward to accountable design owner.

No recursive SELF procedure without new material evidence.

---

# 18. Delegation / lossy context

Delegated work returns:
- bounded evidence/findings;
- scope;
- provenance;
- unknowns.

Delegation never inherits COMPLETE or DECIDE authority.

Across real lossy boundary:
- persist only decision-critical STATE;
- preserve provenance/evidence references;
- rebind mutable authority/source/freshness on continuation;
- revalidate only dependent conclusions.

Persisted state is memory/index, not source of truth.

---

# 19. Output compatibility

## Finding categories

For material findings:
- `PASS` — bounded finding/check supported; never implies global readiness unless bound claim itself earns it
- `ACTION` — material issue warrants follow-up/fix/review; does not itself authorize modification
- `CONFLICT` — unresolved blocker/tradeoff/authority/UNKNOWN that prevents the dependent stronger claim

## Final task categories

Every formal RunSkeptic task ends:
- `HANDLED`
- or `CONFLICT`

### HANDLED

The assigned Skeptic task was completed within permission/scope.

HANDLED may contain:
- no-action answer;
- bounded supported answer;
- read-only ACTION findings;
- verified FIX;
- completed child DECOMPOSE work.

HANDLED does not automatically mean reviewed artifact is ready/clean/promotion-ready.

### CONFLICT

Use when the requested Skeptic task itself cannot be validly completed because unresolved conflict/authority/blocking UNKNOWN/required coverage prevents the bound outcome.

## User-facing result

Give useful result first.

Expose canonical aspect annotations for every material Thinker finding.

Expose only material:
- scope/assurance limitation;
- consequential finding/support;
- UNKNOWN/CONFLICT/blocker;
- material skipped required coverage;
- action + observed verification/recovery;
- stop basis when relevant.

Do not dump:
- full STATE;
- lens checklist;
- internal DECIDE predicates;
- internal accounting

unless needed for challengeability or explicitly requested.

---

# 20. Razor — bounded read-only diagnostic

Razor is a lightweight alternative entrypoint, not a RunSkeptic stage.

Bind:
- exact bounded target/question;
- available evidence/currentness;
- explicit unknowns;
- selected domain, if explicitly requested/obvious.

Razor:
- is always read-only;
- uses proportionate CH/FE/PO/KT reasoning and directly relevant conditional families;
- does not owe full RunSkeptic ATTACK/convergence machinery;
- never establishes readiness/promotion/completeness beyond its exact bound.

Output:
- PASS
- ACTION
- CONFLICT

Escalate to RunSkeptic for:
- requested modification;
- readiness/promotion/completeness;
- material domain finding needing stronger assurance;
- consequential unresolved issue/authority conflict;
- assurance beyond bounded diagnostic.

Expert Review = Razor + explicit domain.

---

# 21. Artifact/domain aids

Artifact patterns/question banks are detection aids, not exhaustive rules.

Optional domain-question registry: `skeptic-questions.md` (when available). Its domain files are optional detection aids; a missing selected file limits only claims dependent on that coverage.

Load only selected domain files when available and material to the task.

Do not let companion files override this runtime.

Useful artifact prompts include:
- code: behavior, errors, timeout/retry/cleanup, wrong-input success;
- tests: behavior vs implementation, shared state/order dependence, never-red, regression gaps;
- config: stale fields/defaults/paths, type/unit/name inconsistency, missing validation;
- workflows: entrypoint, unique responsibility, dependencies/consumers, exit/return, duplicate/unreachable machinery;
- docs: prerequisites, hidden assumptions, untested/silent-failure steps;
- design: lock-in, hidden assumptions, implicit dependencies, observability, single-point failure;
- requirements: user need, testability, revalidation, acceptance criteria.

---

# 22. Invariants

- Never act without bound DONE and authority.
- Never act from unresolved decision-critical O.
- Never decide from a model beyond its support.
- Never present inference as fact.
- Never use stale current-state assumptions for time-dependent claims/actions.
- Never silently narrow COMPLETE to BOUNDED.
- Never use a clean result as proof of missing coverage.
- Never skip OM/AJ/SH/domain when its condition is materially present or cannot safely be ruled out.
- Never reuse ATTACK credit after the dependent residual failure space/support basis materially changed.
- Never replay ATTACK merely because any state changed.
- Never use the low-risk BOUNDED exemption when C depends on provisional M/unobserved mechanism/hidden transformation/unresolved dependency.
- Never treat synthesis as inheriting component proof.
- Never close parent DONE from child success without reintegration.
- Never act from stale mutable premises.
- Never treat transport/ack failure as proof that a remote effect did not occur.
- Never unsafe-retry an ambiguous non-idempotent effect before reconciliation.
- Recovery is a new action and restoration must be observed.
- Never treat repeated pattern as governing authority.
- Never self-adopt a successor Skeptic rule.
- Never manufacture findings to justify process.
- Never use a fixed replay count as proof of convergence.
- Every formal task ends HANDLED or CONFLICT.
- This public runtime carries no authority to mutate or promote itself.

---

# One-line summary

RunSkeptic V5:
> **Bind -> maintain live truth/model/open-state -> inquire -> attack what represented reasoning may have missed -> decide only from supported state -> act under contract -> observe reality -> reopen only what reality changed.**
