#!/usr/bin/env python3
"""Credit-free two-step Target Task lifecycle qualification."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from concepts.target_task.boundary import (
    admit_and_persist_transition,
    new_step_cursor_from_plan,
    persist_cursor_transition,
)
from concepts.target_task.contracts import LunaAction, Phase
from concepts.target_task.controller import accept, advance, handoff, prepare, resume, status, validate_execution
from concepts.target_task.executable_plan import persist_execution_manifest
from concepts.target_task.launcher import GenericRecordedLauncher
from concepts.target_task.routing import resolve_route
from concepts.target_task.store import (
    persist_finding_set_artifact,
    persist_plan_artifact,
    write_content_addressed_artifact,
    write_immutable_artifact,
)
from concepts.target_task.trigger import bootstrap_task


ROOT = Path(__file__).resolve().parents[1]


def canonical(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def reference(root: Path, path: str, artifact_type: str) -> dict:
    raw = (root / path).read_bytes()
    return {
        "reference_id": Path(path).stem[:64],
        "repository_relative_path": path,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
        "artifact_type": artifact_type,
        "description": "durable Target Task evidence",
        "read_condition": "read by the deterministic Boundary",
    }


def validation_receipt(task_root: Path, task_id: str, gate: str, subject_ref: dict) -> dict:
    payload = {
        "schema_version": "1", "task_id": task_id, "gate": gate,
        "status": "PASS", "subject_sha256": subject_ref["sha256"],
    }
    ref = write_content_addressed_artifact(
        task_root, "validation", ".json", canonical(payload),
        reference_id=f"validation-{gate}", artifact_type="validation_receipt",
        description=f"deterministic {gate} fixture receipt",
        read_condition="read only by the matching lifecycle gate",
    )
    return {"status": "PASS", "reference": ref}


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="tt-generic-lifecycle-") as tmp:
        base = Path(tmp)
        tasks_root = base / "tasks"
        source_root = base / "source"
        tasks_root.mkdir()
        source_root.mkdir()
        task_id = "generic-smoke"
        mission = "Create hello.txt containing exactly hello, then validate its exact content."
        boot = bootstrap_task(mission, task_id, tasks_root)
        task_root = boot.workspace_root

        admit_and_persist_transition(
            Phase.MISSION_PERSISTED, LunaAction.CONTINUE,
            task_root=task_root, task_id=task_id, event_id="phase-plan-drafted",
        )
        admit_and_persist_transition(
            Phase.PLAN_DRAFTED, LunaAction.CONTINUE,
            task_root=task_root, task_id=task_id, event_id="phase-plan-review",
        )

        worker_instruction = write_immutable_artifact(
            task_root, "instructions/worker.md",
            b"Create hello.txt in the source root containing exactly hello.\n",
            reference_id="worker-instruction", artifact_type="step_instruction",
            description="worker step instruction", read_condition="read only by the worker",
        )
        worker_contract = write_immutable_artifact(
            task_root, "contracts/worker.json",
            canonical({"required_outputs": ["step_result", "routing_evidence"]}),
            reference_id="worker-output-contract", artifact_type="output_contract",
            description="worker output contract", read_condition="read only by worker and Boundary",
        )
        command_instruction = write_immutable_artifact(
            task_root, "instructions/command.md",
            b"Validate that hello.txt contains exactly hello.\n",
            reference_id="command-instruction", artifact_type="step_instruction",
            description="command step instruction", read_condition="read only by the command role",
        )
        command_contract = write_immutable_artifact(
            task_root, "contracts/command.json",
            canonical({"required_outputs": ["command_receipt", "command_log", "routing_evidence"]}),
            reference_id="command-output-contract", artifact_type="output_contract",
            description="command output contract", read_condition="read only by command and Boundary",
        )

        plan = {
            "schema_version": "1", "plan_id": "generic-smoke-plan", "task_id": task_id,
            "mission_sha256": boot.mission_sha256,
            "steps": [
                {"step_id": "write-hello", "objective": "create exact hello file", "role": "worker", "success_criteria": ["hello.txt contains exactly hello"]},
                {"step_id": "validate-hello", "objective": "validate exact hello file", "role": "command", "success_criteria": ["deterministic exact-content validation passes"]},
            ],
        }
        plan_ref = persist_plan_artifact(task_root, plan)
        execution = {
            "schema_version": "1", "task_id": task_id, "sealed_plan_sha256": plan_ref["sha256"],
            "steps": [
                {
                    "step_id": "write-hello", "objective": "create exact hello file", "role": "worker",
                    "instruction_ref": worker_instruction, "task_artifact_references": [],
                    "source_artifact_references": [], "retrieval_recipe_ref": None,
                    "output_contract_ref": worker_contract,
                    "routing_profile": {"provider": "generic-recorded-host", "model_class": "small", "effort": "low", "timeout_seconds": 30, "budget": 0},
                    "scope": "hello.txt only", "authority": "write-source",
                    "prohibitions": ["do not modify Target Task control artifacts"],
                    "validation_commands": [], "success_criteria": ["hello.txt contains exactly hello"],
                    "result_manifest_directory": "results/manifests",
                },
                {
                    "step_id": "validate-hello", "objective": "validate exact hello file", "role": "command",
                    "instruction_ref": command_instruction, "task_artifact_references": [],
                    "source_artifact_references": [], "retrieval_recipe_ref": None,
                    "output_contract_ref": command_contract,
                    "routing_profile": {"provider": "generic-recorded-host", "model_class": "small", "effort": "low", "timeout_seconds": 30, "budget": 0},
                    "scope": "read hello.txt and report exact-content result", "authority": "command-only",
                    "prohibitions": ["do not modify source or Target Task control artifacts"],
                    "validation_commands": ["test $(cat hello.txt) = hello"],
                    "success_criteria": ["deterministic exact-content validation passes"],
                    "result_manifest_directory": "results/manifests",
                },
            ],
        }
        persist_execution_manifest(task_root, plan_ref, plan, execution)

        findings_ref = persist_finding_set_artifact(task_root, {
            "schema_version": "1", "task_id": task_id, "findings": [],
        })
        skeptic_raw = (ROOT / "skeptic.md").read_bytes()
        fix_loop_state = {
            "TARGET_TASK_SHA256": boot.mission_sha256,
            "REVIEWED_ARTIFACT_SHA256": plan_ref["sha256"],
            "SKEPTIC_SOURCE_BLOB_SHA": git_blob_sha(skeptic_raw),
            "APPLICABLE_COMPANION_SET_SHA256": hashlib.sha256(b"generic-smoke-companions-v1").hexdigest(),
            "MATERIAL_FINDINGS_SHA256": findings_ref["sha256"],
            "INVOCATION_KIND": "FIX_LOOP", "PERMISSION_MODE": "fix-if-valid",
            "QUALIFYING_PASSES_REQUIRED": 3, "CONSECUTIVE_QUALIFYING_PASSES": 3,
            "OPEN_ITEMS": [], "MATERIAL_FINDINGS_REFERENCE": findings_ref,
        }
        admit_and_persist_transition(
            Phase.PLAN_REVIEW, LunaAction.ADVANCE,
            task_root=task_root, task_id=task_id, event_id="phase-plan-sealed",
            fix_loop_state=fix_loop_state, material_findings_reference=findings_ref,
            accepted_plan_reference=plan_ref,
            plan_qualification_receipt=validation_receipt(task_root, task_id, "plan_qualification", plan_ref),
        )
        cursor = new_step_cursor_from_plan(plan)
        cursor_state = persist_cursor_transition(
            task_root, task_id, Phase.PLAN_SEALED, cursor,
            event_id="initial-cursor", accepted_plan_reference=plan_ref,
        )
        admit_and_persist_transition(
            Phase.PLAN_SEALED, LunaAction.ADVANCE,
            task_root=task_root, task_id=task_id, event_id="phase-step-executing",
            accepted_plan_reference=plan_ref, cursor=cursor,
            cursor_reference=cursor_state["cursor_reference"],
        )

        receipts = [status(tasks_root, task_id)]

        first = prepare(tasks_root, task_id, source_root=source_root)
        route1 = resolve_route("worker", execution["steps"][0]["routing_profile"])
        def worker_handler(request):
            (source_root / "hello.txt").write_text("hello", encoding="utf-8")
            return {"step_result": "hello.txt created and persisted outside the Lead\n"}
        launch1 = GenericRecordedLauncher(worker_handler).invoke(
            task_root=task_root, source_root=source_root,
            request_ref=reference(task_root, first["request_ref"], "role_request"),
            dispatch_evidence_ref=reference(task_root, first["dispatch_evidence_ref"], "dispatch_evidence"),
            route=route1,
        )
        receipts.extend([first, accept(tasks_root, task_id, launch1.receipt, source_root=source_root), advance(tasks_root, task_id, source_root=source_root)])

        handoff_receipt = handoff(tasks_root, task_id)
        receipts.extend([handoff_receipt, resume(tasks_root, handoff_receipt)])

        second = prepare(tasks_root, task_id, source_root=source_root)
        route2 = resolve_route("command", execution["steps"][1]["routing_profile"])
        def command_handler(request):
            observed = (source_root / "hello.txt").read_text(encoding="utf-8")
            if observed != "hello":
                raise RuntimeError("exact-content validation failed")
            return {
                "command_receipt": canonical({"status": "PASS", "check": "hello.txt exact content"}),
                "command_log": "PASS hello.txt contains exactly hello\n",
            }
        launch2 = GenericRecordedLauncher(command_handler).invoke(
            task_root=task_root, source_root=source_root,
            request_ref=reference(task_root, second["request_ref"], "role_request"),
            dispatch_evidence_ref=reference(task_root, second["dispatch_evidence_ref"], "dispatch_evidence"),
            route=route2,
        )
        receipts.extend([second, accept(tasks_root, task_id, launch2.receipt, source_root=source_root), advance(tasks_root, task_id, source_root=source_root)])
        final = validate_execution(tasks_root, task_id)
        receipts.append(final)

        for item in receipts:
            raw = canonical(item)
            assert len(raw) <= 4096
            lowered = raw.lower()
            for forbidden in (b'"body"', b'"content"', b'"transcript"', b'"patch"', b'"excerpt"'):
                assert forbidden not in lowered
        assert (source_root / "hello.txt").read_text(encoding="utf-8") == "hello"
        assert final["phase"] == Phase.STEP_VALIDATED.value
        print(json.dumps({
            "status": "PASS",
            "task_id": task_id,
            "execution_status": "EXECUTION_COMPLETE",
            "phase": Phase.STEP_VALIDATED.value,
            "accepted_steps": 2,
            "roles": ["worker", "command"],
            "provider": "generic-recorded-host",
            "fresh_session_resume": "PASS",
            "compact_reference_only_receipts": "PASS",
            "closed": False,
            "live_provider_not_run": True,
            "hidden_host_context_isolation": "UNKNOWN",
        }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
