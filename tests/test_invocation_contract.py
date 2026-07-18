# made by AI
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKEPTIC = ROOT / "skeptic.md"


class InvocationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SKEPTIC.read_text(encoding="utf-8")

    def test_invocation_contract_exists(self) -> None:
        self.assertIn("## Invocation Contract", self.text)
        self.assertIn("`RunSkeptic` is the formal invocation string", self.text)
        self.assertIn("`beskeptic`", self.text)
        self.assertIn("`run skeptic.md`", self.text)

    def test_runskeptic_requires_actual_current_file(self) -> None:
        self.assertIn(
            "Read the actual current `skeptic.md`, or an explicitly supplied candidate Skeptic file, before analysis.",
            self.text,
        )
        self.assertIn("Do not use memory, summaries, previous variants, or generated replacements as substitutes.", self.text)
        self.assertIn("Treat the source under review as the runtime source of truth.", self.text)

    def test_runskeptic_requires_exact_recipe_and_evidence(self) -> None:
        self.assertIn("Apply the current recipe exactly and in order.", self.text)
        self.assertIn("Consider every Thinker required by this file.", self.text)
        self.assertIn("Show which major Skeptic steps were run.", self.text)
        self.assertIn("Show evidence for material findings.", self.text)
        self.assertIn("Use the exact output categories from this file.", self.text)

    def test_runskeptic_protects_file_modification(self) -> None:
        self.assertIn("Do not modify files unless DECIDE says FIX and edits are explicitly allowed.", self.text)
        self.assertIn("Verify the recommendation against the framework.", self.text)
        self.assertIn("State unresolved conflicts, unknowns, skipped areas, and missing evidence.", self.text)

    def test_runskeptic_unavailable_file_rule(self) -> None:
        self.assertIn("If the source under review is unavailable, say so", self.text)
        self.assertIn("do not claim RunSkeptic/Skeptic compliance", self.text)

    def test_self_work_invariant_exists(self) -> None:
        self.assertIn("For Skeptic self-work, read the authoritative current `skeptic.md`", self.text)
        self.assertIn("Do not claim RunSkeptic/Skeptic compliance if the source under review was unavailable or not applied exactly.", self.text)

    def test_current_framework_output_categories_remain_unchanged(self) -> None:
        self.assertIn("Every task ends as HANDLED or CONFLICT.", self.text)
        self.assertIn("PASS", self.text)
        self.assertIn("ACTION", self.text)
        self.assertIn("CONFLICT", self.text)

    def test_idempotent_markers_are_not_duplicated(self) -> None:
        self.assertEqual(self.text.count("## Invocation Contract"), 1)
        self.assertEqual(self.text.count("For Skeptic self-work, read the authoritative current `skeptic.md`"), 1)
        self.assertEqual(self.text.count("`RunSkeptic` is the formal invocation string"), 1)

    def test_runskeptic_receipt_exists(self) -> None:
        for marker in [
            "### RunSkeptic Receipt",
            "Every RunSkeptic report must include a compact receipt:",
            "Source read: path/ref/SHA or explicit unavailable state",
            "Companion files read, if any",
            "Permission mode: read-only / patch-local / fix-if-valid",
            "DONE statement",
            "Prompt review level and task feasibility, when applicable",
            "Major steps run",
            "Thinkers considered",
            "Evidence used",
            "Decision path",
            "Verification performed",
            "Unresolved conflicts / unknowns",
            "Final output category",
            "Do not claim RunSkeptic compliance without this receipt.",
        ]:
            self.assertIn(marker, self.text)

    def test_runskeptic_receipt_is_not_duplicated(self) -> None:
        self.assertEqual(self.text.count("### RunSkeptic Receipt"), 1)
        self.assertEqual(self.text.count("Do not claim RunSkeptic compliance without this receipt."), 1)


if __name__ == "__main__":
    unittest.main()
