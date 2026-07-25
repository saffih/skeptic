# Shadow Scenario Inventory

## Purpose

Identify archived mechanisms that may deserve a small non-gating discovery suite
without restoring the former governance system, historical candidate machinery,
generated evidence, or old runtime contracts.

## Correction to the first inventory

The first automated inventory incorrectly classified
`benchmarks/benchmark.py` as the only discovery source. That file is benchmark
implementation, not scenario content.

The archived scenario evidence is mainly embedded in Markdown catalogs and Python
decision tables rather than standalone JSON fixtures. No duplicate normalized
JSON prompt fingerprints were found because there were effectively no relevant
standalone JSON scenario records to compare.

This corrected inventory supersedes the earlier classification in this file.

## Pinned state

- Current main: `1477d278b920a72e21862b3c4446e0c9488f3534`
- Preserved archive: `197bf70d35ce791de7de7499a58bb2a4f970450e`
- Stable golden benchmark: 12 cases
- QuickCompare visible set: 6 fixtures
- Stable scorer remains Scorer V2

## Current coverage that must not be duplicated

The stable benchmark already covers:

- untrusted content promoted into privileged execution;
- unbounded fix-until-PASS iteration;
- proportional handling of a clean internal change;
- executable source of truth versus stale documentation;
- catastrophic recovery risk hidden by cosmetic distractors;
- unsupported quantitative claims;
- consequence-weighted shipment;
- false simplification;
- coercion, hidden burden, and retaliation;
- local optimization and wrong leverage;
- unfalsifiable success criteria;
- speculative architecture.

QuickCompare already covers:

- silent-pass and clean-negative controls;
- tool-instruction promotion;
- authority/source conflict;
- wrong-constraint detection;
- legitimate trade-off restraint.

A discovery scenario should therefore add a distinct mechanism rather than restate
one of these eighteen visible cases.

## Corrected source classification

| Archived source | Blob | Classification | Decision |
|---|---|---|---|
| `benchmarks/benchmark.py` | `67db9fce2152e699adf4b76b1593a68993e5d067` | Benchmark implementation | Exclude as scenario source |
| `skeptic-tests.md` | `233cdb41d30702a85a25373f347be1361a6db70f` | Mixed historical scenario catalog and former governance contract | Use only as a mechanism index; never restore wholesale |
| `tests/test_task_prompt_scenarios.py` | `51b4259a75672ab5b349bd8d09456148860b9803` | Executable former Task Prompt and simplicity decision table | Extract selected mechanisms into new natural-language discovery cases; do not restore the gate oracle |
| `tests/test_constraint_leverage_dominance_routing.py` | `36225f32c46f00db3056200a6e214b417cd8929e` | Eight-case routing contract for CH:CR, SH:WL, and SH:PF | Archive evidence for behavior already promoted; do not restore as a new discovery suite |
| `tests/test_pareto_frontier.py` | `8504539e9f6f0f6d44d2257b8bbe08211dc2f705` | Sixteen-case deterministic Pareto and false-dominance contract | Primary source for under-covered decision mechanisms; transform rather than copy |
| `calibration/quickcompare-20260724/SUMMARY.md` | `b866af86157dd90b164aa732094913d19be3b151` | Generated historical calibration summary | Exclude |
| Historical plans and slice records | mixed | Design history and execution instructions | Reference only; not scenario fixtures |

## Mechanism-level decisions

### Select for a future non-gating discovery suite

| Proposed ID | Mechanism | Archived basis | Why current visible coverage is insufficient |
|---|---|---|---|
| `SD01` | Completion feasibility before launching a batch | Task Prompt feasibility and completion-reserve scenarios | Current visible cases test unbounded loops, but not a finite plan that cannot preserve enough capacity to synthesize, verify, integrate, and close |
| `SD02` | Conditional persistence and progressive durability | Task Prompt persistence scenarios | Current clean-case coverage rejects universal checkpoint machinery, but does not test when expensive accepted work genuinely needs to survive handoff or interruption |
| `SD03` | Repair without unnecessary replay | Checkpoint/resume, validator-defect, and receipt-authority scenarios | No visible case tests a malformed receipt or validator after valid expensive outputs already exist |
| `SD04` | Dominance remains unproven under stale, correlational, or overlapping evidence | Pareto cases PF08, PF09, and PF13 | Current wrong-constraint cases do not test false certainty caused by evidence quality |
| `SD05` | Aggregation or weighting hides minority harm | Pareto cases PF06, PF10, and PF11 | The coercion case covers dignity and retaliation, but not a numerically superior average that conceals a protected subgroup loss |
| `SD06` | Long-tail, reversibility, and option value preserve the frontier | Pareto cases PF07, PF14, and PF15 | Current visible cases do not test short-term dominance claims that erase long-tail protection or future options |

### Do not select

| Mechanism | Reason |
|---|---|
| False simplification | Already a stable golden case |
| Wrong constraint versus wrong lever | Already represented in QuickCompare and the stable local-optimization case |
| Hidden burden and coercion | Already a critical stable golden case |
| Unbounded retries | Already a critical stable golden case |
| Ordinary-task silence | Already represented by stable and QuickCompare clean controls |
| Exact old PASS/ACTION/DECOMPOSE/CONFLICT gate oracle | Belongs to the rejected former governance model |
| P0-P6 lifecycle, closure-only state, mandatory reserve fields, and Task Closure Receipt | Do not restore old lifecycle machinery |
| Full deterministic Pareto oracle | Discovery fixtures should test behavioral reasoning, not reintroduce a parallel runtime decision engine |

## Deduplication conclusion

There are no useful exact prompt duplicates to eliminate because the historical
material is expressed as mechanism catalogs and executable decision tables.

Deduplication must happen at the mechanism level:

- merge stale evidence, correlation-only evidence, and overlapping uncertainty
  into one false-dominance evidence case;
- merge weighting and grouping traps into one minority-harm aggregation case;
- merge long-tail, consequence-horizon, reversibility, and option-value traps
  into one frontier-preservation case;
- keep completion feasibility, conditional persistence, and no-replay repair
  separate because they fail through different causal mechanisms.

The minimal proposed discovery suite is therefore six cases.

## Next branch

`reorg/shadow-discovery-suite`

Authorized scope for the next task:

- create one non-gating discovery manifest;
- create six original natural-language fixtures, `SD01` through `SD06`;
- include expected material mechanisms, acceptable alternative findings,
  prohibited false positives, and dangerous failures;
- add deterministic schema/fixture validation tests;
- document archive provenance by commit and source IDs only.

Explicit exclusions:

- no changes to `skeptic.md`, `AGENTS.md`, or `agents/`;
- no changes to the stable 12-case benchmark, Scorer V2, or baseline V1;
- no changes to QuickCompare;
- no copied historical model responses or judge outputs;
- no private or protected holdout content;
- no generated baseline scores;
- no lifecycle controller, checkpoint state machine, receipt gate, or model calls.

The suite remains non-gating until a fresh current-main behavioral baseline can be
generated.
