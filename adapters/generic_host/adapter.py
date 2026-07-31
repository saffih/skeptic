"""Deterministic recorded-host adapter used by tests and qualification."""

from __future__ import annotations

from pathlib import Path

from concepts.target_task.host_adapter import (
    InvocationReport, ProviderCapabilities, TargetTaskHostAdapter, HostAdapterError,
)


class GenericHostAdapter(TargetTaskHostAdapter):
    provider_id = "generic-recorded-host"
    LEAD_ROLE = "lead"
    MODEL_ALIASES = {"small": "recorded-small", "medium": "recorded-medium", "strongest": "recorded-strongest"}
    LAUNCH_MODE = "recorded"

    def discover_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(self.provider_id, True, ("planner", "reviewer", "worker", "command"), True, "recorded")

    def provider_role(self, canonical_role: str) -> str:
        if canonical_role not in {"planner", "reviewer", "worker", "command"}:
            raise HostAdapterError("unknown canonical role")
        return canonical_role

    def validate_provider_evidence(self, raw: bytes) -> InvocationReport:
        import json
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HostAdapterError("generic evidence JSON") from exc
        if not isinstance(value, dict) or set(value) != {"provider_id", "invocation_id", "completion_status", "timeout", "exit_status"}:
            raise HostAdapterError("generic evidence schema")
        if value["provider_id"] != self.provider_id:
            raise HostAdapterError("generic provider identity mismatch")
        return InvocationReport(self.provider_id, value["invocation_id"], value["completion_status"], value["timeout"], value["exit_status"], "UNAVAILABLE")
