"""Helper to construct compact Planner dispatch tickets."""

import json
from typing import Optional, List, Dict
from concepts.target_task.artifact_reference import ArtifactReference
from concepts.target_task.dispatch_ticket import DispatchTicket, validate_ticket_over_wire


def build_planner_ticket(
    dispatch_id: str,
    task_id: str,
    task_reference: ArtifactReference,
    evidence_manifest_reference: ArtifactReference,
    objectives: List[str],
    constraints: List[str],
    expected_return_contract: Dict,
    validation_rules: List[str],
    terminal_conditions: List[str],
    plan_reference: Optional[ArtifactReference] = None,
    context_budget_bytes: int = 8192,
) -> DispatchTicket:
    """Build a compact Planner dispatch ticket.

    Args:
        dispatch_id: unique dispatch identifier
        task_id: target task ID
        task_reference: ArtifactReference to Target Task
        evidence_manifest_reference: ArtifactReference to evidence manifest
        objectives: list of bounded objectives
        constraints: list of constraints
        expected_return_contract: dict with output requirements
        validation_rules: list of validation requirements
        terminal_conditions: list of stop/replan conditions
        plan_reference: optional ArtifactReference to previous plan (for revision)
        context_budget_bytes: ticket size budget (default 8192)

    Returns:
        DispatchTicket

    Raises:
        ValueError: if validation fails or ticket oversized
    """
    # Construct ticket
    ticket = DispatchTicket(
        dispatch_id=dispatch_id,
        task_id=task_id,
        task_reference=task_reference,
        evidence_manifest_reference=evidence_manifest_reference,
        plan_reference=plan_reference,
        objectives=objectives,
        constraints=constraints,
        expected_return_contract=expected_return_contract,
        validation_rules=validation_rules,
        terminal_conditions=terminal_conditions,
        context_budget_bytes=context_budget_bytes,
    )

    # Serialize and check size
    ticket_dict = ticket.to_dict()
    ticket_json = json.dumps(
        ticket_dict, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    ticket_bytes = ticket_json.encode("utf-8")

    if len(ticket_bytes) > context_budget_bytes:
        raise ValueError(
            f"Ticket size {len(ticket_bytes)} exceeds budget {context_budget_bytes} bytes"
        )

    # Validate structure
    is_valid, errors = validate_ticket_over_wire(ticket_bytes, context_budget_bytes)
    if not is_valid:
        raise ValueError(f"Ticket validation failed: {'; '.join(errors)}")

    return ticket


def ticket_to_json_bytes(ticket: DispatchTicket) -> bytes:
    """Convert ticket to canonical JSON bytes."""
    ticket_dict = ticket.to_dict()
    return (
        json.dumps(ticket_dict, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")
