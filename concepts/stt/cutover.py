from __future__ import annotations

import os
import shutil
import stat
import uuid
from pathlib import Path
from typing import Any

from .boundary import validate_tree
from .canonical import atomic_write, canonical_json_bytes, loads_strict, safe_relpath, sha256_file
from .errors import require


def _map(root: Path) -> dict[str, dict[str, Any]]:
    return {entry["path"]: entry for entry in validate_tree(root)["entries"]}


def build_manifest(source_baseline: Path, final_candidate: Path) -> dict[str, Any]:
    before, after = _map(source_baseline), _map(final_candidate)
    operations: list[dict[str, Any]] = []
    for rel in sorted(set(before) | set(after)):
        left, right = before.get(rel), after.get(rel)
        if left == right:
            continue
        if right is None:
            operations.append({"path": rel, "op": "delete", "before": left})
        elif left is None:
            operations.append({"path": rel, "op": "create", "after": right})
        elif left["kind"] == right["kind"] == "directory":
            operations.append({"path": rel, "op": "chmod", "before": left, "after": right})
        else:
            operations.append({"path": rel, "op": "replace", "before": left, "after": right})
    return {"schema_version": 1, "operations": operations}


def _matches(path: Path, identity: dict[str, Any] | None) -> bool:
    if identity is None:
        return not path.exists() and not path.is_symlink()
    if not path.exists() and not path.is_symlink():
        return False
    st = os.lstat(path)
    kind = identity["kind"]
    if kind == "directory":
        return stat.S_ISDIR(st.st_mode) and stat.S_IMODE(st.st_mode) == identity["mode"]
    if kind == "symlink":
        return stat.S_ISLNK(st.st_mode) and os.readlink(path) == identity["target"]
    return stat.S_ISREG(st.st_mode) and stat.S_IMODE(st.st_mode) == identity["mode"] and sha256_file(path) == identity["sha256"]


def _load_journal(journal: Path) -> list[str]:
    value = loads_strict(journal.read_bytes())
    require(isinstance(value, dict) and set(value) == {"schema_version", "completed"}, "CUTOVER_JOURNAL_INVALID", "cutover journal schema invalid")
    require(value["schema_version"] == 1 and isinstance(value["completed"], list), "CUTOVER_JOURNAL_INVALID", "cutover journal invalid")
    completed = value["completed"]
    require(all(isinstance(rel, str) for rel in completed) and len(completed) == len(set(completed)), "CUTOVER_JOURNAL_INVALID", "cutover journal completed set invalid")
    return list(completed)


def _write_journal(journal: Path, completed: list[str], *, create_only: bool = False) -> None:
    atomic_write(journal, canonical_json_bytes({"schema_version": 1, "completed": completed}), create_only=create_only)


def _copy_backup_atomic(target: Path, backup: Path) -> None:
    if backup.exists() or backup.is_symlink():
        return
    backup.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = backup.parent / f".{backup.name}.partial-{uuid.uuid4().hex}"
    try:
        if target.is_symlink():
            os.symlink(os.readlink(target), temp)
        elif target.is_dir():
            shutil.copytree(target, temp, symlinks=True)
        else:
            shutil.copy2(target, temp, follow_symlinks=False)
        os.rename(temp, backup)
    finally:
        if temp.is_symlink() or temp.is_file():
            temp.unlink(missing_ok=True)
        elif temp.is_dir():
            shutil.rmtree(temp)


def _remove_target(target: Path, rel: str) -> None:
    if target.is_dir() and not target.is_symlink():
        require(not any(target.iterdir()), "NONEMPTY_DIRECTORY_OPERATION", "cutover refuses to remove a nonempty directory", path=rel)
        target.rmdir()
    else:
        target.unlink()


def _install_after(target: Path, candidate: Path, after: dict[str, Any]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if after["kind"] == "directory":
        target.mkdir(exist_ok=True)
        os.chmod(target, after["mode"])
    elif after["kind"] == "symlink":
        os.symlink(after["target"], target)
    else:
        shutil.copy2(candidate, target, follow_symlinks=False)
        os.chmod(target, after["mode"])


def apply_manifest(*, source_repo: Path, final_candidate: Path, manifest: dict[str, Any], journal: Path, backup_root: Path) -> None:
    require(isinstance(manifest, dict) and manifest.get("schema_version") == 1 and isinstance(manifest.get("operations"), list), "CUTOVER_MANIFEST_INVALID", "cutover manifest invalid")
    backup_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    if journal.exists():
        completed = _load_journal(journal)
    else:
        completed = []
        _write_journal(journal, completed, create_only=True)
    completed_set = set(completed)
    operations = manifest["operations"]
    delete_ops = sorted((op for op in operations if op["op"] == "delete"), key=lambda x: x["path"].count("/"), reverse=True)
    chmod_ops = sorted((op for op in operations if op["op"] == "chmod"), key=lambda x: x["path"].count("/"))
    write_ops = sorted((op for op in operations if op["op"] in {"create", "replace"}), key=lambda x: x["path"].count("/"))
    ordered = [*delete_ops, *write_ops, *chmod_ops]
    require(len({op["path"] for op in ordered}) == len(ordered), "CUTOVER_MANIFEST_INVALID", "duplicate cutover path")
    for op in ordered:
        rel = safe_relpath(op["path"])
        target = source_repo / rel
        candidate = final_candidate / rel
        before = op.get("before")
        after = op.get("after")
        if rel in completed_set:
            require(_matches(target, after), "CONTROL_STATE_FAILED", "completed cutover path no longer matches target state", path=rel)
            continue
        if _matches(target, after):
            completed.append(rel)
            completed_set.add(rel)
            _write_journal(journal, completed)
            continue
        backup = backup_root / rel
        target_present = target.exists() or target.is_symlink()
        if target_present:
            require(_matches(target, before), "CONTROL_STATE_FAILED", "source path in unexpected third state", path=rel)
            if op["op"] == "chmod":
                os.chmod(target, after["mode"])
            else:
                if before is not None:
                    _copy_backup_atomic(target, backup)
                _remove_target(target, rel)
                if after is not None:
                    _install_after(target, candidate, after)
        else:
            if op["op"] == "create" and before is None:
                _install_after(target, candidate, after)
            else:
                # Valid interruption point: original was durably backed up and removed,
                # but the replacement/journal update was not yet completed.
                require(op["op"] != "chmod" and before is not None and (backup.exists() or backup.is_symlink()), "CONTROL_STATE_FAILED", "source path absent without recoverable cutover prefix", path=rel)
                if after is not None:
                    _install_after(target, candidate, after)
        require(_matches(target, after), "CONTROL_STATE_FAILED", "cutover operation did not reach intended state", path=rel)
        completed.append(rel)
        completed_set.add(rel)
        _write_journal(journal, completed)
