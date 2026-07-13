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
FREEZE_COMMIT = "73d39551c019d73abc41db67a988742bd5e35230"
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


def load_json(relative: str) -> dict:
    return json.loads(read(relative))


def check_results_paths(repo: Path) -> None:
    output = git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    for record in (item for item in output.split(b"\0") if item):
        if len(record) < 4:
            fail("malformed porcelain status record")
        status = record[:2].decode("ascii", "strict")
        if "R" in status or "C" in status:
            fail("rename or copy status is forbidden")
        path = record[3:].decode("utf-8", "strict")
        if not path.startswith(EXPERIMENT_PREFIX):
            fail(f"mutation outside experiment directory: {path}")


def check_frozen_immutability(repo: Path) -> None:
    if git(repo, "rev-parse", f"{FREEZE_COMMIT}^").decode().strip() != EXPECTED_BASE:
        fail("freeze commit is not a direct child of the parked base")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", FREEZE_COMMIT, "HEAD"],
        cwd=repo,
        check=False,
    ).returncode != 0:
        fail("freeze commit is not an ancestor of HEAD")
    frozen = (
        "candidates/A/skeptic.md",
        "candidates/A/skeptic-questions.md",
        "candidates/B/skeptic.md",
        "candidates/B/skeptic-questions.md",
        "fixtures/discovery-fixtures.md",
        "freeze-manifest.json",
        "scoring/scoring-addendum.md",
    )
    for relative in frozen:
        committed = git(repo, "show", f"{FREEZE_COMMIT}:{EXPERIMENT_PREFIX}{relative}")
        if read(relative) != committed:
            fail(f"frozen artifact changed after freeze: {relative}")


