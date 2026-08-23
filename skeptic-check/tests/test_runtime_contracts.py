from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEXT = (ROOT / "skeptic.md").read_text(encoding="utf-8")


class RuntimeContractTests(unittest.TestCase):
    def test_invocation_contract(self):
        for marker in [
            "## Invocation Contract",
            "`RunSkeptic` is the formal invocation string",
            "Read the actual current `skeptic.md`, or an explicitly supplied candidate Skeptic file, before analysis.",
            "Do not use memory, summaries, previous variants, or generated replacements as substitutes.",
            "Treat the source under review as the runtime source of truth.",
            "Apply the current recipe exactly and in order.",
            "Consider every Thinker required by this file.",
            "Do not modify files unless DECIDE says FIX and edits are explicitly allowed.",
        ]:
            self.assertIn(marker, TEXT)

    def test_receipt_and_output_contract(self):
        for marker in [
            "### RunSkeptic Receipt",
            "Do not claim RunSkeptic compliance without this receipt.",
            "Every task ends as HANDLED or CONFLICT.",
        ]:
            self.assertIn(marker, TEXT)

    def test_decision_and_promotion_contract(self):
        for marker in ["### FIX", "### DECOMPOSE", "### CONFLICT", "### Promotion Check"]:
            self.assertIn(marker, TEXT)
        self.assertIn("If yes, do not promote. Decide FIX, DECOMPOSE, or CONFLICT.", TEXT)
        self.assertIn("Act only after DECIDE says FIX.", TEXT)
        self.assertIn("Do not decide on raw findings.", TEXT)

    def test_ambiguity_assumption_and_scope_guardrails(self):
        for marker in [
            "intent, assumptions, and chosen approach are explicit enough to test",
            "multiple valid interpretations -> list them; proceed only if one is evidence-backed, low-risk, and testable",
            "unresolved or unsafe ambiguity -> CONFLICT",
            "assumptions, including intent and approach assumptions; challenge them before DECIDE",
            "Does this solve a current verified need, or speculate about a future one?",
            "why this is the smallest change that solves the verified issue without broadening scope",
            "no speculative code for unverified future requirements",
            "no premature abstraction unless a current concrete need requires it",
            "follow existing style and conventions unless that style is the verified problem",
            "no out-of-scope edits; log unrelated improvements separately",
        ]:
            self.assertIn(marker, TEXT)

    def test_failed_verification_does_not_blind_loop(self):
        self.assertIn("Do not proceed to another task until the current change is verified or safely reverted.", TEXT)
        self.assertIn("Verification is pass/fail.", TEXT)
        self.assertIn(
            "If fail, preserve evidence, revert unsafe partial state, and retry only with a new observed reason that makes retry safer; otherwise CONFLICT.",
            TEXT,
        )

    def test_additive_focus_contract(self):
        for marker in ["Within the bound scope", "additional adversarial attention", "without narrowing the otherwise applicable review"]:
            self.assertIn(marker, TEXT)

    def test_normative_warrant_keeps_permission_separate(self):
        line = next(line for line in TEXT.splitlines() if "the applicable normative basis:" in line)
        for marker in ["requirement", "contract", "design", "policy", "Skeptic-owned rule"]:
            self.assertIn(marker, line)
        self.assertNotIn("permission", line)
        self.assertIn("the established current fact and evidence that conflict with that normative basis", TEXT)
        self.assertIn("Runs are read-only unless fixing is explicitly authorized", TEXT)

    def test_verification_is_explicit_risk_derived_and_resettable(self):
        for marker in [
            "explicit target number of material checks",
            "do not use a universal quota",
            "reset the count to zero",
            "re-derive the target",
            "checks that directly exercise the intended result and material preserved constraints",
            "consequence",
            "dependency reach",
            "irreversibility",
            "uncertainty",
            "trust elevation",
            "claim strength",
            "pre-mortem: when risk warrants it, address materially plausible failure modes before action",
        ]:
            self.assertIn(marker, TEXT)
        self.assertNotIn("3-5 targeted spot checks", TEXT)
        self.assertNotIn("3 concrete failure modes", TEXT)

    def test_existing_boundary_safety_contract_remains(self):
        for marker in [
            "clean scan is not proof of safety",
            "Never treat no findings as proof of safety",
            "Never treat clean top-down scan as proof of safety",
            "What depends on it, and what does it depend on?",
        ]:
            self.assertIn(marker, TEXT)


if __name__ == "__main__":
    unittest.main()
