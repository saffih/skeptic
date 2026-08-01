from __future__ import annotations

import os
import shutil
import stat
import uuid
from pathlib import Path
from typing import Any

from .artifacts import ArtifactRef, ArtifactStore
from .boundary import compact_receipt, copy_tree, scope_contains, tree_profile, tree_storage_upper_bound, validate_tree
from .canonical import canonical_json_bytes, ensure_no_symlink_components, loads_strict, sha256_bytes, sha256_file
from .capsule import derive_delta, materialize_capsule, overlay_delta
from .command import run_command
from .contracts import DEFAULT_LIMITS
from .cutover import apply_manifest, build_manifest
from .errors import STTError, require
from .gitutil import resolve_repo, run_git
from .inventory import derive_inventory, derive_toolchain
from .host import load_adapter
from .ledger import Ledger
from .locks import Lease, lock_root, workspace_key
from .plan import validate_plan
from .snapshot import build_snapshot, verify_source_identity
from .state import derive


TASK_OUTCOME = "COMPLETE"


class Runner:
    def __init__(self, task_root: Path, *, read_only: bool = False) -> None:
        self.task_root = task_root.resolve(strict=False)
        task_path = self.task_root / "task.json"
        require(task_path.is_file(), "TASK_NOT_FOUND", "task.json not found")
        self.task = loads_strict(task_path.read_bytes())
        self.task_id = self.task["task_id"]
        self.read_only = read_only
        limits = self.task["limits"]
        self.store = ArtifactStore(self.task_root, max_bytes=limits["max_task_state_bytes"], min_free_reserve=limits["min_free_space_reserve_bytes"])
        self.ledger = Ledger(self.task_root, self.task_id)
        if read_only:
            require(self.ledger.path.is_file(), "LEDGER_MISSING", "ledger.jsonl not found")
            self.ledger.read(recover_partial=False)
        else:
            self.ledger.initialize()

    @staticmethod
    def bootstrap(*, repo: Path, state_root: Path, mission: bytes, included_ignored: list[str], allow_unconfined: bool = False, require_final_entrypoint_smoke: bool = False, task_id: str | None = None, parent_binding: dict[str, Any] | None = None, input_checkpoint: Path | None = None) -> dict[str, Any]:
        repo_root, git_common = resolve_repo(repo)
        try:
            require(mission.decode("utf-8").strip() != "", "MISSION_REQUIRED", "mission is effectively blank")
        except UnicodeDecodeError as exc:
            raise STTError("MISSION_NOT_UTF8", "mission must be UTF-8") from exc
        state_root = state_root.resolve(strict=False)
        # Explicit --state-root and STT_TASKS_ROOT are supported overrides; both
        # remain subject to the non-overlap, no-symlink, ownership checks below.
        local_state = (repo_root / ".stt" / "tasks").resolve(strict=False)
        require(state_root == local_state or (state_root not in repo_root.parents and repo_root not in state_root.parents), "STATE_ROOT_UNSAFE", "state root overlaps repository unsafely")
        ensure_no_symlink_components(state_root, include_leaf=False)
        state_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        state_stat = os.lstat(state_root)
        require(stat.S_ISDIR(state_stat.st_mode) and state_stat.st_uid == os.geteuid(), "STATE_ROOT_UNSAFE", "state root owner/type mismatch")
        require(stat.S_IMODE(state_stat.st_mode) == 0o700, "STATE_ROOT_UNSAFE", "state root must be mode 0700")
        ensure_no_symlink_components(state_root)
        task_id = task_id or str(uuid.uuid4()); task_root = state_root / task_id
        require(not task_root.exists(), "TASK_ID_COLLISION", "deterministic Task identity already exists")
        limits = dict(DEFAULT_LIMITS)
        store = ArtifactStore(task_root, max_bytes=limits["max_task_state_bytes"], min_free_reserve=limits["min_free_space_reserve_bytes"])
        store.initialize()
        mission_ref = store.publish_bytes("mission.txt", mission)
        provider_id = os.environ.get("STT_PROVIDER", "generic-recorded-host")
        adapter = load_adapter(provider_id)
        capabilities = adapter.discover_capabilities()
        require(capabilities.available, "HOST_CAPABILITY_UNAVAILABLE", f"semantic provider unavailable: {provider_id}")
        require(set(capabilities.semantic_roles) >= {"planner", "reviewer", "worker"}, "HOST_CAPABILITY_UNAVAILABLE", "provider lacks required semantic roles")
        require(capabilities.durable_invocation_id and capabilities.status_inspection and capabilities.cancellation_confirmation, "HOST_CAPABILITY_UNAVAILABLE", "provider lacks durable operation controls")
        routing = {
            "schema_version": 1,
            "provider_id": provider_id,
            "capabilities": {"durable_invocation_id": capabilities.durable_invocation_id, "status_inspection": capabilities.status_inspection, "cancellation_confirmation": capabilities.cancellation_confirmation, "evidence_schema": capabilities.evidence_schema},
            "profiles": {
                "economical": {"provider": provider_id, "role": adapter.provider_role("planner"), "model": "economical", "effort": "low"},
                "standard": {"provider": provider_id, "role": adapter.provider_role("reviewer"), "model": "standard", "effort": "medium"},
            },
        }
        routing_ref = store.publish_json("routing/resolver.json", routing)
        task = {
            "schema_version": 1,
            "task_id": task_id,
            "mission": mission_ref.as_dict(),
            "workspace": {"root": str(repo_root), "git_common_dir": str(git_common), "included_ignored_paths": sorted(included_ignored), "input_checkpoint": str(input_checkpoint.resolve()) if input_checkpoint else None},
            "authority": {
                "working_tree_repair": True,
                "semantic_provider_dispatch": True,
                "provider_disclosure_scope": "declared_execution_policy_evidence_only",
                "task_runtime_network": False,
                "task_runtime_external_side_effects": False,
                "git_control_mutation": False,
                "commit_or_publication": False,
                "candidate_dynamic_execution": "owner_risk_accepted" if allow_unconfined else "sandbox_required",
            },
            "routing": {
                "resolver_ref": routing_ref.ref,
                "resolver_sha256": routing_ref.sha256,
                "planner_profile": "economical",
                "reviewer_profile": "standard",
                "worker_profile_ceiling": "standard",
                "premium_authorized": False,
            },
            "limits": limits,
            "qualification": {"final_entrypoint_smoke_required": require_final_entrypoint_smoke},
            "parent_binding": parent_binding,
            "parent_task_id": parent_binding.get("parent_task_id") if parent_binding else None,
            "parent_plan_sha256": parent_binding.get("parent_plan_sha256") if parent_binding else None,
            "parent_step_id": parent_binding.get("parent_step_id") if parent_binding else None,
            "parent_checkpoint_sha256": parent_binding.get("parent_checkpoint_sha256") if parent_binding else None,
            "depth": int(parent_binding.get("depth", 0)) if parent_binding else 0,
        }
        task_ref = store.publish_json("task.json", task)
        ledger = Ledger(task_root, task_id); ledger.initialize(); ledger.append("TASK_CREATED", task_ref.ref, task_ref.sha256)
        runner = Runner(task_root)
        return runner._prepare_initial_state()

    def _leases(self) -> tuple[Lease, Lease]:
        root = lock_root(self.task_root); workspace = Path(self.task["workspace"]["git_common_dir"])
        return Lease(self.task_root / ".task.lock", "TASK_BUSY"), Lease(root / f"workspace-{workspace_key(workspace)}.lock", "WORKSPACE_BUSY")

    def _task_lease(self) -> Lease:
        return Lease(self.task_root / ".task.lock", "TASK_BUSY")

    def _workspace_lease(self) -> Lease:
        root = lock_root(self.task_root)
        key = workspace_key(Path(self.task["workspace"]["git_common_dir"]))
        return Lease(root / f"workspace-{key}.lock", "WORKSPACE_BUSY")

    def _events(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for event in self.ledger.read(recover_partial=not self.read_only):
            value = event.value
            payload_path = self.task_root / value["payload_ref"]
            payload: Any = None
            if payload_path.is_file():
                try:
                    payload = loads_strict(payload_path.read_bytes())
                except STTError:
                    payload = None
            records.append({"event": value, "payload": payload})
        return records

    def _append_json_fact(self, event_type: str, directory: str, value: dict[str, Any]) -> ArtifactRef:
        ref = self.store.publish_json(f"{directory}/{uuid.uuid4().hex}.json", value)
        self.ledger.append(event_type, ref.ref, ref.sha256)
        return ref

    def _prepare_initial_state(self) -> dict[str, Any]:
        task_lease, workspace_lease = self._leases()
        with task_lease, workspace_lease:
            snapshot_dir = self.task_root / "preservation" / "initial"
            source_root = Path(self.task["workspace"]["root"] )
            source_bound = tree_storage_upper_bound(source_root, exclude_root_git=True)
            profile = tree_profile(source_root, exclude_root_git=True)
            require(profile["regular_bytes"] <= self.task["limits"]["max_workspace_bytes"], "WORKSPACE_LIMIT_EXCEEDED", "workspace byte limit exceeded", profile=profile)
            require(profile["objects"] <= self.task["limits"]["max_workspace_files"], "WORKSPACE_LIMIT_EXCEEDED", "workspace object-count limit exceeded", profile=profile)
            require(profile["max_file_bytes"] <= self.task["limits"]["max_single_file_bytes"], "WORKSPACE_LIMIT_EXCEEDED", "workspace single-file limit exceeded", profile=profile)
            self.store.admit(source_bound * 2)
            snapshot = build_snapshot(source_root, snapshot_dir, self.task["workspace"]["included_ignored_paths"])
            snapshot_ref = self.store.publish_json("preservation/initial-receipt.json", snapshot)
            self.ledger.append("INITIAL_SNAPSHOT_READY", snapshot_ref.ref, snapshot_ref.sha256)
            checkpoint_root = self.task_root / "checkpoints" / "000"
            checkpoint_root.mkdir(parents=True, mode=0o700)
            input_checkpoint = self.task["workspace"].get("input_checkpoint")
            input_root = Path(input_checkpoint) if input_checkpoint else snapshot_dir / "execution_workspace"
            self.store.admit(tree_storage_upper_bound(input_root))
            shutil.copytree(input_root, checkpoint_root / "workspace", symlinks=True, dirs_exist_ok=False)
            tree = self._validate_tree(checkpoint_root / "workspace")
            checkpoint_ref = self.store.publish_json("checkpoints/000/receipt.json", {"schema_version": 1, "checkpoint_number": 0, "step_id": None, "tree": tree})
            self.ledger.append("CHECKPOINT_ACCEPTED", checkpoint_ref.ref, checkpoint_ref.sha256)
            inventory = derive_inventory(checkpoint_root / "workspace", snapshot)
            inventory_ref = self.store.publish_json("inventory/current-main.json", inventory)
            self.ledger.append("INVENTORY_RECORDED", inventory_ref.ref, inventory_ref.sha256)
            catalog = derive_toolchain(); catalog_ref = self.store.publish_json("toolchain/catalog.json", catalog)
            self.ledger.append("TOOLCHAIN_BOUND", catalog_ref.ref, catalog_ref.sha256)
            skeptic = checkpoint_root / "workspace" / "skeptic.md"
            require(skeptic.is_file(), "SKEPTIC_SOURCE_UNAVAILABLE", "skeptic.md missing from checkpoint")
            companions = []
            companion = checkpoint_root / "workspace" / "skeptic-questions.md"
            if companion.is_file():
                companions.append({"path": "skeptic-questions.md", "sha256": sha256_file(companion), "size": companion.stat().st_size})
            methodology = {"schema_version": 1, "skeptic": {"path": "skeptic.md", "sha256": sha256_file(skeptic), "size": skeptic.stat().st_size}, "companions": companions}
            method_ref = self.store.publish_json("methodology/binding.json", methodology)
            self.ledger.append("METHODOLOGY_BOUND", method_ref.ref, method_ref.sha256)
            request_ref = self._create_semantic_request(
                role="planner",
                purpose="initial_plan",
                body={"mission": self.task["mission"], "inventory": inventory_ref.as_dict(), "toolchain": catalog_ref.as_dict(), "methodology": method_ref.as_dict(), "baseline_id": snapshot["manifest_sha256"]},
            )
            return self.receipt("RUNNING", "DISPATCH_PLANNER", [snapshot_ref, checkpoint_ref, inventory_ref, catalog_ref, method_ref, request_ref])

    def _create_semantic_request(self, *, role: str, purpose: str, body: dict[str, Any]) -> ArtifactRef:
        operation_id = f"{len(self.ledger.read(recover_partial=True)) + 1}-{uuid.uuid4()}"
        result_dir = self.task_root / "semantic" / "results" / operation_id
        result_dir.mkdir(parents=True, mode=0o700)
        request = {
            "schema_version": 1,
            "operation_id": operation_id,
            "role": role,
            "purpose": purpose,
            "result_ref": f"semantic/results/{operation_id}/result.json",
            **body,
        }
        request_ref = self.store.publish_json(f"semantic/requests/{operation_id}.json", request)
        admission = self.store.publish_json(f"semantic/admissions/{operation_id}.json", {
            "schema_version": 1,
            "operation_id": operation_id,
            "request": request_ref.as_dict(),
            "role": role,
            "purpose": purpose,
            "provider_id": loads_strict((self.task_root / self.task["routing"]["resolver_ref"]).read_bytes())["provider_id"],
            "provider_evidence_ref": f"semantic/provider-evidence/{operation_id}.json",
        })
        self.ledger.append("OPERATION_ADMITTED", admission.ref, admission.sha256)
        return request_ref

    def _pending_operation(self) -> tuple[dict[str, Any], ArtifactRef] | None:
        admitted: list[dict[str, Any]] = []
        completed: set[str] = set()
        for record in self._events():
            event_type = record["event"]["event_type"]
            payload = record["payload"]
            if event_type == "OPERATION_ADMITTED" and isinstance(payload, dict):
                admitted.append(payload)
            elif event_type in {"OPERATION_ACCEPTED", "OPERATION_RESULT"} and isinstance(payload, dict):
                completed.add(str(payload.get("operation_id")))
        for admission in reversed(admitted):
            operation_id = str(admission["operation_id"])
            if operation_id in completed:
                continue
            request_ref = ArtifactRef(**admission["request"])
            request_path = self.store.verify(request_ref)
            request = loads_strict(request_path.read_bytes())
            request["_provider_evidence_ref"] = admission["provider_evidence_ref"]
            request["_provider_id"] = admission["provider_id"]
            return request, request_ref
        return None

    def _adopt_result(self, request: dict[str, Any]) -> tuple[dict[str, Any], ArtifactRef, dict[str, Any]] | None:
        result_path = self.task_root / request["result_ref"]
        evidence_path = self.task_root / request["_provider_evidence_ref"]
        if not result_path.is_file() or not evidence_path.is_file():
            return None
        evidence_ref = self.store.adopt_existing(request["_provider_evidence_ref"], max_size=self.task["limits"]["max_semantic_result_bytes"])
        adapter = load_adapter(request["_provider_id"])
        report = adapter.validate_provider_evidence(self.store.verify(evidence_ref).read_bytes())
        require(report.provider_id == request["_provider_id"], "PROVIDER_IDENTITY_MISMATCH", "provider evidence identity mismatch")
        if report.status == "UNKNOWN":
            previous = self._last_event_payload("OPERATION_UNKNOWN")
            if not previous or previous.get("operation_id") != request["operation_id"] or previous.get("provider_evidence", {}).get("sha256") != evidence_ref.sha256:
                blocked = self.store.publish_json(f"semantic/operation-unknown/{request['operation_id']}-{uuid.uuid4().hex}.json", {"schema_version": 1, "operation_id": request["operation_id"], "provider_evidence": evidence_ref.as_dict(), "provider_report": report.as_dict(), "outer_status": "UNKNOWN"})
                self.ledger.append("OPERATION_UNKNOWN", blocked.ref, blocked.sha256)
            raise STTError("BLOCKED_UNKNOWN", "semantic operation remains inconclusive")
        require(report.status == "COMPLETE", "SEMANTIC_OPERATION_FAILED", "semantic provider reported failure", report=report.as_dict())
        result_ref = self.store.adopt_existing(request["result_ref"], max_size=self.task["limits"]["max_semantic_result_bytes"])
        result = loads_strict(self.store.verify(result_ref).read_bytes())
        require(isinstance(result, dict), "SEMANTIC_RESULT_MISSING_OR_INVALID", "semantic result must be an object")
        require(result.get("schema_version") == 1 and result.get("operation_id") == request["operation_id"], "SEMANTIC_RESULT_MISSING_OR_INVALID", "semantic result identity mismatch")
        require(result.get("request_sha256") == sha256_file(self.task_root / f"semantic/requests/{request['operation_id']}.json"), "SEMANTIC_RESULT_MISSING_OR_INVALID", "semantic request hash mismatch")
        return result, result_ref, report.as_dict()

    def _accept_operation(self, request: dict[str, Any], result_ref: ArtifactRef, evidence_ref: ArtifactRef) -> ArtifactRef:
        """Publish one authoritative event only after every role-specific check succeeds."""
        value = {"schema_version": 1, "operation_id": request["operation_id"], "role": request["role"], "provider_id": request["_provider_id"], "request": {"ref": f"semantic/requests/{request['operation_id']}.json", "sha256": sha256_file(self.task_root / f"semantic/requests/{request['operation_id']}.json")}, "result": result_ref.as_dict(), "provider_evidence": evidence_ref.as_dict()}
        receipt = self.store.publish_json(f"semantic/operation-accepted/{request['operation_id']}.json", value)
        self.ledger.append("OPERATION_ACCEPTED", receipt.ref, receipt.sha256)
        return receipt

    def _reject_operation(self, request: dict[str, Any], exc: STTError) -> ArtifactRef:
        value = {"schema_version": 1, "operation_id": request["operation_id"], "role": request["role"], "code": exc.code, "message": exc.message, "retryable": True}
        receipt = self.store.publish_json(f"semantic/operation-rejected/{request['operation_id']}-{uuid.uuid4().hex}.json", value)
        self.ledger.append("OPERATION_RESULT_REJECTED", receipt.ref, receipt.sha256)
        return receipt

    def _last_event_payload(self, event_type: str) -> dict[str, Any] | None:
        for record in reversed(self._events()):
            if record["event"]["event_type"] == event_type and isinstance(record["payload"], dict):
                return record["payload"]
        return None

    def _current_plan(self) -> tuple[dict[str, Any], ArtifactRef] | None:
        payload = self._last_event_payload("PLAN_CANDIDATE_RECORDED")
        if not payload:
            return None
        ref = ArtifactRef(**payload["plan"])
        plan = loads_strict(self.store.verify(ref).read_bytes())
        return plan, ref

    def _catalog(self) -> tuple[dict[str, Any], ArtifactRef]:
        payload = self._last_event_payload("TOOLCHAIN_BOUND")
        require(payload is not None, "CONTROL_STATE_FAILED", "toolchain event payload unavailable")
        event = next(record for record in reversed(self._events()) if record["event"]["event_type"] == "TOOLCHAIN_BOUND")
        ref = ArtifactRef(event["event"]["payload_ref"], event["event"]["payload_sha256"], (self.task_root / event["event"]["payload_ref"]).stat().st_size)
        return loads_strict(self.store.verify(ref).read_bytes()), ref

    def _snapshot(self) -> dict[str, Any]:
        return loads_strict((self.task_root / "preservation/initial-receipt.json").read_bytes())

    def _validate_tree(self, root: Path) -> dict[str, Any]:
        policy = self._snapshot().get("git_path_policy", {})
        tree = validate_tree(root, ignore_case=bool(policy.get("ignore_case", False)))
        files = [entry for entry in tree["entries"] if entry["kind"] == "file"]
        require(len(tree["entries"]) <= self.task["limits"]["max_workspace_files"], "WORKSPACE_LIMIT_EXCEEDED", "candidate object-count limit exceeded")
        require(sum(entry["size"] for entry in files) <= self.task["limits"]["max_workspace_bytes"], "WORKSPACE_LIMIT_EXCEEDED", "candidate byte limit exceeded")
        require(max((entry["size"] for entry in files), default=0) <= self.task["limits"]["max_single_file_bytes"], "WORKSPACE_LIMIT_EXCEEDED", "candidate single-file limit exceeded")
        return tree

    def _process_evidence_request(self, request: dict[str, Any], result: dict[str, Any]) -> ArtifactRef:
        selectors = result.get("selectors")
        require(isinstance(selectors, list) and len(selectors) <= self.task["limits"]["max_evidence_refs_per_round"], "EVIDENCE_BUDGET_EXHAUSTED", "invalid evidence selector set")
        bundle_id = uuid.uuid4().hex; bundle_root = self.task_root / "evidence" / bundle_id; bundle_root.mkdir(parents=True, mode=0o700)
        items: list[dict[str, Any]] = []; total = 0
        latest_checkpoint = self._latest_checkpoint()[1]
        for index, selector in enumerate(selectors):
            require(isinstance(selector, dict) and set(selector) == {"kind", "path"}, "EVIDENCE_SELECTOR_INVALID", "evidence selector schema invalid")
            kind, raw = selector["kind"], selector["path"]
            if kind == "checkpoint_path":
                source = latest_checkpoint / raw
                require(source.is_file() and not source.is_symlink(), "EVIDENCE_SELECTOR_INVALID", "checkpoint selector must name one regular file")
            elif kind == "exported_task_artifact":
                require(not raw.startswith("preservation/") and not raw.startswith("ledger"), "EVIDENCE_SELECTOR_INVALID", "artifact class is not exportable")
                source = self.task_root / raw
                require(source.is_file() and not source.is_symlink(), "EVIDENCE_SELECTOR_INVALID", "exported artifact missing")
            else:
                raise STTError("EVIDENCE_SELECTOR_INVALID", "unknown evidence selector kind")
            size = source.stat().st_size; total += size
            require(total <= self.task["limits"]["max_evidence_bytes_per_round"], "EVIDENCE_BUDGET_EXHAUSTED", "evidence byte limit exceeded")
            self.store.admit(size + 4096)
            destination = bundle_root / f"{index:03d}-{source.name}"
            shutil.copy2(source, destination, follow_symlinks=False)
            items.append({"selector": selector, "ref": destination.relative_to(self.task_root).as_posix(), "sha256": sha256_file(destination), "size": size})
        bundle = self.store.publish_json(f"evidence/{bundle_id}/manifest.json", {"schema_version": 1, "purpose": request["purpose"], "items": items})
        self.ledger.append("EVIDENCE_BUNDLE_EXTENDED", bundle.ref, bundle.sha256)
        body = {key: value for key, value in request.items() if key not in {"schema_version", "operation_id", "role", "purpose", "result_ref"} and not key.startswith("_")}
        prior = list(body.get("evidence_bundles", [])); prior.append(bundle.as_dict()); body["evidence_bundles"] = prior
        self._create_semantic_request(role=request["role"], purpose=request["purpose"], body=body)
        return bundle

    def _validate_plan_write_scopes(self, plan: dict[str, Any], snapshot: dict[str, Any]) -> None:
        nested = [Path(rel) for rel in snapshot.get("nested_repository_roots", [])]
        for step in plan["steps"]:
            if step["kind"] != "change":
                continue
            scope = step["write_scope"]
            for item in scope:
                declared = Path(item["path"])
                for root in nested:
                    require(not (declared == root or declared in root.parents or root in declared.parents), "NESTED_REPOSITORY_SCOPE_FORBIDDEN", "write scope overlaps nested repository or submodule", scope=item["path"], nested_root=root.as_posix())
            for entry in snapshot["execution_entries"]:
                if not scope_contains(scope, entry["path"]):
                    continue
                require(entry["uid"] == os.geteuid(), "UNSUPPORTED_METADATA", "write-scope owner mismatch", path=entry["path"] )
                require(not (entry["mode"] & 0o7000), "UNSUPPORTED_METADATA", "write-scope special mode bits", path=entry["path"] )
                require(not entry.get("xattrs"), "UNSUPPORTED_METADATA", "write-scope xattrs unsupported", path=entry["path"] )
                if entry["kind"] == "file":
                    require(entry["nlink"] == 1, "UNSUPPORTED_METADATA", "write-scope hard-linked file", path=entry["path"] )

    def _process_planner_result(self, request: dict[str, Any], result: dict[str, Any], result_ref: ArtifactRef) -> None:
        if result.get("kind") == "NEEDS_EVIDENCE":
            self._process_evidence_request(request, result)
            return
        expected = {"schema_version", "operation_id", "request_sha256", "kind", "plan_ref", "plan_sha256", "finding_map_ref"}
        require(set(result) == expected and result["kind"] == "PLAN_CANDIDATE", "SEMANTIC_RESULT_MISSING_OR_INVALID", "Planner result schema invalid")
        plan_ref = self.store.adopt_existing(result["plan_ref"], max_size=self.task["limits"]["max_semantic_result_bytes"])
        require(plan_ref.sha256 == result["plan_sha256"], "PLAN_BINDING", "Planner Plan hash mismatch")
        finding_map_ref = self.store.adopt_existing(result["finding_map_ref"], max_size=self.task["limits"]["max_request_bytes"])
        finding_map = loads_strict(self.store.verify(finding_map_ref).read_bytes())
        require(isinstance(finding_map, dict) and isinstance(finding_map.get("findings"), list), "FINDING_MAP_INVALID", "finding map must contain a findings array")
        plan = loads_strict(self.store.verify(plan_ref).read_bytes())
        catalog, _ = self._catalog(); snapshot = self._snapshot()
        validate_plan(plan, mission_sha256=self.task["mission"]["sha256"], baseline_id=snapshot["manifest_sha256"], catalog_ids={tool["tool_id"] for tool in catalog["tools"]}, source_paths=[self.task["workspace"]["root"], self.task["workspace"]["git_common_dir"], str(self.task_root)], limits=self.task["limits"])
        self._validate_plan_write_scopes(plan, snapshot)
        prior_candidates = sum(1 for record in self._events() if record["event"]["event_type"] == "PLAN_CANDIDATE_RECORDED")
        require(prior_candidates < self.task["limits"]["max_plan_candidates"], "PLAN_CANDIDATE_BUDGET_EXHAUSTED", "Plan candidate budget exhausted")
        receipt = self._append_json_fact("PLAN_CANDIDATE_RECORDED", "plans/candidate-receipts", {"schema_version": 1, "candidate_number": prior_candidates + 1, "plan": plan_ref.as_dict(), "finding_map": finding_map_ref.as_dict(), "planner_result": result_ref.as_dict(), "baseline_id": snapshot["manifest_sha256"]})
        self._create_semantic_request(role="reviewer", purpose="plan_review", body={"subject": plan_ref.as_dict(), "methodology_ref": "methodology/binding.json", "prior_findings": [], "candidate_number": prior_candidates + 1})

    def _consecutive_plan_passes(self, plan_sha: str) -> list[dict[str, Any]]:
        passes: list[dict[str, Any]] = []
        for record in reversed(self._events()):
            if record["event"]["event_type"] == "PLAN_CANDIDATE_RECORDED":
                break
            if record["event"]["event_type"] == "PLAN_REVIEW_RECORDED" and isinstance(record["payload"], dict):
                payload = record["payload"]
                if payload.get("subject_sha256") == plan_sha and payload.get("qualifying") is True:
                    passes.append(payload)
                else:
                    break
        return list(reversed(passes))

    def _process_reviewer_result(self, request: dict[str, Any], result: dict[str, Any], result_ref: ArtifactRef, provider_report: dict[str, Any]) -> None:
        if result.get("review_disposition") == "NEEDS_EVIDENCE" or result.get("kind") == "NEEDS_EVIDENCE":
            self._process_evidence_request(request, result)
            return
        expected = {"schema_version", "operation_id", "request_sha256", "protocol_outcome", "review_disposition", "runskeptic_final_outcome", "receipt_ref", "findings_ref", "subject_sha256", "session_id", "claims"}
        require(set(result) == expected and result["protocol_outcome"] == "COMPLETE", "SEMANTIC_RESULT_MISSING_OR_INVALID", "Reviewer result schema invalid")
        disposition = result["review_disposition"]
        require(disposition in {"PASS", "ACTION", "CONFLICT"}, "SEMANTIC_RESULT_MISSING_OR_INVALID", "Reviewer disposition invalid")
        receipt_ref = self.store.adopt_existing(result["receipt_ref"], max_size=self.task["limits"]["max_semantic_result_bytes"])
        findings_ref = self.store.adopt_existing(result["findings_ref"], max_size=self.task["limits"]["max_semantic_result_bytes"])
        findings = loads_strict(self.store.verify(findings_ref).read_bytes())
        require(isinstance(findings, dict) and isinstance(findings.get("findings"), list), "SEMANTIC_RESULT_MISSING_OR_INVALID", "Reviewer finding set invalid")
        prior_sessions = {record["payload"].get("session_id") for record in self._events() if record["event"]["event_type"] in {"PLAN_REVIEW_RECORDED", "FINAL_REVIEW_RECORDED"} and isinstance(record["payload"], dict)}
        require(result["session_id"] == provider_report["invocation_id"], "REVIEW_INDEPENDENCE_UNEVIDENCED", "Reviewer session does not match provider invocation identity")
        require(result["session_id"] not in prior_sessions and result["session_id"] not in {None, "", "UNKNOWN"}, "REVIEW_INDEPENDENCE_UNEVIDENCED", "Reviewer session identity missing or reused")
        qualifying = disposition == "PASS" and not findings["findings"] and result["runskeptic_final_outcome"] == "PASS"
        event_type = "PLAN_REVIEW_RECORDED" if request["purpose"] == "plan_review" else "FINAL_REVIEW_RECORDED"
        payload = {
            "schema_version": 1,
            "purpose": request["purpose"],
            "subject_sha256": result["subject_sha256"],
            "session_id": result["session_id"],
            "disposition": disposition,
            "qualifying": qualifying,
            "review_receipt": receipt_ref.as_dict(),
            "findings": findings_ref.as_dict(),
            "claims": result["claims"],
            "reviewer_result": result_ref.as_dict(),
        }
        self._append_json_fact(event_type, "reviews/receipts", payload)
        if request["purpose"] == "plan_review":
            current = self._current_plan(); require(current is not None, "CONTROL_STATE_FAILED", "Plan review without current Plan")
            _, plan_ref = current
            require(result["subject_sha256"] == plan_ref.sha256, "REVIEW_SUBJECT_MISMATCH", "Plan review subject mismatch")
            if disposition == "CONFLICT":
                self._terminal("FAILED", "PLAN_CONFLICT", [receipt_ref, findings_ref]); return
            if disposition == "ACTION":
                self._append_json_fact("PLAN_BASELINE_SUPERSEDED", "plans/superseded", {"schema_version": 1, "plan": plan_ref.as_dict(), "findings": findings_ref.as_dict()})
                self._create_semantic_request(role="planner", purpose="plan_repair", body={"mission": self.task["mission"], "inventory_ref": "inventory/current-main.json", "toolchain_ref": "toolchain/catalog.json", "methodology_ref": "methodology/binding.json", "previous_plan": plan_ref.as_dict(), "findings": findings_ref.as_dict(), "baseline_id": self._snapshot()["manifest_sha256"]})
                return
            passes = self._consecutive_plan_passes(plan_ref.sha256)
            if len(passes) >= 3:
                self._seal_plan(plan_ref, passes[-3:])
            else:
                self._create_semantic_request(role="reviewer", purpose="plan_review", body={"subject": plan_ref.as_dict(), "methodology_ref": "methodology/binding.json", "prior_findings": [], "candidate_number": self._last_event_payload("PLAN_CANDIDATE_RECORDED")["candidate_number"]})
        else:
            frozen = self._last_event_payload("FINAL_SUBJECT_FROZEN")
            require(frozen is not None and result["subject_sha256"] == frozen["subject_sha256"], "REVIEW_SUBJECT_MISMATCH", "final review subject mismatch")
            if disposition != "PASS":
                self._terminal("FAILED", "FINAL_REVIEW_NOT_CLEAN", [receipt_ref, findings_ref]); return
            passes = self._consecutive_final_passes(frozen["subject_sha256"])
            if len(passes) < 3:
                self._create_semantic_request(role="reviewer", purpose="final_review", body={"subject": frozen["subject"], "methodology_ref": "methodology/binding.json", "required_claims": ["mission_objective_satisfied", "final_find_loop_clean"]})

    def _seal_plan(self, plan_ref: ArtifactRef, passes: list[dict[str, Any]]) -> ArtifactRef:
        task_hash = sha256_file(self.task_root / "task.json")
        seal = {
            "schema_version": 1,
            "task_sha256": task_hash,
            "mission_sha256": self.task["mission"]["sha256"],
            "routing_resolver_sha256": self.task["routing"]["resolver_sha256"],
            "toolchain_sha256": sha256_file(self.task_root / "toolchain/catalog.json"),
            "methodology_sha256": sha256_file(self.task_root / "methodology/binding.json"),
            "inventory_sha256": sha256_file(self.task_root / "inventory/current-main.json"),
            "snapshot_sha256": self._snapshot()["manifest_sha256"],
            "plan": plan_ref.as_dict(),
            "qualifying_reviews": [payload["review_receipt"] for payload in passes],
        }
        ref = self.store.publish_json("plans/seal.json", seal)
        self.ledger.append("PLAN_SEALED", ref.ref, ref.sha256)
        return ref

    def _latest_checkpoint(self) -> tuple[int, Path]:
        payloads = [record["payload"] for record in self._events() if record["event"]["event_type"] == "CHECKPOINT_ACCEPTED" and isinstance(record["payload"], dict)]
        require(payloads, "CONTROL_STATE_FAILED", "no accepted checkpoint")
        number = max(int(payload["checkpoint_number"]) for payload in payloads)
        return number, self.task_root / "checkpoints" / f"{number:03d}" / "workspace"

    def _checkpoint_sha256(self, number: int) -> str:
        for record in reversed(self._events()):
            if record["event"]["event_type"] == "CHECKPOINT_ACCEPTED" and isinstance(record["payload"], dict) and int(record["payload"].get("checkpoint_number", -1)) == number:
                tree = record["payload"].get("tree")
                require(isinstance(tree, dict) and isinstance(tree.get("sha256"), str), "CONTROL_STATE_FAILED", "checkpoint hash unavailable")
                return tree["sha256"]
        raise STTError("CONTROL_STATE_FAILED", "checkpoint hash unavailable")

    def _descendant_count(self) -> int:
        return sum(1 for record in self._events() if record["event"]["event_type"] == "TASK_BOUND")

    def _active_task_binding(self) -> dict[str, Any] | None:
        bound: dict[str, Any] | None = None
        accepted: set[str] = set()
        for record in self._events():
            event = record["event"]["event_type"]
            payload = record.get("payload")
            if not isinstance(payload, dict):
                continue
            if event == "TASK_BOUND":
                bound = payload
            elif event == "TASK_RESULT_ACCEPTED":
                accepted.add(str(payload.get("child_task_id")))
        if bound and str(bound.get("child_task_id")) not in accepted:
            return bound
        return None

    def _task_binding_for(self, step: dict[str, Any], plan_ref: ArtifactRef) -> dict[str, Any]:
        number, _ = self._latest_checkpoint()
        checkpoint_sha = self._checkpoint_sha256(number)
        depth = int(self.task.get("depth", 0))
        require(depth < self.task["limits"]["max_task_depth"], "TASK_DEPTH_EXCEEDED", "Task depth limit exceeded")
        child_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "skeptic-task\0" + "\0".join([self.task_id, plan_ref.sha256, step["id"], checkpoint_sha])))
        return {
            "parent_task_id": self.task_id,
            "parent_plan_sha256": plan_ref.sha256,
            "parent_step_id": step["id"],
            "parent_checkpoint_sha256": checkpoint_sha,
            "depth": depth + 1,
            "child_task_id": child_id,
            "mission_sha256": sha256_bytes(step["mission"].encode("utf-8")),
        }

    def _bind_task(self, step: dict[str, Any], plan_ref: ArtifactRef) -> dict[str, Any]:
        existing = self._active_task_binding()
        if existing is not None:
            require(existing["parent_step_id"] == step["id"], "CONTROL_STATE_FAILED", "multiple active child Tasks")
            return existing
        binding = self._task_binding_for(step, plan_ref)
        input_number, input_workspace = self._latest_checkpoint()
        state_root = self.task_root.parent
        child_root = state_root / binding["child_task_id"]
        if child_root.exists():
            child = Runner(child_root, read_only=True)
            require(child.task_id == binding["child_task_id"], "CONTROL_STATE_FAILED", "existing deterministic child has the wrong Task ID")
            child_binding = child.task.get("parent_binding")
            require(child_binding == binding, "CONTROL_STATE_FAILED", "deterministic child identity has a mismatching binding")
        else:
            started = Runner.bootstrap(
                repo=Path(self.task["workspace"]["root"]), state_root=state_root, mission=step["mission"].encode("utf-8"),
                included_ignored=self.task["workspace"].get("included_ignored_paths", []),
                allow_unconfined=self.task["authority"]["candidate_dynamic_execution"] == "owner_risk_accepted",
                parent_binding=binding, task_id=binding["child_task_id"], input_checkpoint=input_workspace,
            )
            require(started["task_id"] == binding["child_task_id"], "CONTROL_STATE_FAILED", "child identity mismatch during creation")
        payload = {
            "schema_version": 1,
            "parent_step_id": step["id"],
            "child_task_id": binding["child_task_id"],
            "child_task_root": str(child_root),
            "parent_plan_sha256": binding["parent_plan_sha256"],
            "parent_checkpoint_sha256": binding["parent_checkpoint_sha256"],
            "parent_binding": binding,
            "input_checkpoint_number": input_number,
        }
        self._append_json_fact("TASK_BOUND", "tasks/bindings", payload)
        return payload

    def _child_result(self, child: "Runner", binding: dict[str, Any]) -> dict[str, Any]:
        from .verifier import verify_task_terminal

        return verify_task_terminal(Path(binding["child_task_root"]), expected_parent_binding=binding["parent_binding"], expected_success_outcome=TASK_OUTCOME)

    def _accept_task_result(self, binding: dict[str, Any], verified: dict[str, Any]) -> None:
        child = Runner(Path(binding["child_task_root"]), read_only=True)
        current_number, _ = self._latest_checkpoint()
        require(self._checkpoint_sha256(current_number) == binding["parent_checkpoint_sha256"], "TASK_CHECKPOINT_MISMATCH", "parent checkpoint changed before child acceptance")
        result = verified["result"]
        child_number = int(result["checkpoint"]["number"])
        child_workspace = child.task_root / "checkpoints" / f"{child_number:03d}" / "workspace"
        self._validate_tree(child_workspace)
        expected_tree = result["checkpoint"]["tree_sha256"]
        require(self._validate_tree(child_workspace)["sha256"] == expected_tree, "TASK_RESULT_INVALID", "reviewed child checkpoint hash mismatch")
        current_number, _ = self._latest_checkpoint()
        new_checkpoint: dict[str, Any] | None = None
        if expected_tree != self._checkpoint_sha256(current_number):
            next_number = current_number + 1
            candidate_root = self.task_root / "checkpoints" / f".{next_number:03d}.import-{uuid.uuid4().hex}"
            candidate = candidate_root / "workspace"
            self.store.admit(tree_storage_upper_bound(child_workspace))
            shutil.copytree(child_workspace, candidate, symlinks=True, dirs_exist_ok=False)
            tree = self._validate_tree(candidate)
            require(tree["sha256"] == expected_tree, "TASK_RESULT_INVALID", "staged child checkpoint hash mismatch")
            final_root = self.task_root / "checkpoints" / f"{next_number:03d}"
            if final_root.exists():
                existing_tree = self._validate_tree(final_root / "workspace")
                require(existing_tree["sha256"] == expected_tree, "CONTROL_STATE_FAILED", "conflicting existing checkpoint")
                shutil.rmtree(candidate_root)
                tree = existing_tree
            else:
                os.rename(candidate_root, final_root)
            receipt_path = final_root / "receipt.json"
            if receipt_path.is_file():
                receipt = self.store.adopt_existing(f"checkpoints/{next_number:03d}/receipt.json", max_size=self.task["limits"]["max_semantic_result_bytes"])
            else:
                receipt = self.store.publish_json(f"checkpoints/{next_number:03d}/receipt.json", {"schema_version": 1, "checkpoint_number": next_number, "step_id": None, "tree": tree, "child_task_id": child.task_id, "child_checkpoint_number": child_number})
            if not any(r["event"]["event_type"] == "CHECKPOINT_ACCEPTED" and isinstance(r.get("payload"), dict) and r["payload"].get("checkpoint_number") == next_number for r in self._events()):
                self.ledger.append("CHECKPOINT_ACCEPTED", receipt.ref, receipt.sha256)
            new_checkpoint = {"number": next_number, "tree_sha256": tree["sha256"], "receipt": receipt.as_dict()}
        imported = {"schema_version": 1, "result": result, "result_ref": verified["result_ref"].as_dict()}
        accepted = {"schema_version": 1, "parent_step_id": binding["parent_step_id"], "child_task_id": child.task_id, "verified_terminal_receipt": verified["terminal_ref"].as_dict(), "imported_result": imported, "new_parent_checkpoint": new_checkpoint}
        self._append_json_fact("TASK_RESULT_ACCEPTED", "tasks/results", accepted)

    def _completed_steps(self) -> set[str]:
        completed: set[str] = set()
        for record in self._events():
            if record["event"]["event_type"] in {"CHECKPOINT_ACCEPTED", "VALIDATION_RECORDED", "INSPECTION_RECORDED"} and isinstance(record["payload"], dict):
                step_id = record["payload"].get("step_id")
                if step_id:
                    completed.add(step_id)
            if record["event"]["event_type"] == "TASK_RESULT_ACCEPTED" and isinstance(record["payload"], dict):
                completed.add(str(record["payload"].get("parent_step_id")))
        return completed

    def _execute_next_step(self) -> bool:
        current = self._current_plan(); require(current is not None, "CONTROL_STATE_FAILED", "sealed Plan unavailable")
        plan, plan_ref = current; completed = self._completed_steps()
        next_step = next((step for step in plan["steps"] if step["id"] not in completed), None)
        if next_step is None:
            return False
        if next_step["kind"] == "task":
            raise STTError("CONTROL_STATE_FAILED", "task steps require the depth-first Runner path")
        if next_step["kind"] == "inspect":
            self._run_inspect_step(next_step)
            return True
        if next_step["kind"] == "change":
            number, checkpoint = self._latest_checkpoint(); capsule_root = self.task_root / "capsules" / next_step["id"] / uuid.uuid4().hex
            capsule_workspace = capsule_root / "workspace"
            self.store.admit(tree_storage_upper_bound(checkpoint))
            admission = materialize_capsule(checkpoint, capsule_workspace, next_step["read_scope"], next_step["write_scope"])
            admission_ref = self.store.publish_json(f"capsules/{next_step['id']}/{capsule_root.name}/admission.json", {"schema_version": 1, "step": next_step, "checkpoint_number": number, "checkpoint_path": str(checkpoint), "capsule_path": str(capsule_workspace), **admission})
            self._create_semantic_request(role="worker", purpose="change_step", body={"sealed_plan": plan_ref.as_dict(), "step": next_step, "checkpoint_number": number, "capsule_path": str(capsule_workspace), "admission": admission_ref.as_dict()})
            return True
        self._run_validation_step(next_step)
        return True

    def _run_inspect_step(self, step: dict[str, Any]) -> None:
        """Execute only the closed, deterministic read-only inspection capability."""
        source = Path(self.task["workspace"]["root"])
        inspected = Path(self.task["workspace"].get("input_checkpoint") or self._latest_checkpoint()[1])
        report: dict[str, Any] = {
            "schema_version": 1,
            "step_id": step["id"],
            "scope": step["scope"],
            "operation": step["operation"],
            "baseline": self._snapshot()["manifest_sha256"],
            "inspected_checkpoint": str(inspected),
            "source_workspace_unchanged": True,
        }
        if step["operation"] in {"repository_inventory", "git_state"}:
            report["git"] = {
                "head": run_git(source, ["rev-parse", "HEAD"]).stdout.decode().strip(),
                "branch": run_git(source, ["branch", "--show-current"]).stdout.decode().strip(),
                "status": run_git(source, ["status", "--short", "--branch"]).stdout.decode(errors="replace"),
            }
        if step["operation"] in {"repository_inventory", "task_artifact_inventory"}:
            report["entries"] = sorted(path.relative_to(inspected).as_posix() for path in inspected.rglob("*") if not path.is_symlink())
            report["task_roots"] = sorted(str(path) for path in self.task_root.parent.iterdir() if path.is_dir())
        ref = self.store.publish_json(f"inspect/steps/{step['id']}.json", report)
        self._append_json_fact("INSPECTION_RECORDED", "inspect/receipts", {"schema_version": 1, "step_id": step["id"], "report": ref.as_dict(), "source_workspace_unchanged": True})

    def _process_worker_result(self, request: dict[str, Any], result: dict[str, Any], result_ref: ArtifactRef) -> None:
        expected = {"schema_version", "operation_id", "request_sha256", "kind", "step_id", "summary", "declared_outputs"}
        require(set(result) == expected and result["kind"] == "WORKER_RESULT" and result["step_id"] == request["step"]["id"], "SEMANTIC_RESULT_MISSING_OR_INVALID", "Worker result invalid")
        step = request["step"]; parent = self.task_root / "checkpoints" / f"{request['checkpoint_number']:03d}" / "workspace"; capsule = Path(request["capsule_path"])
        delta = derive_delta(parent, capsule, step["write_scope"], self.task["limits"]["max_changed_paths_per_step"])
        next_number = int(request["checkpoint_number"]) + 1
        candidate_root = self.task_root / "checkpoints" / f".{next_number:03d}.candidate-{uuid.uuid4().hex}"; candidate = candidate_root / "workspace"
        self.store.admit(tree_storage_upper_bound(parent))
        overlay_delta(parent, capsule, candidate, delta)
        validation_refs: list[dict[str, Any]] = []
        catalog, _ = self._catalog()
        for index, command in enumerate(step["validation_commands"]):
            validation_copy = self.task_root / "validation" / step["id"] / f"{index:03d}-{uuid.uuid4().hex}" / "workspace"
            self.store.admit(tree_storage_upper_bound(candidate))
            copy_tree(candidate, validation_copy)
            result_command = run_command(candidate=validation_copy, command=command, catalog=catalog, logs_dir=self.task_root / "logs" / step["id"], mode=self.task["authority"]["candidate_dynamic_execution"], max_log_bytes=self.task["limits"]["max_command_log_bytes"])
            command_ref = self.store.publish_json(f"validation/{step['id']}/{index:03d}-{uuid.uuid4().hex}.json", result_command)
            validation_refs.append(command_ref.as_dict())
            if result_command.get("result_status") != "SUCCEEDED":
                reason = result_command.get("reason", result_command.get("result_status", "VALIDATION_FAILED"))
                if result_command.get("result_status") == "TERMINATION_UNKNOWN":
                    self._record_blocked_unknown(reason, [result_ref, command_ref])
                else:
                    self._terminal("FAILED", reason, [result_ref, command_ref])
                return
        tree = self._validate_tree(candidate)
        intent = self._append_json_fact("CHECKPOINT_PROMOTION_INTENT", "checkpoints/promotion-intents", {"schema_version": 1, "checkpoint_number": next_number, "step_id": step["id"], "candidate_path": str(candidate_root), "tree": tree, "delta": delta, "worker_result": result_ref.as_dict(), "validations": validation_refs})
        final_root = self.task_root / "checkpoints" / f"{next_number:03d}"
        require(not final_root.exists(), "CONTROL_STATE_FAILED", "checkpoint destination already exists")
        os.rename(candidate_root, final_root)
        receipt = self.store.publish_json(f"checkpoints/{next_number:03d}/receipt.json", {"schema_version": 1, "checkpoint_number": next_number, "step_id": step["id"], "tree": tree, "promotion_intent": intent.as_dict(), "worker_result": result_ref.as_dict(), "validations": validation_refs})
        self.ledger.append("CHECKPOINT_ACCEPTED", receipt.ref, receipt.sha256)

    def _run_validation_step(self, step: dict[str, Any]) -> None:
        _, checkpoint = self._latest_checkpoint(); catalog, _ = self._catalog(); refs: list[dict[str, Any]] = []
        for index, command in enumerate(step["commands"]):
            validation_copy = self.task_root / "validation" / step["id"] / f"{index:03d}-{uuid.uuid4().hex}" / "workspace"
            self.store.admit(tree_storage_upper_bound(checkpoint))
            copy_tree(checkpoint, validation_copy)
            result = run_command(candidate=validation_copy, command=command, catalog=catalog, logs_dir=self.task_root / "logs" / step["id"], mode=self.task["authority"]["candidate_dynamic_execution"], max_log_bytes=self.task["limits"]["max_command_log_bytes"])
            ref = self.store.publish_json(f"validation/{step['id']}/{index:03d}-{uuid.uuid4().hex}.json", result); refs.append(ref.as_dict())
            if result.get("result_status") != "SUCCEEDED":
                reason = result.get("reason", result.get("result_status", "VALIDATION_FAILED"))
                if result.get("result_status") == "TERMINATION_UNKNOWN":
                    self._record_blocked_unknown(reason, [ref])
                else:
                    self._terminal("FAILED", reason, [ref])
                return
        self._append_json_fact("VALIDATION_RECORDED", "validation/step-receipts", {"schema_version": 1, "step_id": step["id"], "commands": refs})

    def _freeze_final(self) -> None:
        number, checkpoint = self._latest_checkpoint(); catalog, _ = self._catalog()
        smoke_ref: ArtifactRef | None = None
        if self.task.get("qualification", {}).get("final_entrypoint_smoke_required") is True:
            smoke_script = checkpoint / "scripts/generic_host_smoke.py"
            require(smoke_script.is_file(), "FINAL_ENTRYPOINT_SMOKE_UNAVAILABLE", "candidate generic-host smoke missing")
            smoke_copy = self.task_root / "final-smoke" / uuid.uuid4().hex / "workspace"
            self.store.admit(tree_storage_upper_bound(checkpoint))
            copy_tree(checkpoint, smoke_copy)
            smoke_command = {"tool_id": "python", "args": ["scripts/generic_host_smoke.py"], "cwd": ".", "timeout_seconds": min(900, self.task["limits"]["max_semantic_operation_seconds"]), "accepted_exit_codes": [0]}
            smoke = run_command(candidate=smoke_copy, command=smoke_command, catalog=catalog, logs_dir=self.task_root / "logs/final-smoke", mode=self.task["authority"]["candidate_dynamic_execution"], max_log_bytes=self.task["limits"]["max_command_log_bytes"])
            smoke_ref = self.store.publish_json("final/smoke.json", smoke)
            if smoke.get("result_status") != "SUCCEEDED":
                self._terminal("FAILED", "FINAL_ENTRYPOINT_SMOKE_FAILED", [smoke_ref]); return
        task_results = [record["payload"] for record in self._events() if record["event"]["event_type"] == "TASK_RESULT_ACCEPTED" and isinstance(record["payload"], dict)]
        inspect_results = [record["payload"] for record in self._events() if record["event"]["event_type"] == "INSPECTION_RECORDED" and isinstance(record["payload"], dict)]
        report_ref: ArtifactRef | None = None
        if self._current_plan()[0].get("delivery_kind") == "inspect":
            report_ref = self.store.publish_json("inspect/report.json", {"schema_version": 1, "baseline": self._snapshot()["manifest_sha256"], "source_workspace_unchanged": True, "inspections": inspect_results, "accepted_task_results": task_results, "done": ["inventory_scope_completed", "report_bound_to_baseline", "source_workspace_unchanged", "mission_objective_satisfied", "final_find_loop_clean"]})
        tree = self._validate_tree(checkpoint)
        result_artifacts = [report_ref.as_dict()] if report_ref else []
        result_value = {"schema_version": 1, "checkpoint": {"number": number, "tree_sha256": tree["sha256"]}, "artifacts": result_artifacts}
        result_ref = self.store.publish_json("final/task-result.json", result_value)
        subject = {"schema_version": 1, "checkpoint_number": number, "tree": tree, "result": result_ref.as_dict(), "accepted_task_results": task_results, "inspection_results": inspect_results, "done_proof": ["plan_sealed", "final_subject_frozen", "three_final_reviews"]}
        subject_bytes = canonical_json_bytes(subject); subject_ref = self.store.publish_bytes("final/frozen-subject.json", subject_bytes)
        freeze_ref = self.store.publish_json("final/freeze-receipt.json", {"schema_version": 1, "subject": subject_ref.as_dict(), "subject_sha256": subject_ref.sha256, "result": result_ref.as_dict(), "checkpoint_number": number, "smoke": smoke_ref.as_dict() if smoke_ref else None, "inspect_report": report_ref.as_dict() if report_ref else None})
        self.ledger.append("FINAL_SUBJECT_FROZEN", freeze_ref.ref, freeze_ref.sha256)
        self._create_semantic_request(role="reviewer", purpose="final_review", body={"subject": subject_ref.as_dict(), "methodology_ref": "methodology/binding.json", "required_claims": ["mission_objective_satisfied", "final_find_loop_clean"]})

    def _consecutive_final_passes(self, subject_sha: str) -> list[dict[str, Any]]:
        passes: list[dict[str, Any]] = []
        for record in reversed(self._events()):
            if record["event"]["event_type"] == "FINAL_SUBJECT_FROZEN":
                break
            if record["event"]["event_type"] == "FINAL_REVIEW_RECORDED" and isinstance(record["payload"], dict):
                payload = record["payload"]
                claims = set(payload.get("claims") or [])
                if payload.get("subject_sha256") == subject_sha and payload.get("qualifying") is True and {"mission_objective_satisfied", "final_find_loop_clean"}.issubset(claims):
                    passes.append(payload)
                else:
                    break
        return list(reversed(passes))

    def _verify_installed_candidate(self, source: Path, final_checkpoint: Path) -> tuple[dict[str, Any], dict[str, Any]]:
        candidate = self._validate_tree(final_checkpoint)
        candidate_map = {entry["path"]: entry for entry in candidate["entries"]}
        for rel, entry in candidate_map.items():
            path = source / rel
            require(path.exists() or path.is_symlink(), "INSTALLED_TREE_MISMATCH", "candidate path missing after cutover", path=rel)
            st = os.lstat(path); mode = stat.S_IMODE(st.st_mode)
            require(mode == entry["mode"], "INSTALLED_TREE_MISMATCH", "mode mismatch after cutover", path=rel)
            if entry["kind"] == "directory":
                require(stat.S_ISDIR(st.st_mode), "INSTALLED_TREE_MISMATCH", "kind mismatch after cutover", path=rel)
            elif entry["kind"] == "symlink":
                require(stat.S_ISLNK(st.st_mode) and os.readlink(path) == entry["target"], "INSTALLED_TREE_MISMATCH", "symlink mismatch after cutover", path=rel)
            else:
                require(stat.S_ISREG(st.st_mode) and sha256_file(path) == entry["sha256"], "INSTALLED_TREE_MISMATCH", "file mismatch after cutover", path=rel)
        snapshot = self._snapshot()
        execution_paths = {entry["path"] for entry in snapshot["execution_entries"]}
        excluded = {entry["path"]: entry for entry in snapshot["all_entries"] if entry["path"] not in execution_paths}
        for rel, entry in excluded.items():
            path = source / rel
            require(path.exists() or path.is_symlink(), "EXCLUDED_PATH_CHANGED", "excluded path disappeared", path=rel)
            st = os.lstat(path); mode = stat.S_IMODE(st.st_mode)
            require(mode == entry["mode"], "EXCLUDED_PATH_CHANGED", "excluded path mode changed", path=rel)
            if entry["kind"] == "directory":
                require(stat.S_ISDIR(st.st_mode), "EXCLUDED_PATH_CHANGED", "excluded directory kind changed", path=rel)
            elif entry["kind"] == "symlink":
                require(stat.S_ISLNK(st.st_mode) and os.readlink(path) == entry["target"], "EXCLUDED_PATH_CHANGED", "excluded symlink changed", path=rel)
            else:
                require(stat.S_ISREG(st.st_mode) and sha256_file(path) == entry["sha256"], "EXCLUDED_PATH_CHANGED", "excluded file changed", path=rel)
        for rel in execution_paths - set(candidate_map):
            path = source / rel
            original = next(entry for entry in snapshot["execution_entries"] if entry["path"] == rel)
            if original["kind"] == "directory" and path.is_dir() and any(path.iterdir()):
                continue
            require(not path.exists() and not path.is_symlink(), "INSTALLED_TREE_MISMATCH", "removed execution path remains", path=rel)
        installed_subject = {"schema_version": 1, "candidate_entries": candidate["entries"], "excluded_preserved_count": len(excluded)}
        installed_subject["sha256"] = sha256_bytes(canonical_json_bytes(installed_subject))
        return installed_subject, candidate

    def _apply_cutover(self) -> None:
        require(self.task.get("parent_task_id") is None, "TASK_CUTOVER_FORBIDDEN", "only the root Task may cut over the authoritative repository")
        frozen = self._last_event_payload("FINAL_SUBJECT_FROZEN"); require(frozen is not None, "CONTROL_STATE_FAILED", "final subject not frozen")
        passes = self._consecutive_final_passes(frozen["subject_sha256"]); require(len(passes) >= 3, "FINAL_REVIEW_NOT_CLEAN", "three final qualifying passes missing")
        final_number = frozen["checkpoint_number"]; final_checkpoint = self.task_root / "checkpoints" / f"{final_number:03d}" / "workspace"; baseline = self.task_root / "checkpoints/000/workspace"
        manifest = build_manifest(baseline, final_checkpoint); manifest_ref = self.store.publish_json("cutover/manifest.json", manifest)
        self.store.admit(tree_storage_upper_bound(baseline))
        source = Path(self.task["workspace"]["root"]); verify_source_identity(source, self._snapshot())
        intent_ref = self.store.publish_json("cutover/intent.json", {"schema_version": 1, "manifest": manifest_ref.as_dict(), "source": str(source), "final_checkpoint": str(final_checkpoint)})
        self.ledger.append("CUTOVER_INTENT_RECORDED", intent_ref.ref, intent_ref.sha256)
        apply_manifest(source_repo=source, final_candidate=final_checkpoint, manifest=manifest, journal=self.task_root / "cutover/journal.json", backup_root=self.task_root / "cutover/backup")
        installed, candidate = self._verify_installed_candidate(source, final_checkpoint)
        snapshot = self._snapshot()
        require(run_git(source, ["rev-parse", "HEAD"]).stdout.decode().strip() == snapshot["head"], "GIT_CONTROL_CHANGED", "HEAD changed")
        require(sha256_bytes(run_git(source, ["ls-files", "--stage", "-z"]).stdout) == snapshot["index_tree"], "GIT_CONTROL_CHANGED", "index changed")
        branch_proc = run_git(source, ["symbolic-ref", "--short", "-q", "HEAD"], check=False); branch = branch_proc.stdout.decode().strip() if branch_proc.returncode == 0 else None
        require(branch == snapshot["branch"], "GIT_CONTROL_CHANGED", "branch changed")
        applied_ref = self.store.publish_json("cutover/applied.json", {"schema_version": 1, "manifest": manifest_ref.as_dict(), "installed_tree_sha256": installed["sha256"], "candidate_tree_sha256": candidate["sha256"]})
        self.ledger.append("CUTOVER_APPLIED", applied_ref.ref, applied_ref.sha256)
        self._terminal("COMPLETE", "SIGNED_PLAN_AND_DONE_PROOF_SATISFIED", [manifest_ref, applied_ref])

    def _record_blocked_unknown(self, reason: str, refs: list[ArtifactRef]) -> ArtifactRef:
        existing = self._last_event_payload("TASK_BLOCKED_UNKNOWN")
        if existing and existing.get("reason") == reason:
            return ArtifactRef(**existing["receipt"])
        receipt = self.store.publish_json(f"blocked/{uuid.uuid4().hex}.json", {"schema_version": 1, "status": "BLOCKED_UNKNOWN", "reason": reason, "evidence": [ref.as_dict() for ref in refs], "resumable": True})
        marker = self.store.publish_json(f"blocked/events/{uuid.uuid4().hex}.json", {"schema_version": 1, "reason": reason, "receipt": receipt.as_dict()})
        self.ledger.append("TASK_BLOCKED_UNKNOWN", marker.ref, marker.sha256)
        return receipt

    def _terminal(self, outcome: str, reason: str, refs: list[ArtifactRef]) -> ArtifactRef:
        existing = self._last_event_payload("TERMINAL_RECEIPT_RECORDED")
        if existing:
            return ArtifactRef(existing["receipt"]["ref"], existing["receipt"]["sha256"], existing["receipt"]["size"])
        frozen = self._last_event_payload("FINAL_SUBJECT_FROZEN")
        result = frozen.get("result") if outcome == TASK_OUTCOME and frozen else None
        value = {"schema_version": 1, "outcome": outcome, "reason": reason, "accepted_checkpoint": self._latest_checkpoint()[0] if (self.task_root / "checkpoints").exists() else None, "result": result, "evidence": [ref.as_dict() for ref in refs], "publication_occurred": False}
        receipt = self.store.publish_json("terminal/receipt.json", value)
        marker = self.store.publish_json("terminal/event.json", {"schema_version": 1, "receipt": receipt.as_dict(), "outcome": outcome})
        self.ledger.append("TERMINAL_RECEIPT_RECORDED", marker.ref, marker.sha256)
        return receipt

    def receipt(self, status: str, next_action: str | None, refs: list[ArtifactRef], reason: str | None = None) -> dict[str, Any]:
        events = self.ledger.read(recover_partial=not self.read_only); head = events[-1].event_sha256 if events else "0" * 64
        return compact_receipt(task_id=self.task_id, task_root=self.task_root, status=status, next_action=next_action, ledger_head=head, refs=[ref.as_dict() for ref in refs], reason=reason)

    def _status_unlocked(self) -> dict[str, Any]:
        terminal = self._last_event_payload("TERMINAL_RECEIPT_RECORDED")
        if terminal:
            receipt = terminal["receipt"]
            return self.receipt(terminal["outcome"], None, [ArtifactRef(**receipt)])
        task_block = self._last_event_payload("TASK_BLOCKED_UNKNOWN")
        if task_block:
            return self.receipt("BLOCKED_UNKNOWN", "RECONCILE_OPERATION", [ArtifactRef(**task_block["receipt"])], task_block["reason"])
        pending = self._pending_operation()
        if pending:
            request, request_ref = pending
            reduced = derive(self._events(), pending_operation=request)
            unknown = self._last_event_payload("OPERATION_UNKNOWN")
            if unknown and unknown.get("operation_id") == request["operation_id"]:
                return self.receipt("BLOCKED_UNKNOWN", "RECONCILE_OPERATION", [request_ref], "semantic operation status remains inconclusive; no redispatch performed")
            result_path = self.task_root / request["result_ref"]
            if self._last_event_payload("OPERATION_RESULT_REJECTED") and any(r["event"]["event_type"] == "OPERATION_RESULT_REJECTED" and r["payload"].get("operation_id") == request["operation_id"] for r in self._events() if isinstance(r.get("payload"), dict)):
                return self.receipt(reduced["status"], reduced["next_action"], [request_ref], "operation result rejected; retry or replan")
            if result_path.is_file():
                return self.receipt("RUNNING", "FINALIZE_OPERATION", [request_ref])
            action = {"planner": "DISPATCH_PLANNER", "reviewer": "DISPATCH_REVIEWER", "worker": "DISPATCH_WORKER"}[request["role"]]
            return self.receipt("RUNNING", action, [request_ref])
        if not self._last_event_payload("PLAN_SEALED"):
            current = self._current_plan()
            return self.receipt("RUNNING", "DISPATCH_PLAN_REVIEW" if current else "DISPATCH_PLANNER", [])
        if not self._last_event_payload("FINAL_SUBJECT_FROZEN"):
            active = self._active_task_binding()
            if active is not None:
                child = Runner(Path(active["child_task_root"]), read_only=True)
                child_status = child.status()
                if child_status["status"] == TASK_OUTCOME:
                    return self.receipt("RUNNING", "ACCEPT_TASK_RESULT", [], "terminal child result awaits parent verification")
                if child_status["status"] in {"FAILED", "BLOCKED_UNKNOWN", "STOPPED"}:
                    return self.receipt(child_status["status"], "RESUME_CHILD_TASK" if child_status["status"] == "STOPPED" else "RUN_PARENT", [], "child Task is terminal and parent has not accepted it")
                return self.receipt("RUNNING", "RUN_CHILD_TASK", [], "active Task chain descends into child")
            return self.receipt("RUNNING", "EXECUTE_OR_VALIDATE_NEXT_STEP", [])
        frozen = self._last_event_payload("FINAL_SUBJECT_FROZEN")
        if len(self._consecutive_final_passes(frozen["subject_sha256"])) < 3:
            return self.receipt("RUNNING", "DISPATCH_FINAL_REVIEW", [])
        if not self._last_event_payload("CUTOVER_APPLIED"):
            return self.receipt("RUNNING", "APPLY_CUTOVER", [])
        return self.receipt("CONTROL_STATE_FAILED", None, [], "cutover exists without terminal receipt")

    def status(self) -> dict[str, Any]:
        return self._status_unlocked()

    def run(self) -> dict[str, Any]:
        for _ in range(64):
            child_binding: dict[str, Any] | None = None
            with self._task_lease():
                terminal = self._last_event_payload("TERMINAL_RECEIPT_RECORDED")
                if terminal or self._last_event_payload("TASK_BLOCKED_UNKNOWN"):
                    return self._status_unlocked()
                pending = self._pending_operation()
                if pending:
                    request, request_ref = pending
                    try:
                        adopted = self._adopt_result(request)
                    except STTError as exc:
                        if exc.code == "BLOCKED_UNKNOWN":
                            return self.receipt("BLOCKED_UNKNOWN", "RECONCILE_OPERATION", [request_ref], exc.message)
                        rejection = self._reject_operation(request, exc)
                        return self.receipt("REJECTED", "RETRY_OPERATION", [request_ref, rejection], exc.message)
                    if adopted is None:
                        return self._status_unlocked()
                    result, result_ref, provider_report = adopted
                    evidence_ref = self.store.adopt_existing(request["_provider_evidence_ref"], max_size=self.task["limits"]["max_semantic_result_bytes"])
                    try:
                        if request["role"] == "planner":
                            self._process_planner_result(request, result, result_ref)
                        elif request["role"] == "reviewer":
                            self._process_reviewer_result(request, result, result_ref, provider_report)
                        else:
                            self._process_worker_result(request, result, result_ref)
                    except STTError as exc:
                        rejection = self._reject_operation(request, exc)
                        return self.receipt("REJECTED", "RETRY_OPERATION", [request_ref, rejection], exc.message)
                    self._accept_operation(request, result_ref, evidence_ref)
                    continue
                if not self._last_event_payload("PLAN_SEALED"):
                    current = self._current_plan()
                    if current is None:
                        return self.receipt("CONTROL_STATE_FAILED", None, [], "no pending Planner request and no Plan")
                    _, plan_ref = current
                    self._create_semantic_request(role="reviewer", purpose="plan_review", body={"subject": plan_ref.as_dict(), "methodology_ref": "methodology/binding.json", "prior_findings": [], "candidate_number": self._last_event_payload("PLAN_CANDIDATE_RECORDED")["candidate_number"]})
                    continue
                current = self._current_plan()
                require(current is not None, "CONTROL_STATE_FAILED", "sealed Plan unavailable")
                plan, plan_ref = current
                if not self._last_event_payload("FINAL_SUBJECT_FROZEN"):
                    completed = self._completed_steps()
                    next_step = next((step for step in plan["steps"] if step["id"] not in completed), None)
                    if next_step is not None and next_step["kind"] == "task":
                        child_binding = self._bind_task(next_step, plan_ref)
                    elif self._execute_next_step():
                        continue
                    else:
                        self._freeze_final()
                        continue
                else:
                    frozen = self._last_event_payload("FINAL_SUBJECT_FROZEN")
                    if len(self._consecutive_final_passes(frozen["subject_sha256"])) < 3:
                        self._create_semantic_request(role="reviewer", purpose="final_review", body={"subject": frozen["subject"], "methodology_ref": "methodology/binding.json", "required_claims": ["mission_objective_satisfied", "final_find_loop_clean"]})
                        continue
                    if self.task.get("parent_task_id") is not None:
                        self._terminal(TASK_OUTCOME, "TASK_FINAL_REVIEWS_COMPLETE", [])
                        continue
                    with self._workspace_lease():
                        self._apply_cutover()
                    continue
            if child_binding is not None:
                child = Runner(Path(child_binding["child_task_root"]))
                child_status = child.status()
                if child_status["status"] not in {"COMPLETE", "FAILED", "BLOCKED_UNKNOWN", "STOPPED"}:
                    child.run()
                child_status = child.status()
                with self._task_lease():
                    if child_status["status"] in {"RUNNING", "REJECTED", "RETRYABLE"}:
                        return self.receipt("RUNNING", "RUN_CHILD_TASK", [], "deepest child Task is not terminal")
                    if child_status["status"] == "STOPPED":
                        return self.receipt("STOPPED", "RESUME_CHILD_TASK", [], "child Task stopped; parent remains resumable")
                    if child_status["status"] != TASK_OUTCOME:
                        self._terminal("BLOCKED_UNKNOWN" if child_status["status"] == "BLOCKED_UNKNOWN" else "FAILED", "CHILD_TASK_" + child_status["status"], [])
                        return self._status_unlocked()
                    verified = self._child_result(child, child_binding)
                    self._accept_task_result(child_binding, verified)
                continue
        return self.receipt("RUNNING", "FOREGROUND_CYCLE_BOUND_REACHED", [])

    def reconcile(self) -> dict[str, Any]:
        task_lease, workspace_lease = self._leases()
        should_run = False
        with task_lease, workspace_lease:
            pending = self._pending_operation()
            if not pending:
                return self._status_unlocked()
            request, request_ref = pending
            result_path = self.task_root / request["result_ref"]
            evidence_path = self.task_root / request["_provider_evidence_ref"]
            if result_path.is_file() and evidence_path.is_file():
                should_run = True
            else:
                return self.receipt("BLOCKED_UNKNOWN", "RECONCILE_OPERATION", [request_ref], "host adapter must provide conclusive operation evidence; no redispatch performed")
        if should_run:
            return self.run()
        raise STTError("CONTROL_STATE_FAILED", "unreachable reconcile state")

    def restore(self, destination: Path) -> dict[str, Any]:
        task_lease, _ = self._leases()
        with task_lease:
            destination = destination.resolve(strict=False)
            require(not destination.exists() or not any(destination.iterdir()), "RESTORE_DESTINATION_NOT_EMPTY", "restore destination must be empty")
            destination.mkdir(parents=True, exist_ok=True)
            source = self.task_root / "preservation" / "initial" / "preserved_workspace"
            shutil.copytree(source, destination, symlinks=True, dirs_exist_ok=True)
            tree = self._validate_tree(destination)
            ref = self.store.publish_json(f"restore/{uuid.uuid4().hex}.json", {"destination": str(destination), "tree": tree})
            return self.receipt("RESTORED", None, [ref])

    def retry(self) -> dict[str, Any]:
        pending = self._pending_operation()
        if not pending:
            return self._status_unlocked()
        request, ref = pending
        return self.receipt("RETRYABLE", {"planner": "DISPATCH_PLANNER", "reviewer": "DISPATCH_REVIEWER", "worker": "DISPATCH_WORKER"}[request["role"]], [ref], "rejected operation remains pending")

    def replan(self) -> dict[str, Any]:
        pending = self._pending_operation()
        require(pending is not None and pending[0]["role"] == "planner", "CONTROL_STATE_FAILED", "replan requires a pending Planner operation")
        request, ref = pending
        new_ref = self._create_semantic_request(role="planner", purpose="replan", body={"mission": self.task["mission"], "baseline_id": self._snapshot()["manifest_sha256"], "supersedes": ref.as_dict(), "schema_ref": "concepts/stt/schema.py"})
        return self.receipt("REPLANNED", "DISPATCH_PLANNER", [ref, new_ref])

    def stop(self) -> dict[str, Any]:
        if self._last_event_payload("TERMINAL_RECEIPT_RECORDED"):
            return self._status_unlocked()
        receipt = self._terminal("STOPPED", "OWNER_STOP_REQUESTED", [])
        return self.receipt("STOPPED", None, [receipt])

    def resume(self) -> dict[str, Any]:
        terminal = self._last_event_payload("TERMINAL_RECEIPT_RECORDED")
        require(not terminal or terminal.get("outcome") == "STOPPED", "CONTROL_STATE_FAILED", "only stopped tasks can be resumed")
        if terminal:
            return self.receipt("RESUMABLE", "RUN", [])
        return self.run()

    def diagnose(self) -> dict[str, Any]:
        state = self._status_unlocked()
        state["diagnosis"] = {"ledger_head": state.get("ledger_head"), "pending_operation": state.get("next_action"), "authoritative": "ledger.jsonl"}
        return state