def check_results() -> None:
    repo = ROOT.parents[3]
    check_frozen_immutability(repo)
    check_results_paths(repo)

    execution = load_json("runs/discovery/execution-manifest.json")
    records = execution.get("records", [])
    if execution.get("freeze_commit") != FREEZE_COMMIT:
        fail("execution manifest freeze commit mismatch")
    if execution.get("model") != "gpt-5.6-sol" or execution.get("reasoning_effort") != "high":
        fail("runner model or effort mismatch")
    expected_pairs = {(candidate, f"PV{i:02d}") for candidate in "AB" for i in range(1, 9)}
    pairs = {(record["candidate"], record["fixture"]) for record in records}
    if len(records) != 16 or pairs != expected_pairs:
        fail("discovery output matrix is incomplete")
    contexts = [record["fresh_context_id"] for record in records]
    if len(set(contexts)) != 16:
        fail("runner context IDs are not unique")
    for record in records:
        if not record.get("protocol_valid") or record.get("attempt") != 1:
            fail("runner protocol or attempt mismatch")
        expected_path = f"runs/discovery/{record['candidate']}/{record['fixture']}/raw-response.md"
        if record["response_path"] != expected_path:
            fail(f"unexpected response path: {record['response_path']}")
        data = read(expected_path)
        if len(data) != record["byte_count"] or sha256(data) != record["sha256"]:
            fail(f"response byte/hash mismatch: {expected_path}")

    mapping = load_json("scoring/discovery/anonymization-map.json")
    mapping_bytes = read("scoring/discovery/anonymization-map.json")
    outputs = mapping.get("outputs", [])
    if len(outputs) != 16 or len({item["output_id"] for item in outputs}) != 16:
        fail("anonymization map output IDs invalid")
    if {item["packet_position"] for item in outputs} != set(range(1, 17)):
        fail("randomized packet positions invalid")
    output_by_id = {item["output_id"]: item for item in outputs}
    if {(item["candidate"], item["fixture_id"]) for item in outputs} != expected_pairs:
        fail("anonymization map pair set mismatch")
    if set(mapping.get("candidate_to_label", {})) != {"A", "B"}:
        fail("candidate label mapping incomplete")

    packet_bytes = read("scoring/discovery/blinded-packet.json")
    packet = json.loads(packet_bytes)
    packet_records = {item["output_id"]: item for item in packet.get("records", [])}
    if len(packet_records) != 16 or set(packet_records) != set(output_by_id):
        fail("blinded packet output set incomplete")
    for output_id, item in output_by_id.items():
        source = read(item["source_relative_path"])
        if sha256(source) != item["source_sha256"]:
            fail(f"mapping source hash mismatch: {output_id}")
        blinded = packet_records[output_id]["raw_output"].encode("utf-8")
        if source != blinded:
            fail(f"source-to-blinded byte mismatch: {output_id}")
        if packet_records[output_id]["fixture_id"] != item["fixture_id"]:
            fail(f"blinded fixture mismatch: {output_id}")

    blinding_receipt = load_json("results/blinding-receipt.json")
    receipt_records = {item["output_id"]: item for item in blinding_receipt.get("records", [])}
    if len(receipt_records) != 16 or set(receipt_records) != set(output_by_id):
        fail("blinding receipt output set incomplete")
    if blinding_receipt.get("mapping_sha256") != sha256(mapping_bytes):
        fail("blinding receipt mapping hash mismatch")
    if blinding_receipt.get("blinded_packet_sha256") != sha256(packet_bytes):
        fail("blinding receipt packet hash mismatch")
    for output_id, item in output_by_id.items():
        receipt = receipt_records[output_id]
        source = read(item["source_relative_path"])
        if receipt.get("source_sha256") != sha256(source):
            fail(f"blinding receipt source hash mismatch: {output_id}")
        if receipt.get("sanitized_sha256") != sha256(source):
            fail(f"blinding receipt sanitized hash mismatch: {output_id}")
        if receipt.get("metadata_removed") is not False or receipt.get("source_equals_blinded") is not True:
            fail(f"blinding receipt transformation claim invalid: {output_id}")

    judges = [load_json("scoring/discovery/judge-1.json"), load_json("scoring/discovery/judge-2.json")]
    judge_contexts = [judge["context_id"] for judge in judges]
    if len(set(judge_contexts)) != 2 or set(judge_contexts) & set(contexts):
        fail("Judge contexts are reused")
    for judge in judges:
        if not judge.get("protocol_valid") or judge.get("model") != "gpt-5.6-sol":
            fail("Judge protocol/model mismatch")
        if judge.get("reasoning_effort") != "high" or judge.get("tool_calls") != 0:
            fail("Judge effort or tool-use mismatch")
        if judge.get("packet_sha256") != sha256(packet_bytes):
            fail("Judge packet hash mismatch")
        failures = judge.get("pre_context_failures", [])
        if judge.get("retry_count") != len(failures):
            fail("Judge retry count mismatch")
        if any(failure.get("context_created") is not False for failure in failures):
            fail("Judge retry record contains an untracked created context")
        scores = judge.get("scores", [])
        if len(scores) != 16 or {item["output_id"] for item in scores} != set(output_by_id):
            fail("Judge score set incomplete")
        for item in scores:
            if item["score"] not in (-1, 0, 1, 2):
                fail("Judge score outside locked scale")
            if item["fixture_id"] != output_by_id[item["output_id"]]["fixture_id"]:
                fail("Judge fixture/output mismatch")

    j1 = {item["output_id"]: item for item in judges[0]["scores"]}
    j2 = {item["output_id"]: item for item in judges[1]["scores"]}
    disagreements = {
        output_id
        for output_id in output_by_id
        if (j1[output_id]["score"], j1[output_id]["dangerous"])
        != (j2[output_id]["score"], j2[output_id]["dangerous"])
    }
    adjudication = load_json("scoring/discovery/adjudication.json")
    adjudicated = {item["output_id"]: item for item in adjudication.get("records", [])}
    if set(adjudicated) != disagreements or adjudication.get("disagreement_count") != len(disagreements):
        fail("adjudication set does not equal Judge disagreements")
    if disagreements:
        if adjudication.get("context_id") in set(contexts + judge_contexts):
            fail("adjudicator context reused")
        if not adjudication.get("protocol_valid") or adjudication.get("tool_calls") != 0:
            fail("adjudicator protocol/tool-use mismatch")

    final = load_json("scoring/discovery/final-anonymous-scores.json")
    if final.get("blinded_packet_sha256") != sha256(packet_bytes):
        fail("final score manifest packet hash mismatch")
    final_records = {item["output_id"]: item for item in final.get("records", [])}
    if len(final_records) != 16 or set(final_records) != set(output_by_id):
        fail("final anonymous score set incomplete")
    for output_id, record in final_records.items():
        if output_id in adjudicated:
            expected = (adjudicated[output_id]["score"], adjudicated[output_id]["dangerous"])
        else:
            expected = (j1[output_id]["score"], j1[output_id]["dangerous"])
        if (record["final_score"], record["final_dangerous"]) != expected:
            fail("final score does not reconcile with Judges/adjudicator")
    frozen_hash = load_json("scoring/discovery/final-anonymous-scores.sha256.json")
    if frozen_hash.get("mapping_unsealed") is not False:
        fail("score freeze does not record sealed mapping")
    if sha256(read("scoring/discovery/final-anonymous-scores.json")) != frozen_hash.get("sha256"):
        fail("final anonymous score freeze hash mismatch")

    matrix = load_json("scoring/discovery/discovery-score-matrix.json")
    if matrix.get("anonymization_map_sha256") != sha256(mapping_bytes):
        fail("score matrix mapping hash mismatch")
    expected_scores = {
        "A": [2, 2, 2, 1, 2, 2, 1, 2],
        "B": [2, 2, 2, 1, 2, 2, 2, 2],
    }
    for candidate, scores in expected_scores.items():
        observed = [matrix["candidates"][candidate]["fixtures"][f"PV{i:02d}"]["score"] for i in range(1, 9)]
        if observed != scores:
            fail(f"{candidate} score matrix drift")
        if matrix["candidates"][candidate]["total"] != sum(scores):
            fail(f"{candidate} total arithmetic mismatch")
        if matrix["candidates"][candidate]["positive_total"] != sum(scores[:4]):
            fail(f"{candidate} positive arithmetic mismatch")
        if matrix["candidates"][candidate]["negative_control_total"] != sum(scores[4:]):
            fail(f"{candidate} negative arithmetic mismatch")
    if matrix.get("judge_agreement_count") != 14 or matrix.get("adjudication_count") != 2:
        fail("agreement/adjudication counts drift")

    a, b = expected_scores["A"], expected_scores["B"]
    if all(score == 2 for score in a):
        fail("recorded gate should be BASELINE_SUFFICIENT")
    positive_improvements = sum(b[i] >= a[i] + 1 for i in range(4))
    positive_delta = sum(b[:4]) - sum(a[:4])
    if positive_improvements != 0 or positive_delta != 0:
        fail("locked discovery-gate arithmetic changed")
    if (ROOT / "runs/visible").exists() or (ROOT / "scoring/visible").exists():
        fail("visible regression ran despite failed discovery gate")

    report = read("results/experiment-results.md").decode("utf-8")
    for statement in ("Discovery gate: `NO_ADDITIONAL_VALUE`", "Source patch authorized: no", "Private evidence accessed: no"):
        if statement not in report:
            fail(f"result report missing: {statement}")
    private_tokens = (
        ".local/share/" + "skeptic-benchmark-private",
        ".config/" + "skeptic-benchmark-private-backup",
    )
    for path in ROOT.rglob("*"):
        if path.is_file() and not path.is_symlink():
            data = path.read_bytes()
            for token in private_tokens:
                if token.encode() in data:
                    fail(f"private path token published in {path.relative_to(ROOT)}")

    print("PASS: frozen inputs, 16 runs, blinded scoring, adjudication, arithmetic, gate, and path boundary")


if __name__ == "__main__":
    if sys.argv[1:] == ["freeze"]:
        check_freeze()
    elif sys.argv[1:] == ["results"]:
        check_results()
    else:
        fail("usage: check_experiment.py freeze|results")
