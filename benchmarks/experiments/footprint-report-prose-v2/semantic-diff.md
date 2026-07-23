# Semantic diff — footprint-report-prose-v2

One conceptual change (canonical reporting/receipt schema defined once;
duplicated restatements become explicit mandatory references), applied
at its two genuine duplication sites. Three hunks total; verified by
`git diff main -- skeptic.md` showing no other hunk.

## Site 1 — Invocation Contract numbered list

### Removed → surviving equivalent

| Removed instruction | Surviving text |
|---|---|
| item 7: "Show which major Skeptic steps were run." | Receipt field "Major steps run" (untouched) + new item 7 making every receipt field mandatory reporting |
| item 8: "Show evidence for material findings." | Receipt field "Evidence used" (untouched) + untouched receipt paragraph: "Material findings must point to the evidence that supports them; listing steps or Thinkers considered without their material application and evidence does not establish RunSkeptic compliance." + new item 7 |
| item 12: "State unresolved conflicts, unknowns, skipped areas, and missing evidence." | Receipt field extended in place to "Unresolved conflicts / unknowns / skipped areas / missing evidence" — every one of item 12's four enumerated obligations now lives verbatim in the canonical schema — + new item 7 |

### Added

New item 7: "Report through the complete RunSkeptic Receipt below; every
receipt field is mandatory." This is an explicit, imperative,
mandatory-per-field reference (unlike v1's advisory pointer). It adds no
new obligation: the receipt section already requires and enforces the
same content ("Do not claim RunSkeptic compliance without this
receipt.").

### Renumbering (mechanical, wording identical)

- old 9 → new 8 ("Use the exact output categories from this file.")
- old 10 → new 9 ("Do not modify files unless DECIDE says FIX…")
- old 11 → new 10 ("Verify the recommendation against the framework.")
- old 13 → new 11 ("If the source under review is unavailable…")

## Site 2 — Section 8 Evidence Levels, last two rules

| Removed instruction | Surviving text |
|---|---|
| "HANDLED must include evidence level." | Section 13 HANDLED schema (untouched): "Each item includes: … evidence level …" + replacement rule below |
| "CONFLICTS must include missing evidence." | Section 13 CONFLICTS schema (untouched): "Each item includes: … missing evidence …" + replacement rule below |

### Added

Replacement rule: "HANDLED and CONFLICTS report these classifications
through their exact Output item schemas (section 13)." — keeps the
evidence-classification→reporting binding inside Evidence Levels while
the field definitions live only in section 13.

## Receipt field label extension (Site 1, canonical side)

"Unresolved conflicts / unknowns" → "Unresolved conflicts / unknowns /
skipped areas / missing evidence". No field removed; no field renamed
beyond this absorbing extension; the other eleven receipt fields are
byte-identical. Scorer V2 receipt detection matches this label via the
`unresolved` alias prefix (verified against frozen
`benchmarks/benchmark.py` `_RECEIPT_FIELDS`; scorer not modified).

## Static gate check — every protected element mapped

| Invariant class | Status |
|---|---|
| Six Thinker families, all lens/aspect tags (§3, §18) | untouched, byte-identical |
| Evidence rules: INFERRED RISK handling, FIX requires OBSERVED, vulnerability claims, security escalation (§8) | untouched except the two mapped duplicate lines |
| Evidence levels (OBSERVED/REPRODUCED/HISTORICAL/INFERRED RISK) | untouched |
| Decision categories (FIX/DECOMPOSE/CONFLICT, PASS/ACTION/CONFLICT) | untouched |
| Output categories and item schemas (HANDLED, CONFLICTS, §13) | untouched |
| Receipt fields | all twelve present; one label extended, none removed |
| Receipt enforcement rules (compact-index paragraph, compliance claims) | untouched |
| Escalation/gate rules (§0 gate, promotion check, §12 Learn, CONFLICT paths) | untouched |
| Dignity/consent (KT), recovery (CH:SM, §10–11), proportionality (CH:EV, smallest-credible guard), safety evidence (OM:FS), whole-system effects (CH:SO, KT:HB) | untouched |
| §19 Invariants | byte-identical |
| Companion behavior (`skeptic-questions.md`, `agents/task-prompt.md`) | untouched |

Every removed instruction maps confidently to surviving normative text.
No unique rule, lens, decision, receipt field, or safeguard is lost.
**Static gate: PASS — proceed (not EXPERIMENT_REJECTED_BEFORE_RUN).**

## Deltas

- Control: 791 lines, 5402 words, 36626 bytes, SHA-256
  `18ec8655724fcf1e35238c5fc0547414aa389d999467a2002f9d4e82f59f3169`.
- Candidate: 788 lines, 5400 words, 36613 bytes, SHA-256
  `88536af049187614585f44277b98789f54dbaa7d32babb7c8f2c08beaaed3810`.
- Delta: −3 lines, −2 words, −13 bytes (~0.04% by bytes). The structural
  consolidation is real (five duplicated normative lines become two
  reference lines) but the net textual footprint reduction is very
  small because the mandatory-reference wording and the absorbed field
  enumeration intentionally preserve imperative force; see
  `experiment-note.md` for why the honest in-scope duplication surface
  is this small.
