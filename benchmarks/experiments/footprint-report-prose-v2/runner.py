#!/usr/bin/env python3
"""Paired A/B runner for the footprint-report-prose-v2 experiment.

Executes prepared benchmark prompts against Codex CLI (gpt-5.6-sol,
effort high, read-only sandbox, ephemeral, no web) with a fresh isolated
empty temporary working directory per response. Pair order (which arm
runs first) and pair sequence are randomized with a recorded seed.
Writes raw responses and run metadata incrementally so partial progress
survives interruption. Stdlib only; does not modify benchmark files.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CODEX_ARGS = [
    "codex", "exec",
    "--ephemeral", "--ignore-rules", "--ignore-user-config",
    "--skip-git-repo-check",
    "-m", "gpt-5.6-sol",
    "-c", "model_reasoning_effort=high",
    "-s", "read-only",
    "--color", "never",
    "--json",
]
RUN_TIMEOUT_SECONDS = 900
MAX_ATTEMPTS = 2

RUNTIME_METADATA = {
    "model": "gpt-5.6-sol",
    "version": "not exposed by Codex CLI 0.145.0",
    "effort": "high",
    "provider": "OpenAI",
    "runtime": "Codex CLI 0.145.0 via ChatGPT authentication",
    "settings": {
        "ephemeral": True,
        "ignore_rules": True,
        "ignore_user_config": True,
        "maximum_output_tokens": None,
        "sandbox": "read-only",
        "temperature": None,
        "top_p": None,
        "web_search": False,
        "working_directory": "fresh isolated empty temporary directory",
    },
    "context_isolation": (
        "new codex exec --ephemeral process in a fresh empty temp directory "
        "for each response"
    ),
    "fresh_context_per_response": True,
}


def load_prompts(path: Path) -> dict[str, str]:
    packet = json.loads(path.read_text(encoding="utf-8"))
    return {p["case_id"]: p["prompt"] for p in packet["prompts"]}


def extract_usage(jsonl_text: str) -> dict:
    usage: dict = {}
    model_seen = None
    for line in jsonl_text.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            info = event.get("usage") or (event.get("msg") or {}).get("usage") \
                if isinstance(event.get("msg"), dict) else event.get("usage")
            if isinstance(info, dict):
                usage = info
            for key in ("model",):
                found = event.get(key) or (
                    event.get("msg", {}).get(key)
                    if isinstance(event.get("msg"), dict) else None
                )
                if isinstance(found, str):
                    model_seen = found
    return {"usage": usage, "model_reported": model_seen}


def run_once(prompt: str, events_path: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="skeptic-exp-v2-") as workdir:
        last_path = Path(workdir) / "last-message.txt"
        started = time.monotonic()
        proc = subprocess.run(
            [*CODEX_ARGS, "-o", str(last_path), "-"],
            input=prompt,
            capture_output=True,
            text=True,
            cwd=workdir,
            timeout=RUN_TIMEOUT_SECONDS,
        )
        elapsed = time.monotonic() - started
        response = last_path.read_text(encoding="utf-8") if last_path.exists() else ""
        events_path.write_text(proc.stdout, encoding="utf-8")
        return {
            "response": response,
            "elapsed_seconds": round(elapsed, 3),
            "exit_code": proc.returncode,
            "stderr_tail": proc.stderr[-2000:],
            **extract_usage(proc.stdout),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-prompts", type=Path, required=True)
    parser.add_argument("--candidate-prompts", type=Path, required=True)
    parser.add_argument("--cases", required=True,
                        help="comma-separated case ids")
    parser.add_argument("--reps", type=int, default=1)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--events-dir", type=Path, required=True)
    args = parser.parse_args()

    control = load_prompts(args.control_prompts)
    candidate = load_prompts(args.candidate_prompts)
    case_ids = [c.strip() for c in args.cases.split(",") if c.strip()]
    missing = [c for c in case_ids if c not in control or c not in candidate]
    if missing:
        print(f"ERROR: cases missing from packets: {missing}", file=sys.stderr)
        return 2

    rng = random.Random(args.seed)
    pairs = [(case_id, rep) for case_id in case_ids
             for rep in range(1, args.reps + 1)]
    rng.shuffle(pairs)
    schedule = []
    for case_id, rep in pairs:
        arms = ["control", "candidate"]
        rng.shuffle(arms)
        for arm in arms:
            schedule.append({"case_id": case_id, "rep": rep, "arm": arm})

    args.events_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "schema_version": "skeptic-exp-v2-raw/1",
        "seed": args.seed,
        "reps": args.reps,
        "case_ids": case_ids,
        "runtime_metadata": RUNTIME_METADATA,
        "schedule": schedule,
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "runs": [],
    }
    if args.output.exists():
        previous = json.loads(args.output.read_text(encoding="utf-8"))
        if previous.get("seed") == args.seed and previous.get("schedule") == schedule:
            result = previous
            print(f"RESUME: {len(result['runs'])} runs already recorded")

    done = {(r["case_id"], r["rep"], r["arm"]) for r in result["runs"]}
    prompts = {"control": control, "candidate": candidate}
    for index, slot in enumerate(schedule, 1):
        key = (slot["case_id"], slot["rep"], slot["arm"])
        if key in done:
            continue
        label = f"{slot['case_id']}.rep{slot['rep']}.{slot['arm']}"
        events_path = args.events_dir / f"{label}.jsonl"
        record = {**slot, "order_index": index, "attempts": []}
        for attempt in range(1, MAX_ATTEMPTS + 1):
            print(f"[{index}/{len(schedule)}] {label} attempt {attempt}",
                  flush=True)
            try:
                run = run_once(prompts[slot["arm"]][slot["case_id"]], events_path)
            except subprocess.TimeoutExpired:
                run = {"response": "", "elapsed_seconds": RUN_TIMEOUT_SECONDS,
                       "exit_code": None, "stderr_tail": "TIMEOUT",
                       "usage": {}, "model_reported": None}
            record["attempts"].append(
                {"attempt": attempt, "exit_code": run["exit_code"],
                 "elapsed_seconds": run["elapsed_seconds"],
                 "empty": not run["response"].strip()})
            if run["response"].strip() and run["exit_code"] == 0:
                break
        record.update(run)
        result["runs"].append(record)
        result["updated_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        args.output.write_text(json.dumps(result, indent=2) + "\n",
                               encoding="utf-8")
    result["completed_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    empty = [r for r in result["runs"] if not r["response"].strip()]
    print(f"DONE: {len(result['runs'])} runs, {len(empty)} empty")
    return 1 if empty else 0


if __name__ == "__main__":
    raise SystemExit(main())
