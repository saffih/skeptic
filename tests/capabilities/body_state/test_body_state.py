import hashlib, json, tempfile, unittest
from pathlib import Path
from capabilities.body_state.body_state import MAX_STATE_BYTES, BodyStateError, validate_state_bytes, validate_state_file

def enc(value): return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()

class BodyStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name); p = self.root / "evidence.bin"; p.write_bytes(b"external evidence\n")
        h = hashlib.sha256(p.read_bytes()).hexdigest(); self.state = {"TASK_ID":"TT-BODY-METADATA-SLICE-001","SEALED_PLAN_REFERENCE":"evidence.bin","SEALED_PLAN_SHA256":h,"CURRENT_STEP":"validate","COMPLETED_STEP_IDS":[],"VALIDATED_FACTS":[{"summary":"External evidence exists","status":"verified","artifact_reference_ids":["e1"]}],"OPEN_BLOCKERS":[],"ARTIFACT_REFERENCES":[{"reference_id":"e1","repository_relative_path":"evidence.bin","sha256":h,"byte_size":p.stat().st_size,"artifact_type":"evidence","description":"External evidence file","read_condition":"Read when validating the next action"}],"NEXT_AUTHORIZED_ACTION":"Validate external evidence","VALIDATION_STATUS":"VALID"}
    def tearDown(self): self.tmp.cleanup()
    def valid(self, state=None): return validate_state_bytes(enc(state or self.state), repository_root=self.root)
    def invalid(self, state=None, raw=None, code=None):
        with self.assertRaises(BodyStateError) as c: validate_state_bytes(raw, repository_root=self.root) if raw is not None else self.valid(state)
        if code: self.assertEqual(c.exception.code, code)
    def test_valid_and_correct_metadata_pass(self): self.assertEqual(self.valid()["TASK_ID"], self.state["TASK_ID"])
    def test_missing_unknown_and_inline_content_fail(self):
        for bad in ({k:v for k,v in self.state.items() if k != "CURRENT_STEP"}, dict(self.state, UNKNOWN="x"), dict(self.state, RAW_CONTENT="full log")): self.invalid(bad, code="STATE_FIELDS")
    def test_oversized_summary_and_total_fail(self):
        self.invalid(dict(self.state, NEXT_AUTHORIZED_ACTION="x"*257), code="SHORT_STRING"); self.invalid(raw=b"{"+b"x"*MAX_STATE_BYTES+b"}\n", code="STATE_TOO_LARGE")
    def test_absolute_and_traversal_paths_fail(self):
        for path in ("/tmp/evidence.bin", "../evidence.bin", "a/../evidence.bin"): self.invalid(dict(self.state, ARTIFACT_REFERENCES=[dict(self.state["ARTIFACT_REFERENCES"][0], repository_relative_path=path)]), code="UNSAFE_PATH")
    def test_missing_and_mismatched_artifact_fail(self):
        self.invalid(dict(self.state, ARTIFACT_REFERENCES=[dict(self.state["ARTIFACT_REFERENCES"][0], repository_relative_path="missing")]), code="ARTIFACT_MISSING")
        self.invalid(dict(self.state, ARTIFACT_REFERENCES=[dict(self.state["ARTIFACT_REFERENCES"][0], sha256="0"*64)], SEALED_PLAN_SHA256="0"*64), code="ARTIFACT_MISMATCH")
    def test_malformed_sha_fails(self): self.invalid(dict(self.state, SEALED_PLAN_SHA256="bad"), code="SHA256")
    def test_large_external_artifact_stays_external(self):
        p=self.root/"large"; p.write_bytes(b"z"*2_000_000); h=hashlib.sha256(p.read_bytes()).hexdigest(); ref=dict(self.state["ARTIFACT_REFERENCES"][0],repository_relative_path="large",sha256=h,byte_size=p.stat().st_size); state=dict(self.state,SEALED_PLAN_REFERENCE="large",SEALED_PLAN_SHA256=h,ARTIFACT_REFERENCES=[ref],VALIDATED_FACTS=[]); self.assertLess(len(enc(state)),MAX_STATE_BYTES); self.valid(state)
    def test_multiple_references_remain_compact(self):
        refs=[]
        for i in range(1,20):
            p=self.root/f"e{i}"; p.write_text(str(i)); refs.append({"reference_id":f"e{i}","repository_relative_path":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"byte_size":p.stat().st_size,"artifact_type":"evidence","description":"external evidence","read_condition":"Read when needed"})
        state=dict(self.state,SEALED_PLAN_REFERENCE="e1",SEALED_PLAN_SHA256=refs[0]["sha256"],ARTIFACT_REFERENCES=refs,VALIDATED_FACTS=[]); self.assertLess(len(enc(state)),MAX_STATE_BYTES); self.valid(state)
    def test_facts_need_evidence(self): self.invalid(dict(self.state,VALIDATED_FACTS=[{"summary":"unsupported","status":"verified","artifact_reference_ids":[] }]),code="FACT_WITHOUT_EVIDENCE")
    def test_malformed_encoding_and_duplicate_keys_fail(self): self.invalid(raw=b'{"TASK_ID":"x","TASK_ID":"y"}\n',code="DUPLICATE_KEY"); self.invalid(raw=enc(self.state).replace(b"\n",b"\n\n"),code="ENCODING")
    def test_file_api_and_task_id(self):
        p=self.root/"state"; p.write_bytes(enc(self.state)); self.assertEqual(validate_state_file(p,repository_root=self.root,expected_task_id=self.state["TASK_ID"])["CURRENT_STEP"],"validate")
        with self.assertRaises(BodyStateError) as c: validate_state_file(p,repository_root=self.root,expected_task_id="other")
        self.assertEqual(c.exception.code,"TASK_ID_MISMATCH")
    def test_templates_reference_the_single_contract(self):
        root = Path(__file__).parents[3]
        body = (root / "experiments/body-brain-artifacts/body.md").read_text()
        readme = (root / "experiments/body-brain-artifacts/README.md").read_text()
        agents = (root / "AGENTS.md").read_text()
        self.assertIn("capabilities/body_state/body_state.py", body)
        self.assertIn("capabilities/body_state/body_state.md", readme)
        self.assertIn("metadata-only Body state", agents)

if __name__ == "__main__": unittest.main()
