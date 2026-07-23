# Experiment note — footprint-report-prose-v1

## Exact repetition identified

`skeptic.md`'s "Invocation Contract" numbered list (lines 20-33) and the
immediately-following "RunSkeptic Receipt" section (lines 35-53) both
enumerate the same reporting obligations for one invocation:

- Invocation Contract item 7: "Show which major Skeptic steps were run."
  duplicates Receipt field "Major steps run".
- Invocation Contract item 8: "Show evidence for material findings."
  duplicates Receipt field "Evidence used".
- Invocation Contract item 12: "State unresolved conflicts, unknowns,
  skipped areas, and missing evidence." duplicates Receipt field
  "Unresolved conflicts / unknowns" (and the CONFLICTS output category's
  "missing evidence" requirement in section 8, Evidence Levels).

Items 6 ("Consider every Thinker required by this file") and 9 ("Use the
exact output categories from this file") are explicitly out of scope: they
are behavioral requirements (what to *do*), not reporting instructions
about what to *show* in the receipt, and are not restated verbatim by the
receipt field list.

## Why this is semantically redundant

The Receipt section, two paragraphs below the Invocation Contract, already
normatively requires this exact content ("Major steps run", "Evidence
used", "Unresolved conflicts / unknowns" as compact receipt fields) and
already enforces it independently ("Do not claim RunSkeptic compliance
without this receipt."). Items 7, 8, and 12 restate, in imperative prose,
obligations the Receipt section already states and already enforces as a
structural field list. Removing the prose duplicate does not remove the
requirement — the requirement survives intact in the Receipt section,
which is the more precise and already-enforced statement of it.

## Proposed consolidation

Replace Invocation Contract items 7, 8, and 12 with one cross-reference
item pointing at the Receipt section below, which already defines and
enforces this content. Renumber the surrounding list items accordingly.
No other text in the Invocation Contract, Receipt section, or elsewhere
in the file changes.

## Expected footprint reduction

Approximately 2-3 lines / ~35-45 words removed from a 791-line, 5402-word
file (roughly 0.3-0.6% of total prose). This is a small, narrowly-scoped
reduction by design — the single-variable constraint prohibits a larger
consolidation pass.

## Invariants that must remain unchanged

- All six Thinker families and all current lens/aspect tags.
- The full Receipt field list and its semantics (unchanged, untouched).
- The "do not claim RunSkeptic compliance without this receipt" rule
  (unchanged, untouched).
- Invocation Contract items 1-5, 6, 9, 10, 11, 13 (unchanged in wording
  and meaning; only renumbered if their position shifts).
- Every decision category, output category, evidence level, and
  Invariants-section rule (Section 19 is not touched by this experiment).
- No change to `skeptic-questions.md` companion behavior, gate logic, or
  any Thinker's lens content.

## Principal regression risk

A model reading the consolidated Invocation Contract might, in some
generations, produce a receipt that omits "major steps run" or "evidence
used" content if it treats the cross-reference as advisory rather than
mandatory, since the imperative "Show ..." / "State ..." phrasing is
replaced by a pointer to another section. This is exactly what the
blinded judgment and manual audit (receipt-completeness dimension) are
designed to catch, and is the primary hypothesis this experiment tests.
