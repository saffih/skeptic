from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

from .errors import STTError, require


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise STTError("DUPLICATE_JSON_KEY", f"duplicate JSON key: {key}")
        result[key] = value
    return result


def loads_strict(data: bytes | str) -> Any:
    if isinstance(data, bytes):
        try:
            data = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise STTError("NON_UTF8_JSON", "control JSON must be UTF-8") from exc
    try:
        return json.loads(data, object_pairs_hook=_pairs_no_duplicates)
    except STTError:
        raise
    except json.JSONDecodeError as exc:
        raise STTError("MALFORMED_JSON", str(exc)) from exc


def canonical_json_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise STTError("NON_CANONICAL_JSON", str(exc)) from exc
    return text.encode("utf-8") + b"\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write(path: Path, data: bytes, mode: int = 0o600, *, create_only: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd: int | None = None
    tmp_path: Path | None = None
    try:
        fd, raw_tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        tmp_path = Path(raw_tmp)
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb", closefd=True) as handle:
            fd = None
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if create_only:
            try:
                os.link(tmp_path, path, follow_symlinks=False)
            except FileExistsError as exc:
                raise STTError("ARTIFACT_EXISTS", f"create-only artifact exists: {path}") from exc
            tmp_path.unlink()
        else:
            os.replace(tmp_path, path)
        fsync_dir(path.parent)
    finally:
        if fd is not None:
            os.close(fd)
        if tmp_path is not None and tmp_path.exists():
            tmp_path.unlink()


def safe_relpath(raw: str, *, allow_dot: bool = False) -> str:
    require(isinstance(raw, str), "INVALID_PATH", "path must be a string")
    require("\x00" not in raw, "INVALID_PATH", "NUL is forbidden")
    require(raw != "", "INVALID_PATH", "empty path is forbidden")
    path = PurePosixPath(raw)
    require(not path.is_absolute(), "INVALID_PATH", "absolute path is forbidden", path=raw)
    parts = path.parts
    require(all(part not in ("", ".", "..") for part in parts), "INVALID_PATH", "path must be canonical", path=raw)
    normalized = path.as_posix()
    if allow_dot and raw == ".":
        return raw
    require(normalized == raw, "INVALID_PATH", "path must be canonical", path=raw)
    require(raw != ".git" and not raw.startswith(".git/"), "GIT_CONTROL_PATH_FORBIDDEN", "Git control path is forbidden")
    return raw


def ensure_no_symlink_components(path: Path, *, include_leaf: bool = True) -> None:
    current = Path(path.anchor or "/")
    parts = path.parts[1:] if path.is_absolute() else path.parts
    for index, part in enumerate(parts):
        current = current / part
        if index == len(parts) - 1 and not include_leaf:
            break
        if current.exists() or current.is_symlink():
            st = os.lstat(current)
            require(not stat.S_ISLNK(st.st_mode), "SYMLINK_COMPONENT", f"symlink component: {current}")


def exact_object_identity(path: Path) -> dict[str, Any]:
    st = os.lstat(path)
    kind = "file" if stat.S_ISREG(st.st_mode) else "directory" if stat.S_ISDIR(st.st_mode) else "symlink" if stat.S_ISLNK(st.st_mode) else "other"
    result: dict[str, Any] = {
        "kind": kind,
        "mode": stat.S_IMODE(st.st_mode),
        "uid": st.st_uid,
        "gid": st.st_gid,
        "device": st.st_dev,
        "inode": st.st_ino,
        "nlink": st.st_nlink,
        "size": st.st_size,
    }
    if kind == "file":
        result["sha256"] = sha256_file(path)
    elif kind == "symlink":
        target = os.readlink(path).encode("utf-8", "surrogateescape")
        result["target_sha256"] = sha256_bytes(target)
        result["target"] = os.readlink(path)
    return result
