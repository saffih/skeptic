"""Exact domain-separated STT identity derivation."""
import hashlib
import re
import uuid

MAX_U64 = (1 << 64) - 1
_HEX = re.compile(r"^[0-9a-f]{64}$")


def uint64_be(value):
    if type(value) is not int or not 0 <= value <= MAX_U64:
        raise ValueError("expected uint64")
    return value.to_bytes(8, "big")


def raw_sha256(value):
    if not isinstance(value, str) or not _HEX.fullmatch(value):
        raise ValueError("expected lowercase SHA-256 hex")
    return bytes.fromhex(value)


def text(value):
    if not isinstance(value, str):
        raise ValueError("expected exact string")
    return value.encode("utf-8")


def H(domain, *parts):
    if not isinstance(domain, str) or not domain.isascii():
        raise ValueError("domain tag must be ASCII")
    digest = hashlib.sha256(domain.encode("ascii"))
    for part in parts:
        if not isinstance(part, bytes):
            raise ValueError("H inputs must be exact bytes")
        digest.update(uint64_be(len(part)))
        digest.update(part)
    return digest.hexdigest()


def uuid4_lower(value):
    try:
        parsed = uuid.UUID(value)
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid UUIDv4") from exc
    if parsed.version != 4 or str(parsed) != value:
        raise ValueError("expected lowercase UUIDv4")
    return value


def root_task_id(run_id, root_task_spec, authority, required_outputs): return H("stt-root-task-v1", text(run_id), root_task_spec, authority, required_outputs)
def child_task_id(parent_task, round_number, step_id, child_task_step): return H("stt-child-task-v1", text(parent_task), uint64_be(round_number), text(step_id), child_task_step)
def round_id(task_id, round_number): return H("stt-round-v1", text(task_id), uint64_be(round_number))
def plan_id(request, body): return H("stt-plan-v1", request, body)
def step_id(plan, ordinal, body): return H("stt-step-v1", text(plan), uint64_be(ordinal), body)
def input_id(step, ordinal, dependency): return H("stt-input-v1", text(step), uint64_be(ordinal), dependency)
def requirement_id(step, ordinal, requirement): return H("stt-requirement-v1", text(step), uint64_be(ordinal), requirement)
def authority_id(body): return H("stt-authority-v1", body)
def routing_identity(body): return H("stt-routing-v1", body)
def prefix_id(jsonl): return H("stt-prefix-v1", jsonl)
def operation_request_id(body): return H("stt-operation-v1", body)
def attempt_id(request, ordinal): return H("stt-attempt-v1", text(request), uint64_be(ordinal))
def artifact_id(body): return H("stt-artifact-v1", body)
def record_id(kind, path, size, content_hash): return H("stt-record-v1", text(kind), text(path), uint64_be(size), raw_sha256(content_hash))
def observation_id(body): return H("stt-observation-v1", body)
def transition_id(manifest): return H("stt-transition-v1", manifest)
def event_hash(preimage): return H("stt-event-v1", preimage)
