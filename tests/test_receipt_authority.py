# made by AI
from __future__ import annotations

import unittest
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKEPTIC = ROOT / "skeptic.md"
TASK_PROMPT = ROOT / "agents" / "task-prompt.md"
LEAD_PROMPT = ROOT / "agents" / "lead-agent-prompt.md"
GOVERNANCE = ROOT / "skeptic-tests.md"


class EvidenceState(str, Enum):
    VERIFIED_MATCH = "VERIFIED_MATCH"
    VERIFIED_MISMATCH = "VERIFIED_MISMATCH"
    UNVERIFIED = "UNVERIFIED"


class CheckpointState(str, Enum):
    VALID = "VALID"
    INVALIDATED = "INVALIDATED"
    UNKNOWN = "UNKNOWN"


class Promotion(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    VERIFY = "VERIFY"


class ReceiptAction(str, Enum):
    NONE = "NONE"
    REPAIR = "REPAIR"
    RECONSTRUCT = "RECONSTRUCT"


@dataclass(frozen=True)
class Result:
    promotion: Promotion
    reopen_smallest_phase: bool
    receipt_action: ReceiptAction
    preserve_accepted_outputs: bool


@dataclass(frozen=True)
class ReceiptCase:
    """No field has a default: an incomplete case must fail to construct,
    not silently resolve toward success."""

    evidence_state: EvidenceState
    checkpoint_state: CheckpointState
    promotion_critical: bool
    material_evidence_present: bool
    terminal_facts_complete: bool
    closure_field_missing: bool
    closure_field_reconstructable: bool
    accepted_outputs_valid: bool


def evaluate(case: ReceiptCase) -> Result:
    """Executable reference for the binding-aware authority rule in
    agents/task-prompt.md. Fails closed: unverified or unbound evidence
    never promotes or closes."""
    preserve = case.accepted_outputs_valid

    if case.checkpoint_state is CheckpointState.UNKNOWN:
        return Result(Promotion.VERIFY, False, ReceiptAction.NONE, preserve)

    reopen = case.checkpoint_state is CheckpointState.INVALIDATED

    if case.evidence_state is EvidenceState.UNVERIFIED:
        promotion = Promotion.BLOCK if reopen else Promotion.VERIFY
        return Result(promotion, reopen, ReceiptAction.NONE, preserve)

    if not case.material_evidence_present:
        return Result(Promotion.BLOCK, reopen, ReceiptAction.NONE, preserve)

    if case.evidence_state is EvidenceState.VERIFIED_MISMATCH:
        promotion = Promotion.BLOCK if (case.promotion_critical or reopen) else Promotion.ALLOW
        return Result(promotion, reopen, ReceiptAction.REPAIR, preserve)

    if reopen:
        return Result(Promotion.BLOCK, True, ReceiptAction.NONE, preserve)

    if not case.terminal_facts_complete:
        return Result(Promotion.VERIFY, False, ReceiptAction.NONE, preserve)

    if case.closure_field_missing:
        if case.closure_field_reconstructable:
            return Result(Promotion.ALLOW, False, ReceiptAction.RECONSTRUCT, preserve)
        return Result(Promotion.VERIFY, False, ReceiptAction.NONE, preserve)

    return Result(Promotion.ALLOW, False, ReceiptAction.NONE, preserve)


def requires_detailed_report(*, detailed_output_required: bool) -> bool:
    """Every Boundary Agent returns a compact receipt; a separate detailed
    report exists only when the task produces detailed output."""
    return detailed_output_required


def decision_owner(
    *, deterministic_facts_complete: bool, requires_authorized_judgment: bool
) -> str:
    """A Boundary Agent can compute facts; only the owner supplies a reserved
    human judgment. The orchestration-only Lead does neither."""
    if requires_authorized_judgment:
        return "OWNER"
    return "BOUNDARY_AGENT" if deterministic_facts_complete else "UNRESOLVED"


MATCH_VALID_COMPLETE = dict(
    evidence_state=EvidenceState.VERIFIED_MATCH,
    checkpoint_state=CheckpointState.VALID,
    promotion_critical=False,
    material_evidence_present=True,
    terminal_facts_complete=True,
    closure_field_missing=False,
    closure_field_reconstructable=False,
    accepted_outputs_valid=True,
)


class CrossFileAuthorityMarkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skeptic = SKEPTIC.read_text(encoding="utf-8")
        cls.task_prompt = TASK_PROMPT.read_text(encoding="utf-8")
        cls.lead_prompt = LEAD_PROMPT.read_text(encoding="utf-8")
        cls.governance = GOVERNANCE.read_text(encoding="utf-8")

    def test_skeptic_receipt_is_not_authoritative(self) -> None:
        self.assertIn("not proof and not an authorization artifact", self.skeptic)

    def test_task_prompt_defines_binding_aware_authority(self) -> None:
        self.assertIn("compact claim-and-evidence index", self.task_prompt)
        self.assertIn("A receipt never outranks the evidence it summarizes", self.task_prompt)
        self.assertIn("identity, scope, inputs, freshness, and acceptance state", self.task_prompt)
        self.assertIn("block consequential promotion", self.task_prompt)

    def test_required_receipts_remain_proportionate(self) -> None:
        self.assertIn("required terminal summary for the whole Task Prompt", self.task_prompt)
        self.assertIn("A small Boundary Agent task still returns its declared compact receipt", self.task_prompt)
        self.assertIn("it need not create a separate detailed report", self.task_prompt)
        self.assertIn("Do not claim RunSkeptic compliance without this receipt", self.skeptic)

    def test_closure_receipt_is_not_overclaimed_as_proof(self) -> None:
        self.assertIn("required terminal summary for the whole Task Prompt", self.task_prompt)
        self.assertNotIn("only terminal proof", self.task_prompt)

    def test_lead_prompt_validates_receipts_structurally(self) -> None:
        # The old "claims, not authority" framing was removed with the
        # longer Lead prompt. The current orchestration-only contract
        # achieves the same not-taken-at-face-value effect structurally: a
        # Boundary Agent may return only its declared, allowlisted fields,
        # and any undeclared or substantive content is rejected outright
        # rather than accepted as authoritative.
        self.assertIn(
            "A Boundary Agent may return only the fields declared in its dispatch.",
            self.lead_prompt,
        )
        self.assertIn(
            "If a Boundary Agent returns undeclared or substantive information, "
            "reject the receipt and stop with:",
            self.lead_prompt,
        )
        self.assertIn("CONTEXT_BOUNDARY_VIOLATION", self.lead_prompt)

    def test_current_simplicity_guard_remains_present(self) -> None:
        self.assertIn("Smallest credible alternative guard", self.skeptic)
        self.assertIn("materially smaller alternative is equally sufficient", self.skeptic)

    def test_governance_has_receipt_authority_scenarios_and_binding_rules(self) -> None:
        self.assertIn("Receipt authority regression scenarios", self.governance)
        for marker in [
            "an unverified receipt authorizes a consequential transition",
            "receipt prose overrides primary evidence or deterministic state",
            "missing receipt prose causes completed phases to replay",
            "a trivial Boundary Agent task is forced to create a detailed report",
            "a checklist-only RunSkeptic receipt is accepted without evidence",
            "a closure receipt independently invents DONE",
            "artifact type alone does not establish authority",
            "stale or wrong-run evidence cannot promote",
            "Receipt-authority and simplicity fixtures must not let omitted decision-critical facts silently resolve to success",
        ]:
            self.assertIn(marker, self.governance)


class ReceiptAuthorityScenarioTests(unittest.TestCase):
    """Exercises the fail-closed authority outcomes as a compact decision table."""

    def test_authority_decision_table(self) -> None:
        cases = [
            ("false test claim", {"evidence_state": EvidenceState.VERIFIED_MISMATCH, "promotion_critical": True}, Promotion.BLOCK, False, ReceiptAction.REPAIR),
            ("noncritical mismatch", {"evidence_state": EvidenceState.VERIFIED_MISMATCH}, Promotion.ALLOW, False, ReceiptAction.REPAIR),
            ("reconstructable closure field", {"closure_field_missing": True, "closure_field_reconstructable": True}, Promotion.ALLOW, False, ReceiptAction.RECONSTRUCT),
            ("receipt versus valid checkpoint", {"evidence_state": EvidenceState.VERIFIED_MISMATCH}, Promotion.ALLOW, False, ReceiptAction.REPAIR),
            ("invalidated checkpoint", {"checkpoint_state": CheckpointState.INVALIDATED}, Promotion.BLOCK, True, ReceiptAction.NONE),
            ("mismatch and invalidation", {"evidence_state": EvidenceState.VERIFIED_MISMATCH, "checkpoint_state": CheckpointState.INVALIDATED}, Promotion.BLOCK, True, ReceiptAction.REPAIR),
            ("unverified evidence and invalidation", {"evidence_state": EvidenceState.UNVERIFIED, "checkpoint_state": CheckpointState.INVALIDATED}, Promotion.BLOCK, True, ReceiptAction.NONE),
            ("checklist theatre", {"material_evidence_present": False}, Promotion.BLOCK, False, ReceiptAction.NONE),
            ("controller failure versus DONE prose", {"evidence_state": EvidenceState.VERIFIED_MISMATCH, "promotion_critical": True}, Promotion.BLOCK, False, ReceiptAction.REPAIR),
        ]
        for name, overrides, promotion, reopen, action in cases:
            with self.subTest(name=name):
                result = evaluate(ReceiptCase(**{**MATCH_VALID_COMPLETE, **overrides}))
                self.assertEqual(result.promotion, promotion)
                self.assertEqual(result.reopen_smallest_phase, reopen)
                self.assertEqual(result.receipt_action, action)
                self.assertTrue(result.preserve_accepted_outputs)

    def test_trivial_boundary_task_needs_no_detailed_report(self) -> None:
        self.assertFalse(requires_detailed_report(detailed_output_required=False))
        self.assertTrue(requires_detailed_report(detailed_output_required=True))

    def test_human_owned_judgment_is_not_computed_by_lead_or_checker(self) -> None:
        owner = decision_owner(deterministic_facts_complete=True, requires_authorized_judgment=True)
        self.assertEqual(owner, "OWNER")
        self.assertNotEqual(owner, "BOUNDARY_AGENT")

    def test_unbound_or_stale_evidence_never_promotes(self) -> None:
        cases = [
            {"evidence_state": EvidenceState.UNVERIFIED},
            {"checkpoint_state": CheckpointState.UNKNOWN},
        ]
        for overrides in cases:
            with self.subTest(overrides=overrides):
                result = evaluate(ReceiptCase(**{**MATCH_VALID_COMPLETE, **overrides}))
                self.assertEqual(result.promotion, Promotion.VERIFY)
                self.assertFalse(result.reopen_smallest_phase)

    def test_omitted_fields_raise_type_error(self) -> None:
        with self.assertRaises(TypeError):
            ReceiptCase(evidence_state=EvidenceState.VERIFIED_MATCH)  # type: ignore[call-arg]

    def test_old_terminal_proof_phrase_is_absent(self) -> None:
        task_prompt = TASK_PROMPT.read_text(encoding="utf-8")
        self.assertNotIn("only terminal proof", task_prompt)


if __name__ == "__main__":
    unittest.main()
