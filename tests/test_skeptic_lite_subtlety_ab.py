from pathlib import Path
import unittest

BEFORE = Path.home().joinpath("Downloads/skeptic_lite_before_subtlety.md").read_text(encoding="utf-8")
AFTER = Path("skeptic-lite.md").read_text(encoding="utf-8")


class SkepticLiteSubtletyABTests(unittest.TestCase):
    def test_b_adds_subtlety_delegate(self):
        self.assertNotIn("Subtlety Delegate", BEFORE)
        self.assertIn("Subtlety Delegate", AFTER)

    def test_b_limits_lite_to_obvious_low_risk_reversible_cases(self):
        marker = "Lite may handle only obvious, low-risk, reversible cases with a clear verification path."
        self.assertNotIn(marker, BEFORE)
        self.assertIn(marker, AFTER)

    def test_b_routes_hidden_coupling_to_full_skeptic(self):
        self.assertIn("dependency or coupling", AFTER)
        self.assertIn("Stop Lite and run full `skeptic.md`", AFTER)

    def test_b_routes_weak_verification_to_full_skeptic(self):
        self.assertIn("weak or missing verification", AFTER)

    def test_b_routes_repeated_unclear_symptoms_to_full_skeptic(self):
        self.assertIn("repeated symptoms with unclear shared cause", AFTER)

    def test_b_routes_silent_failure_to_full_skeptic(self):
        self.assertIn("silent failure", AFTER)

    def test_b_routes_suspiciously_clean_results_to_full_skeptic(self):
        self.assertIn("suspiciously clean results", AFTER)

    def test_b_keeps_integrate_force(self):
        self.assertIn("INTEGRATE", AFTER)
        self.assertIn("what must stay connected", AFTER)


if __name__ == "__main__":
    unittest.main()
