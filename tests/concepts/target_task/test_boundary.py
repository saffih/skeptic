import hashlib
import tempfile
import unittest
from pathlib import Path

from concepts.target_task.boundary import (
    BoundaryError,
    admit_transition,
    advance_find_loop,
    build_luna_receipt,
    find_loop_complete,
    retrieve_evidence,
    validate_find_loop_state,
)
from concepts.target_task.contracts import LunaAction, Phase
from concepts.target_task.flow import IllegalTransitionError


class AdmitTransitionTests(unittest.TestCase):
    def test_delegates_to_flow(self) -> None:
        result = admit_transition(Phase.MISSION_PERSISTED, LunaAction.CONTINUE)
        self.assertEqual(result.phase, Phase.PLAN_DRAFTED)

    def test_illegal_transition_raises(self) -> None:
        with self.assertRaises(IllegalTransitionError):
            admit_transition(Phase.PLAN_SEALED, LunaAction.RETRY)


def _write(path: Path, content: bytes) -> tuple[str, int]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return hashlib.sha256(content).hexdigest(), len(content)


class BuildLunaReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repository_root = Path(self.tmp.name)
        self.plan_sha, self.plan_size = _write(self.repository_root / "plans/plan-001.md", b"# Plan\n")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _state(self, **overrides):
        state = {
            "TASK_ID": "task-1",
            "SEALED_PLAN_REFERENCE": "plans/plan-001.md",
            "SEALED_PLAN_SHA256": self.plan_sha,
            "CURRENT_STEP": "step-1",
            "COMPLETED_STEP_IDS": [],
            "VALIDATED_FACTS": [],
            "OPEN_BLOCKERS": [],
            "ARTIFACT_REFERENCES": [{
                "reference_id": "plan", "repository_relative_path": "plans/plan-001.md",
                "sha256": self.plan_sha, "byte_size": self.plan_size,
                "artifact_type": "plan", "description": "sealed plan", "read_condition": "read at seal",
            }],
            "NEXT_AUTHORIZED_ACTION": "execute step-1",
            "VALIDATION_STATUS": "VALID",
        }
        state.update(overrides)
        return state

    def test_valid_receipt_serializes(self) -> None:
        raw = build_luna_receipt(self._state(), repository_root=self.repository_root)
        self.assertTrue(raw.endswith(b"\n"))
        self.assertIn(b'"TASK_ID":"task-1"', raw)

    def test_receipt_cannot_carry_extra_field(self) -> None:
        state = self._state()
        state["MISSION_BODY"] = "the entire mission text should never be here"
        with self.assertRaises(BoundaryError):
            build_luna_receipt(state, repository_root=self.repository_root)

    def test_sealed_plan_hash_mismatch_is_rejected(self) -> None:
        state = self._state(SEALED_PLAN_SHA256="a" * 64)
        with self.assertRaises(BoundaryError):
            build_luna_receipt(state, repository_root=self.repository_root)

    def test_structural_only_skips_artifact_io(self) -> None:
        missing_sha = "a" * 64
        state = self._state(
            SEALED_PLAN_REFERENCE="plans/plan-missing.md",
            SEALED_PLAN_SHA256=missing_sha,
            ARTIFACT_REFERENCES=[{
                "reference_id": "plan", "repository_relative_path": "plans/plan-missing.md",
                "sha256": missing_sha, "byte_size": 7,
                "artifact_type": "plan", "description": "sealed plan", "read_condition": "read at seal",
            }],
        )
        # Full validation must fail: the file does not exist on disk.
        with self.assertRaises(BoundaryError):
            build_luna_receipt(state, repository_root=self.repository_root)
        # Structural-only validation only checks internal cross-references
        # (which are self-consistent here), never touching the filesystem.
        raw = build_luna_receipt(state, repository_root=self.repository_root, structural_only=True)
        self.assertTrue(raw.endswith(b"\n"))


class RetrieveEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repository_root = Path(self.tmp.name)
        source_sha, source_size = _write(self.repository_root / "source.md", b"line one\nline two\nline three\n")
        state = {
            "TASK_ID": "task-1", "SEALED_PLAN_REFERENCE": "source.md", "SEALED_PLAN_SHA256": source_sha,
            "CURRENT_STEP": "step-1", "COMPLETED_STEP_IDS": [], "VALIDATED_FACTS": [], "OPEN_BLOCKERS": [],
            "ARTIFACT_REFERENCES": [{
                "reference_id": "src", "repository_relative_path": "source.md", "sha256": source_sha,
                "byte_size": source_size, "artifact_type": "evidence", "description": "d", "read_condition": "r",
            }],
            "NEXT_AUTHORIZED_ACTION": "review", "VALIDATION_STATUS": "VALID",
        }
        self.body_sha, self.body_size = _write(self.repository_root / "body.json", build_luna_receipt(state, repository_root=self.repository_root))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_returns_only_requested_range(self) -> None:
        result = retrieve_evidence({
            "REQUEST_ID": "req-1", "TASK_ID": "task-1", "STEP_ID": "step-1", "PURPOSE": "verify",
            "BODY_STATE_PATH": "body.json", "BODY_STATE_SHA256": self.body_sha, "BODY_STATE_BYTE_SIZE": self.body_size,
            "ARTIFACT_REFERENCE_ID": "src", "START_LINE": 2, "END_LINE": 2, "MAX_EXCERPT_BYTES": 256,
        }, repository_root=self.repository_root)
        self.assertEqual(result["EXCERPT"], "line two\n")

    def test_unknown_reference_id_is_rejected(self) -> None:
        with self.assertRaises(BoundaryError):
            retrieve_evidence({
                "REQUEST_ID": "req-1", "TASK_ID": "task-1", "STEP_ID": "step-1", "PURPOSE": "verify",
                "BODY_STATE_PATH": "body.json", "BODY_STATE_SHA256": self.body_sha, "BODY_STATE_BYTE_SIZE": self.body_size,
                "ARTIFACT_REFERENCE_ID": "does-not-exist", "START_LINE": 1, "END_LINE": 1, "MAX_EXCERPT_BYTES": 256,
            }, repository_root=self.repository_root)


class FindLoopTests(unittest.TestCase):
    def _bindings(self, findings_hash="a" * 64):
        return {
            "TARGET_TASK_SHA256": "b" * 64, "REVIEWED_ARTIFACT_SHA256": "c" * 64,
            "SKEPTIC_SOURCE_BLOB_SHA": "d" * 40, "APPLICABLE_COMPANION_SET_SHA256": "e" * 64,
            "MATERIAL_FINDINGS_SHA256": findings_hash, "INVOCATION_KIND": "FIND_LOOP", "PERMISSION_MODE": "read-only",
        }

    def _state(self, passes=0, **overrides):
        state = dict(self._bindings())
        state["CONSECUTIVE_STABLE_PASSES"] = passes
        state["PASSES_REQUIRED"] = 3
        state.update(overrides)
        return state

    def test_valid_state_passes_validation(self) -> None:
        self.assertTrue(validate_find_loop_state(self._state()).ok)

    def test_fix_loop_kind_is_rejected(self) -> None:
        state = self._state()
        state["INVOCATION_KIND"] = "FIX_LOOP"
        self.assertFalse(validate_find_loop_state(state).ok)

    def test_non_read_only_permission_is_rejected(self) -> None:
        state = self._state()
        state["PERMISSION_MODE"] = "fix-if-valid"
        self.assertFalse(validate_find_loop_state(state).ok)

    def test_stable_receipt_increments_streak(self) -> None:
        state = self._state(passes=1)
        receipt = self._bindings()
        next_state = advance_find_loop(state, receipt)
        self.assertEqual(next_state["CONSECUTIVE_STABLE_PASSES"], 2)

    def test_new_finding_resets_streak(self) -> None:
        state = self._state(passes=2)
        receipt = self._bindings(findings_hash="f" * 64)
        next_state = advance_find_loop(state, receipt)
        self.assertEqual(next_state["CONSECUTIVE_STABLE_PASSES"], 0)

    def test_three_stable_passes_complete_the_loop(self) -> None:
        state = self._state(passes=0)
        receipt = self._bindings()
        for _ in range(3):
            state = advance_find_loop(state, receipt)
        self.assertTrue(find_loop_complete(state))

    def test_not_complete_before_three_passes(self) -> None:
        state = self._state(passes=2)
        self.assertFalse(find_loop_complete(state))

    def test_modifying_receipt_is_rejected(self) -> None:
        state = self._state(passes=1)
        receipt = self._bindings()
        receipt["PERMISSION_MODE"] = "fix-if-valid"
        with self.assertRaises(BoundaryError):
            advance_find_loop(state, receipt)


if __name__ == "__main__":
    unittest.main()
