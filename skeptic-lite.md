# Skeptic Lite Adapter

Small triage adapter. Not the runtime source of truth.

Rules:
- Read the actual current `skeptic.md` before claiming RunSkeptic compliance.
- Do not use this file as a substitute for `skeptic.md`.
- Use this only for quick triage: STOP, DECOMPOSE, INTEGRATE, CONFLICT, FIX, or FULL SKEPTIC.
- Lite may handle only obvious, low-risk, reversible cases with a clear verification path.

## Lite Flow

1. Gate
- DONE testable?
- scope tractable?
- wrong-answer cost acceptable?
- intent, assumptions, and approach explicit enough to test?
- If not: STOP, DECOMPOSE, or CONFLICT.

2. Map
For the main entity:
- purpose
- dependencies
- invariant
- source of truth / owner / contract
- what must stay connected
- failure mode and failure signal
- verification path

3. Subtlety Delegate
Stop Lite and run full `skeptic.md` if the issue may hide:
- dependency or coupling
- source-of-truth, owner, or contract drift
- indirect downstream effects
- weak or missing verification
- repeated symptoms with unclear shared cause
- cross-domain impact
- silent failure
- suspiciously clean results

4. Thinkers
- CH: what breaks downstream, and what must stay connected?
- OM: what is unnecessary or missing?
- FE: what is true now and verified?
- PO: what would prove this wrong or unsafe?
- KT: should this pattern exist everywhere?
- SH: should we split, integrate, or expose a conflict?

5. Stabilize
- Do not decide on raw findings.
- Repeated findings are candidate patterns, not proven patterns.
- Before grouping, state the shared rule, boundary, lifecycle point, and why they may not be one pattern.
- Before splitting, state what coherence, source of truth, owner, contract, or feedback loop must survive.

6. Decide
- FIX only when root cause, source of truth, owner/contract, reversibility, and verification path are clear.
- DECOMPOSE when scope is large but structure is clear and the split preserves required connections.
- INTEGRATE when split parts must stay together for source of truth, lifecycle coherence, ownership, contract, or feedback loop.
- CONFLICT when owner, source of truth, contract, intent, safety, or confidence is unclear.
- FULL SKEPTIC when risk is high, evidence is weak, domains interact, the result looks suspiciously clean, or the Subtlety Delegate triggers.

7. Act and Verify
- Act only after DECIDE=FIX.
- Apply the smallest reversible change.
- If verification fails, preserve evidence, revert unsafe partial state, and retry only with a new observed reason that makes retry safer; otherwise CONFLICT.

Output: HANDLED or CONFLICT.
