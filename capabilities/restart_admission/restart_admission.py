"""Validated, non-executing admission from one immutable Body checkpoint."""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from capabilities.body_state.body_state import MAX_ID_BYTES, MAX_PATH_BYTES, MAX_STATE_BYTES, BodyStateError, SHA256_RE, validate_state_bytes, validate_state_structure_bytes
from capabilities.immutable_checkpoint.immutable_checkpoint import CHECKPOINT_MAX_BYTES, CheckpointError, validate_checkpoint_bytes

REQUEST_MAX_BYTES = 8192
RECEIPT_MAX_BYTES = 4096
MAX_SHORT_BYTES = 256
REQUEST_FIELDS = {"REQUEST_ID", "TASK_ID", "CHECKPOINT_ID", "CHECKPOINT_PATH", "CHECKPOINT_SHA256", "CHECKPOINT_BYTE_SIZE", "EXPECTED_SEALED_PLAN_REFERENCE", "EXPECTED_SEALED_PLAN_SHA256", "RESUMED_BODY_STATE_PATH"}
READY_FIELDS = {"REQUEST_ID", "STATUS", "TASK_ID", "CHECKPOINT_ID", "CHECKPOINT_PATH", "CHECKPOINT_SHA256", "CHECKPOINT_BYTE_SIZE", "SEALED_PLAN_REFERENCE", "SEALED_PLAN_SHA256", "CURRENT_STEP", "COMPLETED_STEP_COUNT", "VALIDATION_STATUS", "NEXT_AUTHORIZED_ACTION", "RESUMED_BODY_STATE_PATH", "RESUMED_BODY_STATE_SHA256", "RESUMED_BODY_STATE_BYTE_SIZE", "SUMMARY"}
BLOCKED_FIELDS = READY_FIELDS - {"NEXT_AUTHORIZED_ACTION"} | {"OPEN_BLOCKER_COUNT"}
_HEX = re.compile(r"^[0-9a-f]{64}$")


class ResumeError(ValueError):
    def __init__(self, code: str, phase: str = "BEFORE_PUBLICATION", *, output_visible: bool = False, final_bytes_verified: bool = False):
        self.code = code
        self.phase = phase
        self.output_visible = output_visible
        self.final_bytes_verified = final_bytes_verified
        super().__init__(f"{code} ({phase})")


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _parse(raw: bytes, maximum: int) -> Any:
    if len(raw) > maximum:
        raise ResumeError("REQUEST_TOO_LARGE" if maximum == REQUEST_MAX_BYTES else "RECEIPT_TOO_LARGE")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ResumeError("UTF8") from exc
    if text.startswith("\ufeff") or not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise ResumeError("NONCANONICAL")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ResumeError("DUPLICATE_KEY")
            result[key] = value
        return result

    try:
        value = json.loads(text, object_pairs_hook=pairs)
    except ResumeError:
        raise
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ResumeError("JSON") from exc
    if _canonical(value) != raw:
        raise ResumeError("NONCANONICAL")
    return value


def _short(value: Any, *, ids: bool = False) -> str:
    limit = MAX_ID_BYTES if ids else MAX_SHORT_BYTES
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > limit:
        raise ResumeError("INVALID_STRING")
    return value


def _safe_relative(value: Any) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > MAX_PATH_BYTES or Path(value).is_absolute() or "\\" in value or any(part in {"", ".", ".."} for part in value.split("/")):
        raise ResumeError("UNSAFE_PATH")
    return value


def _root(value: Path | str, code: str) -> Path:
    try:
        root = Path(value).resolve(strict=True)
    except OSError as exc:
        raise ResumeError(code) from exc
    if not root.is_dir():
        raise ResumeError(code)
    return root


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _path(root: Path, relative: str, *, file: bool = False) -> Path:
    current = root
    parts = relative.split("/")
    for part in parts[:-1] if not file else parts:
        current = current / part
        try:
            if current.is_symlink():
                raise ResumeError("SYMLINK_PATH")
        except OSError as exc:
            raise ResumeError("PATH_IO") from exc
    target = root.joinpath(*parts)
    if file:
        try:
            if target.is_symlink() or not target.is_file():
                raise ResumeError("CHECKPOINT_INVALID")
        except OSError as exc:
            raise ResumeError("PATH_IO") from exc
    return target


