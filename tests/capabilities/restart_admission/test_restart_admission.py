import errno
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from capabilities.immutable_checkpoint.immutable_checkpoint import create_checkpoint
from capabilities.restart_admission.restart_admission import ResumeError, admit_restart, process_request, validate_restart_receipt


def enc(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); root = Path(self.tmp.name)
        self.repo = root / "repo"; self.repo.mkdir(); self.workspace = root / "workspace"; self.workspace.mkdir(); self.out = self.workspace / "resumed"; self.out.mkdir()
        plan = self.repo / "plan.md"; plan.write_text("sealed plan\n", encoding="utf-8"); ph = hashlib.sha256(plan.read_bytes()).hexdigest()
        evidence = self.repo / "evidence.txt"; evidence.write_text("evidence\n", encoding="utf-8"); eh = hashlib.sha256(evidence.read_bytes()).hexdigest()
        self.state = {"TASK_ID":"TT-VALIDATED-RESTART-SLICE-005","SEALED_PLAN_REFERENCE":"plan.md","SEALED_PLAN_SHA256":ph,"CURRENT_STEP":"publish","COMPLETED_STEP_IDS":["validate","review"],"VALIDATED_FACTS":[{"summary":"plan is sealed","status":"PASS","artifact_reference_ids":["plan"]}],"OPEN_BLOCKERS":[],"ARTIFACT_REFERENCES":[{"reference_id":"plan","repository_relative_path":"plan.md","sha256":ph,"byte_size":plan.stat().st_size,"artifact_type":"plan","description":"sealed plan","read_condition":"validate restart"},{"reference_id":"evidence","repository_relative_path":"evidence.txt","sha256":eh,"byte_size":evidence.stat().st_size,"artifact_type":"evidence","description":"evidence","read_condition":"validate restart"}],"NEXT_AUTHORIZED_ACTION":"publish the prepared result","VALIDATION_STATUS":"VALID"}
        self.source = self.workspace / "body.json"; self.source.write_bytes(enc(self.state)); (self.workspace / "checkpoints").mkdir()
        self.request_value = {"REQUEST_ID":"resume-request-1","TASK_ID":self.state["TASK_ID"],"CHECKPOINT_ID":"checkpoint-1","CHECKPOINT_PATH":"checkpoints/checkpoint.json","CHECKPOINT_SHA256":"0" * 64,"CHECKPOINT_BYTE_SIZE":0,"EXPECTED_SEALED_PLAN_REFERENCE":"plan.md","EXPECTED_SEALED_PLAN_SHA256":ph,"RESUMED_BODY_STATE_PATH":"resumed/body-state.json"}
        self.checkpoint = create_checkpoint(enc({"REQUEST_ID":"create","CHECKPOINT_ID":"checkpoint-1","TASK_ID":self.state["TASK_ID"],"BODY_STATE_PATH":"body.json","BODY_STATE_SHA256":hashlib.sha256(self.source.read_bytes()).hexdigest(),"BODY_STATE_BYTE_SIZE":self.source.stat().st_size,"CHECKPOINT_PATH":"checkpoints/checkpoint.json"}), repository_root=self.repo, workspace_root=self.workspace)
        self.checkpoint_path = self.workspace / "checkpoints/checkpoint.json"
        self.request_value.update(CHECKPOINT_SHA256=hashlib.sha256(self.checkpoint_path.read_bytes()).hexdigest(), CHECKPOINT_BYTE_SIZE=self.checkpoint_path.stat().st_size)

    def tearDown(self): self.tmp.cleanup()
    def request(self, **changes): return enc(dict(self.request_value, **changes))

    def test_ready_materializes_exact_snapshot_and_receipt_validates(self):
        receipt = admit_restart(self.request(), repository_root=self.repo, workspace_root=self.workspace)
        self.assertEqual(receipt["STATUS"], "READY"); self.assertEqual(receipt["COMPLETED_STEP_COUNT"], 2); self.assertEqual(receipt["NEXT_AUTHORIZED_ACTION"], self.state["NEXT_AUTHORIZED_ACTION"])
        snapshot = enc(self.state); output = self.workspace / receipt["RESUMED_BODY_STATE_PATH"]
        self.assertEqual(output.read_bytes(), snapshot); self.assertEqual(receipt["RESUMED_BODY_STATE_SHA256"], hashlib.sha256(snapshot).hexdigest()); self.assertEqual(receipt["RESUMED_BODY_STATE_BYTE_SIZE"], len(snapshot))
        self.assertEqual(validate_restart_receipt(enc(receipt), repository_root=self.repo, workspace_root=self.workspace)["STATUS"], "READY")
        self.checkpoint_path.unlink(); self.assertEqual(output.read_bytes(), snapshot)

    def test_blocked_is_success_and_omits_action(self):
        state = dict(self.state, VALIDATION_STATUS="PENDING")
        self._replace_checkpoint(state)
        code, raw = process_request(self.request(), repository_root=self.repo, workspace_root=self.workspace)
        self.assertEqual(code, 0); receipt = json.loads(raw); self.assertEqual(receipt["STATUS"], "BLOCKED"); self.assertNotIn("NEXT_AUTHORIZED_ACTION", receipt)
        self.assertEqual((self.workspace / receipt["RESUMED_BODY_STATE_PATH"]).read_bytes(), enc(state))
        self.assertEqual(validate_restart_receipt(raw, repository_root=self.repo, workspace_root=self.workspace)["STATUS"], "BLOCKED")

    def test_blocked_with_open_blocker(self):
        state = dict(self.state, OPEN_BLOCKERS=[{"summary":"owner decision","artifact_reference_ids":["plan"]}])
        self._replace_checkpoint(state); receipt = admit_restart(self.request(), repository_root=self.repo, workspace_root=self.workspace)
        self.assertEqual(receipt["STATUS"], "BLOCKED"); self.assertEqual(receipt["OPEN_BLOCKER_COUNT"], 1); self.assertNotIn("NEXT_AUTHORIZED_ACTION", receipt)

    def test_identity_and_completed_step_guards(self):
        for changes, code in (({"TASK_ID":"other"}, "TASK_MISMATCH"), ({"CHECKPOINT_ID":"other"}, "CHECKPOINT_ID_MISMATCH"), ({"EXPECTED_SEALED_PLAN_REFERENCE":"other"}, "SEALED_PLAN_REFERENCE_MISMATCH"), ({"EXPECTED_SEALED_PLAN_SHA256":"0" * 64}, "SEALED_PLAN_HASH_MISMATCH"), ({"CHECKPOINT_SHA256":"0" * 64}, "CHECKPOINT_IDENTITY_MISMATCH"), ({"CHECKPOINT_BYTE_SIZE":1}, "CHECKPOINT_IDENTITY_MISMATCH")):
            with self.assertRaises(ResumeError) as caught: admit_restart(self.request(**changes, RESUMED_BODY_STATE_PATH="out-" + code), repository_root=self.repo, workspace_root=self.workspace)
            self.assertEqual(caught.exception.code, code)
        self._replace_checkpoint(dict(self.state, COMPLETED_STEP_IDS=["publish"]))
        with self.assertRaises(ResumeError) as caught: admit_restart(self.request(RESUMED_BODY_STATE_PATH="already"), repository_root=self.repo, workspace_root=self.workspace)
        self.assertEqual(caught.exception.code, "CURRENT_STEP_ALREADY_COMPLETED")
        self._replace_checkpoint(dict(self.state, COMPLETED_STEP_IDS=["review", "validate"]))
        receipt = admit_restart(self.request(RESUMED_BODY_STATE_PATH="ordered"), repository_root=self.repo, workspace_root=self.workspace)
        self.assertEqual(json.loads((self.workspace / "ordered").read_text())["COMPLETED_STEP_IDS"], ["review", "validate"])

    def test_duplicate_completed_steps_and_paths(self):
        self._replace_checkpoint(dict(self.state, COMPLETED_STEP_IDS=["validate", "validate"]))
        with self.assertRaises(ResumeError) as caught: admit_restart(self.request(RESUMED_BODY_STATE_PATH="duplicate"), repository_root=self.repo, workspace_root=self.workspace)
        self.assertEqual(caught.exception.code, "DUPLICATE_COMPLETED_STEP_IDS")
        with self.assertRaises(ResumeError) as caught: admit_restart(self.request(CHECKPOINT_PATH="checkpoints/checkpoint.json", RESUMED_BODY_STATE_PATH="checkpoints/checkpoint.json"), repository_root=self.repo, workspace_root=self.workspace)
        self.assertEqual(caught.exception.code, "PATHS_MUST_DIFFER")
        with self.assertRaises(ResumeError): admit_restart(self.request(CHECKPOINT_PATH="../repo/plan.md", RESUMED_BODY_STATE_PATH="same"), repository_root=self.repo, workspace_root=self.workspace)
        with self.assertRaises(ResumeError): admit_restart(self.request(RESUMED_BODY_STATE_PATH="../repo/out"), repository_root=self.repo, workspace_root=self.workspace)

    def test_artifact_changes_rejected_and_existing_output_preserved(self):
        (self.repo / "evidence.txt").write_text("changed\n", encoding="utf-8")
        with self.assertRaises(ResumeError): admit_restart(self.request(), repository_root=self.repo, workspace_root=self.workspace)
        (self.repo / "evidence.txt").write_text("evidence\n", encoding="utf-8")
        output = self.workspace / "existing-output"; output.write_bytes(b"keep")
        with self.assertRaises(ResumeError) as caught: admit_restart(self.request(RESUMED_BODY_STATE_PATH="existing-output"), repository_root=self.repo, workspace_root=self.workspace)
        self.assertEqual(caught.exception.code, "OUTPUT_EXISTS"); self.assertEqual(output.read_bytes(), b"keep")

    def test_race_and_directory_fsync_modes(self):
        real_link = os.link
        def race(source, target): Path(target).write_bytes(b"keep"); return real_link(source, target)
        with patch("capabilities.restart_admission.restart_admission.os.link", side_effect=race):
            with self.assertRaises(ResumeError) as caught: admit_restart(self.request(RESUMED_BODY_STATE_PATH="race"), repository_root=self.repo, workspace_root=self.workspace)
        self.assertEqual(caught.exception.code, "OUTPUT_EXISTS"); self.assertEqual((self.workspace / "race").read_bytes(), b"keep")
        with patch("capabilities.restart_admission.restart_admission.os.fsync", side_effect=[None, OSError(errno.ENOTSUP, "unsupported")]):
            receipt = admit_restart(self.request(RESUMED_BODY_STATE_PATH="fallback"), repository_root=self.repo, workspace_root=self.workspace)
        self.assertEqual(receipt["STATUS"], "READY")

    def test_cli_separate_process_and_no_action_execution(self):
        request_path = self.workspace / "request.json"; request_path.write_bytes(self.request())
        result = subprocess.run([sys.executable, "-m", "capabilities.restart_admission.restart_admission", str(request_path), "--repository-root", str(self.repo), "--workspace-root", str(self.workspace)], cwd=Path(__file__).parents[3], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr); self.assertEqual(json.loads(result.stdout)["STATUS"], "READY")

    def test_receipt_validator_rejects_unknown_noncanonical_and_state_mutation(self):
        receipt = admit_restart(self.request(RESUMED_BODY_STATE_PATH="receipt-state"), repository_root=self.repo, workspace_root=self.workspace); raw = enc(receipt)
        with self.assertRaises(ResumeError): validate_restart_receipt(enc(dict(receipt, UNKNOWN="x")), repository_root=self.repo, workspace_root=self.workspace)
        with self.assertRaises(ResumeError): validate_restart_receipt(raw + b"\n", repository_root=self.repo, workspace_root=self.workspace)
        output = self.workspace / "receipt-state"; output.write_bytes(output.read_bytes().replace(b"publish the prepared result", b"changed action"))
        with self.assertRaises(ResumeError) as caught: validate_restart_receipt(raw, repository_root=self.repo, workspace_root=self.workspace)
        self.assertEqual(caught.exception.code, "RESUMED_STATE_IDENTITY_MISMATCH")

    def test_prepublication_failure_cleans_temp_and_postpublication_is_truthful(self):
        with patch("capabilities.restart_admission.restart_admission.tempfile.mkstemp", side_effect=OSError("fail")):
            with self.assertRaises(ResumeError) as caught: admit_restart(self.request(RESUMED_BODY_STATE_PATH="pre"), repository_root=self.repo, workspace_root=self.workspace)
        self.assertEqual(caught.exception.phase, "BEFORE_PUBLICATION"); self.assertFalse((self.workspace / "pre").exists())
        with patch("capabilities.restart_admission.restart_admission.os.fsync", side_effect=[None, OSError("directory failure")]):
            with self.assertRaises(ResumeError) as caught: admit_restart(self.request(RESUMED_BODY_STATE_PATH="post"), repository_root=self.repo, workspace_root=self.workspace)
        self.assertEqual(caught.exception.phase, "AFTER_PUBLICATION"); self.assertTrue(caught.exception.output_visible)

    def _replace_checkpoint(self, state):
        self.source.write_bytes(enc(state)); self.checkpoint_path.unlink()
        create_checkpoint(enc({"REQUEST_ID":"create","CHECKPOINT_ID":"checkpoint-1","TASK_ID":state["TASK_ID"],"BODY_STATE_PATH":"body.json","BODY_STATE_SHA256":hashlib.sha256(self.source.read_bytes()).hexdigest(),"BODY_STATE_BYTE_SIZE":self.source.stat().st_size,"CHECKPOINT_PATH":"checkpoints/checkpoint.json"}), repository_root=self.repo, workspace_root=self.workspace)
        self.request_value["CHECKPOINT_SHA256"] = hashlib.sha256(self.checkpoint_path.read_bytes()).hexdigest(); self.request_value["CHECKPOINT_BYTE_SIZE"] = self.checkpoint_path.stat().st_size


if __name__ == "__main__": unittest.main()
