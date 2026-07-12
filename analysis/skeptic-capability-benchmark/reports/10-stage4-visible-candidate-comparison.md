# Stage 4 Visible Candidate Comparison

Task ID: `STAGE_4_VISIBLE_CANDIDATE_COMPARISON_REMOTE_VERIFIED_PACKET_001`

## Input Checkpoint

- Branch: `benchmark/skeptic-capability-stage2-2026-07-04`
- Input commit: `b49747a41cf78b123d8f1428dddb1c6129ebcc6e`
- Source baseline: `183acd39cc51a8ada33bcf7506d506aa528fbca7`
- Comparison scope: accepted visible-fixture scoring reports only.
- Raw outputs rescored: no.
- Holdout content read: no.
- Final candidate promoted: no.
- Merge readiness claimed: no.

## Canonical Candidate Definitions

| Candidate | Candidate definition path | SHA-256 |
|---|---|---:|
| C0-current-main | `analysis/skeptic-capability-benchmark/candidates/C0-current-main/definition.md` | `bb5a68b3d5aabfcfe875161bf266a2a1078968cefdc23f8c9e6fd6904c09dd6f` |
| C1-current-main-plus-loop-collect | `analysis/skeptic-capability-benchmark/candidates/C1-current-main-plus-loop-collect/definition.md` | `3e6b77186277d6a4abf257c5f64e6c5940c2432bb771d82a468029adc2b70aaf` |
| C2-current-main-plus-code-skeptic-domain-extension | `analysis/skeptic-capability-benchmark/candidates/C2-current-main-plus-code-skeptic-domain-extension/definition.md` | `122874f4a8a9383a045afa913ee255cf97081c07268f3e08a75b85036aebe85c` |
| C3-current-main-plus-loop-and-code-extension | `analysis/skeptic-capability-benchmark/candidates/C3-current-main-plus-loop-and-code-extension/definition.md` | `9567e6cc9266131bd36fabb4638b4a9fc0c50092aecb853ff8bb31f1f4535c0c` |

Candidate hashes reconcile with `analysis/skeptic-capability-benchmark/reports/02-candidate-definitions.md`.

## Canonical Visible Scoring Reports

| Candidate | Canonical report path | SHA-256 | Validation result |
|---|---|---:|---|
| C0-current-main | `analysis/skeptic-capability-benchmark/reports/05-stage3-c0-current-main-visible-scoring.md` | `699d344faac82cae8d73df4e60f41f0274c7814f32fc670bbd338249555270d3` | PASS |
| C1-current-main-plus-loop-collect | `analysis/skeptic-capability-benchmark/reports/06-stage3-c1-current-main-plus-loop-collect-visible-scoring.md` | `1cf0fc810f05278e75f21ce1016916371b45e3204acfd7cbbbe1b5c3e8f64097` | PASS |
| C2-current-main-plus-code-skeptic-domain-extension | `analysis/skeptic-capability-benchmark/reports/07-stage3-c2-current-main-plus-code-skeptic-domain-extension-visible-scoring.md` | `e6ad48915320f5a523422116745c589b8c995121ceae646445652d0c71fba728` | PASS |
| C3-current-main-plus-loop-and-code-extension | `analysis/skeptic-capability-benchmark/reports/09-stage3-c3-current-main-plus-loop-and-code-extension-visible-scoring-corrected.md` | `7a1680e6d957ffebe70c8b97905b714b010049f1d317a0b5ebc792aa2118ab6b` | PASS |

Superseded C3 report:

- Path: `analysis/skeptic-capability-benchmark/reports/08-stage3-c3-current-main-plus-loop-and-code-extension-visible-scoring.md`
- SHA-256: `d29f02192c5af7531b194375e56e5d1fa26d8384a79a5156f68846f2e69f10bd`
- Current comparison use: supersession and immutability verification only.
- Current comparison conclusion source: corrected C3 report only.

## Validation Gate

- Four canonical reports validated: PASS.
- Exactly 36 visible fixture rows per report: PASS.
- Expected visible fixture manifest reconciled: PASS.
- Score/category mapping validated: PASS.
- Aggregate arithmetic reconciled: PASS.
- Dangerous lists reconciled: PASS.
- Disqualification lists reconciled: PASS.
- Corrected-C3 supersession validated: PASS.
- Corrected-C3 differs from the original final result set only at `CI04`: PASS.
- Holdout content read: no.
- Raw responses rescored: no.
- Candidate comparison before this stage: no current comparison conclusion used a prior comparison.
- Source/design files changed: no.

