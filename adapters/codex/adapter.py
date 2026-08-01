from __future__ import annotations

import json
import os
import shutil

from concepts.stt.host import HostAdapterError, InvocationReport, ProviderCapabilities


class CodexAdapter:
    provider_id = "codex"
    LEAD_ROLE = "lead"
    MODEL_ALIASES = {
        "economical": os.environ.get("STT_CODEX_ECONOMICAL_MODEL", ""),
        "standard": os.environ.get("STT_CODEX_STANDARD_MODEL", ""),
        "strongest": os.environ.get("STT_CODEX_STRONGEST_MODEL", ""),
    }
    ROLE_MAP = {"planner": "stt-planner", "reviewer": "stt-reviewer", "worker": "stt-worker"}

    def discover_capabilities(self) -> ProviderCapabilities:
        available = shutil.which("codex") is not None
        return ProviderCapabilities(self.provider_id, available, tuple(self.ROLE_MAP), True, True, True, "codex-replay-v1")

    def provider_role(self, canonical_role: str) -> str:
        try:
            return self.ROLE_MAP[canonical_role]
        except KeyError as exc:
            raise HostAdapterError("unknown canonical semantic role") from exc

    def validate_provider_evidence(self, raw: bytes) -> InvocationReport:
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HostAdapterError("Codex replay evidence JSON invalid") from exc
        expected = {"kind", "invocation_id", "status", "timed_out", "exit_code"}
        if not isinstance(value, dict) or set(value) != expected or value["kind"] != "codex.replay.v1":
            raise HostAdapterError("Codex replay evidence schema invalid")
        return InvocationReport(self.provider_id, str(value["invocation_id"]), value["status"], bool(value["timed_out"]), value["exit_code"], "UNAVAILABLE")
