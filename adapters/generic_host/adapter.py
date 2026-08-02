from __future__ import annotations

from concepts.stt.canonical import loads_strict
from concepts.stt.errors import STTError
from concepts.stt.host import (
    HostAdapterError,
    InvocationReport,
    ProviderCapabilities,
    validated_invocation_report,
)


class GenericHostAdapter:
    provider_id = "generic-recorded-host"
    ROLE_MAP = {"planner": "planner", "reviewer": "reviewer", "worker": "worker"}

    def discover_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(self.provider_id, True, tuple(self.ROLE_MAP), True, True, "generic-recorded-v1")

    def provider_role(self, canonical_role: str) -> str:
        try:
            return self.ROLE_MAP[canonical_role]
        except KeyError as exc:
            raise HostAdapterError("unknown canonical semantic role") from exc

    def validate_provider_evidence(self, raw: bytes) -> InvocationReport:
        if not isinstance(raw, bytes):
            raise HostAdapterError("generic evidence must be bytes")
        try:
            value = loads_strict(raw)
        except (STTError, TypeError, AttributeError) as exc:
            raise HostAdapterError("generic evidence JSON invalid") from exc
        expected = {"provider_id", "invocation_id", "status", "timed_out", "exit_code"}
        if not isinstance(value, dict) or set(value) != expected or value.get("provider_id") != self.provider_id:
            raise HostAdapterError("generic evidence schema invalid")
        return validated_invocation_report(provider_id=value["provider_id"], invocation_id=value["invocation_id"], status=value["status"], timed_out=value["timed_out"], exit_code=value["exit_code"])
