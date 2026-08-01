from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .errors import STTError
from .runner import Runner


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="stt")
    sub = p.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start")
    start.add_argument("--repo", required=True)
    start.add_argument("--state-root")
    start.add_argument("--include-ignored", action="append", default=[])
    start.add_argument("--allow-unconfined-candidate-execution", action="store_true")
    start.add_argument("--require-final-entrypoint-smoke", action="store_true")
    start.add_argument("--mission-file", required=True)
    for name in ("run", "status", "reconcile"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--task-root", required=True)
    restore = sub.add_parser("restore")
    restore.add_argument("--task-root", required=True)
    restore.add_argument("--destination", required=True)
    return p


def local_state_root(repo: Path) -> Path:
    repo = repo.resolve(strict=True)
    return repo.with_name(f"{repo.name}.stt") / "tasks"


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "start":
            repo = Path(args.repo)
            state_root = Path(args.state_root) if args.state_root else local_state_root(repo)
            if state_root.resolve(strict=False) != local_state_root(repo).resolve(strict=False):
                raise STTError("STATE_ROOT_NONLOCAL", "--state-root must equal the checkout-local default", {"expected": str(local_state_root(repo)), "actual": str(state_root.resolve(strict=False))})
            result = Runner.bootstrap(
                repo=repo,
                state_root=state_root,
                mission=Path(args.mission_file).read_bytes(),
                included_ignored=args.include_ignored,
                allow_unconfined=args.allow_unconfined_candidate_execution,
                require_final_entrypoint_smoke=args.require_final_entrypoint_smoke,
            )
        else:
            runner = Runner(Path(args.task_root), read_only=args.command == "status")
            result = (
                runner.run()
                if args.command == "run"
                else runner.status()
                if args.command == "status"
                else runner.reconcile()
                if args.command == "reconcile"
                else runner.restore(Path(args.destination))
            )
        print(json.dumps(result, sort_keys=True, ensure_ascii=False, separators=(",", ":")))
        return 0
    except STTError as exc:
        print(
            json.dumps(
                {"status": "ERROR", "code": exc.code, "message": exc.message, "details": exc.details},
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
