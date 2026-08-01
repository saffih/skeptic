from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from concepts.stt.ledger import Ledger
from concepts.stt.errors import STTError


class LedgerTests(unittest.TestCase):
    def test_append_and_partial_suffix_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); ledger = Ledger(root, "task"); ledger.initialize()
            first = ledger.append("TASK_CREATED", "task.json", "a" * 64)
            self.assertEqual(first.value["sequence"], 1)
            with ledger.path.open("ab") as handle: handle.write(b'{"broken"')
            events = ledger.read(recover_partial=True)
            self.assertEqual(len(events), 1)

    def test_pending_event_recovered_on_initialize(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); ledger = Ledger(root, "task"); ledger.initialize()
            ledger.append("TASK_CREATED", "task.json", "a" * 64)
            events = ledger.read()
            value = ledger._event_with_hash(sequence=2, event_type="NEXT", payload_ref="x.json", payload_sha256="b" * 64, previous=events[-1].event_sha256)
            from concepts.stt.canonical import atomic_write, canonical_json_bytes
            atomic_write(ledger.pending, canonical_json_bytes(value), create_only=True)
            Ledger(root, "task").initialize()
            self.assertEqual([e.value["event_type"] for e in ledger.read()], ["TASK_CREATED", "NEXT"])
            self.assertFalse(ledger.pending.exists())

    def test_committed_malformed_line_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); ledger = Ledger(root, "task"); ledger.initialize()
            ledger.path.write_bytes(b'not-json\n')
            with self.assertRaises(STTError): ledger.read(recover_partial=True)
