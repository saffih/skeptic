from __future__ import annotations

import os
import re
import shutil
import stat
import uuid
from pathlib import Path
from typing import Any, Iterable

from .artifacts import ArtifactRef, ArtifactStore
from .boundary import compact_receipt, discover_nested_repositories, scope_overlaps_nested
from .canonical import canonical_json_bytes, ensure_no_symlink_components, fsync_dir, loads_strict, safe_relpath, sha256_bytes, sha256_file
from .capsule import apply_delta, derive_delta, materialize_capsule, object_identity, prepare_capsule_admission, validate_workspace_target
from .command import run_command
from .contracts import DEFAULT_LIMITS
from .errors import STTError, require
from .gitutil import resolve_repo, run_git
from .host import load_adapter
from .inventory import derive_toolchain
from .ledger import Ledger
from .locks import Lease, lock_root, workspace_key
from .plan import validate_plan


TASK_OUTCOME = "COMPLETE"
ROLE_EFFECT_TYPES = {
    "PLAN_CANDIDATE_RECORDED",
    "PLAN_REVIEW_RECORDED",
    "FINAL_REVIEW_RECORDED",
    "EVIDENCE_BUNDLE_EXTENDED",
    "OPERATION_RESULT",
}
FORBIDDEN_EVIDENCE_EXPORT_PREFIXES = (
    "ledger.jsonl",
    "task.json",
    "routing/",
    "semantic/admissions/",
    "semantic/provider-evidence/",
    "semantic/results/",
    "semantic/requests/",
)
TASK_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z")


