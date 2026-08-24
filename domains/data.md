# Data / I/O (DAT)

Detection aid only. `skeptic.md` owns timing, stabilization, decisions, action, and verification.

DAT1. Every external call, such as subprocess, network, or DB, timed out?
DAT2. Race condition? Locks minimal and correct?
DAT3. What happens when disk is full or filesystem is read-only?
DAT4. Encoding explicit, such as UTF-8, or assumed?
DAT5. Where is this data authored?
DAT6. How often is it updated relative to reality?
DAT7. Who consumes it, and is consistency preserved over time?
