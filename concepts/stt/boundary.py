from __future__ import annotations

import os
import stat
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from .canonical import canonical_json_bytes, safe_relpath, sha256_bytes, sha256_file
from .errors import STTError, require


ALLOWED_ROLES = {"planner", "reviewer", "worker"}
CONTROL_COMPONENTS = {".git", ".stt"}


def compact_receipt(*, task_id: str, task_root: Path, status: str, next_action: str | None, ledger_head: str, refs: list[dict[str, Any]], reason: str | None = None) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "task_id": task_id,
        "task_root": str(task_root),
        "status": status,
        "ledger_head": ledger_head,
        "next_action": next_action,
        "artifact_refs": refs,
    }
    if reason is not None:
        receipt["reason"] = reason
    data = canonical_json_bytes(receipt)
    require(len(data) <= 64 * 1024, "COMPACT_RECEIPT_TOO_LARGE", "Lead receipt exceeded compact bound")
    return receipt


def scope_contains(scope: list[dict[str, str]], rel: str) -> bool:
    target = PurePosixPath(safe_relpath(rel))
    for item in scope:
        base = PurePosixPath(item["path"])
        if item["kind"] == "file" and target == base:
            return True
        if item["kind"] == "tree" and (target == base or base in target.parents):
            return True
    return False


def validate_path_collisions(paths: Iterable[str], *, ignore_case: bool = False) -> None:
    seen: dict[str, str] = {}
    for rel in paths:
        key = unicodedata.normalize("NFC", rel)
        if ignore_case:
            key = key.casefold()
        prior = seen.get(key)
        require(prior is None or prior == rel, "PATH_ALIAS_COLLISION", "case-fold or Unicode-normalization path collision", first=prior, second=rel)
        seen[key] = rel


def discover_nested_repositories(workspace: Path) -> list[str]:
    """Find descendant Git directory or gitfile markers without entering them."""
    root = workspace.resolve(strict=True)
    found: list[str] = []
    for base, dirs, files in os.walk(root, topdown=True, followlinks=False):
        current = Path(base)
        if current != root and ".git" in {*dirs, *files}:
            marker = current / ".git"
            marker_stat = os.lstat(marker)
            require(stat.S_ISDIR(marker_stat.st_mode) or stat.S_ISREG(marker_stat.st_mode), "NESTED_REPOSITORY_MARKER_INVALID", "nested Git marker has unsupported type", path=marker.relative_to(root).as_posix())
            found.append(current.relative_to(root).as_posix())
            dirs[:] = []
            continue
        kept: list[str] = []
        for name in dirs:
            if name in CONTROL_COMPONENTS:
                continue
            path = current / name
            if stat.S_ISLNK(os.lstat(path).st_mode):
                continue
            kept.append(name)
        dirs[:] = kept
    validate_path_collisions(found, ignore_case=True)
    return sorted(found)


def scope_overlaps_nested(scope_path: str, nested_roots: Iterable[str]) -> str | None:
    declared = PurePosixPath(safe_relpath(scope_path))
    for raw_root in nested_roots:
        root = PurePosixPath(safe_relpath(raw_root))
        if declared == root or declared in root.parents or root in declared.parents:
            return root.as_posix()
    return None


def validate_scope_against_nested(scope: Iterable[dict[str, str]], nested_roots: Iterable[str]) -> None:
    roots = tuple(nested_roots)
    for item in scope:
        overlap = scope_overlaps_nested(item["path"], roots)
        require(overlap is None, "NESTED_REPOSITORY_SCOPE_FORBIDDEN", "scope overlaps nested repository or submodule", scope=item["path"], nested_root=overlap)


def validate_tree(root: Path, *, changed_paths: Iterable[str] | None = None, ignore_case: bool = False) -> dict[str, Any]:
    allowed_changed = set(changed_paths or [])
    entries: list[dict[str, Any]] = []
    for base, dirs, files in os.walk(root, followlinks=False):
        controls = CONTROL_COMPONENTS.intersection({*dirs, *files})
        require(not controls, "CONTROL_PATH_FORBIDDEN", "candidate contains Git or STT control state", paths=sorted(controls))
        dirs.sort(); files.sort()
        for name in dirs + files:
            path = Path(base) / name
            rel = path.relative_to(root).as_posix()
            safe_relpath(rel)
            st = os.lstat(path)
            mode = stat.S_IMODE(st.st_mode)
            require(st.st_uid == os.geteuid(), "UNSUPPORTED_METADATA", "candidate owner mismatch", path=rel)
            require(not mode & 0o7000, "UNSUPPORTED_METADATA", "candidate special mode bits", path=rel)
            if hasattr(os, "listxattr"):
                require(not os.listxattr(path, follow_symlinks=False), "UNSUPPORTED_METADATA", "candidate xattrs unsupported", path=rel)
            if stat.S_ISDIR(st.st_mode):
                kind = "directory"; entry = {"path": rel, "kind": kind, "mode": mode}
            elif stat.S_ISREG(st.st_mode):
                require(st.st_nlink == 1, "UNSUPPORTED_METADATA", "candidate hard-linked file", path=rel)
                kind = "file"; entry = {"path": rel, "kind": kind, "mode": mode, "size": st.st_size, "sha256": sha256_file(path)}
            elif stat.S_ISLNK(st.st_mode):
                target = os.readlink(path)
                require(not os.path.isabs(target), "SYMLINK_ESCAPE", "absolute symlink target", path=rel)
                normalized = (PurePosixPath(rel).parent / target)
                require(".." not in normalized.parts, "SYMLINK_ESCAPE", "symlink target escapes capsule", path=rel)
                kind = "symlink"; entry = {"path": rel, "kind": kind, "mode": mode, "target": target}
            else:
                raise STTError("UNSUPPORTED_OBJECT_TYPE", f"unsupported candidate object: {rel}")
            entries.append(entry)
    validate_path_collisions((entry["path"] for entry in entries), ignore_case=ignore_case)
    body = canonical_json_bytes({"schema_version": 1, "entries": entries})
    return {"schema_version": 1, "entries": entries, "sha256": sha256_bytes(body)}
