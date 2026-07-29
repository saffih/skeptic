"""Compact dispatch ticket schema for Planner and bounded model agents."""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
import json
from concepts.target_task.artifact_reference import ArtifactReference


@dataclass
class DispatchTicket:
    """Immutable dispatch ticket for Planner or bounded agent.

    Maximum 8,192 UTF-8 bytes. Contains only references and metadata, no
    embedded artifact bodies or plans.
    """
    dispatch_id: str
    task_id: str
    task_reference: ArtifactReference
    evidence_manifest_reference: ArtifactReference
    objectives: List[str]
    constraints: List[str]
    expected_return_contract: Dict
    validation_rules: List[str]
    terminal_conditions: List[str]
    plan_reference: Optional[ArtifactReference] = None
    context_budget_bytes: int = 8192

    def __post_init__(self) -> None:
        """Validate ticket structure."""
        # Dispatch ID validation
        if not self.dispatch_id or not isinstance(self.dispatch_id, str):
            raise ValueError("dispatch_id must be non-empty string")
        if len(self.dispatch_id.encode("utf-8")) > 64:
            raise ValueError("dispatch_id exceeds 64-byte limit")

        # Task ID validation
        if not self.task_id or not isinstance(self.task_id, str):
            raise ValueError("task_id must be non-empty string")

        # Reference validation
        if not isinstance(self.task_reference, ArtifactReference):
            raise ValueError("task_reference must be ArtifactReference")
        if not isinstance(self.evidence_manifest_reference, ArtifactReference):
            raise ValueError("evidence_manifest_reference must be ArtifactReference")
        if self.plan_reference is not None and not isinstance(
            self.plan_reference, ArtifactReference
        ):
            raise ValueError("plan_reference must be ArtifactReference or None")

        # Objectives and constraints validation
        if not self.objectives or not isinstance(self.objectives, list):
            raise ValueError("objectives must be non-empty list")
        if not self.constraints or not isinstance(self.constraints, list):
            raise ValueError("constraints must be non-empty list")

        for obj in self.objectives:
            if not isinstance(obj, str) or len(obj) == 0:
                raise ValueError("each objective must be non-empty string")

        for constr in self.constraints:
            if not isinstance(constr, str) or len(constr) == 0:
                raise ValueError("each constraint must be non-empty string")

        # Return contract validation
        if not isinstance(self.expected_return_contract, dict):
            raise ValueError("expected_return_contract must be dict")

        # Validation rules and terminal conditions
        if not isinstance(self.validation_rules, list):
            raise ValueError("validation_rules must be list")
        if not isinstance(self.terminal_conditions, list):
            raise ValueError("terminal_conditions must be list")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "dispatch_id": self.dispatch_id,
            "task_id": self.task_id,
            "task_reference": self.task_reference.to_dict(),
            "evidence_manifest_reference": self.evidence_manifest_reference.to_dict(),
            "plan_reference": self.plan_reference.to_dict()
            if self.plan_reference
            else None,
            "objectives": self.objectives,
            "constraints": self.constraints,
            "expected_return_contract": self.expected_return_contract,
            "validation_rules": self.validation_rules,
            "terminal_conditions": self.terminal_conditions,
            "context_budget_bytes": self.context_budget_bytes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DispatchTicket":
        """Construct from dictionary."""
        task_ref = ArtifactReference.from_dict(data["task_reference"])
        manifest_ref = ArtifactReference.from_dict(
            data["evidence_manifest_reference"]
        )
        plan_ref = (
            ArtifactReference.from_dict(data["plan_reference"])
            if data.get("plan_reference")
            else None
        )
        return cls(
            dispatch_id=data["dispatch_id"],
            task_id=data["task_id"],
            task_reference=task_ref,
            evidence_manifest_reference=manifest_ref,
            plan_reference=plan_ref,
            objectives=data["objectives"],
            constraints=data["constraints"],
            expected_return_contract=data["expected_return_contract"],
            validation_rules=data["validation_rules"],
            terminal_conditions=data["terminal_conditions"],
            context_budget_bytes=data.get("context_budget_bytes", 8192),
        )


def validate_dispatch_ticket(ticket: DispatchTicket) -> tuple[bool, List[str]]:
    """Validate a DispatchTicket.

    Returns:
        (bool: is_valid, list: errors)
    """
    errors = []

    if not isinstance(ticket, DispatchTicket):
        errors.append("Not a DispatchTicket instance")
        return False, errors

    # All validation happens in __post_init__, so if we got here, it's valid
    return True, errors


def validate_ticket_over_wire(
    ticket_bytes: bytes, max_bytes: int = 8192
) -> tuple[bool, List[str]]:
    """Validate raw ticket bytes for size and well-formedness.

    Returns:
        (bool: is_valid, list: errors)
    """
    errors = []

    if len(ticket_bytes) > max_bytes:
        errors.append(f"Ticket size {len(ticket_bytes)} exceeds {max_bytes}-byte limit")

    # Try to parse as JSON
    try:
        data = json.loads(ticket_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        errors.append(f"Ticket is not valid JSON: {e}")
        return False, errors

    # Check for embedded bodies (catch common red flags)
    ticket_str = json.dumps(data, ensure_ascii=False)
    forbidden_indicators = [
        '"plan"',  # Large plans should not be inline
        '"code"',  # Source code should not be inline
        '"transcript"',  # Transcripts should not be inline
        '"log"',  # Logs should not be inline
        '"diff"',  # Diffs should not be inline
    ]

    for indicator in forbidden_indicators:
        if indicator in ticket_str and len(ticket_str) > 2000:
            errors.append(
                f"Possible embedded body detected ({indicator}); use ArtifactReference instead"
            )

    # Validate required fields exist
    required_fields = {
        "dispatch_id",
        "task_id",
        "task_reference",
        "evidence_manifest_reference",
        "objectives",
        "constraints",
        "expected_return_contract",
        "validation_rules",
        "terminal_conditions",
    }
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors
    return True, []


def reject_malformed_or_oversized_ticket(
    ticket_bytes: bytes, max_bytes: int = 8192
) -> tuple[bool, Optional[str]]:
    """Reject ticket if oversized, malformed, or contains embedded bodies.

    Returns:
        (bool: is_valid, str: error_reason or None)
    """
    is_valid, errors = validate_ticket_over_wire(ticket_bytes, max_bytes)
    if not is_valid:
        return False, "; ".join(errors)
    return True, None
