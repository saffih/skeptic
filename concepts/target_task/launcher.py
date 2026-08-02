"""Host-owned Target Task invocation boundary.

The deterministic recorded host is executable in CI. Live providers may return
launch specifications elsewhere, but raw transcript text is never accepted as a
role result. Only a validated compact receipt crosses back into the controller.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Union

from adapters.generic_host import GenericHostAdapter
from concepts.target_task.host_adapter import persist_raw_provider_evidence
from concepts.target_task.routing import ResolvedRoute
from concepts.target_task.runtime import RuntimeAdapterError, validate_host_role_receipt, validate_host_role_request, validate_task_artifact_reference
from concepts.target_task.store import write_immutable_artifact


class LauncherError(ValueError):
    pass


RecordedHandler = Callable[[Mapping[str, Any]], Mapping[str, Union[str, bytes]]]


@dataclass(frozen=True)
class LaunchResult:
    receipt: dict[str, Any]
    raw_provider_evidence_ref: dict[str, Any]
    routing_evidence_ref: dict[str, Any]
    invocation_status: str


class HostLauncher(Protocol):
    def invoke(
        self,
        *,
        task_root: Path,
        source_root: Path,
        request_ref: Mapping[str, Any],
        dispatch_evidence_ref: Mapping[str, Any],
        route: ResolvedRoute,
    ) -> LaunchResult: ...


def _bytes(value: str | bytes, name: str) -> bytes:
    if isinstance(value, str):
        return value.encode("utf-8")
    if isinstance(value, bytes):
        return value
    raise LauncherError(f"{name} must be text or bytes")


def _json_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


class GenericRecordedLauncher:
    """Execute one deterministic handler and emit the production receipt shape."""

    def __init__(self, handler: RecordedHandler) -> None:
        self._handler = handler
        self._adapter = GenericHostAdapter()

    def _output_artifacts(
        self,
        *,
        request: Mapping[str, Any],
        output: Mapping[str, str | bytes],
        task_root: Path,
        route: ResolvedRoute,
        raw_ref: Mapping[str, Any],
        status: str,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        operation_id = request["operation_id"]
        role = request["role"]
        routing_payload = {
            "schema_version": "1",
            "task_id": request["task_id"],
            "operation_id": operation_id,
            "provider_id": route.provider_id,
            "canonical_role": route.canonical_role,
            "provider_role": route.provider_role,
            "requested_model_class": route.requested_model_class,
            "resolved_model": route.resolved_model,
            "effort": route.effort,
            "raw_provider_evidence_ref": raw_ref,
            "actual_provider_routing_proven": True,
        }
        routing_ref = write_immutable_artifact(
            task_root,
            f"evidence/{operation_id}-routing.json",
            _json_bytes(routing_payload),
            reference_id=f"routing-{operation_id}",
            artifact_type="routing_evidence",
            description="provider route and immutable raw-evidence binding",
            read_condition="read when validating actual host routing",
        )
        references: list[dict[str, Any]] = [routing_ref]
        if status != "COMPLETE":
            return references, routing_ref
        if role == "worker":
            if set(output) != {"step_result"}:
                raise LauncherError("complete worker handler must return only step_result")
            references.insert(0, write_immutable_artifact(
                task_root,
                f"results/{operation_id}.md",
                _bytes(output["step_result"], "step_result"),
                reference_id=f"step-result-{operation_id}",
                artifact_type="step_result",
                description="complete worker step result",
                read_condition="read when reviewing or validating this step",
            ))
        elif role == "command":
            if set(output) != {"command_receipt", "command_log"}:
                raise LauncherError("complete command handler must return command_receipt and command_log")
            references.insert(0, write_immutable_artifact(
                task_root,
                f"commands/{operation_id}-receipt.json",
                _bytes(output["command_receipt"], "command_receipt"),
                reference_id=f"command-receipt-{operation_id}",
                artifact_type="command_receipt",
                description="deterministic command result receipt",
                read_condition="read when validating the command step",
            ))
            references.insert(1, write_immutable_artifact(
                task_root,
                f"commands/{operation_id}.log",
                _bytes(output["command_log"], "command_log"),
                reference_id=f"command-log-{operation_id}",
                artifact_type="command_log",
                description="complete deterministic command output",
                read_condition="read only when diagnosing or reviewing this command",
            ))
        else:
            raise LauncherError("recorded launcher supports worker and command execution only")
        return references, routing_ref

    def invoke(
        self,
        *,
        task_root: Path,
        source_root: Path,
        request_ref: Mapping[str, Any],
        dispatch_evidence_ref: Mapping[str, Any],
        route: ResolvedRoute,
    ) -> LaunchResult:
        if route.status != "RESOLVED" or route.provider_id != self._adapter.provider_id:
            raise LauncherError("generic launcher requires a resolved generic-recorded-host route")
        validated_dispatch_ref = validate_task_artifact_reference(
            dispatch_evidence_ref, task_root, "$.dispatch_evidence_ref"
        )
        if validated_dispatch_ref["artifact_type"] != "dispatch_evidence":
            raise LauncherError("dispatch evidence type")
        try:
            dispatch_value = json.loads(
                (Path(task_root) / validated_dispatch_ref["repository_relative_path"]).read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise LauncherError("dispatch evidence JSON") from exc
        exact_request_ref = dispatch_value.get("request_ref") if isinstance(dispatch_value, Mapping) else None
        if not isinstance(exact_request_ref, Mapping):
            raise LauncherError("dispatch evidence request reference")
        if exact_request_ref.get("repository_relative_path") != request_ref.get("repository_relative_path"):
            raise LauncherError("prepared request and dispatch evidence disagree")
        request_ref = dict(exact_request_ref)
        # validate_host_role_request requires exact expected identities. Read the
        # canonical request first, then validate it with those identities.
        raw_request = (Path(task_root) / request_ref["repository_relative_path"]).read_bytes()
        try:
            request_value = json.loads(raw_request.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise LauncherError("request JSON") from exc
        request = validate_host_role_request(
            request_ref,
            task_root=task_root,
            source_root=source_root,
            expected_task_id=request_value.get("task_id"),
            expected_operation_id=request_value.get("operation_id"),
            expected_attempt=request_value.get("attempt"),
            expected_role=request_value.get("role"),
            expected_step_id=request_value.get("step_id"),
        )
        status = "COMPLETE"
        timed_out = False
        exit_status: int | None = 0
        output: Mapping[str, str | bytes] = {}
        summary = "recorded host completed"
        try:
            output = self._handler(request)
            if not isinstance(output, Mapping):
                raise LauncherError("recorded handler must return a mapping")
        except TimeoutError:
            status, timed_out, exit_status, summary = "UNKNOWN", True, None, "recorded host timed out"
            output = {}
        except LauncherError:
            raise
        except Exception:
            status, exit_status, summary = "FAILED", 1, "recorded host failed"
            output = {}
        raw_evidence = _json_bytes({
            "provider_id": self._adapter.provider_id,
            "invocation_id": f"generic-{request['operation_id']}",
            "status": status,
            "timed_out": timed_out,
            "exit_code": exit_status,
        })
        raw_ref = persist_raw_provider_evidence(task_root, self._adapter.provider_id, raw_evidence)
        report = self._adapter.validate_provider_evidence(raw_evidence)
        if report.status != status or report.timed_out != timed_out or report.exit_code != exit_status:
            raise LauncherError("provider evidence normalization mismatch")
        output_refs, routing_ref = self._output_artifacts(
            request=request,
            output=output,
            task_root=task_root,
            route=route,
            raw_ref=raw_ref,
            status=status,
        )
        manifest = {
            "schema_version": "1",
            "task_id": request["task_id"],
            "operation_id": request["operation_id"],
            "attempt": request["attempt"],
            "role": request["role"],
            "step_id": request["step_id"],
            "status": status,
            "output_references": output_refs,
        }
        result_ref = write_immutable_artifact(
            task_root,
            request["result_relative_path"],
            _json_bytes(manifest),
            reference_id=f"manifest-{request['operation_id']}",
            artifact_type="role_result_manifest",
            description="bounded recorded-host role result manifest",
            read_condition="read when accepting this exact operation outcome",
        )
        receipt = {
            "schema_version": "1",
            "task_id": request["task_id"],
            "operation_id": request["operation_id"],
            "attempt": request["attempt"],
            "role": request["role"],
            "step_id": request["step_id"],
            "status": status,
            "summary": summary,
            "request_ref": dict(request_ref),
            "result_ref": result_ref,
            "dispatch_evidence_ref": dict(dispatch_evidence_ref),
            "synthetic": False,
        }
        try:
            normalized = validate_host_role_receipt(
                receipt,
                workspace_root=task_root,
                source_root=source_root,
                expected_task_id=request["task_id"],
                expected_operation_id=request["operation_id"],
                expected_attempt=request["attempt"],
                expected_role=request["role"],
                expected_step_id=request["step_id"],
                expected_request_ref=request_ref,
            )
        except RuntimeAdapterError as exc:
            raise LauncherError(str(exc)) from exc
        compact_receipt = {key: normalized[key] for key in receipt}
        return LaunchResult(compact_receipt, raw_ref, routing_ref, status)


__all__ = ["GenericRecordedLauncher", "HostLauncher", "LaunchResult", "LauncherError"]
