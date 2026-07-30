import hashlib
import tempfile
import unittest
from pathlib import Path

from concepts.target_task.contracts import LedgerEvent, LunaAction, Phase
from concepts.target_task.store import (
    AppendOnlyLedger,
    RecoveryResult,
    StoreError,
    read_ledger,
    recover_torn_tail,
    verify_chain,
    write_immutable_artifact,
)


def make_event(sequence, previous_event_hash, **overrides):
    fields = dict(
        schema_version="1",
        sequence=sequence,
        event_id=f"ev-{sequence}",
        task_id="task-1",
        phase=Phase.MISSION_PERSISTED.value,
        accepted_plan_ref=None,
        current_step=None,
        operation_id=None,
        attempt=1,
        request_ref=None,
        result_ref=None,
        status="COMPLETE",
        validation="PASS",
        blocker=None,
        allowed_actions=(LunaAction.CONTINUE.value,),
        next_action=LunaAction.CONTINUE.value,
        previous_event_hash=previous_event_hash,
        receipt_ref=None,
    )
    fields.update(overrides)
    return LedgerEvent(**fields)


class WriteImmutableArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_write_then_hash_matches(self) -> None:
        ref = write_immutable_artifact(
            self.workspace, "mission.md", b"do the thing",
            reference_id="mission", artifact_type="mission", description="d", read_condition="r",
        )
        self.assertEqual(ref["sha256"], hashlib.sha256(b"do the thing").hexdigest())
        self.assertEqual(ref["byte_size"], len(b"do the thing"))
        self.assertEqual((self.workspace / "mission.md").read_bytes(), b"do the thing")

    def test_second_write_to_same_path_is_rejected(self) -> None:
        write_immutable_artifact(self.workspace, "a.txt", b"1", reference_id="a", artifact_type="t", description="d", read_condition="r")
        with self.assertRaises(StoreError):
            write_immutable_artifact(self.workspace, "a.txt", b"2", reference_id="a2", artifact_type="t", description="d", read_condition="r")

    def test_traversal_is_rejected(self) -> None:
        with self.assertRaises(StoreError):
            write_immutable_artifact(self.workspace, "../escape.txt", b"x", reference_id="a", artifact_type="t", description="d", read_condition="r")

    def test_absolute_path_is_rejected(self) -> None:
        with self.assertRaises(StoreError):
            write_immutable_artifact(self.workspace, "/etc/passwd", b"x", reference_id="a", artifact_type="t", description="d", read_condition="r")

    def test_nested_directory_is_created(self) -> None:
        ref = write_immutable_artifact(self.workspace, "steps/step-1/result.md", b"x", reference_id="s1", artifact_type="t", description="d", read_condition="r")
        self.assertTrue((self.workspace / "steps/step-1/result.md").is_file())
        self.assertEqual(ref["repository_relative_path"], "steps/step-1/result.md")


class AppendOnlyLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger_path = Path(self.tmp.name) / "ledger.jsonl"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_first_append_requires_no_previous_hash(self) -> None:
        ledger = AppendOnlyLedger(self.ledger_path)
        result = ledger.append(make_event(0, None))
        self.assertEqual(result.event.sequence, 0)
        events = read_ledger(self.ledger_path)
        self.assertEqual(len(events), 1)
        self.assertTrue(verify_chain(events))

    def test_chain_extends_correctly(self) -> None:
        ledger = AppendOnlyLedger(self.ledger_path)
        first = ledger.append(make_event(0, None))
        second = ledger.append(make_event(1, first.head_hash))
        ledger.append(make_event(2, second.head_hash))
        events = read_ledger(self.ledger_path)
        self.assertEqual([e["sequence"] for e in events], [0, 1, 2])
        self.assertTrue(verify_chain(events))

    def test_wrong_sequence_is_rejected(self) -> None:
        ledger = AppendOnlyLedger(self.ledger_path)
        ledger.append(make_event(0, None))
        with self.assertRaises(StoreError):
            ledger.append(make_event(2, "a" * 64))

    def test_wrong_previous_hash_is_rejected(self) -> None:
        ledger = AppendOnlyLedger(self.ledger_path)
        ledger.append(make_event(0, None))
        with self.assertRaises(StoreError):
            ledger.append(make_event(1, "b" * 64))

    def test_head_of_empty_ledger(self) -> None:
        ledger = AppendOnlyLedger(self.ledger_path)
        self.assertEqual(ledger.head(), (0, None))


class VerifyChainTests(unittest.TestCase):
    def test_tampered_sequence_fails(self) -> None:
        events = [make_event(0, None).to_dict(), make_event(2, "a" * 64).to_dict()]
        self.assertFalse(verify_chain(events))

    def test_empty_chain_is_valid(self) -> None:
        self.assertTrue(verify_chain([]))


class RecoverTornTailTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger_path = Path(self.tmp.name) / "ledger.jsonl"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_missing_ledger_is_not_recovered(self) -> None:
        result = recover_torn_tail(self.ledger_path)
        self.assertEqual(result, RecoveryResult(recovered=False, valid_event_count=0))

    def test_complete_ledger_is_untouched(self) -> None:
        ledger = AppendOnlyLedger(self.ledger_path)
        ledger.append(make_event(0, None))
        before = self.ledger_path.read_bytes()
        result = recover_torn_tail(self.ledger_path)
        self.assertFalse(result.recovered)
        self.assertEqual(self.ledger_path.read_bytes(), before)

    def test_torn_final_line_is_removed_when_prior_lines_are_valid(self) -> None:
        ledger = AppendOnlyLedger(self.ledger_path)
        first = ledger.append(make_event(0, None))
        with open(self.ledger_path, "ab") as stream:
            stream.write(b'{"sequence":1,"previous_event_hash":"' + first.head_hash.encode() + b'"')  # truncated, no closing brace/newline
        result = recover_torn_tail(self.ledger_path)
        self.assertTrue(result.recovered)
        self.assertEqual(result.valid_event_count, 1)
        events = read_ledger(self.ledger_path)
        self.assertEqual(len(events), 1)
        self.assertTrue(verify_chain(events))

    def test_unrecoverable_when_prior_lines_are_also_invalid(self) -> None:
        with open(self.ledger_path, "wb") as stream:
            stream.write(b"not even json\n")
            stream.write(b'{"still": "torn"')
        with self.assertRaises(StoreError):
            recover_torn_tail(self.ledger_path)


if __name__ == "__main__":
    unittest.main()
