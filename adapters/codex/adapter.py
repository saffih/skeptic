from __future__ import annotations

import shutil

from concepts.stt.canonical import loads_strict
from concepts.stt.errors import STTError
from concepts.stt.host import HostAdapterError, InvocationReport, ProviderCapabilities, validated_invocation_report


class CodexAdapter:
    provider_id = "codex"
    ROLE_MAP = {"planner": "stt-planner", "reviewer": "stt-reviewer", "worker": "stt-worker"}

    def discover_capabilities(self) -> ProviderCapabilities:
        available = shutil.which("codex") is not None
        return ProviderCapabilities(self.provider_id, available, tuple(self.ROLE_MAP), True, True, "codex-invocation-v1")

    def provider_role(self, canonical_role: str) -> str:
        try:
            return self.ROLE_MAP[canonical_role]
        except KeyError as exc:
            raise HostAdapterError("unknown canonical semantic role") from exc

    def validate_provider_evidence(self, raw: bytes) -> InvocationReport:
        if not isinstance(raw, bytes):
            raise HostAdapterError("Codex invocation evidence must be bytes")
        try:
            value = loads_strict(raw)
        except (STTError, TypeError, AttributeError) as exc:
            raise HostAdapterError("Codex invocation evidence JSON invalid") from exc
        expected = {"kind", "invocation_id", "status", "timed_out", "exit_code"}
        if not isinstance(value, dict) or set(value) != expected or value["kind"] != "codex.invocation.v1":
            raise HostAdapterError("Codex invocation evidence schema invalid")
        return validated_invocation_report(provider_id=self.provider_id, invocation_id=value["invocation_id"], status=value["status"], timed_out=value["timed_out"], exit_code=value["exit_code"])
