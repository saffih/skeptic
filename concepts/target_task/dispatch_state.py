"""Dispatch state tracking and failed ID registry for transport failure recovery."""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Set, Dict, List
from datetime import datetime


class DispatchState(Enum):
    """State machine for dispatch lifecycle."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RECOVERED = "RECOVERED"


@dataclass
class FailedDispatch:
    """Record of a failed dispatch."""
    dispatch_id: str
    error_class: str  # e.g., "context_exhaustion", "network_timeout"
    error_message: str
    original_ticket_reference: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    redispatch_attempt_count: int = 0
    is_consumed: bool = True  # Mark so it cannot be reused


@dataclass
class FailedDispatchRegistry:
    """Track consumed failed dispatch IDs to prevent reuse and limit redispatches.

    Rules:
    - A failed dispatch ID is marked consumed and cannot be reused
    - One redispatch per transport failure with a new unique ID
    - Second same-class failure triggers rotation or CONFLICT
    """
    failed_dispatches: Dict[str, FailedDispatch] = field(default_factory=dict)
    dispatch_id_to_error_class: Dict[str, str] = field(default_factory=dict)

    def record_failure(
        self,
        dispatch_id: str,
        error_class: str,
        error_message: str,
        original_ticket_reference: str,
    ) -> None:
        """Record a dispatch failure.

        Args:
            dispatch_id: the failed dispatch ID
            error_class: category of error (e.g., "context_exhaustion")
            error_message: error details
            original_ticket_reference: reference to the original ticket
        """
        if dispatch_id in self.failed_dispatches:
            raise ValueError(f"Dispatch {dispatch_id} already recorded as failed")

        failed = FailedDispatch(
            dispatch_id=dispatch_id,
            error_class=error_class,
            error_message=error_message,
            original_ticket_reference=original_ticket_reference,
        )
        self.failed_dispatches[dispatch_id] = failed
        self.dispatch_id_to_error_class[dispatch_id] = error_class

    def is_consumed(self, dispatch_id: str) -> bool:
        """Check if dispatch ID has been consumed by a prior failure."""
        return dispatch_id in self.failed_dispatches

    def get_failure(self, dispatch_id: str) -> Optional[FailedDispatch]:
        """Retrieve a failed dispatch record."""
        return self.failed_dispatches.get(dispatch_id)

    def count_failures_by_class(self, error_class: str) -> int:
        """Count how many failures of a given error class."""
        return sum(
            1
            for dispatch in self.failed_dispatches.values()
            if dispatch.error_class == error_class
        )

    def should_rotate_on_second_failure(self, error_class: str) -> bool:
        """Determine if a second same-class failure should trigger rotation.

        Rule: second same-class failure → rotation/conflict (do not redispatch again).
        """
        return self.count_failures_by_class(error_class) >= 1  # Already have 1, this would be 2


def mark_dispatch_id_consumed(dispatch_id: str, registry: FailedDispatchRegistry) -> bool:
    """Mark a dispatch ID as consumed (cannot be reused).

    Returns:
        True if successfully marked, False if already consumed
    """
    if registry.is_consumed(dispatch_id):
        return False
    registry.failed_dispatches[dispatch_id] = FailedDispatch(
        dispatch_id=dispatch_id,
        error_class="consumed",
        error_message="ID consumed by prior dispatch or recovery",
        original_ticket_reference="N/A",
    )
    return True
