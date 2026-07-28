"""Small, deterministic validator for source-bound RunSkeptic receipts."""

from __future__ import annotations

import hashlib
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
SKEPTIC = ROOT / "skeptic.md"
REQUIRED_INVOCATION_FIELDS = (
    "INVOCATION_ID", "INVOCATION_KIND", "PERMISSION_MODE", "DONE",
    "TARGET_TASK_SHA256", "REVIEWED_ARTIFACT_REFERENCE",
    "REVIEWED_ARTIFACT_SHA256", "SKEPTIC_SOURCE_PATH", "SKEPTIC_SOURCE_REF",
    "SKEPTIC_SOURCE_BLOB_SHA", "APPLICABLE_COMPANION_SET_SHA256",
    "PREVIOUS_FINDINGS_REFERENCE", "MATERIAL_FINDINGS_SHA256",
)
REQUIRED_STEPS = ("GATE", "FUNDAMENTAL SCAN", "MAP", "CONFIDENCE", "STABILIZE",
                  "EVIDENCE", "DECIDE", "ACT", "VERIFY", "LEARN")
REQUIRED_THINKERS = ("CH", "OM", "FE", "PO", "KT", "SH")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: tuple[str, ...] = ()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _result(errors: list[str]) -> ValidationResult:
    return ValidationResult(not errors, tuple(errors))


