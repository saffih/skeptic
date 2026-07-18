from pathlib import Path
import subprocess
import unittest

TEXT = Path("skeptic.md").read_text(encoding="utf-8")
MAIN = subprocess.check_output(["git", "show", "origin/main:skeptic.md"], text=True)


class AndreiABVsMain(unittest.TestCase):
    def test_b_has_guardrails_missing_or_weaker_in_a(self):
        markers = [
            "intent, assumptions, and chosen approach are explicit enough to test",
            "multiple valid interpretations -> list them; proceed only if one is evidence-backed, low-risk, and testable",
            "assumptions, including intent and approach assumptions; challenge them before DECIDE",
            "purpose/value gap",
            "why this is the smallest change that solves the verified issue without broadening scope",
            "no speculative code for unverified future requirements",
            "no premature abstraction unless a current concrete need requires it",
            "follow existing style and conventions unless that style is the verified problem",
            "no out-of-scope edits; log unrelated improvements separately",
        ]
        missing = [m for m in markers if m not in TEXT]
        self.assertEqual(missing, [])

    def test_bad_pr_wording_removed(self):
        forbidden = [
            "multiple valid interpretations -> enumerate before proceeding",
            "Verification is pass/fail. If fail, return to Act.",
        ]
        present = [m for m in forbidden if m in TEXT]
        self.assertEqual(present, [])

    def test_main_contract_still_present_in_b(self):
        for marker in [
            "`RunSkeptic` is the formal invocation string",
            "Do not decide on raw findings.",
            "Act only after DECIDE says FIX.",
            "Every task ends as HANDLED or CONFLICT.",
        ]:
            self.assertIn(marker, TEXT)
            self.assertIn(marker, MAIN)


if __name__ == "__main__":
    unittest.main()
