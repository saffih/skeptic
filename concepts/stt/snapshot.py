from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path
from typing import Any, Iterable

from .boundary import validate_path_collisions
from .canonical import canonical_json_bytes, safe_relpath, sha256_bytes, sha256_file
from .errors import STTError, require
from .gitutil import nul_list, run_git


def _safe_source_object(path: Path, rel: str) -> dict[str, Any]:
    st = os.lstat(path)
    mode = stat.S_IMODE(st.st_mode)
    require(not (mode & 0o7000), "UNSUPPORTED_METADATA", "special mode bits are unsupported", path=rel)
    require(st.st_uid == os.geteuid(), "UNSUPPORTED_METADATA", "source object owner mismatch", path=rel)
    xattrs: list[str] = []
    if hasattr(os, "listxattr"):
        try:
            xattrs = os.listxattr(path, follow_symlinks=False)
        except OSError as exc:
            raise STTError("HOST_CAPABILITY_UNAVAILABLE", f"cannot inspect xattrs: {rel}") from exc
    entry: dict[str, Any] = {"path": rel, "mode": mode, "uid": st.st_uid, "gid": st.st_gid, "nlink": st.st_nlink, "xattrs": sorted(xattrs)}
    if stat.S_ISREG(st.st_mode):
        entry.update({"kind": "file", "size": st.st_size, "sha256": sha256_file(path)})
    elif stat.S_ISDIR(st.st_mode):
        entry.update({"kind": "directory", "size": 0})
    elif stat.S_ISLNK(st.st_mode):
        target = os.readlink(path)
        entry.update({"kind": "symlink", "size": len(target.encode("utf-8", "surrogateescape")), "target": target, "target_sha256": sha256_bytes(target.encode("utf-8", "surrogateescape"))})
    else:
        raise STTError("UNSUPPORTED_OBJECT_TYPE", f"unsupported source object: {rel}")
    return entry


def _copy_entry(source: Path, destination: Path, entry: dict[str, Any]) -> None:
    kind = entry["kind"]
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    if kind == "directory":
        destination.mkdir(exist_ok=True)
        os.chmod(destination, entry["mode"])
    elif kind == "file":
        with source.open("rb") as src, destination.open("xb") as dst:
            shutil.copyfileobj(src, dst, 1024 * 1024)
            dst.flush(); os.fsync(dst.fileno())
        os.chmod(destination, entry["mode"])
    elif kind == "symlink":
        os.symlink(entry["target"], destination)


def nested_repository_roots(repo: Path) -> set[str]:
    roots: set[str] = set()
    for base, dirs, files in os.walk(repo, topdown=True, followlinks=False):
        base_path = Path(base)
        rel_base = base_path.relative_to(repo).as_posix()
        if rel_base in {".", ""}:
            dirs[:] = [name for name in dirs if name != ".git"]
        if ".git" in dirs or ".git" in files:
            if rel_base not in {".", ""}:
                roots.add(rel_base)
            if ".git" in dirs:
                dirs.remove(".git")
        dirs.sort()
    raw = run_git(repo, ["ls-files", "--stage", "-z"]).stdout
    for record in raw.split(b"\0"):
        if not record:
            continue
        meta, _, path = record.partition(b"\t")
        if meta.split(b" ", 1)[0] == b"160000":
            roots.add(path.decode("utf-8", "strict"))
    return roots


def _under_any(rel: str, roots: set[str]) -> bool:
    return any(rel == root or rel.startswith(root.rstrip("/") + "/") for root in roots)


def source_path_sets(repo: Path, included_ignored: Iterable[str]) -> tuple[set[str], set[str], set[str]]:
    tracked = set(nul_list(repo, ["ls-files", "-z", "--cached"]))
    untracked = set(nul_list(repo, ["ls-files", "-z", "--others", "--exclude-standard"]))
    ignored = set(nul_list(repo, ["ls-files", "-z", "--others", "-i", "--exclude-standard"]))
    included: set[str] = set()
    for raw in included_ignored:
        rel = safe_relpath(raw)
        for candidate in ignored:
            if candidate == rel or candidate.startswith(rel.rstrip("/") + "/"):
                included.add(candidate)
    private = {path for path in tracked | untracked | included if path == ".stt" or path.startswith(".stt/")}
    return tracked - private, untracked - private, included - private


def _git_bool(repo: Path, key: str) -> bool:
    result = run_git(repo, ["config", "--bool", "--get", key], check=False)
    if result.returncode != 0:
        return False
    return result.stdout.decode("utf-8", "strict").strip().lower() == "true"


