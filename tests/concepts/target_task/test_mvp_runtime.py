import json
import tempfile
import unittest
from pathlib import Path

from concepts.target_task.boundary import admit_operation, new_step_cursor, record_validated_host_outcome
from concepts.target_task.contracts import CursorStatus
from concepts.target_task.runtime import (
    RuntimeAdapterError,
    prepare_host_role_dispatch,
    validate_host_role_receipt,
)
from concepts.target_task.store import write_immutable_artifact


class HostReceiptBindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        request = {
            "schema_version": "1",
            "task_id": "task-1",
            "operation_id": "op-1",
            "attempt": 1,
            "role": "worker",
            "step_id": "s1",
            "objective": "perform the bounded step",
            "scope": "one declared result artifact",
            "authority": "write-source",
            "prohibitions": ["do not change task control artifacts"],
            "success_criteria": ["write the exact declared result"],
            "task_artifact_references": [],
            "source_artifact_references": [],
            "result_relative_path": "results/manifests/op-1.json",
        }
        dispatch = prepare_host_role_dispatch(request, task_root=self.root, source_root=self.root)
        self.request_ref = dispatch["request_ref"]
        self.evidence_ref = dispatch["dispatch_evidence_ref"]
        output_ref = write_immutable_artifact(
            self.root,
            "results/op-1.md",
            b"full substantive body",
            reference_id="result-op-1",
            artifact_type="step_result",
            description="worker output",
            read_condition="review the completed step",
        )
        routing_ref = write_immutable_artifact(
            self.root,
            "evidence/op-1-routing.json",
            b"routing",
            reference_id="routing-op-1",
            artifact_type="routing_evidence",
            description="routing evidence",
            read_condition="validate the host receipt",
        )
        manifest = {
            "schema_version": "1",
            "task_id": "task-1",
            "operation_id": "op-1",
            "attempt": 1,
            "role": "worker",
            "step_id": "s1",
            "status": "COMPLETE",
            "output_references": [output_ref, routing_ref],
        }
        manifest_raw = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
        self.result_ref = write_immutable_artifact(
            self.root,
            "results/manifests/op-1.json",
            manifest_raw,
            reference_id="manifest-op-1",
            artifact_type="role_result_manifest",
            description="bounded worker result manifest",
            read_condition="validate the host receipt",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def receipt(self, **overrides):
        value = {
            "schema_version": "1",
            "task_id": "task-1",
            "operation_id": "op-1",
            "attempt": 1,
            "role": "worker",
            "step_id": "s1",
            "status": "COMPLETE",
            "summary": "done",
            "request_ref": self.request_ref,
            "result_ref": self.result_ref,
            "dispatch_evidence_ref": self.evidence_ref,
            "synthetic": False,
        }
        value.update(overrides)
        return value

    def validate(self, receipt):
        return validate_host_role_receipt(
            receipt,
            workspace_root=self.root,
            source_root=self.root,
            expected_task_id="task-1",
            expected_operation_id="op-1",
            expected_attempt=1,
            expected_role="worker",
            expected_step_id="s1",
            expected_request_ref=self.request_ref,
        )

    def test_valid_receipt_and_explicit_advance_boundary(self):
        cursor = admit_operation(new_step_cursor(("s1",)), "op-1")
        cursor = record_validated_host_outcome(
            cursor,
            self.receipt(),
            workspace_root=self.root,
            source_root=self.root,
            expected_task_id="task-1",
            expected_role="worker",
            expected_step_id="s1",
            expected_request_ref=self.request_ref,
        )
        self.assertEqual(cursor.status, CursorStatus.STEP_AWAITING_ADVANCE)

    def test_each_dispatch_binding_mismatch_is_rejected_without_state_change(self):
        cases = {
            "task_id": "task-2",
            "operation_id": "op-2",
            "attempt": 2,
            "role": "reviewer",
            "step_id": "s2",
        }
        for field, bad in cases.items():
            with self.subTest(field=field), self.assertRaises(RuntimeAdapterError):
                self.validate(self.receipt(**{field: bad}))
        other_request = write_immutable_artifact(
            self.root,
            "requests/other.json",
            b"{}\n",
            reference_id="other",
            artifact_type="role_request",
            description="other",
            read_condition="dispatch",
        )
        with self.assertRaises(RuntimeAdapterError):
            self.validate(self.receipt(request_ref=other_request))

    def test_dispatch_evidence_content_must_match(self):
        bad = dict(self.receipt())
        evidence = json.loads((self.root / self.evidence_ref["repository_relative_path"]).read_text())
        evidence["role"] = "reviewer"
        content = (json.dumps(evidence, sort_keys=True, separators=(",", ":")) + "\n").encode()
        bad_ref = write_immutable_artifact(
            self.root,
            "dispatch/bad.json",
            content,
            reference_id="bad",
            artifact_type="dispatch_evidence",
            description="bad",
            read_condition="validate",
        )
        bad["dispatch_evidence_ref"] = bad_ref
        with self.assertRaises(RuntimeAdapterError):
            self.validate(bad)

    def test_body_field_oversize_and_synthetic_production_are_rejected(self):
        extra = self.receipt()
        extra["body"] = "leak"
        with self.assertRaises(RuntimeAdapterError):
            self.validate(extra)
        with self.assertRaises(RuntimeAdapterError):
            self.validate(self.receipt(summary="x" * 513))
        synthetic = self.receipt(synthetic=True, dispatch_evidence_ref=None)
        with self.assertRaises(RuntimeAdapterError):
            self.validate(synthetic)


if __name__ == "__main__":
    unittest.main()
