#!/usr/bin/env python3
import argparse
import base64
import hashlib
import hmac
import json
import os
import stat
import subprocess
from pathlib import Path

TASK_ID = "STAGE_5E_PRIVATE_RAW_EVIDENCE_RETENTION_AND_SAFE_RECEIPT_PUBLICATION_PACKET_004"
INPUT_COMMIT = "0c6fb76c87b9e52074764f37f189c2d9788ebf7d"
EXPECTED_MAPPING = "f2099d2922bef9777208e814ab773a86c256ccb04b316ec8275c94d8429c170a"
EXPECTED_HOLDOUT = "3373a48a93a29a3d30d09d25f88b1d76b6df60dd52a44373dd092d540abccf7b"
SLOTS = ["SLOT-A", "SLOT-B", "SLOT-C"]
ALIASES = ["PF01", "PF02", "PF03", "PF04"]
PAIRS = [f"{slot}/{alias}" for slot in SLOTS for alias in ALIASES]
PUBLIC_PATHS = [
    "analysis/skeptic-capability-benchmark/audits/10-stage5e-exploratory-holdout-execution.md",
    "analysis/skeptic-capability-benchmark/reports/11-stage5e-exploratory-holdout-execution-summary.md",
    "analysis/skeptic-capability-benchmark/receipts/stage5e-exploratory-holdout-execution-001/00-packet-builder.py",
    "analysis/skeptic-capability-benchmark/receipts/stage5e-exploratory-holdout-execution-001/01-run-verifier.py",
    "analysis/skeptic-capability-benchmark/receipts/stage5e-exploratory-holdout-execution-001/02-runskeptic-gate.md",
]
PRIVATE_RUN_ROOT = "analysis/skeptic-capability-benchmark/runs/private-holdout-stage5e-packet-001"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def keyed(key: bytes, *parts: str) -> str:
    return hmac.new(key, b"\0".join(part.encode("ascii") for part in parts), hashlib.sha256).hexdigest()


def git_z(repo: Path, *args: str) -> list[bytes]:
    result = subprocess.run(["git", *args], cwd=repo, check=True, stdout=subprocess.PIPE)
    return [item for item in result.stdout.split(b"\0") if item]


def describe(repo: Path, raw_path: bytes) -> dict[str, object]:
    rel = os.fsdecode(raw_path)
    path = repo / rel
    info = path.lstat()
    entry: dict[str, object] = {"path": rel, "mode": stat.S_IMODE(info.st_mode)}
    if stat.S_ISREG(info.st_mode):
        entry.update(type="regular", bytes=info.st_size, sha256=sha256(path.read_bytes()))
    elif stat.S_ISLNK(info.st_mode):
        entry.update(type="symlink", target=os.readlink(path))
    else:
        entry.update(type="other", bytes=info.st_size)
    return entry


def current_untracked(repo: Path) -> list[dict[str, object]]:
    root = "analysis/skeptic-capability-benchmark"
    entries = [describe(repo, item) for item in git_z(repo, "ls-files", "--others", "--exclude-standard", "-z", "--", root)]
    return sorted(entries, key=lambda item: str(item["path"]))


