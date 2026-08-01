#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from concepts.stt.canonical import canonical_json_bytes, sha256_file
from concepts.stt.runner import Runner


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_bytes(canonical_json_bytes(value))
    os.chmod(path, 0o600)


def provider_evidence(request: dict, invocation_id: str) -> None:
    write_json(
        Path(request["_task_root"]) / request["_provider_evidence_ref"],
        {"provider_id": "generic-recorded-host", "invocation_id": invocation_id, "status": "COMPLETE", "timed_out": False, "exit_code": 0},
    )


def complete_planner(request: dict) -> None:
    task_root = Path(request["_task_root"]); result_dir = task_root / request["result_ref"].rsplit('/', 1)[0]
    plan_path = result_dir / "plan.json"; map_path = result_dir / "finding-map.json"
    plan = {
        "schema_version": 2,
        "mission_sha256": request["mission"]["sha256"],
        "baseline_id": request["baseline_id"],
        "objective": "replace app.txt with the required repaired value",
        "delivery_kind": "workspace_change",
        "done": [
            {"id": "tests", "kind": "deterministic_predicate", "predicate_id": "all_declared_final_commands_succeeded", "subject_ref": "final_evidence"},
            {"id": "bound", "kind": "deterministic_predicate", "predicate_id": "changed_paths_bound_to_workspace", "subject_ref": "frozen_evidence"},
            {"id": "objective", "kind": "reviewer_claim", "claim_id": "mission_objective_satisfied", "subject_ref": "frozen_final_candidate"},
            {"id": "clean", "kind": "reviewer_claim", "claim_id": "final_find_loop_clean", "subject_ref": "frozen_final_candidate"},
        ],
        "steps": [
            {
                "id": "repair-app",
                "kind": "change",
                "route_profile": "standard",
                "objective": "write repaired content",
                "read_scope": [{"path": "app.txt", "kind": "file"}],
                "write_scope": [{"path": "app.txt", "kind": "file"}],
                "validation_commands": [],
            }
        ],
    }
    write_json(plan_path, plan); write_json(map_path, {"findings": []})
    invocation = "smoke-planner-1"; provider_evidence(request, invocation)
    write_json(task_root / request["result_ref"], {
        "schema_version": 1, "operation_id": request["operation_id"], "request_sha256": request["_request_sha256"],
        "kind": "PLAN_CANDIDATE", "plan_ref": plan_path.relative_to(task_root).as_posix(), "plan_sha256": sha256_file(plan_path),
        "finding_map_ref": map_path.relative_to(task_root).as_posix(),
    })


def complete_reviewer(request: dict, ordinal: int, final: bool) -> None:
    task_root = Path(request["_task_root"]); result_dir = task_root / request["result_ref"].rsplit('/', 1)[0]
    receipt_path = result_dir / "review-receipt.json"; findings_path = result_dir / "findings.json"
    invocation = f"smoke-{'final' if final else 'plan'}-review-{ordinal}"
    write_json(receipt_path, {"verdict": "PASS", "invocation_id": invocation, "subject_sha256": request["subject"]["sha256"]})
    write_json(findings_path, {"findings": []})
    provider_evidence(request, invocation)
    write_json(task_root / request["result_ref"], {
        "schema_version": 1, "operation_id": request["operation_id"], "request_sha256": request["_request_sha256"],
        "protocol_outcome": "COMPLETE", "review_disposition": "PASS", "runskeptic_final_outcome": "PASS",
        "receipt_ref": receipt_path.relative_to(task_root).as_posix(), "findings_ref": findings_path.relative_to(task_root).as_posix(),
        "subject_sha256": request["subject"]["sha256"], "session_id": invocation,
        "claims": ["mission_objective_satisfied", "final_find_loop_clean"] if final else [],
    })


def complete_worker(request: dict) -> None:
    task_root = Path(request["_task_root"]); capsule = Path(request["capsule_path"])
    (capsule / "app.txt").write_text("repaired\n", encoding="utf-8")
    invocation = "smoke-worker-1"; provider_evidence(request, invocation)
    write_json(task_root / request["result_ref"], {
        "schema_version": 1, "operation_id": request["operation_id"], "request_sha256": request["_request_sha256"],
        "kind": "WORKER_RESULT", "step_id": request["step"]["id"], "summary": "repaired app.txt", "declared_outputs": [],
    })


def pending_request(runner: Runner) -> dict:
    pending = runner._pending_operation()
    if pending is None:
        raise AssertionError("expected pending semantic operation")
    request, request_ref = pending
    request["_task_root"] = str(runner.task_root)
    request["_request_sha256"] = request_ref.sha256
    return request


def main() -> int:
    os.environ["STT_PROVIDER"] = "generic-recorded-host"
    with tempfile.TemporaryDirectory(prefix="stt-smoke-") as td:
        root = Path(td); repo = root / "repo"; repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "smoke@example.com"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "Smoke"], check=True)
        (repo / "skeptic.md").write_text("# Skeptic\n", encoding="utf-8")
        (repo / "skeptic-questions.md").write_text("# Questions\n", encoding="utf-8")
        (repo / ".gitignore").write_text("ignored.secret\n", encoding="utf-8")
        (repo / "app.txt").write_text("broken\n", encoding="utf-8")
        (repo / "ignored.secret").write_text("preserve me\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "skeptic.md", "skeptic-questions.md", ".gitignore", "app.txt"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
        head_before = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        index_before = subprocess.check_output(["git", "-C", str(repo), "ls-files", "--stage", "-z"])
        receipt = Runner.bootstrap(repo=repo, state_root=repo / ".stt" / "tasks", mission=b"repair app\n", included_ignored=[])
        runner = Runner(Path(receipt["task_root"])); plan_reviews = 0; final_reviews = 0
        for _ in range(32):
            status = runner.status()
            if status["status"] == "COMPLETE":
                break
            request = pending_request(runner)
            if request["role"] == "planner":
                complete_planner(request)
            elif request["role"] == "worker":
                complete_worker(request)
            elif request["purpose"] == "plan_review":
                plan_reviews += 1; complete_reviewer(request, plan_reviews, False)
            elif request["purpose"] == "final_review":
                final_reviews += 1; complete_reviewer(request, final_reviews, True)
            else:
                raise AssertionError(request)
            runner.run()
        else:
            raise AssertionError("smoke cycle bound exceeded")
        final = runner.status()
        assert final["status"] == "COMPLETE", final
        assert plan_reviews == 3 and final_reviews == 3
        assert (repo / "app.txt").read_text() == "repaired\n"
        assert (repo / "ignored.secret").read_text() == "preserve me\n"
        assert subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip() == head_before
        assert subprocess.check_output(["git", "-C", str(repo), "ls-files", "--stage", "-z"]) == index_before
        print(json.dumps({"status": "PASS", "plan_reviews": plan_reviews, "final_reviews": final_reviews, "outcome": final["status"], "dynamic_execution": "sandbox_required", "dynamic_commands": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
