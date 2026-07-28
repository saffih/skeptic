from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from harness.target_task_lifecycle import *

HANDOFF = list(HANDOFF_FIELDS)
def step(i, deps=()):
    return {"id": i, "objective": i, "direct_inputs": [], "referenced_inputs": [],
            "dependencies": list(deps), "authority": "body", "prohibitions": [],
            "actions": ["act"], "outputs": ["artifact"], "validation": ["test"],
            "handoff_requirements": HANDOFF, "retrieval_conditions": [],
            "escalation_conditions": [], "stop_conditions": ["failure"]}
PLAN = {"task_id": "TT-LIFECYCLE-001", "objective": "exercise lifecycle",
        "done": "all deterministic checks pass", "scope": ["harness"],
        "prohibitions": ["no runtime isolation claims"],
        "source_of_truth_order": ["authority", "plan", "checkpoint"],
        "assumptions": [], "unknowns": [], "steps": [step("S1"), step("S2", ("S1",))],
        "validation": ["focused tests"], "handoff": HANDOFF,
        "stop_conditions": ["integrity mismatch"], "retrieval_conditions": [],
        "escalation_conditions": [], "review_mode": "DETERMINISTIC_ONLY",
        "success_criteria": ["pass"], "retry_policy": {"S1": 2}}
def checkpoint(sealed, current="S2", completed=None, **kw):
    return make_checkpoint(task_id="TT-LIFECYCLE-001", task_reference="task://001",
        authority_reference="authority://001", plan_reference=sealed["PLAN_REFERENCE"],
        plan_hash=sealed["PLAN_HASH"], execution_mode="SHARED_CONTEXT_DEGRADED",
        observed_context_status="CONTEXT_ISOLATION_UNKNOWN", current_step=current,
        completed_steps_and_evidence=completed or {"S1": {"status": "ACCEPTED", "artifact": "evidence.md", "max_attempts": 2}},
        next_authorized_action="RUN-" + current, last_validation_state="PASS", **kw)

