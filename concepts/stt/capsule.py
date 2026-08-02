from __future__ import annotations

import os
import stat
import tempfile
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any

from .boundary import scope_contains, scope_overlaps_nested, validate_path_collisions
from .canonical import fsync_dir, safe_relpath, sha256_file
from .errors import STTError, require


def validate_workspace_target(
    workspace: Path,
    relative_path: str,
    *,
    allow_leaf_symlink_delete: bool = False,
    nested_roots: tuple[str, ...] = (),
) -> Path:
    """Validate one lexical workspace target without following its path."""
    rel = safe_relpath(relative_path)
    overlap = scope_overlaps_nested(rel, nested_roots)
    require(overlap is None, "NESTED_REPOSITORY_SCOPE_FORBIDDEN", "target overlaps nested repository or submodule", path=rel, nested_root=overlap)
    root = Path(os.path.abspath(os.fspath(workspace)))
    root_stat = os.lstat(root)
    require(stat.S_ISDIR(root_stat.st_mode) and not stat.S_ISLNK(root_stat.st_mode), "WORKSPACE_ROOT_INVALID", "workspace root must be a real directory")
    target = root.joinpath(*rel.split("/"))
    require(os.path.commonpath((os.fspath(root), os.fspath(target))) == os.fspath(root), "WORKSPACE_PATH_ESCAPE", "workspace target escapes root", path=rel)
    current = root
    components = rel.split("/")
    for index, component in enumerate(components):
        aliases = [
            name
            for name in os.listdir(current)
            if unicodedata.normalize("NFC", name).casefold() == unicodedata.normalize("NFC", component).casefold()
        ]
        require(not aliases or aliases == [component], "PATH_ALIAS_COLLISION", "workspace path casing or Unicode form is not exact", path=rel, component=component, aliases=aliases)
        current = current / component
        if index == len(components) - 1:
            break
        try:
            current_stat = os.lstat(current)
        except FileNotFoundError:
            break
        require(not stat.S_ISLNK(current_stat.st_mode), "WORKSPACE_SYMLINK_PARENT", "workspace target has a symlink parent", path=rel)
        require(stat.S_ISDIR(current_stat.st_mode), "WORKSPACE_PARENT_INVALID", "workspace target parent is not a directory", path=rel)
    try:
        leaf_stat = os.lstat(current)
    except FileNotFoundError:
        return target
    require(
        not stat.S_ISLNK(leaf_stat.st_mode) or allow_leaf_symlink_delete,
        "WORKSPACE_SYMLINK_LEAF",
        "workspace symlink leaf may only be deleted directly",
        path=rel,
    )
    return target


def object_identity(path: Path, rel: str, *, max_single_file_bytes: int, allow_symlink: bool = True) -> dict[str, Any]:
    try:
        value = os.lstat(path)
    except FileNotFoundError:
        return {"path": rel, "state": "missing"}
    mode = stat.S_IMODE(value.st_mode)
    require(value.st_uid == os.geteuid(), "UNSUPPORTED_METADATA", "object owner mismatch", path=rel)
    require(value.st_mode & 0o7000 == 0, "UNSUPPORTED_METADATA", "object has special mode bits", path=rel)
    if stat.S_ISREG(value.st_mode):
        require(value.st_nlink == 1, "UNSUPPORTED_METADATA", "hard-linked files are unsupported", path=rel)
        require(value.st_size <= max_single_file_bytes, "SINGLE_FILE_LIMIT", "single-file byte limit exceeded", path=rel, size=value.st_size)
        return {"path": rel, "state": "file", "sha256": sha256_file(path), "size": value.st_size, "mode": mode}
    if stat.S_ISDIR(value.st_mode):
        return {"path": rel, "state": "directory", "mode": mode}
    if stat.S_ISLNK(value.st_mode):
        require(allow_symlink, "UNSUPPORTED_SYMLINK_DELTA", "Worker-created or Worker-modified symlinks are unsupported", path=rel)
        target = os.readlink(path)
        return {"path": rel, "state": "symlink", "target": target, "size": value.st_size, "mode": mode}
    raise STTError("UNSUPPORTED_OBJECT_TYPE", "unsupported filesystem object", {"path": rel})


def _scope_ancestors(scope: list[dict[str, str]]) -> set[str]:
    ancestors: set[str] = set()
    for item in scope:
        path = PurePosixPath(item["path"])
        ancestors.update(parent.as_posix() for parent in path.parents if parent.as_posix() != ".")
    return ancestors


