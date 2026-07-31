"""Claude Code adapter; Claude stream-json is deliberately not core protocol."""

from __future__ import annotations

import json
import os
import shutil

from concepts.target_task.host_adapter import HostAdapterError, InvocationReport, ProviderCapabilities, TargetTaskHostAdapter


class ClaudeCodeAdapter(TargetTaskHostAdapter):
    provider_id = "claude-code"
    LEAD_ROLE = "lead"
    MODEL_ALIASES = {
        "small": os.environ.get("TT_CLAUDE_SMALL_MODEL", "haiku"),
        "medium": os.environ.get("TT_CLAUDE_MEDIUM_MODEL", "sonnet"),
        "strongest": os.environ.get("TT_CLAUDE_STRONGEST_MODEL", "opus"),
    }
    LAUNCH_MODE = "claude-cli"
    ROLE_MAP = {"planner": "target-task-planner", "reviewer": "target-task-reviewer", "worker": "target-task-worker", "command": "target-task-command"}

    def discover_capabilities(self) -> ProviderCapabilities:
        available = shutil.which("claude") is not None
        return ProviderCapabilities(self.provider_id, available, tuple(self.ROLE_MAP), available, "claude-stream-json")

    def provider_role(self, canonical_role: str) -> str:
        try:
            return self.ROLE_MAP[canonical_role]
        except KeyError as exc:
            raise HostAdapterError("unknown canonical role") from exc

    def validate_provider_evidence(self, raw: bytes) -> InvocationReport:
        events = []
        for line in raw.splitlines():
            try:
                value = json.loads(line.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise HostAdapterError("Claude evidence is not stream-json") from exc
            if not isinstance(value, dict):
                raise HostAdapterError("Claude event must be an object")
            events.append(value)
        if not events or not any(event.get("type") == "result" for event in events):
            raise HostAdapterError("Claude completion event missing")
        result = next(event for event in events if event.get("type") == "result")
        return InvocationReport(self.provider_id, str(result.get("session_id", "claude-invocation")), "COMPLETE" if result.get("is_error") is not True else "FAILED", False, result.get("exit_status", 0), result.get("total_cost_usd", "UNAVAILABLE"))
