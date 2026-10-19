# Install Skeptic RC with V5/V6 comparison

Owner-experimental configuration. The public distribution source is **`saffih/skeptic@RC`**, not public `main`. The public `RC` contains V6 in `skeptic.md`, V5 in `skeptic-v5.md`, plus `runskeptic-dual.md` and the optional `decision-frontier.md`.

To activate in an assistant capable of reading GitHub and creating **two independent semantic invocations**, install this user preference:

```text
For my "RunSkeptic" requests, use the experimental dual review
described at:
https://github.com/saffih/skeptic/blob/RC/runskeptic-dual.md

Freshly read:
V5: https://github.com/saffih/skeptic/blob/RC/skeptic-v5.md
V6: https://github.com/saffih/skeptic/blob/RC/skeptic.md

Run genuinely independent, read-only V5 and V6 arms for the same
bound input whenever independently isolated execution is available.
Prefer V6 for the user-facing candidate answer, but preserve V5
findings and make any material disagreement explicit. Do not
count duplicate same-context role-play as independent evidence.

If two isolated runs or a required source cannot be obtained,
clearly disclose that dual review was NOT performed; do not claim
a paired result or a logged observation. Never silently fall back
to another runtime. Do not change the default public main branch.

For "RunSkeptic RC", run only V6 using the above RC skeptic.md.
For "Skeptic Grill: <task>" (alias "Decision Frontier RC: <task>"),
read the V6 RC skeptic.md above plus
https://github.com/saffih/skeptic/blob/RC/decision-frontier.md
and apply stage-necessary questioning with explicitly noted material
deferrals and their reopening conditions.

Record comparison outcomes only through a verified, authorized
write to Hartal's evidence ledger. No automatic background
capture or persistent user binding is implied by this file.
Neither mode authorizes edits, publication or promotion.
```

If the receiving environment lacks a persistent instruction mechanism, this binding lasts only while supplied in its active session or task. Both `RC` URLs are moving refs; bind exact commit and Git blob identities for reproducibility.
