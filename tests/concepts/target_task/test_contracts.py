import unittest

from concepts.target_task.contracts import (
    ContractError,
    LedgerEvent,
    LunaAction,
    Phase,
    canonical_bytes,
)


def make_event(**overrides):
    fields = dict(
        schema_version="1",
        sequence=0,
        event_id="ev-0",
        task_id="task-1",
        phase=Phase.MISSION_PERSISTED.value,
        accepted_plan_ref=None,
        current_step=None,
        operation_id=None,
        attempt=1,
        request_ref=None,
        result_ref="mission.md",
        status="COMPLETE",
        validation="PASS",
        blocker=None,
        allowed_actions=(LunaAction.CONTINUE.value,),
        next_action=LunaAction.CONTINUE.value,
        previous_event_hash=None,
        receipt_ref=None,
    )
    fields.update(overrides)
    return LedgerEvent(**fields)


class LedgerEventTests(unittest.TestCase):
    def test_round_trip_through_dict(self) -> None:
        event = make_event()
        restored = LedgerEvent.from_dict(event.to_dict())
        self.assertEqual(event, restored)

    def test_to_dict_has_exact_field_set(self) -> None:
        from concepts.target_task.contracts import LEDGER_EVENT_FIELDS

        self.assertEqual(set(make_event().to_dict()), LEDGER_EVENT_FIELDS)

    def test_missing_field_is_rejected(self) -> None:
        data = make_event().to_dict()
        del data["status"]
        with self.assertRaises(ContractError):
            LedgerEvent.from_dict(data)

    def test_extra_field_is_rejected(self) -> None:
        data = make_event().to_dict()
        data["unexpected"] = "value"
        with self.assertRaises(ContractError):
            LedgerEvent.from_dict(data)

    def test_negative_sequence_is_rejected(self) -> None:
        with self.assertRaises(ContractError):
            LedgerEvent.from_dict(make_event(sequence=-1).to_dict())

    def test_zero_attempt_is_rejected(self) -> None:
        with self.assertRaises(ContractError):
            LedgerEvent.from_dict(make_event(attempt=0).to_dict())

    def test_unknown_phase_is_rejected(self) -> None:
        with self.assertRaises(ContractError):
            LedgerEvent.from_dict(make_event(phase="NOT_A_PHASE").to_dict())

    def test_empty_allowed_actions_is_rejected(self) -> None:
        with self.assertRaises(ContractError):
            LedgerEvent.from_dict(make_event(allowed_actions=()).to_dict())

    def test_unknown_allowed_action_is_rejected(self) -> None:
        with self.assertRaises(ContractError):
            LedgerEvent.from_dict(make_event(allowed_actions=("FLY_AWAY",)).to_dict())

    def test_non_hex_previous_event_hash_is_rejected(self) -> None:
        with self.assertRaises(ContractError):
            LedgerEvent.from_dict(make_event(previous_event_hash="not-a-hash").to_dict())

    def test_valid_previous_event_hash_is_accepted(self) -> None:
        digest = "a" * 64
        event = LedgerEvent.from_dict(make_event(sequence=1, previous_event_hash=digest).to_dict())
        self.assertEqual(event.previous_event_hash, digest)


class CanonicalBytesTests(unittest.TestCase):
    def test_deterministic_for_equal_content(self) -> None:
        a = make_event().to_dict()
        b = dict(reversed(list(make_event().to_dict().items())))
        self.assertEqual(canonical_bytes(a), canonical_bytes(b))

    def test_no_trailing_newline(self) -> None:
        raw = canonical_bytes(make_event().to_dict())
        self.assertFalse(raw.endswith(b"\n"))

    def test_invalid_event_is_rejected(self) -> None:
        data = make_event().to_dict()
        del data["status"]
        with self.assertRaises(ContractError):
            canonical_bytes(data)

    def test_oversized_event_is_rejected(self) -> None:
        data = make_event(blocker="x" * 5000).to_dict()
        with self.assertRaises(ContractError):
            canonical_bytes(data)


if __name__ == "__main__":
    unittest.main()
