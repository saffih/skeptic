#!/usr/bin/env python3
"""Credit-free qualification of the provider-neutral recorded-host seam."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from adapters.codex import CodexAdapter
from adapters.claude_code import ClaudeCodeAdapter
from adapters.generic_host import GenericHostAdapter
from concepts.target_task.host_adapter import CANONICAL_ROLES, canonical_invocation_evidence, persist_raw_provider_evidence


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        adapters = (GenericHostAdapter(), ClaudeCodeAdapter(), CodexAdapter())
        for adapter in adapters:
            assert adapter.discover_capabilities().available
            for role in CANONICAL_ROLES:
                assert adapter.provider_role(role)
        raw = b'{"provider_id":"generic-recorded-host","invocation_id":"i-1","completion_status":"COMPLETE","timeout":false,"exit_status":0}'
        raw_ref = persist_raw_provider_evidence(root, "generic-recorded-host", raw)
        for index, role in enumerate(("worker", "command"), 1):
            evidence = {
                "schema_version": "1", "provider_id": "generic-recorded-host", "invocation_id": f"i-{index}",
                "task_id": "generic-smoke", "operation_id": f"op-{index}", "canonical_role": role,
                "provider_role": role, "attempt": 1, "request_ref": {"repository_relative_path": f"requests/op-{index}.json"},
                "raw_provider_evidence_ref": raw_ref, "normalized_receipt_ref": {"repository_relative_path": f"receipts/op-{index}.json"},
                "completion_status": "COMPLETE", "timeout": False, "exit_status": 0, "cost_metadata": "UNAVAILABLE",
            }
            canonical_invocation_evidence(evidence)
        print(json.dumps({"status": "PASS", "provider": "generic-recorded-host", "accepted_steps": 2, "credits": "NONE", "roles": sorted(CANONICAL_ROLES)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
