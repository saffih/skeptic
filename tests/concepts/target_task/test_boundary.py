import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from concepts.target_task.boundary import (
    BoundaryError,
    admit_transition,
    advance_find_loop,
    build_luna_receipt,
    find_loop_complete,
    new_step_cursor,
)
from concepts.target_task.contracts import (
    CursorStatus, LedgerEvent, LunaAction, Phase, StepCursor,
    canonical_candidate_manifest_bytes, canonical_remote_verification_manifest_bytes,
)
from concepts.target_task.store import (
    AppendOnlyLedger,
    persist_cursor_snapshot,
    persist_finding_set_artifact,
    persist_plan_artifact,
    write_immutable_artifact,
)
from concepts.target_task.trigger import bootstrap_task

ROOT = Path(__file__).resolve().parents[3]


def blob_digest(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def write_gate_receipt(root: Path, task_id: str, gate: str, subject_ref):
    payload = {
        "schema_version": "1",
        "task_id": task_id,
        "gate": gate,
        "status": "PASS",
        "subject_sha256": subject_ref["sha256"],
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    ref = write_immutable_artifact(
        root,
        f"receipts/{gate}.json",
        raw,
        reference_id=f"{gate}-receipt",
        artifact_type="validation_receipt",
        description=f"{gate} receipt",
        read_condition="admit the bound gate",
    )
    return {"status": "PASS", "reference": ref}


def empty_findings(root: Path, task_id: str):
    return persist_finding_set_artifact(
        root,
        {"schema_version": "1", "task_id": task_id, "findings": []},
    )


def make_plan(root: Path, task_id: str, mission_sha: str):
    return persist_plan_artifact(
        root,
        {
            "schema_version": "1",
            "plan_id": "p-1",
            "task_id": task_id,
            "mission_sha256": mission_sha,
            "steps": [
                {
                    "step_id": "s1",
                    "objective": "one bounded step",
                    "role": "worker",
                    "success_criteria": ["done"],
                }
            ],
        },
    )


class PhaseGateTests(unittest.TestCase):
    def test_plan_cannot_seal_without_complete_bound_fix_loop(self):
        with tempfile.TemporaryDirectory() as tmp:
            boot = bootstrap_task("mission", "task-1", Path(tmp))
            root = boot.workspace_root
            plan_ref = make_plan(root, "task-1", boot.mission_sha256)
            findings_ref = empty_findings(root, "task-1")
            state = {
                "TARGET_TASK_SHA256": boot.mission_sha256,
                "REVIEWED_ARTIFACT_SHA256": plan_ref["sha256"],
                "SKEPTIC_SOURCE_BLOB_SHA": "c" * 40,
                "APPLICABLE_COMPANION_SET_SHA256": "d" * 64,
                "MATERIAL_FINDINGS_SHA256": findings_ref["sha256"],
                "MATERIAL_FINDINGS_REFERENCE": findings_ref,
                "INVOCATION_KIND": "FIX_LOOP",
                "PERMISSION_MODE": "fix-if-valid",
                "QUALIFYING_PASSES_REQUIRED": 3,
                "CONSECUTIVE_QUALIFYING_PASSES": 3,
                "OPEN_ITEMS": [],
            }
            with self.assertRaises(BoundaryError):
                admit_transition(
                    Phase.PLAN_REVIEW,
                    LunaAction.ADVANCE,
                    task_root=root,
                    task_id="task-1",
                    fix_loop_state={**state, "CONSECUTIVE_QUALIFYING_PASSES": 2},
                    material_findings_reference=findings_ref,
                    accepted_plan_reference=plan_ref,
                )
            receipt = write_gate_receipt(root, "task-1", "plan_qualification", plan_ref)
            result = admit_transition(
                Phase.PLAN_REVIEW,
                LunaAction.ADVANCE,
                task_root=root,
                task_id="task-1",
                fix_loop_state=state,
                material_findings_reference=findings_ref,
                accepted_plan_reference=plan_ref,
                plan_qualification_receipt=receipt,
            )
            self.assertEqual(result.phase, Phase.PLAN_SEALED)

    def test_execution_cannot_validate_before_persisted_complete_cursor(self):
        with tempfile.TemporaryDirectory() as tmp:
            boot = bootstrap_task("mission", "task-1", Path(tmp))
            root = boot.workspace_root
            plan_ref = make_plan(root, "task-1", boot.mission_sha256)
            incomplete = new_step_cursor(("s1",))
            with self.assertRaises(BoundaryError):
                admit_transition(
                    Phase.STEP_EXECUTING,
                    LunaAction.ADVANCE,
                    task_root=root,
                    task_id="task-1",
                    accepted_plan_reference=plan_ref,
                    cursor=incomplete,
                    cursor_reference=None,
                )

            complete = StepCursor(
                ("s1",),
                current_index=1,
                status=CursorStatus.EXECUTION_COMPLETE,
                completed_step_ids=("s1",),
            )
            cursor_ref = persist_cursor_snapshot(root, complete)
            ledger = AppendOnlyLedger(root / "ledger.jsonl")
            sequence, previous_hash = ledger.head()
            ledger.append(
                LedgerEvent(
                    schema_version="1",
                    sequence=sequence,
                    event_id="task-1:execution-complete",
                    task_id="task-1",
                    phase=Phase.STEP_EXECUTING.value,
                    accepted_plan_ref=plan_ref["repository_relative_path"],
                    current_step=None,
                    operation_id=None,
                    attempt=1,
                    request_ref=None,
                    result_ref=None,
                    cursor_ref=cursor_ref["repository_relative_path"],
                    status="EXECUTION_COMPLETE",
                    validation="PASS",
                    blocker=None,
                    allowed_actions=(LunaAction.ADVANCE.value, LunaAction.STOP.value),
                    next_action=LunaAction.ADVANCE.value,
                    previous_event_hash=previous_hash,
                    receipt_ref=None,
                )
            )
            self.assertEqual(
                admit_transition(
                    Phase.STEP_EXECUTING,
                    LunaAction.ADVANCE,
                    task_root=root,
                    task_id="task-1",
                    accepted_plan_reference=plan_ref,
                    cursor=complete,
                    cursor_reference=cursor_ref,
                ).phase,
                Phase.STEP_VALIDATED,
            )

    def test_freeze_integration_and_close_are_subject_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            boot = bootstrap_task("mission", "task-1", Path(tmp))
            root = boot.workspace_root
            candidate = {
                "schema_version": "1", "task_id": "task-1", "base_commit": "1" * 40,
                "candidate_commit": "2" * 40, "candidate_tree": "3" * 40,
                "sealed_plan_sha256": "a" * 64, "completed_cursor_sha256": "b" * 64,
            }
            candidate_ref = write_immutable_artifact(
                root,
                "candidate/manifest.json",
                canonical_candidate_manifest_bytes(candidate),
                reference_id="candidate",
                artifact_type="candidate_manifest",
                description="frozen candidate",
                read_condition="validate and review",
            )
            validation = write_gate_receipt(root, "task-1", "deterministic_validation", candidate_ref)
            self.assertEqual(
                admit_transition(
                    Phase.STEP_VALIDATED,
                    LunaAction.ADVANCE,
                    task_root=root,
                    task_id="task-1",
                    candidate_reference=candidate_ref,
                    deterministic_validation_receipt=validation,
                ).phase,
                Phase.CANDIDATE_FROZEN,
            )

            findings_ref = empty_findings(root, "task-1")
            state = {
                "TARGET_TASK_SHA256": boot.mission_sha256,
                "REVIEWED_ARTIFACT_SHA256": candidate_ref["sha256"],
                "SKEPTIC_SOURCE_BLOB_SHA": "c" * 40,
                "APPLICABLE_COMPANION_SET_SHA256": "d" * 64,
                "MATERIAL_FINDINGS_SHA256": findings_ref["sha256"],
                "MATERIAL_FINDINGS_REFERENCE": findings_ref,
                "INVOCATION_KIND": "FIND_LOOP",
                "PERMISSION_MODE": "read-only",
                "CONSECUTIVE_STABLE_PASSES": 3,
                "PASSES_REQUIRED": 3,
                "OPEN_ITEMS": [],
            }
            integration = write_gate_receipt(root, "task-1", "integration", candidate_ref)
            self.assertEqual(
                admit_transition(
                    Phase.FINAL_REVIEW,
                    LunaAction.ADVANCE,
                    task_root=root,
                    task_id="task-1",
                    candidate_reference=candidate_ref,
                    find_loop_state=state,
                    material_findings_reference=findings_ref,
                    integration_receipt=integration,
                ).phase,
                Phase.INTEGRATED,
            )

            remote = {
                "schema_version": "1", "task_id": "task-1", "remote_name": "origin",
                "remote_ref": "refs/heads/main", "expected_commit": "2" * 40,
                "expected_tree": "3" * 40, "observed_commit": "2" * 40,
                "observed_tree": "3" * 40,
            }
            remote_ref = write_immutable_artifact(
                root,
                "remote/manifest.json",
                canonical_remote_verification_manifest_bytes(remote),
                reference_id="remote",
                artifact_type="remote_verification_manifest",
                description="verified remote state",
                read_condition="close the task",
            )
            remote_receipt = write_gate_receipt(root, "task-1", "remote_verification", remote_ref)
            self.assertEqual(
                admit_transition(
                    Phase.INTEGRATED,
                    LunaAction.ADVANCE,
                    task_root=root,
                    task_id="task-1",
                    candidate_reference=candidate_ref,
                    remote_state_reference=remote_ref,
                    remote_verification_receipt=remote_receipt,
                ).phase,
                Phase.CLOSED,
            )

    def test_recovery_requires_durable_proof(self):
        with self.assertRaises(BoundaryError):
            admit_transition(Phase.BLOCKED, LunaAction.RECOVER, resume_phase=Phase.STEP_EXECUTING)


class LunaReceiptTests(unittest.TestCase):
    def test_task_root_is_the_only_artifact_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = root / "plans/p.json"
            plan.parent.mkdir()
            plan.write_text("{}\n")
            digest = hashlib.sha256(plan.read_bytes()).hexdigest()
            state = {
                "TASK_ID": "task-1",
                "SEALED_PLAN_REFERENCE": "plans/p.json",
                "SEALED_PLAN_SHA256": digest,
                "CURRENT_STEP": "s1",
                "COMPLETED_STEP_IDS": [],
                "VALIDATED_FACTS": [],
                "OPEN_BLOCKERS": [],
                "ARTIFACT_REFERENCES": [
                    {
                        "reference_id": "plan",
                        "repository_relative_path": "plans/p.json",
                        "sha256": digest,
                        "byte_size": plan.stat().st_size,
                        "artifact_type": "plan",
                        "description": "sealed plan",
                        "read_condition": "step dispatch",
                    }
                ],
                "NEXT_AUTHORIZED_ACTION": "execute s1",
                "VALIDATION_STATUS": "VALID",
            }
            raw = build_luna_receipt(state, task_root=root)
            self.assertIn(b'"TASK_ID":"task-1"', raw)
            with self.assertRaises(BoundaryError):
                build_luna_receipt({**state, "MISSION_BODY": "leak"}, task_root=root)


class FindLoopReceiptTests(unittest.TestCase):
    def test_full_validated_receipt_and_finding_manifest_are_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            boot = bootstrap_task("mission", "task-1", Path(tmp))
            root = boot.workspace_root
            candidate_ref = write_immutable_artifact(
                root,
                "candidate.txt",
                b"candidate",
                reference_id="candidate",
                artifact_type="candidate_manifest",
                description="candidate",
                read_condition="review",
            )
            findings_ref = empty_findings(root, "task-1")
            bindings = {
                "TARGET_TASK_SHA256": boot.mission_sha256,
                "REVIEWED_ARTIFACT_SHA256": candidate_ref["sha256"],
                "SKEPTIC_SOURCE_BLOB_SHA": blob_digest(ROOT / "skeptic.md"),
                "APPLICABLE_COMPANION_SET_SHA256": "c" * 64,
                "MATERIAL_FINDINGS_SHA256": findings_ref["sha256"],
                "MATERIAL_FINDINGS_REFERENCE": findings_ref,
                "INVOCATION_KIND": "FIND_LOOP",
                "PERMISSION_MODE": "read-only",
            }
            state = {**bindings, "CONSECUTIVE_STABLE_PASSES": 0, "PASSES_REQUIRED": 3, "OPEN_ITEMS": []}
            with self.assertRaises(BoundaryError):
                advance_find_loop(
                    state,
                    bindings,
                    source_root=ROOT,
                    artifact_root=root,
                    task_id="task-1",
                    material_findings_reference=findings_ref,
                )
            receipt = {
                **{key: value for key, value in bindings.items() if key != "MATERIAL_FINDINGS_REFERENCE"},
                "INVOCATION_ID": "r-1",
                "DONE": "complete review",
                "REVIEWED_ARTIFACT_REFERENCE": {
                    "path": candidate_ref["repository_relative_path"],
                    "sha256": candidate_ref["sha256"],
                },
                "SKEPTIC_SOURCE_PATH": "skeptic.md",
                "SKEPTIC_SOURCE_REF": "WORKTREE",
                "PREVIOUS_FINDINGS_REFERENCE": "NONE",
                "MAJOR_STEPS_RUN": [
                    "GATE",
                    "FUNDAMENTAL SCAN",
                    "MAP",
                    "CONFIDENCE",
                    "STABILIZE",
                    "EVIDENCE",
                    "DECIDE",
                    "ACT",
                    "VERIFY",
                    "LEARN",
                ],
                "THINKERS_CONSIDERED": ["CH", "OM", "FE", "PO", "KT", "SH"],
                "FINDING_CATEGORIES": ["PASS"],
                "FINAL_OUTPUT_CATEGORY": "HANDLED",
                "OPEN_ITEMS": [],
                "REVIEW_SCOPE": "COMPLETE",
                "REPAIR_RUN": False,
            }
            for _ in range(3):
                state = advance_find_loop(
                    state,
                    receipt,
                    source_root=ROOT,
                    artifact_root=root,
                    task_id="task-1",
                    material_findings_reference=findings_ref,
                )
            self.assertTrue(find_loop_complete(state))


if __name__ == "__main__":
    unittest.main()
