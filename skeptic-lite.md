# Skeptic Lite Adapter

This file is a small adapter for quick triage. It is not the runtime source of truth.

Rules:
- Read the actual current `skeptic.md` before claiming RunSkeptic compliance.
- Do not use this file as a substitute for `skeptic.md`.
- Use this only to decide whether to STOP, DECOMPOSE, CONFLICT, or continue to full Skeptic.

## Lite Flow

1. Gate
- Is DONE testable?
- Is scope tractable?
- Is wrong-answer cost acceptable?
- Are intent, assumptions, and approach explicit enough to test?
- If not: STOP, DECOMPOSE, or CONFLICT.

2. Map
For the main entity, ask:
- What is it for?
- What depends on it?
- What must always be true?
- What breaks it?
- How do we know it works?

3. Thinker Pass
- CH: what breaks downstream?
- OM: what is unnecessary or missing?
- FE: what is true now and verified?
- PO: what would prove this wrong or unsafe?
- KT: should this pattern exist everywhere?
- SH: what tradeoff or conflict must be explicit?

4. Stabilize
- Do not decide on raw findings.
- Repeated findings are candidate patterns, not proven patterns.
- Before grouping them, state the shared rule, boundary, lifecycle point, and why they may not be one pattern.

5. Decide
- FIX only if root cause, source of truth, reversibility, and verification path are clear.
- DECOMPOSE if scope is large but structure is clear.
- CONFLICT if owner, source of truth, contract, design intent, or confidence is unclear.

6. Act and Verify
- Act only after DECIDE=FIX.
- Apply the smallest reversible change.
- If verification fails, preserve evidence, revert unsafe partial state, and retry only with a new observed reason that makes retry safer; otherwise CONFLICT.

Output: HANDLED or CONFLICT.
