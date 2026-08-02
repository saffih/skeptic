from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from concepts.stt.canonical import atomic_write, canonical_json_bytes, sha256_bytes
from concepts.stt.errors import STTError
from concepts.stt.ledger import Ledger


def payload(root: Path, name: str, value: dict) -> tuple[str, str]:
    data = canonical_json_bytes(value)
    atomic_write(root / name, data, create_only=True)
    return name, sha256_bytes(data)


class LedgerTests(unittest.TestCase):
    def test_append_and_partial_suffix_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); ledger = Ledger(root, "task"); ledger.initialize()
            ref, digest = payload(root, "task.json", {"schema_version": 1})
            first = ledger.append("TASK_CREATED", ref, digest)
            self.assertEqual(first.value["sequence"], 1)
            with ledger.path.open("ab") as handle:
                handle.write(b'{"broken"')
            self.assertEqual(len(ledger.read(recover_partial=True)), 1)

    def test_pending_event_recovered_on_initialize(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); ledger = Ledger(root, "task"); ledger.initialize()
            first_ref, first_sha = payload(root, "task.json", {"schema_version": 1})
            ledger.append("TASK_CREATED", first_ref, first_sha)
            second_ref, second_sha = payload(root, "methodology.json", {"schema_version": 1, "source": "bound"})
            events = ledger.read()
            value = ledger._event_with_hash(sequence=2, event_type="METHODOLOGY_BOUND", payload_ref=second_ref, payload_sha256=second_sha, previous=events[-1].event_sha256)
            atomic_write(ledger.pending, canonical_json_bytes(value), create_only=True)
            Ledger(root, "task").initialize()
            self.assertEqual([event.value["event_type"] for event in ledger.read()], ["TASK_CREATED", "METHODOLOGY_BOUND"])
            self.assertFalse(ledger.pending.exists())

    def test_committed_malformed_line_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); ledger = Ledger(root, "task"); ledger.initialize(); ledger.path.write_bytes(b"not-json\n")
            with self.assertRaises(STTError):
                ledger.read(recover_partial=True)

    def test_missing_committed_payload_is_corruption(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); ledger = Ledger(root, "task"); ledger.initialize()
            ref, digest = payload(root, "task.json", {"schema_version": 1})
            ledger.append("TASK_CREATED", ref, digest); (root / ref).unlink()
            with self.assertRaises(STTError) as caught:
                ledger.read()
            self.assertEqual(caught.exception.code, "LEDGER_PAYLOAD_MISSING")

    def test_symlink_and_malformed_json_payloads_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); ledger = Ledger(root, "task"); ledger.initialize()
            target = root / "target.json"; atomic_write(target, b"{}\n", create_only=True)
            (root / "link.json").symlink_to(target)
            with self.assertRaises(STTError) as caught:
                ledger.append("TASK_CREATED", "link.json", sha256_bytes(b"{}\n"))
            self.assertEqual(caught.exception.code, "LEDGER_PAYLOAD_UNSAFE")
            atomic_write(root / "malformed.json", b"not-json", create_only=True)
            with self.assertRaises(STTError) as caught:
                ledger.append("TASK_CREATED", "malformed.json", sha256_bytes(b"not-json"))
            self.assertEqual(caught.exception.code, "MALFORMED_JSON")

    def test_event_after_nonresumable_block_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); ledger = Ledger(root, "task"); ledger.initialize()
            first_ref, first_sha = payload(root, "blocked.json", {"schema_version": 1, "operation_id": "op"})
            ledger.append("TASK_BLOCKED_UNKNOWN", first_ref, first_sha)
            later_ref, later_sha = payload(root, "later.json", {"schema_version": 1})
            with self.assertRaises(STTError) as caught:
                ledger.append("TASK_STOPPED", later_ref, later_sha)
            self.assertEqual(caught.exception.code, "CONTROL_STATE_TERMINAL")


if __name__ == "__main__":
    unittest.main()
