import hashlib
import inspect
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from harness import focused_retrieval as fr
from harness.body_state import validate_state_bytes, validate_state_structure_bytes


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


class FocusedRetrievalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.plan = self.root / "plan.md"
        self.plan.write_bytes(b"sealed plan\n")
        self.source = self.root / "source.txt"
        self.source.write_bytes(b"one\r\ntwo\nthree")
        self.state_path = self.root / "body-state.json"
        self.write_state()

    def tearDown(self):
        self.temp.cleanup()

    def ref(self, path, rid):
        raw = path.read_bytes()
        return {"reference_id": rid, "repository_relative_path": path.name, "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw), "artifact_type": "text", "description": "fixture", "read_condition": "authorized"}

    def write_state(self, source=None, extra_refs=None):
        source = source or self.source
        refs = [self.ref(self.plan, "plan"), self.ref(source, "source")]
        refs.extend(extra_refs or [])
        state = {"TASK_ID": "TT-FOCUSED-RETRIEVAL-SLICE-003", "SEALED_PLAN_REFERENCE": "plan.md", "SEALED_PLAN_SHA256": hashlib.sha256(self.plan.read_bytes()).hexdigest(), "CURRENT_STEP": "retrieve", "COMPLETED_STEP_IDS": [], "VALIDATED_FACTS": [], "OPEN_BLOCKERS": [], "ARTIFACT_REFERENCES": refs, "NEXT_AUTHORIZED_ACTION": "retrieve one range", "VALIDATION_STATUS": "VALID"}
        self.state_path.write_bytes(canonical(state))
        self.state = state

    def request(self, **changes):
        value = {"REQUEST_ID": "req-1", "TASK_ID": self.state["TASK_ID"], "STEP_ID": "retrieve", "PURPOSE": "focused retrieval", "BODY_STATE_PATH": "body-state.json", "BODY_STATE_SHA256": hashlib.sha256(self.state_path.read_bytes()).hexdigest(), "BODY_STATE_BYTE_SIZE": self.state_path.stat().st_size, "ARTIFACT_REFERENCE_ID": "source", "START_LINE": 1, "END_LINE": 2, "MAX_EXCERPT_BYTES": 4096}
        value.update(changes)
        return value

    def execute(self, **changes):
        return fr.process_request(canonical(self.request(**changes)), repository_root=self.root)

    def test_valid_exact_range_and_provenance(self):
        code, raw = self.execute()
        result = json.loads(raw)
        self.assertEqual(code, 0)
        self.assertEqual(result["EXCERPT"], "one\r\ntwo\n")
        self.assertEqual(result["EXCERPT_BYTE_SIZE"], len(b"one\r\ntwo\n"))
        self.assertEqual(result["EXCERPT_SHA256"], hashlib.sha256(b"one\r\ntwo\n").hexdigest())
        self.assertEqual(result["SOURCE_SHA256"], hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertEqual(result["SOURCE_PATH"], "source.txt")

    def test_line_semantics_and_final_unterminated_line(self):
        self.source.write_bytes(b"a\nb\nc")
        self.write_state()
        code, raw = self.execute(START_LINE=3, END_LINE=3)
        self.assertEqual(code, 0); self.assertEqual(json.loads(raw)["EXCERPT"], "c")
        self.source.write_bytes(b"a\n")
        self.write_state()
        self.assertEqual(self.execute(START_LINE=2, END_LINE=2)[0], 2)

    def test_empty_file_has_zero_lines(self):
        self.source.write_bytes(b""); self.write_state()
        self.assertEqual(self.execute(START_LINE=1, END_LINE=1)[0], 2)

    def test_body_state_exact_hash_and_size_and_mismatch(self):
        self.assertEqual(self.execute()[0], 0)
        code, raw = self.execute(BODY_STATE_SHA256="0" * 64)
        self.assertEqual(code, 2); self.assertEqual(json.loads(raw)["ERROR_CODE"], "BODY_STATE_MISMATCH")
        self.assertEqual(self.execute(BODY_STATE_BYTE_SIZE=self.state_path.stat().st_size + 1)[0], 2)

    def test_task_step_and_reference_failures(self):
        for changes, error in (({"TASK_ID": "other"}, "TASK_MISMATCH"), ({"STEP_ID": "wrong"}, "STEP_MISMATCH"), ({"ARTIFACT_REFERENCE_ID": "unknown"}, "UNKNOWN_ARTIFACT_REFERENCE")):
            code, raw = self.execute(**changes)
            self.assertEqual(code, 2); self.assertEqual(json.loads(raw)["ERROR_CODE"], error)

    def test_source_mismatch_and_missing_source(self):
        self.source.write_bytes(b"changed\nline-two\n")
        code, raw = self.execute()
        self.assertEqual(code, 2); self.assertEqual(json.loads(raw)["ERROR_CODE"], "SOURCE_MISMATCH")
        self.source.unlink()
        code, raw = self.execute()
        self.assertEqual(code, 2); self.assertEqual(json.loads(raw)["ERROR_CODE"], "SOURCE_MISSING")

    def test_ranges_reject_zero_negative_boolean_reversed_and_excessive(self):
        for changes in ({"START_LINE": 0}, {"START_LINE": -1}, {"START_LINE": True}, {"START_LINE": 2, "END_LINE": 1}, {"END_LINE": 65}):
            self.assertEqual(self.execute(**changes)[0], 2)

    def test_beyond_eof_and_excerpt_limit_are_not_truncated(self):
        self.assertEqual(self.execute(START_LINE=3, END_LINE=4)[0], 2)
        self.source.write_bytes(b"x" * 20); self.write_state()
        code, raw = self.execute(START_LINE=1, END_LINE=1, MAX_EXCERPT_BYTES=4)
        self.assertEqual(code, 2); self.assertEqual(json.loads(raw)["ERROR_CODE"], "EXCERPT_TOO_LARGE")

    def test_invalid_utf8_before_inside_after_and_nul_fail(self):
        for data in (b"\xff\nvalid", b"valid\xff\n", b"valid\n\xff", b"valid\x00\n"):
            self.source.write_bytes(data); self.write_state()
            code, raw = self.execute(START_LINE=1, END_LINE=1)
            self.assertEqual(code, 2); self.assertIn(json.loads(raw)["ERROR_CODE"], {"INVALID_UTF8", "NUL_SOURCE"})

    def test_unknown_fields_oversized_request_and_result_bound(self):
        self.assertEqual(self.execute(UNKNOWN="x")[0], 2)
        oversized = canonical(self.request(PURPOSE="x" * 256)) + b"x" * 8000
        self.assertEqual(fr.process_request(oversized, repository_root=self.root)[0], 2)
        self.source.write_bytes(b"a\n" * 64); self.write_state()
        with patch.object(fr, "RESULT_LIMIT", 100):
            code, raw = self.execute(START_LINE=1, END_LINE=64, MAX_EXCERPT_BYTES=4096)
        self.assertEqual(code, 2); self.assertEqual(json.loads(raw)["ERROR_CODE"], "RESULT_TOO_LARGE")

    def test_structure_only_does_not_open_unrequested_or_missing_artifacts(self):
        missing = {"reference_id": "missing", "repository_relative_path": "missing.txt", "sha256": "0" * 64, "byte_size": 0, "artifact_type": "text", "description": "missing", "read_condition": "not requested"}
        self.write_state(extra_refs=[missing])
        raw = canonical(self.request())
        original = Path.open
        with patch.object(fr.Path, "open", autospec=True, side_effect=original) as opened:
            self.assertEqual(fr.process_request(raw, repository_root=self.root)[0], 0)
        paths = [str(call.args[0]) for call in opened.call_args_list if call.args]
        self.assertNotIn("missing.txt", " ".join(paths))

    def test_source_is_opened_once_and_large_source_stays_streamed(self):
        self.source.write_bytes(b"small\n" + b"z" * 2_000_000 + b"\nlast\n"); self.write_state()
        original = Path.open
        calls = []
        def counted(path, *args, **kwargs):
            if Path(path).name == "source.txt": calls.append(path)
            return original(path, *args, **kwargs)
        with patch("harness.focused_retrieval.Path.open", new=counted):
            code, raw = self.execute(START_LINE=1, END_LINE=1, MAX_EXCERPT_BYTES=64)
        self.assertEqual(code, 0); self.assertEqual(len(calls), 1); self.assertEqual(json.loads(raw)["EXCERPT"], "small\n")

    def test_prohibited_unbounded_source_reads_are_absent(self):
        source = inspect.getsource(fr._source_excerpt)
        self.assertNotIn("read()", source); self.assertNotIn("readline()", source); self.assertNotIn("read_text", source); self.assertNotIn("read_bytes", source)

    def test_full_body_validator_behavior_remains_and_structure_checks_plan(self):
        self.assertEqual(validate_state_bytes(self.state_path.read_bytes(), repository_root=self.root)["TASK_ID"], self.state["TASK_ID"])
        self.state["SEALED_PLAN_SHA256"] = "0" * 64
        with self.assertRaises(Exception): validate_state_structure_bytes(canonical(self.state))


if __name__ == "__main__":
    unittest.main()
