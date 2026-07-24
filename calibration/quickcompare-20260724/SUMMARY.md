# QuickCompare calibration summary — 2026-07-24

Baseline: `195c500a5a223727771da6168f67140567806428`.

## Metrics

- The deterministic calibration exercises all four verdict paths and passes 4/4:
  `IMPROVED`, `REGRESSED`, `NO_MATERIAL_CHANGE`, and `INCONCLUSIVE`.
- The calibration test module covers 12 named behavior classes.
- The corrective focused suite covers six resume/cache cases, including a
  same-argv runner script edited in place: reuse is invalidated (24 calls are
  regenerated) rather than accepted from cache.
- Raw response cache, cache-temporary file, and raw call-record permissions are
  asserted as `0600`; the containing `raw/` directory is asserted as `0700`.

## Limitations

These are deterministic synthetic and fake-runner checks. They establish the
instrument's cache, privacy, and verdict behavior; they do not establish
provider-model quality, live-run reproducibility, or a behavioral improvement
for a particular candidate. Resume is deliberately disabled when a runner
cannot be bound to file content and no explicit immutable runner identity is
supplied.

## Retained full evidence (not committed)

The complete evidence remains in `analysis/quickcompare-calibration-v1/` and
is intentionally excluded from this corrective commit. Reference hashes:

- `metrics-summary.json` — `1d35027be981c74cfd140398a25c08d1f29ceca06482ca18d92fd73d2470474f`
- `validation-results.json` — `21a4169929520e2b8cb40954e08d1cb7305725dc2c49918a1ae5c6609403304e`
- `pre-post-comparison.md` — `a119bff8f7fcd0abc690a512b6977dc789834b9df3b73d2c5a3ef99424c69a08`
- `runskeptic-final.md` — `a36a2f8275cff760a93806037dd8278c750f554f1854ec95f293d3a9db0144d0`
