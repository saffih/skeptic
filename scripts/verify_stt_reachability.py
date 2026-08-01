#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import sys
from pathlib import Path


EXECUTABLE_ROOTS = [Path("concepts"), Path("adapters"), Path("scripts"), Path("agents"), Path("workflows"), Path(".claude"), Path(".github"), Path("tests")]
FORBIDDEN = [re.compile(r"tools[./]stt[./]stt\.py"), re.compile(r"/Users/[^\s\"']+/skeptic")]
ALLOWED_PATHS = {"scripts/target_task.py", "scripts/verify_stt_reachability.py"}


def main() -> int:
    failures: list[str] = []
    if not Path("scripts/stt.py").is_file() or not Path("concepts/stt").is_dir(): failures.append("repository-native STT runtime is missing")
    for root in EXECUTABLE_ROOTS:
        if not root.exists(): continue
        for base, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git"}]
            for name in files:
                path = Path(base) / name; rel = path.as_posix()
                if rel in ALLOWED_PATHS or path.suffix not in {".py", ".md", ".yml", ".yaml", ".sh"}: continue
                try: text = path.read_text("utf-8")
                except UnicodeDecodeError: continue
                for pattern in FORBIDDEN:
                    if pattern.search(text): failures.append(f"{rel}: forbidden legacy reachability {pattern.pattern}")
    if failures:
        print("\n".join(failures), file=sys.stderr); return 1
    print("STT_REACHABILITY_PASS")
    return 0


if __name__ == "__main__": raise SystemExit(main())
