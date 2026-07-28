"""Create-only, self-contained immutable checkpoints for metadata-only Body state."""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import tempfile
import errno
from pathlib import Path
from typing import Any

from harness.body_state import (
    MAX_ID_BYTES,
    MAX_PATH_BYTES,
    MAX_STATE_BYTES,
    BodyStateError,
    SHA256_RE,
    validate_state_bytes,
    validate_state_structure_bytes,
)

REQUEST_MAX_BYTES = 8192
CHECKPOINT_MAX_BYTES = 40960
RECEIPT_MAX_BYTES = 4096
REQUEST_LIMIT = REQUEST_MAX_BYTES
CHECKPOINT_LIMIT = CHECKPOINT_MAX_BYTES
CREATION_RECEIPT_LIMIT = RECEIPT_MAX_BYTES
MAX_SHORT_BYTES = 256
CHECKPOINT_VERSION = 1
VALIDATOR_ID = "harness.body_state.validate_state_bytes"
REQUEST_FIELDS = {"REQUEST_ID", "CHECKPOINT_ID", "TASK_ID", "BODY_STATE_PATH", "BODY_STATE_SHA256", "BODY_STATE_BYTE_SIZE", "CHECKPOINT_PATH"}
ORIGIN_FIELDS = {"workspace_relative_path", "sha256", "byte_size"}
RECEIPT_FIELDS = {"status", "validator_id", "validated_body_state_sha256", "artifact_reference_count"}
CHECKPOINT_FIELDS = {"CHECKPOINT_VERSION", "CHECKPOINT_ID", "TASK_ID", "SEALED_PLAN_REFERENCE", "SEALED_PLAN_SHA256", "BODY_STATE_ORIGIN", "BODY_STATE_SNAPSHOT", "VALIDATION_RECEIPT"}
RECEIPT_OUTPUT_FIELDS = {"REQUEST_ID", "STATUS", "CHECKPOINT_PATH", "CHECKPOINT_SHA256", "CHECKPOINT_BYTE_SIZE", "BODY_STATE_SHA256", "ATOMIC_PUBLICATION_METHOD", "DURABILITY_MODE", "SUMMARY"}
_HEX = re.compile(r"^[0-9a-f]{64}$")


class CheckpointError(ValueError):
    def __init__(self, code: str, phase: str = "BEFORE_PUBLICATION"):
        self.code, self.phase = code, phase
        self.final_checkpoint_exists = False
        self.final_bytes_verified = False
        self.durability_confirmation = "NOT_APPLICABLE"
        super().__init__(f"{code} ({phase})")


