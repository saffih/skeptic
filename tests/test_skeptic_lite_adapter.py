from pathlib import Path
import unittest

ROOT = Path(".")
MAIN = Path("skeptic.md").read_text(encoding="utf-8")
LITE = Path("skeptic-lite.md").read_text(encoding="utf-8")


class SkepticLiteAdapterTests(unittest.TestCase):
    def test_lite_file_exists_and_is_non_authoritative(self):
        self.assertIn("small adapter for quick triage", LITE)
        self.assertIn("not the runtime source of truth", LITE)
        self.assertIn("Read the actual current `skeptic.md`", LITE)
        self.assertIn("Do not use this file as a substitute for `skeptic.md`.", LITE)

    def test_lite_preserves_full_skeptic_contract_boundary(self):
        self.assertIn("`RunSkeptic` is the formal invocation string", MAIN)
        self.assertIn("Treat `skeptic.md` as the runtime source of truth.", MAIN)
        self.assertIn("Apply the current recipe exactly and in order.", MAIN)

    def test_lite_has_minimal_effective_flow(self):
        for marker in [
            "Gate",
            "Map",
            "Thinker Pass",
            "Stabilize",
            "Decide",
            "Act and Verify",
            "Output: HANDLED or CONFLICT.",
        ]:
            self.assertIn(marker, LITE)

    def test_lite_blocks_unsafe_old_wording(self):
        forbidden = [
            "multiple valid interpretations -> enumerate before proceeding",
            "Verification is pass/fail. If fail, return to Act.",
            "assumptions about intent and approach are explicit",
        ]
        present = [marker for marker in forbidden if marker in LITE]
        self.assertEqual(present, [])

    def test_lite_keeps_corrected_andrei_guardrails(self):
        for marker in [
            "intent, assumptions, and approach explicit enough to test",
            "Act only after DECIDE=FIX.",
            "retry only with a new observed reason that makes retry safer; otherwise CONFLICT",
        ]:
            self.assertIn(marker, LITE)

    def test_lite_keeps_pattern_classification_short_form(self):
        for marker in [
            "Repeated findings are candidate patterns, not proven patterns.",
            "shared rule, boundary, lifecycle point",
            "why they may not be one pattern",
        ]:
            self.assertIn(marker, LITE)

    def test_heavy_experimental_payload_removed(self):
        self.assertFalse((ROOT / "harness").exists())
        self.assertFalse((ROOT / "skeptic-compact.md").exists())


if __name__ == "__main__":
    unittest.main()
