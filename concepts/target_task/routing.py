"""Provider-neutral Target Task route resolution.

Core selects canonical roles and model classes. Provider adapters own concrete
role names and model aliases. Resolution is descriptive until raw provider
evidence is persisted; it never proves that a provider or model actually ran.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from adapters.claude_code import ClaudeCodeAdapter
from adapters.codex import CodexAdapter
from adapters.generic_host import GenericHostAdapter
from concepts.stt.errors import STTError as ActiveSTTError
from concepts.target_task.host_adapter import CANONICAL_ROLES, HostAdapterError, TargetTaskHostAdapter


class RoutingError(ValueError):
    pass


MODEL_CLASSES = {"small", "medium", "strongest"}
EFFORTS = {"low", "medium", "high"}
ROUTE_STATUSES = {"RESOLVED", "RELAUNCH_REQUIRED", "PROVIDER_UNAVAILABLE", "MODEL_UNRESOLVED"}


@dataclass(frozen=True)
class ResolvedRoute:
    status: str
    provider_id: str
    canonical_role: str
    provider_role: str | None
    requested_model_class: str
    resolved_model: str | None
    effort: str
    timeout_seconds: int
    budget: int | float | None
    launch_mode: str | None
    evidence_mode: str | None
    blocker: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


ADAPTER_TYPES = {
    "generic-recorded-host": GenericHostAdapter,
    "claude-code": ClaudeCodeAdapter,
    "codex": CodexAdapter,
}

LEGACY_MODEL_ALIASES = {
    "generic-recorded-host": {"small": "recorded-small", "medium": "recorded-medium", "strongest": "recorded-strongest"},
    "claude-code": {"small": "haiku", "medium": "sonnet", "strongest": "opus"},
    "codex": {"small": None, "medium": None, "strongest": None},
}

LEGACY_COMMAND_ROLES = {
    "generic-recorded-host": "command",
    "claude-code": "stt-command",
    "codex": "stt-command",
}


def adapter_for(provider_id: str) -> Any:
    try:
        return ADAPTER_TYPES[provider_id]()
    except KeyError as exc:
        raise RoutingError(f"unknown provider: {provider_id}") from exc


def _profile(profile: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(profile, Mapping):
        raise RoutingError("routing profile object required")
    expected = {"provider", "model_class", "effort", "timeout_seconds", "budget"}
    if set(profile) != expected:
        raise RoutingError("routing profile fields")
    provider = profile["provider"]
    if not isinstance(provider, str) or not provider or len(provider.encode("utf-8")) > 64:
        raise RoutingError("provider preference")
    model_class = profile["model_class"]
    effort = profile["effort"]
    timeout = profile["timeout_seconds"]
    budget = profile["budget"]
    if model_class not in MODEL_CLASSES:
        raise RoutingError("model class")
    if effort not in EFFORTS:
        raise RoutingError("effort")
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 86400:
        raise RoutingError("timeout")
    if budget is not None and (
        not isinstance(budget, (int, float)) or isinstance(budget, bool) or budget < 0 or budget > 100000
    ):
        raise RoutingError("budget")
    return dict(profile)


def _provider_id(preference: str, current_provider: str | None) -> str:
    if preference != "current":
        return preference
    if not current_provider:
        raise RoutingError("current provider is unresolved")
    return current_provider


def _provider_role(adapter: Any, role: str) -> str:
    if role == "lead":
        return "lead"
    if role == "command":
        value = LEGACY_COMMAND_ROLES.get(adapter.provider_id)
        if value is None:
            raise RoutingError("provider has no Command role")
        return value
    if role not in CANONICAL_ROLES:
        raise RoutingError("unknown canonical role")
    try:
        return adapter.provider_role(role)
    except (HostAdapterError, ActiveSTTError) as exc:
        raise RoutingError(str(exc)) from exc


def resolve_route(
    canonical_role: str,
    profile: Mapping[str, Any],
    *,
    current_provider: str | None = None,
    allow_relaunch: bool = False,
) -> ResolvedRoute:
    normalized = _profile(profile)
    provider_id = _provider_id(normalized["provider"], current_provider)
    adapter = adapter_for(provider_id)
    capabilities = adapter.discover_capabilities()
    evidence_mode = getattr(capabilities, "evidence_schema", getattr(capabilities, "evidence_mode", None))
    supports_execution = getattr(capabilities, "durable_invocation_id", getattr(capabilities, "supports_execution", False))
    try:
        provider_role = _provider_role(adapter, canonical_role)
    except RoutingError as exc:
        if canonical_role == "lead" and allow_relaunch:
            return ResolvedRoute(
                status="RELAUNCH_REQUIRED", provider_id=provider_id,
                canonical_role="lead", provider_role=None,
                requested_model_class=normalized["model_class"], resolved_model=None,
                effort=normalized["effort"], timeout_seconds=normalized["timeout_seconds"],
                budget=normalized["budget"], launch_mode=None,
                evidence_mode=evidence_mode, blocker=str(exc),
            )
        raise
    aliases = LEGACY_MODEL_ALIASES.get(provider_id, getattr(adapter, "MODEL_ALIASES", {}))
    model = aliases.get(normalized["model_class"]) if isinstance(aliases, Mapping) else None
    launch_mode = getattr(adapter, "LAUNCH_MODE", evidence_mode)
    if not capabilities.available or not supports_execution:
        status = "RELAUNCH_REQUIRED" if canonical_role == "lead" and allow_relaunch else "PROVIDER_UNAVAILABLE"
        route = ResolvedRoute(
            status=status, provider_id=provider_id, canonical_role=canonical_role,
            provider_role=provider_role, requested_model_class=normalized["model_class"],
            resolved_model=model, effort=normalized["effort"],
            timeout_seconds=normalized["timeout_seconds"], budget=normalized["budget"],
            launch_mode=launch_mode, evidence_mode=evidence_mode,
            blocker="provider execution is unavailable in the current host",
        )
        if status == "PROVIDER_UNAVAILABLE":
            raise RoutingError(route.blocker)
        return route
    if not isinstance(model, str) or not model:
        status = "RELAUNCH_REQUIRED" if canonical_role == "lead" and allow_relaunch else "MODEL_UNRESOLVED"
        route = ResolvedRoute(
            status=status, provider_id=provider_id, canonical_role=canonical_role,
            provider_role=provider_role, requested_model_class=normalized["model_class"],
            resolved_model=None, effort=normalized["effort"],
            timeout_seconds=normalized["timeout_seconds"], budget=normalized["budget"],
            launch_mode=launch_mode, evidence_mode=evidence_mode,
            blocker="provider model alias is not configured",
        )
        if status == "MODEL_UNRESOLVED":
            raise RoutingError(route.blocker)
        return route
    return ResolvedRoute(
        status="RESOLVED", provider_id=provider_id, canonical_role=canonical_role,
        provider_role=provider_role, requested_model_class=normalized["model_class"],
        resolved_model=model, effort=normalized["effort"],
        timeout_seconds=normalized["timeout_seconds"], budget=normalized["budget"],
        launch_mode=launch_mode, evidence_mode=evidence_mode,
    )


def resolve_lead_route(profile: Mapping[str, Any], *, current_provider: str | None = None) -> ResolvedRoute:
    return resolve_route("lead", profile, current_provider=current_provider, allow_relaunch=True)


__all__ = [
    "ResolvedRoute", "RoutingError", "adapter_for", "resolve_lead_route", "resolve_route",
]
