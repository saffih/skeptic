from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path
from typing import Any

from .boundary import scope_contains
from .canonical import safe_relpath, sha256_file
from .errors import STTError, require


def validate_workspace_target(
    workspace: Path,
    relative_path: str,
    *,
    allow_leaf_symlink_delete: bool = False,
) -> Path:
    """Validate one lexical workspace target without following its path."""
    rel = safe_relpath(relative_path)
    require(rel != ".stt" and not rel.startswith(".stt/"), "STT_CONTROL_PATH_FORBIDDEN", "STT control path is forbidden", path=rel)
    root = Path(os.path.abspath(os.fspath(workspace)))
    root_stat = os.lstat(root)
    require(stat.S_ISDIR(root_stat.st_mode) and not stat.S_ISLNK(root_stat.st_mode), "WORKSPACE_ROOT_INVALID", "workspace root must be a real directory")
    target = root.joinpath(*rel.split("/"))
    require(os.path.commonpath((os.fspath(root), os.fspath(target))) == os.fspath(root), "WORKSPACE_PATH_ESCAPE", "workspace target escapes root", path=rel)

    current = root
    for component in rel.split("/")[:-1]:
        current = current / component
        try:
            current_stat = os.lstat(current)
        except FileNotFoundError:
            break
        require(not stat.S_ISLNK(current_stat.st_mode), "WORKSPACE_SYMLINK_PARENT", "workspace target has a symlink parent", path=rel)
        require(stat.S_ISDIR(current_stat.st_mode), "WORKSPACE_PARENT_INVALID", "workspace target parent is not a directory", path=rel)

    try:
        leaf_stat = os.lstat(target)
    except FileNotFoundError:
        return target
    require(
        not stat.S_ISLNK(leaf_stat.st_mode) or allow_leaf_symlink_delete,
        "WORKSPACE_SYMLINK_LEAF",
        "workspace symlink leaf may only be deleted directly",
        path=rel,
    )
    return target


def materialize_capsule(checkpoint: Path, capsule: Path, read_scope: list[dict[str, str]], write_scope: list[dict[str, str]]) -> dict[str, Any]:
    require(not capsule.exists(), "CAPSULE_EXISTS", "capsule already exists")
    capsule.mkdir(parents=True, mode=0o700)
    selected: set[str] = set()
    for base, dirs, files in os.walk(checkpoint, followlinks=False):
        if Path(base) == checkpoint:
            dirs[:] = [name for name in dirs if name not in {".git", ".stt"}]
        for name in dirs + files:
            source = Path(base) / name
            rel = source.relative_to(checkpoint).as_posix()
            if scope_contains(read_scope, rel) or scope_contains(write_scope, rel):
                selected.add(rel)
    for rel in sorted(selected, key=lambda p: (p.count("/"), p)):
        source = checkpoint / rel; destination = capsule / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            os.symlink(os.readlink(source), destination)
        elif source.is_dir():
            destination.mkdir(exist_ok=True)
        else:
            shutil.copy2(source, destination, follow_symlinks=False)
        if not scope_contains(write_scope, rel) and destination.exists() and not destination.is_symlink():
            os.chmod(destination, os.stat(destination).st_mode & ~0o222)
    return {"selected_paths": sorted(selected)}


