from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path
from typing import Any

from concepts.stt.canonical import canonical_json_bytes, sha256_file
from concepts.stt.runner import Runner


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_bytes(canonical_json_bytes(value))
    os.chmod(path, 0o600)


def done(delivery: str) -> list[dict[str, Any]]:
    semantic = [
        {"id": "objective", "kind": "reviewer_claim", "claim_id": "mission_objective_satisfied", "subject_ref": "frozen_final_candidate"},
        {"id": "clean", "kind": "reviewer_claim", "claim_id": "final_find_loop_clean", "subject_ref": "frozen_final_candidate"},
    ]
    if delivery == "inspect":
        return [
            {"id": "inventory", "kind": "deterministic_predicate", "predicate_id": "inventory_scope_completed", "subject_ref": "inspect_report"},
            {"id": "bound", "kind": "reviewer_claim", "claim_id": "report_bound_to_baseline", "subject_ref": "inspect_report"},
            *semantic,
        ]
    return [
        {"id": "commands", "kind": "deterministic_predicate", "predicate_id": "all_declared_final_commands_succeeded", "subject_ref": "final_evidence"},
        {"id": "paths", "kind": "deterministic_predicate", "predicate_id": "changed_paths_bound_to_workspace", "subject_ref": "final_evidence"},
        *semantic,
    ]


def inspect_step(step_id: str = "inspect", scope: str = ".") -> dict[str, Any]:
    return {"id": step_id, "kind": "inspect", "scope": scope, "operation": "repository_inventory"}


def change_step(step_id: str = "change", path: str = "value.txt") -> dict[str, Any]:
    return {
        "id": step_id,
        "kind": "change",
        "route_profile": "standard",
        "objective": f"change {path}",
        "read_scope": [{"path": path, "kind": "file"}],
        "write_scope": [{"path": path, "kind": "file"}],
        "validation_commands": [],
    }


def task_step(mission: str, step_id: str = "child") -> dict[str, Any]:
    return {"id": step_id, "kind": "task", "mission": mission}


