import unittest

from stt_mvp.records import validate_ref, validate_source_selector


class RecordTests(unittest.TestCase):
    def test_reference_hash_and_event_are_closed(self):
        value = {
            "schema": "RecordRef@1", "record_id": "r", "task_id": "t",
            "ledger_sequence": 0, "event_kind": "TASK_CREATED",
            "transition_id": "x", "payload_path": "p", "size_bytes": 1,
            "sha256": "00" * 32,
        }
        self.assertIs(validate_ref(value, "RecordRef"), value)
        for field, bad in (("sha256", "hex"), ("event_kind", "NOT_AN_EVENT")):
            candidate = dict(value)
            candidate[field] = bad
            with self.assertRaises(ValueError):
                validate_ref(candidate, "RecordRef")

    def test_embedded_schema_is_not_record_kind(self):
        value = {"kind": "RECORD", "source_identity": "s", "record_kind": "Step", "record_id": "r"}
        with self.assertRaises(ValueError):
            validate_source_selector(value)

    def test_producer_constraint_variants_are_closed(self):
        base = {"kind": "REQUIREMENT", "source_identity": "s", "requirement_id": "r"}
        for constraint in (
            {"kind": "ANY_ADMITTED_PRODUCER"},
            {"kind": "STEP", "step_id": "step"},
            {"kind": "ROUTE", "route_name": "route"},
            {"kind": "OPERATION_ROLE", "role": "WORKER"},
        ):
            value = dict(base, producer_constraint=constraint)
            self.assertIs(validate_source_selector(value), value)
