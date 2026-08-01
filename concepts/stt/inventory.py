from __future__ import annotations

import os
import re
import shutil
import stat
from collections import Counter
from pathlib import Path
from typing import Any

from .canonical import sha256_file
from .errors import require


TARGET_PATTERNS = re.compile(r"target[_ -]?task|\bTT:\b|concepts/" + "target_task|scripts/" + "target_task", re.IGNORECASE)


def derive_inventory(checkpoint_workspace: Path, snapshot_manifest: dict[str, Any], *, max_scan_bytes: int = 32 * 1024 * 1024) -> dict[str, Any]:
    paths: list[dict[str, Any]] = []
    types: Counter[str] = Counter()
    references: list[dict[str, Any]] = []
    scanned = 0
    instructions: list[str] = []
    manifests: list[str] = []
    for base, dirs, files in os.walk(checkpoint_workspace, followlinks=False):
        dirs.sort(); files.sort()
        for name in files:
            path = Path(base) / name
            rel = path.relative_to(checkpoint_workspace).as_posix()
            st = os.lstat(path)
            kind = "symlink" if stat.S_ISLNK(st.st_mode) else "file"
            suffix = Path(rel).suffix.lower() or "<none>"
            types[suffix] += 1
            paths.append({"path": rel, "kind": kind, "size": st.st_size})
            if name in {"AGENTS.md", "CLAUDE.md", "skeptic.md", "skeptic-questions.md"} or rel.startswith("workflows/"):
                instructions.append(rel)
            if name in {"pyproject.toml", "requirements.txt", "package.json", "Cargo.toml", "go.mod", "Makefile"}:
                manifests.append(rel)
            if kind == "file" and st.st_size <= 2 * 1024 * 1024 and scanned + st.st_size <= max_scan_bytes:
                try:
                    body = path.read_text("utf-8")
                except (UnicodeDecodeError, OSError):
                    continue
                scanned += st.st_size
                if TARGET_PATTERNS.search(body) or TARGET_PATTERNS.search(rel):
                    references.append({"path": rel, "sha256": sha256_file(path), "size": st.st_size})
    return {
        "schema_version": 1,
        "baseline": {
            "head": snapshot_manifest["head"],
            "branch": snapshot_manifest["branch"],
            "index_tree": snapshot_manifest["index_tree"],
            "snapshot_sha256": snapshot_manifest["manifest_sha256"],
        },
        "paths": paths,
        "file_type_summary": dict(sorted(types.items())),
        "instruction_paths": sorted(instructions),
        "dependency_manifests": sorted(manifests),
        "target_task_references": sorted(references, key=lambda item: item["path"]),
        "limits": {"max_scanned_bytes": max_scan_bytes, "actual_scanned_bytes": scanned},
    }


def derive_toolchain() -> dict[str, Any]:
    candidates = {
        "python": "/usr/bin/python3" if Path("/usr/bin/python3").exists() else (shutil.which("python3") or shutil.which("python")),
        "git": shutil.which("git"),
        "bash": shutil.which("bash"),
        "unshare": shutil.which("unshare"),
        "mount": shutil.which("mount"),
        "sandbox-exec": shutil.which("sandbox-exec"),
    }
    tools: list[dict[str, Any]] = []
    for tool_id, raw in candidates.items():
        if not raw:
            continue
        path = Path(raw).resolve(strict=True)
        st = path.stat()
        require(stat.S_ISREG(st.st_mode) and os.access(path, os.X_OK), "TOOLCHAIN_INVALID", f"tool is not executable: {path}")
        policy: dict[str, Any] = {"forbid_inline_code": tool_id == "python", "forbid_network_publication": True}
        tools.append({"tool_id": tool_id, "path": str(path), "sha256": sha256_file(path), "device": st.st_dev, "inode": st.st_ino, "size": st.st_size, "policy": policy})
    return {"schema_version": 1, "tools": tools}
