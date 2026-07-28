"""Fail-closed validator for the compact Body state contract."""

from __future__ import annotations
import hashlib, json, os, re
from pathlib import Path
from typing import Any

MAX_STATE_BYTES = 32768
MAX_SUMMARY_BYTES = 256
MAX_ID_BYTES = 64
MAX_PATH_BYTES = 512
MAX_ARTIFACTS = 64
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
STATE_FIELDS = {"TASK_ID", "SEALED_PLAN_REFERENCE", "SEALED_PLAN_SHA256", "CURRENT_STEP", "COMPLETED_STEP_IDS", "VALIDATED_FACTS", "OPEN_BLOCKERS", "ARTIFACT_REFERENCES", "NEXT_AUTHORIZED_ACTION", "VALIDATION_STATUS"}
ARTIFACT_FIELDS = {"reference_id", "repository_relative_path", "sha256", "byte_size", "artifact_type", "description", "read_condition"}
FACT_FIELDS = {"summary", "status", "artifact_reference_ids"}
BLOCKER_FIELDS = {"summary", "artifact_reference_ids"}

class BodyStateError(ValueError):
    def __init__(self, code: str, path: str = "$"):
        self.code, self.path = code, path
        super().__init__(f"{code} at {path}")

def _obj(value: Any, fields: set[str], path: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields: raise BodyStateError("FIELDS", path)
    return value

def _short(value: Any, path: str, limit: int = MAX_SUMMARY_BYTES) -> str:
    if not isinstance(value, str) or not value or len(value.encode()) > limit: raise BodyStateError("SHORT_STRING", path)
    return value

def _ids(value: Any, path: str, known: set[str]) -> None:
    if not isinstance(value, list) or len(value) > MAX_ARTIFACTS: raise BodyStateError("LIST", path)
    for i, item in enumerate(value):
        item = _short(item, f"{path}/{i}", MAX_ID_BYTES)
        if item not in known: raise BodyStateError("UNKNOWN_ARTIFACT", f"{path}/{i}")

def _path(value: Any, path: str) -> str:
    value = _short(value, path, MAX_PATH_BYTES)
    if Path(value).is_absolute() or "\\" in value or any(part in {"", ".", ".."} for part in value.split("/")): raise BodyStateError("UNSAFE_PATH", path)
    return value

def _hash_file(path: Path) -> tuple[str, int]:
    digest, size = hashlib.sha256(), 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024): digest.update(chunk); size += len(chunk)
    return digest.hexdigest(), size

