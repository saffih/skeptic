# Skeptic Next-Capability: SH:PF Priority and Promotion Contract

Status: FROZEN before candidate implementation or scenario execution
Base: `e5494db30a7d4873db4f567de9cd073b90a62edb`
Branch: `candidate/skeptic-next-capability-20260718`
Decision owner: Lead Agent under the user-authorized Task Prompt

This is the durable decision artifact for one production slice. It is not runtime instruction. `skeptic.md` remains authoritative after publication.

## Bounded Priority Scan

Scoring uses current repository evidence only. Each criterion is `0` (unfavorable) to `3` (favorable): decision improvement, unique value, failure frequency/severity, testability, build simplicity, low duplication/ceremony risk, minority/long-tail safety, and probability of remote-main DONE. Equal weights keep the scan decision-oriented; a high total cannot override a material safety or duplication objection.

| Rank | Candidate | Improve | Unique | Failure | Test | Simple | Distinct | Minority | DONE | Total | Current evidence and decision |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | SH:PF Pareto frontier/dominance | 3 | 3 | 3 | 3 | 2 | 2 | 2 | 3 | 21 | Current SH detects opposing forces, fake/forced middles, exceptions, hidden conflicts, and wrong leverage, but defines no option-set frontier, dominance predicate, or `DOMINANCE_UNPROVEN` guard. Select the bounded predicate plus preservation guards. |
| 2 | CH:CR versus SH:WL clarification | 2 | 1 | 2 | 2 | 3 | 2 | 2 | 3 | 17 | The current descriptions overlap, but CH:CR already targets the system constraint while SH:WL targets leverage within a trade-off. Clarification is useful but mostly taxonomic. |
| 3 | Non-maleficence and minority-harm protection | 3 | 2 | 3 | 1 | 1 | 1 | 3 | 2 | Harm deserves stronger coverage, but CH inversion/second-order damage, KT universalization/asymmetry, and SH narrow exceptions already cover much of it. A general doctrine would be broader and harder to falsify in one run. SH:PF can add a narrow executable minority guard now. |
| 4 | Clearer Thinker headings and questions | 1 | 1 | 1 | 3 | 3 | 2 | 2 | 3 | Highly finishable and testable for readability, but changes comprehension more than decision behavior. |
| 5 | Balanced Occam language | 2 | 0 | 2 | 2 | 3 | 0 | 2 | 3 | Already explicit: OM preserves proof, protection, responsibility, reversibility, and safety; OM:FS and OM:CF cover false deletion while OM:UE covers false preservation. More wording risks duplication. |
| 6 | Kant persons-as-ends / hidden-burden strengthening | 2 | 1 | 2 | 1 | 2 | 1 | 3 | 2 | KT:HB, KT:UA, and KT:HU already expose shifted burdens and unfair patterns. Persons-as-ends could help, but an operational boundary and oracle need more design. |
| 7 | Concise human-readable glossary | 1 | 1 | 1 | 3 | 2 | 1 | 2 | 3 | Useful for onboarding, but duplicates the tag legend and is unlikely to change high-stakes decisions. |
| 8 | Popper terminology clarification | 1 | 0 | 1 | 2 | 3 | 1 | 2 | 3 | Current PO terms have operational definitions and report conditions; remaining value is mainly wording polish. |
| 9 | FE:PV placement or split | 1 | 1 | 1 | 2 | 2 | 1 | 2 | 3 | FE:PV is clearly defined as a purpose/value gap. Moving or splitting it has uncertain behavioral value and risks taxonomy churn. |
| 10 | Full Priority Scan capability | 3 | 1 | 2 | 1 | 0 | 0 | 2 | 1 | Priority is partly covered by CH:EV, CH:CR, FE:PV, SH:HC/SH:WL, the Task Prompt useful-slice check, and completion feasibility. A full scan would be large, ceremonial, and unlikely to reach behavioral remote-main DONE in this slice. |

### Selection

Select `SH:PF` as a narrow Saffi-lens extension: a strict, uncertainty-aware Pareto dominance predicate that may remove only proven dominated options and otherwise preserves the frontier or defers to existing Skeptic.

Unique behavioral delta from current main:

- Current `SH:FB` can say one side should dominate a forced balance, but it neither compares every live option across every protected dimension nor defines when elimination is justified.
- `SH:OF`, `SH:FM`, `SH:NE`, `SH:HC`, and `SH:WL` expose trade-offs, exceptions, ownership decisions, and leverage; none produces a frontier/dominated set.
- CH, FE, and PO can challenge evidence, causal stories, and silent passes; none connects those checks to a dominance decision with a fail-closed preservation result.
- The selected slice adds one new action: eliminate an option only after strict dominance is proven. All unresolved evidence, value, aggregation, tractability, minority, tail, and option-value cases remain live and route through existing Skeptic.

