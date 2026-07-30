"""Bounded Target Task role adapters and production host-receipt validation."""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from capabilities.execution_envelope.execution_envelope import (
    ExecutionEnvelopeError,
    validate_role_return,
    validate_task_envelope,
)
from concepts.target_task.contracts import validate_task_id
from concepts.target_task.store import (
    StoreError,
    write_content_addressed_artifact,
    write_immutable_artifact,
)


class RuntimeAdapterError(ValueError):
    pass


@dataclass(frozen=True)
class SpecialistOutcome:
    body: str
    status: str
    summary: str
    findings: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    next_authorized_action: str = "NONE"


SpecialistExecutor = Callable[[Mapping[str, Any]], SpecialistOutcome]


def dispatch_specialist(
    task_envelope: Mapping[str, Any],
    executor: SpecialistExecutor,
    *,
    role: str,
    workspace_root: Path,
    output_relative_path: str,
    output_reference_id: str,
    repository_root: Path | str = ".",
) -> dict[str, Any]:
    """Deterministic recorded-host helper; provider adapters use the protocol below."""
    try:
        validated_task = validate_task_envelope(task_envelope, repository_root=repository_root)
    except ExecutionEnvelopeError as exc:
        raise RuntimeAdapterError(f"invalid task envelope: {exc.code} at {exc.path}") from exc
    outcome = executor(validated_task)
    if not isinstance(outcome, SpecialistOutcome):
        raise RuntimeAdapterError("executor must return a SpecialistOutcome")
    try:
        produced_ref = write_immutable_artifact(
            Path(workspace_root),
            output_relative_path,
            outcome.body.encode("utf-8"),
            reference_id=output_reference_id,
            artifact_type="specialist_result",
            description=f"{role} result for {validated_task['task_id']}",
            read_condition="read when validating this dispatch outcome",
        )
    except StoreError as exc:
        raise RuntimeAdapterError(f"could not capture specialist output: {exc.code} at {exc.path}") from exc
    role_return = {
        "role": role,
        "status": outcome.status,
        "summary": outcome.summary,
        "produced_artifact_references": [produced_ref],
        "findings": list(outcome.findings),
        "blockers": list(outcome.blockers),
        "next_authorized_action": outcome.next_authorized_action,
    }
    try:
        return validate_role_return(role_return, repository_root=workspace_root)
    except ExecutionEnvelopeError as exc:
        raise RuntimeAdapterError(f"invalid role return: {exc.code} at {exc.path}") from exc


HOST_ARTIFACT_REFERENCE_FIELDS = {
    "reference_id",
    "repository_relative_path",
    "sha256",
    "byte_size",
    "artifact_type",
    "description",
    "read_condition",
}
HOST_REQUEST_FIELDS = {
    "schema_version",
    "task_id",
    "operation_id",
    "attempt",
    "role",
    "step_id",
    "objective",
    "scope",
    "authority",
    "prohibitions",
    "success_criteria",
    "task_artifact_references",
    "source_artifact_references",
    "result_relative_path",
}
MAX_HOST_REQUEST_BYTES = 32768
HOST_AUTHORITIES = {"read-only", "write-source", "command-only"}

