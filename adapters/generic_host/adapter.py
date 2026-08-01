from __future__ import annotations

import json

from concepts.stt.host import HostAdapterError, InvocationReport, ProviderCapabilities


class GenericHostAdapter:
    provider_id = "generic-recorded-host"
    LEAD_ROLE = "lead"
    MODEL_ALIASES = {"economical": "recorded-economical", "standard": "recorded-standard", "strongest": "recorded-strongest"}
    ROLE_MAP = {"planner": "planner", "reviewer": "reviewer", "worker": "worker"}

    def discover_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(self.provider_id, True, tuple(self.ROLE_MAP), True, True, True, "generic-recorded-v1")

    def provider_role(self, canonical_role: str) -> str:
        try:
            return self.ROLE_MAP[canonical_role]
        except KeyError as exc:
            raise HostAdapterError("unknown canonical semantic role") from exc

    def validate_provider_evidence(self, raw: bytes) -> InvocationReport:
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HostAdapterError("generic evidence JSON invalid") from exc
        expected = {"provider_id", "invocation_id", "status", "timed_out", "exit_code"}
        if not isinstance(value, dict) or set(value) != expected or value["provider_id"] != self.provider_id:
            raise HostAdapterError("generic evidence schema invalid")
        if value["status"] not in {"COMPLETE", "FAILED", "UNKNOWN"}:
            raise HostAdapterError("generic evidence status invalid")
        return InvocationReport(self.provider_id, str(value["invocation_id"]), value["status"], bool(value["timed_out"]), value["exit_code"], "UNAVAILABLE")