Validation implementation:

- Parser path: `/tmp/stage4_validate_reports.py`
- Parser SHA-256: `2c88ac2aaabb4ad932a6b80c56b3bc4f4bf660ac337684ccd708617c97785dc1`
- Validation JSON path: `/tmp/stage4-validation.json`
- Validation JSON SHA-256: `7e560a0f42585ab1c2b04a9440fe294f271286ec4c13706a46a7198bb33e3d49`
- Validation verdict: PASS.

## Aggregate Matrix

| Candidate | Total | Maximum | Strong | Partial | Miss | Dangerous |
|---|---:|---:|---:|---:|---:|---:|
| C0-current-main | 71 | 72 | 35 | 1 | 0 | 0 |
| C1-current-main-plus-loop-collect | 72 | 72 | 36 | 0 | 0 | 0 |
| C2-current-main-plus-code-skeptic-domain-extension | 72 | 72 | 36 | 0 | 0 | 0 |
| C3-current-main-plus-loop-and-code-extension corrected | 61 | 72 | 27 | 7 | 2 | 0 |

## Family Matrix

| Candidate | PG /12 | RB /12 | CI /16 | DQ /8 | WK /14 | LP /10 |
|---|---:|---:|---:|---:|---:|---:|
| C0-current-main | 12 | 12 | 15 | 8 | 14 | 10 |
| C1-current-main-plus-loop-collect | 12 | 12 | 16 | 8 | 14 | 10 |
| C2-current-main-plus-code-skeptic-domain-extension | 12 | 12 | 16 | 8 | 14 | 10 |
| C3-current-main-plus-loop-and-code-extension corrected | 9 | 10 | 11 | 7 | 14 | 10 |

## Target-Capability Comparison

C0-current-main is the baseline control. It scored `71 / 72`, with one partial at `CI07`, no misses, no dangerous failures, all visible negative controls strong, loop family already at `10 / 10`, and code family at `15 / 16`.

C1-current-main-plus-loop-collect scored `72 / 72`, with no non-strong fixtures and no dangerous failures. Its optional runtime placement matches the candidate charter, and visible negative-control behavior did not regress. The visible set does not establish an incremental LOOP-family score gain because C0 already reached the visible LOOP ceiling.

C2-current-main-plus-code-skeptic-domain-extension scored `72 / 72`, with no non-strong fixtures and no dangerous failures. It improves the code family from C0's `15 / 16` to `16 / 16`, with the exact visible improvement at `CI07`. Its code-specific probes remain in the companion domain-question layer and activate conditionally on established code/test relevance.

C3-current-main-plus-loop-and-code-extension corrected scored `61 / 72`, with seven partials, two misses, and no dangerous failures after the CI04 repair. The misses are `PG05` and `CI08`. Regressions extend beyond the combined candidate's intended target capabilities, while `WK` and `LP` remain perfect.

Visible-set ceiling effects matter: C1 and C2 tie at `72 / 72`, but only C2 shows an explicit target-family score improvement over C0 in the visible set. C1 remains unresolved because visible LOOP fixtures cannot distinguish it from a baseline already at ceiling.

## Negative-Control Comparison

- C0-current-main: all visible negative controls strong.
- C1-current-main-plus-loop-collect: all visible negative controls strong.
- C2-current-main-plus-code-skeptic-domain-extension: all visible negative controls strong.
- C3-current-main-plus-loop-and-code-extension corrected: visible negative-control regression is present, including misses at `PG05` and `CI08`.

## Pairwise Findings

### C1 versus C0

- Aggregate delta: `+1`.
- LOOP-family delta: `0`.
- Code-family delta: `+1` at `CI07`.
- Target-aligned LOOP improvement: not demonstrated because the visible LOOP family is ceiling-limited.
- Regression: none observed.
- Conclusion: retain C1 for holdout discrimination, but do not treat it as the provisional visible winner.

### C2 versus C0

- Aggregate delta: `+1`.
- Code-family delta: `+1`.
- Exact improvement: `CI07`.
- Regression: none observed.
- Negative-control regression: none observed.
- Conclusion: C2 has the strongest target-aligned visible evidence.

### C3 corrected versus C0

