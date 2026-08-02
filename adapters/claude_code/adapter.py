from __future__ import annotations

import shutil

from concepts.stt.canonical import loads_strict
from concepts.stt.errors import STTError
from concepts.stt.host import HostAdapterError, InvocationReport, ProviderCapabilities, validated_invocation_report


class ClaudeCodeAdapter:
    provider_id = "claude-code"
    ROLE_MAP = {"planner": "stt-planner", "reviewer": "stt-reviewer", "worker": "stt-worker"}

    def discover_capabilities(self) -> ProviderCapabilities:
        available = shutil.which("claude") is not None
        return ProviderCapabilities(self.provider_id, available, tuple(self.ROLE_MAP), True, True, "claude-stream-json")

    def provider_role(self, canonical_role: str) -> str:
        try:
            return self.ROLE_MAP[canonical_role]
        except KeyError as exc:
            raise HostAdapterError("unknown canonical semantic role") from exc

    def validate_provider_evidence(self, raw: bytes) -> InvocationReport:
        if not isinstance(raw, bytes):
            raise HostAdapterError("Claude evidence must be bytes")
        events = []
        for line in raw.splitlines():
            try:
                item = loads_strict(line)
            except (STTError, TypeError, AttributeError) as exc:
                raise HostAdapterError("Claude evidence is not stream-json") from exc
            if not isinstance(item, dict):
                raise HostAdapterError("Claude evidence event must be an object")
            events.append(item)
        results = [item for item in events if item.get("type") == "result"]
        if len(results) != 1:
            raise HostAdapterError("Claude completion event missing or ambiguous")
        result = results[0]
        if type(result.get("is_error")) is not bool:
            raise HostAdapterError("Claude completion error flag invalid")
        return validated_invocation_report(
            provider_id=self.provider_id,
            invocation_id=result.get("session_id"),
            status="FAILED" if result["is_error"] else "COMPLETE",
            timed_out=False,
            exit_code=result.get("exit_status"),
            cost=result.get("total_cost_usd", "UNAVAILABLE"),
        )