class Runner:
    def __init__(self, task_root: Path, *, read_only: bool = False, _allow_creating: bool = False) -> None:
        raw_root = Path(os.path.realpath(os.path.abspath(os.fspath(task_root))))
        ensure_no_symlink_components(raw_root)
        try:
            root_stat = os.lstat(raw_root)
        except FileNotFoundError as exc:
            raise STTError("TASK_NOT_FOUND", "Task root not found") from exc
        require(stat.S_ISDIR(root_stat.st_mode) and root_stat.st_uid == os.geteuid(), "TASK_ROOT_UNSAFE", "Task root owner/type mismatch")
        self.task_root = raw_root
        task_path = self.task_root / "task.json"
        task_stat = os.lstat(task_path)
        require(stat.S_ISREG(task_stat.st_mode) and task_stat.st_uid == os.geteuid() and task_stat.st_nlink == 1, "TASK_FILE_UNSAFE", "task.json is not an owned unique regular file")
        self.task = loads_strict(task_path.read_bytes())
        require(isinstance(self.task, dict) and self.task.get("schema_version") == 1, "TASK_SCHEMA", "task.json schema invalid")
        self.task_id = self.task.get("task_id")
        creating_name = isinstance(self.task_id, str) and self.task_root.name.startswith(f".{self.task_id}.creating-")
        require(isinstance(self.task_id, str) and TASK_ID.fullmatch(self.task_id) is not None and (self.task_root.name == self.task_id or (_allow_creating and creating_name)), "TASK_SCHEMA", "Task identity invalid")
        limits = self.task.get("limits")
        require(isinstance(limits, dict) and limits == DEFAULT_LIMITS, "TASK_SCHEMA", "Task limits must equal the current enforced policy")
        self.read_only = read_only
        self.store = ArtifactStore(self.task_root, max_bytes=limits["max_task_state_bytes"], min_free_reserve=limits["min_free_space_reserve_bytes"])
        self.ledger = Ledger(self.task_root, self.task_id)
        if read_only:
            require(self.ledger.path.is_file(), "LEDGER_MISSING", "ledger.jsonl not found")
            self.ledger.read(recover_partial=False)
        else:
            self.ledger.initialize()

    @staticmethod
    def bootstrap(
        *,
        repo: Path,
        state_root: Path,
        mission: bytes,
        included_ignored: list[str],
        allow_unconfined: bool = False,
        require_final_entrypoint_smoke: bool = False,
        task_id: str | None = None,
        parent_binding: dict[str, Any] | None = None,
        read_only_authority: bool = False,
    ) -> dict[str, Any]:
        if allow_unconfined:
            raise STTError(
                "UNCONFINED_SHARED_WORKSPACE_EXECUTION_UNSUPPORTED",
                "Unconfined command execution is unsupported because STT operates directly on the shared workspace. Dynamic commands require a successfully initialized sandbox.",
            )
        repo_root, git_common = resolve_repo(repo)
        require(isinstance(mission, bytes), "MISSION_NOT_UTF8", "mission must be bytes")
        try:
            require(mission.decode("utf-8").strip() != "", "MISSION_REQUIRED", "mission is effectively blank")
        except UnicodeDecodeError as exc:
            raise STTError("MISSION_NOT_UTF8", "mission must be UTF-8") from exc
        require(len(mission) <= DEFAULT_LIMITS["max_request_bytes"], "MISSION_TOO_LARGE", "mission exceeds request-size limit")
        included = sorted(safe_relpath(path) for path in included_ignored)
        workspace_state = repo_root / ".stt"
        if workspace_state.exists() or workspace_state.is_symlink():
            workspace_state_stat = os.lstat(workspace_state)
            require(stat.S_ISDIR(workspace_state_stat.st_mode) and not stat.S_ISLNK(workspace_state_stat.st_mode) and workspace_state_stat.st_uid == os.geteuid(), "STATE_ROOT_UNSAFE", "workspace .stt must be an owned real directory")
        state_root = Path(os.path.realpath(os.path.abspath(os.fspath(state_root))))
        local_state = (repo_root / ".stt" / "tasks").resolve(strict=False)
        require(state_root == local_state or (state_root not in repo_root.parents and repo_root not in state_root.parents), "STATE_ROOT_UNSAFE", "state root overlaps repository unsafely")
        local_state_selected = state_root == local_state
        ensure_no_symlink_components(state_root, include_leaf=False)
        state_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if local_state_selected:
            os.chmod(workspace_state, 0o700)
        state_stat = os.lstat(state_root)
        require(stat.S_ISDIR(state_stat.st_mode) and state_stat.st_uid == os.geteuid(), "STATE_ROOT_UNSAFE", "state root owner/type mismatch")
        if stat.S_IMODE(state_stat.st_mode) != 0o700:
            os.chmod(state_root, 0o700)
        ensure_no_symlink_components(state_root)
        final_id = task_id or str(uuid.uuid4())
        require(isinstance(final_id, str) and TASK_ID.fullmatch(final_id) is not None, "TASK_ID_INVALID", "Task identity must be a bounded path-safe token")
        final_root = state_root / final_id
        require(not final_root.exists() and not final_root.is_symlink(), "TASK_ID_COLLISION", "deterministic Task identity already exists")
        temporary_root = state_root / f".{final_id}.creating-{uuid.uuid4().hex}"
        provider_id = os.environ.get("STT_PROVIDER", "generic-recorded-host")
        adapter = load_adapter(provider_id)
        capabilities = adapter.discover_capabilities()
        require(capabilities.available, "HOST_CAPABILITY_UNAVAILABLE", f"semantic provider unavailable: {provider_id}")
        require(set(capabilities.semantic_roles) >= {"planner", "reviewer", "worker"}, "HOST_CAPABILITY_UNAVAILABLE", "provider lacks required semantic roles")
        require(capabilities.durable_invocation_id and capabilities.status_inspection, "HOST_CAPABILITY_UNAVAILABLE", "provider lacks durable operation evidence")
        git_observation = {
            "head": run_git(repo_root, ["rev-parse", "HEAD"]).stdout.decode().strip(),
            "branch": run_git(repo_root, ["branch", "--show-current"]).stdout.decode().strip(),
            "status": run_git(repo_root, ["status", "--short", "--branch", "--untracked-files=no"]).stdout.decode(errors="replace"),
        }
        baseline = {"schema_version": 1, "execution_model": "shared_workspace", "git": git_observation}
        baseline["manifest_sha256"] = sha256_bytes(canonical_json_bytes(baseline))
        nested_roots = discover_nested_repositories(repo_root)
        inherited_read_only = bool(read_only_authority or (parent_binding or {}).get("read_only_authority") is True)
        try:
            limits = dict(DEFAULT_LIMITS)
            store = ArtifactStore(temporary_root, max_bytes=limits["max_task_state_bytes"], min_free_reserve=limits["min_free_space_reserve_bytes"])
            store.initialize()
            mission_ref = store.publish_bytes("mission.txt", mission)
            routing = {
                "schema_version": 1,
                "provider_id": provider_id,
                "capabilities": {
                    "durable_invocation_id": capabilities.durable_invocation_id,
                    "status_inspection": capabilities.status_inspection,
                    "evidence_schema": capabilities.evidence_schema,
                },
                "profiles": {
                    "economical": {"provider": provider_id, "role": adapter.provider_role("planner"), "model": "economical", "effort": "low"},
                    "standard": {"provider": provider_id, "role": adapter.provider_role("reviewer"), "model": "standard", "effort": "medium"},
                },
            }
            routing_ref = store.publish_json("routing/resolver.json", routing)
            task = {
                "schema_version": 1,
                "task_id": final_id,
                "mission": mission_ref.as_dict(),
                "workspace": {
                    "root": str(repo_root),
                    "git_common_dir": str(git_common),
                    "included_ignored_paths": included,
                    "execution_model": "shared_workspace_sequential",
                    "baseline": baseline,
                    "nested_repository_roots": nested_roots,
                },
                "authority": {
                    "working_tree_repair": not inherited_read_only,
                    "read_only": inherited_read_only,
                    "semantic_provider_dispatch": True,
                    "provider_disclosure_scope": "declared_execution_policy_evidence_only",
                    "task_runtime_network": False,
                    "task_runtime_external_side_effects": False,
                    "git_control_mutation": False,
                    "commit_or_publication": False,
                    "candidate_dynamic_execution": "sandbox_required",
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
                "parent_workspace_sha256": parent_binding.get("parent_workspace_sha256") if parent_binding else None,
                "depth": int(parent_binding.get("depth", 0)) if parent_binding else 0,
                "read_only_authority": inherited_read_only,
            }
            task_ref = store.publish_json("task.json", task)
            ledger = Ledger(temporary_root, final_id)
            ledger.initialize()
            ledger.append("TASK_CREATED", task_ref.ref, task_ref.sha256)
            creating = Runner(temporary_root, _allow_creating=True)
            creating._prepare_initial_state()
            Runner(temporary_root, read_only=True, _allow_creating=True)
            os.rename(temporary_root, final_root)
            fsync_dir(state_root)
        except BaseException:
            if temporary_root.exists() and temporary_root.is_dir() and not temporary_root.is_symlink():
                shutil.rmtree(temporary_root)
            raise
        return Runner(final_root).status()

    def _task_lease(self) -> Lease:
        return Lease(self.task_root / ".task.lock", "TASK_BUSY")

    def _workspace_lease(self) -> Lease:
        root = lock_root(self.task_root)
        key = workspace_key(Path(self.task["workspace"]["git_common_dir"]))
        return Lease(root / f"workspace-{key}.lock", "WORKSPACE_BUSY")

    def _events(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for event in self.ledger.read(recover_partial=not self.read_only):
            payload_path = self.task_root / event.value["payload_ref"]
            payload = loads_strict(payload_path.read_bytes())
            require(isinstance(payload, dict), "LEDGER_PAYLOAD_SCHEMA", "lifecycle payload must be an object")
            records.append({"event": event.value, "payload": payload})
        return records

    def _event_ref(self, record: dict[str, Any]) -> ArtifactRef:
        event = record["event"]
        return ArtifactRef(event["payload_ref"], event["payload_sha256"], event["payload_size"])

    def _append_json_fact(self, event_type: str, directory: str, value: dict[str, Any]) -> ArtifactRef:
        ref = self.store.publish_json(f"{directory}/{uuid.uuid4().hex}.json", value)
        self.ledger.append(event_type, ref.ref, ref.sha256)
        return ref

    def _last_event_record(self, event_type: str) -> dict[str, Any] | None:
        for record in reversed(self._events()):
            if record["event"]["event_type"] == event_type:
                return record
        return None

    def _last_event_payload(self, event_type: str) -> dict[str, Any] | None:
        record = self._last_event_record(event_type)
        return record["payload"] if record else None

    def _fact_ref(self, event_type: str) -> ArtifactRef:
        record = self._last_event_record(event_type)
        require(record is not None, "CONTROL_STATE_FAILED", f"required lifecycle fact missing: {event_type}")
        return self._event_ref(record)

    def _prepare_initial_state(self) -> None:
        source_root = self._workspace()
        skeptic = source_root / "skeptic.md"
        require(skeptic.is_file() and not skeptic.is_symlink(), "SKEPTIC_SOURCE_UNAVAILABLE", "skeptic.md missing from shared workspace")
        baseline = self.task["workspace"]["baseline"]
        baseline_ref = self.store.publish_json("baseline/workspace.json", baseline)
        inventory = {
            "schema_version": 1,
            "git": baseline["git"],
            "baseline": baseline_ref.as_dict(),
            "nested_repository_roots": self.task["workspace"]["nested_repository_roots"],
            "scope": "shared_workspace_observation",
        }
        inventory_ref = self.store.publish_json("inventory/current.json", inventory)
        self.ledger.append("INVENTORY_RECORDED", inventory_ref.ref, inventory_ref.sha256)
        catalog_ref = self.store.publish_json("toolchain/catalog.json", derive_toolchain())
        self.ledger.append("TOOLCHAIN_BOUND", catalog_ref.ref, catalog_ref.sha256)
        skeptic_ref = self.store.publish_bytes("methodology/sources/skeptic.md", skeptic.read_bytes())
        companions: list[dict[str, Any]] = []
        companion = source_root / "skeptic-questions.md"
        if companion.is_file() and not companion.is_symlink():
            companions.append(self.store.publish_bytes("methodology/sources/skeptic-questions.md", companion.read_bytes()).as_dict())
        methodology_ref = self.store.publish_json("methodology/binding.json", {"schema_version": 1, "skeptic": skeptic_ref.as_dict(), "companions": companions})
        self.ledger.append("METHODOLOGY_BOUND", methodology_ref.ref, methodology_ref.sha256)
        self._create_semantic_request(
            role="planner",
            purpose="initial_plan",
            body={
                "mission": self.task["mission"],
                "baseline": baseline_ref.as_dict(),
                "inventory": inventory_ref.as_dict(),
                "toolchain": catalog_ref.as_dict(),
                "methodology": methodology_ref.as_dict(),
                "baseline_id": baseline["manifest_sha256"],
                "read_only_authority": self.task["read_only_authority"],
            },
        )

    def _create_semantic_request(self, *, role: str, purpose: str, body: dict[str, Any]) -> ArtifactRef:
        require(role in {"planner", "reviewer", "worker"}, "CONTROL_STATE_FAILED", "unknown semantic role")
        operation_id = f"{len(self.ledger.read(recover_partial=True)) + 1}-{uuid.uuid4()}"
        result_dir = self.task_root / "semantic" / "results" / operation_id
        result_dir.mkdir(parents=True, mode=0o700)
        request = {
            "schema_version": 1,
            "operation_id": operation_id,
            "attempt": 1,
            "role": role,
            "purpose": purpose,
            "result_ref": f"semantic/results/{operation_id}/result.json",
            **body,
        }
        request_bytes = canonical_json_bytes(request)
        require(len(request_bytes) <= self.task["limits"]["max_request_bytes"], "REQUEST_TOO_LARGE", "semantic request exceeds request-size limit")
        request_ref = self.store.publish_bytes(f"semantic/requests/{operation_id}.json", request_bytes)
        routing = loads_strict(self.store.verify(ArtifactRef(self.task["routing"]["resolver_ref"], self.task["routing"]["resolver_sha256"], (self.task_root / self.task["routing"]["resolver_ref"]).stat().st_size)).read_bytes())
        admission = self.store.publish_json(
            f"semantic/admissions/{operation_id}.json",
            {
                "schema_version": 1,
                "operation_id": operation_id,
                "attempt": 1,
                "request": request_ref.as_dict(),
                "role": role,
                "purpose": purpose,
                "provider_id": routing["provider_id"],
                "provider_evidence_ref": f"semantic/provider-evidence/{operation_id}.json",
            },
        )
        self.ledger.append("OPERATION_ADMITTED", admission.ref, admission.sha256)
        return request_ref

    def _consumed_operation_ids(self) -> set[str]:
        consumed: set[str] = set()
        for record in self._events():
            if record["event"]["event_type"] not in {"OPERATION_ACCEPTED", "OPERATION_SUPERSEDED", "TERMINAL_RECEIPT_RECORDED", "TASK_BLOCKED_UNKNOWN"}:
                continue
            operation_id = record["payload"].get("operation_id")
            if isinstance(operation_id, str) and operation_id:
                consumed.add(operation_id)
        return consumed

    def _pending_operation(self) -> tuple[dict[str, Any], ArtifactRef] | None:
        consumed = self._consumed_operation_ids()
        active: list[tuple[dict[str, Any], ArtifactRef]] = []
        for record in self._events():
            if record["event"]["event_type"] != "OPERATION_ADMITTED":
                continue
            admission = record["payload"]
            operation_id = admission.get("operation_id")
            if operation_id in consumed:
                continue
            request_ref = ArtifactRef.from_dict(admission.get("request"))
            request = loads_strict(self.store.verify(request_ref).read_bytes())
            require(isinstance(request, dict) and request.get("operation_id") == operation_id, "CONTROL_STATE_FAILED", "semantic admission/request binding mismatch")
            request["_provider_evidence_ref"] = admission["provider_evidence_ref"]
            request["_provider_id"] = admission["provider_id"]
            request["_request_ref"] = request_ref.as_dict()
            request["_admission_ref"] = self._event_ref(record).as_dict()
            active.append((request, request_ref))
        require(len(active) <= 1, "CONTROL_STATE_FAILED", "multiple concurrent semantic operations are active")
        return active[0] if active else None

    def _effect_records(self, operation_id: str) -> list[dict[str, Any]]:
        return [record for record in self._events() if record["event"]["event_type"] in ROLE_EFFECT_TYPES and record["payload"].get("operation_id") == operation_id]

    def _operation_unknown_unresolved(self, operation_id: str) -> bool:
        unknown_sequence = 0
        conclusive_sequence = 0
        for record in self._events():
            if record["payload"].get("operation_id") != operation_id:
                continue
            event_type = record["event"]["event_type"]
            if event_type == "OPERATION_UNKNOWN":
                unknown_sequence = record["event"]["sequence"]
            elif event_type == "OPERATION_RESULT_REJECTED" or event_type in ROLE_EFFECT_TYPES:
                conclusive_sequence = record["event"]["sequence"]
        return unknown_sequence > conclusive_sequence

    def _verify_refs_recursive(self, value: Any) -> None:
        if isinstance(value, dict):
            if set(value) == {"ref", "sha256", "size"}:
                self.store.verify(ArtifactRef.from_dict(value))
                return
            for child in value.values():
                self._verify_refs_recursive(child)
        elif isinstance(value, list):
            for child in value:
                self._verify_refs_recursive(child)

    def _verify_effect(self, record: dict[str, Any], request_ref: ArtifactRef) -> None:
        payload = record["payload"]
        required = {"operation_id", "request", "result", "provider_evidence"}
        require(required <= set(payload), "ROLE_EFFECT_INVALID", "role effect lacks immutable operation bindings")
        require(payload["request"] == request_ref.as_dict(), "ROLE_EFFECT_INVALID", "role effect request binding mismatch")
        self._verify_refs_recursive(payload)

    def _accept_effect(self, request: dict[str, Any], request_ref: ArtifactRef, effect: dict[str, Any]) -> ArtifactRef:
        self._verify_effect(effect, request_ref)
        effect_ref = self._event_ref(effect)
        value = {
            "schema_version": 1,
            "operation_id": request["operation_id"],
            "role": request["role"],
            "purpose": request["purpose"],
            "effect": {
                "event_type": effect["event"]["event_type"],
                "payload": effect_ref.as_dict(),
                "event_sha256": effect["event"]["event_sha256"],
            },
        }
        ref = self.store.publish_json(f"accepted/{request['operation_id']}/{uuid.uuid4().hex}-acceptance.json", value)
        self.ledger.append("OPERATION_ACCEPTED", ref.ref, ref.sha256)
        return ref

    def _accepted_effects(self, event_type: str | None = None) -> list[dict[str, Any]]:
        effects_by_sha = {record["event"]["event_sha256"]: record for record in self._events() if record["event"]["event_type"] in ROLE_EFFECT_TYPES}
        accepted: list[dict[str, Any]] = []
        accepted_operations: set[str] = set()
        for record in self._events():
            if record["event"]["event_type"] != "OPERATION_ACCEPTED":
                continue
            acceptance = record["payload"]
            require(set(acceptance) == {"schema_version", "operation_id", "role", "purpose", "effect"} and acceptance.get("schema_version") == 1, "OPERATION_ACCEPTANCE_INVALID", "operation acceptance schema invalid")
            binding = acceptance.get("effect")
            require(isinstance(binding, dict) and set(binding) == {"event_type", "payload", "event_sha256"}, "OPERATION_ACCEPTANCE_INVALID", "operation acceptance effect binding missing")
            effect = effects_by_sha.get(binding.get("event_sha256"))
            require(effect is not None, "OPERATION_ACCEPTANCE_INVALID", "operation acceptance effect missing")
            require(binding.get("event_type") == effect["event"]["event_type"] and binding.get("payload") == self._event_ref(effect).as_dict(), "OPERATION_ACCEPTANCE_INVALID", "operation acceptance effect mismatch")
            require(record["payload"].get("operation_id") == effect["payload"].get("operation_id"), "OPERATION_ACCEPTANCE_INVALID", "operation acceptance identity mismatch")
            operation_id = record["payload"]["operation_id"]
            require(operation_id not in accepted_operations, "OPERATION_ACCEPTANCE_INVALID", "operation accepted more than once")
            require(effect["event"]["sequence"] < record["event"]["sequence"], "OPERATION_ACCEPTANCE_INVALID", "operation acceptance precedes its effect")
            accepted_operations.add(operation_id)
            request_ref = ArtifactRef.from_dict(effect["payload"].get("request"))
            request = loads_strict(self.store.verify(request_ref).read_bytes())
            require(isinstance(request, dict) and request.get("operation_id") == operation_id and request.get("role") == acceptance["role"] and request.get("purpose") == acceptance["purpose"], "OPERATION_ACCEPTANCE_INVALID", "operation acceptance request metadata mismatch")
            self._verify_refs_recursive(effect["payload"])
            if event_type is None or effect["event"]["event_type"] == event_type:
                accepted.append(effect)
        return accepted

    def _freeze_staging(
        self,
        request: dict[str, Any],
        ref: str,
        label: str,
        *,
        max_size: int | None = None,
        provider_evidence: bool = False,
    ) -> ArtifactRef:
        rel = safe_relpath(ref)
        if provider_evidence:
            require(rel == request["_provider_evidence_ref"], "PROVIDER_STAGING_PATH_INVALID", "provider evidence source differs from the admitted staging path")
        else:
            result_directory = request["result_ref"].rsplit("/", 1)[0] + "/"
            require(rel.startswith(result_directory), "PROVIDER_STAGING_PATH_INVALID", "provider artifact source is outside this operation's staging directory")
        return self.store.freeze_existing(
            rel,
            accepted_prefix=f"accepted/{request['operation_id']}",
            label=label,
            max_size=max_size or self.task["limits"]["max_semantic_result_bytes"],
        )

    def _adopt_result(self, request: dict[str, Any]) -> tuple[dict[str, Any], ArtifactRef, dict[str, Any], ArtifactRef] | None:
        result_path = self.task_root / request["result_ref"]
        evidence_path = self.task_root / request["_provider_evidence_ref"]
        if not evidence_path.is_file():
            return None
        evidence_ref = self._freeze_staging(request, request["_provider_evidence_ref"], "provider-evidence.json", provider_evidence=True)
        adapter = load_adapter(request["_provider_id"])
        report = adapter.validate_provider_evidence(self.store.verify(evidence_ref).read_bytes())
        require(report.provider_id == request["_provider_id"], "PROVIDER_IDENTITY_MISMATCH", "provider evidence identity mismatch")
        if report.status == "UNKNOWN":
            observations = [record for record in self._events() if record["event"]["event_type"] == "OPERATION_UNKNOWN" and record["payload"].get("operation_id") == request["operation_id"]]
            latest_unknown = observations[-1] if observations else None
            if latest_unknown is None or latest_unknown["payload"].get("provider_evidence", {}).get("sha256") != evidence_ref.sha256 or not self._operation_unknown_unresolved(request["operation_id"]):
                self._append_json_fact(
                    "OPERATION_UNKNOWN",
                    "semantic/operation-unknown",
                    {
                        "schema_version": 1,
                        "operation_id": request["operation_id"],
                        "request": request["_request_ref"],
                        "provider_evidence": evidence_ref.as_dict(),
                        "provider_report": report.as_dict(),
                    },
                )
            raise STTError("OPERATION_STATUS_UNKNOWN", "semantic operation remains inconclusive")
        require(report.status == "COMPLETE", "SEMANTIC_OPERATION_FAILED", "semantic provider reported failure", report=report.as_dict())
        if not result_path.is_file():
            return None
        result_ref = self._freeze_staging(request, request["result_ref"], "result.json")
        result = loads_strict(self.store.verify(result_ref).read_bytes())
        require(isinstance(result, dict), "SEMANTIC_RESULT_MISSING_OR_INVALID", "semantic result must be an object")
        require(result.get("schema_version") == 1 and result.get("operation_id") == request["operation_id"], "SEMANTIC_RESULT_MISSING_OR_INVALID", "semantic result identity mismatch")
        require(result.get("request_sha256") == ArtifactRef.from_dict(request["_request_ref"]).sha256, "SEMANTIC_RESULT_MISSING_OR_INVALID", "semantic request hash mismatch")
        return result, result_ref, report.as_dict(), evidence_ref

    def _reject_operation(self, request: dict[str, Any], exc: STTError) -> ArtifactRef:
        return self._append_json_fact(
            "OPERATION_RESULT_REJECTED",
            "semantic/operation-rejected",
            {"schema_version": 1, "operation_id": request["operation_id"], "role": request["role"], "code": exc.code, "message": exc.message, "retryable": True},
        )

    def _effect_base(self, request: dict[str, Any], result_ref: ArtifactRef, evidence_ref: ArtifactRef) -> dict[str, Any]:
        return {
            "operation_id": request["operation_id"],
            "request": ArtifactRef.from_dict(request["_request_ref"]).as_dict(),
            "result": result_ref.as_dict(),
            "provider_evidence": evidence_ref.as_dict(),
        }

    def _catalog(self) -> tuple[dict[str, Any], ArtifactRef]:
        ref = self._fact_ref("TOOLCHAIN_BOUND")
        value = loads_strict(self.store.verify(ref).read_bytes())
        require(isinstance(value, dict), "CONTROL_STATE_FAILED", "toolchain artifact invalid")
        return value, ref

    def _inventory(self) -> tuple[dict[str, Any], ArtifactRef]:
        ref = self._fact_ref("INVENTORY_RECORDED")
        value = loads_strict(self.store.verify(ref).read_bytes())
        require(isinstance(value, dict), "CONTROL_STATE_FAILED", "inventory artifact invalid")
        return value, ref

    def _methodology_ref(self) -> ArtifactRef:
        return self._fact_ref("METHODOLOGY_BOUND")

    def _baseline(self) -> dict[str, Any]:
        return self.task["workspace"]["baseline"]

    def _nested_roots(self) -> tuple[str, ...]:
        stored = tuple(self.task["workspace"].get("nested_repository_roots", []))
        current = tuple(discover_nested_repositories(self._workspace()))
        return tuple(sorted(set(stored) | set(current)))

    def _disclosed_artifacts(self, request: dict[str, Any]) -> set[tuple[str, str, int]]:
        disclosed: set[tuple[str, str, int]] = set()

        def visit(value: Any) -> None:
            if isinstance(value, dict):
                if set(value) == {"ref", "sha256", "size"}:
                    ref = ArtifactRef.from_dict(value)
                    disclosed.add((ref.ref, ref.sha256, ref.size))
                    return
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        visit({key: value for key, value in request.items() if not key.startswith("_")})
        return disclosed

    def _read_workspace_evidence(self, raw: Any) -> tuple[str, bytes]:
        require(isinstance(raw, str), "EVIDENCE_SELECTOR_INVALID", "workspace selector path must be a string")
        rel = safe_relpath(raw)
        overlap = scope_overlaps_nested(rel, self._nested_roots())
        require(overlap is None, "EVIDENCE_SELECTOR_INVALID", "workspace evidence cannot reach a nested repository", path=rel, nested_root=overlap)
        path = validate_workspace_target(self._workspace(), rel, nested_roots=self._nested_roots())
        ensure_no_symlink_components(path)
        value = os.lstat(path)
        require(stat.S_ISREG(value.st_mode) and value.st_uid == os.geteuid() and value.st_nlink == 1, "EVIDENCE_SELECTOR_INVALID", "workspace selector must name an owned unique regular file")
        require(value.st_mode & 0o7000 == 0 and value.st_mode & 0o022 == 0, "EVIDENCE_SELECTOR_INVALID", "workspace evidence file is not owner-controlled")
        require(value.st_size <= self.task["limits"]["max_single_file_bytes"], "SINGLE_FILE_LIMIT", "evidence file exceeds single-file limit")
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            opened = os.fstat(fd)
            require((opened.st_dev, opened.st_ino, opened.st_size) == (value.st_dev, value.st_ino, value.st_size), "EVIDENCE_SELECTOR_INVALID", "workspace evidence changed before read")
            chunks: list[bytes] = []
            remaining = opened.st_size
            while remaining:
                chunk = os.read(fd, min(1024 * 1024, remaining))
                require(bool(chunk), "EVIDENCE_SELECTOR_INVALID", "workspace evidence was truncated during read")
                chunks.append(chunk); remaining -= len(chunk)
            require(os.read(fd, 1) == b"" and os.fstat(fd).st_size == opened.st_size, "EVIDENCE_SELECTOR_INVALID", "workspace evidence changed during read")
            return rel, b"".join(chunks)
        finally:
            os.close(fd)

    def _process_evidence_request(self, request: dict[str, Any], result: dict[str, Any], result_ref: ArtifactRef, evidence_ref: ArtifactRef) -> ArtifactRef:
        require(set(result) == {"schema_version", "operation_id", "request_sha256", "kind", "selectors"} and result.get("kind") == "NEEDS_EVIDENCE", "SEMANTIC_RESULT_MISSING_OR_INVALID", "NEEDS_EVIDENCE schema invalid")
        prior = [record for record in self._accepted_effects("EVIDENCE_BUNDLE_EXTENDED") if record["payload"].get("purpose") == request["purpose"] and record["payload"].get("role") == request["role"]]
        require(len(prior) < self.task["limits"]["max_evidence_rounds_per_purpose"], "EVIDENCE_BUDGET_EXHAUSTED", "evidence round limit exceeded")
        selectors = result["selectors"]
        require(isinstance(selectors, list) and len(selectors) <= self.task["limits"]["max_evidence_refs_per_round"], "EVIDENCE_BUDGET_EXHAUSTED", "invalid evidence selector set")
        bundle_id = uuid.uuid4().hex
        items: list[dict[str, Any]] = []
        total = 0
        disclosed = self._disclosed_artifacts(request)
        for index, selector in enumerate(selectors):
            require(isinstance(selector, dict) and selector.get("kind") in {"workspace_path", "exported_task_artifact"}, "EVIDENCE_SELECTOR_INVALID", "evidence selector schema invalid")
            if selector["kind"] == "workspace_path":
                require(set(selector) == {"kind", "path"} and request["role"] == "planner", "EVIDENCE_SELECTOR_INVALID", "only Planner may request a workspace path")
                source_name, data = self._read_workspace_evidence(selector["path"])
            else:
                require(set(selector) == {"kind", "artifact"}, "EVIDENCE_SELECTOR_INVALID", "exported artifact selector schema invalid")
                artifact = ArtifactRef.from_dict(selector["artifact"])
                require((artifact.ref, artifact.sha256, artifact.size) in disclosed, "EVIDENCE_SELECTOR_INVALID", "artifact was not disclosed in this semantic request")
                require(not any(artifact.ref == prefix or artifact.ref.startswith(prefix) for prefix in FORBIDDEN_EVIDENCE_EXPORT_PREFIXES), "EVIDENCE_SELECTOR_INVALID", "artifact class is not exportable")
                data = self.store.verify(artifact).read_bytes()
                source_name = Path(artifact.ref).name
            total += len(data)
            require(total <= self.task["limits"]["max_evidence_bytes_per_round"], "EVIDENCE_BUDGET_EXHAUSTED", "evidence byte limit exceeded")
            item_ref = self.store.publish_bytes(f"evidence/{bundle_id}/{index:03d}-{uuid.uuid4().hex}-{source_name}", data)
            items.append({"selector": selector, "artifact": item_ref.as_dict()})
        bundle = self.store.publish_json(f"evidence/{bundle_id}/manifest.json", {"schema_version": 1, "purpose": request["purpose"], "role": request["role"], "items": items})
        payload = {
            "schema_version": 1,
            **self._effect_base(request, result_ref, evidence_ref),
            "purpose": request["purpose"],
            "role": request["role"],
            "round": len(prior) + 1,
            "bundle": bundle.as_dict(),
        }
        self._append_json_fact("EVIDENCE_BUNDLE_EXTENDED", "effects/evidence", payload)
        return bundle

    def _process_planner_result(self, request: dict[str, Any], result: dict[str, Any], result_ref: ArtifactRef, evidence_ref: ArtifactRef) -> None:
        if result.get("kind") == "NEEDS_EVIDENCE":
            self._process_evidence_request(request, result, result_ref, evidence_ref)
            return
        expected = {"schema_version", "operation_id", "request_sha256", "kind", "plan_ref", "plan_sha256", "finding_map_ref"}
        require(set(result) == expected and result["kind"] == "PLAN_CANDIDATE", "SEMANTIC_RESULT_MISSING_OR_INVALID", "Planner result schema invalid")
        require(isinstance(result["plan_ref"], str) and isinstance(result["finding_map_ref"], str), "SEMANTIC_RESULT_MISSING_OR_INVALID", "Planner artifact paths invalid")
        plan_ref = self._freeze_staging(request, result["plan_ref"], "plan.json")
        require(plan_ref.sha256 == result["plan_sha256"], "PLAN_BINDING", "Planner Plan hash mismatch")
        finding_map_ref = self._freeze_staging(request, result["finding_map_ref"], "finding-map.json", max_size=self.task["limits"]["max_request_bytes"])
        finding_map = loads_strict(self.store.verify(finding_map_ref).read_bytes())
        require(isinstance(finding_map, dict) and set(finding_map) == {"findings"} and isinstance(finding_map["findings"], list), "FINDING_MAP_INVALID", "finding map must contain exactly a findings array")
        plan = loads_strict(self.store.verify(plan_ref).read_bytes())
        catalog, _ = self._catalog()
        validate_plan(
            plan,
            mission_sha256=self.task["mission"]["sha256"],
            baseline_id=self._baseline()["manifest_sha256"],
            catalog_ids={tool["tool_id"] for tool in catalog["tools"]},
            source_paths=[self.task["workspace"]["root"], self.task["workspace"]["git_common_dir"], str(self.task_root)],
            limits=self.task["limits"],
            nested_roots=self._nested_roots(),
            read_only_authority=self.task["read_only_authority"],
        )
        prior_candidates = len(self._accepted_effects("PLAN_CANDIDATE_RECORDED")) + len(self._effect_records(request["operation_id"]))
        require(prior_candidates < self.task["limits"]["max_plan_candidates"], "PLAN_CANDIDATE_BUDGET_EXHAUSTED", "Plan candidate budget exhausted")
        self._append_json_fact(
            "PLAN_CANDIDATE_RECORDED",
            "effects/plans",
            {
                "schema_version": 1,
                **self._effect_base(request, result_ref, evidence_ref),
                "candidate_number": prior_candidates + 1,
                "plan": plan_ref.as_dict(),
                "finding_map": finding_map_ref.as_dict(),
                "baseline_id": self._baseline()["manifest_sha256"],
            },
        )

    def _process_reviewer_result(self, request: dict[str, Any], result: dict[str, Any], result_ref: ArtifactRef, provider_report: dict[str, Any], evidence_ref: ArtifactRef) -> None:
        if result.get("review_disposition") == "NEEDS_EVIDENCE" or result.get("kind") == "NEEDS_EVIDENCE":
            self._process_evidence_request(request, result, result_ref, evidence_ref)
            return
        expected = {"schema_version", "operation_id", "request_sha256", "protocol_outcome", "review_disposition", "runskeptic_final_outcome", "receipt_ref", "findings_ref", "subject_sha256", "session_id", "claims"}
        require(set(result) == expected and result["protocol_outcome"] == "COMPLETE", "SEMANTIC_RESULT_MISSING_OR_INVALID", "Reviewer result schema invalid")
        disposition = result["review_disposition"]
        require(disposition in {"PASS", "ACTION", "CONFLICT"}, "SEMANTIC_RESULT_MISSING_OR_INVALID", "Reviewer disposition invalid")
        require(isinstance(result["receipt_ref"], str) and isinstance(result["findings_ref"], str), "SEMANTIC_RESULT_MISSING_OR_INVALID", "Reviewer artifact paths invalid")
        receipt_ref = self._freeze_staging(request, result["receipt_ref"], "review-receipt.json")
        findings_ref = self._freeze_staging(request, result["findings_ref"], "review-findings.json")
        receipt_value = loads_strict(self.store.verify(receipt_ref).read_bytes())
        findings = loads_strict(self.store.verify(findings_ref).read_bytes())
        require(isinstance(receipt_value, dict), "SEMANTIC_RESULT_MISSING_OR_INVALID", "Reviewer receipt invalid")
        require(isinstance(findings, dict) and set(findings) == {"findings"} and isinstance(findings["findings"], list), "SEMANTIC_RESULT_MISSING_OR_INVALID", "Reviewer finding set invalid")
        prior_sessions = {record["payload"].get("session_id") for record in [*self._accepted_effects("PLAN_REVIEW_RECORDED"), *self._accepted_effects("FINAL_REVIEW_RECORDED")]}
        require(result["session_id"] == provider_report["invocation_id"], "REVIEW_INDEPENDENCE_UNEVIDENCED", "Reviewer session does not match provider invocation identity")
        require(result["session_id"] not in prior_sessions and result["session_id"] not in {None, "", "UNKNOWN"}, "REVIEW_INDEPENDENCE_UNEVIDENCED", "Reviewer session identity missing or reused")
        require(isinstance(result["claims"], list) and all(isinstance(item, str) for item in result["claims"]), "SEMANTIC_RESULT_MISSING_OR_INVALID", "Reviewer claims invalid")
        qualifying = disposition == "PASS" and not findings["findings"] and result["runskeptic_final_outcome"] == "PASS"
        event_type = "PLAN_REVIEW_RECORDED" if request["purpose"] == "plan_review" else "FINAL_REVIEW_RECORDED"
        limit_name = "max_plan_reviews" if event_type == "PLAN_REVIEW_RECORDED" else "max_final_find_reviews"
        require(len(self._accepted_effects(event_type)) < self.task["limits"][limit_name], "REVIEW_BUDGET_EXHAUSTED", "review budget exhausted")
        effect_payload = {
            "schema_version": 1,
            **self._effect_base(request, result_ref, evidence_ref),
            "purpose": request["purpose"],
            "subject_sha256": result["subject_sha256"],
            "session_id": result["session_id"],
            "disposition": disposition,
            "qualifying": qualifying,
            "review_receipt": receipt_ref.as_dict(),
            "findings": findings_ref.as_dict(),
            "claims": result["claims"],
        }
        if event_type == "PLAN_REVIEW_RECORDED":
            candidate_operation_id = request.get("candidate_operation_id")
            require(isinstance(candidate_operation_id, str) and candidate_operation_id, "SEMANTIC_RESULT_MISSING_OR_INVALID", "Plan review candidate operation binding missing")
            effect_payload["candidate_operation_id"] = candidate_operation_id
        self._append_json_fact(
            event_type,
            "effects/reviews",
            effect_payload,
        )

    def _freeze_command_logs(self, result: dict[str, Any], *, category: str) -> dict[str, Any]:
        frozen = dict(result)
        for stream in ("stdout", "stderr"):
            value = result.get(stream)
            if not isinstance(value, dict) or not isinstance(value.get("path"), str):
                continue
            path = Path(value["path"])
            ensure_no_symlink_components(path)
            data = path.read_bytes()
            require(len(data) == value.get("size") and sha256_bytes(data) == value.get("sha256"), "COMMAND_LOG_CHANGED", "command log changed before freezing")
            frozen[stream] = self.store.publish_bytes(f"command-logs/{category}/{uuid.uuid4().hex}-{stream}.log", data).as_dict()
        return frozen

    def _run_bound_command(self, command: dict[str, Any], *, category: str) -> tuple[dict[str, Any], ArtifactRef]:
        catalog, _ = self._catalog()
        with self._workspace_lease():
            result = run_command(
                candidate=self._workspace(),
                command=command,
                catalog=catalog,
                logs_dir=self.task_root / "command-staging" / category,
                mode=self.task["authority"]["candidate_dynamic_execution"],
                max_log_bytes=self.task["limits"]["max_command_log_bytes"],
                max_scratch_bytes=self.task["limits"]["max_command_scratch_bytes"],
                max_processes=self.task["limits"]["max_command_processes"],
                max_address_space_bytes=self.task["limits"]["max_command_address_space_bytes"],
            )
        frozen = self._freeze_command_logs(result, category=category)
        ref = self.store.publish_json(f"validation/{category}/{uuid.uuid4().hex}.json", frozen)
        return frozen, ref

    def _worker_failure_evidence(self, *, intent: dict[str, Any], application_state: str, validations: list[dict[str, Any]], reason: str) -> ArtifactRef:
        return self.store.publish_json(
            f"worker-failures/{intent['operation_id']}/{uuid.uuid4().hex}.json",
            {
                "schema_version": 1,
                "operation_id": intent["operation_id"],
                "step_id": intent["step_id"],
                "kind": "WORKER_EXECUTION_FAILED",
                "application_state": application_state,
                "delta": intent["delta"],
                "worker_result": intent["worker_result"],
                "provider_evidence": intent["provider_evidence"],
                "admission": intent["admission"],
                "validations": validations,
                "reason": reason,
            },
        )

    def _worker_state_reserve(self, intent: dict[str, Any], validation_count: int) -> int:
        """Bound state needed to finish or honestly fail after workspace mutation."""
        limits = self.task["limits"]
        command_state = validation_count * (
            2 * limits["max_command_log_bytes"] + limits["max_request_bytes"]
        )
        control_state = 3 * len(canonical_json_bytes(intent)) + 8 * limits["max_request_bytes"] + 1024 * 1024
        return command_state + control_state

    def _process_worker_result(self, request: dict[str, Any], result: dict[str, Any], result_ref: ArtifactRef, evidence_ref: ArtifactRef) -> None:
        expected = {"schema_version", "operation_id", "request_sha256", "kind", "step_id", "summary", "declared_outputs"}
        require(set(result) == expected and result["kind"] == "WORKER_RESULT" and result["step_id"] == request["step"]["id"], "SEMANTIC_RESULT_MISSING_OR_INVALID", "Worker result invalid")
        require(isinstance(result["summary"], str) and isinstance(result["declared_outputs"], list), "SEMANTIC_RESULT_MISSING_OR_INVALID", "Worker result fields invalid")
        admission_ref = ArtifactRef.from_dict(request["admission"])
        admission = loads_strict(self.store.verify(admission_ref).read_bytes())
        require(isinstance(admission, dict) and admission.get("step") == request["step"], "CAPSULE_ADMISSION_INVALID", "Worker admission binding invalid")
        manifest = admission.get("manifest")
        require(isinstance(manifest, dict), "CAPSULE_ADMISSION_INVALID", "Worker admission manifest missing")
        step = request["step"]
        capsule = Path(request["capsule_path"])
        delta = derive_delta(manifest, capsule, step["write_scope"], self.task["limits"])
        intent = {
            "schema_version": 1,
            "operation_id": request["operation_id"],
            "step_id": step["id"],
            "delta": delta,
            "worker_result": result_ref.as_dict(),
            "provider_evidence": evidence_ref.as_dict(),
            "admission": admission_ref.as_dict(),
        }
        self.store.admit(self._worker_state_reserve(intent, len(step["validation_commands"])))
        self._append_json_fact("WORKER_DELTA_INTENT_RECORDED", "worker-intents", intent)
        try:
            with self._workspace_lease():
                apply_delta(
                    self._workspace(),
                    capsule,
                    delta,
                    step["write_scope"],
                    max_single_file_bytes=self.task["limits"]["max_single_file_bytes"],
                    nested_roots=self._nested_roots(),
                )
        except Exception as exc:
            failure = self._worker_failure_evidence(intent=intent, application_state="partial_or_unknown", validations=[], reason=f"APPLY_DELTA_FAILED: {type(exc).__name__}: {exc}")
            self._record_blocked_unknown("WORKER_DELTA_PARTIAL_OR_UNKNOWN", [failure], operation_id=request["operation_id"])
            return
        validations: list[dict[str, Any]] = []
        for index, command in enumerate(step["validation_commands"]):
            try:
                command_result, command_ref = self._run_bound_command(command, category=f"{step['id']}-{index:03d}")
            except Exception as exc:
                failure = self._worker_failure_evidence(intent=intent, application_state="applied", validations=validations, reason=f"VALIDATION_EXECUTION_FAILED: {type(exc).__name__}: {exc}")
                self._terminal("FAILED", "VALIDATION_EXECUTION_FAILED", [failure], operation_id=request["operation_id"])
                return
            validations.append(command_ref.as_dict())
            if command_result.get("result_status") != "SUCCEEDED":
                reason = command_result.get("reason", command_result.get("result_status", "VALIDATION_FAILED"))
                failure = self._worker_failure_evidence(intent=intent, application_state="applied", validations=validations, reason=reason)
                if command_result.get("result_status") == "TERMINATION_UNKNOWN":
                    self._record_blocked_unknown(reason, [failure], operation_id=request["operation_id"])
                else:
                    self._terminal("FAILED", reason, [failure], operation_id=request["operation_id"])
                return
        self._append_json_fact(
            "OPERATION_RESULT",
            "effects/worker-results",
            {
                "schema_version": 1,
                **self._effect_base(request, result_ref, evidence_ref),
                "step_id": step["id"],
                "kind": "WORKER_DELTA_APPLIED",
                "delta": delta,
                "worker_result": result_ref.as_dict(),
                "admission": admission_ref.as_dict(),
                "validations": validations,
            },
        )

    def _unresolved_worker_intent(self) -> dict[str, Any] | None:
        resolved: set[str] = set()
        for record in self._events():
            if record["event"]["event_type"] in {"OPERATION_RESULT", "TERMINAL_RECEIPT_RECORDED", "TASK_BLOCKED_UNKNOWN"}:
                operation_id = record["payload"].get("operation_id")
                if isinstance(operation_id, str):
                    resolved.add(operation_id)
        for record in reversed(self._events()):
            if record["event"]["event_type"] == "WORKER_DELTA_INTENT_RECORDED" and record["payload"].get("operation_id") not in resolved:
                return record["payload"]
        return None

    def _current_candidate_effect(self) -> dict[str, Any] | None:
        superseded = {record["payload"].get("operation_id") for record in self._events() if record["event"]["event_type"] == "OPERATION_SUPERSEDED"}
        for record in reversed(self._accepted_effects("PLAN_CANDIDATE_RECORDED")):
            if record["payload"].get("operation_id") not in superseded:
                return record
        return None

    def _current_plan(self) -> tuple[dict[str, Any], ArtifactRef] | None:
        candidate = self._current_candidate_effect()
        if candidate is None:
            return None
        ref = ArtifactRef.from_dict(candidate["payload"]["plan"])
        plan = loads_strict(self.store.verify(ref).read_bytes())
        require(isinstance(plan, dict), "TASK_PLAN_INVALID", "Plan artifact invalid")
        return plan, ref

    def _candidate_reviews(self, candidate: dict[str, Any]) -> list[dict[str, Any]]:
        sha = candidate["payload"]["plan"]["sha256"]
        operation_id = candidate["payload"]["operation_id"]
        return [
            record
            for record in self._accepted_effects("PLAN_REVIEW_RECORDED")
            if record["payload"].get("subject_sha256") == sha
            and record["payload"].get("candidate_operation_id") == operation_id
        ]

    def _consecutive_plan_passes(self, plan_sha: str) -> list[dict[str, Any]]:
        candidate = self._current_candidate_effect()
        if candidate is None or candidate["payload"]["plan"]["sha256"] != plan_sha:
            return []
        passes: list[dict[str, Any]] = []
        for record in self._candidate_reviews(candidate):
            payload = record["payload"]
            if payload.get("qualifying") is True and payload.get("disposition") == "PASS":
                passes.append(payload)
            else:
                passes = []
        return passes

    def _plan_review_body(self, candidate: dict[str, Any]) -> dict[str, Any]:
        inventory, inventory_ref = self._inventory()
        prior_reviews = self._candidate_reviews(candidate)
        evidence = [record["payload"]["bundle"] for record in self._accepted_effects("EVIDENCE_BUNDLE_EXTENDED") if record["payload"].get("purpose") == "plan_review"]
        return {
            "mission": self.task["mission"],
            "subject": candidate["payload"]["plan"],
            "candidate_plan": candidate["payload"]["plan"],
            "finding_map": candidate["payload"]["finding_map"],
            "baseline": inventory["baseline"],
            "inventory": inventory_ref.as_dict(),
            "toolchain": self._fact_ref("TOOLCHAIN_BOUND").as_dict(),
            "methodology": self._methodology_ref().as_dict(),
            "prior_findings": [record["payload"]["findings"] for record in prior_reviews],
            "evidence_bundles": evidence,
            "candidate_number": candidate["payload"]["candidate_number"],
            "candidate_operation_id": candidate["payload"]["operation_id"],
        }

    def _replacement_body(self, *, previous_plan: dict[str, Any] | None = None, findings: dict[str, Any] | None = None) -> dict[str, Any]:
        inventory, inventory_ref = self._inventory()
        body: dict[str, Any] = {
            "mission": self.task["mission"],
            "baseline": inventory["baseline"],
            "inventory": inventory_ref.as_dict(),
            "toolchain": self._fact_ref("TOOLCHAIN_BOUND").as_dict(),
            "methodology": self._methodology_ref().as_dict(),
            "baseline_id": self._baseline()["manifest_sha256"],
            "read_only_authority": self.task["read_only_authority"],
        }
        if previous_plan is not None:
            body["previous_plan"] = previous_plan
        if findings is not None:
            body["findings"] = findings
        return body

    def _evidence_continuation(self) -> bool:
        effects = self._accepted_effects("EVIDENCE_BUNDLE_EXTENDED")
        if not effects:
            return False
        latest = effects[-1]
        later_admission = any(
            record["event"]["event_type"] == "OPERATION_ADMITTED"
            and record["event"]["sequence"] > latest["event"]["sequence"]
            for record in self._events()
        )
        if later_admission:
            return False
        operation_id = latest["payload"]["operation_id"]
        admissions = [
            record["payload"]
            for record in self._events()
            if record["event"]["event_type"] == "OPERATION_ADMITTED"
            and record["payload"].get("operation_id") == operation_id
        ]
        require(len(admissions) == 1, "CONTROL_STATE_FAILED", "evidence operation admission is not unique")
        request_ref = ArtifactRef.from_dict(admissions[0]["request"])
        original = loads_strict(self.store.verify(request_ref).read_bytes())
        require(isinstance(original, dict), "CONTROL_STATE_FAILED", "evidence request is invalid")
        body = {
            key: value
            for key, value in original.items()
            if key not in {"schema_version", "operation_id", "attempt", "role", "purpose", "result_ref", "evidence_bundles"}
        }
        body["evidence_bundles"] = [
            record["payload"]["bundle"]
            for record in effects
            if record["payload"].get("role") == latest["payload"]["role"]
            and record["payload"].get("purpose") == latest["payload"]["purpose"]
        ]
        self._create_semantic_request(role=latest["payload"]["role"], purpose=latest["payload"]["purpose"], body=body)
        return True

    def _supersede_operation(self, operation_id: str, *, reason: str, replacement_purpose: str, replacement_body: dict[str, Any]) -> ArtifactRef:
        existing = [record for record in self._events() if record["event"]["event_type"] == "OPERATION_SUPERSEDED" and record["payload"].get("operation_id") == operation_id]
        if existing:
            return self._event_ref(existing[-1])
        return self._append_json_fact(
            "OPERATION_SUPERSEDED",
            "semantic/superseded",
            {
                "schema_version": 1,
                "operation_id": operation_id,
                "reason": reason,
                "replacement": {"role": "planner", "purpose": replacement_purpose, "body": replacement_body},
            },
        )

    def _admit_missing_replacement(self) -> bool:
        if self._pending_operation() is not None:
            return False
        superseded = [record for record in self._events() if record["event"]["event_type"] == "OPERATION_SUPERSEDED"]
        if not superseded:
            return False
        last = superseded[-1]
        later_admissions = [record for record in self._events() if record["event"]["event_type"] == "OPERATION_ADMITTED" and record["event"]["sequence"] > last["event"]["sequence"]]
        if later_admissions:
            return False
        replacement = last["payload"]["replacement"]
        self._create_semantic_request(role=replacement["role"], purpose=replacement["purpose"], body=replacement["body"])
        return True

    def _seal_plan(self, candidate: dict[str, Any], passes: list[dict[str, Any]]) -> ArtifactRef:
        plan_ref = ArtifactRef.from_dict(candidate["payload"]["plan"])
        inventory, inventory_ref = self._inventory()
        seal = {
            "schema_version": 1,
            "task": self._fact_ref("TASK_CREATED").as_dict(),
            "mission": self.task["mission"],
            "routing": {"ref": self.task["routing"]["resolver_ref"], "sha256": self.task["routing"]["resolver_sha256"], "size": (self.task_root / self.task["routing"]["resolver_ref"]).stat().st_size},
            "toolchain": self._fact_ref("TOOLCHAIN_BOUND").as_dict(),
            "methodology": self._methodology_ref().as_dict(),
            "inventory": inventory_ref.as_dict(),
            "baseline": inventory["baseline"],
            "plan": plan_ref.as_dict(),
            "qualifying_reviews": [payload["review_receipt"] for payload in passes[-3:]],
        }
        ref = self.store.publish_json(f"plans/seals/{uuid.uuid4().hex}.json", seal)
        self.ledger.append("PLAN_SEALED", ref.ref, ref.sha256)
        return ref

    def _workspace(self) -> Path:
        return Path(self.task["workspace"]["root"])

    def _workspace_identity(self) -> str:
        repo = self._workspace()
        observation = {
            "head": run_git(repo, ["rev-parse", "HEAD"]).stdout.decode().strip(),
            "branch": run_git(repo, ["branch", "--show-current"]).stdout.decode().strip(),
            "status": run_git(repo, ["status", "--short", "--branch", "--untracked-files=no"]).stdout.decode(errors="replace"),
        }
        return sha256_bytes(canonical_json_bytes(observation))

    def _active_task_binding(self) -> dict[str, Any] | None:
        accepted = {record["payload"].get("child_task_id") for record in self._events() if record["event"]["event_type"] == "TASK_RESULT_ACCEPTED"}
        active = [record["payload"] for record in self._events() if record["event"]["event_type"] == "TASK_BOUND" and record["payload"].get("child_task_id") not in accepted]
        require(len(active) <= 1, "CONTROL_STATE_FAILED", "multiple active child Tasks")
        return active[0] if active else None

    def _task_binding_for(self, step: dict[str, Any], plan_ref: ArtifactRef, plan: dict[str, Any]) -> dict[str, Any]:
        workspace_sha = self._workspace_identity()
        depth = int(self.task.get("depth", 0))
        require(depth < self.task["limits"]["max_task_depth"], "TASK_DEPTH_EXCEEDED", "Task depth limit exceeded")
        child_id = str(uuid.uuid5(uuid.NAMESPACE_URL, "skeptic-task\0" + "\0".join([self.task_id, plan_ref.sha256, step["id"], workspace_sha])))
        read_only = bool(self.task["read_only_authority"] or plan["delivery_kind"] == "inspect")
        return {
            "parent_task_id": self.task_id,
            "parent_plan_sha256": plan_ref.sha256,
            "parent_step_id": step["id"],
            "parent_workspace_sha256": workspace_sha,
            "depth": depth + 1,
            "child_task_id": child_id,
            "mission_sha256": sha256_bytes(step["mission"].encode("utf-8")),
            "read_only_authority": read_only,
        }

    def _bind_task(self, step: dict[str, Any], plan_ref: ArtifactRef, plan: dict[str, Any]) -> dict[str, Any]:
        existing = self._active_task_binding()
        if existing is not None:
            require(existing["parent_step_id"] == step["id"], "CONTROL_STATE_FAILED", "multiple active child Tasks")
            return existing
        binding = self._task_binding_for(step, plan_ref, plan)
        state_root = self.task_root.parent
        child_root = state_root / binding["child_task_id"]
        if child_root.exists():
            child = Runner(child_root, read_only=True)
            require(child.task_id == binding["child_task_id"] and child.task.get("parent_binding") == binding, "CONTROL_STATE_FAILED", "deterministic child identity has a mismatching binding")
        else:
            started = Runner.bootstrap(
                repo=self._workspace(),
                state_root=state_root,
                mission=step["mission"].encode("utf-8"),
                included_ignored=self.task["workspace"].get("included_ignored_paths", []),
                parent_binding=binding,
                task_id=binding["child_task_id"],
                read_only_authority=binding["read_only_authority"],
            )
            require(started["task_id"] == binding["child_task_id"], "CONTROL_STATE_FAILED", "child identity mismatch during creation")
        payload = {
            "schema_version": 1,
            "parent_step_id": step["id"],
            "child_task_id": binding["child_task_id"],
            "child_task_root": str(child_root),
            "parent_plan_sha256": binding["parent_plan_sha256"],
            "parent_workspace_sha256": binding["parent_workspace_sha256"],
            "mission_sha256": binding["mission_sha256"],
            "parent_binding": binding,
        }
        self._append_json_fact("TASK_BOUND", "tasks/bindings", payload)
        return payload

    def _accept_task_result(self, binding: dict[str, Any]) -> None:
        from .verifier import verify_task_terminal

        verified = verify_task_terminal(Path(binding["child_task_root"]), expected_parent_binding=binding["parent_binding"], expected_success_outcome=TASK_OUTCOME)
        accepted = {
            "schema_version": 1,
            "parent_step_id": binding["parent_step_id"],
            "child_task_id": binding["child_task_id"],
            "verified_terminal_receipt": verified["terminal_ref"].as_dict(),
            "result": verified["result"],
            "result_ref": verified["result_ref"].as_dict(),
            "frozen_evidence": verified["evidence_ref"].as_dict(),
        }
        self._append_json_fact("TASK_RESULT_ACCEPTED", "tasks/results", accepted)

    def _step_completion_records(self) -> dict[str, list[dict[str, Any]]]:
        completed: dict[str, list[dict[str, Any]]] = {}
        for record in self._accepted_effects("OPERATION_RESULT"):
            step_id = record["payload"].get("step_id")
            if isinstance(step_id, str):
                completed.setdefault(step_id, []).append(record)
        for record in self._events():
            event_type = record["event"]["event_type"]
            if event_type in {"VALIDATION_RECORDED", "INSPECTION_RECORDED"}:
                step_id = record["payload"].get("step_id")
            elif event_type == "TASK_RESULT_ACCEPTED":
                step_id = record["payload"].get("parent_step_id")
            else:
                continue
            if isinstance(step_id, str):
                completed.setdefault(step_id, []).append(record)
        return completed

    def _completed_steps(self) -> set[str]:
        records = self._step_completion_records()
        require(all(len(items) == 1 for items in records.values()), "DUPLICATE_STEP_COMPLETION", "a sealed Plan step completed more than once")
        return set(records)

    def _run_inspect_step(self, step: dict[str, Any]) -> None:
        source = self._workspace()
        scope = safe_relpath(step["scope"], allow_dot=True)
        if scope == ".":
            inspected = source
        else:
            overlap = scope_overlaps_nested(scope, self._nested_roots())
            require(overlap is None, "NESTED_REPOSITORY_SCOPE_FORBIDDEN", "inspection scope overlaps nested repository", scope=scope, nested_root=overlap)
            inspected = validate_workspace_target(source, scope, nested_roots=self._nested_roots())
        require(inspected.is_dir() and not inspected.is_symlink(), "INSPECTION_SCOPE_INVALID", "inspection scope must be a real directory")
        report: dict[str, Any] = {"schema_version": 1, "step_id": step["id"], "scope": scope, "operation": step["operation"], "baseline": self._baseline()["manifest_sha256"]}
        if step["operation"] == "git_state":
            require(scope == ".", "INSPECTION_SCOPE_INVALID", "git_state requires repository-root scope")
            report["git"] = {
                "head": run_git(source, ["rev-parse", "HEAD"]).stdout.decode().strip(),
                "branch": run_git(source, ["branch", "--show-current"]).stdout.decode().strip(),
                "status": run_git(source, ["status", "--short", "--branch", "--untracked-files=no"]).stdout.decode(errors="replace"),
            }
        else:
            require(step["operation"] == "repository_inventory", "PLAN_INSPECT_OPERATION", "unknown inspection operation")
            entries: list[dict[str, Any]] = []
            nested = set(self._nested_roots())
            for base, dirs, files in os.walk(inspected, topdown=True, followlinks=False):
                current = Path(base)
                kept: list[str] = []
                non_descending: list[str] = []
                for name in dirs:
                    child = current / name
                    rel_workspace = child.relative_to(source).as_posix()
                    if name in {".git", ".stt"} or rel_workspace in nested:
                        continue
                    if child.is_symlink():
                        non_descending.append(name)
                        continue
                    kept.append(name)
                dirs[:] = kept
                files[:] = [name for name in files if name not in {".git", ".stt"}]
                for name in non_descending + dirs + files:
                    path = current / name
                    rel_workspace = path.relative_to(source).as_posix()
                    safe_relpath(rel_workspace)
                    if any(root == rel_workspace or rel_workspace.startswith(root + "/") for root in nested):
                        continue
                    value = os.lstat(path)
                    kind = "directory" if stat.S_ISDIR(value.st_mode) else "file" if stat.S_ISREG(value.st_mode) else "symlink" if stat.S_ISLNK(value.st_mode) else "other"
                    entry = {"path": path.relative_to(inspected).as_posix(), "type": kind, "size": value.st_size}
                    if kind == "file":
                        require(value.st_size <= self.task["limits"]["max_single_file_bytes"], "SINGLE_FILE_LIMIT", "inventory file exceeds single-file limit")
                    entries.append(entry)
                    require(len(entries) <= self.task["limits"]["max_inventory_entries"], "INVENTORY_ENTRY_LIMIT", "repository inventory entry limit exceeded")
            report["entries"] = entries
        report_ref = self.store.publish_json(f"inspect/reports/{step['id']}/{uuid.uuid4().hex}.json", report)
        self._append_json_fact("INSPECTION_RECORDED", "inspect/receipts", {"schema_version": 1, "step_id": step["id"], "report": report_ref.as_dict()})

    def _run_validation_step(self, step: dict[str, Any]) -> None:
        refs: list[dict[str, Any]] = []
        for index, command in enumerate(step["commands"]):
            result, ref = self._run_bound_command(command, category=f"{step['id']}-{index:03d}")
            refs.append(ref.as_dict())
            if result.get("result_status") != "SUCCEEDED":
                reason = result.get("reason", result.get("result_status", "VALIDATION_FAILED"))
                if result.get("result_status") == "TERMINATION_UNKNOWN":
                    self._record_blocked_unknown(reason, [ref])
                else:
                    self._terminal("FAILED", reason, [ref])
                return
        self._append_json_fact("VALIDATION_RECORDED", "validation/step-receipts", {"schema_version": 1, "step_id": step["id"], "commands": refs})

    def _execute_next_step(self, plan: dict[str, Any], plan_ref: ArtifactRef) -> dict[str, Any] | None:
        completed = self._completed_steps()
        next_step = next((step for step in plan["steps"] if step["id"] not in completed), None)
        if next_step is None:
            return None
        if next_step["kind"] == "task":
            return self._bind_task(next_step, plan_ref, plan)
        if next_step["kind"] == "inspect":
            self._run_inspect_step(next_step)
            return {}
        if next_step["kind"] == "validation":
            self._run_validation_step(next_step)
            return {}
        require(not self.task["read_only_authority"] and plan["delivery_kind"] != "inspect", "INSPECT_AUTHORITY_VIOLATION", "read-only authority forbids Worker execution")
        capsule_root = self.task_root / "capsules" / next_step["id"] / uuid.uuid4().hex
        capsule_workspace = capsule_root / "workspace"
        manifest = prepare_capsule_admission(
            self._workspace(),
            next_step["read_scope"],
            next_step["write_scope"],
            nested_roots=self._nested_roots(),
            limits=self.task["limits"],
        )
        self.store.admit(manifest["capsule_bytes"] + manifest["capsule_entries"] * 4096 + 4096)
        materialize_capsule(self._workspace(), capsule_workspace, manifest, next_step["write_scope"])
        admission_ref = self.store.publish_json(
            f"capsules/{next_step['id']}/{capsule_root.name}/admission-{uuid.uuid4().hex}.json",
            {"schema_version": 1, "step": next_step, "manifest": manifest},
        )
        self._create_semantic_request(
            role="worker",
            purpose="change_step",
            body={"sealed_plan": plan_ref.as_dict(), "step": next_step, "capsule_path": str(capsule_workspace), "admission": admission_ref.as_dict()},
        )
        return {}

    def _workspace_path_identity(self, rel: str) -> dict[str, Any]:
        path = validate_workspace_target(self._workspace(), rel, allow_leaf_symlink_delete=True, nested_roots=self._nested_roots())
        return object_identity(path, rel, max_single_file_bytes=self.task["limits"]["max_single_file_bytes"])

    def _verified_accepted_child(self, accepted: dict[str, Any]) -> dict[str, Any]:
        from .verifier import verify_task_terminal

        bindings = [record["payload"] for record in self._events() if record["event"]["event_type"] == "TASK_BOUND" and record["payload"].get("child_task_id") == accepted.get("child_task_id") and record["payload"].get("parent_step_id") == accepted.get("parent_step_id")]
        require(len(bindings) == 1, "TASK_RESULT_INVALID", "accepted child has no unique Task binding")
        binding = bindings[0]
        verified = verify_task_terminal(Path(binding["child_task_root"]), expected_parent_binding=binding["parent_binding"], expected_success_outcome=TASK_OUTCOME)
        require(accepted.get("verified_terminal_receipt") == verified["terminal_ref"].as_dict(), "TASK_RESULT_INVALID", "accepted child terminal receipt changed")
        require(accepted.get("result_ref") == verified["result_ref"].as_dict() and accepted.get("result") == verified["result"], "TASK_RESULT_INVALID", "accepted child result changed")
        require(accepted.get("frozen_evidence") == verified["evidence_ref"].as_dict(), "TASK_RESULT_INVALID", "accepted child frozen evidence changed")
        return verified

    def _workspace_evidence(self) -> dict[str, Any]:
        paths: set[str] = set()
        operations: list[dict[str, Any]] = []
        validations: list[dict[str, Any]] = []
        for record in self._accepted_effects("OPERATION_RESULT"):
            payload = record["payload"]
            require(payload.get("kind") == "WORKER_DELTA_APPLIED" and isinstance(payload.get("delta"), list), "CONTROL_STATE_FAILED", "accepted Worker result malformed")
            for item in payload["delta"]:
                paths.add(safe_relpath(item["path"]))
            operations.append(self._event_ref(record).as_dict())
            validations.extend(payload.get("validations", []))
        accepted_children = [record["payload"] for record in self._events() if record["event"]["event_type"] == "TASK_RESULT_ACCEPTED"]
        for child_result in accepted_children:
            verified = self._verified_accepted_child(child_result)
            for entry in verified["evidence"]["declared_changed_paths"]:
                paths.add(safe_relpath(entry["path"]))
        return {
            "schema_version": 1,
            "declared_changed_paths": [self._workspace_path_identity(rel) for rel in sorted(paths)],
            "operation_refs": operations,
            "validation_refs": validations,
            "accepted_task_results": [self._event_ref(record).as_dict() for record in self._events() if record["event"]["event_type"] == "TASK_RESULT_ACCEPTED"],
        }

    def _verify_frozen_workspace(self, evidence: dict[str, Any]) -> None:
        for entry in evidence.get("declared_changed_paths", []):
            require(isinstance(entry, dict) and isinstance(entry.get("path"), str), "TASK_FINAL_INVALID", "frozen changed-path entry malformed")
            actual = self._workspace_path_identity(safe_relpath(entry["path"]))
            require(actual == entry, "FINAL_WORKSPACE_CHANGED", "frozen workspace path identity changed", path=entry["path"])

    def _freeze_final(self, plan: dict[str, Any], plan_ref: ArtifactRef) -> None:
        attempt = uuid.uuid4().hex
        smoke_ref: ArtifactRef | None = None
        if self.task.get("qualification", {}).get("final_entrypoint_smoke_required") is True:
            smoke_script = self._workspace() / "scripts/generic_host_smoke.py"
            require(smoke_script.is_file(), "FINAL_ENTRYPOINT_SMOKE_UNAVAILABLE", "generic-host smoke missing")
            smoke_command = {"tool_id": "python", "args": ["scripts/generic_host_smoke.py"], "cwd": ".", "timeout_seconds": min(900, self.task["limits"]["max_semantic_operation_seconds"]), "accepted_exit_codes": [0]}
            smoke, smoke_ref = self._run_bound_command(smoke_command, category=f"final-smoke-{attempt}")
            if smoke.get("result_status") != "SUCCEEDED":
                self._terminal("FAILED", "FINAL_ENTRYPOINT_SMOKE_FAILED", [smoke_ref])
                return
        evidence_ref = self.store.publish_json(f"final/attempts/{attempt}/evidence.json", self._workspace_evidence())
        inspection_refs = [self._event_ref(record).as_dict() for record in self._events() if record["event"]["event_type"] == "INSPECTION_RECORDED"]
        task_result_refs = [self._event_ref(record).as_dict() for record in self._events() if record["event"]["event_type"] == "TASK_RESULT_ACCEPTED"]
        result_artifacts = [evidence_ref.as_dict()]
        if plan["delivery_kind"] == "inspect":
            report_ref = self.store.publish_json(
                f"final/attempts/{attempt}/inspection-report.json",
                {"schema_version": 1, "baseline": self._baseline()["manifest_sha256"], "inspections": inspection_refs, "accepted_task_results": task_result_refs},
            )
            result_artifacts.append(report_ref.as_dict())
        result_ref = self.store.publish_json(f"final/attempts/{attempt}/task-result.json", {"schema_version": 1, "artifacts": result_artifacts})
        completion_records = self._step_completion_records()
        done_proof = [
            {"step_id": step["id"], "completion": self._event_ref(completion_records[step["id"]][0]).as_dict()}
            for step in plan["steps"]
        ]
        subject = {
            "schema_version": 1,
            "mission": self.task["mission"],
            "sealed_plan": plan_ref.as_dict(),
            "plan_seal": self._fact_ref("PLAN_SEALED").as_dict(),
            "evidence": evidence_ref.as_dict(),
            "result": result_ref.as_dict(),
            "accepted_task_results": task_result_refs,
            "inspection_results": inspection_refs,
            "done_proof": done_proof,
        }
        subject_ref = self.store.publish_json(f"final/attempts/{attempt}/frozen-subject.json", subject)
        freeze_ref = self.store.publish_json(
            f"final/attempts/{attempt}/freeze-receipt.json",
            {
                "schema_version": 1,
                "subject": subject_ref.as_dict(),
                "subject_sha256": subject_ref.sha256,
                "mission": self.task["mission"],
                "sealed_plan": plan_ref.as_dict(),
                "plan_seal": self._fact_ref("PLAN_SEALED").as_dict(),
                "evidence": evidence_ref.as_dict(),
                "result": result_ref.as_dict(),
                "accepted_task_results": task_result_refs,
                "inspection_results": inspection_refs,
                "done_proof": done_proof,
                "smoke": smoke_ref.as_dict() if smoke_ref else None,
            },
        )
        self.ledger.append("FINAL_SUBJECT_FROZEN", freeze_ref.ref, freeze_ref.sha256)

    def _consecutive_final_passes(self, subject_sha: str) -> list[dict[str, Any]]:
        current = self._current_plan()
        require(current is not None, "TASK_PLAN_INVALID", "final review requires a sealed Plan")
        required_claims = {
            clause["claim_id"]
            for clause in current[0]["done"]
            if clause["kind"] == "reviewer_claim"
        }
        passes: list[dict[str, Any]] = []
        for record in self._accepted_effects("FINAL_REVIEW_RECORDED"):
            payload = record["payload"]
            claims = set(payload.get("claims") or [])
            if payload.get("subject_sha256") == subject_sha and payload.get("qualifying") is True and required_claims <= claims:
                passes.append(payload)
            else:
                passes = []
        return passes

    def _final_review_body(self, frozen: dict[str, Any]) -> dict[str, Any]:
        current = self._current_plan()
        require(current is not None, "TASK_PLAN_INVALID", "final review requires a sealed Plan")
        required_claims = sorted(
            clause["claim_id"]
            for clause in current[0]["done"]
            if clause["kind"] == "reviewer_claim"
        )
        return {
            "subject": frozen["subject"],
            "methodology": self._methodology_ref().as_dict(),
            "required_claims": required_claims,
            "evidence_bundles": [record["payload"]["bundle"] for record in self._accepted_effects("EVIDENCE_BUNDLE_EXTENDED") if record["payload"].get("purpose") == "final_review"],
        }

    def _advance(self) -> dict[str, Any] | None:
        """Derive and perform exactly one deterministic lifecycle advancement."""
        if self._pending_operation() is not None or self._is_stopped() or self._last_event_payload("TERMINAL_RECEIPT_RECORDED") or self._last_event_payload("TASK_BLOCKED_UNKNOWN"):
            return None
        if self._admit_missing_replacement():
            return {}
        if self._evidence_continuation():
            return {}
        seal = self._last_event_payload("PLAN_SEALED")
        if seal is None:
            candidate = self._current_candidate_effect()
            require(candidate is not None, "CONTROL_STATE_FAILED", "no active Plan candidate or Planner operation")
            reviews = self._candidate_reviews(candidate)
            if reviews:
                latest = reviews[-1]["payload"]
                if latest["disposition"] == "CONFLICT":
                    self._terminal("FAILED", "PLAN_CONFLICT", [ArtifactRef.from_dict(latest["review_receipt"]), ArtifactRef.from_dict(latest["findings"])])
                    return {}
                if latest["disposition"] == "ACTION":
                    replacement = self._replacement_body(previous_plan=candidate["payload"]["plan"], findings=latest["findings"])
                    self._supersede_operation(candidate["payload"]["operation_id"], reason="PLAN_REVIEW_ACTION", replacement_purpose="plan_repair", replacement_body=replacement)
                    return {}
            passes = self._consecutive_plan_passes(candidate["payload"]["plan"]["sha256"])
            if len(passes) >= 3:
                self._seal_plan(candidate, passes[-3:])
                return {}
            require(len(reviews) < self.task["limits"]["max_plan_reviews"], "REVIEW_BUDGET_EXHAUSTED", "Plan review budget exhausted")
            self._create_semantic_request(role="reviewer", purpose="plan_review", body=self._plan_review_body(candidate))
            return {}
        current = self._current_plan()
        require(current is not None, "CONTROL_STATE_FAILED", "sealed Plan unavailable")
        plan, plan_ref = current
        frozen = self._last_event_payload("FINAL_SUBJECT_FROZEN")
        if frozen is None:
            completed = self._completed_steps()
            next_step = next((step for step in plan["steps"] if step["id"] not in completed), None)
            if next_step is not None:
                return self._execute_next_step(plan, plan_ref)
            self._freeze_final(plan, plan_ref)
            return {}
        final_reviews = [record for record in self._accepted_effects("FINAL_REVIEW_RECORDED") if record["payload"].get("subject_sha256") == frozen["subject_sha256"]]
        if final_reviews and final_reviews[-1]["payload"]["disposition"] != "PASS":
            latest = final_reviews[-1]["payload"]
            self._terminal("FAILED", "FINAL_REVIEW_NOT_CLEAN", [ArtifactRef.from_dict(latest["review_receipt"]), ArtifactRef.from_dict(latest["findings"])])
            return {}
        passes = self._consecutive_final_passes(frozen["subject_sha256"])
        if len(passes) < 3:
            require(len(final_reviews) < self.task["limits"]["max_final_find_reviews"], "REVIEW_BUDGET_EXHAUSTED", "final review budget exhausted")
            self._create_semantic_request(role="reviewer", purpose="final_review", body=self._final_review_body(frozen))
            return {}
        evidence_ref = ArtifactRef.from_dict(frozen["evidence"])
        evidence = loads_strict(self.store.verify(evidence_ref).read_bytes())
        try:
            self._verify_frozen_workspace(evidence)
            from .verifier import verify_task_ready_for_complete

            verify_task_ready_for_complete(self)
        except STTError as exc:
            self._terminal("FAILED", exc.code, [evidence_ref])
            return {}
        self._terminal(TASK_OUTCOME, "TASK_FINAL_REVIEWS_COMPLETE", [])
        return {}

    def _record_blocked_unknown(self, reason: str, refs: list[ArtifactRef], operation_id: str | None = None) -> ArtifactRef:
        existing = self._last_event_payload("TASK_BLOCKED_UNKNOWN")
        if existing:
            return ArtifactRef.from_dict(existing["receipt"])
        receipt = self.store.publish_json(
            f"blocked/receipts/{uuid.uuid4().hex}.json",
            {"schema_version": 1, "status": "BLOCKED_UNKNOWN", "reason": reason, "evidence": [ref.as_dict() for ref in refs], "resumable": False, "next_action": "DIAGNOSE"},
        )
        marker_value: dict[str, Any] = {"schema_version": 1, "reason": reason, "receipt": receipt.as_dict(), "resumable": False}
        if operation_id is not None:
            marker_value["operation_id"] = operation_id
        marker = self.store.publish_json(f"blocked/events/{uuid.uuid4().hex}.json", marker_value)
        self.ledger.append("TASK_BLOCKED_UNKNOWN", marker.ref, marker.sha256)
        return receipt

    def _terminal(self, outcome: str, reason: str, refs: list[ArtifactRef], operation_id: str | None = None) -> ArtifactRef:
        existing = self._last_event_payload("TERMINAL_RECEIPT_RECORDED")
        if existing:
            return ArtifactRef.from_dict(existing["receipt"])
        frozen = self._last_event_payload("FINAL_SUBJECT_FROZEN")
        result = frozen.get("result") if outcome == TASK_OUTCOME and frozen else None
        receipt = self.store.publish_json(
            f"terminal/receipts/{uuid.uuid4().hex}.json",
            {"schema_version": 1, "outcome": outcome, "reason": reason, "result": result, "evidence": [ref.as_dict() for ref in refs], "workspace_model": "direct_shared_workspace", "rollback": "unsupported"},
        )
        marker_value: dict[str, Any] = {"schema_version": 1, "receipt": receipt.as_dict(), "outcome": outcome}
        if operation_id is not None:
            marker_value["operation_id"] = operation_id
        marker = self.store.publish_json(f"terminal/events/{uuid.uuid4().hex}.json", marker_value)
        self.ledger.append("TERMINAL_RECEIPT_RECORDED", marker.ref, marker.sha256)
        return receipt

    def _is_stopped(self) -> bool:
        stopped = False
        for record in self._events():
            if record["event"]["event_type"] == "TASK_STOPPED":
                stopped = True
            elif record["event"]["event_type"] == "TASK_RESUMED":
                stopped = False
        return stopped

    def receipt(self, status: str, next_action: str | None, refs: list[ArtifactRef], reason: str | None = None) -> dict[str, Any]:
        events = self.ledger.read(recover_partial=not self.read_only)
        head = events[-1].event_sha256 if events else "0" * 64
        return compact_receipt(task_id=self.task_id, task_root=self.task_root, status=status, next_action=next_action, ledger_head=head, refs=[ref.as_dict() for ref in refs], reason=reason)

    def _status_unlocked(self) -> dict[str, Any]:
        terminal = self._last_event_payload("TERMINAL_RECEIPT_RECORDED")
        if terminal:
            return self.receipt(terminal["outcome"], None, [ArtifactRef.from_dict(terminal["receipt"])])
        blocked = self._last_event_payload("TASK_BLOCKED_UNKNOWN")
        if blocked:
            result = self.receipt("BLOCKED_UNKNOWN", "DIAGNOSE", [ArtifactRef.from_dict(blocked["receipt"])], blocked["reason"])
            result["resumable"] = False
            return result
        if self._is_stopped():
            return self.receipt("STOPPED", "RESUME", [])
        active_child = self._active_task_binding()
        if active_child is not None:
            child = Runner(Path(active_child["child_task_root"]), read_only=True)
            child_status = child.status()
            if child_status["status"] == "STOPPED":
                return self.receipt("STOPPED", "RESUME_CHILD_TASK", [], "deepest active child Task is stopped")
            if child_status["status"] == TASK_OUTCOME:
                return self.receipt("RUNNING", "ACCEPT_TASK_RESULT", [])
            if child_status["status"] in {"FAILED", "BLOCKED_UNKNOWN"}:
                return self.receipt("RUNNING", "RUN_PARENT", [], f"active child Task is {child_status['status']} and must be consumed by the parent")
            return self.receipt("RUNNING", "RUN_CHILD_TASK", [])
        pending = self._pending_operation()
        if pending:
            request, request_ref = pending
            effects = self._effect_records(request["operation_id"])
            if effects:
                return self.receipt("RUNNING", "FINALIZE_OPERATION", [request_ref])
            if self._operation_unknown_unresolved(request["operation_id"]):
                return self.receipt("OPERATION_UNKNOWN", "RECONCILE_OPERATION", [request_ref], "semantic operation status remains inconclusive; no redispatch performed")
            rejected = any(record["event"]["event_type"] == "OPERATION_RESULT_REJECTED" and record["payload"].get("operation_id") == request["operation_id"] for record in self._events())
            if rejected:
                return self.receipt("RETRYABLE", "RETRY_OPERATION", [request_ref], "operation result rejected; same admission remains pending")
            if (self.task_root / request["result_ref"]).is_file():
                return self.receipt("RUNNING", "FINALIZE_OPERATION", [request_ref])
            return self.receipt("RUNNING", {"planner": "DISPATCH_PLANNER", "reviewer": "DISPATCH_REVIEWER", "worker": "DISPATCH_WORKER"}[request["role"]], [request_ref])
        if self._last_event_payload("FINAL_SUBJECT_FROZEN"):
            frozen = self._last_event_payload("FINAL_SUBJECT_FROZEN")
            return self.receipt("RUNNING", "VERIFY_AND_COMPLETE" if len(self._consecutive_final_passes(frozen["subject_sha256"])) >= 3 else "DISPATCH_FINAL_REVIEW", [])
        if self._last_event_payload("PLAN_SEALED"):
            return self.receipt("RUNNING", "EXECUTE_OR_VALIDATE_NEXT_STEP", [])
        if self._current_candidate_effect():
            return self.receipt("RUNNING", "DISPATCH_PLAN_REVIEW", [])
        return self.receipt("RUNNING", "ADVANCE", [])

    def status(self) -> dict[str, Any]:
        return self._status_unlocked()

    def run(self) -> dict[str, Any]:
        for _ in range(128):
            child_binding: dict[str, Any] | None = None
            with self._task_lease():
                if self._last_event_payload("TERMINAL_RECEIPT_RECORDED") or self._last_event_payload("TASK_BLOCKED_UNKNOWN") or self._is_stopped():
                    return self._status_unlocked()
                unresolved = self._unresolved_worker_intent()
                if unresolved is not None:
                    failure = self._worker_failure_evidence(intent=unresolved, application_state="partial_or_unknown", validations=[], reason="PROCESS_INTERRUPTED_AFTER_WORKER_DELTA_INTENT")
                    self._record_blocked_unknown("WORKER_DELTA_PARTIAL_OR_UNKNOWN", [failure], operation_id=unresolved["operation_id"])
                    return self._status_unlocked()
                pending = self._pending_operation()
                if pending:
                    request, request_ref = pending
                    effects = self._effect_records(request["operation_id"])
                    require(len(effects) <= 1, "DUPLICATE_ROLE_EFFECT", "semantic operation has multiple role effects")
                    if effects:
                        self._accept_effect(request, request_ref, effects[0])
                        continue
                    try:
                        adopted = self._adopt_result(request)
                        if adopted is None:
                            return self._status_unlocked()
                        result, result_ref, provider_report, evidence_ref = adopted
                        if request["role"] == "planner":
                            self._process_planner_result(request, result, result_ref, evidence_ref)
                        elif request["role"] == "reviewer":
                            self._process_reviewer_result(request, result, result_ref, provider_report, evidence_ref)
                        else:
                            self._process_worker_result(request, result, result_ref, evidence_ref)
                    except STTError as exc:
                        if exc.code == "OPERATION_STATUS_UNKNOWN":
                            return self._status_unlocked()
                        if self._last_event_payload("TERMINAL_RECEIPT_RECORDED") or self._last_event_payload("TASK_BLOCKED_UNKNOWN"):
                            return self._status_unlocked()
                        rejection = self._reject_operation(request, exc)
                        return self.receipt("REJECTED", "RETRY_OPERATION", [request_ref, rejection], exc.message)
                    except (KeyError, TypeError, AttributeError, ValueError, OSError, RecursionError, UnicodeError, OverflowError) as exc:
                        bounded = STTError("SEMANTIC_RESULT_MISSING_OR_INVALID", f"malformed semantic output: {type(exc).__name__}")
                        rejection = self._reject_operation(request, bounded)
                        return self.receipt("REJECTED", "RETRY_OPERATION", [request_ref, rejection], bounded.message)
                    if self._last_event_payload("TERMINAL_RECEIPT_RECORDED") or self._last_event_payload("TASK_BLOCKED_UNKNOWN"):
                        return self._status_unlocked()
                    effects = self._effect_records(request["operation_id"])
                    require(len(effects) == 1, "ROLE_EFFECT_MISSING", "successful semantic processing did not record exactly one role effect")
                    self._accept_effect(request, request_ref, effects[0])
                    continue
                advanced = self._advance()
                if advanced is None:
                    return self._status_unlocked()
                if advanced.get("child_task_root"):
                    child_binding = advanced
                else:
                    continue
            if child_binding is not None:
                child = Runner(Path(child_binding["child_task_root"]))
                child_status = child.status()
                if child_status["status"] not in {"COMPLETE", "FAILED", "BLOCKED_UNKNOWN", "STOPPED"}:
                    child.run()
                child_status = child.status()
                with self._task_lease():
                    if child_status["status"] in {"RUNNING", "REJECTED", "RETRYABLE", "OPERATION_UNKNOWN"}:
                        return self.receipt("RUNNING", "RUN_CHILD_TASK", [])
                    if child_status["status"] == "STOPPED":
                        return self.receipt("STOPPED", "RESUME_CHILD_TASK", [])
                    if child_status["status"] != TASK_OUTCOME:
                        if child_status["status"] == "BLOCKED_UNKNOWN":
                            self._record_blocked_unknown("CHILD_TASK_BLOCKED_UNKNOWN", [])
                        else:
                            self._terminal("FAILED", "CHILD_TASK_" + child_status["status"], [])
                        return self._status_unlocked()
                    self._accept_task_result(child_binding)
                continue
        return self.receipt("RUNNING", "FOREGROUND_CYCLE_BOUND_REACHED", [])

    def reconcile(self) -> dict[str, Any]:
        with self._task_lease():
            if self._is_stopped():
                return self._status_unlocked()
            pending = self._pending_operation()
            if not pending:
                return self._status_unlocked()
            request, request_ref = pending
            require(self._operation_unknown_unresolved(request["operation_id"]), "CONTROL_STATE_FAILED", "reconcile requires an unresolved OPERATION_UNKNOWN observation")
            if not (self.task_root / request["_provider_evidence_ref"]).is_file():
                return self.receipt("OPERATION_UNKNOWN", "RECONCILE_OPERATION", [request_ref], "host adapter must provide conclusive operation evidence; no redispatch performed")
        return self.run()

    def restore(self, destination: Path) -> dict[str, Any]:
        raise STTError("UNSUPPORTED", "STT does not provide rollback or restoration; inspect ledger and artifacts for manual recovery")

    def retry(self) -> dict[str, Any]:
        with self._task_lease():
            require(not self._last_event_payload("TERMINAL_RECEIPT_RECORDED") and not self._last_event_payload("TASK_BLOCKED_UNKNOWN"), "CONTROL_STATE_FAILED", "terminal or nonresumable blocked Tasks cannot retry")
            if self._is_stopped():
                return self._status_unlocked()
            pending = self._pending_operation()
            if not pending:
                return self._status_unlocked()
            request, ref = pending
            if self._operation_unknown_unresolved(request["operation_id"]):
                return self.receipt("OPERATION_UNKNOWN", "RECONCILE_OPERATION", [ref], "unknown operations cannot be redispatched")
            return self.receipt("RETRYABLE", {"planner": "DISPATCH_PLANNER", "reviewer": "DISPATCH_REVIEWER", "worker": "DISPATCH_WORKER"}[request["role"]], [ref], "same admitted operation and attempt remain pending")

    def replan(self) -> dict[str, Any]:
        with self._task_lease():
            require(not self._is_stopped(), "CONTROL_STATE_FAILED", "stopped Task must be resumed before replanning")
            pending = self._pending_operation()
            require(pending is not None and pending[0]["role"] == "planner", "CONTROL_STATE_FAILED", "replan requires a pending Planner operation")
            request, ref = pending
            rejected = any(record["event"]["event_type"] == "OPERATION_RESULT_REJECTED" and record["payload"].get("operation_id") == request["operation_id"] for record in self._events())
            require(rejected, "CONTROL_STATE_FAILED", "replan requires an explicitly rejected pending Planner operation")
            replacement = self._replacement_body()
            superseded = self._supersede_operation(request["operation_id"], reason="OWNER_REPLAN", replacement_purpose="replan", replacement_body=replacement)
            self._create_semantic_request(role="planner", purpose="replan", body=replacement)
            return self.receipt("REPLANNED", "DISPATCH_PLANNER", [ref, superseded])

    def stop(self) -> dict[str, Any]:
        with self._task_lease():
            if self._last_event_payload("TERMINAL_RECEIPT_RECORDED") or self._last_event_payload("TASK_BLOCKED_UNKNOWN"):
                return self._status_unlocked()
            if not self._is_stopped():
                self._append_json_fact("TASK_STOPPED", "control/stops", {"schema_version": 1, "reason": "OWNER_STOP_REQUESTED"})
            return self.receipt("STOPPED", "RESUME", [])

    def _active_chain(self) -> list["Runner"]:
        chain = [self]
        current = self
        while binding := current._active_task_binding():
            current = Runner(Path(binding["child_task_root"]))
            chain.append(current)
        return chain

    def resume(self) -> dict[str, Any]:
        require(not self._last_event_payload("TERMINAL_RECEIPT_RECORDED") and not self._last_event_payload("TASK_BLOCKED_UNKNOWN"), "CONTROL_STATE_FAILED", "terminal and nonresumable blocked Tasks cannot be resumed")
        chain = self._active_chain()
        target = next((runner for runner in reversed(chain) if runner._is_stopped()), None)
        require(target is not None, "CONTROL_STATE_FAILED", "resume requires an unmatched TASK_STOPPED")
        with target._task_lease():
            target._append_json_fact("TASK_RESUMED", "control/resumes", {"schema_version": 1, "reason": "OWNER_RESUME_REQUESTED"})
        return self.receipt("RESUMABLE", "RUN", [], "resume recorded; no workspace work was performed")

    def diagnose(self) -> dict[str, Any]:
        state = self._status_unlocked()
        state["diagnosis"] = {"ledger_head": state.get("ledger_head"), "next_action": state.get("next_action"), "authoritative": "ledger.jsonl"}
        return state
