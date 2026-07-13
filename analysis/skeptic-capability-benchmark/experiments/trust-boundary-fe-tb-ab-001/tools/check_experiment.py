#!/usr/bin/env python3
"""Fail-closed deterministic freeze checks for the public FE:TB experiment."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path, PurePosixPath


SCRIPT = Path(__file__).absolute()
ROOT = SCRIPT.parents[1]
REPO = ROOT.parents[3]
EXPERIMENT_PREFIX = (
    "analysis/skeptic-capability-benchmark/experiments/"
    "trust-boundary-fe-tb-ab-001/"
)
EXPECTED_BASE = "9c24f6f3a8a8c9f75d060ccef07f49e736866689"
EXPECTED_MAIN = "ba03bf2614faba98c4f589abef86a163c3de8664"
EXPECTED_SOURCE_BLOBS = {
    "skeptic.md": "1985bd385380ff57fe610099c4cab1e91c551e86",
    "skeptic-questions.md": "f5f299d2e3fa925dabb5ba4e661cbb5fa3c1c6cd",
}
EXPECTED_HASHES = {
    "candidates/A/skeptic.md": "9ef639b607bd2cf7e5094f6af494872ef3dd029c1cd448184bf40b64c5ef7acd",
    "candidates/B/skeptic.md": "dfe8e4801cb77840308c47ff3d1486023b8f6de05898abea1ffb6f846cc089b0",
    "candidates/A/skeptic-questions.md": "6580ea8cd22f7e2ce653f6c0ec6f8fca4d03d218f115adfe926e6db8cc7b4f25",
    "candidates/B/skeptic-questions.md": "6580ea8cd22f7e2ce653f6c0ec6f8fca4d03d218f115adfe926e6db8cc7b4f25",
    "candidates/candidate-diff.patch": "ef5b7ad5f596ad2a7b2377810193f5d09bf47484d14a57f561e8a6712b41cfcd",
    "fixtures/discovery-fixtures.md": "42bb46d7182b09421b1c8f43eb04a34c80b385e5a38e116a0b3b970f98829cc9",
    "scoring/scoring-addendum.md": "8fc208eec44acb9785d544864d0038687535648ecdfad0157f7b0b35be3bbffb",
}
EXPECTED_BUNDLES = {
    "A": "30d81fdb3923a5f2596d1c91886a90a9802b8fd20a3fde0d3ad1e0b712cae49c",
    "B": "6d607b252ddeb2b2d8c78ebfe9c8841895f4f58146cedca59393d6e6e455ead0",
}
EXPECTED_FAMILIES = {
    "AGENT/PROMPT",
    "COMMAND/INTERPRETER",
    "CONFIGURATION/POLICY/AUTOMATION",
    "FILESYSTEM/RESOURCE",
    "MEMORY/EVIDENCE",
    "QUERY/CODE",
    "TOOL/WORKER",
}
RESULT_VOCABULARY = (
    "BASELINE_SUFFICIENT",
    "NO_ADDITIONAL_VALUE",
    "INCONCLUSIVE",
    "NEGATIVE_CONTROL_REGRESSION",
    "TARGET_GAIN_TOO_NARROW_FOR_CORE",
    "TARGET_GAIN_WITH_REGRESSION",
    "TARGET_GAIN_NO_VISIBLE_REGRESSION",
)
FREEZE_RELATIVE_PATHS = (
    "README.md",
    "candidates/A/skeptic.md",
    "candidates/A/skeptic-questions.md",
    "candidates/B/skeptic.md",
    "candidates/B/skeptic-questions.md",
    "candidates/candidate-diff.patch",
    "fixtures/discovery-fixtures.md",
    "freeze-manifest.json",
    "scoring/scoring-addendum.md",
    "tools/check_experiment.py",
)
FREEZE_ALLOWLIST = {
    EXPERIMENT_PREFIX + relative for relative in FREEZE_RELATIVE_PATHS
}
MANIFEST_HASHED_RELATIVE_PATHS = tuple(
    relative for relative in FREEZE_RELATIVE_PATHS if relative != "freeze-manifest.json"
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str, input_bytes: bytes | None = None) -> bytes:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=REPO, input=input_bytes, stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as error:
        detail = error.stderr.decode("utf-8", "replace").strip()
        fail(f"git {' '.join(args)} failed: {detail}")


def safe_path(relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or not pure.parts or any(part in ("", ".", "..") for part in pure.parts):
        fail(f"unsafe relative path: {relative!r}")
    path = ROOT.joinpath(*pure.parts)
    try:
        root_real = ROOT.resolve(strict=True)
        path_real = path.resolve(strict=True)
    except OSError as error:
        fail(f"missing path {relative}: {error}")
    if path_real != root_real and root_real not in path_real.parents:
        fail(f"path escapes experiment root: {relative}")
    current = ROOT
    if current.is_symlink():
        fail("experiment root is a symlink")
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            fail(f"symlink is forbidden: {relative}")
    if not path.is_file():
        fail(f"missing regular file: {relative}")
    return path


def read(relative: str) -> bytes:
    return safe_path(relative).read_bytes()


def candidate_hash(skeptic: bytes, questions: bytes) -> str:
    return sha256(
        b"candidate-bundle-v1\0skeptic.md\0"
        + skeptic
        + b"\0skeptic-questions.md\0"
        + questions
    )


def expected_manifest() -> dict:
    return {
        "candidate_bundle_hash_algorithm": (
            "SHA256(candidate-bundle-v1\\0skeptic.md\\0<skeptic-bytes>"
            "\\0skeptic-questions.md\\0<questions-bytes>)"
        ),
        "candidate_diff_sha256": EXPECTED_HASHES["candidates/candidate-diff.patch"],
        "candidates": {
            label: {
                "bundle_sha256": EXPECTED_BUNDLES[label],
                "skeptic_questions_sha256": EXPECTED_HASHES[
                    f"candidates/{label}/skeptic-questions.md"
                ],
                "skeptic_sha256": EXPECTED_HASHES[f"candidates/{label}/skeptic.md"],
            }
            for label in ("A", "B")
        },
        "experiment_branch_base": EXPECTED_BASE,
        "fixture_count": 12,
        "fixtures_sha256": EXPECTED_HASHES["fixtures/discovery-fixtures.md"],
        "live_main_sha": EXPECTED_MAIN,
        "negative_control_count": 4,
        "positive_fixture_count": 8,
        "positive_representation_families": sorted(EXPECTED_FAMILIES),
        "prompt_revision": "001_FE_TB_AB",
        "scoring_addendum_sha256": EXPECTED_HASHES["scoring/scoring-addendum.md"],
        "source_blobs": EXPECTED_SOURCE_BLOBS,
        "task_id": "SKEPTIC_TRUST_BOUNDARY_FE_TB_REAL_AB_AND_MINIMAL_MERGE_001",
        "terminal_result_vocabulary": list(RESULT_VOCABULARY),
    }


def check_git_checkpoint() -> None:
    if git("rev-parse", "HEAD").decode().strip() != EXPECTED_BASE:
        fail("HEAD is not the pinned experiment base")
    if git("rev-parse", "origin/main").decode().strip() != EXPECTED_MAIN:
        fail("origin/main is not the pinned live-main checkpoint")
    for commit in (EXPECTED_BASE, EXPECTED_MAIN):
        if git("cat-file", "-t", commit).decode().strip() != "commit":
            fail(f"pinned object is not a commit: {commit}")


def check_candidates() -> None:
    for relative, expected in EXPECTED_HASHES.items():
        if sha256(read(relative)) != expected:
            fail(f"frozen SHA-256 mismatch: {relative}")

    a_skeptic = read("candidates/A/skeptic.md")
    b_skeptic = read("candidates/B/skeptic.md")
    a_questions = read("candidates/A/skeptic-questions.md")
    b_questions = read("candidates/B/skeptic-questions.md")

    for name, candidate in (
        ("skeptic.md", a_skeptic),
        ("skeptic-questions.md", a_questions),
    ):
        tree_blob = git("rev-parse", f"{EXPECTED_MAIN}:{name}").decode().strip()
        if tree_blob != EXPECTED_SOURCE_BLOBS[name]:
            fail(f"live-main source blob drift: {name}")
        if git("show", f"{EXPECTED_MAIN}:{name}") != candidate:
            fail(f"Candidate A does not byte-match live main: {name}")
        object_id = git("hash-object", "--stdin", input_bytes=candidate).decode().strip()
        if object_id != EXPECTED_SOURCE_BLOBS[name]:
            fail(f"Candidate A object mismatch: {name}")

    if a_questions != b_questions:
        fail("candidate questions differ")

    first_marker = (
        b"- `FE:PV` purpose/value gap: the artifact is coherent or well-structured, "
        b"but the useful outcome, user, owner, or value is unclear\n"
    )
    first_addition = (
        b"- `FE:TB` trust-boundary transition: lower-authority content is\n"
        b"  interpreted or promoted as instruction, evidence, code, query,\n"
        b"  path, configuration, policy, tool action, memory, or trusted\n"
        b"  state beyond its permitted role\n"
    )
    second_marker = b"- FE:PV purpose/value gap\n"
    second_addition = (
        b"- FE:TB trust-boundary transition / lower-authority content gaining\n"
        b"  unintended control or authority\n"
    )
    if a_skeptic.count(first_marker) != 1 or a_skeptic.count(second_marker) != 1:
        fail("Candidate A treatment anchors are not unique")
    expected_b = a_skeptic.replace(
        first_marker, first_marker + first_addition, 1
    ).replace(second_marker, second_marker + second_addition, 1)
    if b_skeptic != expected_b:
        fail("Candidate B is not exactly the two pinned FE:TB additions")

    for label, skeptic, questions in (
        ("A", a_skeptic, a_questions),
        ("B", b_skeptic, b_questions),
    ):
        if candidate_hash(skeptic, questions) != EXPECTED_BUNDLES[label]:
            fail(f"Candidate {label} bundle hash mismatch")

    result = subprocess.run(
        [
            "git", "-c", "color.ui=false", "diff", "--no-index",
            "--no-ext-diff", "--no-textconv", "--no-renames", "--abbrev=7",
            "--unified=0",
            "--", "A/skeptic.md", "B/skeptic.md",
        ],
        cwd=ROOT / "candidates",
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 1 or result.stderr:
        fail("mechanical candidate diff did not complete as an ordinary difference")
    if result.stdout != read("candidates/candidate-diff.patch"):
        fail("candidate-diff.patch is not the mechanical A-to-B diff")


def parse_fixture_fields(section: str, fixture_id: str) -> dict[str, str]:
    required = (
        "ID",
        "Source type",
        "Representation family",
        "Capabilities",
        "Negative-control status",
        "Input",
        "Prompt",
        "Expected finding",
        "Dangerous miss",
        "False-positive risk",
        "Scoring notes",
        "Evidence/reduction basis",
    )
    fields: dict[str, str] = {}
    for name in required:
        matches = re.findall(rf"^- {re.escape(name)}: (.+)$", section, re.MULTILINE)
        if len(matches) != 1:
            fail(f"{fixture_id} must contain exactly one {name!r} field")
        fields[name] = matches[0]
    return fields


def check_fixtures() -> None:
    text = read("fixtures/discovery-fixtures.md").decode("utf-8", "strict")
    matches = list(re.finditer(r"^## (TB\d{2})\b.*$", text, re.MULTILINE))
    ids = [match.group(1) for match in matches]
    expected_ids = [f"TB{index:02d}" for index in range(1, 13)]
    if ids != expected_ids:
        fail(f"fixture IDs invalid: {ids}")

    records: list[tuple[str, dict[str, str]]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        fixture_id = match.group(1)
        fields = parse_fixture_fields(text[match.end():end], fixture_id)
        if fields["ID"] != f"`{fixture_id}`":
            fail(f"{fixture_id} ID field does not match its heading")
        if fields["Capabilities"] != "`TBND`":
            fail(f"{fixture_id} capability is not exactly TBND")
        if fields["Negative-control status"] not in ("yes", "no"):
            fail(f"{fixture_id} has invalid negative-control status")
        records.append((fixture_id, fields))

    positives = [fields for _, fields in records if fields["Negative-control status"] == "no"]
    controls = [fields for _, fields in records if fields["Negative-control status"] == "yes"]
    if len(positives) != 8 or len(controls) != 4:
        fail(f"fixture balance invalid: positives={len(positives)}, controls={len(controls)}")

    families = [fields["Representation family"].strip("`") for fields in positives]
    if any(not re.fullmatch(r"[A-Z]+(?:/[A-Z]+)*", family) for family in families):
        fail("positive fixture contains an invalid named representation family")
    if set(families) != EXPECTED_FAMILIES or len(set(families)) < 7:
        fail(f"positive representation-family coverage invalid: {sorted(set(families))}")
    primary_counts = Counter(family.split("/", 1)[0] for family in families)
    if max(primary_counts.values(), default=0) > 3:
        fail(f"a primary representation family exceeds three positives: {primary_counts}")


def check_scoring() -> None:
    text = read("scoring/scoring-addendum.md").decode("utf-8", "strict")
    marker = "## Exact Result Vocabulary\n"
    if text.count(marker) != 1:
        fail("scoring addendum lacks one exact-result-vocabulary section")
    vocabulary_section = text.split(marker, 1)[1]
    observed = tuple(re.findall(r"^- `([A-Z][A-Z0-9_]*)`$", vocabulary_section, re.MULTILINE))
    if observed != RESULT_VOCABULARY:
        fail(f"terminal result vocabulary drift: {observed}")

    verbatim_gates = (
        "Discovery baseline: A=2 on all 12 -> BASELINE_SUFFICIENT.",
        "B advances only if: (1) improves >=2 positive fixtures;",
        "Regression if B advances: 36 unchanged contemporaneous A/B;",
        "Patch gate: only TARGET_GAIN_NO_VISIBLE_REGRESSION;",
    )
    if any(gate not in text for gate in verbatim_gates):
        fail("verbatim gate freeze is incomplete")


def check_readme() -> None:
    text = read("README.md").decode("utf-8", "strict")
    required = (
        "## Public Scope",
        "It generates no runner, scoring, adjudication, result, or source output.",
        "## Execution Model",
        "## Conditional Gates",
        "## Authority Boundary",
        "not permission to execute it or mutate source",
        "Separate current, scoped authorization is required",
    )
    if any(statement not in text for statement in required):
        fail("README public-scope or authority contract is incomplete")


def check_paths() -> None:
    for relative in FREEZE_RELATIVE_PATHS:
        safe_path(relative)

    output = git("status", "--porcelain=v1", "-z", "--untracked-files=all")
    records = [record for record in output.split(b"\0") if record]
    paths: set[str] = set()
    for record in records:
        if len(record) < 4 or record[2:3] != b" ":
            fail("malformed NUL-delimited porcelain status record")
        try:
            status = record[:2].decode("ascii", "strict")
            path_text = record[3:].decode("utf-8", "strict")
        except UnicodeDecodeError:
            fail("non-UTF-8 status record is forbidden")
        if "R" in status or "C" in status:
            fail("rename or copy status is forbidden during freeze")
        pure = PurePosixPath(path_text)
        if (
            pure.is_absolute()
            or str(pure) != path_text
            or any(part in ("", ".", "..") for part in pure.parts)
        ):
            fail(f"unsafe status path: {path_text!r}")
        if not path_text.startswith(EXPERIMENT_PREFIX):
            fail(f"mutation outside experiment directory: {path_text}")
        paths.add(path_text)
    if paths != FREEZE_ALLOWLIST or len(records) != len(FREEZE_ALLOWLIST):
        missing = sorted(FREEZE_ALLOWLIST - paths)
        extra = sorted(paths - FREEZE_ALLOWLIST)
        fail(f"freeze path set mismatch; missing={missing}, extra={extra}")


def check_freeze() -> None:
    check_git_checkpoint()
    manifest = json.loads(read("freeze-manifest.json"))
    frozen_hashes = manifest.pop("freeze_file_sha256", None)
    if manifest != expected_manifest():
        fail("freeze manifest differs from independently pinned constants")
    expected_hash_paths = set(MANIFEST_HASHED_RELATIVE_PATHS)
    if not isinstance(frozen_hashes, dict) or set(frozen_hashes) != expected_hash_paths:
        fail("freeze manifest does not bind every non-manifest freeze file")
    for relative in MANIFEST_HASHED_RELATIVE_PATHS:
        if frozen_hashes[relative] != sha256(read(relative)):
            fail(f"freeze-file SHA-256 mismatch: {relative}")
    check_candidates()
    check_fixtures()
    check_scoring()
    check_readme()
    check_paths()
    print(
        "PASS: pinned objects, exact treatment/diff, 12-fixture coverage, "
        "gate vocabulary, and 10-file path boundary"
    )


if __name__ == "__main__":
    if sys.argv[1:] == ["freeze"]:
        check_freeze()
    else:
        fail("usage: check_experiment.py freeze")