def _existing_scope_paths(workspace: Path, scope: list[dict[str, str]], nested_roots: tuple[str, ...]) -> set[str]:
    selected: set[str] = set()
    for item in scope:
        rel = safe_relpath(item["path"])
        overlap = scope_overlaps_nested(rel, nested_roots)
        require(overlap is None, "NESTED_REPOSITORY_SCOPE_FORBIDDEN", "scope overlaps nested repository or submodule", scope=rel, nested_root=overlap)
        target = validate_workspace_target(workspace, rel, allow_leaf_symlink_delete=True, nested_roots=nested_roots)
        if not target.exists() and not target.is_symlink():
            continue
        selected.add(rel)
        if item["kind"] == "file":
            continue
        require(target.is_dir() and not target.is_symlink(), "PLAN_SCOPE_TYPE", "tree scope must name a real directory", path=rel)
        for base, dirs, files in os.walk(target, topdown=True, followlinks=False):
            current = Path(base)
            dirs[:] = [name for name in dirs if name not in {".git", ".stt"}]
            files[:] = [name for name in files if name not in {".git", ".stt"}]
            for name in dirs + files:
                child = current / name
                child_rel = child.relative_to(workspace).as_posix()
                safe_relpath(child_rel)
                overlap = scope_overlaps_nested(child_rel, nested_roots)
                require(overlap is None, "NESTED_REPOSITORY_SCOPE_FORBIDDEN", "scope reaches nested repository or submodule", scope=rel, nested_root=overlap)
                selected.add(child_rel)
    return selected


def prepare_capsule_admission(
    workspace: Path,
    read_scope: list[dict[str, str]],
    write_scope: list[dict[str, str]],
    *,
    nested_roots: tuple[str, ...],
    limits: dict[str, int],
) -> dict[str, Any]:
    selected = _existing_scope_paths(workspace, [*read_scope, *write_scope], nested_roots)
    for ancestor in _scope_ancestors([*read_scope, *write_scope]):
        path = workspace / ancestor
        if path.exists() and not path.is_symlink():
            selected.add(ancestor)
    identities = [object_identity(workspace / rel, rel, max_single_file_bytes=limits["max_single_file_bytes"]) for rel in sorted(selected)]
    by_path = {item["path"]: item for item in identities}
    for item in write_scope:
        by_path.setdefault(item["path"], {"path": item["path"], "state": "missing"})
    write_paths = sorted(rel for rel in by_path if scope_contains(write_scope, rel))
    validate_path_collisions(write_paths, ignore_case=True)
    read_bytes = sum(item.get("size", 0) for item in identities if scope_contains(read_scope, item["path"]) and item["state"] == "file")
    capsule_bytes = sum(item.get("size", 0) for item in identities if item["state"] == "file")
    require(read_bytes <= limits["max_read_scope_bytes_per_step"], "READ_SCOPE_BYTE_LIMIT", "read-scope byte limit exceeded", size=read_bytes)
    require(capsule_bytes <= limits["max_capsule_bytes_per_step"], "CAPSULE_BYTE_LIMIT", "capsule byte limit exceeded", size=capsule_bytes)
    require(len(identities) <= limits["max_capsule_entries_per_step"], "CAPSULE_ENTRY_LIMIT", "capsule entry limit exceeded", entries=len(identities))
    return {
        "schema_version": 1,
        "selected_paths": sorted(selected),
        "admitted_paths": identities,
        "write_baseline": [by_path[rel] for rel in write_paths],
        "read_scope_bytes": read_bytes,
        "capsule_bytes": capsule_bytes,
        "capsule_entries": len(identities),
        "nested_repository_roots": list(nested_roots),
    }


