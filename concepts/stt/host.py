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
    cancellation_confirmation: bool
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
        super().__init__("HOST_ADAPTER_ERROR", message, details)


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
