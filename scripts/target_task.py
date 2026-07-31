#!/usr/bin/env python3
"""Compact command-line interface for the Target Task controller."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from concepts.target_task.controller import (
    ControllerError, accept, advance, bootstrap, handoff, prepare, resume, retry,
    status, stop, validate_execution,
)


def _json_file(path: str) -> dict:
    raw = Path(path).read_bytes()
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ControllerError(f"JSON object required: {path}")
    return value


def _emit(value: dict) -> int:
    sys.stdout.write(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="target-task")
    p.add_argument("--tasks-root", required=True)
    p.add_argument("--task-id")
    sub = p.add_subparsers(dest="command", required=True)

    b = sub.add_parser("bootstrap")
    b.add_argument("--message", required=True)
    b.add_argument("--lead-profile", required=True)
    b.add_argument("--current-provider")

    sub.add_parser("status")

    prep = sub.add_parser("prepare")
    prep.add_argument("--source-root", required=True)
    prep.add_argument("--current-provider")

    a = sub.add_parser("accept")
    a.add_argument("--source-root", required=True)
    a.add_argument("--receipt", required=True)

    adv = sub.add_parser("advance")
    adv.add_argument("--source-root", required=True)

    sub.add_parser("retry")

    st = sub.add_parser("stop")
    st.add_argument("--blocker", default="STOP_REQUESTED")

    sub.add_parser("handoff")

    r = sub.add_parser("resume")
    r.add_argument("--handoff", required=True)

    sub.add_parser("validate")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    tasks_root = Path(args.tasks_root)
    if args.command != "bootstrap" and args.task_id is None and args.command != "resume":
        raise ControllerError("--task-id is required")
    if args.command == "bootstrap":
        if args.task_id is None:
            raise ControllerError("--task-id is required")
        result = bootstrap(
            args.message, args.task_id, tasks_root,
            lead_profile=_json_file(args.lead_profile), current_provider=args.current_provider,
        )
    elif args.command == "status":
        result = status(tasks_root, args.task_id)
    elif args.command == "prepare":
        result = prepare(tasks_root, args.task_id, source_root=Path(args.source_root), current_provider=args.current_provider)
    elif args.command == "accept":
        result = accept(tasks_root, args.task_id, _json_file(args.receipt), source_root=Path(args.source_root))
    elif args.command == "advance":
        result = advance(tasks_root, args.task_id, source_root=Path(args.source_root))
    elif args.command == "retry":
        result = retry(tasks_root, args.task_id)
    elif args.command == "stop":
        result = stop(tasks_root, args.task_id, blocker=args.blocker)
    elif args.command == "handoff":
        result = handoff(tasks_root, args.task_id)
    elif args.command == "resume":
        result = resume(tasks_root, _json_file(args.handoff))
    else:
        result = validate_execution(tasks_root, args.task_id)
    return _emit(result)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ControllerError, OSError, json.JSONDecodeError) as exc:
        sys.stderr.write(json.dumps({"status": "BLOCKED", "error": str(exc)}, sort_keys=True) + "\n")
        raise SystemExit(2)
