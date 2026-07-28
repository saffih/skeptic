import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from harness.checkpoint import (
    CHECKPOINT_MAX_BYTES,
    REQUEST_MAX_BYTES,
    CheckpointError,
    create_checkpoint,
    validate_checkpoint_bytes,
    validate_checkpoint_file,
    validate_checkpoint_structure_bytes,
)


def enc(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"; self.repo.mkdir(); self.workspace = self.root / "workspace"; self.workspace.mkdir()
        plan = self.repo / "plan.md"; plan.write_text("# sealed plan\n", encoding="utf-8")
        self.plan_hash = hashlib.sha256(plan.read_bytes()).hexdigest()
        evidence = self.repo / "evidence.txt"; evidence.write_text("validated evidence\n", encoding="utf-8")
        evidence_hash = hashlib.sha256(evidence.read_bytes()).hexdigest()
        self.state = {"TASK_ID":"TT-COMPACT-CHECKPOINT-SLICE-004","SEALED_PLAN_REFERENCE":"plan.md","SEALED_PLAN_SHA256":self.plan_hash,"CURRENT_STEP":"publish","COMPLETED_STEP_IDS":["validate"],"VALIDATED_FACTS":[{"summary":"Plan validated","status":"PASS","artifact_reference_ids":["plan"]}],"OPEN_BLOCKERS":[],"ARTIFACT_REFERENCES":[{"reference_id":"plan","repository_relative_path":"plan.md","sha256":self.plan_hash,"byte_size":plan.stat().st_size,"artifact_type":"sealed-plan","description":"Sealed plan","read_condition":"Read during checkpoint validation"},{"reference_id":"evidence","repository_relative_path":"evidence.txt","sha256":evidence_hash,"byte_size":evidence.stat().st_size,"artifact_type":"evidence","description":"Validated evidence","read_condition":"Read during full validation"}],"NEXT_AUTHORIZED_ACTION":"Stop after publication","VALIDATION_STATUS":"VALID"}
        self.source = self.workspace / "body.json"; self.source.write_bytes(enc(self.state))
        self.request_value = {"REQUEST_ID":"request-1","CHECKPOINT_ID":"checkpoint-1","TASK_ID":self.state["TASK_ID"],"BODY_STATE_PATH":"body.json","BODY_STATE_SHA256":hashlib.sha256(self.source.read_bytes()).hexdigest(),"BODY_STATE_BYTE_SIZE":self.source.stat().st_size,"CHECKPOINT_PATH":"checkpoints/checkpoint.json"}
        (self.workspace / "checkpoints").mkdir()
    def tearDown(self): self.tmp.cleanup()
    def request(self, value=None): return enc(value or self.request_value)
    def create(self, value=None): return create_checkpoint(self.request(value), repository_root=self.repo, workspace_root=self.workspace)
    def assert_error(self, code, value=None):
        with self.assertRaises(CheckpointError) as caught: self.create(value)
        self.assertEqual(caught.exception.code, code)

    def test_create_structural_full_and_receipt(self):
        receipt = self.create(); path = self.workspace / receipt["CHECKPOINT_PATH"]; raw = path.read_bytes()
        self.assertEqual(receipt["STATUS"], "SUCCESS"); self.assertEqual(receipt["CHECKPOINT_SHA256"], hashlib.sha256(raw).hexdigest()); self.assertEqual(receipt["CHECKPOINT_BYTE_SIZE"], len(raw))
        self.assertEqual(validate_checkpoint_structure_bytes(raw)["TASK_ID"], self.state["TASK_ID"])
        self.assertEqual(validate_checkpoint_bytes(raw, repository_root=self.repo)["CHECKPOINT_ID"], "checkpoint-1")
        self.assertEqual(receipt["DURABILITY_MODE"], "ATOMIC_REPLACE_FILE_AND_DIRECTORY_FSYNC")
    def test_origin_binding_and_self_containment(self):
        self.create(); checkpoint = self.workspace / "checkpoints/checkpoint.json"; original = self.source.read_bytes(); value = json.loads(checkpoint.read_text())
        self.assertEqual(value["BODY_STATE_ORIGIN"], {"workspace_relative_path":"body.json","sha256":hashlib.sha256(original).hexdigest(),"byte_size":len(original)})
        self.source.unlink(); validate_checkpoint_structure_bytes(checkpoint.read_bytes()); self.source.write_bytes(b"changed\n"); validate_checkpoint_structure_bytes(checkpoint.read_bytes())
    def test_task_hash_size_and_body_validation_rejections(self):
        self.assert_error("TASK_ID_MISMATCH", dict(self.request_value, TASK_ID="other"))
        self.assert_error("BODY_STATE_HASH", dict(self.request_value, BODY_STATE_SHA256="0" * 64))
        self.assert_error("BODY_STATE_SIZE", dict(self.request_value, BODY_STATE_BYTE_SIZE=self.request_value["BODY_STATE_BYTE_SIZE"] + 1))
        bad = dict(self.state); bad["VALIDATION_STATUS"] = "x" * 257; self.source.write_bytes(enc(bad)); self.assert_error("BODY_STATE_SHORT_STRING", dict(self.request_value, BODY_STATE_SHA256=hashlib.sha256(self.source.read_bytes()).hexdigest(), BODY_STATE_BYTE_SIZE=self.source.stat().st_size))
    def test_artifact_and_plan_rejections(self):
        (self.repo / "evidence.txt").unlink(); self.assert_error("BODY_STATE_ARTIFACT_MISSING")
        self.source.write_bytes(enc(self.state)); (self.repo / "evidence.txt").write_text("changed", encoding="utf-8"); self.assert_error("BODY_STATE_ARTIFACT_MISMATCH")
        (self.repo / "evidence.txt").write_text("validated evidence\n", encoding="utf-8")
        self.source.write_bytes(enc(dict(self.state, SEALED_PLAN_SHA256="0" * 64))); request = dict(self.request_value, BODY_STATE_SHA256=hashlib.sha256(self.source.read_bytes()).hexdigest(), BODY_STATE_BYTE_SIZE=self.source.stat().st_size); self.assert_error("BODY_STATE_PLAN_HASH_MISMATCH", request)
    def test_checkpoint_tampering_and_artifact_change(self):
        self.create(); path = self.workspace / "checkpoints/checkpoint.json"; value = json.loads(path.read_text())
        for field in ("TASK_ID", "SEALED_PLAN_SHA256"):
            tampered = dict(value); tampered[field] = "tampered" if field == "TASK_ID" else "0" * 64
            with self.assertRaises(CheckpointError): validate_checkpoint_structure_bytes(enc(tampered))
        tampered = json.loads(path.read_text()); tampered["BODY_STATE_SNAPSHOT"]["CURRENT_STEP"] = "tampered"
        with self.assertRaises(CheckpointError): validate_checkpoint_structure_bytes(enc(tampered))
        tampered = json.loads(path.read_text()); tampered["VALIDATION_RECEIPT"]["status"] = "FAIL"
        with self.assertRaises(CheckpointError): validate_checkpoint_structure_bytes(enc(tampered))
        (self.repo / "evidence.txt").write_text("mutated", encoding="utf-8")
        with self.assertRaises(CheckpointError): validate_checkpoint_file(path, repository_root=self.repo, full=True)
    def test_limits_unknown_and_unsafe_paths(self):
        self.assert_error("REQUEST_FIELDS", dict(self.request_value, EXTRA="x"))
        oversized = enc(dict(self.request_value, REQUEST_ID="x" * 64)) + b"x" * REQUEST_MAX_BYTES
        with self.assertRaises(CheckpointError): create_checkpoint(oversized, repository_root=self.repo, workspace_root=self.workspace)
        for key, value in (("BODY_STATE_PATH", "/tmp/body"), ("CHECKPOINT_PATH", "/tmp/checkpoint"), ("BODY_STATE_PATH", "../body.json")):
            self.assert_error("UNSAFE_PATH", dict(self.request_value, **{key:value}))
    def test_symlinks_existing_target_and_preservation(self):
        os.symlink(self.source, self.workspace / "source-link")
        self.assert_error("SYMLINK_PATH", dict(self.request_value, BODY_STATE_PATH="source-link"))
        os.symlink(self.workspace / "checkpoints", self.workspace / "link-dir")
        self.assert_error("SYMLINK_PATH", dict(self.request_value, CHECKPOINT_PATH="link-dir/x.json"))
        existing = self.workspace / "checkpoints/existing.json"; existing.write_bytes(b"keep")
        self.assert_error("TARGET_EXISTS", dict(self.request_value, CHECKPOINT_PATH="checkpoints/existing.json")); self.assertEqual(existing.read_bytes(), b"keep")
    def test_atomic_temp_sibling_fsync_recheck_and_cleanup(self):
        seen = []; real_mkstemp = __import__("tempfile").mkstemp
        def mkstemp(*args, **kwargs):
            result = real_mkstemp(*args, **kwargs); seen.append(Path(result[1])); return result
        with patch("harness.checkpoint.tempfile.mkstemp", side_effect=mkstemp), patch("harness.checkpoint.os.fsync", wraps=os.fsync) as fsync:
            self.create()
        self.assertTrue(seen and seen[0].parent.resolve() == (self.workspace / "checkpoints").resolve()); self.assertGreaterEqual(fsync.call_count, 2); self.assertFalse(seen[0].exists())
        with patch("harness.checkpoint.os.replace", side_effect=RuntimeError("stop")):
            with self.assertRaises(CheckpointError): self.create(dict(self.request_value, CHECKPOINT_PATH="checkpoints/fail.json"))
        self.assertFalse((self.workspace / "checkpoints/fail.json").exists()); self.assertFalse(any(p.name.startswith(".fail.json.tmp-") for p in (self.workspace / "checkpoints").iterdir()))
    def test_checkpoint_size_and_metadata_only(self):
        receipt = self.create(); raw = (self.workspace / receipt["CHECKPOINT_PATH"]).read_bytes(); self.assertLessEqual(len(raw), CHECKPOINT_MAX_BYTES)
        text = raw.decode();
        for forbidden in ("full log", "report", "diff", "transcript", "review reasoning", "source payload"): self.assertNotIn(forbidden, text.lower())
        value = validate_checkpoint_structure_bytes(raw); self.assertEqual(value["BODY_STATE_SNAPSHOT"]["TASK_ID"], self.state["TASK_ID"])


if __name__ == "__main__": unittest.main()
