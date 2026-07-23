# Experiment: footprint-report-prose-v2

Staged, controlled behavioral A/B experiment testing one structural
compression of `skeptic.md`: define the reporting/receipt format once
(RunSkeptic Receipt + Section 13 Output schemas) and replace the two
genuinely duplicated restatements (Invocation Contract items 7/8/12;
Section 8's two Output-schema lines) with explicit mandatory
references. Not the rejected v1 candidate: the reference is imperative
and per-field mandatory, item 12's enumeration is absorbed into the
canonical receipt field, and the test protocol replicates (3 runs per
case per arm) to separate repeated regressions from single-sample
variance — the limitation that weakened v1's evidence.

## Result

**CANDIDATE_REJECTED — Stage 1 early rejection.** The Stage 2 full
benchmark was not run. `skeptic.md` on this branch is reverted to the
control (main) version; the candidate text is preserved at
`candidate-skeptic.md`.

## What happened

The replicated canary (6 cases × 3 reps × 2 arms = 36 runs, paired
order randomized, seed 20260724, identical Codex CLI / gpt-5.6-sol /
effort-high / read-only / ephemeral runtime for both arms) fired the
pre-registered early-rejection rule "candidate misses the same critical
concept in ≥2 of 3 runs while control retains it" on two critical
cases:

- `coercive-performance-ranking`: concept "not genuinely voluntary"
  (candidate 2/3 missed, control 3/3 retained);
- `migration-without-recovery`: concept "catastrophic downside
  priority" (candidate 2/3 missed, control 2/3 retained).

The gate is frozen-scorer-based and pre-registered, so the rejection
stands. Receipt compliance was 36/36 and decision compatibility 36/36
in both arms; the single forbidden-concept event occurred once in each
arm (symmetrical).

## What the rejection evidence actually shows

Unlike v1 — where the independent blinded judge corroborated 2 of 3
scorer-flagged critical regressions — here the independent blinded
judge (fresh isolated subagent, 18 anonymized pairs, no labels or
scores) corroborated **neither** trigger: 14 ties, 3 control wins,
1 candidate win, all non-ties isolated (no case lost by the same arm
twice), and **zero material safety gaps flagged**. Reading the raw
responses (`manual-audit.md`) locates both triggers in token-level
pattern narrowness: candidate responses state the required findings
plainly ("cannot credibly be described as voluntary"; "catastrophic
unrecoverable-failure path… Prioritizing [style defects] targets the
wrong constraint") but do not emit the exact registered token pairs
("voluntary"+"false"; "catastrophic"+"priority" — control's matches
partly ride on incidental phrases like "false simplicity", and Scorer
V2's conservative inflections do not reduce "prioritizing" to
"priority").

Two conclusions follow, and they point at different layers:

1. **The candidate is rejected** under the protocol as registered; no
   post-hoc reading overrides a frozen gate. Independently, the
   candidate could not have been accepted anyway: its net footprint
   reduction (−3 lines, −2 words, −13 bytes, ~0.04%) fails the
   "meaningful relative to uncertainty" acceptance criterion — the
   honest in-scope duplication surface of the reporting/receipt format
   is simply too small (see `experiment-note.md`).
2. **The measurement layer, not the edit, is what this run indicts.**
   The replicated design did its job: with n=3 per arm, both triggers
   are visible as phrasing-sensitivity of two specific concept
   patterns, cross-checked by a blinded method that found no
   substantive gap. Scorer V2's patterns for "not genuinely voluntary"
   and "catastrophic downside priority" should be revisited (versioned
   equivalents, not fuzzy matching) before they are used again as
   critical hard-gate evidence.

## Files

- `experiment-note.md` — pre-registered candidate design (written
  before editing).
- `semantic-diff.md` — exact edit, 1:1 removal→survival mapping, static
  gate (PASS).
- `control-skeptic.md`, `candidate-skeptic.md` — the two arms.
- `runner.py` — paired, order-randomized Codex CLI runner (fresh
  isolated ephemeral process and empty temp dir per response).
- `canary-responses.json` — all 36 raw responses with runtime metadata,
  schedule, per-run token usage and timing.
- `score_canary.py`, `canary-scores.json` — per-response frozen Scorer
  V2 scoring and pre-registered early-rejection evaluation.
- `blind-packet.json`, `blind-key.json`, `judgments.json`,
  `reveal.json` — blinded paired review, seed 20260724.
- `comparison.json` — Stage 1 controlled comparison summary and
  verdict (`early_rejection`).
- `manual-audit.md` — per-case classification; deep dives on both
  triggers.
- `protected-hashes-before.txt`, `protected-hashes-after.txt` —
  protected-file integrity record.
- `experiment.json` — compact manifest / hashes / verdict.

## Next recommended action

Do not iterate further on receipt-format compression: two experiments
now show the remaining duplication is too small to matter and the file
is effectively deduplicated in this dimension. If footprint reduction
remains a goal, the two candidates worth a properly scoped experiment
are (a) revising the two over-narrow scorer concept patterns (a
measurement fix, prerequisite to any future hard-gate use), and (b) the
Section 18 tag-legend restatement of Sections 3 and 5 (~50 lines), a
different conceptual change requiring its own pre-registered
experiment.
