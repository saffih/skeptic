from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Sequence

from .errors import STTError, require


def run_git(repo: Path, args: Sequence[str], *, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LANG": "C", "LC_ALL": "C", "GIT_OPTIONAL_LOCKS": "0"}
    proc = subprocess.run(["git", "-C", str(repo), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, check=False)
    if check and proc.returncode != 0:
        raise STTError("GIT_READ_FAILED", proc.stderr.decode("utf-8", "replace"), {"args": list(args), "returncode": proc.returncode})
    return proc


def resolve_repo(repo: Path) -> tuple[Path, Path]:
    root = Path(run_git(repo, ["rev-parse", "--show-toplevel"]).stdout.decode().strip()).resolve(strict=True)
    common_raw = run_git(root, ["rev-parse", "--git-common-dir"]).stdout.decode().strip()
    common = (root / common_raw).resolve(strict=True) if not Path(common_raw).is_absolute() else Path(common_raw).resolve(strict=True)
    require(root != common and common not in root.parents, "INVALID_REPOSITORY", "workspace and Git common directory identity invalid")
    return root, common


def nul_list(repo: Path, args: Sequence[str]) -> list[str]:
    out = run_git(repo, args).stdout
    if not out:
        return []
    return [item.decode("utf-8", "strict") for item in out.split(b"\0") if item]