def apply_delta(workspace: Path, capsule: Path, delta: list[dict[str, Any]], write_scope: list[dict[str, str]]) -> None:
    """Apply a validated sparse delta directly to the shared workspace.

    All paths and source objects are checked before the first mutation. There
    is deliberately no rollback: a process failure can leave a partial delta.
    """
    validated: list[tuple[dict[str, Any], str, Path, Path | None]] = []
    seen: set[str] = set()
    for item in delta:
        rel = safe_relpath(item["path"])
        require(rel not in seen, "DUPLICATE_DELTA_PATH", "delta path is duplicated", path=rel)
        seen.add(rel)
        require(scope_contains(write_scope, rel), "WRITE_SCOPE_VIOLATION", "delta path outside write scope", path=rel)
        operation = item.get("op")
        require(operation in {"delete", "file", "directory", "symlink"}, "UNSUPPORTED_OBJECT_TYPE", "unsupported delta operation", op=operation)
        require(operation != "symlink", "UNSUPPORTED_SYMLINK_DELTA", "Worker-created or Worker-modified symlinks are unsupported", path=rel)
        target = validate_workspace_target(workspace, rel, allow_leaf_symlink_delete=operation == "delete")
        if item["op"] == "delete":
            validated.append((item, rel, target, None))
            continue
        source = validate_workspace_target(capsule, rel)
        require(source.exists() or source.is_symlink(), "DELTA_SOURCE_MISSING", "delta source missing", path=rel)
        if item["op"] == "file":
            require(source.is_file() and not source.is_symlink(), "UNSUPPORTED_OBJECT_TYPE", "delta file is not regular", path=rel)
        elif item["op"] == "directory":
            require(source.is_dir() and not source.is_symlink(), "UNSUPPORTED_OBJECT_TYPE", "delta directory invalid", path=rel)
        validated.append((item, rel, target, source))
    for item, rel, target, _ in sorted(validated, key=lambda value: value[1].count("/"), reverse=True):
        if item["op"] != "delete":
            continue
        if target.is_dir() and not target.is_symlink():
            try:
                target.rmdir()
            except OSError as exc:
                raise STTError("NONEMPTY_DIRECTORY_OPERATION", "delta refuses to remove a nonempty directory", {"path": rel}) from exc
        elif target.exists() or target.is_symlink():
            target.unlink()
    for item, rel, target, source in sorted(validated, key=lambda value: value[1].count("/")):
        if item["op"] == "delete":
            continue
        require(source is not None, "CONTROL_STATE_FAILED", "validated delta source missing", path=rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            if target.is_dir() and not target.is_symlink():
                try:
                    target.rmdir()
                except OSError as exc:
                    raise STTError("NONEMPTY_DIRECTORY_OPERATION", "delta refuses to replace a nonempty directory", {"path": rel}) from exc
            else: target.unlink()
        if item["op"] == "directory":
            target.mkdir(); os.chmod(target, item["mode"])
        else:
            shutil.copy2(source, target, follow_symlinks=False); os.chmod(target, item["mode"])


def derive_delta(parent: Path, capsule: Path, write_scope: list[dict[str, str]], max_changed: int) -> list[dict[str, Any]]:
    paths: set[str] = set()
    for root in (parent, capsule):
        for base, dirs, files in os.walk(root, followlinks=False):
            if Path(base) == root:
                dirs[:] = [name for name in dirs if name not in {".git", ".stt"}]
            for name in dirs + files:
                paths.add((Path(base) / name).relative_to(root).as_posix())
    delta: list[dict[str, Any]] = []
    for rel in sorted(paths):
        if not scope_contains(write_scope, rel):
            continue
        before, after = parent / rel, capsule / rel
        if not after.exists() and not after.is_symlink():
            if before.exists() or before.is_symlink():
                delta.append({"path": rel, "op": "delete"})
            continue
        if after.is_symlink():
            target = os.readlink(after)
            if not before.is_symlink() or os.readlink(before) != target:
                delta.append({"path": rel, "op": "symlink", "target": target})
        elif after.is_dir():
            if not before.is_dir():
                delta.append({"path": rel, "op": "directory", "mode": os.stat(after).st_mode & 0o777})
        elif after.is_file():
            changed = not before.is_file() or sha256_file(before) != sha256_file(after) or (os.stat(before).st_mode & 0o777) != (os.stat(after).st_mode & 0o777)
            if changed:
                delta.append({"path": rel, "op": "file", "sha256": sha256_file(after), "mode": os.stat(after).st_mode & 0o777})
    require(len(delta) <= max_changed, "CHANGED_PATH_LIMIT", "Worker delta exceeds changed-path limit")
    return delta
