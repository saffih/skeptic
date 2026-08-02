from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any

from .boundary import scope_overlaps_nested, validate_path_collisions, validate_scope_against_nested
from .canonical import canonical_json_bytes, safe_relpath, sha256_bytes
from .errors import STTError, require
from .schema import PLAN_SCHEMA, SCHEMA_VERSION


DONE_PREDICATES = {key: key for key in PLAN_SCHEMA["deterministic_predicate_ids"]}
REVIEWER_CLAIMS = {key: key for key in PLAN_SCHEMA["reviewer_claim_ids"]}
TOP_FIELDS = {"schema_version", "mission_sha256", "baseline_id", "objective", "done", "steps", "delivery_kind"}
SCOPE_FIELDS = {"path", "kind"}
COMMAND_FIELDS = {"tool_id", "args", "cwd", "timeout_seconds", "accepted_exit_codes"}
STEP_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z")


def _exact(obj: dict[str, Any], expected: set[str], code: str) -> None:
    require(set(obj) == expected, code, "schema fields mismatch", expected=sorted(expected), actual=sorted(obj))


def _validate_scope(value: Any, *, write: bool = False) -> list[dict[str, str]]:
    require(isinstance(value, list), "PLAN_SCHEMA", "scope must be an array")
    result: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in value:
        require(isinstance(item, dict), "PLAN_SCHEMA", "scope entry must be an object")
        _exact(item, SCOPE_FIELDS, "PLAN_SCHEMA")
        path = safe_relpath(item["path"])
        kind = item["kind"]
        require(isinstance(kind, str) and kind in {"file", "tree"}, "PLAN_SCHEMA", "scope kind must be file or tree")
        key = (path, kind)
        require(key not in seen, "PLAN_SCOPE_DUPLICATE", "duplicate scope entry", path=path)
        seen.add(key)
        result.append({"path": path, "kind": kind})
    validate_path_collisions((item["path"] for item in result), ignore_case=True)
    if write:
        for i, left in enumerate(result):
            for right in result[i + 1:]:
                lp, rp = PurePosixPath(left["path"]), PurePosixPath(right["path"])
                overlaps = lp == rp or lp in rp.parents or rp in lp.parents
                if overlaps:
                    allowed = (left["kind"] == "tree" and lp in rp.parents) or (right["kind"] == "tree" and rp in lp.parents)
                    require(allowed, "PLAN_SCOPE_OVERLAP", "ambiguous write-scope overlap", left=left, right=right)
    return result


def validate_command(command: Any, catalog_ids: set[str], source_paths: list[str], limits: dict[str, int], nested_roots: tuple[str, ...] = ()) -> dict[str, Any]:
    require(isinstance(command, dict), "PLAN_SCHEMA", "command must be an object")
    _exact(command, COMMAND_FIELDS, "PLAN_SCHEMA")
    tool_id = command["tool_id"]
    require(isinstance(tool_id, str) and tool_id in catalog_ids, "PLAN_TOOL_NOT_BOUND", "tool is not bound in the catalog")
    require(tool_id not in {"unshare", "mount"}, "PLAN_TOOL_POLICY", "sandbox infrastructure tools cannot be Plan commands")
    args = command["args"]
    require(isinstance(args, list) and all(isinstance(arg, str) and "\x00" not in arg for arg in args), "PLAN_COMMAND_ARGS", "command args must be UTF-8 strings")
    try:
        for arg in args:
            arg.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise STTError("PLAN_COMMAND_ARGS", "command args must be UTF-8 strings") from exc
    if tool_id == "python":
        require("-c" not in args, "PLAN_TOOL_POLICY", "python -c is forbidden")
    forbidden_tokens = {"push", "publish", "upload", "curl", "wget", "ssh"}
    require(not any(arg.lower() in forbidden_tokens for arg in args), "PLAN_TOOL_POLICY", "network/publication command argument forbidden")
    for arg in args:
        require(".." not in PurePosixPath(arg).parts, "PLAN_COMMAND_PATH", "parent traversal in command argument")
        require(not any(path and path in arg for path in source_paths), "PLAN_COMMAND_PATH", "authoritative path leaked into command argument")
    cwd = command["cwd"]
    safe_relpath(cwd, allow_dot=True)
    if cwd != ".":
        overlap = scope_overlaps_nested(cwd, nested_roots)
        require(overlap is None, "NESTED_REPOSITORY_SCOPE_FORBIDDEN", "command working directory overlaps nested repository", scope=cwd, nested_root=overlap)
    timeout = command["timeout_seconds"]
    require(type(timeout) is int and 0 < timeout <= limits["max_semantic_operation_seconds"], "PLAN_COMMAND_TIMEOUT", "invalid command timeout")
    accepted = command["accepted_exit_codes"]
    require(isinstance(accepted, list) and accepted and all(type(code) is int and 0 <= code <= 255 for code in accepted), "PLAN_COMMAND_EXITS", "invalid accepted exit codes")
    require(len(set(accepted)) == len(accepted), "PLAN_COMMAND_EXITS", "duplicate accepted exit code")
    return command


