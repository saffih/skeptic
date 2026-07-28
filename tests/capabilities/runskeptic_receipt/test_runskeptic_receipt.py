from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from capabilities.runskeptic_receipt.runskeptic_receipt import (  # noqa: E402
    REQUIRED_STEPS,
    REQUIRED_THINKERS,
    advance_fix_loop,
    fix_loop_complete,
    validate_loop_state,
    validate_receipt,
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob_digest(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


class ReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.artifact = ROOT / "tests" / "capabilities" / "runskeptic_receipt" / "test_runskeptic_receipt.py"
        self.receipt = {
            "INVOCATION_ID": "R-001", "INVOCATION_KIND": "FIX_LOOP",
            "PERMISSION_MODE": "fix-if-valid", "DONE": "tests pass",
            "TARGET_TASK_SHA256": "a" * 64,
            "REVIEWED_ARTIFACT_REFERENCE": {"path": str(self.artifact.relative_to(ROOT)), "sha256": digest(self.artifact)},
            "REVIEWED_ARTIFACT_SHA256": digest(self.artifact),
            "SKEPTIC_SOURCE_PATH": "skeptic.md", "SKEPTIC_SOURCE_REF": "WORKTREE",
            "SKEPTIC_SOURCE_BLOB_SHA": blob_digest(ROOT / "skeptic.md"),
            "APPLICABLE_COMPANION_SET_SHA256": "c" * 64, "MATERIAL_FINDINGS_SHA256": "e" * 64,
            "PREVIOUS_FINDINGS_REFERENCE": "NONE",
            "MAJOR_STEPS_RUN": list(REQUIRED_STEPS), "THINKERS_CONSIDERED": list(REQUIRED_THINKERS),
            "FINDING_CATEGORIES": ["PASS"], "FINAL_OUTPUT_CATEGORY": "HANDLED",
            "OPEN_ITEMS": [],
        }

    def test_valid_current_source_bound_receipt(self) -> None:
        self.assertTrue(validate_receipt(self.receipt, root=ROOT).ok)

    def test_stale_source_and_nonroot_source_rejected(self) -> None:
        self.receipt["SKEPTIC_SOURCE_BLOB_SHA"] = "d" * 40
        self.receipt["SKEPTIC_SOURCE_PATH"] = "agents/planner.md"
        result = validate_receipt(self.receipt, root=ROOT)
        self.assertFalse(result.ok)
        self.assertTrue(any("stale" in e for e in result.errors))
        self.assertTrue(any("authorized source" in e for e in result.errors))

    def test_stale_source_ref_rejected(self) -> None:
        self.receipt["SKEPTIC_SOURCE_REF"] = "0" * 40
        result = validate_receipt(self.receipt, root=ROOT)
        self.assertFalse(result.ok)
        self.assertTrue(any("source ref" in e for e in result.errors))

    def test_missing_thinker_step_and_fail_are_rejected(self) -> None:
        self.receipt["MAJOR_STEPS_RUN"] = ["GATE"]
        self.receipt["THINKERS_CONSIDERED"] = ["CH"]
        self.receipt["FINDING_CATEGORIES"] = ["FAIL"]
        result = validate_receipt(self.receipt, root=ROOT)
        self.assertFalse(result.ok)
        self.assertGreaterEqual(len(result.errors), 3)

    def test_missing_source_identity_is_rejected(self) -> None:
        self.receipt.pop("SKEPTIC_SOURCE_BLOB_SHA")
        self.assertFalse(validate_receipt(self.receipt, root=ROOT).ok)

    def test_missing_required_receipt_field_is_rejected(self) -> None:
        self.receipt.pop("MATERIAL_FINDINGS_SHA256")
        result = validate_receipt(self.receipt, root=ROOT)
        self.assertFalse(result.ok)
        self.assertTrue(any("missing field" in error for error in result.errors))

    def test_missing_major_step_is_rejected(self) -> None:
        self.receipt["MAJOR_STEPS_RUN"] = list(REQUIRED_STEPS[:-1])
        self.assertFalse(validate_receipt(self.receipt, root=ROOT).ok)

    def test_missing_thinker_is_rejected(self) -> None:
        self.receipt["THINKERS_CONSIDERED"] = list(REQUIRED_THINKERS[:-1])
        self.assertFalse(validate_receipt(self.receipt, root=ROOT).ok)

    def test_artifact_reference_hash_mismatch_is_rejected(self) -> None:
        self.receipt["REVIEWED_ARTIFACT_REFERENCE"]["sha256"] = "f" * 64
        result = validate_receipt(self.receipt, root=ROOT)
        self.assertFalse(result.ok)
        self.assertTrue(any("hash" in error for error in result.errors))


class LoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = {
            "TARGET_TASK_SHA256": "a" * 64, "REVIEWED_ARTIFACT_SHA256": "b" * 64,
            "SKEPTIC_SOURCE_BLOB_SHA": "c" * 40, "APPLICABLE_COMPANION_SET_SHA256": "d" * 64,
            "MATERIAL_FINDINGS_SHA256": "e" * 64,
            "INVOCATION_KIND": "FIX_LOOP", "PERMISSION_MODE": "fix-if-valid",
            "QUALIFYING_PASSES_REQUIRED": 3, "CONSECUTIVE_QUALIFYING_PASSES": 0, "OPEN_ITEMS": [],
        }
        self.receipt = {**self.state, "FINAL_OUTPUT_CATEGORY": "HANDLED", "FINDING_CATEGORIES": ["PASS"], "OPEN_ITEMS": []}

    def test_repair_does_not_increment_and_unchanged_pass_does(self) -> None:
        repair = {**self.receipt, "REPAIR_RUN": True}
        self.assertEqual(advance_fix_loop(self.state, repair)["CONSECUTIVE_QUALIFYING_PASSES"], 0)
        self.assertEqual(advance_fix_loop(self.state, self.receipt)["CONSECUTIVE_QUALIFYING_PASSES"], 1)

    def test_changed_basis_resets(self) -> None:
        changed = {**self.receipt, "SKEPTIC_SOURCE_BLOB_SHA": "e" * 40}
        self.assertEqual(advance_fix_loop({**self.state, "CONSECUTIVE_QUALIFYING_PASSES": 2}, changed)["CONSECUTIVE_QUALIFYING_PASSES"], 0)

    def test_changed_material_finding_resets(self) -> None:
        changed = {**self.receipt, "MATERIAL_FINDINGS_SHA256": "f" * 64}
        self.assertEqual(advance_fix_loop({**self.state, "CONSECUTIVE_QUALIFYING_PASSES": 2}, changed)["CONSECUTIVE_QUALIFYING_PASSES"], 0)

    def test_delta_only_review_does_not_qualify(self) -> None:
        delta = {**self.receipt, "REVIEW_SCOPE": "DELTA"}
        self.assertEqual(advance_fix_loop({**self.state, "CONSECUTIVE_QUALIFYING_PASSES": 2}, delta)["CONSECUTIVE_QUALIFYING_PASSES"], 0)

    def test_changed_each_loop_binding_resets(self) -> None:
        for field, value in (
            ("TARGET_TASK_SHA256", "f" * 64),
            ("REVIEWED_ARTIFACT_SHA256", "f" * 64),
            ("SKEPTIC_SOURCE_BLOB_SHA", "f" * 40),
            ("APPLICABLE_COMPANION_SET_SHA256", "f" * 64),
            ("INVOCATION_KIND", "SINGLE"),
            ("PERMISSION_MODE", "read-only"),
        ):
            with self.subTest(field=field):
                changed = {**self.receipt, field: value}
                state = {**self.state, "CONSECUTIVE_QUALIFYING_PASSES": 2}
                self.assertEqual(advance_fix_loop(state, changed)["CONSECUTIVE_QUALIFYING_PASSES"], 0)

    def test_nonidentical_receipts_cannot_close_loop(self) -> None:
        state = {**self.state, "CONSECUTIVE_QUALIFYING_PASSES": 2}
        changed = {**self.receipt, "MATERIAL_FINDINGS_SHA256": "f" * 64}
        state = advance_fix_loop(state, changed)
        self.assertFalse(fix_loop_complete(state))

    def test_three_passes_close_and_loop_state_validates(self) -> None:
        state = self.state
        for _ in range(3):
            state = advance_fix_loop(state, self.receipt)
        self.assertEqual(state["CONSECUTIVE_QUALIFYING_PASSES"], 3)
        self.assertTrue(validate_loop_state(state).ok)
        self.assertTrue(fix_loop_complete(state))


if __name__ == "__main__":
    unittest.main()
