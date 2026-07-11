# Candidate C1-current-main-plus-loop-collect

- Candidate ID: `C1-current-main-plus-loop-collect`
- Base format: `versions/F5-current-main`
- Candidate text location: this definition only; source files are not edited.
- Intended capability target: `LOOP`, `NOISE`, `EVID`

## Minimal Runtime Extension Under Test

Optional `loop: collect` mode:

- Applies only when the user explicitly requests repeated Skeptic passes, finding collection, or compare-across-passes behavior.
- Does not change normal Skeptic behavior when absent.
- Collects findings by stable issue identity: artifact, claim, evidence, and material risk.
- Dedupes repeated findings before reporting.
- Tracks each finding as `new`, `changed`, `unchanged`, `resolved`, or `blocked`.
- Stops when source is unavailable, evidence cannot be rechecked, or the next pass would repeat without new information.

## Non-Change Constraint

This candidate must not alter permission rules, source-of-truth rules, worker receipt requirements, or normal single-pass output.