HOST_RECEIPT_FIELDS = {
    "schema_version",
    "task_id",
    "operation_id",
    "attempt",
    "role",
    "step_id",
    "status",
    "summary",
    "request_ref",
    "result_ref",
    "dispatch_evidence_ref",
    "synthetic",
}
DISPATCH_EVIDENCE_FIELDS = {
    "schema_version",
    "task_id",
    "operation_id",
    "attempt",
    "role",
    "step_id",
    "request_ref",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
HOST_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
MAX_HOST_RECEIPT_BYTES = 4096
MAX_HOST_SUMMARY_BYTES = 512
HOST_STATUSES = {"COMPLETE", "FAILED", "UNKNOWN"}
HOST_ROLES = {"planner", "reviewer", "worker", "command"}
REQUEST_ARTIFACT_TYPES = {"role_request", "plan_request", "review_request", "step_request"}
RESULT_ARTIFACT_TYPES = {"role_result_manifest"}
ROLE_RESULT_MANIFEST_FIELDS = {
    "schema_version", "task_id", "operation_id", "attempt", "role", "step_id",
    "status", "output_references",
}
ROLE_OUTPUT_ARTIFACT_TYPES = {
    "planner": {"plan_version", "finding_map", "routing_evidence"},
    "reviewer": {"review_body", "material_findings", "runskeptic_receipt", "routing_evidence"},
    "worker": {"step_result", "routing_evidence"},
    "command": {"command_receipt", "command_log", "routing_evidence"},
}
ROLE_OUTPUT_PREFIXES = {
    "planner": ("plans/versions/", "results/", "evidence/"),
    "reviewer": ("reviews/", "findings/", "evidence/"),
    "worker": ("results/", "evidence/"),
    "command": ("commands/", "evidence/"),
}
ROLE_OUTPUT_PREFIX_BY_TYPE = {
    "plan_version": "plans/versions/", "finding_map": "findings/", "routing_evidence": "evidence/",
    "review_body": "reviews/", "material_findings": "findings/", "runskeptic_receipt": "receipts/",
    "step_result": "results/", "command_receipt": "commands/", "command_log": "commands/",
}


def _short(value: Any, name: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > maximum:
        raise RuntimeAdapterError(f"invalid {name}")
    return value


def _safe_file(workspace_root: Path, relative: str, path: str) -> Path:
    if not isinstance(relative, str) or not relative or relative.startswith("/") or "\\" in relative:
        raise RuntimeAdapterError(f"unsafe artifact path at {path}")
    parts = relative.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise RuntimeAdapterError(f"unsafe artifact path at {path}")
    supplied = Path(workspace_root).expanduser()
    if supplied.is_symlink():
        raise RuntimeAdapterError("invalid workspace root")
    try:
        root = supplied.resolve(strict=True)
    except OSError as exc:
        raise RuntimeAdapterError("invalid workspace root") from exc
    if not root.is_dir():
        raise RuntimeAdapterError("invalid workspace root")
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise RuntimeAdapterError(f"symlink artifact path at {path}")
    if not current.is_file():
        raise RuntimeAdapterError(f"unresolvable artifact at {path}")
    return current


def validate_task_artifact_reference(reference: Any, workspace_root: Path, path: str = "$.artifact_ref") -> dict[str, Any]:
    if not isinstance(reference, Mapping) or set(reference) != HOST_ARTIFACT_REFERENCE_FIELDS:
        raise RuntimeAdapterError(f"invalid artifact reference fields at {path}")
    normalized = dict(reference)
    _short(normalized["reference_id"], f"{path}.reference_id", 64)
    target = _safe_file(workspace_root, normalized["repository_relative_path"], path)
    if not isinstance(normalized["sha256"], str) or not SHA256_RE.fullmatch(normalized["sha256"]):
        raise RuntimeAdapterError(f"invalid artifact hash at {path}")
    if not isinstance(normalized["byte_size"], int) or isinstance(normalized["byte_size"], bool) or normalized["byte_size"] < 0:
        raise RuntimeAdapterError(f"invalid artifact size at {path}")
    for key in ("artifact_type", "description", "read_condition"):
        _short(normalized[key], f"{path}.{key}")
    data = target.read_bytes()
    if hashlib.sha256(data).hexdigest() != normalized["sha256"] or len(data) != normalized["byte_size"]:
        raise RuntimeAdapterError(f"artifact identity mismatch at {path}")
    return normalized


def _parse_dispatch_evidence(raw: bytes) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeAdapterError("dispatch evidence is not UTF-8") from exc
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise RuntimeAdapterError("dispatch evidence encoding")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise RuntimeAdapterError("dispatch evidence duplicate key")
            result[key] = value
        return result

    try:
        value = json.loads(text, object_pairs_hook=pairs)
    except RuntimeAdapterError:
        raise
    except json.JSONDecodeError as exc:
        raise RuntimeAdapterError("dispatch evidence JSON") from exc
    if not isinstance(value, dict) or set(value) != DISPATCH_EVIDENCE_FIELDS:
        raise RuntimeAdapterError("dispatch evidence fields")
    canonical = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if canonical != raw:
        raise RuntimeAdapterError("dispatch evidence noncanonical")
    return value


def _canonical_json_object(raw: bytes, *, limit: int, label: str) -> dict[str, Any]:
    if len(raw) > limit:
        raise RuntimeAdapterError(f"{label} too large")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeAdapterError(f"{label} is not UTF-8") from exc
    if not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise RuntimeAdapterError(f"{label} encoding")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise RuntimeAdapterError(f"{label} duplicate key")
            result[key] = value
        return result

    try:
        value = json.loads(text, object_pairs_hook=pairs)
    except RuntimeAdapterError:
        raise
    except json.JSONDecodeError as exc:
        raise RuntimeAdapterError(f"{label} JSON") from exc
    if not isinstance(value, dict):
        raise RuntimeAdapterError(f"{label} object required")
    canonical = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if canonical != raw:
        raise RuntimeAdapterError(f"{label} noncanonical")
    return value


def _safe_relative_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value.startswith("/") or "\\" in value:
        raise RuntimeAdapterError(f"invalid {label}")
    if any(part in {"", ".", ".."} for part in value.split("/")):
        raise RuntimeAdapterError(f"invalid {label}")
    return value


def _validate_reference_list(references: Any, root: Path, path: str) -> list[dict[str, Any]]:
    if not isinstance(references, list) or len(references) > 64:
        raise RuntimeAdapterError(f"invalid reference list at {path}")
    normalized: list[dict[str, Any]] = []
    ids: set[str] = set()
    paths: set[str] = set()
    for index, reference in enumerate(references):
        item = validate_task_artifact_reference(reference, root, f"{path}/{index}")
        if item["reference_id"] in ids or item["repository_relative_path"] in paths:
            raise RuntimeAdapterError(f"duplicate artifact reference at {path}/{index}")
        ids.add(item["reference_id"]); paths.add(item["repository_relative_path"])
        normalized.append(item)
    return normalized


def _validate_host_request_payload(
    request: Mapping[str, Any],
    *,
    task_root: Path,
    source_root: Path,
    expected_task_id: str,
    expected_operation_id: str,
    expected_attempt: int,
    expected_role: str,
    expected_step_id: str,
    require_result_absent: bool = False,
) -> dict[str, Any]:
    if not isinstance(request, Mapping) or set(request) != HOST_REQUEST_FIELDS or request.get("schema_version") != "1":
        raise RuntimeAdapterError("host request fields")
    try:
        validate_task_id(expected_task_id)
    except Exception as exc:
        raise RuntimeAdapterError("invalid task_id") from exc
    for label, identifier in (("operation_id", expected_operation_id), ("step_id", expected_step_id)):
        if not isinstance(identifier, str) or not HOST_ID_RE.fullmatch(identifier):
            raise RuntimeAdapterError(f"invalid {label}")
    if not isinstance(expected_attempt, int) or isinstance(expected_attempt, bool) or expected_attempt < 1:
        raise RuntimeAdapterError("invalid attempt")
    expected = {
        "task_id": expected_task_id, "operation_id": expected_operation_id,
        "attempt": expected_attempt, "role": expected_role, "step_id": expected_step_id,
    }
    for key, value in expected.items():
        if request.get(key) != value:
            raise RuntimeAdapterError(f"host request {key} mismatch")
    if expected_role not in HOST_ROLES or request["authority"] not in HOST_AUTHORITIES:
        raise RuntimeAdapterError("host request role/authority")
    if expected_role in {"planner", "skeptic", "reviewer"} and request["authority"] != "read-only":
        raise RuntimeAdapterError("review roles require read-only source authority")
    if expected_role == "command" and request["authority"] != "command-only":
        raise RuntimeAdapterError("command role requires command-only authority")
    if expected_role == "worker" and request["authority"] not in {"read-only", "write-source"}:
        raise RuntimeAdapterError("worker authority mismatch")
    _short(request["objective"], "objective", 2048)
    _short(request["scope"], "scope", 1024)
    for field in ("prohibitions", "success_criteria"):
        values = request[field]
        if not isinstance(values, list) or len(values) > 64:
            raise RuntimeAdapterError(f"invalid {field}")
        for index, value in enumerate(values):
            _short(value, f"{field}/{index}", 1024)
    normalized_task = _validate_reference_list(request["task_artifact_references"], task_root, "$.task_artifact_references")
    normalized_source = _validate_reference_list(request["source_artifact_references"], source_root, "$.source_artifact_references")
    result_relative_path = _safe_relative_string(request["result_relative_path"], "result_relative_path")
    if not result_relative_path.startswith("results/manifests/"):
        raise RuntimeAdapterError("result manifest path must be under results/manifests")
    supplied_root = Path(task_root).expanduser()
    if supplied_root.is_symlink():
        raise RuntimeAdapterError("invalid task root")
    root = supplied_root.resolve()
    target = root.joinpath(*result_relative_path.split("/"))
    current = root
    for part in result_relative_path.split("/")[:-1]:
        current = current / part
        if current.exists() and current.is_symlink():
            raise RuntimeAdapterError("result manifest path crosses a symlink")
    if require_result_absent and target.exists():
        raise RuntimeAdapterError("result manifest path already exists")
    return {
        **dict(request),
        "task_artifact_references": normalized_task,
        "source_artifact_references": normalized_source,
        "result_relative_path": result_relative_path,
    }


def _validate_result_manifest(
    result_ref: Mapping[str, Any],
    *,
    task_root: Path,
    expected: Mapping[str, Any],
    expected_status: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if result_ref["artifact_type"] != "role_result_manifest":
        raise RuntimeAdapterError("result artifact type mismatch")
    raw = (Path(task_root) / result_ref["repository_relative_path"]).read_bytes()
    manifest = _canonical_json_object(raw, limit=32768, label="role result manifest")
    if set(manifest) != ROLE_RESULT_MANIFEST_FIELDS or manifest.get("schema_version") != "1":
        raise RuntimeAdapterError("role result manifest fields")
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise RuntimeAdapterError(f"role result manifest {key} mismatch")
    if manifest.get("status") != expected_status:
        raise RuntimeAdapterError("role result manifest status mismatch")
    outputs = _validate_reference_list(manifest.get("output_references"), task_root, "$.output_references")
    allowed_types = ROLE_OUTPUT_ARTIFACT_TYPES[expected["role"]]
    allowed_types = ROLE_OUTPUT_ARTIFACT_TYPES[expected["role"]]
    required_types = set(allowed_types)
    observed_types: set[str] = set()
    for index, output in enumerate(outputs):
        if output["repository_relative_path"] == result_ref["repository_relative_path"]:
            raise RuntimeAdapterError(f"role result manifest cannot reference itself at $.output_references/{index}")
        output_type = output["artifact_type"]
        if output_type not in allowed_types or output_type in observed_types:
            raise RuntimeAdapterError(f"role output artifact type mismatch at $.output_references/{index}")
        observed_types.add(output_type)
        if not output["repository_relative_path"].startswith(ROLE_OUTPUT_PREFIX_BY_TYPE[output_type]):
            raise RuntimeAdapterError(f"role output path mismatch at $.output_references/{index}")
    if expected_status == "COMPLETE" and observed_types != required_types:
        raise RuntimeAdapterError("complete role result requires the unique minimum role outputs")
    return manifest, outputs


def prepare_host_role_dispatch(
    request: Mapping[str, Any],
    *,
    task_root: Path,
    source_root: Path,
) -> dict[str, Any]:
    """Validate and persist one content-addressed request plus dispatch evidence."""
    normalized = _validate_host_request_payload(
        request, task_root=task_root, source_root=source_root,
        expected_task_id=request.get("task_id"), expected_operation_id=request.get("operation_id"),
        expected_attempt=request.get("attempt"), expected_role=request.get("role"),
        expected_step_id=request.get("step_id"), require_result_absent=True,
    )
    raw = (json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(raw) > MAX_HOST_REQUEST_BYTES:
        raise RuntimeAdapterError("host request too large")
    request_ref = write_content_addressed_artifact(
        Path(task_root), "requests", ".json", raw, reference_id=f"request-{normalized['operation_id']}",
        artifact_type="role_request", description=f"immutable {normalized['role']} request",
        read_condition="read only for this admitted role dispatch",
    )
    evidence = {
        "schema_version": "1", "task_id": normalized["task_id"],
        "operation_id": normalized["operation_id"], "attempt": normalized["attempt"],
        "role": normalized["role"], "step_id": normalized["step_id"], "request_ref": request_ref,
    }
    evidence_raw = (json.dumps(evidence, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    evidence_ref = write_content_addressed_artifact(
        Path(task_root), "dispatch", ".json", evidence_raw,
        reference_id=f"dispatch-{normalized['operation_id']}", artifact_type="dispatch_evidence",
        description="immutable host dispatch binding", read_condition="read when validating the role return",
    )
    return {"request_ref": request_ref, "dispatch_evidence_ref": evidence_ref, "request": normalized}


def validate_host_role_request(
    request_ref: Mapping[str, Any],
    *,
    task_root: Path,
    source_root: Path,
    expected_task_id: str,
    expected_operation_id: str,
    expected_attempt: int,
    expected_role: str,
    expected_step_id: str,
) -> dict[str, Any]:
    validated_ref = validate_task_artifact_reference(request_ref, task_root, "$.request_ref")
    if validated_ref["artifact_type"] != "role_request":
        raise RuntimeAdapterError("request artifact type mismatch")
    raw = (Path(task_root) / validated_ref["repository_relative_path"]).read_bytes()
    request = _canonical_json_object(raw, limit=MAX_HOST_REQUEST_BYTES, label="host request")
    normalized = _validate_host_request_payload(
        request, task_root=task_root, source_root=source_root,
        expected_task_id=expected_task_id, expected_operation_id=expected_operation_id,
        expected_attempt=expected_attempt, expected_role=expected_role, expected_step_id=expected_step_id,
    )
    return {**normalized, "request_ref": validated_ref}


def validate_host_role_receipt(
    receipt: Mapping[str, Any],
    *,
    workspace_root: Path,
    source_root: Path,
    expected_task_id: str,
    expected_operation_id: str,
    expected_attempt: int,
    expected_role: str,
    expected_step_id: str,
    expected_request_ref: Mapping[str, Any],
    allow_test_synthetic: bool = False,
) -> dict[str, Any]:
    """Validate one host return against the exact admitted dispatch.

    Production always leaves `allow_test_synthetic=False`. Validation happens
    before any cursor or ledger transition.
    """
    if not isinstance(receipt, Mapping) or set(receipt) != HOST_RECEIPT_FIELDS:
        raise RuntimeAdapterError("host receipt fields mismatch")
    raw = json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(raw) > MAX_HOST_RECEIPT_BYTES:
        raise RuntimeAdapterError("host receipt too large")
    if receipt["schema_version"] != "1":
        raise RuntimeAdapterError("invalid schema_version")
    for field in ("task_id", "operation_id", "role", "step_id", "summary"):
        _short(receipt[field], field, MAX_HOST_SUMMARY_BYTES if field == "summary" else 256)
    if receipt["status"] not in HOST_STATUSES:
        raise RuntimeAdapterError("invalid status")
    if receipt["role"] not in HOST_ROLES:
        raise RuntimeAdapterError("invalid role")
    if not isinstance(receipt["attempt"], int) or isinstance(receipt["attempt"], bool) or receipt["attempt"] < 1:
        raise RuntimeAdapterError("invalid attempt")
    if not isinstance(receipt["synthetic"], bool):
        raise RuntimeAdapterError("synthetic must be boolean")
    if receipt["synthetic"] and not allow_test_synthetic:
        raise RuntimeAdapterError("synthetic receipt rejected in production")

    expected_request = validate_task_artifact_reference(expected_request_ref, workspace_root, "$.expected_request_ref")
    request = validate_host_role_request(
        receipt["request_ref"],
        task_root=workspace_root,
        source_root=source_root,
        expected_task_id=expected_task_id,
        expected_operation_id=expected_operation_id,
        expected_attempt=expected_attempt,
        expected_role=expected_role,
        expected_step_id=expected_step_id,
    )
    request_ref = request["request_ref"]
    result_ref = validate_task_artifact_reference(receipt["result_ref"], workspace_root, "$.result_ref")
    if expected_request["artifact_type"] != "role_request" or request_ref != expected_request:
        raise RuntimeAdapterError("host receipt request identity mismatch")
    if result_ref["repository_relative_path"] != request["result_relative_path"]:
        raise RuntimeAdapterError("result path does not match admitted request")

    expected = {
        "task_id": expected_task_id,
        "operation_id": expected_operation_id,
        "attempt": expected_attempt,
        "role": expected_role,
        "step_id": expected_step_id,
    }
    for key, value in expected.items():
        if receipt[key] != value:
            raise RuntimeAdapterError(f"host receipt {key} mismatch")
    manifest, output_references = _validate_result_manifest(
        result_ref, task_root=workspace_root, expected=expected, expected_status=receipt["status"]
    )
    evidence_ref_raw = receipt["dispatch_evidence_ref"]
    if receipt["synthetic"]:
        if evidence_ref_raw is not None:
            validate_task_artifact_reference(evidence_ref_raw, workspace_root, "$.dispatch_evidence_ref")
    else:
        evidence_ref = validate_task_artifact_reference(evidence_ref_raw, workspace_root, "$.dispatch_evidence_ref")
        if evidence_ref["artifact_type"] != "dispatch_evidence":
            raise RuntimeAdapterError("dispatch evidence artifact type mismatch")
        evidence_path = _safe_file(workspace_root, evidence_ref["repository_relative_path"], "$.dispatch_evidence_ref")
        evidence = _parse_dispatch_evidence(evidence_path.read_bytes())
        expected_evidence = {"schema_version": "1", **expected, "request_ref": expected_request}
        if evidence != expected_evidence:
            raise RuntimeAdapterError("dispatch evidence binding mismatch")
    return {
        **dict(receipt),
        "request_ref": request_ref,
        "result_ref": result_ref,
        "result_manifest": manifest,
        "output_references": output_references,
    }


def persist_validated_host_receipt(
    receipt: Mapping[str, Any],
    *,
    workspace_root: Path,
    source_root: Path,
    expected_task_id: str,
    expected_operation_id: str,
    expected_attempt: int,
    expected_role: str,
    expected_step_id: str,
    expected_request_ref: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate first, then persist the compact receipt by content identity."""
    validated = validate_host_role_receipt(
        receipt, workspace_root=workspace_root, source_root=source_root,
        expected_task_id=expected_task_id, expected_operation_id=expected_operation_id,
        expected_attempt=expected_attempt, expected_role=expected_role,
        expected_step_id=expected_step_id, expected_request_ref=expected_request_ref,
    )
    stored = {key: validated[key] for key in HOST_RECEIPT_FIELDS}
    raw = (json.dumps(stored, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    return write_content_addressed_artifact(
        Path(workspace_root), "receipts", ".json", raw,
        reference_id=f"receipt-{expected_operation_id}", artifact_type="host_receipt",
        description="validated compact host role receipt",
        read_condition="read on restart or deterministic role acceptance",
    )
