from pathlib import Path
import unittest

TEXT = Path("skeptic.md").read_text(encoding="utf-8")


class PromotionCheckScenarioTests(unittest.TestCase):
    def test_ready_but_architecture_review_required_is_blocked(self):
        self.assertIn("review-required status", TEXT)
        self.assertIn("do not promote", TEXT)

    def test_ready_but_action_open_is_blocked(self):
        self.assertIn("ACTION", TEXT)
        self.assertIn("do not promote", TEXT)

    def test_ready_but_conflict_open_is_blocked(self):
        self.assertIn("CONFLICT", TEXT)
        self.assertIn("do not promote", TEXT)

    def test_ready_but_blocking_unknown_open_is_blocked(self):
        self.assertIn("blocking unknown", TEXT)
        self.assertIn("do not promote", TEXT)

    def test_promotion_failure_returns_to_existing_decisions(self):
        self.assertIn("Decide FIX, DECOMPOSE, or CONFLICT.", TEXT)

    def test_rule_is_not_hldspec_specific(self):
        forbidden = [
            "HLDspec",
            "spec_build_plan",
            "architecture findings are dispositioned",
            "DEMOTE_TO_CONTEXT",
            "MERGE_WITH_SPEC",
            "REFERENCE_ONLY",
        ]
        present = [marker for marker in forbidden if marker in TEXT]
        self.assertEqual(present, [])


if __name__ == "__main__":
    unittest.main()