- Aggregate delta: `-10`.
- PG delta: `-3`.
- RB delta: `-2`.
- CI delta: `-4`.
- DQ delta: `-1`.
- WK delta: `0`.
- LP delta: `0`.
- Negative-control misses: `PG05`, `CI08`.
- Conclusion: reject the combined candidate for holdout advancement.

### C1 versus C2

- Aggregate result: tie at `72 / 72`.
- Both candidates have no visible regression or dangerous result.
- C1 targets optional repeated-pass collection.
- C2 targets code/test/integration detection.
- Only C2 shows an explicit target-family score improvement over C0 in the visible set.
- Visible LOOP fixtures cannot distinguish C1 because C0 is already at ceiling.
- Conclusion: C2 is the provisional visible leader; C1 remains an unresolved co-finalist.

## Minimality And Architecture

- C0-current-main: no candidate change; retained as baseline control.
- C1-current-main-plus-loop-collect: optional core-runtime loop behavior; visibly safe and complete, with no visible LOOP score separation from C0.
- C2-current-main-plus-code-skeptic-domain-extension: optional companion domain-question probes; clearest target-aligned visible improvement and no observed visible regression.
- C3-current-main-plus-loop-and-code-extension: composition of C1 and C2; visible results show material noise and execution degradation rather than dominance over the components.

The visible evidence supports continued evaluation of C0, C1, and C2. It does not support advancing C3 to private holdout evaluation.

## Scoring-Provenance Limitation

C0, C1, and C2 reports were produced under earlier accepted benchmark scoring procedures. C3 uses later fresh-scoring and append-only correction receipts. Stage 4 treats every canonical accepted report as benchmark evidence. Stage 4 does not claim the scoring procedures were identical in provenance depth. Stage 4 does not rescore or normalize candidates. This limitation strengthens the need for controlled private holdout execution before final promotion.

## Visible Disposition

| Candidate | Visible disposition | Reason |
|---|---|---|
| C0-current-main | BASELINE_CONTROL | Required unchanged baseline and holdout control. |
| C1-current-main-plus-loop-collect | UNRESOLVED_COFINALIST | Perfect visible score, no regression, and LOOP fixtures are ceiling-limited against C0. |
| C2-current-main-plus-code-skeptic-domain-extension | PROVISIONAL_VISIBLE_LEADER | Perfect visible score plus the clearest target-aligned visible improvement at `CI07`. |
| C3-current-main-plus-loop-and-code-extension corrected | ELIMINATED_VISIBLE_REGRESSION | Corrected visible score has material regressions, including misses at `PG05` and `CI08`. |

## Holdout Finalists

- `C0-current-main`
- `C1-current-main-plus-loop-collect`
- `C2-current-main-plus-code-skeptic-domain-extension`

Visible provisional leader:

- `C2-current-main-plus-code-skeptic-domain-extension`

Visible final winner:

- none

Reason:

- C2 has the clearest target-aligned visible improvement.
- C1 remains unresolved because LOOP fixtures are ceiling-limited.
- C0 is required to determine whether holdout differences represent real candidate improvement.
- C3 has material visible regressions.

## Final Decision Boundary

- Final candidate promoted: no.
- Winner selected: no.
- Holdout result claimed: no.
- Source patch recommended: no.
- Merge readiness claimed: no.

## RunSkeptic Comparison Gate

- Source read: `skeptic.md`
- Skeptic blob SHA: `1985bd385380ff57fe610099c4cab1e91c551e86`
- Permission mode: report-only, then exact-path commit/push if PASS.
- DONE statement: compare accepted visible results, create exactly one report, commit and push it, stop before holdouts.
- Major steps run: GATE, FUNDAMENTAL SCAN, MAP, CONFIDENCE, STABILIZE, EVIDENCE, DECIDE, ACT, VERIFY, LEARN.
- Thinkers considered: Charlie Munger, Occam's Razor, Richard Feynman, Karl Popper, Immanuel Kant, Saffi.
- Evidence used: canonical report hashes, deterministic row parser, aggregate matrix, family matrix, corrected-C3 supersession, candidate definition hash table.
- Decision path: PASS; proceed with one bounded comparison report.
- Verification performed: report arithmetic, corrected-C3 usage, holdout boundary, no final winner claim, exact mutation path.
- Unresolved conflicts / unknowns: none blocking this visible-comparison report.
- Final output category: HANDLED.

## Next Authorized Task

`STAGE_5_PRIVATE_HOLDOUT_EXECUTION_C0_C1_C2_CLEAN_ROOM_PACKET_001`

Do not execute that task from this report.
