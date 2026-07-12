#!/usr/bin/env python3
import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import shutil
import stat
from pathlib import Path
from typing import Optional

TASK_ID = "STAGE_5E_PRIVATE_INPUT_PROVENANCE_REPAIR_AND_EXPLORATORY_EXECUTION_PACKET_002"
INPUT_COMMIT = "0c6fb76c87b9e52074764f37f189c2d9788ebf7d"
EXPECTED_F5 = {
    "F5-skeptic.md": "9ef639b607bd2cf7e5094f6af494872ef3dd029c1cd448184bf40b64c5ef7acd",
    "F5-skeptic-questions.md": "6580ea8cd22f7e2ce653f6c0ec6f8fca4d03d218f115adfe926e6db8cc7b4f25",
}
CANDIDATES = {
    "C0-current-main": None,
    "C1-current-main-plus-loop-collect": "## Minimal Runtime Extension Under Test",
    "C2-current-main-plus-code-skeptic-domain-extension": "## Minimal Domain Extension Under Test",
}
DEFINITION_PATHS = {
    candidate: f"analysis/skeptic-capability-benchmark/candidates/{candidate}/definition.md"
    for candidate in CANDIDATES
}
PROHIBITED_BUNDLE_TEXT = [
    b"C0-current-main",
    b"C1-current-main-plus-loop-collect",
    b"C2-current-main-plus-code-skeptic-domain-extension",
    b"C3-current-main-plus-loop-and-code-extension",
]
FORBIDDEN_PACKET_LABELS = [
    b"Expected good finding",
    b"Dangerous miss",
    b"False-positive risk",
    b"Scoring notes",
    b"Negative-control",
    b"Capability",
    b"Evidence",
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def shuffle(values: list[str]) -> list[str]:
    result = list(values)
    for index in range(len(result) - 1, 0, -1):
        other = secrets.randbelow(index + 1)
        result[index], result[other] = result[other], result[index]
    return result


def ensure_private_dir(path: Path) -> None:
    if path.is_symlink():
        raise SystemExit(f"symlink directory rejected: {path}")
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)
    if stat.S_IMODE(path.stat().st_mode) != 0o700:
        raise SystemExit(f"private directory mode mismatch: {path}")


