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
    receipt_verified: bool
    terminal_facts_complete: bool
    closure_field_missing: bool
    closure_field_reconstructable: bool
    accepted_outputs_valid: bool


def evaluate(case: ReceiptCase) -> Result:
    """Executable reference for the binding-aware authority rule in
    agents/task-prompt.md. Fails closed: unverified or unbound evidence
    never promotes or closes."""
    preserve = case.accepted_outputs_valid

    if case.evidence_state is EvidenceState.UNVERIFIED or case.checkpoint_state is CheckpointState.UNKNOWN:
        return Result(Promotion.VERIFY, False, ReceiptAction.NONE, preserve)

    reopen = case.checkpoint_state is CheckpointState.INVALIDATED

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


MATCH_VALID_COMPLETE = dict(
    evidence_state=EvidenceState.VERIFIED_MATCH,
    checkpoint_state=CheckpointState.VALID,
    promotion_critical=False,
    material_evidence_present=True,
    receipt_verified=True,
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
        self.assertIn("not an independent promotion input", self.task_prompt)

    def test_closure_receipt_is_not_overclaimed_as_proof(self) -> None:
        self.assertIn("required terminal summary for the whole Task Prompt", self.task_prompt)
        self.assertNotIn("only terminal proof", self.task_prompt)

    def test_lead_prompt_treats_receipts_as_claims(self) -> None:
        self.assertIn(
            "Treat an Agent Receipt or Task Closure Receipt as a claim, not authority",
            self.lead_prompt,
        )

    def test_governance_has_receipt_authority_scenarios_and_binding_rules(self) -> None:
        self.assertIn("Receipt authority regression scenarios", self.governance)
        for marker in [
            "an unverified receipt authorizes a consequential transition",
            "receipt prose overrides primary evidence or deterministic state",
            "missing receipt prose causes completed phases to replay",
            "receipt ceremony becomes mandatory for trivial non-delegated work",
            "a checklist-only RunSkeptic receipt is accepted without evidence",
            "a closure receipt independently invents DONE",
            "artifact type alone does not establish authority",
            "stale or wrong-run evidence cannot promote",
            "governance fixtures that default to success are rejected",
        ]:
            self.assertIn(marker, self.governance)


class ReceiptAuthorityScenarioTests(unittest.TestCase):
    """Exercises the fourteen fail-closed cases from the Minimal Repair Plan."""

    def test_case_1_false_test_claim_blocks_and_repairs(self) -> None:
        case = ReceiptCase(**{**MATCH_VALID_COMPLETE, "evidence_state": EvidenceState.VERIFIED_MISMATCH, "promotion_critical": True})
        result = evaluate(case)
        self.assertEqual(result.promotion, Promotion.BLOCK)
        self.assertEqual(result.receipt_action, ReceiptAction.REPAIR)
        self.assertFalse(result.reopen_smallest_phase)

    def test_case_2_claimed_mutation_without_mutation_repairs_no_reopen(self) -> None:
        case = ReceiptCase(**{**MATCH_VALID_COMPLETE, "evidence_state": EvidenceState.VERIFIED_MISMATCH})
        result = evaluate(case)
        self.assertEqual(result.receipt_action, ReceiptAction.REPAIR)
        self.assertFalse(result.reopen_smallest_phase)
        self.assertEqual(result.promotion, Promotion.ALLOW)

    def test_case_3_missing_reconstructable_closure_field_closes_without_replay(self) -> None:
        case = ReceiptCase(**{**MATCH_VALID_COMPLETE, "closure_field_missing": True, "closure_field_reconstructable": True})
        result = evaluate(case)
        self.assertEqual(result.promotion, Promotion.ALLOW)
        self.assertEqual(result.receipt_action, ReceiptAction.RECONSTRUCT)
        self.assertFalse(result.reopen_smallest_phase)

    def test_case_4_receipt_conflicts_with_valid_checkpoint_repairs_checkpoint_stays_valid(self) -> None:
        case = ReceiptCase(**{**MATCH_VALID_COMPLETE, "evidence_state": EvidenceState.VERIFIED_MISMATCH})
        result = evaluate(case)
        self.assertEqual(result.receipt_action, ReceiptAction.REPAIR)
        self.assertFalse(result.reopen_smallest_phase)

    def test_case_5_deterministic_invalidation_blocks_and_reopens(self) -> None:
        case = ReceiptCase(**{**MATCH_VALID_COMPLETE, "checkpoint_state": CheckpointState.INVALIDATED})
        result = evaluate(case)
        self.assertEqual(result.promotion, Promotion.BLOCK)
        self.assertTrue(result.reopen_smallest_phase)

    def test_case_6_mismatch_and_invalidation_together_repairs_and_reopens(self) -> None:
        case = ReceiptCase(
            **{
                **MATCH_VALID_COMPLETE,
                "evidence_state": EvidenceState.VERIFIED_MISMATCH,
                "checkpoint_state": CheckpointState.INVALIDATED,
            }
        )
        result = evaluate(case)
        self.assertEqual(result.promotion, Promotion.BLOCK)
        self.assertEqual(result.receipt_action, ReceiptAction.REPAIR)
        self.assertTrue(result.reopen_smallest_phase)

    def test_case_7_trivial_non_delegated_task_needs_no_formal_receipt(self) -> None:
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

    def test_case_8_checklist_theatre_blocks_on_missing_material_evidence(self) -> None:
        case = ReceiptCase(**{**MATCH_VALID_COMPLETE, "material_evidence_present": False})
        result = evaluate(case)
        self.assertEqual(result.promotion, Promotion.BLOCK)

    def test_case_9_controller_incomplete_beats_closure_prose_preserves_outputs(self) -> None:
        case = ReceiptCase(
            **{**MATCH_VALID_COMPLETE, "evidence_state": EvidenceState.VERIFIED_MISMATCH, "promotion_critical": True, "accepted_outputs_valid": True}
        )
        result = evaluate(case)
        self.assertEqual(result.promotion, Promotion.BLOCK)
        self.assertEqual(result.receipt_action, ReceiptAction.REPAIR)
        self.assertTrue(result.preserve_accepted_outputs)

    def test_case_10_human_owned_judgment_is_not_computed_by_a_checker(self) -> None:
        owner = decision_owner(deterministic_facts_complete=True, requires_authorized_judgment=True)
        self.assertEqual(owner, "LEAD_OR_OWNER")
        self.assertNotEqual(owner, "DETERMINISTIC")

    def test_case_11_raw_log_from_another_run_is_unverified(self) -> None:
        case = ReceiptCase(**{**MATCH_VALID_COMPLETE, "evidence_state": EvidenceState.UNVERIFIED})
        result = evaluate(case)
        self.assertEqual(result.promotion, Promotion.VERIFY)

    def test_case_12_stale_commit_evidence_is_unverified(self) -> None:
        case = ReceiptCase(**{**MATCH_VALID_COMPLETE, "checkpoint_state": CheckpointState.UNKNOWN})
        result = evaluate(case)
        self.assertEqual(result.promotion, Promotion.VERIFY)

    def test_case_13_omitted_fields_raise_type_error(self) -> None:
        with self.assertRaises(TypeError):
            ReceiptCase(evidence_state=EvidenceState.VERIFIED_MATCH)  # type: ignore[call-arg]

    def test_case_14_old_terminal_proof_phrase_is_absent(self) -> None:
        task_prompt = TASK_PROMPT.read_text(encoding="utf-8")
        self.assertNotIn("only terminal proof", task_prompt)


if __name__ == "__main__":
    unittest.main()
