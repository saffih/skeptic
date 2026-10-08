# W3 Lens Application — Simple Family Rule — 2026-09-24

Status: **PREFERRED EXPERIMENTAL LENS-APPLICATION CANDIDATE / W3 CORE UNCHANGED / NO PUBLIC RUNTIME AUTHORITY**

Derived from:
- RunSkeptic always-vs-conditional review
- InnoSkeptic partition search

## Core rule

For every **material decision**:

### ALWAYS APPLY
- **CH — Charlie Munger / risk**
- **FE — Feynman / reality & evidence**
- **PO — Popper / falsification & completeness**
- **KT — Kant / consistency, feasibility, human impact & morality**

Do not first ask whether these families are relevant.

They are broad, cross-domain, and contain self-concealing failure modes that can be missed if applicability is decided before the reasoning is applied.

### CONDITIONALLY APPLY
- **OM — Occam**
- **AJ — Juarrero**
- **SH — Saffi**
- **Domain lenses**

Conditionality is allowed only because their activation conditions are external and directly recognizable.

---

# 1. CH — ALWAYS

Apply all CH lenses:
- CH:IV
- CH:IN
- CH:SO
- CH:MJ
- CH:CP
- CH:SM
- CH:CR
- CH:EV
- CH:SR

Why always:
- risk, incentives, second-order effects, misjudgment, competence gaps, safety margin, effort/constraint targeting, and scale effects may be absent from the current framing;
- deciding whether CH is relevant can itself miss the reason CH matters.

No finding is required.
Most lenses may resolve immediately as not material.

---

# 2. FE — ALWAYS

Apply all FE lenses:
- FE:SC
- FE:ME
- FE:WY
- FE:HL
- FE:WE
- FE:PG
- FE:PV
- FE:TB

Why always:
- reality/evidence is foundational;
- hidden limits, stale assumptions, mechanism gaps, and trust transitions can be self-concealing;
- almost every material decision depends on whether the evidence and explanation fit reality.

No finding is required.

---

# 3. PO — ALWAYS

Apply all PO lenses:
- PO:UF
- PO:CO
- PO:CN
- PO:WR
- PO:SI
- PO:OC
- PO:CG

Why always:
- every material conclusion should survive a serious attempt to show it wrong;
- missing obligations, silent invalidation, confirmation-only proof, and overclaim can remain invisible unless explicitly challenged.

No finding is required.

---

# 4. KT — ALWAYS

Apply all KT lenses:
- KT:HU
- KT:EX
- KT:IR
- KT:UA
- KT:HB
- KT:HHB
- KT:NH
- KT:MC
- KT:OC

Why always:
- human burden, fairness, feasibility, avoidable harm, and moral conflict can be hidden by a technical/operational frame;
- the user explicitly weights moral false negatives heavily;
- the cost of briefly applying the family is lower than building another human-impact selector.

No moral finding is required.
Ordinary downside is not automatically moral harm.

---

# 5. OM — CONDITIONAL

Apply OM when:

> **We are choosing, adding, removing, simplifying, replacing, abstracting, or retaining meaningful structure, process, machinery, or complexity.**

This condition is directly observable from the task/action.
OM is not needed to discover that such a structural/process choice exists.

Apply all OM lenses once triggered:
- OM:UE
- OM:FS
- OM:SS
- OM:OD
- OM:AC
- OM:CF

Examples:
- refactor;
- remove a stage;
- add a service;
- simplify a workflow;
- introduce an abstraction;
- decide whether machinery is necessary.

Do not apply OM merely because an artifact exists.

---

# 6. AJ — CONDITIONAL

Apply AJ when:

> **The decision materially concerns what must remain fixed, what may vary, constraints, invariants, interfaces, ownership boundaries, degrees of freedom, adaptation, or where flexibility starts/stops.**

This is a property of the target/action and can normally be recognized before AJ reasoning.

Apply all AJ lenses once triggered:
- AJ:IN
- AJ:OC
- AJ:UC
- AJ:AF
- AJ:EC
- AJ:JB
- AJ:RL
- AJ:FL

Examples:
- architecture boundaries;
- policy constraints;
- interface contracts;
- authority boundaries;
- adaptive workflows;
- invariant vs configurable behavior.

Re-entry rule:
- if ALWAYS families reveal a previously hidden material boundary/constraint/adaptation issue, trigger AJ then.

---

# 7. SH — CONDITIONAL

Apply SH when:

> **Two or more materially live alternatives/protections remain, or there is a real compromise, exception, dominance, leverage, or accountable value-choice question.**

This condition is visible from the live candidate/obligation state.

Apply all SH lenses once triggered:
- SH:OF
- SH:FM
- SH:FB
- SH:NE
- SH:HC
- SH:WL
- SH:PF

Examples:
- two valid architectures remain;
- safety conflicts with flexibility;
- one rule needs a narrow exception;
- compromise may preserve both costs;
- one option may dominate another.

If there is no real trade-off or live alternative set, do not apply SH.

Re-entry rule:
- if ALWAYS families expose competing material protections/options, trigger SH then.

---

# 8. DOMAIN — CONDITIONAL

Apply specialized domain lenses when:

> **Correct reasoning materially depends on specialized subject-matter facts, rules, failure modes, or expertise beyond the general families.**

Trigger is satisfied when:
- the user explicitly requests the domain;
- the subject inherently requires specialist knowledge;
- or ALWAYS families establish a material expertise gap.

Examples:
- security;
- finance/options;
- medicine;
- law;
- database/concurrency;
- accessibility;
- specialized engineering.

Domain lenses add detection/evidence only.
They do not own COMMIT or action.

---

# 9. Fallback rule

For OM, AJ, SH, or a domain lens:

> **If the condition cannot be reliably ruled out and missing the family could materially change the decision, apply the family.**

This is the safety fallback.

Do not spend substantial reasoning proving that a family is unnecessary.
When exclusion itself becomes difficult, application is cheaper and safer.

---

# 10. Finding discipline

Application != finding.

A lens may be applied and return nothing material.

A finding enters W3 BOARD only when:
- supported by evidence appropriate to its claim;
- material to the decision;
- scoped correctly;
- not a duplicate restatement.

This is the main false-positive control.

---

# 11. Exact application summary

```
EVERY MATERIAL DECISION
    |
    +-- CH  ALWAYS
    +-- FE  ALWAYS
    +-- PO  ALWAYS
    +-- KT  ALWAYS
    |
    +-- OM  if structure/process/machinery is being chosen or changed
    +-- AJ  if constraints/invariants/interfaces/adaptation are material
    +-- SH  if real live alternatives/trade-offs exist
    +-- DOMAIN if specialist expertise is materially needed
    |
    +-- if unsure whether a conditional family is needed
        and the miss could matter -> APPLY IT
```

No Scout.
No scoring.
No per-lens applicability decisions.
No mandatory findings.
No family receipt by default.

---

# 12. Why this rule is preferred

It is simpler than:
- all 54 always;
- per-lens conditional routing;
- Scout-Focus;
- five-role traversal.

It is safer than:
- five-lens always core;
- pure selective routing.

It directly implements:
> conditional only when the condition is independently recognizable and well justified; otherwise always.

No W3 core mutation.
No public promotion.
