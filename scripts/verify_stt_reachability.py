#!/usr/bin/env python3
from __future__ import annotations

import os
import re
import sys
from pathlib import Path


ACTIVE_ROOTS = (
    Path("concepts/stt"),
    Path("adapters"),
    Path("scripts/stt.py"),
    Path("scripts/target_task.py"),
    Path("scripts/generic_host_smoke.py"),
    Path("scripts/probe_stt_sandbox.py"),
    Path("scripts/verify_stt_reachability.py"),
    Path("workflows/target_task.md"),
    Path("AGENTS.md"),
    Path("CLAUDE.md"),
    Path(".claude/agents"),
    Path(".github/workflows/target-task-tests.yml"),
)
TEXT_SUFFIXES = {".py", ".md", ".yml", ".yaml", ".sh"}
FORBIDDEN_PATTERNS = {
    "legacy Target Task import": re.compile(r"(?:concepts\.target_task|from\s+\.\.target_task|from\s+concepts\s+import\s+target_task)"),
    "repository tools/stt runner": re.compile(r"tools[./]stt[./]stt\.py"),
    "obsolete state reducer": re.compile(r"(?:concepts\.stt\.state|from\s+\.state\s+import)"),
    "metadata-preserving copy": re.compile(r"shutil\.copy2\s*\("),
    "unqualified macOS sandbox": re.compile(r"macos-seatbelt"),
    "historical adapter dispatch compatibility": re.compile(r"(?:DispatchRequest|build_dispatch_request|report_outcome)"),
}
OBSOLETE_FILES = {
    Path("concepts/stt/state.py"),
    Path("concepts/stt/snapshot.py"),
    Path("concepts/stt/cutover.py"),
}


def active_files() -> list[Path]:
    result: list[Path] = []
    for root in ACTIVE_ROOTS:
        if root.is_file():
            result.append(root)
            continue
        if not root.is_dir():
            continue
        for base, dirs, files in os.walk(root):
            dirs[:] = [name for name in dirs if name not in {"__pycache__", ".git"}]
            for name in files:
                path = Path(base) / name
                if path.suffix in TEXT_SUFFIXES and (root != Path(".claude/agents") or path.name.startswith("stt-")):
                    result.append(path)
    return sorted(set(result))


def main() -> int:
    failures: list[str] = []
    if not Path("scripts/stt.py").is_file() or not Path("concepts/stt").is_dir():
        failures.append("repository-native STT runtime is missing")
    for obsolete in sorted(OBSOLETE_FILES):
        if obsolete.exists():
            failures.append(f"obsolete active implementation exists: {obsolete}")
    for path in active_files():
        if path == Path("scripts/verify_stt_reachability.py"):
            continue
        try:
            source = path.read_text("utf-8")
        except UnicodeDecodeError:
            failures.append(f"{path}: active source is not UTF-8")
            continue
        for description, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(source):
                failures.append(f"{path}: {description}")
    runner = Path("concepts/stt/runner.py").read_text("utf-8")
    if ".adopt_existing(" in runner:
        failures.append("concepts/stt/runner.py: mutable provider artifact adoption remains reachable")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"STT_REACHABILITY_PASS active_files={len(active_files())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
