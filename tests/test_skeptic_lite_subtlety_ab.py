from pathlib import Path
import unittest

# Stable A baseline: the previous lite adapter before the explicit Subtlety Delegate.
# Keep this embedded so the test is idempotent and does not depend on a temp "before" file.
A_BASELINE = """
# Skeptic Lite Adapter

Small triage adapter. Not the runtime source of truth.

Rules:
- Read the actual current `skeptic.md` before claiming RunSkeptic compliance.
- Do not use this file as a substitute for `skeptic.md`.
- Use this only for quick triage: STOP, DECOMPOSE, INTEGRATE, CONFLICT, FIX, or FULL SKEPTIC.

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

3. Thinkers
- CH: what breaks downstream, and what must stay connected?
- OM: what is unnecessary or missing?
- FE: what is true now and verified?
- PO: what would prove this wrong or unsafe?
- KT: should this pattern exist everywhere?
- SH: should we split, integrate, or expose a conflict?

4. Stabilize
- Do not decide on raw findings.
- Repeated findings are candidate patterns, not proven patterns.
- Before grouping, state the shared rule, boundary, lifecycle point, and why they may not be one pattern.
- Before splitting, state what coherence, source of truth, owner, contract, or feedback loop must survive.

5. Decide
- FIX only when root cause, source of truth, owner/contract, reversibility, and verification path are clear.
- DECOMPOSE when scope is large but structure is clear and the split preserves required connections.
- INTEGRATE when split parts must stay together for source of truth, lifecycle coherence, ownership, contract, or feedback loop.
- CONFLICT when owner, source of truth, contract, intent, safety, or confidence is unclear.
- FULL SKEPTIC when risk is high, evidence is weak, domains interact, or the result looks suspiciously clean.

6. Act and Verify
- Act only after DECIDE=FIX.
- Apply the smallest reversible change.
- If verification fails, preserve evidence, revert unsafe partial state, and retry only with a new observed reason that makes retry safer; otherwise CONFLICT.

Output: HANDLED or CONFLICT.
"""

B = Path("skeptic-lite.md").read_text(encoding="utf-8")


class SkepticLiteSubtletyABTests(unittest.TestCase):
    def test_b_adds_subtlety_delegate(self):
        self.assertNotIn("Subtlety Delegate", A_BASELINE)
        self.assertIn("Subtlety Delegate", B)

    def test_b_limits_lite_to_obvious_low_risk_reversible_cases(self):
        marker = "Lite may handle only obvious, low-risk, reversible cases with a clear verification path."
        self.assertNotIn(marker, A_BASELINE)
        self.assertIn(marker, B)

    def test_b_routes_hidden_coupling_to_full_skeptic(self):
        self.assertNotIn("dependency or coupling", A_BASELINE)
        self.assertIn("dependency or coupling", B)
        self.assertIn("Stop Lite and run full `skeptic.md`", B)

    def test_b_routes_source_of_truth_owner_contract_drift(self):
        self.assertNotIn("source-of-truth, owner, or contract drift", A_BASELINE)
        self.assertIn("source-of-truth, owner, or contract drift", B)

    def test_b_routes_indirect_downstream_effects(self):
        self.assertNotIn("indirect downstream effects", A_BASELINE)
        self.assertIn("indirect downstream effects", B)

    def test_b_routes_weak_verification_to_full_skeptic(self):
        self.assertNotIn("weak or missing verification", A_BASELINE)
        self.assertIn("weak or missing verification", B)

    def test_b_routes_repeated_unclear_symptoms_to_full_skeptic(self):
        self.assertNotIn("repeated symptoms with unclear shared cause", A_BASELINE)
        self.assertIn("repeated symptoms with unclear shared cause", B)

    def test_b_routes_silent_failure_to_full_skeptic(self):
        self.assertNotIn("silent failure", A_BASELINE)
        self.assertIn("silent failure", B)

    def test_b_routes_suspiciously_clean_results_to_full_skeptic(self):
        self.assertNotIn("suspiciously clean results", A_BASELINE)
        self.assertIn("suspiciously clean results", B)

    def test_b_keeps_integrate_force(self):
        self.assertIn("INTEGRATE", B)
        self.assertIn("what must stay connected", B)


if __name__ == "__main__":
    unittest.main()
