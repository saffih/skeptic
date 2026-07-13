#!/usr/bin/env python3
"""Fail-closed deterministic checks for the public process-value experiment."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT_PREFIX = "analysis/skeptic-capability-benchmark/experiments/process-value-ab-001/"
EXPECTED_MAIN = "ba03bf2614faba98c4f589abef86a163c3de8664"
EXPECTED_BASE = "fcd1fa31a40fea050dc1f0699948e5e2c7cfebd4"
EXPECTED_SOURCE_BLOBS = {
    "skeptic.md": "1985bd385380ff57fe610099c4cab1e91c551e86",
    "skeptic-questions.md": "f5f299d2e3fa925dabb5ba4e661cbb5fa3c1c6cd",
}
EXPECTED_FROZEN_HASHES = {
    "fixtures/discovery-fixtures.md": "7ba257d89c82cb0f1bea2b896e3a6cb7ddf056869b9bb7eef414c180f1bd547a",
    "scoring/scoring-addendum.md": "147997c01da80acdf51b3e4a5995f86f79f99b4450401a98b951828dc6a9426b",
}
FREEZE_ALLOWLIST = {
    EXPERIMENT_PREFIX + path
    for path in (
        "README.md",
        "candidates/A/skeptic.md",
        "candidates/A/skeptic-questions.md",
        "candidates/B/skeptic.md",
        "candidates/B/skeptic-questions.md",
        "fixtures/discovery-fixtures.md",
        "freeze-manifest.json",
        "scoring/scoring-addendum.md",
        "tools/check_experiment.py",
    )
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def read(relative: str) -> bytes:
    path = ROOT / relative
    if not path.is_file() or path.is_symlink():
        fail(f"missing or unsafe file: {relative}")
    return path.read_bytes()


def candidate_hash(skeptic: bytes, questions: bytes) -> str:
    payload = (
        b"candidate-bundle-v1\0skeptic.md\0"
        + skeptic
        + b"\0skeptic-questions.md\0"
        + questions
    )
    return sha256(payload)


def git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    return subprocess.check_output(["git", *args], cwd=repo, input=input_bytes)


def check_paths() -> None:
    repo = ROOT.parents[3]
    output = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    records = [record for record in output.split(b"\0") if record]
    paths: set[str] = set()
    for record in records:
        if len(record) < 4:
            fail("malformed porcelain status record")
        status = record[:2].decode("ascii", "strict")
        if "R" in status or "C" in status:
            fail("rename or copy status is forbidden during freeze")
        paths.add(record[3:].decode("utf-8", "strict"))
    if paths != FREEZE_ALLOWLIST:
        missing = sorted(FREEZE_ALLOWLIST - paths)
        extra = sorted(paths - FREEZE_ALLOWLIST)
        fail(f"freeze path set mismatch; missing={missing}, extra={extra}")


def check_freeze() -> None:
    repo = ROOT.parents[3]
    manifest = json.loads(read("freeze-manifest.json"))
    if manifest["live_main_sha"] != EXPECTED_MAIN:
        fail("manifest live main SHA is not pinned value")
    if manifest["experiment_branch_base"] != EXPECTED_BASE:
        fail("manifest experiment base is not pinned value")
    if git(repo, "rev-parse", "origin/main").decode().strip() != EXPECTED_MAIN:
        fail("origin/main no longer matches frozen live-main checkpoint")
    if git(repo, "rev-parse", "HEAD").decode().strip() != EXPECTED_BASE:
        fail("freeze must run before a commit on the exact parked base")
    if manifest["source_blobs"] != EXPECTED_SOURCE_BLOBS:
        fail("manifest source blob IDs drifted")

    a_s = read("candidates/A/skeptic.md")
    a_q = read("candidates/A/skeptic-questions.md")
    b_s = read("candidates/B/skeptic.md")
    b_q = read("candidates/B/skeptic-questions.md")

    for label, skeptic, questions in (("A", a_s, a_q), ("B", b_s, b_q)):
        frozen = manifest["candidates"][label]
        if sha256(skeptic) != frozen["skeptic_sha256"]:
            fail(f"{label} skeptic hash drift")
        if sha256(questions) != frozen["skeptic_questions_sha256"]:
            fail(f"{label} questions hash drift")
        if candidate_hash(skeptic, questions) != frozen["bundle_sha256"]:
            fail(f"{label} bundle hash drift")

    if a_s != b_s:
        fail("candidate skeptic.md files differ")
    for name, data in (("skeptic.md", a_s), ("skeptic-questions.md", a_q)):
        source = git(repo, "show", f"{EXPECTED_MAIN}:{name}")
        if data != source:
            fail(f"Candidate A does not byte-match {EXPECTED_MAIN}:{name}")
        blob = git(repo, "hash-object", "--stdin", input_bytes=data).decode().strip()
        if blob != EXPECTED_SOURCE_BLOBS[name]:
            fail(f"Candidate A source blob mismatch for {name}")
    addition = b"""CPX6. When an artifact creates or expands a process, review,
