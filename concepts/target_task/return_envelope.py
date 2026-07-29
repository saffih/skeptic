"""Compact return envelope for artifact-first reporting."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
import json
from concepts.target_task.artifact_reference import ArtifactReference


@dataclass
class CompactReturn:
    """Compact return envelope for agent completion (max 4,096 bytes).

    Contains only references, status, findings, and blockers. No embedded
    artifact bodies, plans, or logs.
    """
    status: str  # "SUCCESS", "CONFLICT", "ROTATION_REQUIRED"
    dispatch_id: str
    task_id: str
    verdict: str  # "DONE", "CONFLICT", "ROTATION_REQUIRED"
    plan_reference: Optional[ArtifactReference] = None
    plan_sha256: Optional[str] = None
    checkpoint_reference: Optional[ArtifactReference] = None
    material_findings: List[str] = field(default_factory=list)
    unresolved_blockers: List[str] = field(default_factory=list)
    retrieval_guidance: List[str] = field(default_factory=list)
    artifact_references: List[ArtifactReference] = field(default_factory=list)
    validation_status: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status,
            "dispatch_id": self.dispatch_id,
            "task_id": self.task_id,
            "verdict": self.verdict,
            "plan_reference": self.plan_reference.to_dict() if self.plan_reference else None,
            "plan_sha256": self.plan_sha256,
            "checkpoint_reference": self.checkpoint_reference.to_dict()
            if self.checkpoint_reference
            else None,
            "material_findings": self.material_findings,
            "unresolved_blockers": self.unresolved_blockers,
            "retrieval_guidance": self.retrieval_guidance,
            "artifact_references": [ref.to_dict() for ref in self.artifact_references],
            "validation_status": self.validation_status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CompactReturn":
        """Construct from dictionary."""
        plan_ref = (
            ArtifactReference.from_dict(data["plan_reference"])
            if data.get("plan_reference")
            else None
        )
        checkpoint_ref = (
            ArtifactReference.from_dict(data["checkpoint_reference"])
            if data.get("checkpoint_reference")
            else None
        )
        artifact_refs = [
            ArtifactReference.from_dict(ref) for ref in data.get("artifact_references", [])
        ]
        return cls(
            status=data["status"],
            dispatch_id=data["dispatch_id"],
            task_id=data["task_id"],
            verdict=data["verdict"],
            plan_reference=plan_ref,
            plan_sha256=data.get("plan_sha256"),
            checkpoint_reference=checkpoint_ref,
            material_findings=data.get("material_findings", []),
            unresolved_blockers=data.get("unresolved_blockers", []),
            retrieval_guidance=data.get("retrieval_guidance", []),
            artifact_references=artifact_refs,
            validation_status=data.get("validation_status", ""),
        )


def validate_compact_return(ret: CompactReturn, max_bytes: int = 4096) -> tuple[bool, List[str]]:
    """Validate compact return for correctness and size.

    Args:
        ret: CompactReturn to validate
        max_bytes: maximum return size (default 4096)

    Returns:
        (is_valid, list of errors)
    """
    errors = []

    # Size check
    ret_json = json.dumps(ret.to_dict(), ensure_ascii=False, sort_keys=True)
    ret_bytes = len(ret_json.encode("utf-8"))
    if ret_bytes > max_bytes:
        errors.append(f"Return size {ret_bytes} exceeds {max_bytes}-byte limit")

    # Blocker preservation check
    if ret.verdict in ["CONFLICT", "ROTATION_REQUIRED"] and not ret.unresolved_blockers:
        errors.append(
            f"Return verdict is {ret.verdict} but unresolved_blockers is empty; "
            f"material blocker must be listed"
        )

    # Status consistency
    if ret.status != ret.verdict:
        # Allow mismatch for now (can be intentional)
        pass

    return len(errors) == 0, errors


def reject_return_concealing_blockers(
    ret: CompactReturn, verdict: str
) -> tuple[bool, Optional[str]]:
    """Reject return if it conceals material blockers.

    Args:
        ret: CompactReturn to check
        verdict: expected verdict (e.g., "CONFLICT")

    Returns:
        (is_valid, error_message or None)
    """
    if verdict in ["CONFLICT", "ROTATION_REQUIRED"]:
        if not ret.unresolved_blockers:
            return (
                False,
                f"Return claims {verdict} but lists no unresolved_blockers; blocker is concealed",
            )
    return True, None
