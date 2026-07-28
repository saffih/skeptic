#!/usr/bin/env python3
"""Validate BRANCH-INVENTORY.md against the current Git refs and worktrees."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT = Path(__file__).with_name("BRANCH-INVENTORY.md")
CLASSES = {
    "MAIN",
    "LOCAL_ONLY",
    "LOCAL_AND_REMOTE_EQUAL",
    "LOCAL_AND_REMOTE_DIVERGED",
    "REMOTE_ONLY",
}
RELATIONS = {"MAIN_HEAD", "ANCESTOR_OF_MAIN", "DESCENDANT_OF_MAIN", "DIVERGED_FROM_MAIN"}


def git(*args: str) -> list[str]:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).splitlines()


def refs(kind: str) -> dict[str, str]:
    prefix = "refs/heads" if kind == "local" else "refs/remotes/origin"
    strip = "2" if kind == "local" else "3"
    result = {}
    for line in git("for-each-ref", f"--format=%(refname:strip={strip}) %(objectname)", prefix):
        name, sha = line.split()
        if kind == "remote" and name == "HEAD":
            continue
        result[name] = sha
    return result


def worktrees() -> dict[str, tuple[str, str]]:
    result = {}
    path = head = branch = None
    for line in git("worktree", "list", "--porcelain") + [""]:
        if line.startswith("worktree "):
            path = line[9:]
            head = branch = None
        elif line.startswith("HEAD "):
            head = line[5:]
        elif line.startswith("branch "):
            branch = line[7:].removeprefix("refs/heads/")
        elif not line and path is not None:
            result[path] = (head, branch or "detached")
            path = None
    return result


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> int:
    text = REPORT.read_text()
    local = refs("local")
    remote = refs("remote")
    trees = worktrees()
    main_sha = local.get("main")
    if not main_sha:
        fail("local main is missing")
    snapshot_main = "c48010ce7da7af645c7ad9cef79e5c9a33f71cdc"

    section = text.split("## Branch records\n", 1)[-1].split("\n## Worktrees\n", 1)[0]
    rows = []
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        fields = [x.strip() for x in line.strip("|").split("|")]
        if len(fields) != 8:
            fail(f"malformed branch row: {line}")
        ref = fields[0].strip("`")
        rows.append((ref, fields[1], fields[2].strip("`"), fields[3].strip("`"), fields[4].strip("`"), fields[5], fields[6], fields[7]))

    expected = set(local) | set(remote)
    actual = {row[0] for row in rows}
    if actual != expected:
        fail(f"branch set mismatch: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    if len(rows) != len(actual):
        fail("duplicate branch rows")

    for ref, cls, sha, counterpart, tree, relation, ahead, behind in rows:
        if cls not in CLASSES:
            fail(f"{ref}: invalid class {cls}")
        if relation not in RELATIONS:
            fail(f"{ref}: invalid relation {relation}")
        expected_sha = snapshot_main if ref == "main" else local.get(ref, remote.get(ref))
        if sha != expected_sha:
            fail(f"{ref}: SHA mismatch")
        if ref == "main":
            expected_class, expected_relation = "MAIN", "MAIN_HEAD"
            expected_ahead = expected_behind = "0"
        else:
            if ref in local and ref in remote:
                expected_class = "LOCAL_AND_REMOTE_EQUAL" if local[ref] == remote[ref] else "LOCAL_AND_REMOTE_DIVERGED"
            elif ref in local:
                expected_class = "LOCAL_ONLY"
            else:
                expected_class = "REMOTE_ONLY"
            behind_n, ahead_n = map(int, git("rev-list", "--left-right", "--count", f"{snapshot_main}...{expected_sha}")[0].split())
            expected_ahead, expected_behind = str(ahead_n), str(behind_n)
            expected_relation = "ANCESTOR_OF_MAIN" if ahead_n == 0 else "DESCENDANT_OF_MAIN" if behind_n == 0 else "DIVERGED_FROM_MAIN"
        if (cls, relation, ahead, behind) != (expected_class, expected_relation, expected_ahead, expected_behind):
            fail(f"{ref}: classification or ahead/behind mismatch")
        expected_counterpart = f"origin/{ref}@{remote[ref]}" if ref in remote else "NONE"
        if counterpart != expected_counterpart:
            fail(f"{ref}: remote counterpart mismatch")
        if ref in local:
            expected_tree = next((path for path, (_, branch) in trees.items() if branch == ref), "NONE")
            if ref == "main" and expected_tree == str(ROOT):
                expected_tree = str(ROOT)
        else:
            expected_tree = "—"
        if tree != expected_tree:
            fail(f"{ref}: worktree mismatch")

    tree_section = text.split("## Worktrees\n", 1)[-1].split("\n## Future deletion candidates\n", 1)[0]
    tree_rows = []
    for line in tree_section.splitlines():
        if not line.startswith("| `"):
            continue
        fields = [x.strip() for x in line.strip("|").split("|")]
        if len(fields) != 3:
            fail(f"malformed worktree row: {line}")
        tree_rows.append(tuple(x.strip("`") for x in fields))
    expected_trees = {
        (path, snapshot_main if path == str(ROOT) and branch == "main" else head, branch)
        for path, (head, branch) in trees.items()
    }
    if set(tree_rows) != expected_trees:
        fail("worktree set mismatch")

    candidate_section = text.split("| Proposed remote ref | SHA | Evidence |\n", 1)[-1].split("\n\nThe seven rows", 1)[0]
    candidates = re.findall(r"^\| `([^`]+)` \| `([^`]+)` \| (.+) \|$", candidate_section, re.MULTILINE)
    for ref, sha, evidence in candidates:
        if not ref.startswith("origin/") or ref.removeprefix("origin/") not in remote:
            fail(f"{ref}: deletion candidate is not a known remote ref")
        remote_ref = ref.removeprefix("origin/")
        if remote[remote_ref] != sha:
            fail(f"{ref}: deletion candidate SHA mismatch")
        equivalents = [name for name, tip in local.items() if tip == sha] + [
            name for name, tip in remote.items() if name != remote_ref and tip == sha
        ]
        if not equivalents:
            fail(f"{ref}: exact equivalent evidence is absent")
        if "exact tip equals" not in evidence:
            fail(f"{ref}: deletion evidence is incomplete")

    print(f"PASS: {len(rows)} branches and {len(trees)} worktrees match current Git state; {len(candidates)} deletion candidates are proven safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
