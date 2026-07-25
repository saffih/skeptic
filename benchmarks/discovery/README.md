# Shadow Discovery Suite

This directory contains six original, non-gating behavioral discovery fixtures.

The suite exists to test mechanisms that are not fully represented by the stable
12-case benchmark or the six visible QuickCompare fixtures. It does not have a
scorer, does not produce a promotion verdict, and must not be treated as a
baseline until model execution is available.

## Cases

- `SD01`: completion feasibility before launching a finite batch;
- `SD02`: conditional persistence and progressive durability;
- `SD03`: repair without replaying valid expensive work;
- `SD04`: dominance unproven under stale, correlational, or overlapping evidence;
- `SD05`: aggregation or weighting hiding a protected subgroup loss;
- `SD06`: long-tail, reversibility, and option value preserving the frontier.

## Validation

```text
python3 -m pytest -q tests/test_shadow_discovery.py
```

Validation checks structure, provenance, uniqueness, non-gating status, and
separation from the existing stable benchmark and QuickCompare fixtures.

## Promotion boundary

A case may move into the stable benchmark only after a fresh current-main
baseline demonstrates distinct decision value and a manual review confirms both
the expected mechanism and false-positive controls.

Do not commit historical model answers, private holdouts, generated scores, or
candidate-specific judge hints here.
