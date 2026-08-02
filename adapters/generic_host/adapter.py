from __future__ import annotations

import json

from concepts.stt.host import DispatchRequest, HostAdapterError, InvocationReport, ProviderCapabilities


class GenericHostAdapter:
    provider_id = "generic-recorded-host"
    LEAD_ROLE = "lead"
    MODEL_ALIASES = {"small": "recorded-small", "medium": "recorded-medium", "strongest": "recorded-strongest", "economical": "recorded-economical", "standard": "recorded-standard"}
    ROLE_MAP = {"planner": "planner", "reviewer": "reviewer", "worker": "worker", "command": "command"}

    def discover_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(self.provider_id, True, tuple(self.ROLE_MAP), True, True, True, "generic-recorded-v1")

    def provider_role(self, canonical_role: str) -> str:
        try:
            return self.ROLE_MAP[canonical_role]
        except KeyError as exc:
            raise HostAdapterError("unknown canonical semantic role") from exc

    def build_dispatch_request(self, request):
        role = request.get("role")
        return DispatchRequest(request["task_id"], request["operation_id"], request["attempt"], role, self.provider_role(role), request)

    def report_outcome(self, report):
        return "UNKNOWN" if report.timed_out else report.status

    def validate_provider_evidence(self, raw: bytes) -> InvocationReport:
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HostAdapterError("generic evidence JSON invalid") from exc
        expected = {"provider_id", "invocation_id", "status", "timed_out", "exit_code"}
        legacy = {"provider_id", "invocation_id", "completion_status", "timeout", "exit_status"}
        if not isinstance(value, dict) or (set(value) != expected and set(value) != legacy) or value["provider_id"] != self.provider_id:
            raise HostAdapterError("generic evidence schema invalid")
        if set(value) == legacy:
            return InvocationReport(self.provider_id, str(value["invocation_id"]), value["completion_status"], bool(value["timeout"]), value["exit_status"], "UNAVAILABLE")
        if value["status"] not in {"COMPLETE", "FAILED", "UNKNOWN"}:
            raise HostAdapterError("generic evidence status invalid")
        return InvocationReport(self.provider_id, str(value["invocation_id"]), value["status"], bool(value["timed_out"]), value["exit_code"], "UNAVAILABLE")
