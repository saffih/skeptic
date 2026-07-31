"""Executable companion for an immutable Target Task sealed Plan.

The existing sealed Plan remains the lifecycle identity.  This companion binds
that Plan hash to mechanically dispatchable step recipes without placing task
bodies in the Plan, ledger, cursor, or Lead receipt.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from concepts.target_task.contracts import ContractError, SAFE_ID_RE, SHA256_RE, validate_plan_dict, validate_task_id
from concepts.target_task.runtime import HOST_ARTIFACT_REFERENCE_FIELDS, validate_task_artifact_reference
from concepts.target_task.store import StoreError, write_immutable_artifact


class ExecutablePlanError(ValueError):
    pass


EXECUTION_MANIFEST_FIELDS = {
    "schema_version", "task_id", "sealed_plan_sha256", "steps",
}
EXECUTION_STEP_FIELDS = {
    "step_id", "objective", "role", "instruction_ref",
    "task_artifact_references", "source_artifact_references",
    "retrieval_recipe_ref", "output_contract_ref", "routing_profile",
    "scope", "authority", "prohibitions", "validation_commands",
    "success_criteria", "result_manifest_directory",
}
ROUTING_PROFILE_FIELDS = {
    "provider", "model_class", "effort", "timeout_seconds", "budget",
}
PLAN_ROLES = {"worker", "command"}
MODEL_CLASSES = {"small", "medium", "strongest"}
EFFORTS = {"low", "medium", "high"}
AUTHORITIES = {"read-only", "write-source", "command-only"}
MAX_EXECUTION_MANIFEST_BYTES = 131072


def _short(value: Any, path: str, maximum: int = 1024) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > maximum:
        raise ExecutablePlanError(f"bounded string required at {path}")
    return value


def _safe_id(value: Any, path: str) -> str:
    value = _short(value, path, 128)
    if not SAFE_ID_RE.fullmatch(value):
        raise ExecutablePlanError(f"safe ID required at {path}")
    return value


def _safe_relative(value: Any, path: str) -> str:
    value = _short(value, path, 512)
    if value.startswith("/") or "\\" in value or any(part in {"", ".", ".."} for part in value.split("/")):
        raise ExecutablePlanError(f"safe relative path required at {path}")
    return value


def _string_list(value: Any, path: str, *, minimum: int = 0, maximum: int = 64) -> list[str]:
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise ExecutablePlanError(f"bounded list required at {path}")
    return [_short(item, f"{path}/{index}", 1024) for index, item in enumerate(value)]


def _reference_shape(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != HOST_ARTIFACT_REFERENCE_FIELDS:
        raise ExecutablePlanError(f"artifact reference fields at {path}")
    result = dict(value)
    _short(result["reference_id"], f"{path}/reference_id", 64)
    _safe_relative(result["repository_relative_path"], f"{path}/repository_relative_path")
    digest = result["sha256"]
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        raise ExecutablePlanError(f"SHA-256 required at {path}/sha256")
    if not isinstance(result["byte_size"], int) or isinstance(result["byte_size"], bool) or result["byte_size"] < 0:
        raise ExecutablePlanError(f"byte size required at {path}/byte_size")
    for field in ("artifact_type", "description", "read_condition"):
        _short(result[field], f"{path}/{field}", 256)
    return result


def _reference_list(value: Any, path: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > 64:
        raise ExecutablePlanError(f"bounded reference list required at {path}")
    result = [_reference_shape(item, f"{path}/{index}") for index, item in enumerate(value)]
    identities = [(item["reference_id"], item["repository_relative_path"]) for item in result]
    if len(set(identities)) != len(identities):
        raise ExecutablePlanError(f"duplicate artifact reference at {path}")
    if len({item["reference_id"] for item in result}) != len(result):
        raise ExecutablePlanError(f"duplicate reference ID at {path}")
    if len({item["repository_relative_path"] for item in result}) != len(result):
        raise ExecutablePlanError(f"duplicate reference path at {path}")
    return result


def _routing_profile(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != ROUTING_PROFILE_FIELDS:
        raise ExecutablePlanError(f"routing profile fields at {path}")
    provider = _short(value["provider"], f"{path}/provider", 64)
    model_class = value["model_class"]
    effort = value["effort"]
    if model_class not in MODEL_CLASSES:
        raise ExecutablePlanError(f"model class at {path}/model_class")
    if effort not in EFFORTS:
        raise ExecutablePlanError(f"effort at {path}/effort")
    timeout = value["timeout_seconds"]
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 86400:
        raise ExecutablePlanError(f"timeout at {path}/timeout_seconds")
    budget = value["budget"]
    if budget is not None and (
        not isinstance(budget, (int, float)) or isinstance(budget, bool) or budget < 0 or budget > 100000
    ):
        raise ExecutablePlanError(f"budget at {path}/budget")
    return {
        "provider": provider,
        "model_class": model_class,
        "effort": effort,
        "timeout_seconds": timeout,
        "budget": budget,
    }


def validate_execution_manifest(value: Mapping[str, Any], *, sealed_plan: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != EXECUTION_MANIFEST_FIELDS:
        raise ExecutablePlanError("execution manifest fields")
    if value["schema_version"] != "1":
        raise ExecutablePlanError("execution manifest schema")
    try:
        task_id = validate_task_id(value["task_id"])
    except ContractError as exc:
        raise ExecutablePlanError("execution manifest task ID") from exc
    digest = value["sealed_plan_sha256"]
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        raise ExecutablePlanError("sealed Plan SHA-256")
    steps = value["steps"]
    if not isinstance(steps, list) or not steps or len(steps) > 128:
        raise ExecutablePlanError("execution steps")
    normalized_steps: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, step in enumerate(steps):
        path = f"$.steps/{index}"
        if not isinstance(step, Mapping) or set(step) != EXECUTION_STEP_FIELDS:
            raise ExecutablePlanError(f"execution step fields at {path}")
        step_id = _safe_id(step["step_id"], f"{path}/step_id")
        if step_id in seen:
            raise ExecutablePlanError(f"duplicate step ID at {path}")
        seen.add(step_id)
        role = step["role"]
        if role not in PLAN_ROLES:
            raise ExecutablePlanError(f"role at {path}/role")
        authority = step["authority"]
        if authority not in AUTHORITIES:
            raise ExecutablePlanError(f"authority at {path}/authority")
        if role == "command" and authority != "command-only":
            raise ExecutablePlanError(f"command authority at {path}/authority")
        if role == "worker" and authority not in {"read-only", "write-source"}:
            raise ExecutablePlanError(f"worker authority at {path}/authority")
        instruction_ref = _reference_shape(step["instruction_ref"], f"{path}/instruction_ref")
        output_contract_ref = _reference_shape(step["output_contract_ref"], f"{path}/output_contract_ref")
        retrieval_ref = None
        if step["retrieval_recipe_ref"] is not None:
            retrieval_ref = _reference_shape(step["retrieval_recipe_ref"], f"{path}/retrieval_recipe_ref")
            if retrieval_ref["artifact_type"] != "retrieval_recipe":
                raise ExecutablePlanError(f"retrieval recipe type at {path}/retrieval_recipe_ref")
        task_refs = _reference_list(step["task_artifact_references"], f"{path}/task_artifact_references")
        source_refs = _reference_list(step["source_artifact_references"], f"{path}/source_artifact_references")
        all_task_refs = [instruction_ref, output_contract_ref, *task_refs]
        if retrieval_ref is not None:
            all_task_refs.append(retrieval_ref)
        if len({item["reference_id"] for item in all_task_refs}) != len(all_task_refs):
            raise ExecutablePlanError(f"duplicate task-root reference ID at {path}")
        if len({item["repository_relative_path"] for item in all_task_refs}) != len(all_task_refs):
            raise ExecutablePlanError(f"duplicate task-root reference path at {path}")
        result_directory = _safe_relative(step["result_manifest_directory"], f"{path}/result_manifest_directory")
        if result_directory != "results/manifests":
            raise ExecutablePlanError(f"result manifests must use results/manifests at {path}")
        normalized_steps.append({
            "step_id": step_id,
            "objective": _short(step["objective"], f"{path}/objective", 2048),
            "role": role,
            "instruction_ref": instruction_ref,
            "task_artifact_references": task_refs,
            "source_artifact_references": source_refs,
            "retrieval_recipe_ref": retrieval_ref,
            "output_contract_ref": output_contract_ref,
            "routing_profile": _routing_profile(step["routing_profile"], f"{path}/routing_profile"),
            "scope": _short(step["scope"], f"{path}/scope", 1024),
            "authority": authority,
            "prohibitions": _string_list(step["prohibitions"], f"{path}/prohibitions", maximum=64),
            "validation_commands": _string_list(step["validation_commands"], f"{path}/validation_commands", maximum=32),
            "success_criteria": _string_list(step["success_criteria"], f"{path}/success_criteria", minimum=1, maximum=32),
            "result_manifest_directory": result_directory,
        })
    normalized = {
        "schema_version": "1",
        "task_id": task_id,
        "sealed_plan_sha256": digest,
        "steps": normalized_steps,
    }
    if sealed_plan is not None:
        try:
            plan = validate_plan_dict(sealed_plan)
        except ContractError as exc:
            raise ExecutablePlanError("sealed Plan invalid") from exc
        if plan["task_id"] != task_id:
            raise ExecutablePlanError("execution manifest task binding")
        plan_steps = plan["steps"]
        if len(plan_steps) != len(normalized_steps):
            raise ExecutablePlanError("execution manifest step count binding")
        for plan_step, execution_step in zip(plan_steps, normalized_steps):
            for field in ("step_id", "objective", "role", "success_criteria"):
                if plan_step[field] != execution_step[field]:
                    raise ExecutablePlanError(f"execution manifest Plan binding: {field}")
    return normalized


def canonical_execution_manifest_bytes(value: Mapping[str, Any], *, sealed_plan: Mapping[str, Any] | None = None) -> bytes:
    normalized = validate_execution_manifest(value, sealed_plan=sealed_plan)
    raw = (json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(raw) > MAX_EXECUTION_MANIFEST_BYTES:
        raise ExecutablePlanError("execution manifest too large")
    return raw


def execution_manifest_relative_path(sealed_plan_sha256: str) -> str:
    if not isinstance(sealed_plan_sha256, str) or not SHA256_RE.fullmatch(sealed_plan_sha256):
        raise ExecutablePlanError("sealed Plan SHA-256")
    return f"plans/execution/{sealed_plan_sha256}.json"


def persist_execution_manifest(
    task_root: Path,
    sealed_plan_reference: Mapping[str, Any],
    sealed_plan: Mapping[str, Any],
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    plan_ref = validate_task_artifact_reference(sealed_plan_reference, task_root, "$.sealed_plan_reference")
    if plan_ref["artifact_type"] != "sealed_plan":
        raise ExecutablePlanError("sealed Plan artifact type")
    normalized = validate_execution_manifest(manifest, sealed_plan=sealed_plan)
    if normalized["sealed_plan_sha256"] != plan_ref["sha256"]:
        raise ExecutablePlanError("execution manifest sealed Plan binding")
    raw = canonical_execution_manifest_bytes(normalized, sealed_plan=sealed_plan)
    relative = execution_manifest_relative_path(plan_ref["sha256"])
    target = Path(task_root) / relative
    if target.exists():
        if target.is_symlink() or target.read_bytes() != raw:
            raise ExecutablePlanError("execution manifest already exists with different content")
        return {
            "reference_id": "execution-manifest",
            "repository_relative_path": relative,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "byte_size": len(raw),
            "artifact_type": "execution_manifest",
            "description": "mechanically executable sealed-Plan companion",
            "read_condition": "read by Boundary/controller when preparing the current step",
        }
    try:
        return write_immutable_artifact(
            task_root,
            relative,
            raw,
            reference_id="execution-manifest",
            artifact_type="execution_manifest",
            description="mechanically executable sealed-Plan companion",
            read_condition="read by Boundary/controller when preparing the current step",
        )
    except StoreError as exc:
        raise ExecutablePlanError(f"could not persist execution manifest: {exc.code}") from exc


def load_execution_manifest(
    task_root: Path,
    sealed_plan_reference: Mapping[str, Any],
    sealed_plan: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    plan_ref = validate_task_artifact_reference(sealed_plan_reference, task_root, "$.sealed_plan_reference")
    if plan_ref["artifact_type"] != "sealed_plan":
        raise ExecutablePlanError("sealed Plan artifact type")
    relative = execution_manifest_relative_path(plan_ref["sha256"])
    target = Path(task_root) / relative
    if not target.is_file() or target.is_symlink():
        raise ExecutablePlanError("executable Plan companion missing")
    raw = target.read_bytes()
    if len(raw) > MAX_EXECUTION_MANIFEST_BYTES:
        raise ExecutablePlanError("execution manifest too large")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ExecutablePlanError("execution manifest JSON") from exc
    normalized = validate_execution_manifest(value, sealed_plan=sealed_plan)
    if canonical_execution_manifest_bytes(normalized, sealed_plan=sealed_plan) != raw:
        raise ExecutablePlanError("execution manifest noncanonical")
    if normalized["sealed_plan_sha256"] != plan_ref["sha256"]:
        raise ExecutablePlanError("execution manifest sealed Plan binding")
    reference = {
        "reference_id": "execution-manifest",
        "repository_relative_path": relative,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
        "artifact_type": "execution_manifest",
        "description": "mechanically executable sealed-Plan companion",
        "read_condition": "read by Boundary/controller when preparing the current step",
    }
    return reference, normalized


def validate_step_references(step: Mapping[str, Any], *, task_root: Path, source_root: Path) -> dict[str, Any]:
    normalized = dict(step)
    task_refs = [normalized["instruction_ref"], normalized["output_contract_ref"], *normalized["task_artifact_references"]]
    if normalized["retrieval_recipe_ref"] is not None:
        task_refs.append(normalized["retrieval_recipe_ref"])
    validated_task = [validate_task_artifact_reference(ref, task_root, "$.task_ref") for ref in task_refs]
    validated_source = [validate_task_artifact_reference(ref, source_root, "$.source_ref") for ref in normalized["source_artifact_references"]]
    if normalized["instruction_ref"]["artifact_type"] != "step_instruction":
        raise ExecutablePlanError("instruction reference type")
    if normalized["output_contract_ref"]["artifact_type"] != "output_contract":
        raise ExecutablePlanError("output contract reference type")
    normalized["resolved_task_artifact_references"] = validated_task
    normalized["resolved_source_artifact_references"] = validated_source
    return normalized


__all__ = [
    "ExecutablePlanError", "canonical_execution_manifest_bytes",
    "execution_manifest_relative_path", "load_execution_manifest",
    "persist_execution_manifest", "validate_execution_manifest",
    "validate_step_references",
]
