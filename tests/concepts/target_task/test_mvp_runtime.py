import hashlib
import tempfile
import unittest
from pathlib import Path

from concepts.target_task.boundary import (
    BoundaryError,
    admit_operation,
    advance_step,
    new_step_cursor,
    record_operation_outcome,
    record_validated_host_outcome,
    recover_operation,
    retry_operation,
)
from concepts.target_task.contracts import CursorStatus
from concepts.target_task.runtime import RuntimeAdapterError, validate_host_role_receipt
from concepts.target_task.trigger import TriggerError, bootstrap_task, parse_trigger, rediscover_task


class ExactTriggerTests(unittest.TestCase):
    def test_suffix_whitespace_is_preserved(self):
        self.assertEqual(parse_trigger("  TT:  mission  \n"), "  mission  \n")

    def test_unicode_round_trip_is_preserved(self):
        mission = " משימה café 🚀\n"
        self.assertEqual(parse_trigger("TT:" + mission).encode("utf-8"), mission.encode("utf-8"))

    def test_whitespace_only_suffix_is_rejected(self):
        with self.assertRaises(TriggerError):
            parse_trigger("TT:\t \n")

    def test_fresh_session_rediscovery_uses_only_root_and_task_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            boot = bootstrap_task(" exact mission ", "task-1", root)
            found = rediscover_task(root, "task-1")
            self.assertEqual(found.workspace_root, boot.workspace_root)
            self.assertEqual(found.task_id, "task-1")
            self.assertEqual(found.phase, "MISSION_PERSISTED")
            self.assertEqual(found.ledger_head_hash, boot.ledger_head_hash)


class LinearCursorTests(unittest.TestCase):
    def test_two_steps_require_explicit_advance(self):
        cursor = new_step_cursor(("s1", "s2"))
        cursor = admit_operation(cursor, "op-1")
        cursor = record_operation_outcome(cursor, "op-1", "COMPLETE")
        self.assertEqual(cursor.status, CursorStatus.STEP_AWAITING_ADVANCE)
        self.assertEqual(cursor.current_step, "s1")
        cursor = advance_step(cursor, "op-1")
        self.assertEqual(cursor.current_step, "s2")
        cursor = admit_operation(cursor, "op-2")
        cursor = record_operation_outcome(cursor, "op-2", "COMPLETE")
        cursor = advance_step(cursor, "op-2")
        self.assertEqual(cursor.status, CursorStatus.EXECUTION_COMPLETE)
        self.assertIsNone(cursor.current_step)
        self.assertEqual(cursor.completed_step_ids, ("s1", "s2"))

    def test_duplicate_advance_fails_closed(self):
        cursor = new_step_cursor(("s1", "s2"))
        cursor = admit_operation(cursor, "op-1")
        cursor = record_operation_outcome(cursor, "op-1", "COMPLETE")
        cursor = advance_step(cursor, "op-1")
        with self.assertRaises(BoundaryError):
            advance_step(cursor, "op-1")

    def test_failure_retry_gets_new_admission(self):
        cursor = new_step_cursor(("s1",), max_attempts=2)
        cursor = admit_operation(cursor, "op-1")
        cursor = record_operation_outcome(cursor, "op-1", "FAILED")
        cursor = retry_operation(cursor)
        cursor = admit_operation(cursor, "op-2")
        self.assertEqual(cursor.attempt, 2)
        self.assertEqual(cursor.operation_id, "op-2")

    def test_unknown_cannot_retry_before_recovery(self):
        cursor = new_step_cursor(("s1",))
        cursor = admit_operation(cursor, "op-1")
        cursor = record_operation_outcome(cursor, "op-1", "UNKNOWN")
        with self.assertRaises(BoundaryError):
            retry_operation(cursor)
        cursor = recover_operation(cursor, "COMPLETE")
        self.assertEqual(cursor.status, CursorStatus.STEP_AWAITING_ADVANCE)


class HostReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _ref(self, relative, content, reference_id):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return {
            "reference_id": reference_id,
            "repository_relative_path": relative,
            "sha256": hashlib.sha256(content).hexdigest(),
            "byte_size": len(content),
            "artifact_type": "evidence",
            "description": reference_id,
            "read_condition": "validate receipt",
        }

    def _receipt(self, *, synthetic=False, summary="ok", status="COMPLETE"):
        result_ref = self._ref("results/r.md", b"full substantive body", "result")
        evidence_ref = None if synthetic else self._ref("receipts/dispatch.json", b"{}", "dispatch")
        return {
            "schema_version": "1",
            "task_id": "task-1",
            "operation_id": "op-1",
            "attempt": 1,
            "role": "worker",
            "status": status,
            "summary": summary,
            "result_ref": result_ref,
            "dispatch_evidence_ref": evidence_ref,
            "synthetic": synthetic,
        }

    def test_production_receipt_with_evidence_passes(self):
        validated = validate_host_role_receipt(self._receipt(), workspace_root=self.root)
        self.assertFalse(validated["synthetic"])

    def test_synthetic_receipt_is_rejected_in_production(self):
        with self.assertRaises(RuntimeAdapterError):
            validate_host_role_receipt(self._receipt(synthetic=True), workspace_root=self.root)

    def test_synthetic_receipt_requires_explicit_test_opt_in(self):
        validated = validate_host_role_receipt(
            self._receipt(synthetic=True), workspace_root=self.root, allow_test_synthetic=True
        )
        self.assertTrue(validated["synthetic"])

    def test_synthetic_receipt_cannot_advance_production_cursor(self):
        cursor = admit_operation(new_step_cursor(("s1",)), "op-1")
        with self.assertRaises(RuntimeAdapterError):
            record_validated_host_outcome(cursor, self._receipt(synthetic=True), workspace_root=self.root)
        self.assertEqual(cursor.status, CursorStatus.OPERATION_ADMITTED)

    def test_valid_production_receipt_moves_only_to_awaiting_advance(self):
        cursor = admit_operation(new_step_cursor(("s1",)), "op-1")
        cursor = record_validated_host_outcome(cursor, self._receipt(), workspace_root=self.root)
        self.assertEqual(cursor.status, CursorStatus.STEP_AWAITING_ADVANCE)

    def test_body_bearing_extra_field_is_rejected(self):
        receipt = self._receipt()
        receipt["body"] = "leak"
        with self.assertRaises(RuntimeAdapterError):
            validate_host_role_receipt(receipt, workspace_root=self.root)

    def test_oversized_summary_is_rejected(self):
        with self.assertRaises(RuntimeAdapterError):
            validate_host_role_receipt(self._receipt(summary="x" * 513), workspace_root=self.root)


class HostBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(__file__).resolve().parents[3]

    def test_claude_memory_imports_agents(self):
        text = (self.repo / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("@AGENTS.md", text)
        self.assertIn("workflows/target_task.md", text)

    def test_active_workflow_is_live_mvp(self):
        text = (self.repo / "workflows/target_task.md").read_text(encoding="utf-8")
        self.assertIn("Claude Code MVP", text)
        self.assertNotIn("No live agent runtime executes this automatically", text)
        self.assertIn("final open execution step", text)
        self.assertIn("ROUTING_EVIDENCE_REF", text)

    def test_smoke_script_is_bounded(self):
        text = (self.repo / "scripts/target_task_smoke.sh").read_text(encoding="utf-8")
        self.assertIn("RUN_CLAUDE_SMOKE", text)
        self.assertIn("--max-turns", text)
        self.assertIn("--disallowedTools", text)
        self.assertIn("Bash(git push:*)", text)
        self.assertNotIn("--dangerously-skip-permissions", text)
        self.assertIn("remote remove origin", text)


if __name__ == "__main__":
    unittest.main()
