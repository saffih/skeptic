from __future__ import annotations

import os
import shutil
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .canonical import atomic_write, canonical_json_bytes, ensure_no_symlink_components, safe_relpath, sha256_bytes, sha256_file
from .errors import STTError, require


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    ref: str
    sha256: str
    size: int

    def as_dict(self) -> dict[str, Any]:
        return {"ref": self.ref, "sha256": self.sha256, "size": self.size}


class ArtifactStore:
    def __init__(self, root: Path, *, max_bytes: int, min_free_reserve: int) -> None:
        self.root = root.resolve(strict=False)
        self.max_bytes = max_bytes
        self.min_free_reserve = min_free_reserve

    def initialize(self) -> None:
        ensure_no_symlink_components(self.root, include_leaf=False)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        st = os.lstat(self.root)
        require(stat.S_ISDIR(st.st_mode), "STATE_ROOT_UNSAFE", "state root is not a directory")
        require(st.st_uid == os.geteuid(), "STATE_ROOT_UNSAFE", "state root owner mismatch")
        mode = stat.S_IMODE(st.st_mode)
        if mode != 0o700:
            os.chmod(self.root, 0o700)
        ensure_no_symlink_components(self.root)

    def resolve(self, ref: str) -> Path:
        ref = safe_relpath(ref)
        path = self.root / ref
        resolved_parent = path.parent.resolve(strict=False)
        require(resolved_parent == self.root or self.root in resolved_parent.parents, "ARTIFACT_ESCAPE", "artifact escapes task root")
        return path

    def _usage(self) -> int:
        total = 0
        for base, dirs, files in os.walk(self.root, followlinks=False):
            for name in files:
                path = Path(base) / name
                try:
                    total += os.lstat(path).st_size
                except FileNotFoundError:
                    continue
        return total

    def admit(self, upper_bound: int) -> None:
        require(upper_bound >= 0, "INVALID_BUDGET", "negative artifact size")
        current = self._usage()
        require(current + upper_bound <= self.max_bytes, "TASK_STATE_BUDGET_EXHAUSTED", "task-state byte limit exceeded", current=current, requested=upper_bound)
        free = shutil.disk_usage(self.root).free
        require(free - upper_bound >= self.min_free_reserve, "TASK_STATE_BUDGET_EXHAUSTED", "free-space reserve would be violated", free=free, requested=upper_bound)

    def publish_bytes(self, ref: str, data: bytes, *, mode: int = 0o600) -> ArtifactRef:
        self.admit(len(data) + 4096)
        path = self.resolve(ref)
        atomic_write(path, data, mode=mode, create_only=True)
        return ArtifactRef(ref, sha256_bytes(data), len(data))

    def publish_json(self, ref: str, value: Any) -> ArtifactRef:
        return self.publish_bytes(ref, canonical_json_bytes(value))


    def adopt_existing(self, ref: str, *, max_size: int) -> ArtifactRef:
        path = self.resolve(ref)
        require(path.is_file() and not path.is_symlink(), "ARTIFACT_MISSING", f"artifact missing or unsafe: {ref}")
        st = os.lstat(path)
        require(st.st_uid == os.geteuid(), "ARTIFACT_OWNER_MISMATCH", f"artifact owner mismatch: {ref}")
        require(st.st_size <= max_size, "ARTIFACT_TOO_LARGE", f"artifact exceeds trusted limit: {ref}")
        return ArtifactRef(ref, sha256_file(path), st.st_size)

    def verify(self, artifact: ArtifactRef) -> Path:
        path = self.resolve(artifact.ref)
        require(path.is_file(), "ARTIFACT_MISSING", f"artifact missing: {artifact.ref}")
        require(path.stat().st_size == artifact.size, "ARTIFACT_SIZE_MISMATCH", f"artifact size mismatch: {artifact.ref}")
        require(sha256_file(path) == artifact.sha256, "ARTIFACT_HASH_MISMATCH", f"artifact hash mismatch: {artifact.ref}")
        return path