The earlier SH:PF experiment is not selection evidence because its decision-critical artifacts were unavailable. This contract starts from current tracked sources and fresh same-run checks.

## Frozen Promotion Contract

This section is frozen before the executable test module is created. Candidate results must not change its scenarios, expected decisions, or thresholds. If the contract itself is shown wrong, invalidate the run, record why, and restart the priority/contract phase before evaluating a replacement.

### Behavioral hypothesis

Adding `SH:PF` will reliably eliminate genuinely dominated options that current Skeptic leaves as an undifferentiated trade-off, while never eliminating an option when the apparent dominance depends on stale or uncertain evidence, unsupported causation, weighted aggregation, grouping, unmodeled tractability, minority harm, a long-tail benefit, reversibility/information value, or strategic option value.

### Runtime decision procedure to implement

1. `SH:PF` is applicable only to a decision with at least two live options and an explicit comparison objective. Otherwise return `NOT_APPLICABLE` and add no process.
2. Existing authority, source-of-truth, safety, or ownership blockers run first. When they already decide or block the case, return `DEFER_EXISTING`; SH:PF must not duplicate or override them.
3. Compare options on disaggregated, decision-relevant dimensions with the same direction, scope, time horizon, evidence standard, and tractability assumptions. Include hard constraints and protected minority/subgroup outcomes.
4. Evidence must be current enough for the decision. Represent material uncertainty as intervals. A causal outcome may be used only when its causal claim has adequate support; correlation alone cannot prove it.
5. Option A safely weakly exceeds B on a dimension only when A's lower credible bound is at least B's upper credible bound. A is strictly better on a dimension only when A's lower bound is greater than B's upper bound.
6. A dominates B only when A safely weakly exceeds B on every protected dimension and is strictly better on at least one. Weighted totals, averages, or grouped outcomes cannot substitute for the all-dimensions predicate.
7. Before elimination, verify that B has no distinct minority benefit, long-tail value, uncertainty-sensitive upside, reversibility/information value, strategic option value, narrow exception, or legitimate stakeholder weighting that is missing from the dimensions.
8. If the comparison basis or any elimination guard is unresolved, return `DOMINANCE_UNPROVEN`, preserve the option, and route the issue to existing evidence, trade-off, exception, or CONFLICT handling.
9. If the basis and guards are adequate but no option dominates another, return `PRESERVE_FRONTIER` and keep every non-dominated option. Equal options are not Pareto-dominated; OM may separately test whether duplication is unnecessary.
10. Only a proven dominated option returns `ELIMINATE_DOMINATED`. Report the dominating option, dominated option, dimensions, evidence/uncertainty basis, and preservation guards checked.

### Executable scenario set and frozen oracle

| ID | Required concern | Baseline/current behavior | Frozen SH:PF decision | Essential disconfirming fact |
|---|---|---|---|---|
| PF01 | Material change: cost/speed | Generic trade-off review; no frontier rule | `ELIMINATE_DOMINATED` | A is safely no worse on all dimensions and strictly better on cost and speed. |
| PF02 | Material change: reliability/tractability | Generic force/leverage review | `ELIMINATE_DOMINATED` | A is safely better on reliability and implementation effort with equal protected outcomes. |
| PF03 | Existing Skeptic sufficient: source-of-truth conflict | Existing Gate/Fundamental Scan blocks | `DEFER_EXISTING` | The authoritative requirements conflict before option comparison. |
| PF04 | Existing Skeptic sufficient: hard safety violation | Existing CH/KT/SEC block | `DEFER_EXISTING` | One option violates a non-negotiable safety constraint; no frontier computation is needed. |
| PF05 | Ordinary typo edit | Lightweight existing flow | `NOT_APPLICABLE` | There is no multi-option decision. |
| PF06 | Minority harm | Trade-off/exception may surface | `PRESERVE_FRONTIER` | The apparent winner is worse for a protected subgroup, so it is not no-worse on every dimension. |
| PF07 | Long-tail value | May remain an implicit exception | `PRESERVE_FRONTIER` | The apparent loser retains a rare but material outcome on a disaggregated tail dimension. |
| PF08 | Stale evidence | FE:SC can challenge evidence | `DOMINANCE_UNPROVEN` | A's superiority depends on measurements outside the decision's freshness window. |
| PF09 | Causation versus correlation | FE/PO can challenge story | `DOMINANCE_UNPROVEN` | The strict improvement is a causal claim supported only by correlation. |
| PF10 | Consequences with different weights | SH can expose trade-off | `DOMINANCE_UNPROVEN` | A wins only after one legitimate stakeholder weighting is imposed; another weighting protects B. |
| PF11 | Grouping and aggregation error | DAT/KT may surface asymmetry | `DOMINANCE_UNPROVEN` | An average hides a subgroup dimension on which A may be worse. |
| PF12 | Tractability difference | CH:CR/SH:WL may challenge leverage | `DOMINANCE_UNPROVEN` | A's projected upside omits materially lower feasibility or higher execution burden. |
| PF13 | Overlapping uncertainty | FE/PO can challenge proof | `DOMINANCE_UNPROVEN` | Credible intervals overlap, so safe weak superiority is not established. |
| PF14 | Strategic option and information value | SH:NE may preserve exception | `PRESERVE_FRONTIER` | B buys reversibility, learning, or a future option absent from the apparent winner. |
| PF15 | Different consequence horizons | SH/CH:SO may expose hidden cost | `DOMINANCE_UNPROVEN` | A's short-term win and B's long-term protection were compared on mismatched horizons. |
| PF16 | Equal/duplicate outcomes | OM may simplify separately | `PRESERVE_FRONTIER` | Neither option is strictly better; equality alone is not Pareto dominance. |

