"""Closed versioned schemas and persisted-record family mapping."""
from enum import Enum
import re

_SCHEMA = re.compile(r"^[A-Za-z][A-Za-z0-9_]*@[1-9][0-9]*$")

SCHEMA_TO_KIND = {
 "RunRecord@1":"RunRecord", "TaskRecord@1":"TaskRecord", "RoundRecord@1":"RoundRecord", "Plan@1":"Plan", "OperationRequest@1":"OperationRequest", "AttemptRecord@1":"AttemptRecord", "AttemptOutcome@1":"AttemptOutcome", "CaptureRecord@1":"CaptureRecord", "PlannerResult@1":"PlannerResult", "WorkerResult@1":"WorkerResult", "StepResult@1":"StepResult", "ValidatorResult@1":"ValidatorResult", "TaskResult@1":"TaskResult", "TaskOutputAssessment@1":"TaskOutputAssessment", "ArtifactRef@1":"ArtifactRef", "InputRef@1":"InputRef", "InputResolution@1":"InputResolution", "TransitionManifest@1":"TransitionManifest", "EventBody@1":"EventBody", "LedgerEvent@1":"LedgerEvent", "RunPrefixManifest@1":"RunPrefixManifest", "PrefixTaskHead@1":"PrefixTaskHead",
}
CanonicalRecordKind = Enum("CanonicalRecordKind", {kind: kind for kind in SCHEMA_TO_KIND.values()}, type=str)

def validate_schema_identifier(schema):
    if type(schema) is not str or not _SCHEMA.fullmatch(schema):
        raise ValueError("invalid schema identifier")
    return schema

def record_kind_for_schema(schema):
    validate_schema_identifier(schema)
    if type(schema) is not str or schema not in SCHEMA_TO_KIND:
        raise ValueError("unsupported exact persisted schema")
    return CanonicalRecordKind(SCHEMA_TO_KIND[schema])

def validate_record_kind(schema, record_kind):
    kind = record_kind_for_schema(schema)
    if isinstance(record_kind, CanonicalRecordKind): record_kind = record_kind.value
    if record_kind != kind.value: raise ValueError("schema and record kind mismatch")
    return kind

def validate_allowed_record_kinds(kinds):
    if not isinstance(kinds, list) or not kinds: raise ValueError("nonempty kinds required")
    if len(set(kinds)) != len(kinds): raise ValueError("duplicate record kind")
    return [CanonicalRecordKind(k) for k in kinds]
