from __future__ import annotations

import os
import shutil
import stat
import uuid
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

    @classmethod
    def from_dict(cls, value: Any) -> "ArtifactRef":
        require(isinstance(value, dict) and set(value) == {"ref", "sha256", "size"}, "ARTIFACT_REF_INVALID", "artifact reference schema invalid")
        require(isinstance(value["ref"], str) and isinstance(value["sha256"], str) and len(value["sha256"]) == 64, "ARTIFACT_REF_INVALID", "artifact reference identity invalid")
        require(type(value["size"]) is int and value["size"] >= 0, "ARTIFACT_REF_INVALID", "artifact reference size invalid")
        return cls(value["ref"], value["sha256"], value["size"])


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
        ensure_no_symlink_components(path, include_leaf=False)
        return path

    def _read_owned_regular(self, ref: str, *, max_size: int | None = None) -> tuple[Path, bytes, os.stat_result]:
        path = self.resolve(ref)
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(path, flags)
        except (FileNotFoundError, NotADirectoryError) as exc:
            raise STTError("ARTIFACT_MISSING", f"artifact missing: {ref}") from exc
        except OSError as exc:
            raise STTError("ARTIFACT_NOT_REGULAR", f"artifact is unsafe: {ref}") from exc
        try:
            before = os.fstat(fd)
            require(stat.S_ISREG(before.st_mode), "ARTIFACT_NOT_REGULAR", f"artifact is not a regular file: {ref}")
            require(before.st_uid == os.geteuid(), "ARTIFACT_OWNER_MISMATCH", f"artifact owner mismatch: {ref}")
            require(before.st_nlink == 1, "ARTIFACT_HARDLINK", f"artifact has unexpected hard links: {ref}")
            require(before.st_mode & 0o7000 == 0 and before.st_mode & 0o022 == 0, "ARTIFACT_MODE_UNSAFE", f"artifact mode is not owner-controlled: {ref}")
            if max_size is not None:
                require(before.st_size <= max_size, "ARTIFACT_TOO_LARGE", f"artifact exceeds trusted limit: {ref}")
            chunks: list[bytes] = []
            remaining = before.st_size
            while remaining:
                chunk = os.read(fd, min(1024 * 1024, remaining))
                require(bool(chunk), "ARTIFACT_CHANGED_DURING_READ", f"artifact truncated while read: {ref}")
                chunks.append(chunk)
                remaining -= len(chunk)
            require(os.read(fd, 1) == b"", "ARTIFACT_CHANGED_DURING_READ", f"artifact grew while read: {ref}")
            after = os.fstat(fd)
            require((before.st_dev, before.st_ino, before.st_size) == (after.st_dev, after.st_ino, after.st_size), "ARTIFACT_CHANGED_DURING_READ", f"artifact identity changed while read: {ref}")
            return path, b"".join(chunks), after
        finally:
            os.close(fd)

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

    def freeze_existing(self, ref: str, *, accepted_prefix: str, label: str, max_size: int) -> ArtifactRef:
        """Copy bounded staging bytes into a unique immutable trusted artifact."""
        safe_relpath(accepted_prefix)
        require(label and "/" not in label and "\\" not in label, "ARTIFACT_REF_INVALID", "accepted artifact label invalid")
        _, data, _ = self._read_owned_regular(ref, max_size=max_size)
        return self.publish_bytes(f"{accepted_prefix}/{uuid.uuid4().hex}-{label}", data)

    def verify(self, artifact: ArtifactRef) -> Path:
        path, data, st = self._read_owned_regular(artifact.ref, max_size=artifact.size)
        require(st.st_size == artifact.size, "ARTIFACT_SIZE_MISMATCH", f"artifact size mismatch: {artifact.ref}")
        require(sha256_bytes(data) == artifact.sha256, "ARTIFACT_HASH_MISMATCH", f"artifact hash mismatch: {artifact.ref}")
        return path
