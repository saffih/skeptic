# Trust-Boundary FE:TB A/B Experiment

## Public Scope

This public, repository-local experiment tests whether the frozen Candidate B treatment improves detection of material trust or authority transitions without increasing false positives. It uses only the candidates, synthetic discovery fixtures, and scoring contract frozen in this directory.

The freeze step validates inputs only. It generates no runner, scoring, adjudication, result, or source output.

## Repository Checkpoint

- Experiment branch base: `9c24f6f3a8a8c9f75d060ccef07f49e736866689`
- Live `main` frozen for Candidate A: `ba03bf2614faba98c4f589abef86a163c3de8664`
- Candidate source blobs:
  - `skeptic.md`: `1985bd385380ff57fe610099c4cab1e91c551e86`
  - `skeptic-questions.md`: `f5f299d2e3fa925dabb5ba4e661cbb5fa3c1c6cd`

## Frozen Inputs

- `candidates/A/`: byte-exact live-main baseline.
- `candidates/B/`: the baseline plus exactly two experiment-local `FE:TB` additions in `skeptic.md`; questions are unchanged.
- `candidates/candidate-diff.patch`: mechanically reproduced A-to-B diff.
- `fixtures/discovery-fixtures.md`: eight positive fixtures and four negative controls across the frozen representation families.
- `scoring/scoring-addendum.md`: locked scoring, anonymization, conditional gates, and terminal-result vocabulary.
- `freeze-manifest.json`: independently checked source IDs, SHA-256 hashes, counts, families, and bundle construction.

Run the freeze check from the repository root:

```sh
python3 analysis/skeptic-capability-benchmark/experiments/trust-boundary-fe-tb-ab-001/tools/check_experiment.py freeze
```

## Execution Model

Discovery requires one fresh context for each candidate/fixture pair. A custodian freezes the candidate-to-label mapping before execution; byte-preserved outputs are anonymized under one stable random mapping. Two fresh blinded judges score every randomized output independently, and a fresh blinded adjudicator resolves required disagreements without averaging.

Frozen artifacts remain immutable before any execution. Historical scores are context only and cannot replace contemporaneous A/B evidence.

## Conditional Gates

1. Stop with `BASELINE_SUFFICIENT` if Candidate A scores `2` on all 12 discovery fixtures.
2. Run the 36-visible-fixture contemporaneous regression only if Candidate B passes all eight frozen discovery conditions.
3. Run change-impact and education checks only after B passes discovery and visible regression.
4. Enter the patch gate only after `TARGET_GAIN_NO_VISIBLE_REGRESSION` and all preceding checks pass.

## Authority Boundary

This package records an experiment design, not permission to execute it or mutate source. No checkpoint, score, terminal result, or patch-gate eligibility authorizes source changes, promotion, merge, publication, or access beyond the public frozen inputs. Separate current, scoped authorization is required for every later action.
