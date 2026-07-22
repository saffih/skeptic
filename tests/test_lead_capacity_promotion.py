# made by AI
"""Regression coverage for the capacity/promotion repair.

Observed failure mode (resumed bootstrap, 2026-07-21): an eligible read-only
Checker returns a complete READY receipt with matching hash and all-PASS
categories, Lead capacity is CONSTRAINED, and the Lead is offered an
additional semantic spot-check. The correct behavior is to deterministically
promote the receipt, refuse the spot-check, and persist/advance -- not to
redo the review and burn the closure reserve.

These tests do not prove agent behavior; they freeze the reference decision
table that agents/task-prompt.md must match (capacity states and
action classification now live solely there), plus the analogous
PASS-streak and receipt-rejection rules that agents/lead-agent-prompt.md's
current orchestration-only contract uses in their place, and check the
governing text is present.
"""
from __future__ import annotations

import hashlib
import json
import unittest
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAD_PROMPT = ROOT / "agents" / "lead-agent-prompt.md"
TASK_PROMPT = ROOT / "agents" / "task-prompt.md"


class Capacity(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    CONSTRAINED = "CONSTRAINED"
    UNSAFE = "UNSAFE"


class ActionKind(str, Enum):
    ACCEPTANCE_REQUIRED = "ACCEPTANCE_REQUIRED"
    BLOCKER_REQUIRED = "BLOCKER_REQUIRED"
    OPTIONAL = "OPTIONAL"


class Decision(str, Enum):
    PERSIST_AND_ADVANCE = "PERSIST_AND_ADVANCE"
    HANDLE_BLOCKER = "HANDLE_BLOCKER"
    REFUSE_OPTIONAL = "REFUSE_OPTIONAL"
    ALLOW_OPTIONAL = "ALLOW_OPTIONAL"
    CHECKPOINT_AND_HANDOFF = "CHECKPOINT_AND_HANDOFF"


@dataclass(frozen=True)
class ActionCase:
    """No field has a default: an incomplete case must fail to construct."""

    capacity: Capacity
    action_kind: ActionKind
    just_accepted: bool


def decide(case: ActionCase) -> Decision:
    """Executable reference for the capacity/action-classification rule in
    agents/lead-agent-prompt.md and agents/task-prompt.md."""
    if case.action_kind is ActionKind.ACCEPTANCE_REQUIRED:
        return Decision.PERSIST_AND_ADVANCE
    if case.action_kind is ActionKind.BLOCKER_REQUIRED:
        return Decision.HANDLE_BLOCKER
    # OPTIONAL
    if case.capacity is Capacity.UNSAFE:
        return Decision.CHECKPOINT_AND_HANDOFF
    if case.just_accepted or case.capacity is Capacity.CONSTRAINED:
        return Decision.REFUSE_OPTIONAL
    return Decision.ALLOW_OPTIONAL


@dataclass(frozen=True)
class ReceiptCase:
    """Structurally cannot express 'an additional reviewer opinion changed
    the outcome' -- there is no such field. Promotion depends only on
    deterministic facts."""

    identity_matches: bool
    reviewer_eligible: bool
    required_fields_present: bool
    evidence_references_resolve: bool
    unresolved_blocker: bool


def promote(receipt: ReceiptCase) -> bool:
    """Executable reference for deterministic promotion: True iff every
    deterministic check passes and no blocker remains."""
    return (
        receipt.identity_matches
        and receipt.reviewer_eligible
        and receipt.required_fields_present
        and receipt.evidence_references_resolve
        and not receipt.unresolved_blocker
    )


VALID_READY_RECEIPT = ReceiptCase(
    identity_matches=True,
    reviewer_eligible=True,
    required_fields_present=True,
    evidence_references_resolve=True,
    unresolved_blocker=False,
)

# Frozen regression fixture: a valid READY receipt, Lead capacity CONSTRAINED,
# offered one additional optional semantic spot-check immediately after
# acceptance. Any change to this fixture must change its hash below.
REGRESSION_FIXTURE = {
    "scenario": "valid_ready_receipt_then_optional_spot_check",
    "receipt": {
        "identity_matches": True,
        "reviewer_eligible": True,
        "required_fields_present": True,
        "evidence_references_resolve": True,
        "unresolved_blocker": False,
    },
    "lead_capacity": "CONSTRAINED",
    "offered_action": "OPTIONAL",
    "just_accepted": True,
    "expected_promotion": True,
    "expected_decision": "REFUSE_OPTIONAL",
}
REGRESSION_FIXTURE_SHA256 = (
    "519b815e3fb781fd743741bfd5edc26d5d01f8132172a484bbca5520e19e44f8"
)


class RegressionFixtureTests(unittest.TestCase):
    def test_fixture_is_frozen(self) -> None:
        canonical = json.dumps(REGRESSION_FIXTURE, sort_keys=True).encode("utf-8")
        digest = hashlib.sha256(canonical).hexdigest()
        self.assertEqual(digest, REGRESSION_FIXTURE_SHA256)

    def test_valid_receipt_promotes_regardless_of_capacity(self) -> None:
        self.assertTrue(promote(VALID_READY_RECEIPT))

    def test_offered_spot_check_is_refused_under_constrained_capacity(self) -> None:
        case = ActionCase(
            capacity=Capacity[REGRESSION_FIXTURE["lead_capacity"]],
            action_kind=ActionKind[REGRESSION_FIXTURE["offered_action"]],
            just_accepted=REGRESSION_FIXTURE["just_accepted"],
        )
        self.assertEqual(decide(case), Decision[REGRESSION_FIXTURE["expected_decision"]])


class ActionClassificationScenarioTests(unittest.TestCase):
    def test_acceptance_required_always_persists_and_advances(self) -> None:
        for capacity in Capacity:
            with self.subTest(capacity=capacity):
                case = ActionCase(
                    capacity=capacity,
                    action_kind=ActionKind.ACCEPTANCE_REQUIRED,
                    just_accepted=True,
                )
                self.assertEqual(decide(case), Decision.PERSIST_AND_ADVANCE)

    def test_blocker_required_always_handled(self) -> None:
        case = ActionCase(
            capacity=Capacity.CONSTRAINED,
            action_kind=ActionKind.BLOCKER_REQUIRED,
            just_accepted=False,
        )
        self.assertEqual(decide(case), Decision.HANDLE_BLOCKER)

    def test_optional_allowed_only_when_sufficient_and_not_just_accepted(self) -> None:
        case = ActionCase(
            capacity=Capacity.SUFFICIENT,
            action_kind=ActionKind.OPTIONAL,
            just_accepted=False,
        )
        self.assertEqual(decide(case), Decision.ALLOW_OPTIONAL)

    def test_optional_refused_immediately_after_acceptance_even_if_sufficient(self) -> None:
        case = ActionCase(
            capacity=Capacity.SUFFICIENT,
            action_kind=ActionKind.OPTIONAL,
            just_accepted=True,
        )
        self.assertEqual(decide(case), Decision.REFUSE_OPTIONAL)

    def test_optional_refused_when_constrained(self) -> None:
        case = ActionCase(
            capacity=Capacity.CONSTRAINED,
            action_kind=ActionKind.OPTIONAL,
            just_accepted=False,
        )
        self.assertEqual(decide(case), Decision.REFUSE_OPTIONAL)

    def test_optional_checkpoints_when_unsafe(self) -> None:
        case = ActionCase(
            capacity=Capacity.UNSAFE,
            action_kind=ActionKind.OPTIONAL,
            just_accepted=False,
        )
        self.assertEqual(decide(case), Decision.CHECKPOINT_AND_HANDOFF)

    def test_omitted_fields_raise_type_error(self) -> None:
        with self.assertRaises(TypeError):
            ActionCase(capacity=Capacity.SUFFICIENT)  # type: ignore[call-arg]


class GovernanceMarkerTests(unittest.TestCase):
    """Capacity-state classification (SUFFICIENT/CONSTRAINED/UNSAFE) and the
    optional-work/re-review rules now live solely in agents/task-prompt.md;
    the current orchestration-only agents/lead-agent-prompt.md does not
    restate them. The Lead prompt's own stand-ins for "don't redo accepted
    work" are its PASS-streak rule (stop after three consecutive PASS on an
    unchanged candidate) and its structural receipt rejection
    (CONTEXT_BOUNDARY_VIOLATION on undeclared or substantive content) --
    checked below against their actual current text."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.lead = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.task = TASK_PROMPT.read_text(encoding="utf-8")

    def test_lead_prompt_defines_minimal_orchestration_state(self) -> None:
        for marker in [
            "current_stage",
            "candidate_identity",
            "consecutive_passes",
            "next_action",
            "blocker",
            "receipt_identities",
        ]:
            self.assertIn(marker, self.lead)
        self.assertIn(
            "Do not retain substantive task content in Lead state.",
            self.lead,
        )

    def test_lead_prompt_stops_after_three_pass_on_unchanged_candidate(self) -> None:
        self.assertIn(
            "Any candidate change resets the PASS count to zero.",
            self.lead,
        )
        self.assertIn(
            "Stop verification after three consecutive PASS results on the same "
            "unchanged candidate.",
            self.lead,
        )

    def test_lead_prompt_rejects_undeclared_or_substantive_receipt_content(self) -> None:
        self.assertIn(
            "If a Boundary Agent returns undeclared or substantive information, "
            "reject the receipt and stop with:",
            self.lead,
        )
        self.assertIn("CONTEXT_BOUNDARY_VIOLATION", self.lead)

    def test_task_prompt_requires_capacity_check_per_phase(self) -> None:
        self.assertIn(
            "Before each phase and immediately after each acceptance, a fresh Boundary Agent must return capacity as `SUFFICIENT`",
            self.task,
        )
        self.assertIn(
            "optional work is forbidden immediately after any acceptance and whenever capacity is `CONSTRAINED` or `UNSAFE`",
            self.task,
        )

    def test_task_prompt_phase_contract_has_promotion_fields(self) -> None:
        for marker in [
            "Deterministic promotion checks:",
            "Accepting owner:",
            "What acceptance authorizes:",
            "What acceptance forbids:",
            "Deterministic invalidation conditions:",
        ]:
            self.assertIn(marker, self.task)


if __name__ == "__main__":
    unittest.main()
