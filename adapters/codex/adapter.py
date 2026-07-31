"""Codex adapter contract/replay path with a separate evidence schema."""

from __future__ import annotations

import json
import os
import shutil

from concepts.target_task.host_adapter import HostAdapterError, InvocationReport, ProviderCapabilities, TargetTaskHostAdapter


class CodexAdapter(TargetTaskHostAdapter):
    provider_id = "codex"
    LEAD_ROLE = "lead"
    MODEL_ALIASES = {
        "small": os.environ.get("TT_CODEX_SMALL_MODEL", ""),
        "medium": os.environ.get("TT_CODEX_MEDIUM_MODEL", ""),
        "strongest": os.environ.get("TT_CODEX_STRONGEST_MODEL", ""),
    }
    LAUNCH_MODE = "codex-cli"
    ROLE_MAP = {"planner": "codex-planner", "reviewer": "codex-reviewer", "worker": "codex-worker", "command": "codex-command"}

    def discover_capabilities(self) -> ProviderCapabilities:
        available = shutil.which("codex") is not None
        return ProviderCapabilities(self.provider_id, available, tuple(self.ROLE_MAP), available, "codex-replay")

    def provider_role(self, canonical_role: str) -> str:
        try:
            return self.ROLE_MAP[canonical_role]
        except KeyError as exc:
            raise HostAdapterError("unknown canonical role") from exc

    def validate_provider_evidence(self, raw: bytes) -> InvocationReport:
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HostAdapterError("Codex replay evidence JSON") from exc
        if not isinstance(value, dict) or set(value) != {"kind", "invocation_id", "status", "timed_out", "exit_code"} or value["kind"] != "codex.replay.v1":
            raise HostAdapterError("Codex evidence schema")
        return InvocationReport(self.provider_id, value["invocation_id"], value["status"], value["timed_out"], value["exit_code"], "UNAVAILABLE")
