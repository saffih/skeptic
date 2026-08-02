from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path
from typing import Any

from .canonical import sha256_file
from .errors import require


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
