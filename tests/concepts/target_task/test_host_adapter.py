import json
import tempfile
import unittest
from pathlib import Path

from adapters.claude_code import ClaudeCodeAdapter
from adapters.codex import CodexAdapter
from adapters.generic_host import GenericHostAdapter
from concepts.stt.errors import STTError
from concepts.target_task.host_adapter import (
    CANONICAL_ROLES,
    HostAdapterError,
    canonical_invocation_evidence,
    persist_raw_provider_evidence,
)


class HostAdapterContractTests(unittest.TestCase):
    def test_core_is_provider_neutral_and_role_maps_normalize(self):
        self.assertEqual(CANONICAL_ROLES, {"planner", "reviewer", "worker", "command"})
        claude = ClaudeCodeAdapter()
        codex = CodexAdapter()
        generic = GenericHostAdapter()
        self.assertEqual(claude.discover_capabilities().semantic_roles, tuple(claude.ROLE_MAP))
        for role in {"planner", "reviewer", "worker"}:
            self.assertTrue(claude.provider_role(role))
            self.assertTrue(codex.provider_role(role))
            self.assertEqual(generic.provider_role(role), role)
        for adapter in (claude, codex, generic):
            with self.assertRaises(STTError):
                adapter.provider_role("command")

    def test_raw_evidence_is_immutable_and_provider_specific(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude_raw = b'{"type":"result","session_id":"c-1","is_error":false}\n'
            ref = persist_raw_provider_evidence(root, "claude-code", claude_raw)
            self.assertEqual((root / ref["repository_relative_path"]).read_bytes(), claude_raw)
            self.assertEqual(ClaudeCodeAdapter().validate_provider_evidence(claude_raw).invocation_id, "c-1")
            with self.assertRaises(STTError):
                CodexAdapter().validate_provider_evidence(claude_raw)

    def test_malformed_missing_duplicate_and_body_returns_fail(self):
        good = {"schema_version": "1", "provider_id": "generic-recorded-host", "invocation_id": "i", "task_id": "t", "operation_id": "o", "canonical_role": "worker", "provider_role": "worker", "attempt": 1, "request_ref": {}, "raw_provider_evidence_ref": {}, "normalized_receipt_ref": {}, "completion_status": "COMPLETE", "timeout": False, "exit_status": 0, "cost_metadata": "UNAVAILABLE"}
        canonical_invocation_evidence(good)
        for bad in ({**good, "body": "not a receipt"}, {key: value for key, value in good.items() if key != "raw_provider_evidence_ref"}, {**good, "completion_status": "BODY"}):
            with self.assertRaises(HostAdapterError):
                canonical_invocation_evidence(bad)

    def test_timeout_reports_unknown(self):
        adapter = GenericHostAdapter()
        report = adapter.validate_provider_evidence(json.dumps({"provider_id": adapter.provider_id, "invocation_id": "i", "status": "UNKNOWN", "timed_out": True, "exit_code": None}).encode())
        self.assertEqual((report.status, report.timed_out), ("UNKNOWN", True))


if __name__ == "__main__":
    unittest.main()
