from __future__ import annotations

import fcntl
import hashlib
import os
import stat
from dataclasses import dataclass
from pathlib import Path

from .canonical import ensure_no_symlink_components
from .errors import STTError, require


def lock_root(task_root: Path) -> Path:
    """Return the task-state-local lock directory.

    All coordination is intentionally local to one explicit state root.  This
    keeps the MVP portable, avoids host-global paths, and still serializes all
    tasks that share that state root.
    """
    task_root = task_root.resolve(strict=True)
    state_root = task_root.parent
    root = state_root / ".locks"
    require(root.parent == state_root, "LOCK_ROOT_UNSAFE", "lock root escaped state root")
    ensure_no_symlink_components(state_root)
    root.mkdir(parents=False, exist_ok=True, mode=0o700)
    os.chmod(root, 0o700)
    ensure_no_symlink_components(root)
    st = os.lstat(root)
    require(
        stat.S_ISDIR(st.st_mode) and st.st_uid == os.geteuid() and stat.S_IMODE(st.st_mode) == 0o700,
        "LOCK_ROOT_UNSAFE",
        "local lock root is not an owner-only directory",
    )
    return root


def workspace_key(git_common_dir: Path) -> str:
    canonical = git_common_dir.resolve(strict=True)
    st = os.stat(canonical)
    body = f"{canonical}\0{st.st_dev}\0{st.st_ino}".encode()
    return hashlib.sha256(body).hexdigest()


@dataclass(slots=True)
class Lease:
    path: Path
    busy_code: str
    fd: int | None = None

    def __enter__(self) -> "Lease":
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            os.close(self.fd)
            self.fd = None
            raise STTError(self.busy_code, f"lease busy: {self.path}") from exc
        os.ftruncate(self.fd, 0)
        os.write(self.fd, f"pid={os.getpid()}\n".encode())
        os.fsync(self.fd)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            self.fd = None
