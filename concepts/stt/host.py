from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol

from .errors import STTError

@dataclass(frozen=True, slots=True)
class ProviderCapabilities:
    provider_id: str
    available: bool
    semantic_roles: tuple[str, ...]
    durable_invocation_id: bool
    status_inspection: bool
    evidence_schema: str

@dataclass(frozen=True, slots=True)
class InvocationReport:
    provider_id: str
    invocation_id: str
    status: str
    timed_out: bool
    exit_code: int | None
    cost: str | float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class HostAdapter(Protocol):
    provider_id: str
    def discover_capabilities(self) -> ProviderCapabilities: ...
    def provider_role(self, canonical_role: str) -> str: ...
    def validate_provider_evidence(self, raw: bytes) -> InvocationReport: ...


class HostAdapterError(STTError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        STTError.__init__(self, "HOST_ADAPTER_ERROR", message, details)


def validated_invocation_report(
    *,
    provider_id: Any,
    invocation_id: Any,
    status: Any,
    timed_out: Any,
    exit_code: Any,
    cost: Any = "UNAVAILABLE",
) -> InvocationReport:
    if not isinstance(provider_id, str) or not provider_id:
        raise HostAdapterError("provider identity missing")
    if not isinstance(invocation_id, str) or not invocation_id.strip() or "\x00" in invocation_id:
        raise HostAdapterError("invocation identity invalid")
    try:
        invocation_bytes = invocation_id.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise HostAdapterError("invocation identity invalid") from exc
    if len(invocation_bytes) > 512:
        raise HostAdapterError("invocation identity invalid")
    if not isinstance(status, str) or status not in {"COMPLETE", "FAILED", "UNKNOWN"}:
        raise HostAdapterError("provider evidence status invalid")
    if type(timed_out) is not bool:
        raise HostAdapterError("provider timeout flag must be a boolean")
    if exit_code is not None and (type(exit_code) is not int or not -(2**31) <= exit_code < 2**31):
        raise HostAdapterError("provider exit code must be an integer or null")
    if status == "COMPLETE" and timed_out:
        raise HostAdapterError("complete provider evidence cannot be timed out")
    return InvocationReport(provider_id, invocation_id, status, timed_out, exit_code, cost)


def load_adapter(provider_id: str) -> HostAdapter:
    if provider_id == "generic-recorded-host":
        from adapters.generic_host import GenericHostAdapter
        return GenericHostAdapter()
    if provider_id == "claude-code":
        from adapters.claude_code import ClaudeCodeAdapter
        return ClaudeCodeAdapter()
    if provider_id == "codex":
        from adapters.codex import CodexAdapter
        return CodexAdapter()
    raise HostAdapterError(f"unsupported provider: {provider_id}")