### Executable scoring and decision rules

The focused Python unittest module must encode scenario inputs as data and run one deterministic reference evaluator. For normalized higher-is-better outcome intervals:

- fail closed to `NOT_APPLICABLE` when fewer than two live options or no comparison objective exists;
- return `DEFER_EXISTING` before frontier computation for an existing hard blocker;
- return `DOMINANCE_UNPROVEN` when freshness, causal support when required, symmetric/disaggregated dimensions, grouping, horizon, tractability, weighting, or material-uncertainty guards fail;
- compute safe dominance using lower-versus-upper credible bounds on every protected dimension and strict lower-versus-upper superiority on at least one;
- include minority, tail, reversibility/information, and strategic option values as protected dimensions rather than after-the-fact prose exceptions;
- return `PRESERVE_FRONTIER` when a valid comparison has no dominated option;
- return `ELIMINATE_DOMINATED` only with at least one proven dominated option and a non-empty frontier.

The tests must bind the evaluator to the runtime contract by reading the candidate `skeptic.md` SH section and requiring the complete applicability, fail-closed, safe-bound, all-dimensions, strict-improvement, preservation-guard, and reporting rules. Marker-only tests are insufficient without executing all scenario rows.

### Disconfirming cases

Reject the hypothesis if any of these occurs:

- PF01 or PF02 remains an undifferentiated trade-off or preserves the proven dominated option.
- Any of PF06-PF16 eliminates the protected option.
- PF03/PF04 overrides or duplicates an earlier decisive Skeptic blocker.
- PF05 adds frontier ceremony to an ordinary non-comparative task.
- A weighted total or average can produce dominance despite a worse protected dimension.
- Stale, correlational, mismatched-horizon, or overlapping-interval evidence can silently pass.
- The candidate changes current final output categories, skips a Thinker, weakens evidence/promotion rules, or breaks existing tests.

### Regression thresholds

Promotion requires all of the following, without exception or post-result threshold edits:

- 16/16 frozen scenario decisions pass.
- 2/2 true-dominance scenarios return `ELIMINATE_DOMINATED`.
- 3/3 existing-sufficient/ordinary controls return exactly `DEFER_EXISTING`, `DEFER_EXISTING`, and `NOT_APPLICABLE`.
- 0 false eliminations across PF06-PF16; minority, long-tail, uncertainty, and option-value preservation are safety-critical zero-tolerance checks.
- The focused module verifies the runtime contract and fails against base `e5494db...` for the intended missing-capability reason before runtime edits.
- Full unittest discovery passes with no baseline regression.
- Existing invocation, evidence, decision, output, promotion, Task Prompt, and all-Thinker invariants remain unchanged.
- Implementation- and Task-level RunSkeptic reviews reach PASS/HANDLED with no blocking finding or unknown.

### Final disposition mapping

- `PROMOTE`: every threshold passes; publish the coherent four-file change.
- `REVISE_AND_RERUN`: the unique gap remains supported and a bounded implementation defect can be fixed without changing this contract; root-cause first and respect retry limits.
- `REJECT_DUPLICATE`: executable comparison shows no material behavior beyond existing Skeptic.
- `REJECT_UNSAFE`: any false elimination, minority/long-tail/option-value regression, threshold weakening, or safety invariant regression occurs.
- `CONFLICT`: the contract needs an owner/value decision, cannot be tested within scope, or cannot reach safe remote-main completion.

The final Task outcome remains `HANDLED` or `CONFLICT`; these dispositions govern only candidate promotion.
