# Experiment note — footprint-report-prose-v2

Pre-registered before any edit to `skeptic.md`. Control is `skeptic.md`
at main `534aab276bff65d05b4d3129242d61dc87df4c73` (SHA-256
`18ec8655724fcf1e35238c5fc0547414aa389d999467a2002f9d4e82f59f3169`).

## Relation to rejected v1

v1 replaced Invocation Contract items 7, 8, and 12 with one *generic*
pointer ("Report the content required by the RunSkeptic Receipt below.")
and was rejected on a single-sample run: 2 of 4 critical cases showed
independently-corroborated thinner analysis (scorer + blinded judge),
though receipt compliance stayed 12/12 in both arms and the manual audit
could not exclude single-sample variance. v2 is not the v1 candidate:

1. The reference wording is different — explicitly *mandatory* and
   imperative ("Report through the complete RunSkeptic Receipt below;
   every receipt field is mandatory."), addressing the v1 hypothesis
   that a weak advisory pointer lowers reporting/analysis pressure.
2. The canonical receipt field absorbs IC item 12's full enumeration
   ("skipped areas", "missing evidence") instead of dropping it to
   process-section equivalents only.
3. The same single concept is applied at its second genuine duplication
   site (section 8's two Output-schema restatements), making this a
   define-once-reference-elsewhere structural change rather than a
   deletion of three list items.
4. The test protocol replicates (3 runs per case per arm on six canary
   cases) so a repeated regression is distinguishable from the
   single-sample variance that limited v1's rejection evidence.

## The one conceptual change

**The reporting/receipt format is defined exactly once, in its canonical
schema; duplicated restatements elsewhere become explicit mandatory
references to that schema.**

Canonical schema locations (both already exist; neither moves):

- **RunSkeptic Receipt** section (after the Invocation Contract): the
  compact per-invocation reporting schema, already independently
  enforced ("Do not claim RunSkeptic compliance without this receipt."
  plus the evidence-linkage paragraph).
- **Section 13 Output**: the HANDLED and CONFLICTS item schemas
  ("Each item includes: …").

## Exact duplicated structural blocks

### Site 1 — Invocation Contract items 7, 8, 12 duplicate the Receipt

- Item 7 "Show which major Skeptic steps were run." duplicates receipt
  field "Major steps run".
- Item 8 "Show evidence for material findings." duplicates receipt field
  "Evidence used" plus the receipt paragraph "Material findings must
  point to the evidence that supports them; listing steps or Thinkers
  considered without their material application and evidence does not
  establish RunSkeptic compliance."
- Item 12 "State unresolved conflicts, unknowns, skipped areas, and
  missing evidence." duplicates receipt field "Unresolved conflicts /
  unknowns"; its two extra terms ("skipped areas", "missing evidence")
  are absorbed into that canonical field's label so nothing is demoted
  to a process-only mention.

### Site 2 — Section 8's last two rules duplicate Section 13's schemas

- "HANDLED must include evidence level." duplicates the HANDLED item
  schema field "evidence level" (section 13).
- "CONFLICTS must include missing evidence." duplicates the CONFLICTS
  item schema field "missing evidence" (section 13).

Items 6 ("Consider every Thinker…"), 9 ("Use the exact output
categories…"), 10, 11, and 13 are behavioral requirements, not receipt
restatements, and are out of scope (unchanged apart from renumbering).

## Surviving canonical wording

- Invocation Contract, new item 7: "Report through the complete
  RunSkeptic Receipt below; every receipt field is mandatory."
- Receipt field extended: "Unresolved conflicts / unknowns / skipped
  areas / missing evidence" (was "Unresolved conflicts / unknowns").
- Section 8, replacement rule: "HANDLED and CONFLICTS report these
  classifications through their exact Output item schemas (section 13)."
- Everything else in the Receipt section and Section 13 is
  byte-identical.

## Removed passages and surviving equivalents

| Removed | Surviving equivalent |
|---|---|
| IC 7 "Show which major Skeptic steps were run." | Receipt field "Major steps run" + new mandatory item 7 |
| IC 8 "Show evidence for material findings." | Receipt field "Evidence used" + receipt evidence-linkage paragraph + new mandatory item 7 |
| IC 12 "State unresolved conflicts, unknowns, skipped areas, and missing evidence." | Extended receipt field "Unresolved conflicts / unknowns / skipped areas / missing evidence" + new mandatory item 7 |
| §8 "HANDLED must include evidence level." | §13 HANDLED schema field "evidence level" + §8 reference rule |
| §8 "CONFLICTS must include missing evidence." | §13 CONFLICTS schema field "missing evidence" + §8 reference rule |

## Preserved invariants

- All six Thinker families and every lens/aspect tag (sections 3, 18 —
  untouched).
- All twelve receipt fields (one field label extended, none removed).
- "Do not claim RunSkeptic compliance without this receipt." and the
  receipt evidence-linkage/conflict paragraph — untouched.
- Every decision category (PASS/ACTION/CONFLICT/DECOMPOSE), output
  category (HANDLED, CONFLICTS), and their full item schemas —
  untouched.
- Every evidence level and every other §8 evidence rule (INFERRED RISK,
  FIX requires OBSERVED, vulnerability claims, security escalation) —
  untouched.
- All escalation, gate, promotion-check, and invariant rules (§0, §9,
  §19) — untouched.
- All protections involving dignity/consent (KT), recovery/reversal
  (CH:SM, §10, §11), proportionality (CH:EV, smallest-credible guard),
  safety evidence (OM:FS), and whole-system effects (CH:SO, KT:HB) —
  untouched.
- `skeptic-questions.md` companion behavior — untouched.

## Expected footprint reduction

Approximately −3 lines and −10 to −20 words on 791 lines / 5402 words
(~0.3–0.5%). This is honestly small: outside these two sites, the
reporting/receipt format has no other genuine duplication in the file,
and the instruction "do not delete unique rules merely to meet a
target" dominates the reduction aim. The larger value under test is the
structural pattern itself — whether define-once-plus-mandatory-reference
is behaviorally safe, measured with replication, so future compression
passes can reuse it. (The largest true duplication in the file, the
Section 18 tag legend restating Section 3 and Section 5, is outside the
declared reporting/receipt scope and is deliberately not touched;
recorded as a candidate for a separate experiment.)

## Primary regression risks

1. **Thinner analysis on critical cases** (the v1 rejection signal): a
   consolidated reference may prime less evidence display or fewer
   distinct stabilized findings. Detector: replicated canary on the
   exact v1 regression cases (`unbounded-fix-loop`,
   `coercive-performance-ranking`, `email-shell-execution`) — a repeated
   miss of the same critical concept in ≥2 of 3 runs while control
   retains it rejects early.
2. **Receipt erosion**: a model may treat the referenced schema as
   advisory. Detector: Scorer V2 receipt detection per response;
   any repeated receipt regression rejects.
3. **Loss of "skipped areas"/"missing evidence" reporting**: mitigated
   by absorbing both terms into the canonical field label rather than
   relying on process-section equivalents; checked by blinded review's
   receipt-completeness dimension.
4. **Scorer artifact risk**: the extended field label still matches
   Scorer V2's `unresolved` alias set by prefix ("unresolved …"), and
   none of the edited phrases occurs in any case pattern (checked by
   script before editing; result NONE), so the edit can neither game
   nor spuriously fail the scorer.
