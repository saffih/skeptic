"""The single fail-closed verifier for complete STT Tasks."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifacts import ArtifactRef
from .canonical import loads_strict
from .errors import require
from .plan import validate_plan


def _artifact(runner: Any, value: Any, code: str) -> tuple[ArtifactRef, Any]:
    ref = ArtifactRef.from_dict(value)
    path = runner.store.verify(ref)
    parsed = loads_strict(path.read_bytes())
    require(isinstance(parsed, dict), code, "referenced artifact must be a JSON object")
    return ref, parsed


def _request_for_operation(runner: Any, operation_id: str) -> tuple[ArtifactRef, dict[str, Any]]:
    matches = [
        record
        for record in runner._events()
        if record["event"]["event_type"] == "OPERATION_ADMITTED"
        and record["payload"].get("operation_id") == operation_id
    ]
    require(len(matches) == 1, "OPERATION_BINDING_INVALID", "operation must have one admission")
    admission = matches[0]["payload"]
    request_ref, request = _artifact(runner, admission.get("request"), "OPERATION_BINDING_INVALID")
    require(request.get("operation_id") == operation_id, "OPERATION_BINDING_INVALID", "request operation identity mismatch")
    return request_ref, request


def _verify_parent_binding(runner: Any, expected: dict[str, Any] | None) -> None:
    task = runner.task
    binding = task.get("parent_binding")
    mission_ref = ArtifactRef.from_dict(task.get("mission"))
    runner.store.verify(mission_ref)
    duplicate_fields = {
        "parent_task_id": task.get("parent_task_id"),
        "parent_plan_sha256": task.get("parent_plan_sha256"),
        "parent_step_id": task.get("parent_step_id"),
        "parent_workspace_sha256": task.get("parent_workspace_sha256"),
        "depth": task.get("depth"),
    }
    if expected is None:
        require(binding is None, "TASK_BINDING_MISMATCH", "root Task unexpectedly has a parent binding")
        require(
            duplicate_fields == {
                "parent_task_id": None,
                "parent_plan_sha256": None,
                "parent_step_id": None,
                "parent_workspace_sha256": None,
                "depth": 0,
            },
            "TASK_BINDING_MISMATCH",
            "root Task has inconsistent duplicated parent fields",
        )
        return
    require(binding == expected, "TASK_BINDING_MISMATCH", "Task parent binding mismatch")
    require(
        set(binding)
        == {
            "parent_task_id",
            "parent_plan_sha256",
            "parent_step_id",
            "parent_workspace_sha256",
            "depth",
            "child_task_id",
            "mission_sha256",
            "read_only_authority",
        },
        "TASK_BINDING_MISMATCH",
        "canonical parent binding schema mismatch",
    )
    require(task.get("task_id") == binding["child_task_id"], "TASK_ID_MISMATCH", "Task identity does not match parent binding")
    require(
        duplicate_fields
        == {
            "parent_task_id": binding["parent_task_id"],
            "parent_plan_sha256": binding["parent_plan_sha256"],
            "parent_step_id": binding["parent_step_id"],
            "parent_workspace_sha256": binding["parent_workspace_sha256"],
            "depth": binding["depth"],
        },
        "TASK_BINDING_MISMATCH",
        "duplicated task parent fields differ from canonical binding",
    )
    require(mission_ref.sha256 == binding["mission_sha256"], "TASK_BINDING_MISMATCH", "child mission hash differs from parent binding")
    require(task.get("read_only_authority") is binding["read_only_authority"], "TASK_BINDING_MISMATCH", "child authority differs from parent binding")


def _verify_role_effects(runner: Any) -> None:
    events = runner._events()
    for record in events:
        if record["event"]["event_type"] != "TASK_RESULT_ACCEPTED":
            runner._verify_refs_recursive(record["payload"])
    accepted = runner._accepted_effects()
    accepted_by_operation: dict[str, list[dict[str, Any]]] = {}
    for effect in accepted:
        operation_id = effect["payload"].get("operation_id")
        require(isinstance(operation_id, str), "ROLE_EFFECT_INVALID", "accepted role effect has no operation identity")
        accepted_by_operation.setdefault(operation_id, []).append(effect)
        request_ref, _ = _request_for_operation(runner, operation_id)
        runner._verify_effect(effect, request_ref)
    require(all(len(items) == 1 for items in accepted_by_operation.values()), "DUPLICATE_ROLE_EFFECT", "operation has multiple accepted role effects")

    consumed = runner._consumed_operation_ids()
    for record in events:
        event_type = record["event"]["event_type"]
        operation_id = record["payload"].get("operation_id")
        if event_type in {"OPERATION_UNKNOWN", "OPERATION_RESULT_REJECTED"}:
            require(operation_id in consumed, "UNRESOLVED_OPERATION", "unknown or rejected operation remains unresolved")
    require(runner._pending_operation() is None, "PENDING_OPERATION", "complete Task still has a pending semantic operation")


def _verify_plan(runner: Any) -> tuple[dict[str, Any], ArtifactRef, ArtifactRef]:
    seals = [record for record in runner._events() if record["event"]["event_type"] == "PLAN_SEALED"]
    require(len(seals) == 1, "TASK_PLAN_INVALID", "complete Task must have exactly one Plan seal")
    seal_ref = runner._event_ref(seals[0])
    seal = seals[0]["payload"]
    runner._verify_refs_recursive(seal)
    require(
        set(seal)
        == {"schema_version", "task", "mission", "routing", "toolchain", "methodology", "inventory", "baseline", "plan", "qualifying_reviews"}
        and seal.get("schema_version") == 1,
        "TASK_PLAN_INVALID",
        "Plan seal schema invalid",
    )
    plan_ref, plan = _artifact(runner, seal["plan"], "TASK_PLAN_INVALID")
    catalog, _ = runner._catalog()
    validate_plan(
        plan,
        mission_sha256=runner.task["mission"]["sha256"],
        baseline_id=runner._baseline()["manifest_sha256"],
        catalog_ids={tool["tool_id"] for tool in catalog["tools"]},
        source_paths=[runner.task["workspace"]["root"], runner.task["workspace"]["git_common_dir"], str(runner.task_root)],
        limits=runner.task["limits"],
        nested_roots=runner._nested_roots(),
        read_only_authority=runner.task["read_only_authority"],
    )
    require(seal["mission"] == runner.task["mission"], "TASK_PLAN_INVALID", "Plan seal mission mismatch")
    inventory, inventory_ref = runner._inventory()
    routing_path = runner.task_root / runner.task["routing"]["resolver_ref"]
    routing_ref = {
        "ref": runner.task["routing"]["resolver_ref"],
        "sha256": runner.task["routing"]["resolver_sha256"],
        "size": routing_path.stat().st_size,
    }
    require(seal["task"] == runner._fact_ref("TASK_CREATED").as_dict(), "TASK_PLAN_INVALID", "Plan seal Task binding mismatch")
    require(seal["routing"] == routing_ref, "TASK_PLAN_INVALID", "Plan seal routing binding mismatch")
    require(seal["toolchain"] == runner._fact_ref("TOOLCHAIN_BOUND").as_dict(), "TASK_PLAN_INVALID", "Plan seal toolchain mismatch")
    require(seal["methodology"] == runner._methodology_ref().as_dict(), "TASK_PLAN_INVALID", "Plan seal methodology mismatch")
    require(seal["inventory"] == inventory_ref.as_dict(), "TASK_PLAN_INVALID", "Plan seal inventory mismatch")
    require(seal["baseline"] == inventory["baseline"], "TASK_PLAN_INVALID", "Plan seal baseline mismatch")
    current = runner._current_plan()
    require(current is not None and current[1] == plan_ref and current[0] == plan, "TASK_PLAN_INVALID", "sealed Plan differs from active accepted candidate")
    passes = runner._consecutive_plan_passes(plan_ref.sha256)
    require(len(passes) >= 3, "TASK_PLAN_REVIEWS_INVALID", "complete Task lacks three unchanged Plan reviews")
    require(seal["qualifying_reviews"] == [item["review_receipt"] for item in passes[-3:]], "TASK_PLAN_REVIEWS_INVALID", "Plan seal is not bound to the final three unchanged reviews")

    candidate = runner._current_candidate_effect()
    require(candidate is not None, "TASK_PLAN_INVALID", "accepted Plan candidate missing")
    for review in runner._candidate_reviews(candidate):
        payload = review["payload"]
        _, request = _request_for_operation(runner, payload["operation_id"])
        required_context = {"mission", "candidate_plan", "finding_map", "baseline", "inventory", "toolchain", "methodology", "prior_findings", "evidence_bundles", "candidate_operation_id"}
        require(required_context <= set(request), "TASK_PLAN_REVIEWS_INVALID", "Plan reviewer request lacks immutable mission or planning context")
        require(request["mission"] == runner.task["mission"] and request["candidate_plan"] == plan_ref.as_dict(), "TASK_PLAN_REVIEWS_INVALID", "Plan reviewer reviewed different mission or Plan")
        require(request["finding_map"] == candidate["payload"]["finding_map"], "TASK_PLAN_REVIEWS_INVALID", "Plan reviewer finding map mismatch")
        require(request["candidate_operation_id"] == candidate["payload"]["operation_id"] == payload.get("candidate_operation_id"), "TASK_PLAN_REVIEWS_INVALID", "Plan reviewer candidate operation mismatch")
    return plan, plan_ref, seal_ref


def _verify_steps_and_worker_refs(runner: Any, plan: dict[str, Any]) -> None:
    completions = runner._step_completion_records()
    step_ids = [step["id"] for step in plan["steps"]]
    require(set(completions) == set(step_ids), "TASK_STEPS_INCOMPLETE", "sealed Plan completion set is not exact")
    require(all(len(completions[step_id]) == 1 for step_id in step_ids), "DUPLICATE_STEP_COMPLETION", "sealed Plan step did not complete exactly once")
    require(runner._unresolved_worker_intent() is None, "UNRESOLVED_WORKER_INTENT", "complete Task has an unresolved Worker mutation intent")
    require(runner._active_task_binding() is None, "ACTIVE_CHILD_TASK", "complete Task has an active child")

    intents: dict[str, list[dict[str, Any]]] = {}
    for record in runner._events():
        if record["event"]["event_type"] == "WORKER_DELTA_INTENT_RECORDED":
            intents.setdefault(record["payload"].get("operation_id"), []).append(record["payload"])
    for effect in runner._accepted_effects("OPERATION_RESULT"):
        payload = effect["payload"]
        operation_id = payload.get("operation_id")
        require(len(intents.get(operation_id, [])) == 1, "WORKER_INTENT_INVALID", "accepted Worker result lacks one mutation intent")
        intent = intents[operation_id][0]
        require(
            intent.get("delta") == payload.get("delta")
            and intent.get("worker_result") == payload.get("worker_result")
            and intent.get("provider_evidence") == payload.get("provider_evidence")
            and intent.get("admission") == payload.get("admission"),
            "WORKER_INTENT_INVALID",
            "Worker result differs from its frozen mutation intent",
        )
        for key in ("worker_result", "provider_evidence", "admission"):
            runner.store.verify(ArtifactRef.from_dict(payload[key]))
        for ref_value in payload.get("validations", []):
            runner.store.verify(ArtifactRef.from_dict(ref_value))
        require(isinstance(payload.get("delta"), list), "WORKER_RESULT_INVALID", "Worker delta missing")
        for item in payload["delta"]:
            require(set(item) == {"path", "op", "before", "after"}, "WORKER_RESULT_INVALID", "Worker delta schema invalid")

    for record in runner._events():
        if record["event"]["event_type"] != "TASK_RESULT_ACCEPTED":
            continue
        accepted = record["payload"]
        verified = runner._verified_accepted_child(accepted)
        bindings = [
            item["payload"]
            for item in runner._events()
            if item["event"]["event_type"] == "TASK_BOUND"
            and item["payload"].get("child_task_id") == accepted.get("child_task_id")
        ]
        require(len(bindings) == 1, "TASK_RESULT_INVALID", "accepted child binding is not unique")
        binding = bindings[0]["parent_binding"]
        child_mission = ArtifactRef.from_dict(verified["task"]["mission"])
        require(child_mission.sha256 == binding["mission_sha256"], "TASK_RESULT_INVALID", "accepted child mission differs from binding")


def _verify_frozen_final(runner: Any, plan: dict[str, Any], plan_ref: ArtifactRef, seal_ref: ArtifactRef) -> dict[str, Any]:
    freezes = [record for record in runner._events() if record["event"]["event_type"] == "FINAL_SUBJECT_FROZEN"]
    require(len(freezes) == 1, "TASK_FINAL_INVALID", "complete Task must have exactly one frozen final subject")
    freeze = freezes[0]["payload"]
    runner._verify_refs_recursive(freeze)
    required_freeze = {
        "schema_version", "subject", "subject_sha256", "mission", "sealed_plan", "plan_seal", "evidence", "result",
        "accepted_task_results", "inspection_results", "done_proof", "smoke",
    }
    require(set(freeze) == required_freeze and freeze.get("schema_version") == 1, "TASK_FINAL_INVALID", "freeze receipt schema invalid")
    subject_ref, subject = _artifact(runner, freeze["subject"], "TASK_FINAL_INVALID")
    runner._verify_refs_recursive(subject)
    require(subject_ref.sha256 == freeze["subject_sha256"], "TASK_FINAL_INVALID", "frozen subject hash declaration mismatch")
    subject_fields = {
        "schema_version", "mission", "sealed_plan", "plan_seal", "evidence", "result",
        "accepted_task_results", "inspection_results", "done_proof",
    }
    require(set(subject) == subject_fields and subject.get("schema_version") == 1, "TASK_FINAL_INVALID", "frozen subject schema invalid")
    for key in subject_fields - {"schema_version"}:
        require(subject[key] == freeze[key], "TASK_FINAL_INVALID", f"freeze receipt differs from subject field: {key}")
    require(subject["mission"] == runner.task["mission"], "TASK_FINAL_INVALID", "frozen subject mission mismatch")
    require(subject["sealed_plan"] == plan_ref.as_dict(), "TASK_FINAL_INVALID", "frozen subject Plan mismatch")
    require(subject["plan_seal"] == seal_ref.as_dict(), "TASK_FINAL_INVALID", "frozen subject Plan seal mismatch")
    if freeze["smoke"] is not None:
        runner.store.verify(ArtifactRef.from_dict(freeze["smoke"]))

    evidence_ref, evidence = _artifact(runner, subject["evidence"], "TASK_FINAL_INVALID")
    require(
        set(evidence) == {"schema_version", "declared_changed_paths", "operation_refs", "validation_refs", "accepted_task_results"}
        and evidence.get("schema_version") == 1,
        "TASK_FINAL_INVALID",
        "frozen evidence schema invalid",
    )
    for group in ("operation_refs", "validation_refs", "accepted_task_results"):
        for ref_value in evidence[group]:
            runner.store.verify(ArtifactRef.from_dict(ref_value))
    runner._verify_frozen_workspace(evidence)

    result_ref, result = _artifact(runner, subject["result"], "TASK_RESULT_INVALID")
    require(set(result) == {"schema_version", "artifacts"} and result.get("schema_version") == 1 and isinstance(result["artifacts"], list), "TASK_RESULT_INVALID", "Task result schema invalid")
    for ref_value in result["artifacts"]:
        runner.store.verify(ArtifactRef.from_dict(ref_value))
    require(evidence_ref.as_dict() in result["artifacts"], "TASK_RESULT_INVALID", "Task result omits frozen evidence")

    expected_task_results = [runner._event_ref(record).as_dict() for record in runner._events() if record["event"]["event_type"] == "TASK_RESULT_ACCEPTED"]
    expected_inspections = [runner._event_ref(record).as_dict() for record in runner._events() if record["event"]["event_type"] == "INSPECTION_RECORDED"]
    if plan["delivery_kind"] == "inspect":
        report_refs = [ref for ref in result["artifacts"] if ref != evidence_ref.as_dict()]
        require(len(report_refs) == 1, "TASK_RESULT_INVALID", "inspect Task result must contain exactly one inspection report")
        _, report = _artifact(runner, report_refs[0], "TASK_RESULT_INVALID")
        require(
            set(report) == {"schema_version", "baseline", "inspections", "accepted_task_results"}
            and report.get("schema_version") == 1
            and report.get("baseline") == runner._baseline()["manifest_sha256"]
            and report.get("inspections") == expected_inspections
            and report.get("accepted_task_results") == expected_task_results,
            "TASK_RESULT_INVALID",
            "inspection report does not match its baseline and result sets",
        )
        require(bool(expected_inspections or expected_task_results), "TASK_RESULT_INVALID", "inspect Task produced no inspection or accepted child result")
    else:
        require(result["artifacts"] == [evidence_ref.as_dict()], "TASK_RESULT_INVALID", "workspace-change Task result contains undeclared artifacts")

    completions = runner._step_completion_records()
    completion_refs = {step_id: runner._event_ref(records[0]).as_dict() for step_id, records in completions.items()}
    proof_refs = {
        item["step_id"]: item["completion"]
        for item in subject["done_proof"]
        if isinstance(item, dict) and set(item) == {"step_id", "completion"} and isinstance(item.get("step_id"), str) and isinstance(item.get("completion"), dict)
    }
    require(
        len(subject["done_proof"]) == len(completion_refs)
        and proof_refs == completion_refs,
        "TASK_FINAL_INVALID",
        "frozen done proof does not exactly bind step completions",
    )
    require(subject["accepted_task_results"] == expected_task_results, "TASK_FINAL_INVALID", "frozen subject child-result set mismatch")
    require(subject["inspection_results"] == expected_inspections, "TASK_FINAL_INVALID", "frozen subject inspection-result set mismatch")
    expected_operations = [runner._event_ref(record).as_dict() for record in runner._accepted_effects("OPERATION_RESULT")]
    expected_validations = [ref for record in runner._accepted_effects("OPERATION_RESULT") for ref in record["payload"].get("validations", [])]
    require(evidence["operation_refs"] == expected_operations, "TASK_FINAL_INVALID", "frozen Worker operation set mismatch")
    require(evidence["validation_refs"] == expected_validations, "TASK_FINAL_INVALID", "frozen Worker validation set mismatch")
    require(evidence["accepted_task_results"] == expected_task_results, "TASK_FINAL_INVALID", "frozen evidence child-result set mismatch")

    passes = runner._consecutive_final_passes(subject_ref.sha256)
    require(len(passes) >= 3, "TASK_FINAL_REVIEWS_INVALID", "complete Task lacks three unchanged final reviews")
    for review in passes[-3:]:
        _, request = _request_for_operation(runner, review["operation_id"])
        require(request.get("subject") == subject_ref.as_dict(), "TASK_FINAL_REVIEWS_INVALID", "final reviewer reviewed a different frozen subject")
        required_claims = sorted(clause["claim_id"] for clause in plan["done"] if clause["kind"] == "reviewer_claim")
        require(request.get("required_claims") == required_claims, "TASK_FINAL_REVIEWS_INVALID", "final reviewer request omitted a mandatory Plan claim")
    return {
        "frozen": freeze,
        "subject": subject,
        "subject_ref": subject_ref,
        "evidence": evidence,
        "evidence_ref": evidence_ref,
        "result": result,
        "result_ref": result_ref,
    }


def _verify_complete(runner: Any) -> dict[str, Any]:
    _verify_role_effects(runner)
    plan, plan_ref, seal_ref = _verify_plan(runner)
    _verify_steps_and_worker_refs(runner, plan)
    final = _verify_frozen_final(runner, plan, plan_ref, seal_ref)
    return {"task": runner.task, "plan": plan, **final}


def verify_task_ready_for_complete(runner: Any) -> dict[str, Any]:
    """Prove every COMPLETE invariant before the terminal event is appended."""
    require(runner._last_event_payload("TERMINAL_RECEIPT_RECORDED") is None, "CONTROL_STATE_TERMINAL", "pre-completion verification requires a nonterminal Task")
    require(runner._last_event_payload("TASK_BLOCKED_UNKNOWN") is None, "CONTROL_STATE_TERMINAL", "blocked Task cannot complete")
    _verify_parent_binding(runner, runner.task.get("parent_binding"))
    return _verify_complete(runner)


def verify_task_terminal(
    task_root: Path,
    expected_parent_binding: dict[str, Any] | None = None,
    expected_success_outcome: str | None = None,
) -> dict[str, Any]:
    """Verify a terminal Task exactly as an external parent would."""
    from .runner import Runner

    runner = Runner(task_root, read_only=True)
    _verify_parent_binding(runner, expected_parent_binding)
    terminal_events = [record for record in runner._events() if record["event"]["event_type"] == "TERMINAL_RECEIPT_RECORDED"]
    require(len(terminal_events) == 1, "TERMINAL_RECEIPT_INVALID", "terminal receipt must be unique")
    marker = terminal_events[0]["payload"]
    require(set(marker) in ({"schema_version", "receipt", "outcome"}, {"schema_version", "receipt", "outcome", "operation_id"}), "TERMINAL_RECEIPT_INVALID", "terminal marker schema invalid")
    terminal_ref, receipt = _artifact(runner, marker.get("receipt"), "TERMINAL_RECEIPT_INVALID")
    require(
        set(receipt) == {"schema_version", "outcome", "reason", "result", "evidence", "workspace_model", "rollback"}
        and receipt.get("schema_version") == 1
        and receipt.get("outcome") == marker.get("outcome"),
        "TERMINAL_RECEIPT_INVALID",
        "terminal receipt binding invalid",
    )
    for evidence in receipt["evidence"]:
        runner.store.verify(ArtifactRef.from_dict(evidence))
    if expected_success_outcome is not None:
        require(receipt["outcome"] == expected_success_outcome, "TASK_OUTCOME_MISMATCH", "unexpected Task outcome")

    result: dict[str, Any] = {
        "task": runner.task,
        "outcome": receipt["outcome"],
        "terminal_receipt": receipt,
        "terminal_ref": terminal_ref,
        "result_ref": None,
        "result": None,
        "plan": None,
        "frozen": None,
        "evidence_ref": None,
        "evidence": None,
    }
    if receipt["outcome"] == "COMPLETE":
        complete = _verify_complete(runner)
        require(receipt["result"] == complete["result_ref"].as_dict(), "TASK_RESULT_INVALID", "terminal result differs from reviewed frozen result")
        result.update(complete)
    return result
