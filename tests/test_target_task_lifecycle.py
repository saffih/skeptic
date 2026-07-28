from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from harness.target_task_lifecycle import (
    CHECKPOINT_FIELDS,
    HANDOFF_FIELDS,
    accept_and_seal_plan,
    make_checkpoint,
    resume_checkpoint,
    select_execution_mode,
    terminal_receipt,
    validate_handoff,
    write_checkpoint,
    TargetTaskIntegrityError,
)


PLAN = {
    "task_id": "TT-LIFECYCLE-001", "objective": "exercise lifecycle",
    "done": "all deterministic checks pass", "scope": ["harness"],
    "prohibitions": ["no runtime isolation claims"],
    "source_of_truth_order": ["authority", "plan", "checkpoint"],
    "steps": [{"id": "S1", "objective": "write evidence"}],
    "validation": ["focused tests"], "handoff": list(HANDOFF_FIELDS),
    "stop_conditions": ["integrity mismatch"],
    "review_mode": "DETERMINISTIC_ONLY", "success_criteria": ["pass"],
}


class TargetTaskLifecycleTests(unittest.TestCase):
    def test_context_mode_selection_is_truthful(self) -> None:
        self.assertEqual(select_execution_mode("FRESH_CONTEXT_CONFIRMED", "ISOLATION_REQUIRED"),
                         "ISOLATED_ORCHESTRATION")
        self.assertEqual(select_execution_mode("CONTEXT_ISOLATION_UNKNOWN", "ISOLATION_OPTIONAL"),
                         "SHARED_CONTEXT_DEGRADED")
        self.assertEqual(select_execution_mode("PARENT_CONTEXT_INHERITED", "ISOLATION_REQUIRED"),
                         "ISOLATION_REQUIRED_BLOCKED")

    def test_plan_is_sealed_and_hash_bound(self) -> None:
        sealed = accept_and_seal_plan(PLAN, "TT-LIFECYCLE-001")
        self.assertTrue(sealed["PLAN_HASH"])
        self.assertEqual(sealed["PLAN"]["task_id"], "TT-LIFECYCLE-001")
        with self.assertRaises(ValueError):
            accept_and_seal_plan({**PLAN, "review_mode": "OTHER"}, "TT-LIFECYCLE-001")

    def test_interruption_resume_and_completed_step_nonrepetition(self) -> None:
        sealed = accept_and_seal_plan(PLAN, "TT-LIFECYCLE-001")
        checkpoint = make_checkpoint(
            task_id="TT-LIFECYCLE-001", task_reference="task://001",
            authority_reference="authority://001", plan_reference=sealed["PLAN_REFERENCE"],
            plan_hash=sealed["PLAN_HASH"], execution_mode="SHARED_CONTEXT_DEGRADED",
            observed_context_status="CONTEXT_ISOLATION_UNKNOWN", current_step="S2",
            completed_steps_and_evidence={"S1": {"status": "ACCEPTED", "artifact": "evidence.md"}},
            next_authorized_action="RUN-S2", last_validation_state="PASS",
        )
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "checkpoint.json"
            write_checkpoint(path, checkpoint)
            resumed = resume_checkpoint(path, task_id="TT-LIFECYCLE-001",
                                        plan_hash=sealed["PLAN_HASH"],
                                        plan_reference=sealed["PLAN_REFERENCE"])
        self.assertEqual(resumed["CURRENT_STEP"], "S2")
        self.assertIn("S1", resumed["COMPLETED_STEPS_AND_EVIDENCE"])
        self.assertNotEqual(resumed["CURRENT_STEP"], "S1")

    def test_plan_and_checkpoint_identity_mismatch_blocks(self) -> None:
        sealed = accept_and_seal_plan(PLAN, "TT-LIFECYCLE-001")
        checkpoint = make_checkpoint(
            task_id="TT-LIFECYCLE-001", task_reference="task://001",
            authority_reference="authority://001", plan_reference=sealed["PLAN_REFERENCE"],
            plan_hash=sealed["PLAN_HASH"], execution_mode="SHARED_CONTEXT_DEGRADED",
            observed_context_status="CONTEXT_ISOLATION_UNKNOWN", current_step="S1",
            completed_steps_and_evidence={},
        )
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "checkpoint.json"
            write_checkpoint(path, checkpoint)
            with self.assertRaises(TargetTaskIntegrityError):
                resume_checkpoint(path, task_id="OTHER", plan_hash=sealed["PLAN_HASH"],
                                  plan_reference=sealed["PLAN_REFERENCE"])

    def test_worker_claim_requires_provenance_before_acceptance(self) -> None:
        handoff = {field: () for field in HANDOFF_FIELDS}
        handoff["STATUS"] = "PASS"
        handoff["NEXT_AUTHORIZED_ACTION"] = "VALIDATE"
        handoff["VALIDATED_FACTS"] = ({"claim": "green", "provenance": "WORKER_REPORTED"},)
        validate_handoff(handoff)
        handoff["VALIDATED_FACTS"] = ({"claim": "green"},)
        with self.assertRaises(ValueError):
            validate_handoff(handoff)

    def test_receipt_separates_completion_from_runtime_claims(self) -> None:
        receipt = terminal_receipt(
            TASK_RESULT="ACCEPTED", PLAN_INTEGRITY="PASS",
            DETERMINISTIC_VALIDATION="PASS", REVIEW_RESULT="NOT_RUN",
            EXECUTION_MODE="SHARED_CONTEXT_DEGRADED",
            OBSERVED_CONTEXT_STATUS="CONTEXT_ISOLATION_UNKNOWN",
            BOUNDARY_PROCESSING_STATUS="PASS",
            CHECKPOINT_AND_RESUME_STATUS="PASS",
            CONTEXT_CONTAINMENT_EVIDENCE="BOUNDED_STATE_ONLY",
            ACTUAL_RUNTIME_ISOLATION="UNKNOWN",
            ACTUAL_CONTEXT_REDUCTION="NOT_CLAIMED", BLOCKERS=(),
        )
        self.assertEqual(receipt["TASK_RESULT"], "ACCEPTED")
        self.assertEqual(receipt["ACTUAL_RUNTIME_ISOLATION"], "UNKNOWN")
        self.assertEqual(tuple(CHECKPOINT_FIELDS), tuple(checkpoint_field for checkpoint_field in CHECKPOINT_FIELDS))
