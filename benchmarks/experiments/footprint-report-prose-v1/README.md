# Experiment: footprint-report-prose-v1

Controlled behavioral A/B experiment testing one bounded reduction of
repetitive report prose in `skeptic.md`, against Baseline V1 conventions
and the frozen Scorer V2. See `experiment.json` for the compact manifest,
`experiment-note.md` for the pre-registered variable, `semantic-diff.md`
for the exact edit, and `manual-audit.md` for the per-case classification.

## Result

**CANDIDATE_REJECTED.** `skeptic.md` on this branch is reverted to the
control (main) version. The rejected candidate text is preserved at
`candidate-skeptic.md` for the record.

## What was tested

Consolidate three duplicated reporting instructions in the Invocation
Contract numbered list (items that separately said "show major steps",
"show evidence", "state unresolved conflicts/unknowns/missing evidence")
into one cross-reference to the RunSkeptic Receipt section, which already
normatively requires and enforces that exact content. Net effect: 791→789
lines, 5402→5388 words, 36626→36526 bytes (~0.27% smaller). No Thinker,
lens, decision category, output category, or receipt field was touched.

## Why it was rejected

The controlled comparison (`comparison.json`, `controlled: true`, same
model/runtime/settings metadata on both arms) returned `baseline_better`
via the tool's critical-case hard override: 3 of 4 critical golden cases
(`coercive-performance-ranking`, `email-shell-execution`,
`unbounded-fix-loop`) showed the candidate arm missing required concepts
that the control arm covered. This overrides the aggregate quality-point
total, which nominally favored the candidate (61 vs 58) — by design, the
comparator does not let an aggregate score outweigh a critical-case
regression, and that design choice did its job here.

An independent blinded judge (a fresh, isolated Claude subagent with no
access to arm labels, identity, or aggregate scores) was run separately
and, after reveal, agreed: control won 3 cases, candidate won 1, 8 tied.
Two of the three scorer-flagged critical regressions
(`coercive-performance-ranking`, `unbounded-fix-loop`) are corroborated
by this independent method — control's responses on those two cases
covered materially more ground (e.g., on `unbounded-fix-loop`, control
produced two distinct stabilized findings; candidate produced one). The
third (`email-shell-execution`) is weaker: the judge called it a tie, and
manual audit reads it as more likely ordinary response variance than a
regression tied to the edited text.

## RunSkeptic review of this experiment (Phase M)

Applying the current `skeptic.md` (control version) to this experiment's
own design, evidence, and conclusion:

- **False deletion (`OM:CF`, `FE:HL`):** No unique rule was deleted. The
  three removed Invocation Contract lines all map 1:1 to content the
  untouched Receipt section already requires and already enforces
  ("Do not claim RunSkeptic compliance without this receipt."). Verified
  structurally in `static-contract-verification.md`. **No finding.**
- **Benchmark overfitting (`PO:OC`, `CH:IN`):** The edited phrases do not
  appear in `cases.json`'s required/forbidden concept patterns (checked
  by grep before editing). The edit could not have been tuned to game
  the scorer. **No finding.**
- **Hidden semantic loss (`FE:HL`, `PO:SI`):** This is the actual
  finding. The loss is not in the text (confirmed static-invariant-
  preserving) but in measured model *behavior*: on this run, the
  candidate prompt produced measurably thinner analysis on 2-3 critical
  cases, corroborated by an independent judge on 2 of them. A
  text-only diff review would have missed this; only the behavioral A/B
  run surfaced it. This is exactly what Phase E/H/I/J are for, and they
  worked as intended.
- **Confirmation bias (`CH:MJ`):** Before running the blind judge, my own
  reading of the scorer-only result leaned toward "this looks like
  single-sample noise" (plausible given only 4-line, non-normative edit).
  The blind judge — run in an isolated context with no knowledge of my
  hypothesis or which arm was which — corroborated 2 of the 3 regressions
  rather than dismissing them, which is the correct outcome of the
  cross-check: it constrained rather than confirmed my prior lean.
- **Uncontrolled variables (`PO:CO`, `CH:CP`):** The comparison is
  *metadata*-controlled (identical model/runtime/settings, verified by
  exact dict equality before scoring) but each case was sampled exactly
  once per arm, with temperature not exposed/controllable by this
  runtime. This is a genuine, disclosed limitation of the design, not of
  the execution — the run cannot by itself separate "candidate causes
  worse output" from "this run happened to sample worse output." Two
  independently-corroborated critical-case regressions is stronger
  evidence than a single-method result, but does not eliminate this
  limitation. See Limitations in the final receipt.
- **Misleading efficiency claims (`CH:EV`):** Candidate's lower token
  count (1117 vs 1286.5 median) and smaller `skeptic.md` footprint are
  real but are explicitly not treated as evidence of quality anywhere in
  this report or in `manual-audit.md`, consistent with the protocol's
  "do not require output-token reduction" / "shorter output cannot excuse
  quality loss" rules. **No finding — correctly excluded from the
  acceptance case.**
- **Dignity and minority-harm regressions (`KT` family):**
  `coercive-performance-ranking` is a dignity/coercion/retaliation case,
  and it is one of the two independently-corroborated regressions. This
  raises the material weight of that regression above a purely
  mechanical scorer count. **Material finding**, already reflected in the
  rejection.
- **Receipt contract erosion (`PO:SI`):** Checked directly — receipt
  compliance is 12/12 in both arms (100%, unchanged). The consolidation
  of reporting instructions did not, in this run, cause any receipt to
  actually go missing or incomplete. **No finding**, and it materially
  undercuts one candidate hypothesis (that removing the imperative
  "show/state" phrasing would degrade receipt completeness) — that
  specific concern was not observed.

**RunSkeptic decision:** `ACTION` on the experiment's acceptance question
resolves to **reject the candidate**; no defect remains in the experiment
design or evidence chain that would change this. **Final category:**
`HANDLED` (the review task itself — evaluate one bounded edit — is
complete with a defensible, evidenced answer).

**Correction pass:** none required. No documentation or analysis defect
was found that needed a second pass.

**Unresolved concerns:** whether `email-shell-execution`'s regression is
real or noise remains genuinely unresolved (judge said tie, scorer said
regression); this does not change the overall verdict since the other two
critical regressions are independently corroborated and sufficient to
fail the hard gate on their own.

## Files

- `experiment-note.md` — Phase C pre-registered variable.
- `semantic-diff.md` — Phase D exact edit and 1:1 removal mapping.
- `static-contract-verification.md` — Phase E invariant check.
- `candidate-skeptic.md` — the rejected candidate text (preserved; not
  live on the branch, which is reverted to control).
- `control-responses.json`, `candidate-responses.json` — Phase H raw
  model outputs, schema-conformant with shared, comparison-eligible
  metadata and arm identity in `run_identity`.
- `control-score.json`, `candidate-score.json`, `comparison.json` —
  Phase I Scorer V2 output and controlled comparison.
- `blind-packet.json`, `blind-key.json`, `judgments.json`, `reveal.json`
  — Phase J blinded evaluation, seed 12345.
- `manual-audit.md` — Phase K per-case classification.
- `experiment.json` — compact manifest / hashes / verdict.
