"""Rotation checkpoint schema and creation for pre-exhaustion handoff."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
import hashlib


@dataclass
class RotationCheckpoint:
    """Immutable rotation checkpoint for fresh-session resume.

    Maximum 32,768 UTF-8 bytes. Contains metadata-only state, no full
    transcripts, logs, diffs, or source bundles.
    """
    schema_version: int = 1
    checkpoint_id: str = ""
    task_id: str = ""
    task_reference: str = ""
    task_sha256: str = ""
    plan_id: str = ""
    plan_reference: str = ""
    plan_sha256: str = ""
    repository_base_commit: str = ""
    repository_base_tree: str = ""
    candidate_branch: str = ""
    candidate_commit: str = ""
    current_step: str = ""
    completed_steps: List[str] = field(default_factory=list)
    validated_facts: List[Dict] = field(default_factory=list)
    unresolved_blockers: List[str] = field(default_factory=list)
    deviations: List[Dict] = field(default_factory=list)
    accepted_delegated_work: List[Dict] = field(default_factory=list)
    artifact_references: List[Dict] = field(default_factory=list)
    routing_status: str = "UNKNOWN"
    validation_status: str = ""
    review_status: str = ""
    next_authorized_action: str = ""
    exactly_once_state: Dict[str, str] = field(default_factory=dict)
    checkpoint_created: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "schema_version": self.schema_version,
            "checkpoint_id": self.checkpoint_id,
            "task_id": self.task_id,
            "task_reference": self.task_reference,
            "task_sha256": self.task_sha256,
            "plan_id": self.plan_id,
            "plan_reference": self.plan_reference,
            "plan_sha256": self.plan_sha256,
            "repository_base_commit": self.repository_base_commit,
            "repository_base_tree": self.repository_base_tree,
            "candidate_branch": self.candidate_branch,
            "candidate_commit": self.candidate_commit,
            "current_step": self.current_step,
            "completed_steps": self.completed_steps,
            "validated_facts": self.validated_facts,
            "unresolved_blockers": self.unresolved_blockers,
            "deviations": self.deviations,
            "accepted_delegated_work": self.accepted_delegated_work,
            "artifact_references": self.artifact_references,
            "routing_status": self.routing_status,
            "validation_status": self.validation_status,
            "review_status": self.review_status,
            "next_authorized_action": self.next_authorized_action,
            "exactly_once_state": self.exactly_once_state,
            "checkpoint_created": self.checkpoint_created,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RotationCheckpoint":
        """Construct from dictionary."""
        return cls(**data)


def validate_checkpoint_size(checkpoint: RotationCheckpoint, max_bytes: int = 32768) -> Tuple[bool, Optional[str]]:
    """Validate that checkpoint does not exceed size limit.

    Args:
        checkpoint: RotationCheckpoint to validate
        max_bytes: maximum allowed size (default 32,768)

    Returns:
        (is_valid, error_message or None)
    """
    checkpoint_json = json.dumps(
        checkpoint.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    checkpoint_bytes = len(checkpoint_json.encode("utf-8"))

    if checkpoint_bytes > max_bytes:
        return False, f"Checkpoint size {checkpoint_bytes} exceeds {max_bytes}-byte limit"

    return True, None


def validate_checkpoint_content(checkpoint: RotationCheckpoint) -> Tuple[bool, List[str]]:
    """Validate checkpoint content for forbidden material.

    Forbidden: raw transcripts, logs, diffs, source bundles, repeated task/plan text, secrets.

    Args:
        checkpoint: RotationCheckpoint to validate

    Returns:
        (is_valid, list of violations)
    """
    violations = []
    checkpoint_json = json.dumps(checkpoint.to_dict(), ensure_ascii=False, sort_keys=True)

    # Check for forbidden indicators (these would suggest raw content inclusion)
    forbidden_patterns = [
        ("raw_transcript", "Raw transcripts"),
        ("raw_log", "Raw logs"),
        ("diff", "Diffs"),
        ("source_code", "Source code"),
        ("password", "Passwords or secrets"),
        ("api_key", "API keys"),
        ("credential", "Credentials"),
    ]

    for pattern, description in forbidden_patterns:
        if pattern.lower() in checkpoint_json.lower():
            violations.append(f"Possible {description} detected in checkpoint")

    return len(violations) == 0, violations


def compute_checkpoint_hash(checkpoint: RotationCheckpoint) -> str:
    """Compute SHA-256 hash of checkpoint (excluding hash field itself).

    Args:
        checkpoint: RotationCheckpoint

    Returns:
        SHA-256 hex string
    """
    checkpoint_dict = checkpoint.to_dict()
    canonical = json.dumps(
        checkpoint_dict, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
