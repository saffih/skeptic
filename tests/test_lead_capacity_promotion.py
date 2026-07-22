# made by AI
"""Receipt promotion and verification routing for the orchestration-only Lead.

The removed capacity/action-classification machinery is intentionally absent.
Coverage now freezes only the current contract: structural receipt validation,
candidate-bound PASS streaks, and ACTION routing by finding identity.
"""
from __future__ import annotations

import unittest
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEAD_PROMPT = ROOT / "agents" / "lead-agent-prompt.md"
TASK_PROMPT = ROOT / "agents" / "task-prompt.md"


@dataclass(frozen=True)
class ReceiptCase:
    identity_matches: bool
    required_fields_present: bool
    allowlisted_fields_only: bool
    unresolved_blocker: bool


def promote(receipt: ReceiptCase) -> bool:
    return (
        receipt.identity_matches
        and receipt.required_fields_present
        and receipt.allowlisted_fields_only
        and not receipt.unresolved_blocker
    )


@dataclass(frozen=True)
class VerificationState:
    candidate_identity: str
    consecutive_passes: int


@dataclass(frozen=True)
class ReviewReceipt:
    candidate_identity: str
    verdict: str
    finding_ids: tuple[str, ...]


@dataclass(frozen=True)
class ReviewRoute:
    consecutive_passes: int
    next_state: str
    forwarded_finding_ids: tuple[str, ...]


def route_review(state: VerificationState, receipt: ReviewReceipt) -> ReviewRoute:
    if receipt.candidate_identity != state.candidate_identity:
        return ReviewRoute(0, "REJECT_IDENTITY", ())
    if receipt.verdict == "ACTION":
        return ReviewRoute(0, "REPAIR", receipt.finding_ids)
    if receipt.verdict == "PASS":
        count = state.consecutive_passes + 1
        return ReviewRoute(count, "ACCEPT" if count == 3 else "REVIEW", ())
    return ReviewRoute(0, "STOP", ())


def mutate_candidate(state: VerificationState, new_identity: str) -> VerificationState:
    return VerificationState(new_identity, 0)


VALID_RECEIPT = ReceiptCase(
    identity_matches=True,
    required_fields_present=True,
    allowlisted_fields_only=True,
    unresolved_blocker=False,
)


class ReceiptPromotionTests(unittest.TestCase):
    def test_valid_compact_receipt_promotes(self) -> None:
        self.assertTrue(promote(VALID_RECEIPT))

    def test_each_structural_defect_blocks_promotion(self) -> None:
        for field in [
            "identity_matches",
            "required_fields_present",
            "allowlisted_fields_only",
        ]:
            with self.subTest(field=field):
                values = vars(VALID_RECEIPT) | {field: False}
                self.assertFalse(promote(ReceiptCase(**values)))
        self.assertFalse(
            promote(ReceiptCase(**(vars(VALID_RECEIPT) | {"unresolved_blocker": True})))
        )

    def test_omitted_receipt_field_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            ReceiptCase(identity_matches=True)  # type: ignore[call-arg]


class VerificationRoutingTests(unittest.TestCase):
    def test_pass_counts_only_for_same_candidate(self) -> None:
        state = VerificationState("candidate-a", 1)
        route = route_review(state, ReviewReceipt("candidate-a", "PASS", ()))
        self.assertEqual(route, ReviewRoute(2, "REVIEW", ()))
        self.assertEqual(
            route_review(state, ReviewReceipt("candidate-b", "PASS", ())),
            ReviewRoute(0, "REJECT_IDENTITY", ()),
        )

    def test_third_same_candidate_pass_accepts_and_stops(self) -> None:
        state = VerificationState("candidate-a", 2)
        self.assertEqual(
            route_review(state, ReviewReceipt("candidate-a", "PASS", ())),
            ReviewRoute(3, "ACCEPT", ()),
        )

    def test_action_resets_and_routes_only_finding_ids(self) -> None:
        state = VerificationState("candidate-a", 2)
        self.assertEqual(
            route_review(
                state,
                ReviewReceipt("candidate-a", "ACTION", ("LA-1", "LA-2")),
            ),
            ReviewRoute(0, "REPAIR", ("LA-1", "LA-2")),
        )

    def test_candidate_mutation_resets_pass_streak(self) -> None:
        self.assertEqual(
            mutate_candidate(VerificationState("candidate-a", 2), "candidate-b"),
            VerificationState("candidate-b", 0),
        )


class GovernanceMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.task = TASK_PROMPT.read_text(encoding="utf-8")

    def test_lead_uses_compact_allowlisted_receipts(self) -> None:
        self.assertIn(
            "A Boundary Agent may return only the fields declared in its dispatch.",
            self.lead,
        )
        self.assertIn("CONTEXT_BOUNDARY_VIOLATION", self.lead)

    def test_candidate_and_action_rules_are_explicit(self) -> None:
        self.assertIn("Any candidate change resets the PASS count to zero.", self.lead)
        self.assertIn(
            "If the verdict is ACTION, reset the PASS count to zero and dispatch "
            "a fresh Boundary Agent to repair only the identified findings.",
            self.lead,
        )
        self.assertIn(
            "Stop verification after three consecutive PASS results on the same "
            "unchanged candidate.",
            self.lead,
        )

    def test_task_prompt_does_not_recreate_capacity_state_machine(self) -> None:
        for deleted in [
            "SUFFICIENT",
            "CONSTRAINED",
            "UNSAFE",
            "acceptance-required",
            "blocker-required",
        ]:
            self.assertNotIn(deleted, self.task)

    def test_task_prompt_phase_contract_keeps_promotion_guards(self) -> None:
        for marker in [
            "Deterministic promotion checks:",
            "What acceptance authorizes:",
            "What acceptance forbids:",
            "Deterministic invalidation conditions:",
        ]:
            self.assertIn(marker, self.task)


if __name__ == "__main__":
    unittest.main()
