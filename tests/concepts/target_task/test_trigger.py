import json
import tempfile
import unittest
from pathlib import Path

from concepts.target_task.boundary import (
    admit_operation,
    advance_and_persist_step,
    new_step_cursor_from_plan,
    _persist_cursor_transition as persist_cursor_transition,
    record_validated_host_outcome,
)
from concepts.target_task.contracts import CursorStatus, Phase
from concepts.target_task.runtime import prepare_host_role_dispatch, persist_validated_host_receipt
from concepts.target_task.store import persist_plan_artifact, write_immutable_artifact
from concepts.target_task.trigger import TriggerError, bootstrap_task, parse_trigger, rediscover_task


class TriggerTests(unittest.TestCase):
    def test_exact_suffix_and_unicode(self):
        mission = "  משימה café 🚀\n"
        self.assertEqual(parse_trigger("  TT:" + mission), mission)
        self.assertIsNone(parse_trigger("tt: x"))
        with self.assertRaises(TriggerError):
            parse_trigger("TT: \t")


class BootstrapAndRediscoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tasks = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_content_addressed_mission_detects_tampering(self):
        boot = bootstrap_task(" exact mission ", "task-1", self.tasks)
        found = rediscover_task(self.tasks, "task-1")
        self.assertEqual(found.mission_sha256, boot.mission_sha256)
        mission_path = boot.workspace_root / boot.mission_relative_path
        mission_path.write_text("tampered")
        with self.assertRaises(TriggerError):
            rediscover_task(self.tasks, "task-1")

    def test_task_id_traversal_is_rejected(self):
        for task_id in ("../escape", ".hidden", "a/b"):
            with self.subTest(task_id=task_id), self.assertRaises(TriggerError):
                bootstrap_task("x", task_id, self.tasks)

    def test_complete_cursor_restarts_from_task_root_only(self):
        boot = bootstrap_task("mission", "task-2", self.tasks)
        root = boot.workspace_root
        plan = {
            "schema_version": "1",
            "plan_id": "p-1",
            "task_id": "task-2",
            "mission_sha256": boot.mission_sha256,
            "steps": [
                {
                    "step_id": "s1",
                    "objective": "one",
                    "role": "worker",
                    "success_criteria": ["done"],
                }
            ],
        }
        plan_ref = persist_plan_artifact(root, plan)
        initial = new_step_cursor_from_plan(plan)
        initial_persisted = persist_cursor_transition(
            root,
            "task-2",
            Phase.PLAN_SEALED,
            initial,
            event_id="task-2:ready",
            accepted_plan_reference=plan_ref,
        )

        request = {
            "schema_version": "1",
            "task_id": "task-2",
            "operation_id": "op-1",
            "attempt": 1,
            "role": "worker",
            "step_id": "s1",
            "objective": "execute step one",
            "scope": "one result",
            "authority": "write-source",
            "prohibitions": ["do not modify task control state"],
            "success_criteria": ["produce the declared result"],
            "task_artifact_references": [plan_ref],
            "source_artifact_references": [],
            "result_relative_path": "results/manifests/op-1.json",
        }
        dispatch = prepare_host_role_dispatch(request, task_root=root, source_root=root)
        admitted = admit_operation(initial, "op-1")
        admitted_persisted = persist_cursor_transition(
            root,
            "task-2",
            Phase.STEP_EXECUTING,
            admitted,
            event_id="task-2:op-1-admitted",
            accepted_plan_reference=plan_ref,
            prior_cursor=initial,
            prior_cursor_reference=initial_persisted["cursor_reference"],
            request_reference=dispatch["request_ref"],
            control_evidence_reference=dispatch["dispatch_evidence_ref"],
        )
        mid = rediscover_task(self.tasks, "task-2")
        self.assertEqual(mid.cursor, admitted)
        self.assertEqual(mid.operation_id, "op-1")

        output_ref = write_immutable_artifact(
            root,
            "results/op-1.md",
            b"done",
            reference_id="op-1-output",
            artifact_type="step_result",
            description="step output",
            read_condition="validate step",
        )
        routing_ref = write_immutable_artifact(
            root,
            "evidence/op-1-routing.json",
            b"routing",
            reference_id="routing-op-1",
            artifact_type="routing_evidence",
            description="routing evidence",
            read_condition="validate step",
        )
        manifest = {
            "schema_version": "1",
            "task_id": "task-2",
            "operation_id": "op-1",
            "attempt": 1,
            "role": "worker",
            "step_id": "s1",
            "status": "COMPLETE",
            "output_references": [output_ref, routing_ref],
        }
        manifest_raw = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
        manifest_ref = write_immutable_artifact(
            root,
            "results/manifests/op-1.json",
            manifest_raw,
            reference_id="op-1-manifest",
            artifact_type="role_result_manifest",
            description="result manifest",
            read_condition="validate host receipt",
        )
        receipt = {
            "schema_version": "1",
            "task_id": "task-2",
            "operation_id": "op-1",
            "attempt": 1,
            "role": "worker",
            "step_id": "s1",
            "status": "COMPLETE",
            "summary": "done",
            "request_ref": dispatch["request_ref"],
            "result_ref": manifest_ref,
            "dispatch_evidence_ref": dispatch["dispatch_evidence_ref"],
            "synthetic": False,
        }
        awaiting = record_validated_host_outcome(
            admitted,
            receipt,
            workspace_root=root,
            source_root=root,
            expected_task_id="task-2",
            expected_role="worker",
            expected_step_id="s1",
            expected_request_ref=dispatch["request_ref"],
        )
        receipt_ref = persist_validated_host_receipt(
            receipt,
            workspace_root=root,
            source_root=root,
            expected_task_id="task-2",
            expected_operation_id="op-1",
            expected_attempt=1,
            expected_role="worker",
            expected_step_id="s1",
            expected_request_ref=dispatch["request_ref"],
        )
        awaiting_persisted = persist_cursor_transition(
            root,
            "task-2",
            Phase.STEP_EXECUTING,
            awaiting,
            event_id="task-2:op-1-complete",
            accepted_plan_reference=plan_ref,
            prior_cursor=admitted,
            prior_cursor_reference=admitted_persisted["cursor_reference"],
            request_reference=dispatch["request_ref"],
            result_reference=manifest_ref,
            control_evidence_reference=receipt_ref,
        )
        completed = advance_and_persist_step(
            root,
            "task-2",
            Phase.STEP_EXECUTING,
            awaiting,
            operation_id="op-1",
            event_id="task-2:s1-accepted",
            accepted_plan_reference=plan_ref,
            cursor_reference=awaiting_persisted["cursor_reference"],
            request_reference=dispatch["request_ref"],
            result_reference=manifest_ref,
            host_receipt_reference=receipt_ref,
        )
        self.assertEqual(completed["cursor"].status, CursorStatus.EXECUTION_COMPLETE)
        restarted = rediscover_task(self.tasks, "task-2")
        self.assertEqual(restarted.cursor, completed["cursor"])
        self.assertEqual(restarted.completed_step_ids, ("s1",))


if __name__ == "__main__":
    unittest.main()