def validate_state_bytes(raw: bytes, *, repository_root: Path | str = ".", expected_task_id: str | None = None) -> dict[str, Any]:
    if len(raw) > MAX_STATE_BYTES: raise BodyStateError("STATE_TOO_LARGE")
    try: text = raw.decode("utf-8")
    except UnicodeDecodeError as exc: raise BodyStateError("UTF8") from exc
    if text.startswith("\ufeff") or not raw.endswith(b"\n") or raw.endswith(b"\n\n"): raise BodyStateError("ENCODING")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result: raise BodyStateError("DUPLICATE_KEY")
            result[key] = value
        return result
    try: state = json.loads(text, object_pairs_hook=pairs)
    except BodyStateError: raise
    except (json.JSONDecodeError, UnicodeError) as exc: raise BodyStateError("JSON") from exc
    if not isinstance(state, dict) or set(state) != STATE_FIELDS: raise BodyStateError("STATE_FIELDS")
    canonical = (json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if canonical != raw: raise BodyStateError("NONCANONICAL")
    for key in ("TASK_ID", "SEALED_PLAN_REFERENCE", "CURRENT_STEP", "NEXT_AUTHORIZED_ACTION", "VALIDATION_STATUS"): _short(state[key], f"$.{key}")
    if expected_task_id is not None and state["TASK_ID"] != expected_task_id: raise BodyStateError("TASK_ID_MISMATCH", "$.TASK_ID")
    _path(state["SEALED_PLAN_REFERENCE"], "$.SEALED_PLAN_REFERENCE")
    if not isinstance(state["SEALED_PLAN_SHA256"], str) or not SHA256_RE.fullmatch(state["SEALED_PLAN_SHA256"]): raise BodyStateError("SHA256", "$.SEALED_PLAN_SHA256")
    if not isinstance(state["COMPLETED_STEP_IDS"], list): raise BodyStateError("LIST", "$.COMPLETED_STEP_IDS")
    for i, step in enumerate(state["COMPLETED_STEP_IDS"]): _short(step, f"$.COMPLETED_STEP_IDS/{i}", MAX_ID_BYTES)
    root = Path(repository_root).resolve(); refs = {}; artifacts = state["ARTIFACT_REFERENCES"]
    if not isinstance(artifacts, list) or len(artifacts) > MAX_ARTIFACTS: raise BodyStateError("ARTIFACTS", "$.ARTIFACT_REFERENCES")
    for i, raw_ref in enumerate(artifacts):
        ref = _obj(raw_ref, ARTIFACT_FIELDS, f"$.ARTIFACT_REFERENCES/{i}"); rid = _short(ref["reference_id"], f".../{i}/reference_id", MAX_ID_BYTES)
        if rid in refs: raise BodyStateError("DUPLICATE_REFERENCE", f".../{i}/reference_id")
        refs[rid] = ref; rel = _path(ref["repository_relative_path"], f".../{i}/repository_relative_path")
        if not isinstance(ref["sha256"], str) or not SHA256_RE.fullmatch(ref["sha256"]): raise BodyStateError("SHA256", f".../{i}/sha256")
        if not isinstance(ref["byte_size"], int) or isinstance(ref["byte_size"], bool) or ref["byte_size"] < 0: raise BodyStateError("BYTE_SIZE", f".../{i}/byte_size")
        for key in ("artifact_type", "description", "read_condition"): _short(ref[key], f".../{i}/{key}")
        target = (root / rel).resolve()
        if os.path.commonpath((str(root), str(target))) != str(root) or not target.is_file(): raise BodyStateError("ARTIFACT_MISSING", f".../{i}/repository_relative_path")
        digest, size = _hash_file(target)
        if size != ref["byte_size"] or digest != ref["sha256"]: raise BodyStateError("ARTIFACT_MISMATCH", f".../{i}")
    if state["SEALED_PLAN_REFERENCE"] not in {ref["repository_relative_path"] for ref in refs.values()}: raise BodyStateError("PLAN_REFERENCE_MISSING", "$.SEALED_PLAN_REFERENCE")
    plan_ref = next(ref for ref in refs.values() if ref["repository_relative_path"] == state["SEALED_PLAN_REFERENCE"])
    if plan_ref["sha256"] != state["SEALED_PLAN_SHA256"]: raise BodyStateError("PLAN_HASH_MISMATCH", "$.SEALED_PLAN_SHA256")
    facts = state["VALIDATED_FACTS"]
    if not isinstance(facts, list) or len(facts) > MAX_ARTIFACTS: raise BodyStateError("LIST", "$.VALIDATED_FACTS")
    for i, fact in enumerate(facts):
        fact = _obj(fact, FACT_FIELDS, f"$.VALIDATED_FACTS/{i}"); _short(fact["summary"], f"$.VALIDATED_FACTS/{i}/summary"); _short(fact["status"], f"$.VALIDATED_FACTS/{i}/status"); _ids(fact["artifact_reference_ids"], f"$.VALIDATED_FACTS/{i}/artifact_reference_ids", set(refs))
        if not fact["artifact_reference_ids"]: raise BodyStateError("FACT_WITHOUT_EVIDENCE", f"$.VALIDATED_FACTS/{i}")
    blockers = state["OPEN_BLOCKERS"]
    if not isinstance(blockers, list) or len(blockers) > MAX_ARTIFACTS: raise BodyStateError("LIST", "$.OPEN_BLOCKERS")
    for i, blocker in enumerate(blockers):
        blocker = _obj(blocker, BLOCKER_FIELDS, f"$.OPEN_BLOCKERS/{i}"); _short(blocker["summary"], f"$.OPEN_BLOCKERS/{i}/summary"); _ids(blocker["artifact_reference_ids"], f"$.OPEN_BLOCKERS/{i}/artifact_reference_ids", set(refs))
    return state

def validate_state_file(state_path, *, repository_root=".", expected_task_id=None): return validate_state_bytes(Path(state_path).read_bytes(), repository_root=repository_root, expected_task_id=expected_task_id)

if __name__ == "__main__":
    import argparse, sys
    parser = argparse.ArgumentParser(); parser.add_argument("state_path"); parser.add_argument("--repository-root", default="."); parser.add_argument("--expected-task-id"); args = parser.parse_args()
    try: validate_state_file(args.state_path, repository_root=args.repository_root, expected_task_id=args.expected_task_id)
    except (OSError, BodyStateError) as exc: print(f"BODY_STATE_INVALID {getattr(exc, 'code', 'FILE_IO')}", file=sys.stderr); raise SystemExit(2)
    print("BODY_STATE_VALID")