def _request(raw: bytes) -> dict[str, Any]:
    value = _parse(raw, REQUEST_MAX_BYTES)
    if not isinstance(value, dict) or set(value) != REQUEST_FIELDS:
        raise ResumeError("REQUEST_FIELDS")
    for key in ("REQUEST_ID", "TASK_ID", "CHECKPOINT_ID"):
        _short(value[key], ids=True)
    _safe_relative(value["CHECKPOINT_PATH"]); _safe_relative(value["RESUMED_BODY_STATE_PATH"])
    if value["CHECKPOINT_PATH"] == value["RESUMED_BODY_STATE_PATH"]:
        raise ResumeError("PATHS_MUST_DIFFER")
    for key in ("CHECKPOINT_SHA256", "EXPECTED_SEALED_PLAN_SHA256"):
        if not isinstance(value[key], str) or not _HEX.fullmatch(value[key]):
            raise ResumeError("INVALID_HASH")
    if not isinstance(value["CHECKPOINT_BYTE_SIZE"], int) or isinstance(value["CHECKPOINT_BYTE_SIZE"], bool) or value["CHECKPOINT_BYTE_SIZE"] < 0 or value["CHECKPOINT_BYTE_SIZE"] > CHECKPOINT_MAX_BYTES:
        raise ResumeError("INVALID_BYTE_SIZE")
    _short(value["EXPECTED_SEALED_PLAN_REFERENCE"])
    return value


def _validate_roots(request: dict[str, Any], repository_root: Path | str, workspace_root: Path | str) -> tuple[Path, Path, Path, Path]:
    repo = _root(repository_root, "REPOSITORY_INVALID")
    workspace = _root(workspace_root, "RUNTIME_WORKSPACE_INVALID")
    if _inside(workspace, repo):
        raise ResumeError("RUNTIME_WORKSPACE_IN_REPOSITORY")
    checkpoint = _path(workspace, request["CHECKPOINT_PATH"], file=True)
    output = _path(workspace, request["RESUMED_BODY_STATE_PATH"])
    try:
        checkpoint_real = checkpoint.resolve(strict=True)
        output_parent = output.parent.resolve(strict=True)
    except OSError as exc:
        raise ResumeError("OUTPUT_PARENT_INVALID") from exc
    if _inside(checkpoint_real, repo) or _inside(output_parent, repo):
        raise ResumeError("PATH_INSIDE_REPOSITORY")
    if output.exists() or output.is_symlink():
        raise ResumeError("OUTPUT_EXISTS")
    return repo, workspace, checkpoint, output