def build_snapshot(repo: Path, destination: Path, included_ignored: list[str]) -> dict[str, Any]:
    require(not destination.exists(), "SNAPSHOT_EXISTS", "snapshot destination already exists")
    destination.mkdir(parents=True, mode=0o700)
    preserved_workspace = destination / "preserved_workspace"
    execution_workspace = destination / "execution_workspace"
    preserved_workspace.mkdir(mode=0o700); execution_workspace.mkdir(mode=0o700)
    tracked, untracked, included = source_path_sets(repo, included_ignored)
    nested_roots = nested_repository_roots(repo)
    execution_files = {rel for rel in tracked | untracked | included if not _under_any(rel, nested_roots)}
    execution_dirs: set[str] = set()
    for rel in execution_files:
        parent = Path(rel).parent
        while parent.as_posix() not in {".", ""}:
            execution_dirs.add(parent.as_posix()); parent = parent.parent

    all_entries: list[dict[str, Any]] = []
    for base, dirs, files in os.walk(repo, topdown=True, followlinks=False):
        base_path = Path(base)
        rel_base = base_path.relative_to(repo).as_posix()
        if rel_base in {".", ""}:
            dirs[:] = sorted(name for name in dirs if name not in {".git", ".stt"})
        else:
            dirs.sort()
        files.sort()
        for name in [*dirs, *files]:
            source = base_path / name
            rel = source.relative_to(repo).as_posix()
            if rel == ".git" or rel.startswith(".git/") or rel == ".stt" or rel.startswith(".stt/"):
                continue
            try:
                rel.encode("utf-8", "strict")
            except UnicodeEncodeError as exc:
                raise STTError("NON_UTF8_PATH", f"non-UTF-8 path: {rel!r}") from exc
            entry = _safe_source_object(source, rel)
            all_entries.append(entry)
            _copy_entry(source, preserved_workspace / rel, entry)

    ignore_case = _git_bool(repo, "core.ignorecase")
    precompose_unicode = _git_bool(repo, "core.precomposeunicode")
    validate_path_collisions((entry["path"] for entry in all_entries), ignore_case=ignore_case)
    by_path = {entry["path"]: entry for entry in all_entries}
    execution_paths = sorted(execution_dirs | execution_files, key=lambda value: (value.count("/"), value))
    execution_entries: list[dict[str, Any]] = []
    for rel in execution_paths:
        entry = by_path.get(rel)
        if entry is None:
            continue
        if entry["kind"] == "directory" or rel in execution_files:
            _copy_entry(repo / rel, execution_workspace / rel, entry)
            execution_entries.append(entry)

    status = run_git(repo, ["status", "--porcelain=v2", "-z", "--branch"]).stdout.hex()
    head = run_git(repo, ["rev-parse", "HEAD"]).stdout.decode().strip()
    branch_proc = run_git(repo, ["symbolic-ref", "--short", "-q", "HEAD"], check=False)
    branch = branch_proc.stdout.decode().strip() if branch_proc.returncode == 0 else None
    index = sha256_bytes(run_git(repo, ["ls-files", "--stage", "-z"]).stdout)
    manifest = {
        "schema_version": 1,
        "repo": str(repo),
        "head": head,
        "branch": branch,
        "index_tree": index,
        "porcelain_v2_hex": status,
        "included_ignored_paths": sorted(included_ignored),
        "git_path_policy": {"ignore_case": ignore_case, "precompose_unicode": precompose_unicode},
        "nested_repository_roots": sorted(nested_roots),
        "all_entries": all_entries,
        "execution_entries": execution_entries,
        "ignored_private_count": max(0, len(all_entries) - len(execution_entries)),
    }
    manifest_bytes = canonical_json_bytes(manifest)
    (destination / "manifest.json").write_bytes(manifest_bytes)
    return {**manifest, "manifest_sha256": sha256_bytes(manifest_bytes)}


def verify_source_identity(repo: Path, manifest: dict[str, Any]) -> None:
    expected = {entry["path"]: entry for entry in manifest["all_entries"]}
    actual: dict[str, dict[str, Any]] = {}
    for base, dirs, files in os.walk(repo, topdown=True, followlinks=False):
        base_path = Path(base)
        rel_base = base_path.relative_to(repo).as_posix()
        if rel_base in {".", ""}:
            dirs[:] = sorted(name for name in dirs if name not in {".git", ".stt"})
        else:
            dirs.sort()
        files.sort()
        for name in [*dirs, *files]:
            path = base_path / name
            rel = path.relative_to(repo).as_posix()
            if rel == ".git" or rel.startswith(".git/") or rel == ".stt" or rel.startswith(".stt/"):
                continue
            actual[rel] = _safe_source_object(path, rel)
    require(set(actual) == set(expected), "SOURCE_DRIFT", "source path set changed before cutover")
    for rel in sorted(expected):
        left, right = expected[rel], actual[rel]
        comparable = {key: left[key] for key in left if key not in {"uid", "gid", "nlink", "xattrs"}}
        current = {key: right[key] for key in right if key not in {"uid", "gid", "nlink", "xattrs"}}
        require(comparable == current, "SOURCE_DRIFT", "source object changed before cutover", path=rel)
    status = run_git(repo, ["status", "--porcelain=v2", "-z", "--branch"]).stdout.hex()
    head = run_git(repo, ["rev-parse", "HEAD"]).stdout.decode().strip()
    branch_proc = run_git(repo, ["symbolic-ref", "--short", "-q", "HEAD"], check=False)
    branch = branch_proc.stdout.decode().strip() if branch_proc.returncode == 0 else None
    index = sha256_bytes(run_git(repo, ["ls-files", "--stage", "-z"]).stdout)
    require(status == manifest["porcelain_v2_hex"] and head == manifest["head"] and branch == manifest["branch"] and index == manifest["index_tree"], "SOURCE_DRIFT", "Git observations changed before cutover")
