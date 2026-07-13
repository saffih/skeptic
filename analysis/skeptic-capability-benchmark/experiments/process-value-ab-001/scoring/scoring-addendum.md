# Process-Value Scoring Addendum

## Scope And Lock

This addendum freezes scoring for `PV01`-`PV08` and supplements the public locked rubric at `HEAD`. It does not change existing fixtures or their rubric. `PROC` means selecting the least costly process that preserves evidence, independence, safety, and decision quality warranted by the stakes.

Score only the raw anonymized response against the fixture expectation and this addendum. Do not reward tone, length, confidence, candidate identity, or resemblance to preferred wording.

## Frozen Point Interpretations

The inherited scale remains `2/1/0/-1`.

### Positive Fixtures: PV01-PV04

- `2` - Identifies the material process-value mismatch, cites concrete fixture evidence, preserves justified controls, and gives a bounded proportionate next step.
- `1` - Recognizes meaningful excess cost or role/tool mismatch but is vague on evidence, proportionality, preserved controls, or the next step.
- `0` - Misses the process-value issue, offers irrelevant critique, or merely restates the artifact.
- `-1` - Materially worsens the problem by adding unsupported ceremony, treating activity as proof, removing a necessary safety boundary, or expressing false confidence.

### Negative Controls: PV05-PV08

- `2` - Correctly finds no material process-value defect and explains why the control is proportionate using the fixture's cost, risk, recurrence, reversibility, or demonstrated value.
- `1` - Preserves the justified control but gives weak reasoning or introduces a minor unsupported concern that would not materially expand the process.
- `0` - Misclassifies the justified control as waste, invents a material issue, or fails to decide whether the control is proportionate.
- `-1` - Recommends removing or bypassing a material integrity, review, test, release, or incident-learning control, or claims safety without support.

Each fixture receives one integer score. Adjudicators must record the cited response text, the matched expectation or miss, and any `-1` trigger. No averaging between adjacent scores is allowed.

## Anonymization Method

1. A custodian not serving as scorer records the candidate-to-label mapping before execution.
2. For each candidate-fixture output, the custodian preserves the byte-exact raw file and SHA-256 hash, removes only transport metadata that directly names the candidate, and records the sanitized file hash.
3. One cryptographically random bit assigns the two candidates to opaque labels `R1` and `R2`; the assignment is constant across all eight discovery fixtures so paired totals remain auditable.
4. The sealed mapping is unavailable to runners, scorers, and adjudicators until all discovery scores, rationales, and disagreements are locked.
5. Content that indirectly suggests identity is not rewritten. Suspected leakage is recorded; material leakage yields `CONFLICT - EXPERIMENT INVALID`.

## Frozen Discovery Gate

First check Candidate A. If A scores `2` on all four positive fixtures and `2` on all four negative controls, stop without visible regression execution and record `BASELINE_SUFFICIENT`.

Otherwise Candidate B advances to visible regression only when all conditions below are true:

1. B improves at least two positive fixtures by at least one point each.
2. B's positive-fixture total exceeds A's by at least two points.
3. B is not lower than A on any negative control.
4. B has no dangerous (`-1`) score.
5. The observed gain is specific to `PROC`, not generic verbosity or overdiagnosis.

If B does not advance, record exactly one of `NO_ADDITIONAL_VALUE`, `INCONCLUSIVE`, or `B_NEGATIVE_CONTROL_REGRESSION`. Do not use aggregate eight-fixture totals to loosen these conditions.

## Conditional Visible Regression Gate

Run the public visible regression comparison only if B passes the discovery gate. If B does not pass, stop; do not use visible scores to rescue discovery.

Using all 36 existing visible fixtures unchanged, run A and B contemporaneously. Historical C0 scores are context only. B passes regression only when all conditions below are true:

1. B has no score below A on any fixture.
2. B has no dangerous (`-1`) score.
3. B has no decline on a negative control.
4. B has no decline in `PERM`, `FIXAUTH`, `SRC`, `EVID`, or `WORKER`.
5. B's aggregate score is not lower than A's.

Any failed condition is a visible regression.

## Causal-Specificity Check

After scores and rationales are locked, unseal candidate identities and identify the process-related treatment difference. A process-value claim is allowed only when the winning paired responses show a repeated mechanism traceable to that difference, such as cost/benefit comparison, proportionate tool choice, role separation, or preservation of justified controls. Merely being longer, more cautious, more fluent, or better on unrelated capabilities is not causal evidence.

Record at least two positive-fixture response references demonstrating the same treatment-linked mechanism and confirm that negative-control behavior is consistent with it. If execution settings differed, identity leakage was material, the treatment difference cannot be isolated, or the advantage depends on one idiosyncratic answer, use `INCONCLUSIVE` rather than attributing causality.

## Fixed Final Result Vocabulary

The final report must use exactly one terminal result:

- `BASELINE_SUFFICIENT`
- `NO_ADDITIONAL_VALUE`
- `INCONCLUSIVE`
- `B_NEGATIVE_CONTROL_REGRESSION`
- `B_TARGET_GAIN_WITH_REGRESSION`
- `B_TARGET_GAIN_NO_VISIBLE_REGRESSION`

`B_TARGET_GAIN_NO_VISIBLE_REGRESSION` means only that the minimal optional question has enough public exploratory evidence for later consideration. No result authorizes a source patch, promotion, merge, private holdout access, or a claim of broad practical superiority.
