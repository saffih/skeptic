"""Closed reference and selector validators for Slice A."""
from .codec import closed_object
from .schema import CanonicalRecordKind

def _string(value):
    if type(value) is not str or not value: raise ValueError("nonempty string required")

def validate_ref(value, family):
    fields = {
      "ContentRef": ("schema","record_id","relative_path","size_bytes","sha256"),
      "PayloadRef": ("schema","record_id","payload_path","size_bytes","sha256"),
      "RecordRef": ("schema","record_id","task_id","ledger_sequence","event_kind","transition_id","payload_path","size_bytes","sha256"),
      "PrefixRef": ("schema","prefix_id","run_id","manifest_path","sha256"),
    }
    closed_object(value, fields[family])
    if value["schema"] != family + "@1": raise ValueError("wrong reference schema")
    for key, item in value.items():
        if key not in ("schema", "size_bytes", "ledger_sequence"): _string(item)
        elif key != "schema" and (type(item) is not int or item < 0): raise ValueError("invalid numeric reference field")
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
    closed_object(value, fields[value["kind"]])
    if "record_kind" in value: CanonicalRecordKind(value["record_kind"])
    for item in value.values(): _string(item)
    return value
