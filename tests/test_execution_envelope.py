import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness.execution_envelope import (
    COMMAND_RECEIPT_LIMIT,
    ROLE_RETURN_LIMIT,
    TASK_ENVELOPE_LIMIT,
    ExecutionEnvelopeError,
    run_command,
    serialize_role_return,
    serialize_task_envelope,
    validate_command_receipt,
    validate_role_return,
    validate_task_envelope,
)


class EnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.plan = self.root / "plan.md"
        self.plan.write_text("external plan\n", encoding="utf-8")
        self.large = self.root / "large.bin"
        self.large.write_bytes(b"x" * 100_000)

    def tearDown(self):
        self.temp.cleanup()

    def ref(self, path, reference_id="plan"):
        raw = path.read_bytes()
        return {"reference_id": reference_id, "repository_relative_path": str(path.relative_to(self.root)), "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw), "artifact_type": "evidence", "description": "External artifact", "read_condition": "Read when authorized"}

    def task(self):
        ref = self.ref(self.plan)
        return {"task_id": "T-1", "objective": "Bound the Body", "scope": "Envelope only", "authority": "owner", "prohibitions": ["No inline reports"], "success_criteria": ["Receipts remain bounded"], "contract_references": [ref], "input_artifact_references": [dict(ref, reference_id="input")], "required_output_references": [dict(ref, reference_id="output")]}

    def role(self):
        return {"role": "worker", "status": "COMPLETE", "summary": "Artifact written", "produced_artifact_references": [self.ref(self.plan)], "findings": ["Evidence is external"], "blockers": [], "next_authorized_action": "Validate artifact"}

    def assert_code(self, fn, code, *args, **kwargs):
        with self.assertRaises(ExecutionEnvelopeError) as caught:
            fn(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def test_task_valid_compact_input_passes(self):
        raw = serialize_task_envelope(self.task(), repository_root=self.root)
        self.assertLessEqual(len(raw), TASK_ENVELOPE_LIMIT)

    def test_task_missing_required_field_fails(self):
        value = self.task(); del value["scope"]
        self.assert_code(validate_task_envelope, "FIELDS", value, repository_root=self.root)

    def test_task_unknown_field_fails(self):
        value = dict(self.task(), report="inline")
        self.assert_code(validate_task_envelope, "FIELDS", value, repository_root=self.root)

    def test_task_oversized_total_input_fails(self):
        value = self.task(); value["prohibitions"] = ["x" * 255] * 32
        self.assert_code(serialize_task_envelope, "TOO_LARGE", value, repository_root=self.root)

    def test_task_oversized_short_field_fails(self):
        value = self.task(); value["objective"] = "x" * 257
        self.assert_code(validate_task_envelope, "SHORT_STRING", value, repository_root=self.root)

    def test_task_absolute_and_traversal_paths_fail(self):
        value = self.task(); value["input_artifact_references"][0]["repository_relative_path"] = str(self.plan)
        self.assert_code(validate_task_envelope, "UNSAFE_PATH", value, repository_root=self.root)
        value = self.task(); value["input_artifact_references"][0]["repository_relative_path"] = "../plan.md"
        self.assert_code(validate_task_envelope, "UNSAFE_PATH", value, repository_root=self.root)

    def test_task_missing_reference_fails(self):
        value = self.task(); value["input_artifact_references"][0]["repository_relative_path"] = "missing"
        self.assert_code(validate_task_envelope, "ARTIFACT_MISSING", value, repository_root=self.root)

    def test_task_hash_or_size_mismatch_fails(self):
        value = self.task(); value["input_artifact_references"][0]["sha256"] = "0" * 64
        self.assert_code(validate_task_envelope, "ARTIFACT_MISMATCH", value, repository_root=self.root)
        value = self.task(); value["input_artifact_references"][0]["byte_size"] += 1
        self.assert_code(validate_task_envelope, "ARTIFACT_MISMATCH", value, repository_root=self.root)

    def test_large_external_source_does_not_enlarge_task_envelope(self):
        value = self.task(); value["input_artifact_references"] = [self.ref(self.large, "large")]
        self.assertLess(len(serialize_task_envelope(value, repository_root=self.root)), TASK_ENVELOPE_LIMIT)

    def test_role_valid_and_external_detail_passes(self):
        raw = serialize_role_return(self.role(), repository_root=self.root)
        self.assertLessEqual(len(raw), ROLE_RETURN_LIMIT)
        self.assertEqual(validate_role_return(self.role(), repository_root=self.root)["status"], "COMPLETE")

    def test_role_inline_content_and_unknown_artifact_fail(self):
        value = dict(self.role(), report="full report")
        self.assert_code(validate_role_return, "FIELDS", value, repository_root=self.root)
        value = self.role(); value["produced_artifact_references"][0]["repository_relative_path"] = "missing"
        self.assert_code(validate_role_return, "ARTIFACT_MISSING", value, repository_root=self.root)

    def test_role_oversized_return_fails(self):
        value = self.role(); value["findings"] = ["x" * 255] * 32
        self.assert_code(serialize_role_return, "TOO_LARGE", value, repository_root=self.root)

    def execute(self, command, name="command.log", **kwargs):
        return run_command("c-1", "test command", command, repository_root=self.root, cwd=self.root, log_path=name, **kwargs)

    def test_success_writes_complete_output_and_receipt_validates(self):
        receipt = self.execute([sys.executable, "-c", "print('out'); print('err', file=__import__('sys').stderr)"])
        self.assertEqual(receipt["status"], "SUCCEEDED")
        log = (self.root / "command.log").read_text()
        self.assertIn("out", log); self.assertIn("err", log)
        self.assertEqual(validate_command_receipt(receipt, repository_root=self.root)["log_byte_size"], len(log.encode()))

    def test_large_command_output_keeps_receipt_bounded(self):
        receipt = self.execute([sys.executable, "-c", "print('x' * 100000)"])
        self.assertLess(len(json.dumps(receipt, separators=(",", ":")).encode()), COMMAND_RECEIPT_LIMIT)
        self.assertGreater(receipt["log_byte_size"], 100000)

    def test_failed_command_preserves_output_and_is_nonzero(self):
        receipt = self.execute([sys.executable, "-c", "print('stdout'); print('stderr', file=__import__('sys').stderr); raise SystemExit(7)"])
        self.assertEqual(receipt["status"], "FAILED"); self.assertEqual(receipt["exit_code"], 7)
        log = (self.root / "command.log").read_text(); self.assertIn("stdout", log); self.assertIn("stderr", log)

    def test_command_start_failure_preserves_failure_log(self):
        receipt = self.execute([str(self.root / "does-not-exist")], name="start-failure.log")
        self.assertEqual(receipt["status"], "FAILED"); self.assertEqual(receipt["exit_code"], 127)
        self.assertIn("COMMAND_START_ERROR", (self.root / "start-failure.log").read_text())

    def test_successful_command_is_not_repeated(self):
        marker = self.root / "count"
        code = "from pathlib import Path; p=Path('count'); p.write_text(str(int(p.read_text() if p.exists() else '0')+1)); print('ok')"
        self.assertEqual(self.execute([sys.executable, "-c", code])["status"], "SUCCEEDED")
        self.assertEqual(marker.read_text(), "1")

    def git_setup(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(self.root), "config", "user.name", "Test"], check=True)
        (self.root / "tracked").write_text("tracked")
        subprocess.run(["git", "-C", str(self.root), "branch", "-M", "main"], check=True)
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-qm", "initial"], check=True)
        return subprocess.run(["git", "-C", str(self.root), "rev-parse", "HEAD"], check=True, text=True, stdout=subprocess.PIPE).stdout.strip()

    def expected(self, head, **changes):
        value = {"expected_repository_root": str(self.root), "expected_worktree": str(self.root), "expected_branch": "main", "expected_head": head, "required_clean": True, "mutation_authorized": True}
        value.update(changes); return value

    def test_correct_preflight_permits_mutation(self):
        head = self.git_setup(); marker = self.root / "marker"
        receipt = self.execute([sys.executable, "-c", "from pathlib import Path; Path('marker').write_text('changed')"], mutating=True, preflight=self.expected(head), name="mutate.log")
        self.assertEqual(receipt["status"], "SUCCEEDED"); self.assertTrue(marker.exists())

    def test_wrong_branch_head_root_worktree_clean_or_auth_blocks(self):
        head = self.git_setup()
        cases = [{"expected_branch": "wrong"}, {"expected_head": "0" * 40}, {"expected_repository_root": str(self.root / "other")}, {"expected_worktree": str(self.root / "other")}, {"required_clean": True}, {"mutation_authorized": False}]
        for i, change in enumerate(cases):
            if i == 4:
                (self.root / "dirty-marker").write_text("dirty")
            marker = self.root / f"marker-{i}"
            receipt = self.execute([sys.executable, "-c", f"from pathlib import Path; Path({str(marker)!r}).write_text('changed')"], mutating=True, preflight=self.expected(head, **change), name=f"blocked-{i}.log")
            self.assertEqual(receipt["status"], "BLOCKED")
            self.assertFalse(marker.exists())

    def test_missing_mutation_preflight_blocks_without_marker(self):
        marker = self.root / "marker"
        receipt = self.execute([sys.executable, "-c", "from pathlib import Path; Path('marker').write_text('changed')"], mutating=True, name="required-preflight.log")
        self.assertEqual(receipt["status"], "BLOCKED"); self.assertFalse(marker.exists())

    def test_slice_1_body_state_compatibility(self):
        from harness.body_state import validate_state_file
        self.assertEqual(validate_state_file(Path("experiments/body-brain-artifacts/examples/body-state.json"), repository_root=Path.cwd())["TASK_ID"], "TT-BODY-METADATA-SLICE-001")


if __name__ == "__main__":
    unittest.main()
