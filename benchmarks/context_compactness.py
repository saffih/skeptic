#!/usr/bin/env python3
"""Compare fixed full-history and compact-current-state packets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def measure(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    result = {"file": str(path.relative_to(ROOT)), "bytes": len(text.encode()), "characters": len(text), "lines": text.count("\n")}
    try:
        import tiktoken  # type: ignore
        result["tokens"] = len(tiktoken.get_encoding("cl100k_base").encode(text))
    except (ImportError, ValueError):
        result["tokens"] = None
    return result


def compare() -> dict:
    full = measure(ROOT / "benchmarks/context/full_history_replay.json")
    compact = measure(ROOT / "benchmarks/context/compact_current_state.json")
    return {"full_history_replay": full, "compact_current_state": compact,
            "skeptic_source_fixed_cost": measure(ROOT / "skeptic.md"),
            "strictly_smaller_bytes": compact["bytes"] < full["bytes"],
            "strictly_smaller_characters": compact["characters"] < full["characters"],
            "hidden_runtime_context": "UNKNOWN"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.parse_args()
    print(json.dumps(compare(), indent=2, sort_keys=True))
