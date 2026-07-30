"""Small, deterministic validator for source-bound RunSkeptic receipts."""

from __future__ import annotations

import hashlib
import json
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
REQUIRED_STEPS = (
    "GATE", "FUNDAMENTAL SCAN", "MAP", "CONFIDENCE", "STABILIZE",
    "EVIDENCE", "DECIDE", "ACT", "VERIFY", "LEARN",
)
REQUIRED_THINKERS = ("CH", "OM", "FE", "PO", "KT", "SH")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")

MAX_RECEIPT_BYTES = 16384
MAX_SHORT_BYTES = 1024
ALLOWED_RECEIPT_FIELDS = set(REQUIRED_INVOCATION_FIELDS) | {
    "MAJOR_STEPS_RUN", "THINKERS_CONSIDERED", "FINDING_CATEGORIES",
    "FINAL_OUTPUT_CATEGORY", "OPEN_ITEMS", "REVIEW_SCOPE", "REPAIR_RUN",
    "EVIDENCE_USED", "DECISION_PATH", "VERIFICATION_PERFORMED",
    "UNRESOLVED_CONFLICTS", "COMPANION_FILES_READ",
}


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: tuple[str, ...] = ()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _short(value: Any, name: str, errors: list[str], maximum: int = MAX_SHORT_BYTES) -> None:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > maximum:
        errors.append(f"{name} must be a non-empty bounded string")


def _string_list(value: Any, name: str, errors: list[str], *, maximum_items: int = 64) -> None:
    if not isinstance(value, list) or len(value) > maximum_items:
        errors.append(f"{name} must be a bounded list")
        return
    for index, item in enumerate(value):
        _short(item, f"{name}/{index}", errors)


def _result(errors: list[str]) -> ValidationResult:
    return ValidationResult(not errors, tuple(errors))


