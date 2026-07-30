import unittest

from concepts.target_task.contracts import (
    ContractError,
    CursorStatus,
    LedgerEvent,
    LunaAction,
    Phase,
    StepCursor,
    canonical_bytes,
    canonical_cursor_bytes,
    canonical_plan_bytes,
    parse_cursor_bytes,
    parse_plan_bytes,
    plan_step_ids,
    validate_task_id,
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
        attempt=0,
        request_ref=None,
        result_ref="mission/" + "a" * 64 + ".txt",
        cursor_ref=None,
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
    def test_round_trip_and_exact_fields(self):
        event = make_event()
        self.assertEqual(LedgerEvent.from_dict(event.to_dict()), event)

    def test_missing_extra_and_unknown_values_are_rejected(self):
        data = make_event().to_dict()
        del data["status"]
        with self.assertRaises(ContractError):
            LedgerEvent.from_dict(data)
        data = make_event().to_dict()
        data["extra"] = "x"
        with self.assertRaises(ContractError):
            LedgerEvent.from_dict(data)
        with self.assertRaises(ContractError):
            LedgerEvent.from_dict(make_event(status="WHATEVER").to_dict())
        with self.assertRaises(ContractError):
            LedgerEvent.from_dict(make_event(validation="MAYBE").to_dict())

    def test_safe_task_id_is_enforced(self):
        self.assertEqual(validate_task_id("TT-123_ok"), "TT-123_ok")
        for bad in ("../escape", ".hidden", "a/b", "", "x" * 65):
            with self.subTest(bad=bad), self.assertRaises(ContractError):
                validate_task_id(bad)

    def test_closed_event_has_no_actions(self):
        event = make_event(
            phase=Phase.CLOSED.value,
            status="CLOSED",
            allowed_actions=(),
            next_action=None,
        )
        self.assertEqual(LedgerEvent.from_dict(event.to_dict()), event)
        with self.assertRaises(ContractError):
            LedgerEvent.from_dict(make_event(phase=Phase.CLOSED.value, status="CLOSED").to_dict())

    def test_canonical_bytes_are_deterministic(self):
        a = make_event().to_dict()
        b = dict(reversed(list(a.items())))
        self.assertEqual(canonical_bytes(a), canonical_bytes(b))
        self.assertFalse(canonical_bytes(a).endswith(b"\n"))


class PlanContractTests(unittest.TestCase):
    def plan(self):
        return {
            "schema_version": "1",
            "plan_id": "plan-1",
            "task_id": "task-1",
            "mission_sha256": "a" * 64,
            "steps": [
                {"step_id": "s1", "objective": "create file", "role": "worker", "success_criteria": ["file exists"]},
                {"step_id": "s2", "objective": "validate", "role": "command", "success_criteria": ["exact content"]},
            ],
        }

    def test_plan_round_trip_and_step_ids(self):
        raw = canonical_plan_bytes(self.plan())
        parsed = parse_plan_bytes(raw)
        self.assertEqual(plan_step_ids(parsed), ("s1", "s2"))

    def test_duplicate_steps_and_noncanonical_bytes_are_rejected(self):
        plan = self.plan()
        plan["steps"][1]["step_id"] = "s1"
        with self.assertRaises(ContractError):
            canonical_plan_bytes(plan)
        raw = canonical_plan_bytes(self.plan()).replace(b'"plan_id":"plan-1"', b'"plan_id" : "plan-1"')
        with self.assertRaises(ContractError):
            parse_plan_bytes(raw)


class CursorContractTests(unittest.TestCase):
    def test_every_state_round_trips(self):
        cursors = [
            StepCursor(("s1", "s2")),
            StepCursor(("s1", "s2"), status=CursorStatus.OPERATION_ADMITTED, operation_id="op-1", attempt=1),
            StepCursor(("s1", "s2"), status=CursorStatus.OPERATION_FAILED, operation_id="op-1", attempt=1),
            StepCursor(("s1", "s2"), status=CursorStatus.EXECUTION_OUTCOME_UNKNOWN, operation_id="op-1", attempt=1),
            StepCursor(("s1", "s2"), status=CursorStatus.STEP_AWAITING_ADVANCE, operation_id="op-1", successful_operation_id="op-1", attempt=1),
            StepCursor(("s1", "s2"), current_index=2, status=CursorStatus.EXECUTION_COMPLETE, completed_step_ids=("s1", "s2")),
        ]
        for cursor in cursors:
            with self.subTest(status=cursor.status):
                self.assertEqual(parse_cursor_bytes(canonical_cursor_bytes(cursor)), cursor)

    def test_inconsistent_cursor_is_rejected(self):
        with self.assertRaises(ContractError):
            StepCursor(("s1",), status=CursorStatus.OPERATION_ADMITTED)
        with self.assertRaises(ContractError):
            StepCursor(("s1",), current_index=1, status=CursorStatus.STEP_READY, completed_step_ids=("s1",))


if __name__ == "__main__":
    unittest.main()
