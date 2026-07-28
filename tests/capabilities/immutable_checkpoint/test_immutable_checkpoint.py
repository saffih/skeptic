import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from capabilities.immutable_checkpoint.immutable_checkpoint import (
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
        self.assertEqual(receipt["DURABILITY_MODE"], "ATOMIC_HARD_LINK_FILE_AND_DIRECTORY_FSYNC")
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

    def test_validator_id_is_exactly_enforced(self):
        self.create(); path = self.workspace / "checkpoints/checkpoint.json"; value = json.loads(path.read_text())
        value["VALIDATION_RECEIPT"]["validator_id"] = "other.validator"
        with self.assertRaises(CheckpointError) as caught: validate_checkpoint_structure_bytes(enc(value))
        self.assertEqual(caught.exception.code, "RECEIPT_INVALID")

    def test_external_identity_rejects_coherent_rewrite(self):
        self.create(); path = self.workspace / "checkpoints/checkpoint.json"; raw = path.read_bytes(); value = json.loads(raw)
        value["BODY_STATE_SNAPSHOT"]["CURRENT_STEP"] = "rewritten"
        snapshot = enc(value["BODY_STATE_SNAPSHOT"])
        value["BODY_STATE_ORIGIN"]["sha256"] = hashlib.sha256(snapshot).hexdigest()
        value["BODY_STATE_ORIGIN"]["byte_size"] = len(snapshot)
        value["VALIDATION_RECEIPT"]["validated_body_state_sha256"] = value["BODY_STATE_ORIGIN"]["sha256"]
        rewritten = enc(value)
        validate_checkpoint_structure_bytes(rewritten)
        with self.assertRaises(CheckpointError) as caught:
            validate_checkpoint_bytes(rewritten, expected_sha256=hashlib.sha256(raw).hexdigest(), expected_byte_size=len(raw))
        self.assertEqual(caught.exception.code, "CHECKPOINT_IDENTITY_MISMATCH")

    def test_cli_external_identity_binding(self):
        receipt = self.create(); path = self.workspace / receipt["CHECKPOINT_PATH"]
        command = [sys.executable, "-m", "capabilities.immutable_checkpoint.immutable_checkpoint", "validate", str(path), "--expected-sha256", receipt["CHECKPOINT_SHA256"], "--expected-byte-size", str(receipt["CHECKPOINT_BYTE_SIZE"])]
        result = subprocess.run(command, cwd=Path(__file__).parents[3], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"CHECKPOINT_ID"', result.stdout)
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
        with patch("capabilities.immutable_checkpoint.immutable_checkpoint.tempfile.mkstemp", side_effect=mkstemp), patch("capabilities.immutable_checkpoint.immutable_checkpoint.os.fsync", wraps=os.fsync) as fsync:
            self.create()
        self.assertTrue(seen and seen[0].parent.resolve() == (self.workspace / "checkpoints").resolve()); self.assertGreaterEqual(fsync.call_count, 2); self.assertFalse(seen[0].exists())
        existing = self.workspace / "checkpoints/race.json"; existing.write_bytes(b"keep")
        with patch("capabilities.immutable_checkpoint.immutable_checkpoint.os.link", side_effect=FileExistsError("race")):
            with self.assertRaises(CheckpointError) as caught: self.create(dict(self.request_value, CHECKPOINT_PATH="checkpoints/race.json"))
        self.assertEqual(caught.exception.code, "TARGET_EXISTS"); self.assertEqual(existing.read_bytes(), b"keep")
        self.assertFalse(any(p.name.startswith(".race.json.tmp-") for p in (self.workspace / "checkpoints").iterdir()))

    def test_unexpected_directory_fsync_failure_is_post_publication(self):
        real_fsync = os.fsync; calls = [0]
        def fail_directory(fd):
            calls[0] += 1
            if calls[0] == 2: raise OSError("directory fsync failed")
            return real_fsync(fd)
        with patch("capabilities.immutable_checkpoint.immutable_checkpoint.os.fsync", side_effect=fail_directory):
            with self.assertRaises(CheckpointError) as caught: self.create()
        self.assertEqual(caught.exception.phase, "AFTER_PUBLICATION")
        self.assertTrue(caught.exception.final_checkpoint_exists)
        self.assertFalse(caught.exception.final_bytes_verified)

    def test_directory_fsync_unsupported_falls_back_truthfully(self):
        real_open = os.open
        def unsupported(path, *args):
            if str(path).endswith("checkpoints"): raise OSError(__import__("errno").ENOTSUP, "unsupported")
            return real_open(path, *args)
        with patch("capabilities.immutable_checkpoint.immutable_checkpoint.os.open", side_effect=unsupported):
            receipt = self.create()
        self.assertEqual(receipt["DURABILITY_MODE"], "ATOMIC_HARD_LINK_FILE_FSYNC_ONLY")

    def test_post_publication_readback_reports_phase_and_final_state(self):
        real_link = os.link
        def publish_then_corrupt(source, target):
            real_link(source, target)
            Path(target).write_bytes(b"corrupted-after-publication")
        with patch("capabilities.immutable_checkpoint.immutable_checkpoint.os.link", side_effect=publish_then_corrupt):
            with self.assertRaises(CheckpointError) as caught: self.create()
        self.assertEqual(caught.exception.phase, "AFTER_PUBLICATION")
        self.assertTrue(caught.exception.final_checkpoint_exists)
        self.assertFalse(caught.exception.final_bytes_verified)

    def test_creation_receipt_failure_reports_post_publication_state(self):
        with patch("capabilities.immutable_checkpoint.immutable_checkpoint._receipt", side_effect=CheckpointError("RECEIPT_GENERATION")):
            with self.assertRaises(CheckpointError) as caught: self.create()
        self.assertEqual(caught.exception.phase, "AFTER_PUBLICATION")
        self.assertTrue(caught.exception.final_checkpoint_exists)
        self.assertTrue(caught.exception.final_bytes_verified)
    def test_checkpoint_size_and_metadata_only(self):
        receipt = self.create(); raw = (self.workspace / receipt["CHECKPOINT_PATH"]).read_bytes(); self.assertLessEqual(len(raw), CHECKPOINT_MAX_BYTES)
        text = raw.decode();
        for forbidden in ("full log", "report", "diff", "transcript", "review reasoning", "source payload"): self.assertNotIn(forbidden, text.lower())
        value = validate_checkpoint_structure_bytes(raw); self.assertEqual(value["BODY_STATE_SNAPSHOT"]["TASK_ID"], self.state["TASK_ID"])


if __name__ == "__main__": unittest.main()
