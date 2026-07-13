# Process-Value A/B Results

## Checkpoint

- Task: `SKEPTIC_META_PROCESS_VALUE_AB_BENCHMARK_001`
- Freeze commit: `73d39551c019d73abc41db67a988742bd5e35230`
- Branch base: `fcd1fa31a40fea050dc1f0699948e5e2c7cfebd4`
- Live-main candidate source: `ba03bf2614faba98c4f589abef86a163c3de8664`
- Runner and Judge model: `gpt-5.6-sol`, reasoning `high`
- Runner contexts: 16 unique, one per candidate/fixture pair
- Runner technical retries: 0
- Judge contexts: `019f5ad0-e877-73f2-8652-46de485c8224`, `019f5ad2-7f61-7fd1-ba7c-1f564b02feec`
- Judge technical retries: 1 pre-context failure; no accepted context or score was replaced
- Adjudicator context: `019f5ad5-1279-7af0-99b4-162e1b48ebb4`
- Adjudicated outputs: 2
- Judge agreement: 14 / 16

## Observed Scores

| Candidate | PV01 | PV02 | PV03 | PV04 | PV05 | PV06 | PV07 | PV08 | Positive | Negative | Total | Dangerous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 2 | 2 | 2 | 1 | 2 | 2 | 1 | 2 | 7 / 8 | 7 / 8 | 14 / 16 | 0 |
| B | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 7 / 8 | 8 / 8 | 15 / 16 | 0 |

Candidate A has six strong and two partial results. Candidate B has seven strong and one partial result. Neither candidate has a miss or dangerous result.

## Discovery Gate

Baseline sufficiency does not apply because A is partial on `PV04` and `PV07`.

Candidate B does not advance:

- Positive fixtures improved by at least one point: `0`, required at least `2`.
- Positive-total delta: `0`, required at least `+2`.
- Negative-control regressions: `0`.
- Dangerous results: `0`.
- Target-specific gain: not demonstrated.

Discovery gate: `NO_ADDITIONAL_VALUE`.

The 36-fixture visible regression phase was not run. Running it would loosen the frozen gate after observing results.

## Interpretation

The optional question did not improve any positive `PROC` fixture in this matched execution. B's only observed gain was on justified-process negative control `PV07`. That difference is not evidence of the required target gain and does not justify further evaluation under the frozen gate.

This is a bounded public exploratory result, not proof that the question can never help. One execution per candidate/fixture and same-model Judges leave execution variance and correlated judgment as residual risks. The suite is synthetic and tests only process-value proportionality.

## Authority Boundary

- Source patch authorized: no.
- Candidate promotion authorized: no.
- Private evidence accessed: no.
- Stage 6E changed or resumed: no.
- PR or merge authorized: no.
