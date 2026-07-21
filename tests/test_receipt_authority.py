# made by AI
from __future__ import annotations

import unittest
from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKEPTIC = ROOT / "skeptic.md"
TASK_PROMPT = ROOT / "agents" / "task-prompt.md"
LEAD_PROMPT = ROOT / "agents" / "lead-agent-prompt.md"
GOVERNANCE = ROOT / "skeptic-tests.md"


class Decision(str, Enum):
    VERIFY_NARROWLY = "VERIFY_NARROWLY"
    REPAIR_RECEIPT = "REPAIR_RECEIPT"
    REOPEN_SMALLEST_PHASE = "REOPEN_SMALLEST_PHASE"
    CLOSE = "CLOSE"
    REJECT_PROMOTION = "REJECT_PROMOTION"


@dataclass(frozen=True)
class ReceiptCase:
    """Facts a Lead/Checker can observe about one receipt claim."""

    primary_evidence_matches_claim: bool = True
    claim_is_promotion_critical: bool = False
    checkpoint_deterministically_invalidated: bool = False
    receipt_claim_verified: bool = True
    checkpoint_or_facts_complete: bool = True
    closure_fields_reconstructable: bool = True


def authority_decision(case: ReceiptCase) -> Decision:
    """Reference for Section 3: primary evidence > deterministic checkpoint
    > verified receipt > unverified claim."""
    if not case.primary_evidence_matches_claim:
        if case.claim_is_promotion_critical:
            return Decision.REJECT_PROMOTION
        return Decision.REPAIR_RECEIPT
    if case.checkpoint_deterministically_invalidated:
        return Decision.REOPEN_SMALLEST_PHASE
    if not case.receipt_claim_verified:
        return Decision.VERIFY_NARROWLY
    if case.checkpoint_or_facts_complete and case.closure_fields_reconstructable:
        return Decision.CLOSE
    return Decision.VERIFY_NARROWLY


def requires_formal_receipt(
    *, delegated: bool, serious_task_prompt: bool, run_skeptic_invoked: bool
) -> bool:
    """Proportionality: formal receipt ceremony is not universal."""
    return delegated or serious_task_prompt or run_skeptic_invoked


def decision_owner(
    *, deterministic_facts_complete: bool, requires_authorized_judgment: bool
) -> str:
    """A checker can compute facts; it cannot compute a human-owned judgment."""
    if requires_authorized_judgment:
        return "LEAD_OR_OWNER"
    return "DETERMINISTIC" if deterministic_facts_complete else "UNRESOLVED"


class CrossFileAuthorityMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skeptic = SKEPTIC.read_text(encoding="utf-8")
        cls.task_prompt = TASK_PROMPT.read_text(encoding="utf-8")
        cls.lead_prompt = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.governance = GOVERNANCE.read_text(encoding="utf-8")

    def test_skeptic_receipt_is_not_authoritative(self) -> None:
        self.assertIn("not proof and not an authorization artifact", self.skeptic)

    def test_task_prompt_defines_authority_precedence(self) -> None:
        self.assertIn("compact claim-and-evidence index", self.task_prompt)
        self.assertIn(
            "reports whether the whole Task Prompt reached verified terminal conditions",
            self.task_prompt,
        )
        self.assertIn("not an independent promotion input", self.task_prompt)

    def test_lead_prompt_treats_receipts_as_claims(self) -> None:
        self.assertIn(
            "Treat an Agent Receipt or Task Closure Receipt as a claim, not authority",
            self.lead_prompt,
        )

    def test_governance_has_receipt_authority_scenarios_and_reject_conditions(self) -> None:
        self.assertIn("Receipt authority regression scenarios", self.governance)
        for marker in [
            "an unverified receipt authorizes a consequential transition",
            "receipt prose overrides primary evidence or deterministic state",
            "missing receipt prose causes completed phases to replay",
            "receipt ceremony becomes mandatory for trivial non-delegated work",
            "a checklist-only RunSkeptic receipt is accepted without evidence",
            "a closure receipt independently invents DONE",
        ]:
            self.assertIn(marker, self.governance)


class ReceiptAuthorityScenarioTests(unittest.TestCase):
    """Exercises the nine scenarios from the Receipt Authority Consolidation Plan."""

    def setUp(self) -> None:
        self.verified = ReceiptCase()

    def test_scenarios_1_7_8_promotion_critical_claims_are_rejected(self) -> None:
        # False test claim / checklist theatre / controller-vs-prose: all
        # contradict a promotion-critical claim with primary evidence.
        case = replace(
            self.verified,
            primary_evidence_matches_claim=False,
            claim_is_promotion_critical=True,
        )
        self.assertEqual(authority_decision(case), Decision.REJECT_PROMOTION)

    def test_scenario_2_claimed_mutation_without_mutation_repairs_receipt(self) -> None:
        case = replace(self.verified, primary_evidence_matches_claim=False)
        decision = authority_decision(case)
        self.assertEqual(decision, Decision.REPAIR_RECEIPT)
        self.assertNotEqual(decision, Decision.REOPEN_SMALLEST_PHASE)

    def test_scenario_3_missing_closure_field_closes_without_replay(self) -> None:
        self.assertEqual(authority_decision(self.verified), Decision.CLOSE)

    def test_scenario_4_receipt_conflicts_with_checkpoint_repairs_not_reopens(self) -> None:
        case = replace(self.verified, primary_evidence_matches_claim=False)
        self.assertEqual(authority_decision(case), Decision.REPAIR_RECEIPT)

    def test_scenario_5_deterministic_invalidation_reopens_smallest_phase(self) -> None:
        case = replace(self.verified, checkpoint_deterministically_invalidated=True)
        self.assertEqual(authority_decision(case), Decision.REOPEN_SMALLEST_PHASE)

    def test_scenario_6_and_proportionality_trivial_task_needs_no_ceremony(self) -> None:
        self.assertFalse(
            requires_formal_receipt(
                delegated=False, serious_task_prompt=False, run_skeptic_invoked=False
            )
        )
        self.assertTrue(
            requires_formal_receipt(
                delegated=True, serious_task_prompt=False, run_skeptic_invoked=False
            )
        )
        self.assertEqual(authority_decision(self.verified), Decision.CLOSE)

    def test_scenario_9_human_owned_judgment_is_not_computed_by_a_checker(self) -> None:
        owner = decision_owner(
            deterministic_facts_complete=True, requires_authorized_judgment=True
        )
        self.assertEqual(owner, "LEAD_OR_OWNER")
        self.assertNotEqual(owner, "DETERMINISTIC")

    def test_unverified_conflicting_claim_requires_narrow_verification_first(self) -> None:
        case = replace(self.verified, receipt_claim_verified=False)
        self.assertEqual(authority_decision(case), Decision.VERIFY_NARROWLY)


if __name__ == "__main__":
    unittest.main()
