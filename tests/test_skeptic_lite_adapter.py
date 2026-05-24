from pathlib import Path
import unittest

ROOT = Path(".")
MAIN = Path("skeptic.md").read_text(encoding="utf-8")
LITE = Path("skeptic-lite.md").read_text(encoding="utf-8")


class SkepticLiteAdapterTests(unittest.TestCase):
    def test_lite_is_non_authoritative(self):
        for marker in [
            "Small triage adapter. Not the runtime source of truth.",
            "Read the actual current `skeptic.md` before claiming RunSkeptic compliance.",
            "Do not use this file as a substitute for `skeptic.md`.",
        ]:
            self.assertIn(marker, LITE)

    def test_full_runtime_contract_remains_in_main(self):
        for marker in [
            "`RunSkeptic` is the formal invocation string",
            "Treat `skeptic.md` as the runtime source of truth.",
            "Apply the current recipe exactly and in order.",
            "Every task ends as HANDLED or CONFLICT.",
        ]:
            self.assertIn(marker, MAIN)

    def test_lite_has_minimal_triage_outcomes(self):
        for marker in [
            "STOP",
            "DECOMPOSE",
            "INTEGRATE",
            "CONFLICT",
            "FIX",
            "FULL SKEPTIC",
            "HANDLED or CONFLICT",
        ]:
            self.assertIn(marker, LITE)

    def test_lite_limits_itself_to_obvious_low_risk_work(self):
        self.assertIn(
            "Lite may handle only obvious, low-risk, reversible cases with a clear verification path.",
            LITE,
        )

    def test_lite_has_subtlety_delegate(self):
        for marker in [
            "Subtlety Delegate",
            "Stop Lite and run full `skeptic.md`",
            "dependency or coupling",
            "source-of-truth, owner, or contract drift",
            "indirect downstream effects",
            "weak or missing verification",
            "repeated symptoms with unclear shared cause",
            "cross-domain impact",
            "silent failure",
            "suspiciously clean results",
        ]:
            self.assertIn(marker, LITE)

    def test_lite_routes_subtle_cases_to_full_skeptic(self):
        self.assertIn(
            "FULL SKEPTIC when risk is high, evidence is weak, domains interact, the result looks suspiciously clean, or the Subtlety Delegate triggers.",
            LITE,
        )

    def test_lite_covers_important_system_cases(self):
        for marker in [
            "source of truth / owner / contract",
            "what must stay connected",
            "failure mode and failure signal",
            "verification path",
            "owner/contract",
            "risk is high",
            "evidence is weak",
            "domains interact",
            "suspiciously clean",
        ]:
            self.assertIn(marker, LITE)

    def test_lite_has_integrate_force(self):
        for marker in [
            "Before splitting, state what coherence, source of truth, owner, contract, or feedback loop must survive.",
            "DECOMPOSE when scope is large but structure is clear and the split preserves required connections.",
            "INTEGRATE when split parts must stay together for source of truth, lifecycle coherence, ownership, contract, or feedback loop.",
            "SH: should we split, integrate, or expose a conflict?",
        ]:
            self.assertIn(marker, LITE)

    def test_lite_keeps_pattern_classification_minimum(self):
        for marker in [
            "Repeated findings are candidate patterns, not proven patterns.",
            "shared rule, boundary, lifecycle point",
            "why they may not be one pattern",
        ]:
            self.assertIn(marker, LITE)

    def test_lite_blocks_old_unsafe_wording(self):
        forbidden = [
            "multiple valid interpretations -> enumerate before proceeding",
            "Verification is pass/fail. If fail, return to Act.",
            "assumptions about intent and approach are explicit",
        ]
        present = [marker for marker in forbidden if marker in LITE]
        self.assertEqual(present, [])

    def test_lite_keeps_safe_verify_failure_rule(self):
        self.assertIn(
            "preserve evidence, revert unsafe partial state, and retry only with a new observed reason that makes retry safer; otherwise CONFLICT",
            LITE,
        )

    def test_heavy_experimental_payload_removed(self):
        self.assertFalse((ROOT / "harness").exists())
        self.assertFalse((ROOT / "skeptic-compact.md").exists())


if __name__ == "__main__":
    unittest.main()
