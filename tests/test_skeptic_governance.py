# made by AI
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKEPTIC = ROOT / "skeptic.md"
GOVERNANCE = ROOT / "skeptic-tests.md"


class SkepticGovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skeptic = SKEPTIC.read_text(encoding="utf-8")
        cls.governance = GOVERNANCE.read_text(encoding="utf-8")

    def test_governance_file_exists_and_is_external(self) -> None:
        self.assertTrue(GOVERNANCE.exists())
        self.assertIn("Skeptic Tests - Governance", self.governance)
        self.assertIn("`skeptic.md` remains the runtime source of truth.", self.governance)
        self.assertIn("It is not mandatory runtime context.", self.governance)

    def test_change_acceptance_rule_exists(self) -> None:
        for marker in [
            "Change",
            "Why",
            "Risk",
            "Section Test",
            "Full-Flow Test",
            "Skeptic Self-Review",
            "Accept / Reject Decision",
        ]:
            self.assertIn(marker, self.governance)

    def test_full_flow_cases_exist(self) -> None:
        for marker in [
            "Trivial typo/comment edit",
            "Unclear requirement",
            "Large repo-wide change",
            "Source-of-truth conflict",
            "API/interface change",
            "Security/input/parser change",
            "Test-only change where the test was never red",
            "Architecture tradeoff with unclear owner",
            "Silent failure risk",
            "Repeated local fixes",
        ]:
            self.assertIn(marker, self.governance)

    def test_reject_conditions_preserve_current_skeptic_safety(self) -> None:
        for marker in [
            "safety regresses",
            "a required Thinker is skipped",
            "raw findings become decisions",
            "inferred risk is reported as confirmed bug",
            "action can occur before stabilization",
            "action can occur without DECIDE=FIX",
            "human-owned decisions are hidden",
            "companion files override `skeptic.md` runtime authority",
        ]:
            self.assertIn(marker, self.governance)

    def test_evidence_rule_uses_current_framework_levels(self) -> None:
        for marker in ["OBSERVED", "REPRODUCED", "HISTORICAL", "INFERRED RISK"]:
            self.assertIn(marker, self.skeptic)
            self.assertIn(marker, self.governance)

    def test_runtime_output_categories_are_preserved(self) -> None:
        self.assertIn("Every task ends as HANDLED or CONFLICT.", self.skeptic)
        self.assertIn("full Skeptic ends as HANDLED or CONFLICT", self.governance)
        self.assertIn("Razor ends as PASS, ACTION, or CONFLICT", self.governance)

    def test_runtime_authority_is_not_overridden(self) -> None:
        self.assertIn("Runtime core is authoritative.", self.skeptic)
        self.assertIn("Runtime behavior belongs in `skeptic.md`.", self.governance)
        self.assertIn("companion files apply", self.governance)

    def test_minimal_patch_rule_exists(self) -> None:
        self.assertIn("Prefer the smallest patch", self.governance)
        self.assertIn("Do not rewrite `skeptic.md`", self.governance)

    def test_test_before_merge_rule_exists(self) -> None:
        for marker in [
            "Run targeted tests",
            "Run full unittest discovery",
            "Show git status",
            "Show diff",
            "Report unresolved conflicts and missing evidence",
        ]:
            self.assertIn(marker, self.governance)


if __name__ == "__main__":
    unittest.main()
