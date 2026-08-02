from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from concepts.stt.runner import Runner
from tests.concepts.stt.stt_test_support import STTHarness, change_step, inspect_step, task_step


class SimulatedProcessInterruption(BaseException):
    pass


CASES = (
    "planner_effect_without_acceptance",
    "planner_accepted_without_review_request",
    "review_effect_without_acceptance",
    "third_plan_review_accepted_without_seal",
    "plan_seal_artifact_without_event",
    "evidence_effect_without_continuation",
    "worker_intent_before_apply",
    "worker_interrupted_during_apply",
    "worker_apply_complete_without_result_effect",
    "worker_result_effect_without_acceptance",
    "worker_accepted_without_next_step",
    "inspect_report_without_event",
    "final_artifacts_without_freeze_event",
    "third_final_review_accepted_without_terminal",
    "terminal_receipt_without_event",
    "planner_superseded_without_replacement",
    "stopped_with_pending_operation",
    "child_complete_without_parent_acceptance",
    "bootstrap_before_atomic_rename",
)


class InterruptionMatrixTests(unittest.TestCase):
    maxDiff = None

    def _write_initial_plan(self, harness: STTHarness, runner: Runner, *, delivery: str = "inspect", steps: list[dict] | None = None) -> None:
        request, ref = harness.pending(runner)
        harness.write_plan(runner, request, ref.sha256, delivery=delivery, steps=steps)

    def _write_pending_review(self, harness: STTHarness, runner: Runner) -> None:
        request, ref = harness.pending(runner); self.assertEqual(request["role"], "reviewer")
        harness.write_review(runner, request, ref.sha256)

    def _stage_third_plan_review_unadvanced(self, harness: STTHarness, runner: Runner, *, delivery: str = "inspect", steps: list[dict] | None = None) -> Runner:
        runner = harness.stage_plan_reviews(runner, delivery=delivery, steps=steps, accepted_reviews=2)
        self._write_pending_review(harness, runner); harness.accept_effect_only(runner)
        self.assertIsNone(runner._pending_operation()); self.assertIsNone(runner._last_event_payload("PLAN_SEALED"))
        return runner

    def _stage_third_final_review_unadvanced(self, harness: STTHarness, runner: Runner) -> Runner:
        runner = harness.stage_plan_reviews(runner, accepted_reviews=3)
        runner = harness.stage_final_reviews(runner, accepted_reviews=2)
        self._write_pending_review(harness, runner); harness.accept_effect_only(runner)
        self.assertIsNone(runner._pending_operation()); self.assertIsNone(runner._last_event_payload("TERMINAL_RECEIPT_RECORDED"))
        return runner

    def _process_worker_with(self, harness: STTHarness, runner: Runner, apply_side_effect: object | None = None, *, crash_before_result: bool = False) -> tuple[str, Path]:
        request, request_ref = harness.pending(runner); self.assertEqual(request["role"], "worker")
        harness.write_worker(runner, request, request_ref.sha256)
        adopted = runner._adopt_result(request); self.assertIsNotNone(adopted)
        result, result_ref, _, evidence_ref = adopted
        capsule_value = Path(request["capsule_path"]) / "value.txt"
        if crash_before_result:
            original_append = runner._append_json_fact

            def append(event_type: str, directory: str, value: dict):
                if event_type == "OPERATION_RESULT":
                    raise SimulatedProcessInterruption()
                return original_append(event_type, directory, value)

            with patch.object(runner, "_append_json_fact", side_effect=append):
                runner._process_worker_result(request, result, result_ref, evidence_ref)
        elif apply_side_effect is not None:
            with patch("concepts.stt.runner.apply_delta", side_effect=apply_side_effect):
                runner._process_worker_result(request, result, result_ref, evidence_ref)
        else:
            runner._process_worker_result(request, result, result_ref, evidence_ref)
        return request["operation_id"], capsule_value

    def run_case(self, case: str) -> None:
        with tempfile.TemporaryDirectory(prefix=f"stt-interrupt-{case}-") as td:
            harness = STTHarness(Path(td))

            if case == "bootstrap_before_atomic_rename":
                task_id = "atomic-bootstrap-task"
                with patch("concepts.stt.runner.os.rename", side_effect=SimulatedProcessInterruption()):
                    with self.assertRaises(SimulatedProcessInterruption):
                        Runner.bootstrap(repo=harness.repo, state_root=harness.state_root, mission=b"mission\n", included_ignored=[], task_id=task_id)
                self.assertFalse((harness.state_root / task_id).exists())
                self.assertEqual(list(harness.state_root.glob(f".{task_id}.creating-*")), [])
                started = Runner.bootstrap(repo=harness.repo, state_root=harness.state_root, mission=b"mission\n", included_ignored=[], task_id=task_id)
                reconstructed = Runner(Path(started["task_root"]))
                self.assertEqual(reconstructed._pending_operation()[0]["role"], "planner")
                return

            runner = harness.bootstrap()

            if case == "planner_effect_without_acceptance":
                self._write_initial_plan(harness, runner); operation_id = runner._pending_operation()[0]["operation_id"]
                harness.process_effect_only(runner)
                reconstructed = Runner(runner.task_root); reconstructed.run()
                self.assertEqual(len(reconstructed._effect_records(operation_id)), 1)
                self.assertEqual(len([event for event in reconstructed._events() if event["event"]["event_type"] == "OPERATION_ACCEPTED" and event["payload"].get("operation_id") == operation_id]), 1)
                self.assertEqual(reconstructed._pending_operation()[0]["purpose"], "plan_review")

            elif case == "planner_accepted_without_review_request":
                self._write_initial_plan(harness, runner); operation_id = runner._pending_operation()[0]["operation_id"]
                harness.accept_effect_only(runner)
                reconstructed = Runner(runner.task_root); reconstructed.run()
                self.assertEqual(len(reconstructed._effect_records(operation_id)), 1)
                self.assertEqual(reconstructed._pending_operation()[0]["purpose"], "plan_review")

            elif case == "review_effect_without_acceptance":
                runner = harness.stage_plan_reviews(runner)
                self._write_pending_review(harness, runner); operation_id = runner._pending_operation()[0]["operation_id"]
                harness.process_effect_only(runner)
                reconstructed = Runner(runner.task_root); reconstructed.run()
                self.assertEqual(len(reconstructed._effect_records(operation_id)), 1)
                self.assertEqual(reconstructed._pending_operation()[0]["purpose"], "plan_review")

            elif case == "third_plan_review_accepted_without_seal":
                runner = self._stage_third_plan_review_unadvanced(harness, runner)
                reconstructed = Runner(runner.task_root); reconstructed.run()
                self.assertEqual(len([event for event in reconstructed._events() if event["event"]["event_type"] == "PLAN_SEALED"]), 1)
                self.assertEqual(reconstructed._pending_operation()[0]["purpose"], "final_review")

            elif case == "plan_seal_artifact_without_event":
                runner = self._stage_third_plan_review_unadvanced(harness, runner)
                original_append = runner.ledger.append

                def append(event_type: str, payload_ref: str, payload_sha256: str):
                    if event_type == "PLAN_SEALED":
                        raise SimulatedProcessInterruption()
                    return original_append(event_type, payload_ref, payload_sha256)

                with patch.object(runner.ledger, "append", side_effect=append), self.assertRaises(SimulatedProcessInterruption):
                    runner.run()
                self.assertEqual(len(list((runner.task_root / "plans" / "seals").glob("*.json"))), 1)
                reconstructed = Runner(runner.task_root); reconstructed.run()
                self.assertEqual(len(list((runner.task_root / "plans" / "seals").glob("*.json"))), 2)
                self.assertEqual(len([event for event in reconstructed._events() if event["event"]["event_type"] == "PLAN_SEALED"]), 1)

            elif case == "evidence_effect_without_continuation":
                request, ref = harness.pending(runner); harness.write_needs_evidence(runner, request, ref.sha256); harness.accept_effect_only(runner)
                reconstructed = Runner(runner.task_root); reconstructed.run()
                continuation = reconstructed._pending_operation()[0]
                self.assertEqual((continuation["role"], continuation["purpose"]), ("planner", "initial_plan"))
                self.assertEqual(len(continuation["evidence_bundles"]), 1)

            elif case in {"worker_intent_before_apply", "worker_interrupted_during_apply", "worker_apply_complete_without_result_effect", "worker_result_effect_without_acceptance", "worker_accepted_without_next_step"}:
                steps = [change_step()]
                if case == "worker_accepted_without_next_step":
                    steps.append(change_step("change-two"))
                runner = harness.stage_plan_reviews(runner, delivery="workspace_change", steps=steps, accepted_reviews=3)

                if case == "worker_intent_before_apply":
                    with self.assertRaises(SimulatedProcessInterruption):
                        self._process_worker_with(harness, runner, SimulatedProcessInterruption())
                    self.assertEqual((harness.repo / "value.txt").read_text(), "before\n")
                    reconstructed = Runner(runner.task_root); state = reconstructed.run()
                    self.assertEqual((state["status"], state["next_action"], state["resumable"]), ("BLOCKED_UNKNOWN", "DIAGNOSE", False))

                elif case == "worker_interrupted_during_apply":
                    def partial(*args: object, **kwargs: object) -> None:
                        (harness.repo / "value.txt").write_text("partial\n")
                        raise SimulatedProcessInterruption()
                    with self.assertRaises(SimulatedProcessInterruption):
                        self._process_worker_with(harness, runner, partial)
                    reconstructed = Runner(runner.task_root); state = reconstructed.run()
                    self.assertEqual((state["status"], state["next_action"]), ("BLOCKED_UNKNOWN", "DIAGNOSE"))
                    self.assertEqual((harness.repo / "value.txt").read_text(), "partial\n")

                elif case == "worker_apply_complete_without_result_effect":
                    with self.assertRaises(SimulatedProcessInterruption):
                        self._process_worker_with(harness, runner, crash_before_result=True)
                    self.assertEqual((harness.repo / "value.txt").read_text(), "worker\n")
                    reconstructed = Runner(runner.task_root); state = reconstructed.run()
                    self.assertEqual((state["status"], state["next_action"]), ("BLOCKED_UNKNOWN", "DIAGNOSE"))
                    self.assertFalse(reconstructed._accepted_effects("OPERATION_RESULT"))

                elif case == "worker_result_effect_without_acceptance":
                    operation_id, capsule_value = self._process_worker_with(harness, runner)
                    capsule_value.write_text("would-be-replay\n")
                    reconstructed = Runner(runner.task_root); reconstructed.run()
                    self.assertEqual((harness.repo / "value.txt").read_text(), "worker\n")
                    self.assertEqual(len(reconstructed._effect_records(operation_id)), 1)
                    self.assertEqual(len([event for event in reconstructed._events() if event["event"]["event_type"] == "OPERATION_ACCEPTED" and event["payload"].get("operation_id") == operation_id]), 1)

                else:
                    request, request_ref = harness.pending(runner)
                    operation_id, _ = self._process_worker_with(harness, runner)
                    effect = runner._effect_records(operation_id)[0]; runner._accept_effect(request, request_ref, effect)
                    reconstructed = Runner(runner.task_root); reconstructed.run()
                    next_request = reconstructed._pending_operation()[0]
                    self.assertEqual((next_request["role"], next_request["step"]["id"]), ("worker", "change-two"))
                    self.assertEqual((harness.repo / "value.txt").read_text(), "worker\n")

            elif case == "inspect_report_without_event":
                runner = self._stage_third_plan_review_unadvanced(harness, runner)
                original_append = runner.ledger.append

                def append(event_type: str, payload_ref: str, payload_sha256: str):
                    if event_type == "INSPECTION_RECORDED":
                        raise SimulatedProcessInterruption()
                    return original_append(event_type, payload_ref, payload_sha256)

                with patch.object(runner.ledger, "append", side_effect=append), self.assertRaises(SimulatedProcessInterruption):
                    runner.run()
                self.assertEqual(len(list((runner.task_root / "inspect" / "reports" / "inspect").glob("*.json"))), 1)
                reconstructed = Runner(runner.task_root); reconstructed.run()
                self.assertEqual(len(list((runner.task_root / "inspect" / "reports" / "inspect").glob("*.json"))), 2)
                self.assertEqual(len([event for event in reconstructed._events() if event["event"]["event_type"] == "INSPECTION_RECORDED"]), 1)

            elif case == "final_artifacts_without_freeze_event":
                runner = self._stage_third_plan_review_unadvanced(harness, runner)
                original_append = runner.ledger.append

                def append(event_type: str, payload_ref: str, payload_sha256: str):
                    if event_type == "FINAL_SUBJECT_FROZEN":
                        raise SimulatedProcessInterruption()
                    return original_append(event_type, payload_ref, payload_sha256)

                with patch.object(runner.ledger, "append", side_effect=append), self.assertRaises(SimulatedProcessInterruption):
                    runner.run()
                self.assertEqual(len(list((runner.task_root / "final" / "attempts").iterdir())), 1)
                reconstructed = Runner(runner.task_root); reconstructed.run()
                self.assertEqual(len(list((runner.task_root / "final" / "attempts").iterdir())), 2)
                self.assertEqual(reconstructed._pending_operation()[0]["purpose"], "final_review")

            elif case == "third_final_review_accepted_without_terminal":
                runner = self._stage_third_final_review_unadvanced(harness, runner)
                reconstructed = Runner(runner.task_root); state = reconstructed.run()
                self.assertEqual(state["status"], "COMPLETE")
                self.assertEqual(len([event for event in reconstructed._events() if event["event"]["event_type"] == "TERMINAL_RECEIPT_RECORDED"]), 1)

            elif case == "terminal_receipt_without_event":
                runner = self._stage_third_final_review_unadvanced(harness, runner)
                original_append = runner.ledger.append

                def append(event_type: str, payload_ref: str, payload_sha256: str):
                    if event_type == "TERMINAL_RECEIPT_RECORDED":
                        raise SimulatedProcessInterruption()
                    return original_append(event_type, payload_ref, payload_sha256)

                with patch.object(runner.ledger, "append", side_effect=append), self.assertRaises(SimulatedProcessInterruption):
                    runner.run()
                self.assertEqual(len(list((runner.task_root / "terminal" / "receipts").glob("*.json"))), 1)
                reconstructed = Runner(runner.task_root); self.assertEqual(reconstructed.run()["status"], "COMPLETE")
                self.assertEqual(len(list((runner.task_root / "terminal" / "receipts").glob("*.json"))), 2)

            elif case == "planner_superseded_without_replacement":
                request, ref = harness.pending(runner)
                harness.write_evidence(runner, request, "invalid-plan")
                from tests.concepts.stt.stt_test_support import write_json
                write_json(runner.task_root / request["result_ref"], {"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": "0" * 64, "kind": "PLAN_CANDIDATE"})
                self.assertEqual(runner.run()["next_action"], "RETRY_OPERATION")
                runner._supersede_operation(request["operation_id"], reason="TEST_REPLAN", replacement_purpose="replan", replacement_body=runner._replacement_body())
                reconstructed = Runner(runner.task_root); reconstructed.run()
                replacement = reconstructed._pending_operation()[0]
                self.assertNotEqual(replacement["operation_id"], request["operation_id"])
                self.assertEqual(replacement["purpose"], "replan")

            elif case == "stopped_with_pending_operation":
                operation_id = runner._pending_operation()[0]["operation_id"]
                runner.stop(); reconstructed = Runner(runner.task_root); count = len(reconstructed._events())
                self.assertEqual(reconstructed.run()["status"], "STOPPED"); self.assertEqual(len(reconstructed._events()), count)
                reconstructed.resume(); resumed = Runner(runner.task_root)
                self.assertEqual(resumed._pending_operation()[0]["operation_id"], operation_id)
                self.assertEqual(resumed.status()["next_action"], "DISPATCH_PLANNER")

            elif case == "child_complete_without_parent_acceptance":
                child_mission = "child inspect\n"
                runner = harness.stage_plan_reviews(runner, delivery="workspace_change", steps=[task_step(child_mission)], accepted_reviews=3)
                binding = runner._active_task_binding(); self.assertIsNotNone(binding)
                child = Runner(Path(binding["child_task_root"]))
                harness.complete(child)
                self.assertEqual(child.status()["status"], "COMPLETE")
                self.assertFalse(any(event["event"]["event_type"] == "TASK_RESULT_ACCEPTED" for event in runner._events()))
                reconstructed = Runner(runner.task_root); reconstructed.run()
                accepted = [event for event in reconstructed._events() if event["event"]["event_type"] == "TASK_RESULT_ACCEPTED"]
                self.assertEqual(len(accepted), 1)

            else:
                self.fail(f"unhandled interruption case: {case}")


def _make_test(case: str):
    def test(self: InterruptionMatrixTests) -> None:
        self.run_case(case)
    test.__name__ = f"test_{case}"
    return test


for _case in CASES:
    setattr(InterruptionMatrixTests, f"test_{_case}", _make_test(_case))


if __name__ == "__main__":
    unittest.main()