def public_path(root: Path, repo: Path, path: str, phase: str) -> Path:
    if phase == "pre":
        return root / Path(path).name
    return repo / path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--private-primary", type=Path, required=True)
    parser.add_argument("--private-backup", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--public-root", type=Path, required=True)
    parser.add_argument("--commitments-json", type=Path, required=True)
    parser.add_argument("--phase", choices=["pre", "staged"], required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    primary = args.private_primary.expanduser().resolve()
    backup = args.private_backup.expanduser().resolve()
    if repo == primary or repo in primary.parents or repo == backup or repo in backup.parents:
        raise SystemExit("private evidence root is inside repository")
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    mapping_bytes = (primary / "blind-mapping.json").read_bytes()
    if mapping_bytes != (backup / "blind-mapping.backup.json").read_bytes() or sha256(mapping_bytes) != EXPECTED_MAPPING:
        raise SystemExit("mapping verification failed")
    mapping = json.loads(mapping_bytes)
    key = base64.b64decode(mapping["hmac_key_base64"], validate=True)
    if keyed(key, "holdout-bank", mapping["holdout_bank_sha256"]) != EXPECTED_HOLDOUT:
        raise SystemExit("holdout commitment mismatch")
    if (primary / "frozen-inputs/holdout-fixtures.md").read_bytes() != (backup / "frozen-inputs/holdout-fixtures.md").read_bytes():
        raise SystemExit("frozen holdout copies differ")

    manifest_primary = primary / "accepted-response-manifest.json"
    manifest_backup = backup / "accepted-response-manifest.backup.json"
    manifest_bytes = manifest_primary.read_bytes()
    if manifest_bytes != manifest_backup.read_bytes():
        raise SystemExit("private manifests differ")
    manifest = json.loads(manifest_bytes)
    if manifest["task_id"] != TASK_ID or manifest["input_stage4_commit"] != INPUT_COMMIT:
        raise SystemExit("private manifest identity mismatch")
    if manifest["accepted_response_count"] != 12 or manifest["unique_context_count"] != 12 or manifest["total_technical_retries"] != 0:
        raise SystemExit("private manifest counts mismatch")
    rows = {f"{row['anonymous_slot']}/{row['private_fixture_alias']}": row for row in manifest["responses"]}
    if sorted(rows) != PAIRS or len({row["accepted_context_id"] for row in rows.values()}) != 12:
        raise SystemExit("private response/context manifest mismatch")
    prior = json.loads((primary / "attempts/accepted-manifest.json").read_text(encoding="utf-8"))
    if prior["accepted_run_count"] != 12 or prior["unique_context_count"] != 12 or prior["retry_count"] != 0:
        raise SystemExit("prior acceptance counts mismatch")

    commitments = json.loads(args.commitments_json.read_text(encoding="utf-8"))
    expected_response_hmac = {}
    raw_private_values = [
        mapping["holdout_bank_sha256"], mapping["hmac_key_base64"], mapping["mapping_nonce_base64"],
        *mapping["candidate_bundle_sha256"].values(), *mapping["fixture_packet_sha256"].values(),
        *mapping["holdout_section_sha256"].values(),
    ]
    response_bodies = []
    for pair in PAIRS:
        slot, alias = pair.split("/")
        left = primary / "accepted-responses" / pair / "raw-response.txt"
        right = backup / "accepted-responses" / pair / "raw-response.txt"
        if left.is_symlink() or right.is_symlink() or not left.is_file() or not right.is_file():
            raise SystemExit(f"private response missing: {pair}")
        data = left.read_bytes()
        if data != right.read_bytes():
            raise SystemExit(f"private response copies differ: {pair}")
        row = rows[pair]
        prior_row = prior["response_manifest"][pair]
        raw_hash = sha256(data)
        if len(data) != row["response_byte_count"] or raw_hash != row["raw_response_sha256"]:
            raise SystemExit(f"private manifest does not bind response: {pair}")
        if len(data) != prior_row["bytes"] or raw_hash != prior_row["sha256"]:
            raise SystemExit(f"prior accepted manifest mismatch: {pair}")
        if pair == "SLOT-C/PF04" and not data.split(b"\n", 1)[0].endswith((b" ", b"\t")):
            raise SystemExit("trailing whitespace evidence changed")
        expected_response_hmac[pair] = keyed(key, "accepted-response", slot, alias, raw_hash)
        raw_private_values.append(raw_hash)
        response_bodies.append(data)
    expected_manifest_hmac = keyed(key, "accepted-response-manifest", sha256(manifest_bytes))
    if commitments["accepted_response_hmac_commitments"] != expected_response_hmac:
        raise SystemExit("public response commitments mismatch")
    if commitments["accepted_response_manifest_hmac_commitment"] != expected_manifest_hmac:
        raise SystemExit("public manifest commitment mismatch")
    if commitments["mapping_commitment_sha256"] != EXPECTED_MAPPING or commitments["holdout_public_hmac_commitment"] != EXPECTED_HOLDOUT:
        raise SystemExit("public fixed commitments mismatch")

    public_files = [public_path(args.public_root, repo, path, args.phase) for path in PUBLIC_PATHS]
    if any(not path.is_file() or path.is_symlink() for path in public_files):
        raise SystemExit("public artifact missing or invalid")
    public_bytes = b"\n".join(path.read_bytes() for path in public_files)
    for value in raw_private_values:
        if value.encode("ascii") in public_bytes:
            raise SystemExit("raw private hash, key, or nonce published")
    for body in response_bodies:
        if body and body in public_bytes:
            raise SystemExit("raw response body published")
    for value in expected_response_hmac.values():
        if value.encode("ascii") not in public_bytes:
            raise SystemExit("response commitment missing from public artifacts")
    if expected_manifest_hmac.encode("ascii") not in public_bytes:
        raise SystemExit("manifest commitment missing from public artifacts")
    if (repo / PRIVATE_RUN_ROOT).exists() or (repo / PRIVATE_RUN_ROOT).is_symlink():
        raise SystemExit("private raw response run root exists in repository")

    if subprocess.run(["git", "diff", "--quiet"], cwd=repo).returncode != 0:
        raise SystemExit("tracked worktree modification detected")
    current = current_untracked(repo)
    if args.phase == "pre":
        if current != baseline["untracked"]:
            raise SystemExit("pre-materialization baseline changed")
        for path in PUBLIC_PATHS:
            if (repo / path).exists() or (repo / path).is_symlink():
                raise SystemExit("public path exists before materialization")
        if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo).returncode != 0:
            raise SystemExit("index is not empty before materialization")
    else:
        if current != baseline["untracked"]:
            raise SystemExit("pre-existing untracked baseline changed")
        staged = subprocess.run(
            ["git", "diff", "--cached", "--name-status"], cwd=repo, check=True, stdout=subprocess.PIPE, text=True
        ).stdout.splitlines()
        expected_staged = sorted(f"A\t{path}" for path in PUBLIC_PATHS)
        if sorted(staged) != expected_staged:
            raise SystemExit("staged path manifest mismatch")
        check = subprocess.run(
            ["git", "-c", "core.whitespace=blank-at-eol,blank-at-eof,space-before-tab", "diff", "--cached", "--check", "--", *PUBLIC_PATHS],
            cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if check.returncode != 0 or check.stdout or check.stderr:
            raise SystemExit("Git whitespace check failed")
    print("VERDICT=PASS")
    print("PRIVATE_RESPONSE_PRIMARY_BACKUP_MATCH=yes")
    print("PRIVATE_MANIFEST_PRIMARY_BACKUP_MATCH=yes")
    print("TRAILING_WHITESPACE_PRESERVED=yes")
    print("PUBLIC_COMMITMENTS=PASS")
    print("RAW_RESPONSE_BODIES_COMMITTED=no")
    print("RAW_RESPONSE_HASHES_PUBLISHED=no")
    print("BASELINE_PRESERVATION=PASS")


if __name__ == "__main__":
    main()
