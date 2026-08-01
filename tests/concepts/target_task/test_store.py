import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from concepts.target_task.contracts import CursorStatus, LedgerEvent, LunaAction, Phase, StepCursor, canonical_bytes
from concepts.target_task.store import (
    AppendOnlyLedger,
    RecoveryResult,
    StoreError,
    load_cursor_snapshot,
    persist_cursor_snapshot,
    read_ledger,
    recover_torn_tail,
    verify_chain,
    write_content_addressed_artifact,
    write_immutable_artifact,
)


def make_event(sequence=0, previous_event_hash=None, **overrides):
    fields = dict(
        schema_version="1", sequence=sequence, event_id=f"ev-{sequence}", task_id="task-1",
        phase=Phase.MISSION_PERSISTED.value, accepted_plan_ref=None, current_step=None,
        operation_id=None, attempt=0, request_ref=None, result_ref=None, cursor_ref=None,
        status="COMPLETE", validation="PASS", blocker=None,
        allowed_actions=(LunaAction.CONTINUE.value,), next_action=LunaAction.CONTINUE.value,
        previous_event_hash=previous_event_hash, receipt_ref=None,
    )
    fields.update(overrides)
    return LedgerEvent(**fields)


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_private_create_only_artifact(self):
        ref = write_immutable_artifact(self.root, "a.txt", b"x", reference_id="a", artifact_type="t", description="d", read_condition="r")
        self.assertEqual(ref["sha256"], hashlib.sha256(b"x").hexdigest())
        self.assertEqual((self.root / "a.txt").stat().st_mode & 0o777, 0o600)
        with self.assertRaises(StoreError):
            write_immutable_artifact(self.root, "a.txt", b"y", reference_id="b", artifact_type="t", description="d", read_condition="r")

    def test_traversal_and_symlink_are_rejected(self):
        with self.assertRaises(StoreError):
            write_immutable_artifact(self.root, "../x", b"x", reference_id="a", artifact_type="t", description="d", read_condition="r")
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / "link").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(StoreError):
            write_immutable_artifact(self.root, "link/x", b"x", reference_id="a", artifact_type="t", description="d", read_condition="r")

    def test_content_addressed_reuse_is_idempotent(self):
        a = write_content_addressed_artifact(self.root, "mission", ".txt", b"same", reference_id="m", artifact_type="mission", description="d", read_condition="r")
        b = write_content_addressed_artifact(self.root, "mission", ".txt", b"same", reference_id="m", artifact_type="mission", description="d", read_condition="r")
        self.assertEqual(a, b)

    def test_cursor_snapshot_round_trip(self):
        cursor = StepCursor(("s1",), status=CursorStatus.OPERATION_ADMITTED, operation_id="op-1", attempt=1)
        ref = persist_cursor_snapshot(self.root, cursor)
        self.assertEqual(load_cursor_snapshot(self.root, ref["repository_relative_path"]), cursor)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "ledger.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def test_chain_and_first_directory_fsync(self):
        with patch("concepts.target_task.store._fsync_dir") as fsync:
            ledger = AppendOnlyLedger(self.path)
            first = ledger.append(make_event())
        fsync.assert_called_once_with(self.path.parent)
        second = ledger.append(make_event(1, first.head_hash))
        self.assertEqual(second.event.sequence, 1)
        self.assertTrue(verify_chain(read_ledger(self.path), expected_task_id="task-1"))

    def test_torn_tail_blocks_append_until_recovery(self):
        ledger = AppendOnlyLedger(self.path)
        first = ledger.append(make_event())
        with self.path.open("ab") as stream:
            stream.write(b'{"sequence":1')
        with self.assertRaises(StoreError):
            ledger.append(make_event(1, first.head_hash))
        result = recover_torn_tail(self.path)
        self.assertEqual(result, RecoveryResult(True, 1))
        ledger.append(make_event(1, first.head_hash))

    def test_complete_json_without_newline_is_torn(self):
        event = make_event().to_dict()
        self.path.write_bytes(canonical_bytes(event))
        with self.assertRaises(StoreError):
            read_ledger(self.path)

    def test_noncanonical_and_duplicate_keys_are_rejected(self):
        event = make_event().to_dict()
        noncanonical = json.dumps(event, indent=2).encode() + b"\n"
        self.path.write_bytes(noncanonical)
        with self.assertRaises(StoreError):
            read_ledger(self.path)
        self.path.write_bytes(b'{"schema_version":"1","schema_version":"1"}\n')
        with self.assertRaises(StoreError):
            read_ledger(self.path)

    def test_cross_task_chain_is_rejected(self):
        first = AppendOnlyLedger(self.path).append(make_event())
        with self.assertRaises(StoreError):
            AppendOnlyLedger(self.path).append(make_event(1, first.head_hash, task_id="task-2"))


if __name__ == "__main__":
    unittest.main()