def _canonical(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _parse_canonical(raw: bytes, *, maximum: int, code: str) -> Any:
    if len(raw) > maximum:
        raise CheckpointError(code)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CheckpointError("UTF8") from exc
    if text.startswith("\ufeff") or not raw.endswith(b"\n") or raw.endswith(b"\n\n"):
        raise CheckpointError("ENCODING")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise CheckpointError("DUPLICATE_KEY")
            result[key] = value
        return result

    try:
        value = json.loads(text, object_pairs_hook=pairs)
    except CheckpointError:
        raise
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise CheckpointError("JSON") from exc
    if _canonical(value) != raw:
        raise CheckpointError("NONCANONICAL")
    return value


def _short(value: Any, *, ids: bool = False) -> str:
    if not isinstance(value, str) or not value:
        raise CheckpointError("SHORT_STRING")
    limit = MAX_ID_BYTES if ids else MAX_SHORT_BYTES
    if len(value.encode("utf-8")) > limit:
        raise CheckpointError("SHORT_STRING")
    return value


def _safe_relative(value: Any, *, limit: int = MAX_PATH_BYTES) -> str:
    if not isinstance(value, str) or not value or len(value.encode("utf-8")) > limit:
        raise CheckpointError("UNSAFE_PATH")
    path = Path(value)
    if path.is_absolute() or "\\" in value or any(part in {"", ".", ".."} for part in value.split("/")):
        raise CheckpointError("UNSAFE_PATH")
    return value


def _sha_size(raw: bytes) -> tuple[str, int]:
    return hashlib.sha256(raw).hexdigest(), len(raw)


def _workspace(workspace_root: Path | str) -> Path:
    try:
        root = Path(workspace_root).resolve(strict=True)
    except OSError as exc:
        raise CheckpointError("WORKSPACE_INVALID") from exc
    if not root.is_dir():
        raise CheckpointError("WORKSPACE_INVALID")
    return root


def _no_symlink_components(root: Path, relative: str, *, require_file: bool = False, parent_only: bool = False) -> Path:
    current = root
    parts = relative.split("/")
    check_parts = parts[:-1] if parent_only else parts
    for part in check_parts:
        current = current / part
        try:
            if current.is_symlink():
                raise CheckpointError("SYMLINK_PATH")
        except OSError as exc:
            raise CheckpointError("PATH_IO") from exc
    target = root.joinpath(*parts)
    if require_file:
        try:
            if target.is_symlink() or not target.is_file():
                raise CheckpointError("SOURCE_INVALID")
        except OSError as exc:
            raise CheckpointError("PATH_IO") from exc
    return target


def _request(raw: bytes) -> dict[str, Any]:
    value = _parse_canonical(raw, maximum=REQUEST_MAX_BYTES, code="REQUEST_TOO_LARGE")
    if not isinstance(value, dict) or set(value) != REQUEST_FIELDS:
        raise CheckpointError("REQUEST_FIELDS")
    for key in ("REQUEST_ID", "CHECKPOINT_ID", "TASK_ID"):
        _short(value[key], ids=True)
    _safe_relative(value["BODY_STATE_PATH"])
    _safe_relative(value["CHECKPOINT_PATH"])
    if not isinstance(value["BODY_STATE_SHA256"], str) or not _HEX.fullmatch(value["BODY_STATE_SHA256"]):
        raise CheckpointError("BODY_STATE_SHA256")
    if not isinstance(value["BODY_STATE_BYTE_SIZE"], int) or isinstance(value["BODY_STATE_BYTE_SIZE"], bool) or value["BODY_STATE_BYTE_SIZE"] < 0:
        raise CheckpointError("BODY_STATE_BYTE_SIZE")
    if value["BODY_STATE_BYTE_SIZE"] > MAX_STATE_BYTES:
        raise CheckpointError("BODY_STATE_BYTE_SIZE")
    return value


def _checkpoint_structure(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != CHECKPOINT_FIELDS:
        raise CheckpointError("CHECKPOINT_FIELDS")
    if value["CHECKPOINT_VERSION"] != CHECKPOINT_VERSION or isinstance(value["CHECKPOINT_VERSION"], bool):
        raise CheckpointError("CHECKPOINT_VERSION")
    _short(value["CHECKPOINT_ID"], ids=True); _short(value["TASK_ID"], ids=True); _safe_relative(value["SEALED_PLAN_REFERENCE"])
    if not isinstance(value["SEALED_PLAN_SHA256"], str) or not _HEX.fullmatch(value["SEALED_PLAN_SHA256"]):
        raise CheckpointError("SEALED_PLAN_SHA256")
    origin = value["BODY_STATE_ORIGIN"]
    if not isinstance(origin, dict) or set(origin) != ORIGIN_FIELDS:
        raise CheckpointError("ORIGIN_FIELDS")
    _safe_relative(origin["workspace_relative_path"])
    if not isinstance(origin["sha256"], str) or not _HEX.fullmatch(origin["sha256"]):
        raise CheckpointError("ORIGIN_SHA256")
    if not isinstance(origin["byte_size"], int) or isinstance(origin["byte_size"], bool) or origin["byte_size"] < 0 or origin["byte_size"] > MAX_STATE_BYTES:
        raise CheckpointError("ORIGIN_BYTE_SIZE")
    snapshot = value["BODY_STATE_SNAPSHOT"]
    snapshot_raw = _canonical(snapshot)
    try:
        parsed = validate_state_structure_bytes(snapshot_raw)
    except BodyStateError as exc:
        raise CheckpointError("SNAPSHOT_INVALID") from exc
    if _sha_size(snapshot_raw) != (origin["sha256"], origin["byte_size"]):
        raise CheckpointError("SNAPSHOT_ORIGIN_MISMATCH")
    if value["TASK_ID"] != parsed["TASK_ID"] or value["SEALED_PLAN_REFERENCE"] != parsed["SEALED_PLAN_REFERENCE"] or value["SEALED_PLAN_SHA256"] != parsed["SEALED_PLAN_SHA256"]:
        raise CheckpointError("IDENTITY_MISMATCH")
    receipt = value["VALIDATION_RECEIPT"]
    if not isinstance(receipt, dict) or set(receipt) != RECEIPT_FIELDS:
        raise CheckpointError("RECEIPT_FIELDS")
    if receipt["status"] != "PASS" or receipt["validator_id"] != VALIDATOR_ID:
        raise CheckpointError("RECEIPT_INVALID")
    if receipt["validated_body_state_sha256"] != origin["sha256"] or not isinstance(receipt["artifact_reference_count"], int) or isinstance(receipt["artifact_reference_count"], bool) or receipt["artifact_reference_count"] != len(parsed["ARTIFACT_REFERENCES"]):
        raise CheckpointError("RECEIPT_MISMATCH")
    return value


def validate_checkpoint_structure_bytes(raw: bytes) -> dict[str, Any]:
    if len(raw) > CHECKPOINT_MAX_BYTES:
        raise CheckpointError("CHECKPOINT_TOO_LARGE")
    return _checkpoint_structure(_parse_canonical(raw, maximum=CHECKPOINT_MAX_BYTES, code="CHECKPOINT_TOO_LARGE"))


def _check_external_identity(raw: bytes, expected_sha256: str | None, expected_byte_size: int | None) -> None:
    if expected_sha256 is not None:
        if not isinstance(expected_sha256, str) or not _HEX.fullmatch(expected_sha256):
            raise CheckpointError("EXPECTED_CHECKPOINT_SHA256")
        if hashlib.sha256(raw).hexdigest() != expected_sha256:
            raise CheckpointError("CHECKPOINT_IDENTITY_MISMATCH")
    if expected_byte_size is not None:
        if not isinstance(expected_byte_size, int) or isinstance(expected_byte_size, bool) or expected_byte_size < 0:
            raise CheckpointError("EXPECTED_CHECKPOINT_BYTE_SIZE")
        if len(raw) != expected_byte_size:
            raise CheckpointError("CHECKPOINT_IDENTITY_MISMATCH")


def validate_checkpoint_bytes(raw: bytes, *, repository_root: Path | str = ".", expected_sha256: str | None = None, expected_byte_size: int | None = None) -> dict[str, Any]:
    _check_external_identity(raw, expected_sha256, expected_byte_size)
    value = validate_checkpoint_structure_bytes(raw)
    try:
        validate_state_bytes(_canonical(value["BODY_STATE_SNAPSHOT"]), repository_root=repository_root)
    except BodyStateError as exc:
        raise CheckpointError("ARTIFACT_INVALID") from exc
    return value


def _receipt(request_id: str, status: str, path: str, checkpoint: bytes, source_sha: str, method: str, mode: str, summary: str) -> dict[str, Any]:
    value = {"REQUEST_ID": request_id, "STATUS": status, "CHECKPOINT_PATH": path, "CHECKPOINT_SHA256": hashlib.sha256(checkpoint).hexdigest(), "CHECKPOINT_BYTE_SIZE": len(checkpoint), "BODY_STATE_SHA256": source_sha, "ATOMIC_PUBLICATION_METHOD": method, "DURABILITY_MODE": mode, "SUMMARY": summary}
    if len(_canonical(value)) > RECEIPT_MAX_BYTES:
        raise CheckpointError("RECEIPT_TOO_LARGE", "AFTER_PUBLICATION")
    return value


def create_checkpoint(request_raw: bytes, *, repository_root: Path | str, workspace_root: Path | str) -> dict[str, Any]:
    request = _request(request_raw)
    root = _workspace(workspace_root)
    source_path = _no_symlink_components(root, request["BODY_STATE_PATH"], require_file=True)
    target = _no_symlink_components(root, request["CHECKPOINT_PATH"], parent_only=True)
    try:
        if target.exists() or target.is_symlink():
            raise CheckpointError("TARGET_EXISTS")
    except OSError as exc:
        raise CheckpointError("PATH_IO") from exc
    try:
        with source_path.open("rb") as stream:
            body_raw = stream.read(MAX_STATE_BYTES + 1)
    except OSError as exc:
        raise CheckpointError("SOURCE_READ") from exc
    source_sha, source_size = _sha_size(body_raw)
    if source_size != request["BODY_STATE_BYTE_SIZE"]:
        raise CheckpointError("BODY_STATE_SIZE")
    if source_sha != request["BODY_STATE_SHA256"]:
        raise CheckpointError("BODY_STATE_HASH")
    try:
        state = validate_state_bytes(body_raw, repository_root=repository_root, expected_task_id=request["TASK_ID"])
    except BodyStateError as exc:
        if exc.code == "TASK_ID_MISMATCH":
            raise CheckpointError("TASK_ID_MISMATCH") from exc
        raise CheckpointError(f"BODY_STATE_{exc.code}") from exc
    snapshot_raw = _canonical(state)
    checkpoint = {"CHECKPOINT_VERSION": 1, "CHECKPOINT_ID": request["CHECKPOINT_ID"], "TASK_ID": state["TASK_ID"], "SEALED_PLAN_REFERENCE": state["SEALED_PLAN_REFERENCE"], "SEALED_PLAN_SHA256": state["SEALED_PLAN_SHA256"], "BODY_STATE_ORIGIN":{"workspace_relative_path":request["BODY_STATE_PATH"],"sha256":source_sha,"byte_size":source_size}, "BODY_STATE_SNAPSHOT":state, "VALIDATION_RECEIPT":{"status":"PASS","validator_id":"harness.body_state.validate_state_bytes","validated_body_state_sha256":source_sha,"artifact_reference_count":len(state["ARTIFACT_REFERENCES"])}}
    checkpoint_raw = _canonical(checkpoint)
    if len(checkpoint_raw) > CHECKPOINT_MAX_BYTES:
        raise CheckpointError("CHECKPOINT_TOO_LARGE")
    _checkpoint_structure(_parse_canonical(checkpoint_raw, maximum=CHECKPOINT_MAX_BYTES, code="CHECKPOINT_TOO_LARGE"))
    temp_path = None
    published = False
    final_bytes_verified = False
    durability_confirmation = "INCOMPLETE"
    try:
        fd, temp_path = tempfile.mkstemp(prefix=f".{target.name}.tmp-", suffix=".checkpoint", dir=str(target.parent))
        os.chmod(temp_path, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(checkpoint_raw); stream.flush(); os.fsync(stream.fileno())
        if Path(temp_path).parent != target.parent:
            raise CheckpointError("TEMP_NOT_SIBLING")
        if Path(temp_path).read_bytes() != checkpoint_raw:
            raise CheckpointError("TEMP_READBACK")
        validate_checkpoint_structure_bytes(checkpoint_raw)
        if target.exists() or target.is_symlink():
            raise CheckpointError("TARGET_EXISTS")
        try:
            os.link(temp_path, target)
        except FileExistsError as exc:
            error = CheckpointError("TARGET_EXISTS")
            error.final_checkpoint_exists = True
            raise error from exc
        except OSError as exc:
            if exc.errno in {errno.EXDEV, errno.ENOTSUP, errno.EOPNOTSUPP, errno.EINVAL, errno.ENOSYS}:
                raise CheckpointError("ATOMIC_NO_CLOBBER_UNSUPPORTED") from exc
            raise
        published = True
        os.unlink(temp_path)
        temp_path = None
        method = "ATOMIC_HARD_LINK_CREATE_ONLY"
        directory_fsync = True
        try:
            dir_fd = os.open(str(target.parent), os.O_RDONLY)
            try: os.fsync(dir_fd)
            finally: os.close(dir_fd)
        except (AttributeError, OSError) as exc:
            if isinstance(exc, OSError) and exc.errno in {errno.ENOTSUP, errno.EOPNOTSUPP, errno.EINVAL, errno.ENOSYS}:
                directory_fsync = False
            else:
                raise
        mode = "ATOMIC_HARD_LINK_FILE_AND_DIRECTORY_FSYNC" if directory_fsync else "ATOMIC_HARD_LINK_FILE_FSYNC_ONLY"
        durability_confirmation = mode
        final_raw = target.read_bytes()
        if final_raw != checkpoint_raw or hashlib.sha256(final_raw).hexdigest() != hashlib.sha256(checkpoint_raw).hexdigest():
            error = CheckpointError("FINAL_READBACK_MISMATCH", "AFTER_PUBLICATION")
            error.final_checkpoint_exists = True; error.final_bytes_verified = False; error.durability_confirmation = mode
            raise error
        final_bytes_verified = True
        validate_checkpoint_structure_bytes(final_raw)
        return _receipt(request["REQUEST_ID"], "SUCCESS", request["CHECKPOINT_PATH"], final_raw, source_sha, method, mode, "Immutable checkpoint published and verified")
    except CheckpointError as exc:
        if temp_path is not None:
            try: os.unlink(temp_path)
            except OSError: pass
        if published:
            exc.phase = "AFTER_PUBLICATION"
            exc.final_checkpoint_exists = target.exists() or target.is_symlink()
            exc.final_bytes_verified = final_bytes_verified
            exc.durability_confirmation = durability_confirmation
        raise
    except Exception as exc:
        if temp_path is not None:
            try: os.unlink(temp_path)
            except OSError: pass
        error = CheckpointError("PUBLICATION_IO", "AFTER_PUBLICATION" if published or target.exists() else "BEFORE_PUBLICATION")
        error.final_checkpoint_exists = target.exists() or target.is_symlink()
        error.final_bytes_verified = final_bytes_verified
        error.durability_confirmation = durability_confirmation if error.final_checkpoint_exists else "NOT_APPLICABLE"
        raise error from exc


def validate_checkpoint_file(path: Path | str, *, repository_root: Path | str = ".", full: bool = False, expected_sha256: str | None = None, expected_byte_size: int | None = None) -> dict[str, Any]:
    try: raw = Path(path).read_bytes()
    except OSError as exc: raise CheckpointError("CHECKPOINT_READ") from exc
    _check_external_identity(raw, expected_sha256, expected_byte_size)
    return validate_checkpoint_bytes(raw, repository_root=repository_root) if full else validate_checkpoint_structure_bytes(raw)


def process_request(raw_request: bytes, *, repository_root: Path | str, workspace_root: Path | str) -> tuple[int, bytes]:
    """Return a bounded canonical receipt or bounded failure for one request."""
    try:
        result = create_checkpoint(raw_request, repository_root=repository_root, workspace_root=workspace_root)
        return 0, _canonical(result)
    except (OSError, CheckpointError) as exc:
        failure = {"STATUS":"FAILURE","ERROR_CODE":getattr(exc, "code", "FILE_IO"),"PHASE":getattr(exc, "phase", "BEFORE_PUBLICATION"),"FINAL_CHECKPOINT_EXISTS":getattr(exc, "final_checkpoint_exists", False),"FINAL_BYTES_VERIFIED":getattr(exc, "final_bytes_verified", False),"DURABILITY_CONFIRMATION":getattr(exc, "durability_confirmation", "NOT_APPLICABLE"),"SUMMARY":"Checkpoint operation failed"}
        raw = _canonical(failure)
        if len(raw) > RECEIPT_MAX_BYTES:
            raw = b'{"DURABILITY_CONFIRMATION":"NOT_APPLICABLE","ERROR_CODE":"FAILURE_OUTPUT_TOO_LARGE","FINAL_BYTES_VERIFIED":false,"FINAL_CHECKPOINT_EXISTS":false,"PHASE":"BEFORE_PUBLICATION","STATUS":"FAILURE","SUMMARY":"Checkpoint operation failed"}\n'
        return 2, raw


def _main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create"); create.add_argument("request"); create.add_argument("--repository-root", required=True); create.add_argument("--workspace-root", required=True)
    validate = sub.add_parser("validate"); validate.add_argument("checkpoint"); validate.add_argument("--repository-root", default="."); validate.add_argument("--full", action="store_true"); validate.add_argument("--expected-sha256"); validate.add_argument("--expected-byte-size", type=int)
    args = parser.parse_args()
    try:
        if args.command == "create": result = _receipt(**{}) if False else create_checkpoint(Path(args.request).read_bytes(), repository_root=args.repository_root, workspace_root=args.workspace_root)
        else: result = validate_checkpoint_file(args.checkpoint, repository_root=args.repository_root, full=args.full, expected_sha256=args.expected_sha256, expected_byte_size=args.expected_byte_size)
    except (OSError, CheckpointError) as exc:
        print(json.dumps({"STATUS":"FAILURE","ERROR_CODE":getattr(exc, "code", "FILE_IO"),"PHASE":getattr(exc, "phase", "BEFORE_PUBLICATION"),"FINAL_CHECKPOINT_EXISTS":getattr(exc, "final_checkpoint_exists", False),"FINAL_BYTES_VERIFIED":getattr(exc, "final_bytes_verified", False),"DURABILITY_CONFIRMATION":getattr(exc, "durability_confirmation", "NOT_APPLICABLE"),"SUMMARY":"Checkpoint operation failed"}, separators=(",", ":")))
        return 2
    print(_canonical(result).decode(), end="")
    return 0


if __name__ == "__main__": raise SystemExit(_main())