def write_private(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.parent.chmod(0o700)
    if path.exists() or path.is_symlink():
        raise SystemExit(f"refusing to overwrite private artifact: {path}")
    path.write_bytes(data)
    path.chmod(0o600)


def extract_extension(definition: bytes, heading: Optional[str]) -> bytes:
    if heading is None:
        return b""
    marker = heading.encode("utf-8")
    if definition.count(marker) != 1:
        raise SystemExit(f"extension heading count mismatch: {heading}")
    return definition[definition.index(marker):]


def parse_holdouts(data: bytes) -> dict[str, dict[str, bytes]]:
    text = data.decode("utf-8")
    matches = list(re.finditer(r"(?m)^## (HO\d{2})\b[^\n]*\n", text))
    if len(matches) != 4 or len({m.group(1) for m in matches}) != 4:
        raise SystemExit("expected exactly four unique holdout sections")
    result: dict[str, dict[str, bytes]] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[match.end():end]
        input_matches = list(re.finditer(r"(?m)^- Input artifact: (.+)\n", section))
        prompt_matches = list(re.finditer(r"(?m)^- Prompt to apply: (.+)\n", section))
        if len(input_matches) != 1 or len(prompt_matches) != 1:
            raise SystemExit(f"field count mismatch in holdout section {index + 1}")
        input_bytes = input_matches[0].group(1).encode("utf-8")
        prompt_bytes = prompt_matches[0].group(1).encode("utf-8")
        packet = b"PRIVATE INPUT\n\n" + input_bytes + b"\n\nTASK\n\n" + prompt_bytes
        if any(label in packet for label in FORBIDDEN_PACKET_LABELS):
            raise SystemExit(f"forbidden label leaked in sanitized holdout {index + 1}")
        if re.search(rb"\bHO\d{2}\b", packet):
            raise SystemExit(f"holdout identifier leaked in sanitized holdout {index + 1}")
        result[match.group(1)] = {"section": text[match.start():end].encode("utf-8"), "packet": packet}
    return result


def commitment(key: bytes, *parts: str) -> str:
    payload = b"\0".join(part.encode("ascii") for part in parts)
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--backup", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    primary = args.primary.expanduser().resolve()
    backup = args.backup.expanduser().resolve()
    if repo == primary or repo in primary.parents or repo == backup or repo in backup.parents:
        raise SystemExit("private roots must be outside repository")
    if primary == backup:
        raise SystemExit("primary and backup roots must differ")
    ensure_private_dir(primary)
    ensure_private_dir(backup)
    if (primary / "blind-mapping.json").exists() or (backup / "blind-mapping.backup.json").exists():
        raise SystemExit("mapping already exists")

    frozen = primary / "frozen-inputs"
    for name, expected in EXPECTED_F5.items():
        data = (frozen / name).read_bytes()
        if sha256(data) != expected:
            raise SystemExit(f"F5 hash mismatch: {name}")
    holdout_data = (frozen / "holdout-fixtures.md").read_bytes()

    # Randomize aliases before decoding or structurally parsing private holdout content.
    slots = ["SLOT-A", "SLOT-B", "SLOT-C"]
    aliases = ["PF01", "PF02", "PF03", "PF04"]
    slot_candidates = dict(zip(slots, shuffle(list(CANDIDATES))))
    alias_indexes = dict(zip(aliases, shuffle(["HO01", "HO02", "HO03", "HO04"])))
    execution_order = shuffle([f"{slot}/{alias}" for slot in slots for alias in aliases])
    key = secrets.token_bytes(32)
    nonce = secrets.token_bytes(32)

    skeptic = (frozen / "F5-skeptic.md").read_bytes()
    questions = (frozen / "F5-skeptic-questions.md").read_bytes()
    definition_hashes: dict[str, str] = {}
    bundles: dict[str, bytes] = {}
    bundle_hashes: dict[str, str] = {}
    for slot in slots:
        candidate = slot_candidates[slot]
        definition = (repo / DEFINITION_PATHS[candidate]).read_bytes()
        definition_hashes[candidate] = sha256(definition)
        extension = extract_extension(definition, CANDIDATES[candidate])
        bundle = (
            b"SKEPTIC INSTRUCTIONS\n\n" + skeptic
            + b"\n\nCOMPANION QUESTIONS\n\n" + questions
            + b"\n\nOPTIONAL EXTENSION\n\n" + extension
        )
        if any(identifier in bundle for identifier in PROHIBITED_BUNDLE_TEXT):
            raise SystemExit(f"candidate identifier leaked into bundle for {slot}")
        bundles[slot] = bundle
        bundle_hashes[slot] = sha256(bundle)

    holdouts = parse_holdouts(holdout_data)
    section_hashes = {holdout_id: sha256(value["section"]) for holdout_id, value in holdouts.items()}
    fixture_packets = {alias: holdouts[alias_indexes[alias]]["packet"] for alias in aliases}
    packet_hashes = {alias: sha256(data) for alias, data in fixture_packets.items()}

    candidate_commitments = {
        slot: commitment(key, "candidate-bundle", slot, bundle_hashes[slot]) for slot in slots
    }
    fixture_commitments = {
        alias: commitment(key, "fixture-packet", alias, packet_hashes[alias]) for alias in aliases
    }
    pair_commitments = {
        f"{slot}/{alias}": commitment(
            key, "execution-pair", slot, alias, bundle_hashes[slot], packet_hashes[alias]
        )
        for slot in slots for alias in aliases
    }
    holdout_commitment = commitment(key, "holdout-bank", sha256(holdout_data))

    artifact_root = primary / "artifacts"
    ensure_private_dir(artifact_root)
    for slot, data in bundles.items():
        write_private(artifact_root / "bundles" / f"{slot}.txt", data)
    for alias, data in fixture_packets.items():
        write_private(artifact_root / "fixtures" / f"{alias}.txt", data)

    mapping = {
        "task_id": TASK_ID,
        "input_stage4_commit": INPUT_COMMIT,
        "slot_to_candidate": slot_candidates,
        "alias_to_original_fixture": alias_indexes,
        "candidate_definition_sha256": definition_hashes,
        "holdout_bank_sha256": sha256(holdout_data),
        "holdout_section_sha256": section_hashes,
        "candidate_bundle_sha256": bundle_hashes,
        "fixture_packet_sha256": packet_hashes,
        "hmac_key_base64": base64.b64encode(key).decode("ascii"),
        "mapping_nonce_base64": base64.b64encode(nonce).decode("ascii"),
        "execution_order": execution_order,
    }
    mapping_bytes = canonical_json(mapping)
    write_private(primary / "blind-mapping.json", mapping_bytes)
    write_private(backup / "blind-mapping.backup.json", mapping_bytes)
    if (primary / "blind-mapping.json").read_bytes() != (backup / "blind-mapping.backup.json").read_bytes():
        raise SystemExit("mapping backup mismatch")

    public = {
        "mapping_commitment_sha256": sha256(mapping_bytes),
        "holdout_bank_hmac_sha256": holdout_commitment,
        "candidate_bundle_hmac_sha256": candidate_commitments,
        "fixture_packet_hmac_sha256": fixture_commitments,
        "execution_pair_hmac_sha256": pair_commitments,
    }
    write_private(primary / "public-commitments.json", canonical_json(public))
    print(canonical_json(public).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