class TargetTaskLifecycleTests(unittest.TestCase):
    def test_context_mode_selection_is_truthful(self):
        self.assertEqual(select_execution_mode("FRESH_CONTEXT_CONFIRMED", "ISOLATION_REQUIRED"), "ISOLATED_ORCHESTRATION")
        self.assertEqual(select_execution_mode("CONTEXT_ISOLATION_UNKNOWN", "ISOLATION_OPTIONAL"), "SHARED_CONTEXT_DEGRADED")
        self.assertEqual(select_execution_mode("PARENT_CONTEXT_INHERITED", "ISOLATION_REQUIRED"), "ISOLATION_REQUIRED_BLOCKED")

    def test_plan_is_complete_sealed_and_hash_bound(self):
        sealed = accept_and_seal_plan(PLAN, "TT-LIFECYCLE-001")
        self.assertTrue(sealed["PLAN_HASH"]); self.assertEqual(sealed["PLAN"]["TASK_ID"], "TT-LIFECYCLE-001")
        with self.assertRaises(ValueError): accept_and_seal_plan({**PLAN, "review_mode": "OTHER"}, "TT-LIFECYCLE-001")

    def test_plan_rejects_missing_fields_duplicate_ids_missing_dependency_and_cycle(self):
        with self.assertRaises(ValueError): accept_and_seal_plan({"task_id": "x", "steps": []}, "x")
        with self.assertRaises(ValueError): accept_and_seal_plan({**PLAN, "steps": [step("S1"), step("S1")]}, PLAN["task_id"])
        with self.assertRaises(ValueError): accept_and_seal_plan({**PLAN, "steps": [step("S1", ("NOPE",))]}, PLAN["task_id"])
        with self.assertRaises(ValueError): accept_and_seal_plan({**PLAN, "steps": [step("S1", ("S2",)), step("S2", ("S1",))]}, PLAN["task_id"])
        with self.assertRaises(ValueError): accept_and_seal_plan({**PLAN, "steps": [{**step("S1"), "actions": [""]}]}, PLAN["task_id"])
        with self.assertRaises(ValueError): accept_and_seal_plan({**PLAN, "scope": []}, PLAN["task_id"])
        with self.assertRaises(ValueError): accept_and_seal_plan({**PLAN, "steps": [{**step(" S1 ")}, step("S2", (" S1 ",))]}, PLAN["task_id"])

    def test_interruption_resume_validates_identity_hash_graph_and_evidence(self):
        sealed = accept_and_seal_plan(PLAN, PLAN["task_id"]); cp = checkpoint(sealed)
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "checkpoint.json"; write_checkpoint(path, cp)
            resumed = resume_checkpoint(path, task_id=PLAN["task_id"], plan_hash=sealed["PLAN_HASH"], plan_reference=sealed["PLAN_REFERENCE"], sealed_plan=sealed, task_reference="task://001", authority_reference="authority://001")
            self.assertEqual(resumed["CURRENT_STEP"], "S2")
            for field, value in (("TASK_REFERENCE", "other"), ("AUTHORITY_REFERENCE", "other")):
                bad = dict(cp); bad[field] = value
                write_checkpoint(path, bad)
                with self.assertRaises(TargetTaskIntegrityError):
                    resume_checkpoint(path, task_id=PLAN["task_id"], plan_hash=sealed["PLAN_HASH"], plan_reference=sealed["PLAN_REFERENCE"], sealed_plan=sealed, task_reference="task://001", authority_reference="authority://001")
                write_checkpoint.__name__
            bad = dict(cp); bad["CHECKPOINT_VERSION"] = 999
            with self.assertRaises(TargetTaskIntegrityError): validate_checkpoint(bad, sealed)

    def test_resume_rejects_plan_content_mismatch_unknown_step_bad_evidence_and_blocker(self):
        sealed = accept_and_seal_plan(PLAN, PLAN["task_id"])
        for bad in (dict(sealed, PLAN={**sealed["PLAN"], "OBJECTIVE": "changed"}),):
            with self.assertRaises(TargetTaskIntegrityError): validate_checkpoint(checkpoint(sealed), bad)
        for cp in (checkpoint(sealed, current="NOPE"), checkpoint(sealed, completed={"NOPE": {"status": "ACCEPTED", "artifact": "x"}}), checkpoint(sealed, completed={"S1": {"status": "ACCEPTED"}}), checkpoint(sealed, open_blockers=("blocked",))):
            with self.assertRaises(TargetTaskIntegrityError): validate_checkpoint(cp, sealed)

    def test_nonrepetition_and_authorization_are_behavioral(self):
        sealed = accept_and_seal_plan(PLAN, PLAN["task_id"]); cp = checkpoint(sealed)
        self.assertEqual(authorize_step(cp, sealed, "S2"), "S2")
        for requested in ("S1", "UNKNOWN"):
            with self.assertRaises(TargetTaskIntegrityError): authorize_step(cp, sealed, requested)
        retry = {"RETRY_REASON": "new evidence", "PRIOR_RESULT_STATUS": "ACCEPTED", "AUTHORITY": "authority://001", "EXPECTED_NEW_EVIDENCE": "e2", "MAX_ATTEMPTS": 2}
        self.assertEqual(authorize_step(cp, sealed, "S1", retry=retry), "S1")
        accepted = {"STEP_ID": "S1", "VALIDATION": "PASS", "EVIDENCE": {"status": "ACCEPTED", "artifact": "e2"}, "RETRY": retry}
        accept_step_result(cp, sealed, accepted)
        with self.assertRaises(TargetTaskIntegrityError): authorize_step(cp, sealed, "S1", retry=retry)
        self.assertEqual(cp["COMPLETED_STEPS_AND_EVIDENCE"]["S1"]["artifact"], "e2")
        with self.assertRaises(TargetTaskIntegrityError): accept_step_result(cp, sealed, {"STEP_ID": "S2", "VALIDATION": "PASS", "EVIDENCE": {"status": "ACCEPTED"}})

    def test_claim_acceptance_is_separate_from_handoff_structure(self):
        handoff = {field: () for field in HANDOFF_FIELDS}; handoff.update(STATUS="PASS", WORK_PERFORMED="bounded", RETRIEVAL_GUIDANCE="none", READ_CONDITIONS="focused", NEXT_AUTHORIZED_ACTION="VALIDATE")
        handoff["VALIDATED_FACTS"] = ({"claim": "worker", "provenance": "WORKER_REPORTED"},); validate_handoff(handoff)
        evidence = {"reference": "test:1", "validator": "body"}
        accepted = accept_claims(handoff["VALIDATED_FACTS"] + ({"claim": "det", "provenance": "DETERMINISTICALLY_VALIDATED", "evidence_reference": evidence}, {"claim": "seen", "provenance": "DIRECTLY_OBSERVED", "evidence_reference": {"reference": "log:1", "validator": "body"}}), {"test:1": {"provenance": "DETERMINISTICALLY_VALIDATED", "result": "PASS", "validator": "body"}, "log:1": {"provenance": "DIRECTLY_OBSERVED", "result": "PASS", "validator": "body"}})
        self.assertEqual({x["claim"] for x in accepted}, {"det", "seen"})
        self.assertEqual(accept_claims(({"claim": "fake", "provenance": "DETERMINISTICALLY_VALIDATED", "evidence_reference": {"reference": "missing", "validator": "body"}},), {}), ())
        with self.assertRaises(ValueError): validate_handoff({**handoff, "VALIDATED_FACTS": ({"claim": "x"},)})

    def test_plan_and_handoff_reject_wrong_types(self):
        with self.assertRaises(ValueError): accept_and_seal_plan({**PLAN, "objective": 1}, PLAN["task_id"])
        with self.assertRaises(ValueError): accept_and_seal_plan({**PLAN, "scope": ["ok", {}]}, PLAN["task_id"])
        with self.assertRaises(ValueError): accept_and_seal_plan({**PLAN, "steps": [{**step("S1"), "actions": [{}]}]}, PLAN["task_id"])
        with self.assertRaises(ValueError): accept_and_seal_plan({**PLAN, "handoff": [{"field": "not-a-typed-handoff"}]}, PLAN["task_id"])
        handoff = {field: [] for field in HANDOFF_FIELDS}; handoff.update(STATUS="PASS", NEXT_AUTHORIZED_ACTION="VALIDATE")
        with self.assertRaises(ValueError): validate_handoff({**handoff, "WORK_PERFORMED": None})
        with self.assertRaises(ValueError): validate_handoff({**handoff, "VALIDATED_FACTS": ({"claim": "x", "provenance": "WORKER_REPORTED"},)})

    def test_terminal_receipt_rejects_untyped_counts_and_noncardinal_runs(self):
        with self.assertRaises(ValueError): terminal_receipt(TASK_RESULT="REJECTED", EXECUTION_MODE="SHARED_CONTEXT_DEGRADED", OBSERVED_CONTEXT_STATUS="CONTEXT_ISOLATION_UNKNOWN", BLOCKERS={})
        with self.assertRaises(ValueError): terminal_receipt(TASK_RESULT="REJECTED", EXECUTION_MODE="SHARED_CONTEXT_DEGRADED", OBSERVED_CONTEXT_STATUS="CONTEXT_ISOLATION_UNKNOWN", RUNSKEPTIC_QUALIFYING_PASSES="0")
        with self.assertRaises(ValueError): terminal_receipt(TASK_RESULT="ACCEPTED", PLAN_INTEGRITY="PASS", DETERMINISTIC_VALIDATION="PASS", REVIEW_RESULT="PASS", EXECUTION_MODE="SHARED_CONTEXT_DEGRADED", OBSERVED_CONTEXT_STATUS="CONTEXT_ISOLATION_UNKNOWN", BOUNDARY_PROCESSING_STATUS="PASS", CHECKPOINT_AND_RESUME_STATUS="PASS", DETERMINISTIC_LIFECYCLE_SIMULATION="PASS", DETERMINISTIC_BOUNDARY_SIMULATION="PASS", REAL_INTERRUPTION_RESUME_EXERCISE="PASS", REAL_AGENT_BOUNDARY_EXERCISE="PASS", BLOCKERS="NONE", RUNSKEPTIC_MODEL_PER_RUN=["GPT-5.6"], RUNSKEPTIC_REASONING_LEVEL_PER_RUN=["HIGH"], RUNSKEPTIC_CONTEXT_STATUS_PER_RUN=["UNKNOWN"], RUNSKEPTIC_INDEPENDENCE_PER_RUN=["INDEPENDENT"], RUNSKEPTIC_QUALIFYING_PASSES=3, RUNSKEPTIC_FINAL_CATEGORY="PASS")

    def test_receipt_separates_completion_from_runtime_and_real_exercises(self):
        with self.assertRaises(ValueError): terminal_receipt(TASK_RESULT="ACCEPTED", PLAN_INTEGRITY="PASS", DETERMINISTIC_VALIDATION="PASS", REVIEW_RESULT="NOT_RUN", EXECUTION_MODE="SHARED_CONTEXT_DEGRADED", OBSERVED_CONTEXT_STATUS="CONTEXT_ISOLATION_UNKNOWN", ACTUAL_RUNTIME_ISOLATION="UNKNOWN", ACTUAL_CONTEXT_REDUCTION="NOT_CLAIMED", REAL_INTERRUPTION_RESUME_EXERCISE="BLOCKED", BLOCKERS=())
        receipt = terminal_receipt(TASK_RESULT="REJECTED", PLAN_INTEGRITY="PASS", DETERMINISTIC_VALIDATION="PASS", REVIEW_RESULT="NOT_RUN", EXECUTION_MODE="SHARED_CONTEXT_DEGRADED", OBSERVED_CONTEXT_STATUS="CONTEXT_ISOLATION_UNKNOWN", ACTUAL_RUNTIME_ISOLATION="UNKNOWN", ACTUAL_CONTEXT_REDUCTION="NOT_CLAIMED", REAL_INTERRUPTION_RESUME_EXERCISE="BLOCKED", BLOCKERS=())
        self.assertEqual(receipt["TASK_RESULT"], "REJECTED"); self.assertIn("REAL_AGENT_BOUNDARY_EXERCISE", receipt)
        with self.assertRaises(ValueError): terminal_receipt(TASK_RESULT="ACCEPTED", PLAN_INTEGRITY="PASS", DETERMINISTIC_VALIDATION="PASS", BLOCKERS=(), EXECUTION_MODE="SHARED_CONTEXT_DEGRADED", BOUNDARY_PROCESSING_STATUS="PASS", CHECKPOINT_AND_RESUME_STATUS="PASS", REVIEW_RESULT="PASS", DETERMINISTIC_LIFECYCLE_SIMULATION="PASS", DETERMINISTIC_BOUNDARY_SIMULATION="PASS", REAL_INTERRUPTION_RESUME_EXERCISE="NOT_REQUIRED", REAL_AGENT_BOUNDARY_EXERCISE="NOT_REQUIRED")

if __name__ == "__main__": unittest.main()
