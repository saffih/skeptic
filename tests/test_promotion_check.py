from pathlib import Path
import unittest

TEXT = Path("skeptic.md").read_text(encoding="utf-8")


class PromotionCheckTests(unittest.TestCase):
    def test_promotion_check_exists(self):
        self.assertIn("### Promotion Check", TEXT)

    def test_promotion_check_blocks_unresolved_blockers(self):
        self.assertIn(
            "Before marking anything ready, approved, or safe to proceed, check whether any ACTION, DECOMPOSE, CONFLICT, review-required status, or blocking unknown remains unresolved.",
            TEXT,
        )
        self.assertIn(
            "If yes, do not promote. Decide FIX, DECOMPOSE, or CONFLICT.",
            TEXT,
        )

    def test_promotion_invariant_exists(self):
        self.assertIn(
            "Never mark an artifact ready while ACTION, DECOMPOSE, CONFLICT, review-required status, or blocking unknown remains unresolved.",
            TEXT,
        )

    def test_exact_decision_categories_preserved(self):
        for marker in [
            "### FIX",
            "### DECOMPOSE",
            "### CONFLICT",
        ]:
            self.assertIn(marker, TEXT)
        self.assertNotIn("### DECOMPOSE_MORE", TEXT)
        self.assertNotIn("### PROMOTE", TEXT)

    def test_core_contract_preserved(self):
        for marker in [
            "`RunSkeptic` is the formal invocation string",
            "Treat the source under review as the runtime source of truth.",
            "Apply the current recipe exactly and in order.",
            "Every task ends as HANDLED or CONFLICT.",
        ]:
            self.assertIn(marker, TEXT)


if __name__ == "__main__":
    unittest.main()