def _required_hex(value: Any, name: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        errors.append(f"{name} must be a lowercase SHA-256")


def _git_blob_sha(data: bytes) -> str:
    payload = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    return hashlib.sha1(payload).hexdigest()


def _source_ref_matches(ref: Any, source_blob: str, root: Path, errors: list[str]) -> None:
    """Bind a receipt to the repository object named by its source ref."""
    if ref == "WORKTREE":
        return
    if not isinstance(ref, str) or not ref.strip():
        errors.append("SKEPTIC_SOURCE_REF must be a repository ref or WORKTREE")
        return
    try:
        resolved = subprocess.run(
            ["git", "-C", str(root), "rev-parse", f"{ref}:skeptic.md"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        errors.append("stale or unresolved Skeptic source ref")
        return
    if not HEX40.fullmatch(resolved) or resolved != source_blob:
        errors.append("Skeptic source ref does not resolve to current source blob")


def _reference_ok(value: Any, root: Path, errors: list[str], name: str) -> None:
    if not isinstance(value, Mapping):
        errors.append(f"{name} must contain path and sha256")
        return
    path_value, digest = value.get("path"), value.get("sha256")
    if not isinstance(path_value, str) or not isinstance(digest, str):
        errors.append(f"{name} must contain path and sha256")
        return
    path = (root / path_value).resolve()
    if root.resolve() not in path.parents and path != root.resolve():
        errors.append(f"{name} escapes repository root")
    elif not path.is_file():
        errors.append(f"{name} target is missing")
    elif _sha256(path) != digest:
        errors.append(f"{name} hash mismatch")


def validate_receipt(receipt: Mapping[str, Any], *, root: Path = ROOT) -> ValidationResult:
    """Validate one complete receipt against freshly read current source."""
    errors: list[str] = []
    missing = [field for field in REQUIRED_INVOCATION_FIELDS if field not in receipt]
    errors.extend(f"missing field: {field}" for field in missing)
    if missing:
        return _result(errors)

    if receipt["INVOCATION_KIND"] not in {"SINGLE", "FIND_LOOP", "FIX_LOOP"}:
        errors.append("invalid invocation kind")
    if receipt["PERMISSION_MODE"] not in {"read-only", "patch-local", "fix-if-valid"}:
        errors.append("invalid permission mode")
    if receipt["SKEPTIC_SOURCE_PATH"] != "skeptic.md":
        errors.append("only root skeptic.md is an authorized source")
    current_path = root / "skeptic.md"
    if not current_path.is_file():
        errors.append("current skeptic.md is unavailable")
    else:
        current_source = current_path.read_bytes()
        current_blob = _git_blob_sha(current_source)
        if receipt["SKEPTIC_SOURCE_BLOB_SHA"] != current_blob:
            errors.append("stale Skeptic source blob")
        _source_ref_matches(receipt["SKEPTIC_SOURCE_REF"], current_blob, root, errors)
        source_text = current_source.decode("utf-8")
        for step in REQUIRED_STEPS:
            if step not in source_text:
                errors.append(f"required recipe step absent: {step}")
        for thinker in REQUIRED_THINKERS:
            if not re.search(rf"\({thinker}\)", source_text):
                errors.append(f"required Thinker absent: {thinker}")
        if not all(category in source_text for category in ("PASS", "ACTION", "CONFLICT", "HANDLED")):
            errors.append("canonical categories are incomplete")

    for field in ("TARGET_TASK_SHA256", "REVIEWED_ARTIFACT_SHA256", "APPLICABLE_COMPANION_SET_SHA256", "MATERIAL_FINDINGS_SHA256"):
        _required_hex(receipt[field], field, errors)
    if not isinstance(receipt["SKEPTIC_SOURCE_BLOB_SHA"], str) or not HEX40.fullmatch(receipt["SKEPTIC_SOURCE_BLOB_SHA"]):
        errors.append("SKEPTIC_SOURCE_BLOB_SHA must be a Git blob SHA")
    _reference_ok(receipt["REVIEWED_ARTIFACT_REFERENCE"], root, errors, "artifact reference")
    artifact_reference = receipt["REVIEWED_ARTIFACT_REFERENCE"]
    if isinstance(artifact_reference, Mapping) and artifact_reference.get("sha256") != receipt["REVIEWED_ARTIFACT_SHA256"]:
        errors.append("reviewed artifact hash does not match its reference")

    steps = receipt.get("MAJOR_STEPS_RUN", ())
    if not isinstance(steps, (list, tuple)) or any(step not in steps for step in REQUIRED_STEPS):
        errors.append("complete recipe steps are not declared")
    thinkers = receipt.get("THINKERS_CONSIDERED", ())
    if not isinstance(thinkers, (list, tuple)) or any(thinker not in thinkers for thinker in REQUIRED_THINKERS):
        errors.append("required Thinkers are not declared")
    categories = receipt.get("FINDING_CATEGORIES")
    if not isinstance(categories, list) or not categories:
        errors.append("finding categories are not declared")
    if receipt.get("FINAL_OUTPUT_CATEGORY") not in {"HANDLED", "CONFLICT"}:
        errors.append("invalid final output category")
    if isinstance(categories, list) and any(category not in {"PASS", "ACTION", "CONFLICT"} for category in categories):
        errors.append("noncanonical finding category")
    if receipt.get("REVIEW_SCOPE") == "DELTA":
        errors.append("delta-only reviews cannot qualify")
    if receipt.get("INVOCATION_KIND") == "FIX_LOOP" and receipt.get("REPAIR_RUN"):
        errors.append("repair run cannot qualify")
    return _result(errors)


def validate_loop_state(state: Mapping[str, Any]) -> ValidationResult:
    errors: list[str] = []
    required = ("TARGET_TASK_SHA256", "REVIEWED_ARTIFACT_SHA256", "SKEPTIC_SOURCE_BLOB_SHA",
                "APPLICABLE_COMPANION_SET_SHA256", "MATERIAL_FINDINGS_SHA256", "INVOCATION_KIND", "PERMISSION_MODE",
                "QUALIFYING_PASSES_REQUIRED", "CONSECUTIVE_QUALIFYING_PASSES", "OPEN_ITEMS")
    errors.extend(f"missing loop field: {name}" for name in required if name not in state)
    for name in required[:2]:
        if name in state:
            _required_hex(state[name], name, errors)
    if "SKEPTIC_SOURCE_BLOB_SHA" in state and (
        not isinstance(state["SKEPTIC_SOURCE_BLOB_SHA"], str)
        or not HEX40.fullmatch(state["SKEPTIC_SOURCE_BLOB_SHA"])
    ):
        errors.append("loop Skeptic source must be a Git blob SHA")
    if "APPLICABLE_COMPANION_SET_SHA256" in state:
        _required_hex(state["APPLICABLE_COMPANION_SET_SHA256"], "APPLICABLE_COMPANION_SET_SHA256", errors)
    if "MATERIAL_FINDINGS_SHA256" in state:
        _required_hex(state["MATERIAL_FINDINGS_SHA256"], "MATERIAL_FINDINGS_SHA256", errors)
    if state.get("INVOCATION_KIND") != "FIX_LOOP":
        errors.append("loop state must be FIX_LOOP")
    if state.get("PERMISSION_MODE") not in {"read-only", "patch-local", "fix-if-valid"}:
        errors.append("invalid loop permission mode")
    if state.get("QUALIFYING_PASSES_REQUIRED") != 3:
        errors.append("default qualifying pass count must be three")
    if not isinstance(state.get("CONSECUTIVE_QUALIFYING_PASSES"), int) or state.get("CONSECUTIVE_QUALIFYING_PASSES", -1) < 0:
        errors.append("invalid qualifying pass count")
    if not isinstance(state.get("OPEN_ITEMS"), list):
        errors.append("OPEN_ITEMS must be a list")
    return _result(errors)


def advance_fix_loop(state: Mapping[str, Any], receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Return next external state; bindings change or repairs reset the streak."""
    result = validate_loop_state(state)
    if not result.ok:
        raise ValueError("invalid loop state: " + "; ".join(result.errors))
    binding_fields = ("TARGET_TASK_SHA256", "REVIEWED_ARTIFACT_SHA256", "SKEPTIC_SOURCE_BLOB_SHA",
                      "APPLICABLE_COMPANION_SET_SHA256", "MATERIAL_FINDINGS_SHA256",
                      "INVOCATION_KIND", "PERMISSION_MODE")
    changed = any(state[field] != receipt.get(field) for field in binding_fields)
    repair = bool(receipt.get("REPAIR_RUN")) or receipt.get("REVIEW_SCOPE") == "DELTA"
    qualifying = (
        not changed and not repair and receipt.get("INVOCATION_KIND") == "FIX_LOOP"
        and receipt.get("FINAL_OUTPUT_CATEGORY") == "HANDLED"
        and receipt.get("FINDING_CATEGORIES", []) == ["PASS"]
        and not receipt.get("OPEN_ITEMS")
    )
    next_state = dict(state)
    next_state["CONSECUTIVE_QUALIFYING_PASSES"] = (
        state["CONSECUTIVE_QUALIFYING_PASSES"] + 1 if qualifying else 0
    )
    next_state["OPEN_ITEMS"] = list(receipt.get("OPEN_ITEMS", state["OPEN_ITEMS"]))
    return next_state


def fix_loop_complete(state: Mapping[str, Any]) -> bool:
    """Whether validated external state has reached its required streak."""
    result = validate_loop_state(state)
    return result.ok and state["CONSECUTIVE_QUALIFYING_PASSES"] >= state["QUALIFYING_PASSES_REQUIRED"] and not state["OPEN_ITEMS"]
