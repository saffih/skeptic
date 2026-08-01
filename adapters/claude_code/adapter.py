from __future__ import annotations

import json
import os
import shutil

from concepts.stt.host import HostAdapterError, InvocationReport, ProviderCapabilities


class ClaudeCodeAdapter:
    provider_id = "claude-code"
    LEAD_ROLE = "lead"
    MODEL_ALIASES = {
        "economical": os.environ.get("STT_CLAUDE_ECONOMICAL_MODEL", "haiku"),
        "standard": os.environ.get("STT_CLAUDE_STANDARD_MODEL", "sonnet"),
        "strongest": os.environ.get("STT_CLAUDE_STRONGEST_MODEL", "opus"),
    }
    ROLE_MAP = {"planner": "stt-planner", "reviewer": "stt-reviewer", "worker": "stt-worker"}

    def discover_capabilities(self) -> ProviderCapabilities:
        available = shutil.which("claude") is not None
        return ProviderCapabilities(self.provider_id, available, tuple(self.ROLE_MAP), True, True, True, "claude-stream-json")

    def provider_role(self, canonical_role: str) -> str:
        try:
            return self.ROLE_MAP[canonical_role]
        except KeyError as exc:
            raise HostAdapterError("unknown canonical semantic role") from exc

    def validate_provider_evidence(self, raw: bytes) -> InvocationReport:
        events = []
        for line in raw.splitlines():
            try:
                item = json.loads(line.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise HostAdapterError("Claude evidence is not stream-json") from exc
            if not isinstance(item, dict):
                raise HostAdapterError("Claude evidence event must be an object")
            events.append(item)
        results = [item for item in events if item.get("type") == "result"]
        if len(results) != 1:
            raise HostAdapterError("Claude completion event missing or ambiguous")
        result = results[0]
        return InvocationReport(self.provider_id, str(result.get("session_id", "UNKNOWN")), "FAILED" if result.get("is_error") is True else "COMPLETE", False, result.get("exit_status"), result.get("total_cost_usd", "UNAVAILABLE"))
