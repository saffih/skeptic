from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol

from .errors import STTError

from dataclasses import dataclass

@dataclass(frozen=True)
class DispatchRequest:
    task_id: str
    operation_id: str
    attempt: int
    canonical_role: str
    provider_role: str
    request_ref: Any


@dataclass(frozen=True, slots=True)
class ProviderCapabilities:
    provider_id: str
    available: bool
    semantic_roles: tuple[str, ...]
    durable_invocation_id: bool
    status_inspection: bool
    cancellation_confirmation: bool
    evidence_schema: str

    @property
    def roles(self) -> tuple[str, ...]:
        return self.semantic_roles
    @property
    def supports_execution(self) -> bool:
        return self.available
    @property
    def evidence_mode(self) -> str:
        return self.evidence_schema


@dataclass(frozen=True, slots=True)
class InvocationReport:
    provider_id: str
    invocation_id: str
    status: str
    timed_out: bool
    exit_code: int | None
    cost: str | float

    @property
    def completion_status(self) -> str:
        return self.status
    @property
    def timeout(self) -> bool:
        return self.timed_out
    @property
    def exit_status(self) -> int | None:
        return self.exit_code

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class HostAdapter(Protocol):
    provider_id: str
    def discover_capabilities(self) -> ProviderCapabilities: ...
    def provider_role(self, canonical_role: str) -> str: ...
    def validate_provider_evidence(self, raw: bytes) -> InvocationReport: ...


try:
    from concepts.target_task.host_adapter import HostAdapterError as _LegacyHostAdapterError
except ImportError:  # pragma: no cover
    _LegacyHostAdapterError = ValueError


class HostAdapterError(_LegacyHostAdapterError, STTError):
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
