from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any

from .canonical import canonical_json_bytes, safe_relpath, sha256_bytes
from .errors import STTError, require


DONE_PREDICATES = {
    "all_declared_final_commands_succeeded": "final_checkpoint",
    "installed_tree_equals_frozen_candidate": "installed_tree",
    "git_control_state_unchanged": "installed_tree",
}
REVIEWER_CLAIMS = {
    "mission_objective_satisfied": "frozen_final_candidate",
    "final_find_loop_clean": "frozen_final_candidate",
}
TOP_FIELDS = {"schema_version", "mission_sha256", "baseline_id", "objective", "done", "steps"}
SCOPE_FIELDS = {"path", "kind"}
COMMAND_FIELDS = {"tool_id", "args", "cwd", "timeout_seconds", "accepted_exit_codes"}


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
        require(kind in {"file", "tree"}, "PLAN_SCHEMA", "scope kind must be file or tree")
        key = (path, kind)
        require(key not in seen, "PLAN_SCOPE_DUPLICATE", "duplicate scope entry", path=path)
        seen.add(key)
        result.append({"path": path, "kind": kind})
    if write:
        for i, left in enumerate(result):
            for right in result[i + 1:]:
                lp, rp = PurePosixPath(left["path"]), PurePosixPath(right["path"])
                overlaps = lp == rp or lp in rp.parents or rp in lp.parents
                if overlaps:
                    allowed = (left["kind"] == "tree" and lp in rp.parents) or (right["kind"] == "tree" and rp in lp.parents)
                    require(allowed, "PLAN_SCOPE_OVERLAP", "ambiguous write-scope overlap", left=left, right=right)
    return result


def validate_command(command: Any, catalog_ids: set[str], source_paths: list[str], limits: dict[str, int]) -> dict[str, Any]:
    require(isinstance(command, dict), "PLAN_SCHEMA", "command must be an object")
    _exact(command, COMMAND_FIELDS, "PLAN_SCHEMA")
    tool_id = command["tool_id"]
    require(tool_id in catalog_ids, "PLAN_TOOL_NOT_BOUND", f"tool not in catalog: {tool_id}")
    args = command["args"]
    require(isinstance(args, list) and all(isinstance(arg, str) and "\x00" not in arg for arg in args), "PLAN_COMMAND_ARGS", "command args must be UTF-8 strings")
    if tool_id == "python":
        require("-c" not in args, "PLAN_TOOL_POLICY", "python -c is forbidden")
    forbidden_tokens = {"push", "publish", "upload", "curl", "wget", "ssh"}
    require(not any(arg.lower() in forbidden_tokens for arg in args), "PLAN_TOOL_POLICY", "network/publication command argument forbidden")
    for arg in args:
        require(".." not in PurePosixPath(arg).parts, "PLAN_COMMAND_PATH", "parent traversal in command argument")
        require(not any(path and path in arg for path in source_paths), "PLAN_COMMAND_PATH", "authoritative path leaked into command argument")
    cwd = command["cwd"]
    if cwd != ".":
        safe_relpath(cwd)
    timeout = command["timeout_seconds"]
    require(type(timeout) is int and 0 < timeout <= limits["max_semantic_operation_seconds"], "PLAN_COMMAND_TIMEOUT", "invalid command timeout")
    accepted = command["accepted_exit_codes"]
    require(isinstance(accepted, list) and accepted and all(type(code) is int and 0 <= code <= 255 for code in accepted), "PLAN_COMMAND_EXITS", "invalid accepted exit codes")
    require(len(set(accepted)) == len(accepted), "PLAN_COMMAND_EXITS", "duplicate accepted exit code")
    return command


def validate_plan(plan: Any, *, mission_sha256: str, baseline_id: str, catalog_ids: set[str], source_paths: list[str], limits: dict[str, int]) -> dict[str, Any]:
    require(isinstance(plan, dict), "PLAN_SCHEMA", "Plan must be an object")
    _exact(plan, TOP_FIELDS, "PLAN_SCHEMA")
    require(plan["schema_version"] == 1, "PLAN_SCHEMA", "unsupported Plan schema")
    require(plan["mission_sha256"] == mission_sha256 and plan["baseline_id"] == baseline_id, "PLAN_BINDING", "Plan binding mismatch")
    require(isinstance(plan["objective"], str) and plan["objective"].strip(), "PLAN_SCHEMA", "objective is required")
    done = plan["done"]
    require(isinstance(done, list) and done, "PLAN_DONE", "typed done clauses required")
    done_ids: set[str] = set()
    for clause in done:
        require(isinstance(clause, dict), "PLAN_DONE", "done clause must be an object")
        _exact(clause, {"id", "kind", "predicate_id" if clause.get("kind") == "deterministic_predicate" else "claim_id", "subject_ref"}, "PLAN_DONE")
        require(clause["id"] not in done_ids, "PLAN_DONE", "duplicate done id")
        done_ids.add(clause["id"])
        if clause["kind"] == "deterministic_predicate":
            require(clause["predicate_id"] in DONE_PREDICATES, "PLAN_DONE", "unknown deterministic predicate")
        elif clause["kind"] == "reviewer_claim":
            require(clause["claim_id"] in REVIEWER_CLAIMS, "PLAN_DONE", "unknown reviewer claim")
        else:
            raise STTError("PLAN_DONE", "unknown done clause kind")
    steps = plan["steps"]
    require(isinstance(steps, list) and len(steps) <= limits["max_plan_steps"], "PLAN_STEPS", "invalid Plan step count")
    step_ids: set[str] = set(); total_commands = 0
    for step in steps:
        require(isinstance(step, dict), "PLAN_SCHEMA", "step must be an object")
        kind = step.get("kind")
        if kind == "change":
            _exact(step, {"id", "kind", "route_profile", "objective", "read_scope", "write_scope", "validation_commands"}, "PLAN_SCHEMA")
            require(step["route_profile"] in {"economical", "standard"}, "PLAN_ROUTE", "invalid Worker route")
            read_scope = _validate_scope(step["read_scope"])
            write_scope = _validate_scope(step["write_scope"], write=True)
            require(len(read_scope) <= limits["max_scope_entries_per_step"] and len(write_scope) <= limits["max_scope_entries_per_step"], "PLAN_SCOPE_LIMIT", "scope entry limit exceeded")
            commands = step["validation_commands"]
            require(isinstance(commands, list) and len(commands) <= limits["max_commands_per_change_step"], "PLAN_COMMAND_LIMIT", "change-step command limit exceeded")
        elif kind == "validation":
            _exact(step, {"id", "kind", "commands"}, "PLAN_SCHEMA")
            commands = step["commands"]
            require(isinstance(commands, list), "PLAN_SCHEMA", "commands must be an array")
        else:
            raise STTError("PLAN_SCHEMA", "step kind must be change or validation")
        require(isinstance(step["id"], str) and step["id"] and step["id"] not in step_ids, "PLAN_STEP_ID", "invalid or duplicate step id")
        step_ids.add(step["id"])
        for command in commands:
            validate_command(command, catalog_ids, source_paths, limits)
        total_commands += len(commands)
    require(total_commands <= limits["max_total_commands"], "PLAN_COMMAND_LIMIT", "total command limit exceeded")
    return plan


def plan_identity(plan: dict[str, Any]) -> tuple[bytes, str]:
    body = canonical_json_bytes(plan)
    return body, sha256_bytes(body)
