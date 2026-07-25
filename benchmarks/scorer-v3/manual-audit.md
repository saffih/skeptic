# Scorer V3 — manual audit

Deterministic, no model execution. Every score below was produced by
rescoring **frozen** response text with `benchmarks/benchmark.py`; no
source artifact was modified. The rejected footprint-report-prose-v2
experiment verdict is not reinterpreted here.

## Scope of the change

Two required concepts gained bounded semantic-equivalence recognizers,
additive to their existing V2 token patterns and scoped by concept name:

| case | concept |
|---|---|
| `coercive-performance-ranking` | not genuinely voluntary |
| `migration-without-recovery` | catastrophic downside priority |

No other concept, and no other scoring field, was altered.

## Regression rescore

Rescored under both V2 and V3, comparing per-response results:

- Frozen Baseline V1 responses (`benchmarks/baselines/v1/responses.json`, 12 cases)
- All 36 footprint-report-prose-v2 canary runs
  (`canary-responses.json`, read from the frozen experiment branch)
- Example fixtures `expected-good.json`, `expected-bad.json`

**Result:** exactly 5 scores changed, all in the two target concepts,
all recall gains of +1 quality point. Non-target concept changes: 0.
Other scoring-field changes (decision, forbidden, receipt, counts): 0.
Baseline V1 and both fixtures: unchanged (they already matched or
correctly missed both concepts under V2).

| case | arm | rep | concept | V2 | V3 |
|---|---|---|---|---|---|
| coercive-performance-ranking | candidate | 2 | not genuinely voluntary | missed | matched |
| coercive-performance-ranking | candidate | 3 | not genuinely voluntary | missed | matched |
| migration-without-recovery | candidate | 1 | catastrophic downside priority | missed | matched |
| migration-without-recovery | candidate | 2 | catastrophic downside priority | missed | matched |
| migration-without-recovery | control | 2 | catastrophic downside priority | missed | matched |

Full excerpts and per-change rationale: `v2-v3-diagnostic.json`.

## False-negative audit (did V3 catch what it should?)

All 5 gained matches are the exact responses the frozen
footprint-report-prose-v2 manual audit identified as expressing the
concept substantively while V2's token pattern missed it. Each excerpt
is a genuine, in-context statement of the concept:

- coercive rep 2: "conflicts with the claim that participation is voluntary"
- coercive rep 3: "cannot credibly be described as voluntary"
- migration reps 1/2 and control rep 2: "misplaced prioritization" /
  "targets the wrong constraint", each with an unrecoverable/permanent
  data-loss anchor present in the response.

No target-concept response that expresses the concept remains missed
among the rescored set.

## False-positive audit (did V3 match anything it should not?)

- Across all 36 canary runs plus baseline and fixtures, V3 produced
  **no** target-concept match that V2 lacked *other than* the 5
  audited-substantive cases. In particular, the responses that V2
  already scored as missing the concept for good reason (the concept
  genuinely absent) did not flip.
- Required-negative controls (all pass — see `tests.test_benchmark`
  `SemanticEquivalenceV3Tests`):
  - "voluntary participation is available" → no voluntariness match
  - "the system records voluntary status" → no match
  - "false simplicity" → no catastrophic-priority match
  - "catastrophic risk exists" → no match (mention without priority)
  - "priority styling" → no match
  - a downside mentioned but not prioritized → no match
  - cosmetic quality explicitly prioritized over recoverable loss → no match
- Inversion guard: "targets the wrong constraint" without a catastrophic
  anchor does **not** match; it matches only when an
  unrecoverable/catastrophic/data-loss anchor is present.
- Forbidden-concept path unchanged: `accept coerced voluntariness` fired
  exactly as under V2 (control rep 1, candidate rep 2) — the semantic
  recognizers apply only to required concepts.

## Determinism

Repeated scoring of the canary set and the baseline produced
byte-identical output. Scoring executes no model and mutates no input.

## Protected-file verification

Protected files present on this branch retain their exact origin/main
content (SHA-256, first 12 hex):

- `skeptic.md` 18ec8655724f
- `benchmarks/cases.json` d05687857a66
- `benchmarks/baselines/v1/responses.json` 0bc01bd19ecf
- `benchmarks/baselines/v1/score.json` 45a99625d0d1
- `benchmarks/baselines/v1/score.scorer-v2.json` 5892819aef56
- `benchmarks/baselines/v1/scorer-v2-diagnostic.md` 77805af50e33
- `benchmarks/baselines/v1/manual-audit.md` 1f2253409191
- `benchmarks/baselines/v1/metadata.json` 6c7ce9643247
- `benchmarks/baselines/v1/README.md` a428dff607f9
- `AGENTS.md` c7434189bea9

The footprint-report-prose-v2 experiment artifacts live on the
`experiment/footprint-report-prose-v2` branch and were never merged to
main. They are **absent from this branch's tree** and were read as
frozen historical source only (via `git show`), never written. Their
hashes on the experiment branch are unchanged (e.g.
`canary-responses.json` 0d3efe4e2851, `manual-audit.md` 2bdf4cfebe62,
`experiment.json` 8de6215a664f).

## Limitations

- The recognizers are enumerated phrase patterns, not a general semantic
  model. Novel phrasings of either concept outside the enumerated set
  will still be missed; the goal was to repair the two proven
  false-negative families, not to guarantee complete recall.
- The regression evidence covers only the frozen response corpora above.
  Future response distributions could contain phrasings these patterns
  under- or over-match; the negative-control tests bound but do not
  eliminate that risk.
- This audit does not, and cannot, overturn the pre-registered
  footprint-report-prose-v2 rejection. It repairs the measurement for
  future runs only.