governance, orchestration, or verification layer, does it prevent
a named material failure or unlock a necessary decision, and is a
simpler control sufficient?

Activation rule:

Apply CPX6 only when a process or control layer is materially part
of the target. Do not activate it for routine tasks or controls
whose necessity is already clear.

"""
    marker = b"CPX5. How many things must you hold in your head to understand this?\n\n"
    if a_q.count(marker) != 1 or b_q != a_q.replace(marker, marker + addition):
        fail("candidate delta is not the exact CPX6 block")

    fixtures = read("fixtures/discovery-fixtures.md")
    if manifest["fixtures_sha256"] != EXPECTED_FROZEN_HASHES["fixtures/discovery-fixtures.md"]:
        fail("manifest fixture hash is not independently pinned")
    if sha256(fixtures) != EXPECTED_FROZEN_HASHES["fixtures/discovery-fixtures.md"]:
        fail("fixture hash drift")
    text = fixtures.decode("utf-8")
    ids = re.findall(r"^## (PV\d{2})\b", text, re.MULTILINE)
    if ids != [f"PV{i:02d}" for i in range(1, 9)]:
        fail(f"fixture IDs invalid: {ids}")
    sections = re.split(r"^## PV\d{2}\b.*$", text, flags=re.MULTILINE)[1:]
    required = (
        "- ID:", "- Source type:", "- Target capability:",
        "- Negative-control status:", "- Input artifact:", "- Prompt:",
        "- Expected good finding:", "- Dangerous miss:",
        "- False-positive risk:", "- Scoring notes:", "- Evidence basis:",
    )
    for index, section in enumerate(sections, 1):
        if any(field not in section for field in required):
            fail(f"PV{index:02d} missing required field")
    if text.count("Negative-control status: yes") != 4:
        fail("negative-control count is not four")
    if text.count("Negative-control status: no") != 4:
        fail("positive fixture count is not four")

    scoring = read("scoring/scoring-addendum.md")
    if manifest["scoring_addendum_sha256"] != EXPECTED_FROZEN_HASHES["scoring/scoring-addendum.md"]:
        fail("manifest scoring hash is not independently pinned")
    if sha256(scoring) != EXPECTED_FROZEN_HASHES["scoring/scoring-addendum.md"]:
        fail("scoring addendum hash drift")
    scoring_text = scoring.decode("utf-8")
    required_results = (
        "BASELINE_SUFFICIENT", "NO_ADDITIONAL_VALUE", "INCONCLUSIVE",
        "B_NEGATIVE_CONTROL_REGRESSION", "B_TARGET_GAIN_WITH_REGRESSION",
        "B_TARGET_GAIN_NO_VISIBLE_REGRESSION",
    )
    if any(result not in scoring_text for result in required_results):
        fail("final result vocabulary incomplete")
    for forbidden in ("PROCESS VALUE SUPPORTED", "positive-fixture total advantage is at least `+4`"):
        if forbidden in scoring_text:
            fail(f"superseded scoring rule present: {forbidden}")

    check_paths()
    print("PASS: freeze inputs, candidate delta, fixture balance, scoring contract, and path boundary")


if __name__ == "__main__":
    if sys.argv[1:] != ["freeze"]:
        fail("usage: check_experiment.py freeze")
    check_freeze()