def validate_plan(
    plan: Any,
    *,
    mission_sha256: str,
    baseline_id: str,
    catalog_ids: set[str],
    source_paths: list[str],
    limits: dict[str, int],
    nested_roots: tuple[str, ...] = (),
    read_only_authority: bool = False,
) -> dict[str, Any]:
    require(isinstance(plan, dict), "PLAN_SCHEMA", "Plan must be an object")
    _exact(plan, TOP_FIELDS, "PLAN_SCHEMA")
    require(plan["schema_version"] == SCHEMA_VERSION, "PLAN_SCHEMA", "only Plan schema version 2 is supported")
    delivery_kind = plan["delivery_kind"]
    require(isinstance(delivery_kind, str) and delivery_kind in PLAN_SCHEMA["delivery_kinds"], "PLAN_DELIVERY_KIND", "invalid delivery kind")
    if read_only_authority:
        require(delivery_kind == "inspect", "INSPECT_AUTHORITY_VIOLATION", "inherited inspect authority requires inspect delivery")
    require(plan["mission_sha256"] == mission_sha256 and plan["baseline_id"] == baseline_id, "PLAN_BINDING", "Plan binding mismatch")
    require(isinstance(plan["objective"], str) and plan["objective"].strip(), "PLAN_SCHEMA", "objective is required")
    done = plan["done"]
    require(isinstance(done, list) and done, "PLAN_DONE", "typed done clauses required")
    done_ids: set[str] = set()
    for clause in done:
        require(isinstance(clause, dict), "PLAN_DONE", "done clause must be an object")
        _exact(clause, {"id", "kind", "predicate_id" if clause.get("kind") == "deterministic_predicate" else "claim_id", "subject_ref"}, "PLAN_DONE")
        require(isinstance(clause["id"], str) and STEP_ID.fullmatch(clause["id"]) is not None, "PLAN_DONE", "done clause identity invalid")
        require(isinstance(clause["subject_ref"], str) and clause["subject_ref"].strip(), "PLAN_DONE", "done clause subject reference invalid")
        require(clause["id"] not in done_ids, "PLAN_DONE", "duplicate done id")
        done_ids.add(clause["id"])
        if clause["kind"] == "deterministic_predicate":
            require(isinstance(clause["predicate_id"], str) and clause["predicate_id"] in DONE_PREDICATES, "PLAN_DONE", "unknown deterministic predicate")
        elif clause["kind"] == "reviewer_claim":
            require(isinstance(clause["claim_id"], str) and clause["claim_id"] in REVIEWER_CLAIMS, "PLAN_DONE", "unknown reviewer claim")
        else:
            raise STTError("PLAN_DONE", "unknown done clause kind")
    required_ids = set(PLAN_SCHEMA["delivery_kinds"][delivery_kind]["mandatory_done"])
    actual_ids = {clause.get("predicate_id", clause.get("claim_id")) for clause in done}
    require(required_ids <= actual_ids, "PLAN_DONE", "mandatory done proof is incomplete", missing=sorted(required_ids - actual_ids))
    steps = plan["steps"]
    require(isinstance(steps, list) and len(steps) <= limits["max_plan_steps"], "PLAN_STEPS", "invalid Plan step count")
    step_ids: set[str] = set(); total_commands = 0
    for step in steps:
        require(isinstance(step, dict), "PLAN_SCHEMA", "step must be an object")
        kind = step.get("kind")
        if kind == "change":
            require(delivery_kind != "inspect" and not read_only_authority, "INSPECT_AUTHORITY_VIOLATION", "inspect authority forbids workspace-changing steps")
            _exact(step, {"id", "kind", "route_profile", "objective", "read_scope", "write_scope", "validation_commands"}, "PLAN_SCHEMA")
            require(isinstance(step["route_profile"], str) and step["route_profile"] in {"economical", "standard"}, "PLAN_ROUTE", "invalid Worker route")
            read_scope = _validate_scope(step["read_scope"])
            write_scope = _validate_scope(step["write_scope"], write=True)
            validate_scope_against_nested(read_scope, nested_roots)
            validate_scope_against_nested(write_scope, nested_roots)
            require(len(read_scope) <= limits["max_scope_entries_per_step"] and len(write_scope) <= limits["max_scope_entries_per_step"], "PLAN_SCOPE_LIMIT", "scope entry limit exceeded")
            commands = step["validation_commands"]
            require(isinstance(commands, list) and len(commands) <= limits["max_commands_per_change_step"], "PLAN_COMMAND_LIMIT", "change-step command limit exceeded")
        elif kind == "validation":
            _exact(step, {"id", "kind", "commands"}, "PLAN_SCHEMA")
            commands = step["commands"]
            require(isinstance(commands, list), "PLAN_SCHEMA", "commands must be an array")
        elif kind == "inspect":
            _exact(step, {"id", "kind", "scope", "operation"}, "PLAN_SCHEMA")
            safe_relpath(step["scope"], allow_dot=True)
            if step["scope"] != ".":
                overlap = scope_overlaps_nested(step["scope"], nested_roots)
                require(overlap is None, "NESTED_REPOSITORY_SCOPE_FORBIDDEN", "inspect scope overlaps nested repository", scope=step["scope"], nested_root=overlap)
            require(isinstance(step["operation"], str) and step["operation"] in {"repository_inventory", "git_state"}, "PLAN_INSPECT_OPERATION", "unknown closed inspect operation")
            if step["operation"] == "git_state":
                require(step["scope"] == ".", "PLAN_INSPECT_SCOPE", "git_state requires repository-root scope")
            commands = []
        elif kind == "task":
            _exact(step, {"id", "kind", "mission"}, "PLAN_SCHEMA")
            require(isinstance(step["mission"], str) and step["mission"].strip(), "MISSION_REQUIRED", "task mission is effectively blank")
            try:
                mission_bytes = step["mission"].encode("utf-8")
            except UnicodeEncodeError as exc:
                raise STTError("MISSION_NOT_UTF8", "task mission must be UTF-8") from exc
            require(len(mission_bytes) <= limits["max_request_bytes"], "MISSION_TOO_LARGE", "task mission exceeds request-size limit")
            commands = []
        else:
            raise STTError("PLAN_SCHEMA", "unknown Plan step kind")
        require(isinstance(step["id"], str) and STEP_ID.fullmatch(step["id"]) is not None and step["id"] not in step_ids, "PLAN_STEP_ID", "invalid or duplicate step id")
        step_ids.add(step["id"])
        for command in commands:
            validate_command(command, catalog_ids, source_paths, limits, nested_roots)
        total_commands += len(commands)
    require(total_commands <= limits["max_total_commands"], "PLAN_COMMAND_LIMIT", "total command limit exceeded")
    if delivery_kind == "inspect":
        require(any(step["kind"] in {"inspect", "task"} for step in steps), "PLAN_DONE", "inspect delivery requires an inspection or child Task result")
    return plan


def plan_identity(plan: dict[str, Any]) -> tuple[bytes, str]:
    body = canonical_json_bytes(plan)
    return body, sha256_bytes(body)
