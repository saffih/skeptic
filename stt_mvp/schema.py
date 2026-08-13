"""Closed versioned schemas and persisted-record family mapping."""
from enum import Enum

SCHEMA_TO_KIND = {
 "RunRecord@1":"RunRecord", "TaskRecord@1":"TaskRecord", "RoundRecord@1":"RoundRecord", "Plan@1":"Plan", "OperationRequest@1":"OperationRequest", "AttemptRecord@1":"AttemptRecord", "AttemptOutcome@1":"AttemptOutcome", "CaptureRecord@1":"CaptureRecord", "PlannerResult@1":"PlannerResult", "WorkerResult@1":"WorkerResult", "StepResult@1":"StepResult", "ValidatorResult@1":"ValidatorResult", "TaskResult@1":"TaskResult", "TaskOutputAssessment@1":"TaskOutputAssessment", "ArtifactRef@1":"ArtifactRef", "InputRef@1":"InputRef", "InputResolution@1":"InputResolution", "TransitionManifest@1":"TransitionManifest", "EventBody@1":"EventBody", "LedgerEvent@1":"LedgerEvent", "RunPrefixManifest@1":"RunPrefixManifest", "PrefixTaskHead@1":"PrefixTaskHead",
}
CanonicalRecordKind = Enum("CanonicalRecordKind", {kind: kind for kind in SCHEMA_TO_KIND.values()}, type=str)

def record_kind_for_schema(schema):
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
    return [CanonicalRecordKind(k) for k in kinds]
