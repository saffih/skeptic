# Process-Value A/B Experiment

## Decision

Determine whether one optional `PROC` question has enough public exploratory value to justify later evaluation. This experiment cannot authorize a source patch, candidate promotion, private-evidence access, Stage 6E execution, or merge.

## Repository Checkpoint

- Experiment branch base: `fcd1fa31a40fea050dc1f0699948e5e2c7cfebd4`
- Live `main` frozen for Candidate A: `ba03bf2614faba98c4f589abef86a163c3de8664`
- Candidate source blobs:
  - `skeptic.md`: `1985bd385380ff57fe610099c4cab1e91c551e86`
  - `skeptic-questions.md`: `f5f299d2e3fa925dabb5ba4e661cbb5fa3c1c6cd`
- Runner and Judge model: `gpt-5.6-sol`
- Reasoning effort: `high`

## Frozen Inputs

- `candidates/A/`: exact live-main baseline.
- `candidates/B/`: the same baseline plus only experiment-local `CPX6` and its activation rule.
- `fixtures/discovery-fixtures.md`: four positive `PROC` cases and four negative controls.
- `scoring/scoring-addendum.md`: locked scale, anonymization, discovery gate, conditional visible-regression gate, causal-specificity check, and result vocabulary.
- `freeze-manifest.json`: hashes and candidate-bundle construction.

The freeze commit must precede every raw output. Frozen candidates, fixtures, expectations, and scoring rules must not change afterward.

## Execution Boundary

Discovery runs use one fresh context per candidate/fixture pair. Each runner receives one candidate bundle, one fixture input artifact, and its prompt only. Two fresh blinded Judges score all 16 randomized anonymous outputs independently; a fresh adjudicator resolves required disagreements without averaging.

The 36-fixture visible regression phase runs only if Candidate B passes the frozen discovery gate. Historical scores are context only.

## Result

- Discovery execution: complete, 16 fresh runner contexts, zero runner retries.
- Candidate A: `14 / 16` (`7 / 8` positive, `7 / 8` negative control).
- Candidate B: `15 / 16` (`7 / 8` positive, `8 / 8` negative control).
- Discovery gate: `NO_ADDITIONAL_VALUE`.
- Visible regression: not run because B improved zero positive fixtures and had no positive-total gain.

The observed one-point difference is confined to negative control `PV07`. It does not demonstrate that the optional question improves the target `PROC` cases. No source patch, promotion, private-evidence access, Stage 6E execution, PR, or merge is authorized.