class STTHarness:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.repo = root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "Test"], check=True)
        (self.repo / "skeptic.md").write_text("# Skeptic\n")
        (self.repo / "value.txt").write_text("before\n")
        (self.repo / "src").mkdir(); (self.repo / "src" / "visible.txt").write_text("visible\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "skeptic.md", "value.txt", "src/visible.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "base"], check=True)
        self.state_root = self.repo / ".stt" / "tasks"
        self.review_counter = 0

    def bootstrap(self, mission: bytes = b"mission\n", **kwargs: Any) -> Runner:
        started = Runner.bootstrap(repo=self.repo, state_root=self.state_root, mission=mission, included_ignored=[], **kwargs)
        return Runner(Path(started["task_root"]))

    def write_plan(self, runner: Runner, request: dict[str, Any], request_sha: str, *, delivery: str = "inspect", steps: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        result_dir = runner.task_root / request["result_ref"].rsplit("/", 1)[0]
        plan_path = result_dir / "plan.json"; map_path = result_dir / "finding-map.json"
        plan = {
            "schema_version": 2,
            "mission_sha256": request["mission"]["sha256"],
            "baseline_id": request["baseline_id"],
            "objective": "complete bounded task",
            "done": done(delivery),
            "steps": steps if steps is not None else [inspect_step()],
            "delivery_kind": delivery,
        }
        write_json(plan_path, plan); write_json(map_path, {"findings": []})
        self.write_evidence(runner, request, f"planner-{request['operation_id']}")
        write_json(
            runner.task_root / request["result_ref"],
            {
                "schema_version": 1,
                "operation_id": request["operation_id"],
                "request_sha256": request_sha,
                "kind": "PLAN_CANDIDATE",
                "plan_ref": plan_path.relative_to(runner.task_root).as_posix(),
                "plan_sha256": sha256_file(plan_path),
                "finding_map_ref": map_path.relative_to(runner.task_root).as_posix(),
            },
        )
        return plan

    def write_evidence(self, runner: Runner, request: dict[str, Any], invocation_id: str, *, status: str = "COMPLETE") -> None:
        write_json(
            runner.task_root / request["_provider_evidence_ref"],
            {"provider_id": "generic-recorded-host", "invocation_id": invocation_id, "status": status, "timed_out": False, "exit_code": 0},
        )

    def write_review(self, runner: Runner, request: dict[str, Any], request_sha: str, *, disposition: str = "PASS") -> None:
        self.review_counter += 1
        result_dir = runner.task_root / request["result_ref"].rsplit("/", 1)[0]
        receipt = result_dir / "review.json"; findings = result_dir / "findings.json"
        invocation = f"review-{self.review_counter}-{request['operation_id']}"
        finding_items: list[dict[str, Any]] = [] if disposition == "PASS" else [{"id": "finding", "message": "repair"}]
        write_json(receipt, {"verdict": disposition, "subject_sha256": request["subject"]["sha256"]})
        write_json(findings, {"findings": finding_items})
        self.write_evidence(runner, request, invocation)
        write_json(
            runner.task_root / request["result_ref"],
            {
                "schema_version": 1,
                "operation_id": request["operation_id"],
                "request_sha256": request_sha,
                "protocol_outcome": "COMPLETE",
                "review_disposition": disposition,
                "runskeptic_final_outcome": "PASS" if disposition == "PASS" else "ACTION",
                "receipt_ref": receipt.relative_to(runner.task_root).as_posix(),
                "findings_ref": findings.relative_to(runner.task_root).as_posix(),
                "subject_sha256": request["subject"]["sha256"],
                "session_id": invocation,
                "claims": request["required_claims"] if request["purpose"] == "final_review" and disposition == "PASS" else [],
            },
        )

    def write_needs_evidence(self, runner: Runner, request: dict[str, Any], request_sha: str) -> None:
        self.write_evidence(runner, request, f"evidence-{request['operation_id']}")
        write_json(
            runner.task_root / request["result_ref"],
            {
                "schema_version": 1,
                "operation_id": request["operation_id"],
                "request_sha256": request_sha,
                "kind": "NEEDS_EVIDENCE",
                "selectors": [{"kind": "workspace_path", "path": "src/visible.txt"}],
            },
        )

    def write_worker(self, runner: Runner, request: dict[str, Any], request_sha: str, *, body: str = "worker\n") -> None:
        target = Path(request["capsule_path"]) / request["step"]["write_scope"][0]["path"]
        target.parent.mkdir(parents=True, exist_ok=True); target.write_text(body)
        self.write_evidence(runner, request, f"worker-{request['operation_id']}")
        write_json(
            runner.task_root / request["result_ref"],
            {
                "schema_version": 1,
                "operation_id": request["operation_id"],
                "request_sha256": request_sha,
                "kind": "WORKER_RESULT",
                "step_id": request["step"]["id"],
                "summary": "changed",
                "declared_outputs": [],
            },
        )

    def pending(self, runner: Runner) -> tuple[dict[str, Any], Any]:
        pending = runner._pending_operation()
        if pending is None:
            raise AssertionError(f"pending operation expected: {runner.status()}")
        return pending

    def process_effect_only(self, runner: Runner) -> tuple[dict[str, Any], Any, dict[str, Any]]:
        request, request_ref = self.pending(runner)
        adopted = runner._adopt_result(request)
        if adopted is None:
            raise AssertionError("staged result was not adoptable")
        result, result_ref, provider_report, evidence_ref = adopted
        if request["role"] == "planner":
            runner._process_planner_result(request, result, result_ref, evidence_ref)
        elif request["role"] == "reviewer":
            runner._process_reviewer_result(request, result, result_ref, provider_report, evidence_ref)
        else:
            runner._process_worker_result(request, result, result_ref, evidence_ref)
        effects = runner._effect_records(request["operation_id"])
        if len(effects) != 1:
            raise AssertionError(f"one role effect expected, found {len(effects)}")
        return request, request_ref, effects[0]

    def accept_effect_only(self, runner: Runner) -> tuple[dict[str, Any], Any, dict[str, Any]]:
        request, request_ref, effect = self.process_effect_only(runner)
        runner._accept_effect(request, request_ref, effect)
        return request, request_ref, effect

    def stage_plan_reviews(self, runner: Runner, *, delivery: str = "inspect", steps: list[dict[str, Any]] | None = None, accepted_reviews: int = 0) -> Runner:
        request, ref = self.pending(runner); self.write_plan(runner, request, ref.sha256, delivery=delivery, steps=steps); runner.run()
        for _ in range(accepted_reviews):
            request, ref = self.pending(runner); self.write_review(runner, request, ref.sha256); runner.run()
        return Runner(runner.task_root)

    def stage_final_reviews(self, runner: Runner, *, accepted_reviews: int = 0) -> Runner:
        for _ in range(accepted_reviews):
            request, ref = self.pending(runner); self.write_review(runner, request, ref.sha256); runner.run()
        return Runner(runner.task_root)

    def complete(self, runner: Runner, *, plans: dict[str, tuple[str, list[dict[str, Any]]]] | None = None) -> Runner:
        for _ in range(96):
            status = runner.status()
            if status["status"] in {"COMPLETE", "FAILED", "BLOCKED_UNKNOWN"}:
                return runner
            pending = runner._pending_operation()
            if pending is None:
                runner.run(); continue
            request, ref = pending
            if request["role"] == "planner":
                delivery, steps = (plans or {}).get(request["mission"]["sha256"], ("inspect", [inspect_step()]))
                self.write_plan(runner, request, ref.sha256, delivery=delivery, steps=steps)
            elif request["role"] == "reviewer":
                self.write_review(runner, request, ref.sha256)
            else:
                self.write_worker(runner, request, ref.sha256)
            runner.run()
        raise AssertionError(f"completion cycle exceeded: {runner.status()}")

    @staticmethod
    def mission_sha(mission: str) -> str:
        return hashlib.sha256(mission.encode("utf-8")).hexdigest()
