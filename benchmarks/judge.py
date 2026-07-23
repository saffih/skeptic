#!/usr/bin/env python3
"""Deterministic blinded human-judgment packet helper."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path


CHOICES = {"A better", "B better", "tie", "unusable"}


class JudgeError(ValueError):
    pass


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise JudgeError(f"cannot read JSON {path}: {exc}") from exc


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def response_map(value) -> dict[str, str]:
    records = value.get("responses") if isinstance(value, dict) else value
    if not isinstance(records, list):
        raise JudgeError("response set must be a list or contain responses")
    result: dict[str, str] = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("case_id"), str):
            raise JudgeError("each response needs a string case_id")
        if not isinstance(record.get("response"), str):
            raise JudgeError(f"{record['case_id']}: response must be a string")
        if record["case_id"] in result:
            raise JudgeError(f"duplicate case_id: {record['case_id']}")
        result[record["case_id"]] = record["response"]
    return result


def build_blind_packet(a_value, b_value, seed: int) -> tuple[dict, dict]:
    a = response_map(a_value)
    b = response_map(b_value)
    if set(a) != set(b):
        raise JudgeError("A and B must contain exactly the same case IDs")
    packet_cases = []
    key_cases = []
    for case_id in sorted(a):
        rng = random.Random(f"{seed}:{case_id}")
        a_first = bool(rng.getrandbits(1))
        if a_first:
            response_a, response_b = a[case_id], b[case_id]
            source_a, source_b = "input_a", "input_b"
        else:
            response_a, response_b = b[case_id], a[case_id]
            source_a, source_b = "input_b", "input_a"
        packet_cases.append(
            {"case_id": case_id, "response_A": response_a, "response_B": response_b}
        )
        key_cases.append(
            {"case_id": case_id, "source_for_A": source_a, "source_for_B": source_b}
        )
    return (
        {"schema_version": "skeptic-blind-packet/1", "seed": seed, "cases": packet_cases},
        {"schema_version": "skeptic-blind-key/1", "seed": seed, "cases": key_cases},
    )


def reveal_judgments(judgments: dict, key: dict) -> dict:
    records = judgments.get("judgments")
    if not isinstance(records, list):
        raise JudgeError("judgments must contain a judgments list")
    key_by_id = {record["case_id"]: record for record in key.get("cases", [])}
    revealed = []
    for record in records:
        case_id = record.get("case_id")
        choice = record.get("choice")
        if case_id not in key_by_id:
            raise JudgeError(f"unknown judgment case_id: {case_id}")
        if choice not in CHOICES:
            raise JudgeError(f"{case_id}: invalid choice {choice!r}")
        mapping = key_by_id[case_id]
        if choice == "A better":
            winner = mapping["source_for_A"]
        elif choice == "B better":
            winner = mapping["source_for_B"]
        else:
            winner = choice
        revealed.append({"case_id": case_id, "choice": choice, "winner": winner})
    return {"schema_version": "skeptic-revealed-judgments/1", "judgments": revealed}


def command_blind(args) -> int:
    packet, key = build_blind_packet(read_json(args.a), read_json(args.b), args.seed)
    write_json(args.output, packet)
    write_json(args.key_output, key)
    print(f"BLINDED: {len(packet['cases'])} cases, seed={args.seed}")
    return 0


def command_reveal(args) -> int:
    revealed = reveal_judgments(read_json(args.judgments), read_json(args.key))
    write_json(args.output, revealed)
    print(f"REVEALED: {len(revealed['judgments'])} judgments")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    blind = sub.add_parser("blind")
    blind.add_argument("--a", type=Path, required=True)
    blind.add_argument("--b", type=Path, required=True)
    blind.add_argument("--output", type=Path, required=True)
    blind.add_argument("--key-output", type=Path, required=True)
    blind.add_argument("--seed", type=int, required=True)
    blind.set_defaults(func=command_blind)
    reveal = sub.add_parser("reveal")
    reveal.add_argument("--judgments", type=Path, required=True)
    reveal.add_argument("--key", type=Path, required=True)
    reveal.add_argument("--output", type=Path, required=True)
    reveal.set_defaults(func=command_reveal)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (JudgeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
