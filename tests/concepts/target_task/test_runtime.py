import tempfile
import unittest
from pathlib import Path

from capabilities.execution_envelope.execution_envelope import ExecutionEnvelopeError
from concepts.target_task.runtime import RuntimeAdapterError, SpecialistOutcome, dispatch_specialist


def make_envelope(task_id="task-1"):
    return {
        "task_id": task_id,
        "objective": "do the bounded thing",
        "scope": "one file",
        "authority": "read-only",
        "prohibitions": [],
        "success_criteria": [],
        "contract_references": [],
        "input_artifact_references": [],
        "required_output_references": [],
    }


class DispatchSpecialistTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repository_root = root / "repo"
        self.workspace_root = root / "workspace"
        self.repository_root.mkdir()
        self.workspace_root.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_body_is_captured_to_file_and_not_returned(self) -> None:
        def executor(envelope):
            return SpecialistOutcome(
                body="the entire raw substantive result, potentially very large",
                status="COMPLETE", summary="finished the bounded work",
            )

        result = dispatch_specialist(
            make_envelope(), executor, role="worker",
            workspace_root=self.workspace_root, output_relative_path="steps/step-1/result.md",
            output_reference_id="step-1-result", repository_root=self.repository_root,
        )
        self.assertNotIn("the entire raw substantive result", str(result))
        self.assertEqual(
            (self.workspace_root / "steps/step-1/result.md").read_text(),
            "the entire raw substantive result, potentially very large",
        )
        self.assertEqual(result["role"], "worker")
        self.assertEqual(len(result["produced_artifact_references"]), 1)
        self.assertEqual(result["produced_artifact_references"][0]["repository_relative_path"], "steps/step-1/result.md")

    def test_role_return_is_bounded_and_body_free(self) -> None:
        def executor(envelope):
            return SpecialistOutcome(body="x", status="COMPLETE", summary="ok", findings=("f1",), blockers=())

        result = dispatch_specialist(
            make_envelope(), executor, role="reviewer",
            workspace_root=self.workspace_root, output_relative_path="result.md",
            output_reference_id="r1", repository_root=self.repository_root,
        )
        from capabilities.execution_envelope.execution_envelope import ROLE_FIELDS

        self.assertEqual(set(result), ROLE_FIELDS)

    def test_invalid_task_envelope_is_rejected_before_dispatch(self) -> None:
        called = []

        def executor(envelope):
            called.append(envelope)
            return SpecialistOutcome(body="x", status="COMPLETE", summary="ok")

        bad_envelope = make_envelope()
        del bad_envelope["objective"]
        with self.assertRaises(RuntimeAdapterError):
            dispatch_specialist(
                bad_envelope, executor, role="worker",
                workspace_root=self.workspace_root, output_relative_path="r.md",
                output_reference_id="r1", repository_root=self.repository_root,
            )
        self.assertEqual(called, [])

    def test_executor_returning_wrong_type_is_rejected(self) -> None:
        def executor(envelope):
            return "not a SpecialistOutcome"

        with self.assertRaises(RuntimeAdapterError):
            dispatch_specialist(
                make_envelope(), executor, role="worker",
                workspace_root=self.workspace_root, output_relative_path="r.md",
                output_reference_id="r1", repository_root=self.repository_root,
            )

    def test_second_dispatch_writing_same_output_path_fails(self) -> None:
        def executor(envelope):
            return SpecialistOutcome(body="x", status="COMPLETE", summary="ok")

        dispatch_specialist(
            make_envelope(), executor, role="worker",
            workspace_root=self.workspace_root, output_relative_path="r.md",
            output_reference_id="r1", repository_root=self.repository_root,
        )
        with self.assertRaises(RuntimeAdapterError):
            dispatch_specialist(
                make_envelope(), executor, role="worker",
                workspace_root=self.workspace_root, output_relative_path="r.md",
                output_reference_id="r1", repository_root=self.repository_root,
            )


if __name__ == "__main__":
    unittest.main()
