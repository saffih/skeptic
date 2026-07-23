# Semantic diff — footprint-report-prose-v1

Single conceptual edit, applied to the Invocation Contract numbered list
(`skeptic.md`, "Invocation Contract" section).

## Removed / consolidated

| Removed instruction | Surviving equivalent |
|---|---|
| item 7: "Show which major Skeptic steps were run." | RunSkeptic Receipt field "Major steps run" (unchanged); new item 10, "Report the content required by the RunSkeptic Receipt below." |
| item 8: "Show evidence for material findings." | RunSkeptic Receipt field "Evidence used" (unchanged); enforced further by the receipt's explanatory paragraph ("listing steps or Thinkers considered without their material application and evidence does not establish RunSkeptic compliance"); new item 10 cross-reference. |
| item 12: "State unresolved conflicts, unknowns, skipped areas, and missing evidence." | RunSkeptic Receipt field "Unresolved conflicts / unknowns" (unchanged); CONFLICTS output category already requires "missing evidence" as an item field (section 8/13, unchanged); new item 10 cross-reference. |

## Renumbering (mechanical only, no content change)

Old 9 -> new 7 ("Use the exact output categories from this file.")
Old 10 -> new 8 ("Do not modify files...")
Old 11 -> new 9 ("Verify the recommendation against the framework.")
Old 13 -> new 11 ("If the source under review is unavailable...")

## Added

New item 10: "Report the content required by the RunSkeptic Receipt
below." — a single cross-reference replacing the three removed items.
This does not add a new obligation; the RunSkeptic Receipt section it
points to already normatively requires and enforces the exact content
the three removed items separately restated.

## Not touched

- RunSkeptic Receipt section: field list, "Do not claim RunSkeptic
  compliance without this receipt.", and the explanatory paragraph —
  byte-identical.
- Invocation Contract items 1-6, and old items 9-11, 13 (now 7-9, 11) —
  wording identical, only list position changed for four of them.
- Everything from "Flow: GATE -> ..." (line 53) onward — byte-identical.
- Section 19 Invariants — byte-identical; not part of this experiment.

## Line/word delta

Before: 791 lines, 5402 words, 36626 bytes (SHA-256
18ec8655724fcf1e35238c5fc0547414aa389d999467a2002f9d4e82f59f3169).
After: 789 lines, 5388 words, 36526 bytes (SHA-256
500859af32ce1e24b1246e670f7f78789e5fd0143fe219b37906351623e8d8eb).
Delta: -2 lines, -14 words, -100 bytes (~0.27% smaller by bytes).