def _required_hex(value: Any, name: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        errors.append(f"{name} must be a lowercase SHA-256")


def _git_blob_sha(data: bytes) -> str:
    payload = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    return hashlib.sha1(payload).hexdigest()


def _source_ref_matches(ref: Any, source_blob: str, root: Path, errors: list[str]) -> None:
    if ref == "WORKTREE":
        return
    if not isinstance(ref, str) or not ref.strip():
        errors.append("SKEPTIC_SOURCE_REF must be a repository ref or WORKTREE")
        return
    try:
        resolved = subprocess.run(
            ["git", "-C", str(root), "rev-parse", f"{ref}:skeptic.md"],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        errors.append("stale or unresolved Skeptic source ref")
        return
    if not HEX40.fullmatch(resolved) or resolved != source_blob:
        errors.append("Skeptic source ref does not resolve to current source blob")


def _reference_ok(value: Any, root: Path, errors: list[str], name: str) -> None:
    if not isinstance(value, Mapping) or set(value) != {"path", "sha256"}:
        errors.append(f"{name} must contain exactly path and sha256")
        return
    path_value, digest = value.get("path"), value.get("sha256")
    if not isinstance(path_value, str) or not isinstance(digest, str):
        errors.append(f"{name} must contain path and sha256")
        return
    if Path(path_value).is_absolute() or "\\" in path_value or any(part in {"", ".", ".."} for part in path_value.split("/")):
        errors.append(f"{name} has an unsafe path")
        return
    current = root.resolve()
    for part in path_value.split("/"):
        current = current / part
        if current.is_symlink():
            errors.append(f"{name} crosses a symlink")
            return
    path = current
    if root.resolve() not in path.parents and path != root.resolve():
        errors.append(f"{name} escapes artifact root")
    elif not path.is_file():
        errors.append(f"{name} target is missing")
    elif _sha256(path) != digest:
        errors.append(f"{name} hash mismatch")


def validate_receipt(
    receipt: Mapping[str, Any],
    *,
    root: Path = ROOT,
    artifact_root: Path | None = None,
) -> ValidationResult:
    """Validate one receipt against current `root/skeptic.md` and its artifact root.

    `artifact_root` defaults to `root` for existing callers. Target Task uses the
    source repository for Skeptic identity and the external task root for the
    reviewed Plan/candidate artifact.
    """
    errors: list[str] = []
    root = Path(root).resolve()
    reviewed_root = Path(artifact_root or root).resolve()
    if not isinstance(receipt, Mapping):
        return _result(["receipt must be an object"])
    extra = sorted(set(receipt) - ALLOWED_RECEIPT_FIELDS)
    if extra:
        errors.append("unexpected receipt fields: " + ", ".join(extra))
    try:
        receipt_raw = (json.dumps(dict(receipt), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    except (TypeError, ValueError):
        return _result(errors + ["receipt is not canonical-JSON serializable"])
    if len(receipt_raw) > MAX_RECEIPT_BYTES:
        errors.append("receipt exceeds compact size limit")
    missing = [field for field in REQUIRED_INVOCATION_FIELDS if field not in receipt]
    errors.extend(f"missing field: {field}" for field in missing)
    if missing:
        return _result(errors)

    for field in ("INVOCATION_ID", "DONE", "SKEPTIC_SOURCE_PATH", "SKEPTIC_SOURCE_REF"):
        _short(receipt[field], field, errors)
    previous = receipt["PREVIOUS_FINDINGS_REFERENCE"]
    if isinstance(previous, str):
        if previous != "NONE":
            errors.append("PREVIOUS_FINDINGS_REFERENCE string must be NONE")
    elif isinstance(previous, Mapping):
        _reference_ok(previous, reviewed_root, errors, "previous findings reference")
    else:
        errors.append("PREVIOUS_FINDINGS_REFERENCE must be NONE or an artifact reference")

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
        try:
            source_text = current_source.decode("utf-8")
        except UnicodeDecodeError:
            errors.append("current skeptic.md is not UTF-8")
            source_text = ""
        for step in REQUIRED_STEPS:
            if step not in source_text:
                errors.append(f"required recipe step absent: {step}")
        for thinker in REQUIRED_THINKERS:
            if not re.search(rf"\({thinker}\)", source_text):
                errors.append(f"required Thinker absent: {thinker}")
        if not all(category in source_text for category in ("PASS", "ACTION", "CONFLICT", "HANDLED")):
            errors.append("canonical categories are incomplete")

    for field in (
        "TARGET_TASK_SHA256", "REVIEWED_ARTIFACT_SHA256",
        "APPLICABLE_COMPANION_SET_SHA256", "MATERIAL_FINDINGS_SHA256",
    ):
        _required_hex(receipt[field], field, errors)
    if not isinstance(receipt["SKEPTIC_SOURCE_BLOB_SHA"], str) or not HEX40.fullmatch(receipt["SKEPTIC_SOURCE_BLOB_SHA"]):
        errors.append("SKEPTIC_SOURCE_BLOB_SHA must be a Git blob SHA")
    _reference_ok(receipt["REVIEWED_ARTIFACT_REFERENCE"], reviewed_root, errors, "artifact reference")
    artifact_reference = receipt["REVIEWED_ARTIFACT_REFERENCE"]
    if isinstance(artifact_reference, Mapping) and artifact_reference.get("sha256") != receipt["REVIEWED_ARTIFACT_SHA256"]:
        errors.append("reviewed artifact hash does not match its reference")

    steps = receipt.get("MAJOR_STEPS_RUN", ())
    if not isinstance(steps, list) or len(steps) > 32 or any(step not in steps for step in REQUIRED_STEPS):
        errors.append("complete recipe steps are not declared")
    thinkers = receipt.get("THINKERS_CONSIDERED", ())
    if not isinstance(thinkers, list) or len(thinkers) > 16 or any(thinker not in thinkers for thinker in REQUIRED_THINKERS):
        errors.append("required Thinkers are not declared")
    categories = receipt.get("FINDING_CATEGORIES")
    if not isinstance(categories, list) or not categories:
        errors.append("finding categories are not declared")
    if receipt.get("FINAL_OUTPUT_CATEGORY") not in {"HANDLED", "CONFLICT"}:
        errors.append("invalid final output category")
    if isinstance(categories, list) and any(category not in {"PASS", "ACTION", "CONFLICT"} for category in categories):
        errors.append("noncanonical finding category")
    if "OPEN_ITEMS" in receipt:
        _string_list(receipt["OPEN_ITEMS"], "OPEN_ITEMS", errors)
    for field in ("EVIDENCE_USED", "VERIFICATION_PERFORMED", "UNRESOLVED_CONFLICTS", "COMPANION_FILES_READ"):
        if field in receipt:
            _string_list(receipt[field], field, errors)
    if "DECISION_PATH" in receipt:
        _short(receipt["DECISION_PATH"], "DECISION_PATH", errors, maximum=2048)
    if "REVIEW_SCOPE" in receipt and receipt["REVIEW_SCOPE"] not in {"COMPLETE", "DELTA"}:
        errors.append("invalid REVIEW_SCOPE")
    if "REPAIR_RUN" in receipt and not isinstance(receipt["REPAIR_RUN"], bool):
        errors.append("REPAIR_RUN must be boolean")
    return _result(errors)


def validate_loop_state(state: Mapping[str, Any]) -> ValidationResult:
    errors: list[str] = []
    required = (
        "TARGET_TASK_SHA256", "REVIEWED_ARTIFACT_SHA256", "SKEPTIC_SOURCE_BLOB_SHA",
        "APPLICABLE_COMPANION_SET_SHA256", "MATERIAL_FINDINGS_SHA256", "INVOCATION_KIND",
        "PERMISSION_MODE", "QUALIFYING_PASSES_REQUIRED", "CONSECUTIVE_QUALIFYING_PASSES", "OPEN_ITEMS",
    )
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
    if not isinstance(state.get("CONSECUTIVE_QUALIFYING_PASSES"), int) or isinstance(state.get("CONSECUTIVE_QUALIFYING_PASSES"), bool) or state.get("CONSECUTIVE_QUALIFYING_PASSES", -1) < 0:
        errors.append("invalid qualifying pass count")
    if not isinstance(state.get("OPEN_ITEMS"), list):
        errors.append("OPEN_ITEMS must be a list")
    return _result(errors)


def advance_fix_loop(state: Mapping[str, Any], receipt: Mapping[str, Any]) -> dict[str, Any]:
    result = validate_loop_state(state)
    if not result.ok:
        raise ValueError("invalid loop state: " + "; ".join(result.errors))
    binding_fields = (
        "TARGET_TASK_SHA256", "REVIEWED_ARTIFACT_SHA256", "SKEPTIC_SOURCE_BLOB_SHA",
        "APPLICABLE_COMPANION_SET_SHA256", "MATERIAL_FINDINGS_SHA256", "INVOCATION_KIND", "PERMISSION_MODE",
    )
    changed = any(state[field] != receipt.get(field) for field in binding_fields)
    repair = bool(receipt.get("REPAIR_RUN")) or receipt.get("REVIEW_SCOPE") == "DELTA"
    qualifying = (
        not changed
        and not repair
        and receipt.get("INVOCATION_KIND") == "FIX_LOOP"
        and receipt.get("FINAL_OUTPUT_CATEGORY") == "HANDLED"
        and receipt.get("FINDING_CATEGORIES", []) == ["PASS"]
        and not receipt.get("OPEN_ITEMS")
    )
    next_state = dict(state)
    next_state["CONSECUTIVE_QUALIFYING_PASSES"] = (
        state["CONSECUTIVE_QUALIFYING_PASSES"] + 1 if qualifying else 0
    )
    if changed:
        for field in binding_fields:
            next_state[field] = receipt.get(field)
    next_state["OPEN_ITEMS"] = list(receipt.get("OPEN_ITEMS", state["OPEN_ITEMS"]))
    return next_state


def fix_loop_complete(state: Mapping[str, Any]) -> bool:
    result = validate_loop_state(state)
    return (
        result.ok
        and state["CONSECUTIVE_QUALIFYING_PASSES"] >= state["QUALIFYING_PASSES_REQUIRED"]
        and not state["OPEN_ITEMS"]
    )
