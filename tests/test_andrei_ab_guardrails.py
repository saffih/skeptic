from pathlib import Path
import unittest

TEXT = Path("skeptic.md").read_text(encoding="utf-8")


class AndreiABGuardrails(unittest.TestCase):
    def test_contract_preserved(self):
        for marker in [
            "`RunSkeptic` is the formal invocation string",
            "Treat the source under review as the runtime source of truth.",
            "Apply the current recipe exactly and in order.",
            "Every task ends as HANDLED or CONFLICT.",
        ]:
            self.assertIn(marker, TEXT)

    def test_ambiguity_guardrail_improved(self):
        self.assertIn(
            "multiple valid interpretations -> list them; proceed only if one is evidence-backed, low-risk, and testable",
            TEXT,
        )
        self.assertIn("unresolved or unsafe ambiguity -> CONFLICT", TEXT)
        self.assertNotIn("multiple valid interpretations -> enumerate before proceeding", TEXT)

    def test_assumptions_guardrail_improved(self):
        self.assertIn("intent, assumptions, and chosen approach are explicit enough to test", TEXT)
        self.assertIn("assumptions, including intent and approach assumptions; challenge them before DECIDE", TEXT)

    def test_speculation_scope_and_style_guardrails(self):
        for marker in [
            "purpose/value gap",
            "why this is the smallest change that solves the verified issue without broadening scope",
            "no speculative code for unverified future requirements",
            "no premature abstraction unless a current concrete need requires it",
            "follow existing style and conventions unless that style is the verified problem",
            "no out-of-scope edits; log unrelated improvements separately",
            "Never modify outside the current task's scope; log adjacent issues separately.",
        ]:
            self.assertIn(marker, TEXT)

    def test_failed_verification_no_blind_loop(self):
        self.assertIn("Do not proceed to another task until the current change is verified or safely reverted.", TEXT)
        self.assertIn("Verification is pass/fail.", TEXT)
        self.assertIn(
            "If fail, preserve evidence, revert unsafe partial state, and retry only with a new observed reason that makes retry safer; otherwise CONFLICT.",
            TEXT,
        )
        self.assertNotIn("Verification is pass/fail. If fail, return to Act.", TEXT)


if __name__ == "__main__":
    unittest.main()
