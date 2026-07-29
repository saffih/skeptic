"""Detect and handle transport/context failures with deterministic redispatch."""

from typing import Optional, Tuple
from concepts.target_task.artifact_reference import ArtifactReference
from concepts.target_task.dispatch_ticket import DispatchTicket
from concepts.target_task.dispatch_state import FailedDispatchRegistry


class TransportFailure:
    """Represents a transport or context failure."""
    def __init__(self, error_class: str, error_message: str, dispatch_id: str):
        self.error_class = error_class
        self.error_message = error_message
        self.dispatch_id = dispatch_id


def detect_transport_failure(error: Exception, dispatch_id: str) -> Optional[TransportFailure]:
    """Detect if an error qualifies as a transport/context failure.

    Args:
        error: the exception raised
        dispatch_id: the dispatch ID that failed

    Returns:
        TransportFailure if detected, None otherwise
    """
    error_str = str(error).lower()

    # Context exhaustion
    if any(
        phrase in error_str
        for phrase in [
            "context",
            "token",
            "exhausted",
            "overflow",
            "capacity",
            "length",
        ]
    ):
        return TransportFailure(
            error_class="context_exhaustion",
            error_message=str(error),
            dispatch_id=dispatch_id,
        )

    # Network/transport timeout
    if any(
        phrase in error_str
        for phrase in ["timeout", "connection", "network", "transport", "deadline"]
    ):
        return TransportFailure(
            error_class="network_timeout",
            error_message=str(error),
            dispatch_id=dispatch_id,
        )

    # Generic I/O failure
    if any(phrase in error_str for phrase in ["i/o", "io error", "read", "write"]):
        return TransportFailure(
            error_class="io_failure",
            error_message=str(error),
            dispatch_id=dispatch_id,
        )

    return None


def create_redispatch_ticket(
    original_ticket: DispatchTicket,
    new_dispatch_id: str,
    error_evidence_reference: ArtifactReference,
) -> DispatchTicket:
    """Create a redispatch ticket from a failed original ticket.

    Args:
        original_ticket: the original DispatchTicket that failed
        new_dispatch_id: unique new ID for this redispatch
        error_evidence_reference: ArtifactReference to error log/evidence

    Returns:
        New DispatchTicket for redispatch
    """
    # Build objectives for redispatch
    redispatch_objectives = [
        f"Redispatch of {original_ticket.dispatch_id}",
        "Original objective: " + original_ticket.objectives[0]
        if original_ticket.objectives
        else "Complete original work",
    ]

    # Add constraint about recovery
    redispatch_constraints = (
        original_ticket.constraints
        + [
            "This is a redispatch; previous dispatch failed with transport/context error",
            "Do not modify error evidence artifact",
        ]
    )

    # Validation rules for redispatch
    redispatch_validation = (
        original_ticket.validation_rules
        + [
            "Verify original dispatch ID is marked consumed",
            "Confirm no placeholder text from failed attempt",
        ]
    )

    # Create new ticket with same references but new dispatch ID
    return DispatchTicket(
        dispatch_id=new_dispatch_id,
        task_id=original_ticket.task_id,
        task_reference=original_ticket.task_reference,
        evidence_manifest_reference=original_ticket.evidence_manifest_reference,
        plan_reference=original_ticket.plan_reference,
        objectives=redispatch_objectives,
        constraints=redispatch_constraints,
        expected_return_contract=original_ticket.expected_return_contract,
        validation_rules=redispatch_validation,
        terminal_conditions=original_ticket.terminal_conditions,
        context_budget_bytes=original_ticket.context_budget_bytes,
    )


def handle_transport_failure(
    original_ticket: DispatchTicket,
    error: Exception,
    registry: FailedDispatchRegistry,
    error_log_reference: ArtifactReference,
    next_dispatch_id: str,
) -> Tuple[bool, Optional[DispatchTicket], Optional[str]]:
    """Handle a transport failure with deterministic recovery.

    Args:
        original_ticket: the DispatchTicket that failed
        error: the exception that occurred
        registry: FailedDispatchRegistry tracking state
        error_log_reference: ArtifactReference to error evidence
        next_dispatch_id: new unique dispatch ID for redispatch

    Returns:
        (can_continue: bool, redispatch_ticket: DispatchTicket or None, conflict_reason: str or None)

        If can_continue=True and redispatch_ticket is not None: issue one redispatch
        If can_continue=False and conflict_reason is not None: stop with CONFLICT
    """
    original_id = original_ticket.dispatch_id

    # Detect failure type
    failure = detect_transport_failure(error, original_id)
    if not failure:
        return False, None, f"Unrecognized failure type: {type(error).__name__}"

    # Record the failure
    try:
        registry.record_failure(
            dispatch_id=original_id,
            error_class=failure.error_class,
            error_message=failure.error_message,
            original_ticket_reference="original dispatch",
        )
    except ValueError as e:
        return False, None, f"Failed to record dispatch failure: {e}"

    # Check if this is a second same-class failure
    if registry.should_rotate_on_second_failure(failure.error_class):
        return (
            False,
            None,
            f"Second {failure.error_class} failure detected; must rotate to fresh Lead session or return CONFLICT",
        )

    # Create redispatch with new ID
    try:
        redispatch = create_redispatch_ticket(
            original_ticket=original_ticket,
            new_dispatch_id=next_dispatch_id,
            error_evidence_reference=error_log_reference,
        )
    except Exception as e:
        return False, None, f"Failed to create redispatch ticket: {e}"

    return True, redispatch, None
