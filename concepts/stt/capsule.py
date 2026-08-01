from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from .boundary import copy_tree, scope_contains, validate_tree
from .canonical import safe_relpath, sha256_file
from .errors import require


def materialize_capsule(checkpoint: Path, capsule: Path, read_scope: list[dict[str, str]], write_scope: list[dict[str, str]]) -> dict[str, Any]:
    require(not capsule.exists(), "CAPSULE_EXISTS", "capsule already exists")
    capsule.mkdir(parents=True, mode=0o700)
    selected: set[str] = set()
    for base, dirs, files in os.walk(checkpoint, followlinks=False):
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


def derive_delta(parent: Path, capsule: Path, write_scope: list[dict[str, str]], max_changed: int) -> list[dict[str, Any]]:
    paths: set[str] = set()
    for root in (parent, capsule):
        for base, dirs, files in os.walk(root, followlinks=False):
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


def overlay_delta(parent: Path, capsule: Path, candidate: Path, delta: list[dict[str, Any]]) -> None:
    copy_tree(parent, candidate)
    for item in sorted(delta, key=lambda x: x["path"].count("/"), reverse=True):
        if item["op"] != "delete":
            continue
        target = candidate / safe_relpath(item["path"])
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        elif target.exists() or target.is_symlink():
            target.unlink()
    for item in sorted(delta, key=lambda x: x["path"].count("/")):
        if item["op"] == "delete":
            continue
        rel = safe_relpath(item["path"]); source = capsule / rel; target = candidate / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            if target.is_dir() and not target.is_symlink(): shutil.rmtree(target)
            else: target.unlink()
        if item["op"] == "directory": target.mkdir(); os.chmod(target, item["mode"])
        elif item["op"] == "symlink": os.symlink(item["target"], target)
        else: shutil.copy2(source, target, follow_symlinks=False); os.chmod(target, item["mode"])
    validate_tree(candidate)
