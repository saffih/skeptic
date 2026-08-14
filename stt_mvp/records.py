"""Closed reference and selector validators for Slice A."""
from .codec import closed_object
from .schema import CanonicalRecordKind
from .identity import MAX_U64, raw_sha256

EVENT_KINDS = frozenset((
    "TASK_CREATED", "ROUND_CREATED", "PLANNING_STARTED", "OPERATION_REQUESTED",
    "ATTEMPT_STARTED", "LAUNCH_INTENT_RECORDED", "ATTEMPT_FINISHED",
    "SETTLEMENT_OBSERVED", "PLANNING_FINISHED", "STEP_STARTED", "STEP_FINISHED",
    "VALIDATION_STARTED", "VALIDATION_RECORDED", "OUTPUT_ASSESSMENT_RECORDED",
    "ROUND_FINISHED", "TASK_FINISHED",
))

def _string(value):
    if type(value) is not str or not value: raise ValueError("nonempty string required")

def validate_ref(value, family):
    fields = {
      "ContentRef": ("schema","record_id","relative_path","size_bytes","sha256"),
      "PayloadRef": ("schema","record_id","payload_path","size_bytes","sha256"),
      "RecordRef": ("schema","record_id","task_id","ledger_sequence","event_kind","transition_id","payload_path","size_bytes","sha256"),
      "PrefixRef": ("schema","prefix_id","run_id","manifest_path","sha256"),
    }
    if family not in fields: raise ValueError("unknown reference family")
    closed_object(value, fields[family])
    if value["schema"] != family + "@1": raise ValueError("wrong reference schema")
    for key, item in value.items():
        if key == "sha256":
            raw_sha256(item)
        elif key in ("size_bytes", "ledger_sequence"):
            if type(item) is not int or not 0 <= item <= MAX_U64: raise ValueError("invalid numeric reference field")
        elif key != "schema":
            _string(item)
    if family == "RecordRef" and value["event_kind"] not in EVENT_KINDS:
        raise ValueError("unknown event kind")
    return value

def validate_source_selector(value):
    if not isinstance(value, dict) or type(value.get("kind")) is not str: raise ValueError("invalid selector")
    fields = {
      "RECORD": ("kind","source_identity","record_kind","record_id"),
      "ARTIFACT": ("kind","source_identity","artifact_id"),
      "PATH": ("kind","source_identity","relative_path","object_type"),
      "REQUIREMENT": ("kind","source_identity","requirement_id","producer_constraint"),
      "PRIOR_RUN_RECORD": ("kind","source_identity","source_run_id","record_kind","record_id","import_hash"),
    }
    if value["kind"] not in fields: raise ValueError("unknown selector kind")
    closed_object(value, fields[value["kind"]])
    if "record_kind" in value: CanonicalRecordKind(value["record_kind"])
    for key, item in value.items():
        if key in ("record_kind", "kind"): _string(item)
        elif key == "producer_constraint":
            shapes = {
                "ANY_ADMITTED_PRODUCER": {"kind"}, "STEP": {"kind", "step_id"},
                "ROUTE": {"kind", "route_name"}, "OPERATION_ROLE": {"kind", "role"},
            }
            if not isinstance(item, dict) or item.get("kind") not in shapes or set(item) != shapes[item["kind"]]:
                raise ValueError("invalid producer constraint")
            for nested_key, nested_value in item.items():
                if nested_key != "kind": _string(nested_value)
            if item["kind"] == "OPERATION_ROLE" and item["role"] not in {"PLANNER", "WORKER", "COMMAND", "VALIDATOR"}:
                raise ValueError("invalid operation role")
        else: _string(item)
    return value
