# Phase E — Static contract verification

Method: `git diff skeptic.md` against control (main @
534aab276bff65d05b4d3129242d61dc87df4c73) shows exactly one hunk (lines
24-31 of the Invocation Contract numbered list). Every other line of
`skeptic.md` — including all Thinker sections, tag legend, decision
categories, output categories, receipt field list, invariants, and gate
logic — is byte-identical between control and candidate. Confidence in
this verification therefore rests on the diff scope itself, not manual
per-invariant re-reading.

| Invariant | Location | Status |
|---|---|---|
| All six Thinker families (CH, OM, FE, PO, KT, SH) | Section 3, untouched | preserved |
| All current lens/aspect tags | Section 3, 18, untouched | preserved |
| Evidence requirements | Section 8, untouched | preserved |
| Unsupported-claim handling | FE:PG, FE:WE, PO:OC, untouched | preserved |
| Falsifiability and invalidation | Section PO, untouched | preserved |
| Proportionality | CH:EV, Smallest credible alternative guard, untouched | preserved |
| Recovery and catastrophic-downside priority | CH:SM, Act/Verify sections, untouched | preserved |
| Whole-system and burden-shifting analysis | CH:SO, KT:HB, untouched | preserved |
| Dignity, consent, privacy, retaliation concerns | KT section, untouched | preserved |
| Simplicity and retained safety evidence | OM section, OM:FS, untouched | preserved |
| Stopping and escalation | Gate section, Section 12 (Learn), untouched | preserved |
| All decision labels (PASS/ACTION/CONFLICT/DECOMPOSE/HANDLED) | Sections 9, 13, untouched | preserved |
| All output categories (HANDLED, CONFLICTS) | Section 13, untouched | preserved |
| Every receipt field | RunSkeptic Receipt list, byte-identical (not touched by the edit) | preserved |
| Final synthesis requirements | Section 13, 14, 17, untouched | preserved |

Removed content maps 1:1 to surviving equivalents already present in the
untouched RunSkeptic Receipt section (see `semantic-diff.md`). No
invariant listed above required updating; the edit is confined to four
lines within the Invocation Contract's numbered list.

No ambiguity found. Verdict: proceed to Phase F (does not stop with
`EXPERIMENT_REJECTED_BEFORE_RUN`).
