from pathlib import Path
import unittest

TEXT = Path("skeptic.md").read_text(encoding="utf-8")


class PatternClassificationScenarioTests(unittest.TestCase):
    def test_same_bug_repeated_requires_shared_rule_and_boundary(self):
        self.assertIn("shared rule, root cause, or violated invariant", TEXT)
        self.assertIn("boundary: included, excluded, uncertain", TEXT)

    def test_same_symptom_different_root_causes_is_challenged(self):
        self.assertIn("why they may not be one pattern", TEXT)
        self.assertIn("Promote only if the rule and boundary survive challenge.", TEXT)

    def test_public_internal_risk_difference_is_supported_by_risk_tiers(self):
        self.assertIn("split risk tiers if needed", TEXT)

    def test_hidden_exception_must_be_listed(self):
        self.assertIn("list exceptions", TEXT)

    def test_lifecycle_context_is_required(self):
        self.assertIn("lifecycle point", TEXT)

    def test_action_is_not_allowed_during_stabilize(self):
        self.assertIn("plan action only after DECIDE=FIX", TEXT)
        self.assertIn("Never use Pattern Classification to act before DECIDE=FIX.", TEXT)

    def test_batching_by_surface_similarity_is_forbidden(self):
        for word in ["wording", "location", "file shape", "symptom"]:
            self.assertIn(word, TEXT)

    def test_no_heavy_expanded_variant_leaked_into_core(self):
        forbidden = [
            "For every \"compatible\" claim",
            "verify representative cases, edge cases, highest-risk tier",
            "Pattern Handling stabilizes and plans",
            "Promote a candidate to a stabilized pattern only when an evidence-backed shared treatment rule can be stated",
        ]
        present = [marker for marker in forbidden if marker in TEXT]
        self.assertEqual(present, [])


if __name__ == "__main__":
    unittest.main()