def _copy_regular(source: Path, destination: Path, mode: int) -> None:
    source_fd = os.open(source, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        source_stat = os.fstat(source_fd)
        require(stat.S_ISREG(source_stat.st_mode), "UNSUPPORTED_OBJECT_TYPE", "capsule source is not regular")
        destination_fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
        try:
            while chunk := os.read(source_fd, 1024 * 1024):
                view = memoryview(chunk)
                while view:
                    written = os.write(destination_fd, view)
                    view = view[written:]
            os.fsync(destination_fd)
        finally:
            os.close(destination_fd)
    finally:
        os.close(source_fd)


def materialize_capsule(workspace: Path, capsule: Path, admission: dict[str, Any], write_scope: list[dict[str, str]]) -> None:
    require(not capsule.exists(), "CAPSULE_EXISTS", "capsule already exists")
    capsule.mkdir(parents=True, mode=0o700)
    identities = {item["path"]: item for item in admission["admitted_paths"]}
    for rel in sorted(admission["selected_paths"], key=lambda value: (value.count("/"), value)):
        source = workspace / rel
        destination = capsule / rel
        identity = identities[rel]
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if identity["state"] == "directory":
            destination.mkdir(exist_ok=True, mode=identity["mode"])
        elif identity["state"] == "file":
            _copy_regular(source, destination, identity["mode"])
        elif identity["state"] == "symlink":
            os.symlink(identity["target"], destination)
    write_ancestors = _scope_ancestors(write_scope)
    for base, dirs, files in os.walk(capsule, topdown=False, followlinks=False):
        for name in files + dirs:
            path = Path(base) / name
            if path.is_symlink():
                continue
            rel = path.relative_to(capsule).as_posix()
            mode = stat.S_IMODE(os.stat(path).st_mode)
            if scope_contains(write_scope, rel) or rel in write_ancestors:
                mode |= 0o200
                if path.is_dir():
                    mode |= 0o100
            else:
                mode &= ~0o222
            os.chmod(path, mode)


def _scan_capsule(capsule: Path, *, max_single: int, max_bytes: int, max_entries: int) -> dict[str, dict[str, Any]]:
    identities: dict[str, dict[str, Any]] = {}
    total = 0
    for base, dirs, files in os.walk(capsule, topdown=True, followlinks=False):
        controls = {".git", ".stt"}.intersection({*dirs, *files})
        require(not controls, "CONTROL_PATH_FORBIDDEN", "capsule contains Git or STT control state", paths=sorted(controls))
        for name in dirs + files:
            path = Path(base) / name
            rel = path.relative_to(capsule).as_posix()
            identity = object_identity(path, rel, max_single_file_bytes=max_single)
            identities[rel] = identity
            total += identity.get("size", 0) if identity["state"] == "file" else 0
            require(len(identities) <= max_entries, "CAPSULE_ENTRY_LIMIT", "capsule entry limit exceeded")
            require(total <= max_bytes, "CAPSULE_BYTE_LIMIT", "capsule byte limit exceeded")
    validate_path_collisions(identities, ignore_case=True)
    return identities


def derive_delta(admission: dict[str, Any], capsule: Path, write_scope: list[dict[str, str]], limits: dict[str, int]) -> list[dict[str, Any]]:
    require(isinstance(admission, dict) and admission.get("schema_version") == 1, "CAPSULE_ADMISSION_INVALID", "capsule admission manifest invalid")
    baseline = {item["path"]: item for item in admission["admitted_paths"]}
    write_baseline = {item["path"]: item for item in admission["write_baseline"]}
    final = _scan_capsule(
        capsule,
        max_single=limits["max_single_file_bytes"],
        max_bytes=limits["max_capsule_bytes_per_step"],
        max_entries=limits["max_capsule_entries_per_step"],
    )
    for rel in set(baseline) | set(final):
        if scope_contains(write_scope, rel):
            continue
        require(baseline.get(rel) == final.get(rel), "WRITE_SCOPE_VIOLATION", "capsule changed a path outside write scope", path=rel)
    candidate_paths = {rel for rel in write_baseline} | {rel for rel in final if scope_contains(write_scope, rel)}
    validate_path_collisions(candidate_paths, ignore_case=True)
    delta: list[dict[str, Any]] = []
    for rel in sorted(candidate_paths):
        before = write_baseline.get(rel, {"path": rel, "state": "missing"})
        after = final.get(rel, {"path": rel, "state": "missing"})
        if before == after:
            continue
        if after["state"] == "symlink":
            raise STTError("UNSUPPORTED_SYMLINK_DELTA", "Worker-created or Worker-modified symlinks are unsupported", {"path": rel})
        if before["state"] == "symlink" and after["state"] != "missing":
            raise STTError("UNSUPPORTED_SYMLINK_DELTA", "Worker-created or Worker-modified symlinks are unsupported", {"path": rel})
        operation = "delete" if after["state"] == "missing" else after["state"]
        delta.append({"path": rel, "op": operation, "before": before, "after": after})
    require(len(delta) <= limits["max_changed_paths_per_step"], "CHANGED_PATH_LIMIT", "Worker delta exceeds changed-path limit")
    return delta


def _atomic_install_file(source: Path, target: Path, expected: dict[str, Any]) -> None:
    require(target.parent.is_dir() and not target.parent.is_symlink(), "WORKSPACE_PARENT_INVALID", "file target parent is unavailable")
    fd, raw_tmp = tempfile.mkstemp(prefix=f".{target.name}.stt-", dir=target.parent)
    temporary = Path(raw_tmp)
    try:
        source_fd = os.open(source, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            while chunk := os.read(source_fd, 1024 * 1024):
                view = memoryview(chunk)
                while view:
                    written = os.write(fd, view)
                    view = view[written:]
        finally:
            os.close(source_fd)
        os.fchmod(fd, expected["mode"])
        os.fsync(fd)
        os.close(fd)
        fd = -1
        require(sha256_file(temporary) == expected["sha256"] and temporary.stat().st_size == expected["size"], "DELTA_SOURCE_CHANGED", "temporary installation bytes mismatch")
        os.replace(temporary, target)
        fsync_dir(target.parent)
    finally:
        if fd >= 0:
            os.close(fd)
        if temporary.exists():
            temporary.unlink()


def apply_delta(
    workspace: Path,
    capsule: Path,
    delta: list[dict[str, Any]],
    write_scope: list[dict[str, str]],
    *,
    max_single_file_bytes: int,
    nested_roots: tuple[str, ...] = (),
) -> None:
    """Apply one validated direct delta with atomic per-file replacement and no rollback."""
    validated: list[tuple[dict[str, Any], str, Path, Path | None]] = []
    seen: set[str] = set()
    for item in delta:
        require(isinstance(item, dict) and set(item) == {"path", "op", "before", "after"}, "DELTA_SCHEMA", "delta item schema invalid")
        rel = safe_relpath(item["path"])
        require(rel not in seen, "DUPLICATE_DELTA_PATH", "delta path is duplicated", path=rel)
        seen.add(rel)
        require(scope_contains(write_scope, rel), "WRITE_SCOPE_VIOLATION", "delta path outside write scope", path=rel)
        operation = item["op"]
        require(operation in {"delete", "file", "directory"}, "UNSUPPORTED_OBJECT_TYPE", "unsupported delta operation", op=operation)
        target = validate_workspace_target(workspace, rel, allow_leaf_symlink_delete=operation == "delete", nested_roots=nested_roots)
        current = object_identity(target, rel, max_single_file_bytes=max_single_file_bytes)
        require(current == item["before"], "WORKSPACE_PRECONDITION_CHANGED", "workspace target no longer matches admitted before identity", path=rel)
        source: Path | None = None
        if operation != "delete":
            source = validate_workspace_target(capsule, rel, allow_leaf_symlink_delete=True)
            after = object_identity(source, rel, max_single_file_bytes=max_single_file_bytes, allow_symlink=False)
            require(after == item["after"], "DELTA_SOURCE_CHANGED", "capsule source no longer matches derived after identity", path=rel)
            require(after["state"] == operation, "DELTA_SCHEMA", "delta operation and after identity disagree", path=rel)
        validated.append((item, rel, target, source))
    validate_path_collisions(seen, ignore_case=True)

    for item, rel, target, _ in sorted(validated, key=lambda value: value[1].count("/"), reverse=True):
        if item["op"] != "delete":
            continue
        if item["before"]["state"] == "directory":
            try:
                target.rmdir()
            except OSError as exc:
                raise STTError("NONEMPTY_DIRECTORY_OPERATION", "delta refuses to remove a nonempty directory", {"path": rel}) from exc
            fsync_dir(target.parent)
        elif item["before"]["state"] != "missing":
            target.unlink()
            fsync_dir(target.parent)
    for item, rel, target, source in sorted(validated, key=lambda value: value[1].count("/")):
        if item["op"] == "delete":
            continue
        require(source is not None, "CONTROL_STATE_FAILED", "validated delta source missing", path=rel)
        if item["op"] == "directory":
            if item["before"]["state"] == "missing":
                target.mkdir(mode=item["after"]["mode"])
                os.chmod(target, item["after"]["mode"])
            else:
                require(target.is_dir() and not target.is_symlink(), "UNSUPPORTED_OBJECT_TYPE", "directory replacement requires an existing directory", path=rel)
                os.chmod(target, item["after"]["mode"])
            fsync_dir(target.parent)
        else:
            require(item["before"]["state"] in {"missing", "file"}, "UNSUPPORTED_OBJECT_TYPE", "atomic file replacement supports only missing or regular-file targets", path=rel)
            _atomic_install_file(source, target, item["after"])
