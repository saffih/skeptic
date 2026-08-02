from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from adapters.claude_code import ClaudeCodeAdapter
from adapters.codex import CodexAdapter
from adapters.generic_host import GenericHostAdapter
from concepts.stt.artifacts import ArtifactRef, ArtifactStore
from concepts.stt.boundary import discover_nested_repositories
from concepts.stt.canonical import canonical_json_bytes, loads_strict, sha256_file
from concepts.stt.capsule import apply_delta, derive_delta, materialize_capsule, prepare_capsule_admission
from concepts.stt.contracts import DEFAULT_LIMITS
from concepts.stt.errors import STTError
from concepts.stt.inventory import derive_toolchain
from concepts.stt.ledger import Ledger
from concepts.stt.plan import validate_plan
from concepts.stt.runner import Runner
from concepts.stt.verifier import verify_task_terminal
from tests.concepts.stt.stt_test_support import STTHarness, change_step, done, inspect_step, task_step, write_json


class AdversarialBoundaryTests(unittest.TestCase):
    maxDiff = None

    def test_all_provider_staging_can_change_after_acceptance(self):
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.bootstrap(); mutated: list[Path] = []
            for _ in range(64):
                if runner.status()["status"] == "COMPLETE":
                    break
                request, request_ref = harness.pending(runner)
                result_dir = runner.task_root / request["result_ref"].rsplit("/", 1)[0]
                if request["role"] == "planner":
                    harness.write_plan(runner, request, request_ref.sha256, delivery="workspace_change", steps=[change_step()])
                elif request["role"] == "reviewer":
                    harness.write_review(runner, request, request_ref.sha256)
                else:
                    harness.write_worker(runner, request, request_ref.sha256, body="accepted\n")
                staging = [path for path in result_dir.iterdir() if path.is_file()]
                staging.append(runner.task_root / request["_provider_evidence_ref"])
                runner.run()
                for path in staging:
                    path.write_bytes(b'{"tampered":true}\n'); os.chmod(path, 0o600); mutated.append(path)
            else:
                self.fail(f"completion cycle exceeded: {runner.status()}")
            self.assertGreaterEqual(len(mutated), 21)
            verified = verify_task_terminal(runner.task_root, expected_success_outcome="COMPLETE")
            self.assertEqual(verified["outcome"], "COMPLETE")
            for effect in runner._accepted_effects():
                payload = effect["payload"]
                self.assertTrue(payload["result"]["ref"].startswith(f"accepted/{payload['operation_id']}/"))
                self.assertTrue(payload["provider_evidence"]["ref"].startswith(f"accepted/{payload['operation_id']}/"))
                runner._verify_refs_recursive(payload)

    def test_unknown_provider_observations_are_independently_frozen(self):
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.bootstrap(); request, _ = harness.pending(runner)
            harness.write_evidence(runner, request, "unknown-one", status="UNKNOWN")
            self.assertEqual(runner.run()["status"], "OPERATION_UNKNOWN")
            retry = runner.retry(); self.assertEqual((retry["status"], retry["next_action"]), ("OPERATION_UNKNOWN", "RECONCILE_OPERATION"))
            first = runner._last_event_payload("OPERATION_UNKNOWN")["provider_evidence"]
            harness.write_evidence(runner, request, "unknown-two", status="UNKNOWN")
            self.assertEqual(Runner(runner.task_root).run()["status"], "OPERATION_UNKNOWN")
            observations = [event["payload"]["provider_evidence"] for event in runner._events() if event["event"]["event_type"] == "OPERATION_UNKNOWN"]
            self.assertEqual(len(observations), 2); self.assertNotEqual(observations[0], observations[1]); self.assertEqual(observations[0], first)
            for ref in observations:
                runner.store.verify(ArtifactRef.from_dict(ref))

    def test_conclusive_failure_resolves_unknown_without_new_admission(self):
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.bootstrap(); request, _ = harness.pending(runner)
            operation_id = request["operation_id"]
            harness.write_evidence(runner, request, "unknown", status="UNKNOWN")
            self.assertEqual(runner.run()["status"], "OPERATION_UNKNOWN")
            harness.write_evidence(runner, request, "failed", status="FAILED")
            reconciled = Runner(runner.task_root).reconcile()
            self.assertEqual((reconciled["status"], reconciled["next_action"]), ("REJECTED", "RETRY_OPERATION"))
            reconstructed = Runner(runner.task_root)
            self.assertEqual((reconstructed.status()["status"], reconstructed.retry()["next_action"]), ("RETRYABLE", "DISPATCH_PLANNER"))
            admissions = [record for record in reconstructed._events() if record["event"]["event_type"] == "OPERATION_ADMITTED" and record["payload"].get("operation_id") == operation_id]
            self.assertEqual(len(admissions), 1)

            harness.write_evidence(reconstructed, request, "unknown", status="UNKNOWN")
            self.assertEqual(reconstructed.run()["status"], "OPERATION_UNKNOWN")
            observations = [record for record in reconstructed._events() if record["event"]["event_type"] == "OPERATION_UNKNOWN" and record["payload"].get("operation_id") == operation_id]
            self.assertEqual(len(observations), 2)

    def test_evidence_selector_traversal_and_internal_artifacts_fail_before_copy(self):
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.bootstrap(); request, request_ref = harness.pending(runner)
            result_ref = runner.store.publish_json("test/evidence-result.json", {"schema_version": 1})
            provider_ref = runner.store.publish_json("test/evidence-provider.json", {"schema_version": 1})
            workspace_probes = ["../outside", "/absolute", "nested/.git/config", ".stt/tasks/sibling", "src/.stt/private"]
            for path in workspace_probes:
                result = {"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": request_ref.sha256, "kind": "NEEDS_EVIDENCE", "selectors": [{"kind": "workspace_path", "path": path}]}
                with self.subTest(path=path), self.assertRaises(STTError):
                    runner._process_evidence_request(request, result, result_ref, provider_ref)

            raw_evidence = runner.task_root / request["_provider_evidence_ref"]
            write_json(raw_evidence, {"provider_id": "generic-recorded-host", "invocation_id": "hidden", "status": "UNKNOWN", "timed_out": False, "exit_code": None})
            raw_result = runner.task_root / request["result_ref"]
            write_json(raw_result, {"schema_version": 1})
            internal_refs = [
                request["_admission_ref"],
                {"ref": request["_provider_evidence_ref"], "sha256": sha256_file(raw_evidence), "size": raw_evidence.stat().st_size},
                {"ref": request["result_ref"], "sha256": sha256_file(raw_result), "size": raw_result.stat().st_size},
                {"ref": runner.task["routing"]["resolver_ref"], "sha256": runner.task["routing"]["resolver_sha256"], "size": (runner.task_root / runner.task["routing"]["resolver_ref"]).stat().st_size},
                runner._fact_ref("TASK_CREATED").as_dict(),
                {"ref": "ledger.jsonl", "sha256": sha256_file(runner.ledger.path), "size": runner.ledger.path.stat().st_size},
            ]
            for artifact in internal_refs:
                disclosed = {**request, "probe": artifact}
                result = {"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": request_ref.sha256, "kind": "NEEDS_EVIDENCE", "selectors": [{"kind": "exported_task_artifact", "artifact": artifact}]}
                with self.subTest(artifact=artifact["ref"]), self.assertRaises(STTError) as caught:
                    runner._process_evidence_request(disclosed, result, result_ref, provider_ref)
                self.assertEqual(caught.exception.code, "EVIDENCE_SELECTOR_INVALID")
            self.assertFalse((runner.task_root / "evidence").exists())

    def test_provider_artifact_references_cannot_read_task_control(self):
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.bootstrap(); request, request_ref = harness.pending(runner)
            harness.write_plan(runner, request, request_ref.sha256)
            staged_result = runner.task_root / request["result_ref"]
            value = loads_strict(staged_result.read_bytes())
            value["finding_map_ref"] = "task.json"
            write_json(staged_result, value)
            rejected = runner.run()
            self.assertEqual((rejected["status"], rejected["next_action"]), ("REJECTED", "RETRY_OPERATION"))
            self.assertEqual(runner._last_event_payload("OPERATION_RESULT_REJECTED")["code"], "PROVIDER_STAGING_PATH_INVALID")
            accepted = runner.task_root / "accepted" / request["operation_id"]
            self.assertFalse(any(path.read_bytes() == (runner.task_root / "task.json").read_bytes() for path in accepted.iterdir()))

    def test_evidence_exports_only_disclosed_immutable_refs_and_mode_0600(self):
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.bootstrap(); request, request_ref = harness.pending(runner)
            result_ref = runner.store.publish_json("test/evidence-result.json", {"schema_version": 1})
            provider_ref = runner.store.publish_json("test/evidence-provider.json", {"schema_version": 1})
            result = {"schema_version": 1, "operation_id": request["operation_id"], "request_sha256": request_ref.sha256, "kind": "NEEDS_EVIDENCE", "selectors": [{"kind": "exported_task_artifact", "artifact": request["mission"]}]}
            bundle_ref = runner._process_evidence_request(request, result, result_ref, provider_ref)
            bundle = loads_strict(runner.store.verify(bundle_ref).read_bytes()); copied = ArtifactRef.from_dict(bundle["items"][0]["artifact"])
            copied_path = runner.store.verify(copied)
            self.assertEqual(copied_path.read_bytes(), runner.store.verify(ArtifactRef.from_dict(request["mission"])).read_bytes())
            self.assertEqual(stat.S_IMODE(os.lstat(copied_path).st_mode), 0o600)
            reviewer_request = {**request, "role": "reviewer"}
            workspace_result = {**result, "selectors": [{"kind": "workspace_path", "path": "value.txt"}]}
            with self.assertRaises(STTError) as caught:
                runner._process_evidence_request(reviewer_request, workspace_result, result_ref, provider_ref)
            self.assertEqual(caught.exception.code, "EVIDENCE_SELECTOR_INVALID")

    def test_repository_inventory_hides_control_nested_and_sibling_task_state(self):
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td))
            vendor = harness.repo / "vendor"; vendor.mkdir(); subprocess.run(["git", "init", "-q", str(vendor)], check=True); (vendor / "secret").write_text("nested")
            submodule = harness.repo / "submodule"; submodule.mkdir(); (submodule / ".git").write_text("gitdir: ../.git/modules/submodule\n"); (submodule / "secret").write_text("submodule")
            (harness.repo / "src" / ".stt").mkdir(); (harness.repo / "src" / ".stt" / "secret").write_text("control")
            runner = harness.bootstrap(); sibling = harness.state_root / "sibling-task"; sibling.mkdir(); (sibling / "secret").write_text("sibling")
            self.assertEqual(set(discover_nested_repositories(harness.repo)), {"submodule", "vendor"})
            runner._run_inspect_step(inspect_step())
            receipt = runner._last_event_payload("INSPECTION_RECORDED"); report_ref = ArtifactRef.from_dict(receipt["report"])
            report = loads_strict(runner.store.verify(report_ref).read_bytes()); paths = {entry["path"] for entry in report["entries"]}
            self.assertFalse(any(component in {".git", ".stt"} for path in paths for component in Path(path).parts))
            self.assertFalse(any(path == "vendor" or path.startswith("vendor/") for path in paths))
            self.assertFalse(any(path == "submodule" or path.startswith("submodule/") for path in paths))
            self.assertFalse(any("sibling-task" in path for path in paths))

    def test_nested_repository_scope_delta_evidence_and_command_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); vendor = harness.repo / "vendor"; vendor.mkdir(); subprocess.run(["git", "init", "-q", str(vendor)], check=True); (vendor / "value").write_text("nested")
            runner = harness.bootstrap(); nested = tuple(runner.task["workspace"]["nested_repository_roots"]); self.assertEqual(nested, ("vendor",))
            plan = {"schema_version": 2, "mission_sha256": runner.task["mission"]["sha256"], "baseline_id": runner._baseline()["manifest_sha256"], "objective": "bad", "done": done("workspace_change"), "delivery_kind": "workspace_change", "steps": [change_step(path="vendor/value")]}
            with self.assertRaises(STTError) as caught:
                validate_plan(plan, mission_sha256=runner.task["mission"]["sha256"], baseline_id=runner._baseline()["manifest_sha256"], catalog_ids={tool["tool_id"] for tool in runner._catalog()[0]["tools"]}, source_paths=[], limits=runner.task["limits"], nested_roots=nested)
            self.assertEqual(caught.exception.code, "NESTED_REPOSITORY_SCOPE_FORBIDDEN")
            capsule = Path(td) / "capsule"; capsule.mkdir(); (capsule / "vendor").mkdir(); (capsule / "vendor" / "value").write_text("bad")
            delta = [{"path": "vendor/value", "op": "file", "before": {"path": "vendor/value", "state": "missing"}, "after": {"path": "vendor/value", "state": "file", "sha256": sha256_file(capsule / "vendor" / "value"), "size": 3, "mode": 0o644}}]
            with self.assertRaises(STTError) as caught:
                apply_delta(harness.repo, capsule, delta, [{"path": "vendor", "kind": "tree"}], max_single_file_bytes=DEFAULT_LIMITS["max_single_file_bytes"], nested_roots=nested)
            self.assertEqual(caught.exception.code, "NESTED_REPOSITORY_SCOPE_FORBIDDEN")
            with patch("concepts.stt.command.subprocess.Popen") as popen, self.assertRaises(STTError) as caught:
                from concepts.stt.command import run_command
                run_command(candidate=harness.repo, command={"tool_id": "python", "args": ["x.py"], "cwd": "vendor", "timeout_seconds": 1, "accepted_exit_codes": [0]}, catalog=derive_toolchain(), logs_dir=Path(td) / "logs", mode="sandbox_required", max_log_bytes=1024)
            self.assertEqual(caught.exception.code, "NESTED_REPOSITORY_SCOPE_FORBIDDEN"); popen.assert_not_called()

            covering_scope = "third-party"
            covering = {
                "schema_version": 2,
                "mission_sha256": runner.task["mission"]["sha256"],
                "baseline_id": runner._baseline()["manifest_sha256"],
                "objective": "cover nested repository",
                "done": done("workspace_change"),
                "delivery_kind": "workspace_change",
                "steps": [{**change_step(path=covering_scope), "read_scope": [{"path": covering_scope, "kind": "tree"}], "write_scope": [{"path": covering_scope, "kind": "tree"}]}],
            }
            with self.assertRaises(STTError) as caught:
                validate_plan(covering, mission_sha256=runner.task["mission"]["sha256"], baseline_id=runner._baseline()["manifest_sha256"], catalog_ids={tool["tool_id"] for tool in runner._catalog()[0]["tools"]}, source_paths=[], limits=runner.task["limits"], nested_roots=(*nested, "third-party/repo"))
            self.assertEqual(caught.exception.code, "NESTED_REPOSITORY_SCOPE_FORBIDDEN")

    def test_inspect_authority_propagates_through_child_and_grandchild(self):
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); root = harness.bootstrap(); original = (harness.repo / "value.txt").read_text()
            root = harness.stage_plan_reviews(root, delivery="inspect", steps=[task_step("child inspect\n")], accepted_reviews=3)
            child_binding = root._active_task_binding(); child = Runner(Path(child_binding["child_task_root"]))
            self.assertTrue(child.task["read_only_authority"]); self.assertTrue(child.task["parent_binding"]["read_only_authority"])
            child = harness.stage_plan_reviews(child, delivery="inspect", steps=[task_step("grandchild inspect\n", "grandchild")], accepted_reviews=3)
            grand_binding = child._active_task_binding(); grandchild = Runner(Path(grand_binding["child_task_root"]))
            self.assertTrue(grandchild.task["read_only_authority"]); self.assertTrue(grandchild.task["parent_binding"]["read_only_authority"])
            request, ref = harness.pending(grandchild); harness.write_plan(grandchild, request, ref.sha256, delivery="workspace_change", steps=[change_step()])
            rejected = grandchild.run(); self.assertEqual(rejected["next_action"], "RETRY_OPERATION")
            rejection = grandchild._last_event_payload("OPERATION_RESULT_REJECTED")
            self.assertEqual(rejection["code"], "INSPECT_AUTHORITY_VIOLATION")
            self.assertEqual((harness.repo / "value.txt").read_text(), original)
            self.assertFalse(grandchild._last_event_payload("WORKER_DELTA_INTENT_RECORDED"))

    def test_malformed_provider_evidence_never_escapes_as_python_type_error(self):
        malformed = [b"[]\n", b'{"bad":true}\n', b"not-json", b"[" * 1100 + b"0" + b"]" * 1100]
        for adapter in (GenericHostAdapter(), CodexAdapter(), ClaudeCodeAdapter()):
            for raw in malformed:
                with self.subTest(adapter=adapter.provider_id, raw=raw), self.assertRaises(STTError) as caught:
                    adapter.validate_provider_evidence(raw)
                self.assertEqual(caught.exception.code, "HOST_ADAPTER_ERROR")
        codex_bad = canonical_json_bytes({"kind": "codex.invocation.v1", "invocation_id": [], "status": "COMPLETE", "timed_out": False, "exit_code": 0})
        with self.assertRaises(STTError):
            CodexAdapter().validate_provider_evidence(codex_bad)
        claude_bad = canonical_json_bytes({"type": "result", "session_id": "x", "is_error": False, "exit_status": "zero"})
        with self.assertRaises(STTError):
            ClaudeCodeAdapter().validate_provider_evidence(claude_bad)
        with self.assertRaises(STTError):
            GenericHostAdapter().validate_provider_evidence(b'{"provider_id":"generic-recorded-host","invocation_id":"\\ud800","status":"COMPLETE","timed_out":false,"exit_code":0}\n')

        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.bootstrap(); request, _ = harness.pending(runner)
            harness.write_evidence(runner, request, "deep-semantic")
            result_path = runner.task_root / request["result_ref"]
            result_path.write_bytes(b"[" * 1100 + b"0" + b"]" * 1100); os.chmod(result_path, 0o600)
            rejected = runner.run()
            self.assertEqual((rejected["status"], rejected["next_action"]), ("REJECTED", "RETRY_OPERATION"))
            self.assertIn(runner._last_event_payload("OPERATION_RESULT_REJECTED")["code"], {"MALFORMED_JSON", "SEMANTIC_RESULT_MISSING_OR_INVALID"})

    def test_ledger_missing_and_symlink_payloads_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); ledger = Ledger(root, "task"); ledger.initialize(); task = root / "task.json"; write_json(task, {"schema_version": 1})
            ledger.append("TASK_CREATED", "task.json", sha256_file(task)); task.unlink()
            with self.assertRaises(STTError) as caught:
                ledger.read()
            self.assertEqual(caught.exception.code, "LEDGER_PAYLOAD_MISSING")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); ledger = Ledger(root, "task"); ledger.initialize(); target = root / "target"; write_json(target, {"schema_version": 1}); (root / "link").symlink_to(target)
            with self.assertRaises(STTError) as caught:
                ledger.append("TASK_CREATED", "link", sha256_file(target))
            self.assertEqual(caught.exception.code, "LEDGER_PAYLOAD_UNSAFE")

    def test_terminal_verifier_rejects_missing_nested_lifecycle_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.complete(harness.bootstrap())
            self.assertEqual(runner.status()["status"], "COMPLETE")
            inspection = runner._last_event_payload("INSPECTION_RECORDED")
            report = ArtifactRef.from_dict(inspection["report"])
            runner.store.verify(report).unlink()
            with self.assertRaises(STTError) as caught:
                verify_task_terminal(runner.task_root, expected_success_outcome="COMPLETE")
            self.assertEqual(caught.exception.code, "ARTIFACT_MISSING")

    def test_review_requests_bind_mission_plan_and_final_subject_context(self):
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.bootstrap(); runner = harness.stage_plan_reviews(runner)
            request, request_ref = harness.pending(runner)
            required = {"mission", "candidate_plan", "finding_map", "baseline", "inventory", "toolchain", "methodology", "prior_findings", "evidence_bundles"}
            self.assertTrue(required <= set(request)); self.assertEqual(request["mission"], runner.task["mission"]); self.assertEqual(request_ref.sha256, sha256_file(runner.task_root / request_ref.ref))
            for key in ("mission", "candidate_plan", "finding_map", "baseline", "inventory", "toolchain", "methodology"):
                runner.store.verify(ArtifactRef.from_dict(request[key]))
            for _ in range(3):
                request, ref = harness.pending(runner); harness.write_review(runner, request, ref.sha256); runner.run()
            final_request, _ = harness.pending(runner); self.assertEqual(final_request["purpose"], "final_review")
            self.assertEqual(set(final_request["required_claims"]), {"mission_objective_satisfied", "final_find_loop_clean", "report_bound_to_baseline"})
            subject_ref = ArtifactRef.from_dict(final_request["subject"]); subject = loads_strict(runner.store.verify(subject_ref).read_bytes())
            self.assertEqual(set(subject), {"schema_version", "mission", "sealed_plan", "plan_seal", "evidence", "result", "accepted_task_results", "inspection_results", "done_proof"})
            self.assertNotIn("three_final_reviews", subject)

    def test_superseded_plan_reviews_do_not_transfer_to_identical_repair(self):
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.bootstrap(); runner = harness.stage_plan_reviews(runner)
            request, ref = harness.pending(runner); harness.write_review(runner, request, ref.sha256, disposition="ACTION"); runner.run()
            replacement, replacement_ref = harness.pending(runner); self.assertEqual(replacement["role"], "planner")
            harness.write_plan(runner, replacement, replacement_ref.sha256); runner.run()
            candidate = runner._current_candidate_effect(); self.assertIsNotNone(candidate)
            self.assertEqual(runner._candidate_reviews(candidate), [])
            next_review, _ = harness.pending(runner)
            self.assertEqual(next_review["candidate_operation_id"], candidate["payload"]["operation_id"])

    def test_sandbox_adversarial_probe_passes_or_backend_fails_before_readiness(self):
        completed = subprocess.run([os.environ.get("PYTHON", "python3"), "scripts/probe_stt_sandbox.py"], cwd=Path(__file__).resolve().parents[3], capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertIn(report["status"], {"PASS_FAIL_CLOSED", "PASS_FAIL_CLOSED_BACKEND_BLOCKED", "PASS_CONTAINED_ADVERSARIAL"})

    def test_capsule_read_single_entry_changed_and_state_limits(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); workspace = root / "workspace"; workspace.mkdir(); (workspace / "value").write_bytes(b"1234")
            scope = [{"path": "value", "kind": "file"}]
            for key, expected in (("max_read_scope_bytes_per_step", "READ_SCOPE_BYTE_LIMIT"), ("max_single_file_bytes", "SINGLE_FILE_LIMIT"), ("max_capsule_entries_per_step", "CAPSULE_ENTRY_LIMIT")):
                limits = {**DEFAULT_LIMITS, key: 0}
                with self.subTest(limit=key), self.assertRaises(STTError) as caught:
                    prepare_capsule_admission(workspace, scope, scope, nested_roots=(), limits=limits)
                self.assertEqual(caught.exception.code, expected)
            manifest = prepare_capsule_admission(workspace, scope, scope, nested_roots=(), limits=DEFAULT_LIMITS); capsule = root / "capsule"; materialize_capsule(workspace, capsule, manifest, scope); (capsule / "value").write_bytes(b"changed")
            with self.assertRaises(STTError) as caught:
                derive_delta(manifest, capsule, scope, {**DEFAULT_LIMITS, "max_changed_paths_per_step": 0})
            self.assertEqual(caught.exception.code, "CHANGED_PATH_LIMIT")
            state = root / "state"; store = ArtifactStore(state, max_bytes=0, min_free_reserve=0); store.initialize()
            with self.assertRaises(STTError) as caught:
                store.publish_bytes("x", b"x")
            self.assertEqual(caught.exception.code, "TASK_STATE_BUDGET_EXHAUSTED")
            reserve = ArtifactStore(root / "reserve", max_bytes=10**9, min_free_reserve=10**30); reserve.initialize()
            with self.assertRaises(STTError) as caught:
                reserve.publish_bytes("x", b"x")
            self.assertEqual(caught.exception.code, "TASK_STATE_BUDGET_EXHAUSTED")

        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.stage_plan_reviews(harness.bootstrap(), delivery="workspace_change", steps=[change_step()], accepted_reviews=3)
            request, request_ref = harness.pending(runner); harness.write_worker(runner, request, request_ref.sha256)
            adopted = runner._adopt_result(request); self.assertIsNotNone(adopted)
            result, result_ref, _, provider_ref = adopted
            runner.store.max_bytes = runner.store._usage()
            with self.assertRaises(STTError) as caught:
                runner._process_worker_result(request, result, result_ref, provider_ref)
            self.assertEqual(caught.exception.code, "TASK_STATE_BUDGET_EXHAUSTED")
            self.assertEqual((harness.repo / "value.txt").read_text(), "before\n")
            self.assertIsNone(runner._last_event_payload("WORKER_DELTA_INTENT_RECORDED"))

    def test_plan_review_final_review_evidence_inventory_and_depth_limits(self):
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.bootstrap(); runner.task["limits"]["max_plan_candidates"] = 0
            request, ref = harness.pending(runner); harness.write_plan(runner, request, ref.sha256)
            runner.run(); self.assertEqual(runner._last_event_payload("OPERATION_RESULT_REJECTED")["code"], "PLAN_CANDIDATE_BUDGET_EXHAUSTED")
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.bootstrap(); runner = harness.stage_plan_reviews(runner); runner.task["limits"]["max_plan_reviews"] = 0
            request, ref = harness.pending(runner); harness.write_review(runner, request, ref.sha256); runner.run()
            self.assertEqual(runner._last_event_payload("OPERATION_RESULT_REJECTED")["code"], "REVIEW_BUDGET_EXHAUSTED")
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.bootstrap(); runner.task["limits"]["max_evidence_rounds_per_purpose"] = 0
            request, ref = harness.pending(runner); harness.write_needs_evidence(runner, request, ref.sha256); runner.run()
            self.assertEqual(runner._last_event_payload("OPERATION_RESULT_REJECTED")["code"], "EVIDENCE_BUDGET_EXHAUSTED")
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.bootstrap(); runner = harness.stage_plan_reviews(runner, accepted_reviews=3); runner.task["limits"]["max_final_find_reviews"] = 0
            request, ref = harness.pending(runner); harness.write_review(runner, request, ref.sha256); runner.run()
            self.assertEqual(runner._last_event_payload("OPERATION_RESULT_REJECTED")["code"], "REVIEW_BUDGET_EXHAUSTED")
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.bootstrap(); runner.task["limits"]["max_inventory_entries"] = 0
            with self.assertRaises(STTError) as caught:
                runner._run_inspect_step(inspect_step())
            self.assertEqual(caught.exception.code, "INVENTORY_ENTRY_LIMIT")
            runner.task["depth"] = runner.task["limits"]["max_task_depth"]
            with self.assertRaises(STTError) as caught:
                runner._task_binding_for(task_step("too deep"), ArtifactRef("plan", "0" * 64, 0), {"delivery_kind": "workspace_change"})
            self.assertEqual(caught.exception.code, "TASK_DEPTH_EXCEEDED")

    def test_stop_resume_and_blocked_state_never_claim_false_reconciliation(self):
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); runner = harness.bootstrap(); operation_id = runner._pending_operation()[0]["operation_id"]
            runner.stop(); stopped = Runner(runner.task_root); count = len(stopped._events())
            self.assertEqual((stopped.run()["status"], stopped.retry()["next_action"]), ("STOPPED", "RESUME"))
            self.assertEqual(len(stopped._events()), count)
            with self.assertRaises(STTError):
                stopped.replan()
            stopped.resume(); self.assertEqual(Runner(runner.task_root)._pending_operation()[0]["operation_id"], operation_id)
            failure = runner.store.publish_json("test/failure.json", {"schema_version": 1}); Runner(runner.task_root)._record_blocked_unknown("PARTIAL", [failure], operation_id=operation_id)
            blocked = Runner(runner.task_root).status(); self.assertEqual((blocked["next_action"], blocked["resumable"]), ("DIAGNOSE", False)); self.assertNotEqual(blocked["next_action"], "RECONCILE_OPERATION")

    def test_parent_records_its_own_block_before_advertising_blocked_state(self):
        with tempfile.TemporaryDirectory() as td:
            harness = STTHarness(Path(td)); root = harness.stage_plan_reviews(harness.bootstrap(), delivery="workspace_change", steps=[task_step("child\n")], accepted_reviews=3)
            binding = root._active_task_binding(); self.assertIsNotNone(binding)
            child = Runner(Path(binding["child_task_root"])); operation_id = child._pending_operation()[0]["operation_id"]
            failure = child.store.publish_json("test/child-failure.json", {"schema_version": 1})
            child._record_blocked_unknown("CHILD_PARTIAL", [failure], operation_id=operation_id)
            before = Runner(root.task_root).status()
            self.assertEqual((before["status"], before["next_action"]), ("RUNNING", "RUN_PARENT"))
            after = Runner(root.task_root).run()
            self.assertEqual((after["status"], after["next_action"], after["resumable"]), ("BLOCKED_UNKNOWN", "DIAGNOSE", False))

    def test_root_child_grandchild_success_contract_remains_unchanged(self):
        from tests.concepts.stt.test_recursive_tasks import RecursiveTaskTests
        RecursiveTaskTests("test_root_child_grandchild_executes_depth_first").test_root_child_grandchild_executes_depth_first()


if __name__ == "__main__":
    unittest.main()