def _publish(raw: bytes, output: Path, *, repository_root: Path, task_id: str) -> tuple[str, int]:
    try:
        validate_state_structure_bytes(raw, expected_task_id=task_id)
    except BodyStateError as exc:
        raise ResumeError(f"STATE_{exc.code}") from exc
    temp_path: str | None = None
    published = False
    verified = False
    try:
        fd, temp_path = tempfile.mkstemp(prefix=f".{output.name}.tmp-", suffix=".body-state", dir=str(output.parent))
        os.chmod(temp_path, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        if Path(temp_path).parent != output.parent:
            raise ResumeError("ATOMIC_MATERIALIZATION_UNSUPPORTED")
        if Path(temp_path).read_bytes() != raw:
            raise ResumeError("PREPUBLICATION_READBACK_MISMATCH")
        if output.exists() or output.is_symlink():
            raise ResumeError("OUTPUT_EXISTS")
        try:
            os.link(temp_path, output)
        except FileExistsError as exc:
            raise ResumeError("OUTPUT_EXISTS", output_visible=True) from exc
        except OSError as exc:
            if exc.errno in {errno.EXDEV, errno.ENOTSUP, errno.EOPNOTSUPP, errno.EINVAL, errno.ENOSYS}:
                raise ResumeError("ATOMIC_MATERIALIZATION_UNSUPPORTED") from exc
            raise
        published = True
        os.unlink(temp_path); temp_path = None
        try:
            dir_fd = os.open(str(output.parent), os.O_RDONLY)
            try: os.fsync(dir_fd)
            finally: os.close(dir_fd)
        except OSError as exc:
            if exc.errno not in {errno.ENOTSUP, errno.EOPNOTSUPP, errno.EINVAL, errno.ENOSYS}:
                raise
        final = output.read_bytes()
        if final != raw or hashlib.sha256(final).hexdigest() != hashlib.sha256(raw).hexdigest() or len(final) != len(raw):
            raise ResumeError("FINAL_READBACK_MISMATCH", "AFTER_PUBLICATION", output_visible=True)
        try:
            validate_state_bytes(final, repository_root=repository_root, expected_task_id=task_id)
        except BodyStateError as exc:
            raise ResumeError(f"FINAL_STATE_{exc.code}", "AFTER_PUBLICATION", output_visible=True) from exc
        verified = True
        return hashlib.sha256(final).hexdigest(), len(final)
    except ResumeError as exc:
        if temp_path is not None:
            try: os.unlink(temp_path)
            except OSError: pass
        if published:
            exc.phase = "AFTER_PUBLICATION"
            exc.output_visible = output.exists() or output.is_symlink()
            exc.final_bytes_verified = verified
        raise
    except Exception as exc:
        if temp_path is not None:
            try: os.unlink(temp_path)
            except OSError: pass
        raise ResumeError("ATOMIC_MATERIALIZATION_FAILED", "AFTER_PUBLICATION" if published or output.exists() else "BEFORE_PUBLICATION", output_visible=published or output.exists(), final_bytes_verified=verified) from exc


def _receipt(request: dict[str, Any], checkpoint: dict[str, Any], status: str, output_path: str, output_sha: str, output_size: int) -> dict[str, Any]:
    state = checkpoint["BODY_STATE_SNAPSHOT"]
    result = {"REQUEST_ID": request["REQUEST_ID"], "STATUS": status, "TASK_ID": request["TASK_ID"], "CHECKPOINT_ID": request["CHECKPOINT_ID"], "CHECKPOINT_PATH": request["CHECKPOINT_PATH"], "CHECKPOINT_SHA256": request["CHECKPOINT_SHA256"], "CHECKPOINT_BYTE_SIZE": request["CHECKPOINT_BYTE_SIZE"], "SEALED_PLAN_REFERENCE": checkpoint["SEALED_PLAN_REFERENCE"], "SEALED_PLAN_SHA256": checkpoint["SEALED_PLAN_SHA256"], "CURRENT_STEP": state["CURRENT_STEP"], "COMPLETED_STEP_COUNT": len(state["COMPLETED_STEP_IDS"]), "VALIDATION_STATUS": state["VALIDATION_STATUS"], "RESUMED_BODY_STATE_PATH": output_path, "RESUMED_BODY_STATE_SHA256": output_sha, "RESUMED_BODY_STATE_BYTE_SIZE": output_size, "SUMMARY": "Validated restart admission; no action executed" if status == "READY" else "Validated restart admission is blocked; no action authorized"}
    if status == "READY": result["NEXT_AUTHORIZED_ACTION"] = state["NEXT_AUTHORIZED_ACTION"]
    else: result["OPEN_BLOCKER_COUNT"] = len(state["OPEN_BLOCKERS"])
    raw = _canonical(result)
    if len(raw) > RECEIPT_MAX_BYTES:
        raise ResumeError("RECEIPT_TOO_LARGE", "AFTER_PUBLICATION", output_visible=True, final_bytes_verified=True)
    return result


def admit_restart(request_raw: bytes, *, repository_root: Path | str, workspace_root: Path | str) -> dict[str, Any]:
    request = _request(request_raw)
    repo, _workspace_root, checkpoint_path, output = _validate_roots(request, repository_root, workspace_root)
    try:
        checkpoint_raw = checkpoint_path.read_bytes()
    except OSError as exc:
        raise ResumeError("CHECKPOINT_READ") from exc
    if len(checkpoint_raw) > CHECKPOINT_MAX_BYTES:
        raise ResumeError("CHECKPOINT_TOO_LARGE")
    actual_sha = hashlib.sha256(checkpoint_raw).hexdigest()
    if actual_sha != request["CHECKPOINT_SHA256"] or len(checkpoint_raw) != request["CHECKPOINT_BYTE_SIZE"]:
        raise ResumeError("CHECKPOINT_IDENTITY_MISMATCH")
    try:
        checkpoint = validate_checkpoint_bytes(checkpoint_raw, repository_root=repo, expected_sha256=request["CHECKPOINT_SHA256"], expected_byte_size=request["CHECKPOINT_BYTE_SIZE"])
    except CheckpointError as exc:
        raise ResumeError(f"CHECKPOINT_{exc.code}") from exc
    if checkpoint["TASK_ID"] != request["TASK_ID"]: raise ResumeError("TASK_MISMATCH")
    if checkpoint["CHECKPOINT_ID"] != request["CHECKPOINT_ID"]: raise ResumeError("CHECKPOINT_ID_MISMATCH")
    if checkpoint["SEALED_PLAN_REFERENCE"] != request["EXPECTED_SEALED_PLAN_REFERENCE"]: raise ResumeError("SEALED_PLAN_REFERENCE_MISMATCH")
    if checkpoint["SEALED_PLAN_SHA256"] != request["EXPECTED_SEALED_PLAN_SHA256"]: raise ResumeError("SEALED_PLAN_HASH_MISMATCH")
    state_raw = _canonical(checkpoint["BODY_STATE_SNAPSHOT"])
    origin = checkpoint["BODY_STATE_ORIGIN"]
    if hashlib.sha256(state_raw).hexdigest() != origin["sha256"] or len(state_raw) != origin["byte_size"]:
        raise ResumeError("BODY_STATE_ORIGIN_MISMATCH")
    completed = checkpoint["BODY_STATE_SNAPSHOT"]["COMPLETED_STEP_IDS"]
    if len(set(completed)) != len(completed):
        raise ResumeError("DUPLICATE_COMPLETED_STEP_IDS")
    if checkpoint["BODY_STATE_SNAPSHOT"]["CURRENT_STEP"] in completed:
        raise ResumeError("CURRENT_STEP_ALREADY_COMPLETED")
    status = "READY" if checkpoint["BODY_STATE_SNAPSHOT"]["VALIDATION_STATUS"] == "VALID" and not checkpoint["BODY_STATE_SNAPSHOT"]["OPEN_BLOCKERS"] else "BLOCKED"
    output_sha, output_size = _publish(state_raw, output, repository_root=repo, task_id=request["TASK_ID"])
    return _receipt(request, checkpoint, status, request["RESUMED_BODY_STATE_PATH"], output_sha, output_size)


def validate_restart_receipt(raw: bytes, *, repository_root: Path | str, workspace_root: Path | str) -> dict[str, Any]:
    value = _parse(raw, RECEIPT_MAX_BYTES)
    status = value.get("STATUS") if isinstance(value, dict) else None
    fields = READY_FIELDS if status == "READY" else BLOCKED_FIELDS if status == "BLOCKED" else set()
    if not isinstance(value, dict) or set(value) != fields:
        raise ResumeError("RECEIPT_SCHEMA")
    for key in ("REQUEST_ID", "TASK_ID", "CHECKPOINT_ID", "CURRENT_STEP", "VALIDATION_STATUS", "SUMMARY"):
        _short(value[key], ids=key in {"REQUEST_ID", "TASK_ID", "CHECKPOINT_ID"})
    _safe_relative(value["CHECKPOINT_PATH"]); _safe_relative(value["RESUMED_BODY_STATE_PATH"])
    for key in ("CHECKPOINT_SHA256", "SEALED_PLAN_SHA256", "RESUMED_BODY_STATE_SHA256"):
        if not isinstance(value[key], str) or not _HEX.fullmatch(value[key]): raise ResumeError("RECEIPT_INVALID_HASH")
    for key in ("CHECKPOINT_BYTE_SIZE", "COMPLETED_STEP_COUNT", "RESUMED_BODY_STATE_BYTE_SIZE"):
        if not isinstance(value[key], int) or isinstance(value[key], bool) or value[key] < 0: raise ResumeError("RECEIPT_INVALID_SIZE")
    if value["CHECKPOINT_BYTE_SIZE"] > CHECKPOINT_MAX_BYTES or value["RESUMED_BODY_STATE_BYTE_SIZE"] > MAX_STATE_BYTES or value["COMPLETED_STEP_COUNT"] > 64:
        raise ResumeError("RECEIPT_INVALID_SIZE")
    _short(value["SEALED_PLAN_REFERENCE"])
    if status == "READY": _short(value["NEXT_AUTHORIZED_ACTION"])
    else:
        if not isinstance(value["OPEN_BLOCKER_COUNT"], int) or isinstance(value["OPEN_BLOCKER_COUNT"], bool) or value["OPEN_BLOCKER_COUNT"] < 0: raise ResumeError("RECEIPT_INVALID_BLOCKER_COUNT")
    repo = _root(repository_root, "REPOSITORY_INVALID"); workspace = _root(workspace_root, "RUNTIME_WORKSPACE_INVALID")
    if _inside(workspace, repo): raise ResumeError("RUNTIME_WORKSPACE_IN_REPOSITORY")
    checkpoint = _path(workspace, value["CHECKPOINT_PATH"])
    if _inside(checkpoint.parent.resolve(strict=True), repo): raise ResumeError("PATH_INSIDE_REPOSITORY")
    output = _path(workspace, value["RESUMED_BODY_STATE_PATH"], file=True)
    if _inside(output.resolve(strict=True), repo): raise ResumeError("PATH_INSIDE_REPOSITORY")
    final = output.read_bytes()
    if hashlib.sha256(final).hexdigest() != value["RESUMED_BODY_STATE_SHA256"] or len(final) != value["RESUMED_BODY_STATE_BYTE_SIZE"]:
        raise ResumeError("RESUMED_STATE_IDENTITY_MISMATCH")
    try:
        state = validate_state_bytes(final, repository_root=repo, expected_task_id=value["TASK_ID"])
    except (BodyStateError, OSError) as exc:
        raise ResumeError("RESUMED_STATE_INVALID") from exc
    if state["CURRENT_STEP"] != value["CURRENT_STEP"] or len(state["COMPLETED_STEP_IDS"]) != value["COMPLETED_STEP_COUNT"] or state["VALIDATION_STATUS"] != value["VALIDATION_STATUS"] or state["SEALED_PLAN_REFERENCE"] != value["SEALED_PLAN_REFERENCE"] or state["SEALED_PLAN_SHA256"] != value["SEALED_PLAN_SHA256"]:
        raise ResumeError("RECEIPT_STATE_MISMATCH")
    if status == "READY" and state["NEXT_AUTHORIZED_ACTION"] != value["NEXT_AUTHORIZED_ACTION"]:
        raise ResumeError("RECEIPT_ACTION_MISMATCH")
    if status == "BLOCKED" and state["VALIDATION_STATUS"] == "VALID" and not state["OPEN_BLOCKERS"]:
        raise ResumeError("RECEIPT_BLOCKER_MISMATCH")
    return value


def process_request(raw_request: bytes, *, repository_root: Path | str, workspace_root: Path | str) -> tuple[int, bytes]:
    try:
        return 0, _canonical(admit_restart(raw_request, repository_root=repository_root, workspace_root=workspace_root))
    except (OSError, ResumeError) as exc:
        failure = {"STATUS":"INVALID", "ERROR_CODE":getattr(exc, "code", "FILE_IO"), "PHASE":getattr(exc, "phase", "BEFORE_PUBLICATION"), "OUTPUT_VISIBLE":getattr(exc, "output_visible", False), "FINAL_BYTES_VERIFIED":getattr(exc, "final_bytes_verified", False), "SUMMARY":"Restart admission rejected; no action executed"}
        raw = _canonical(failure)
        if len(raw) > RECEIPT_MAX_BYTES: raw = b'{"ERROR_CODE":"INVALID","FINAL_BYTES_VERIFIED":false,"OUTPUT_VISIBLE":false,"PHASE":"BEFORE_PUBLICATION","STATUS":"INVALID","SUMMARY":"Restart admission rejected"}\n'
        return 2, raw


def _main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("request"); parser.add_argument("--repository-root", required=True); parser.add_argument("--workspace-root", required=True)
    args = parser.parse_args(); code, raw = process_request(Path(args.request).read_bytes(), repository_root=args.repository_root, workspace_root=args.workspace_root); print(raw.decode(), end=""); return code


if __name__ == "__main__": raise SystemExit(_main())
