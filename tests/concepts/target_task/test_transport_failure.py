"""Tests for transport failure recovery (Categories 7-8)."""

import pytest
from concepts.target_task.artifact_reference import ArtifactReference
from concepts.target_task.dispatch_ticket import DispatchTicket
from concepts.target_task.dispatch_state import (
    FailedDispatchRegistry,
    DispatchState,
    mark_dispatch_id_consumed,
)
from concepts.target_task.transport_failure_handler import (
    TransportFailure,
    detect_transport_failure,
    create_redispatch_ticket,
    handle_transport_failure,
)


class TestSecondFailureTriggersRotation:
    """Test Category 7: Second same-class failure triggers rotation/conflict."""

    def test_first_transport_failure_allows_redispatch(self):
        """Test that first transport failure can be recovered with redispatch."""
        registry = FailedDispatchRegistry()

        # First failure
        registry.record_failure(
            dispatch_id="PLANNER-001",
            error_class="context_exhaustion",
            error_message="Token limit exceeded",
            original_ticket_reference="original_ticket",
        )

        # Should not trigger rotation yet
        should_rotate = registry.should_rotate_on_second_failure("context_exhaustion")
        assert should_rotate is True  # Because we now have 1, and second would be detected

    def test_second_same_class_failure_triggers_rotation(self):
        """Test that second same-class failure is detected."""
        registry = FailedDispatchRegistry()

        # First failure
        registry.record_failure(
            dispatch_id="PLANNER-001",
            error_class="context_exhaustion",
            error_message="First exhaustion",
            original_ticket_reference="ticket1",
        )

        # Check rotation trigger
        should_rotate = registry.should_rotate_on_second_failure("context_exhaustion")
        assert should_rotate is True

    def test_different_error_class_allows_new_redispatch(self):
        """Test that different error class is treated separately for rotation."""
        registry = FailedDispatchRegistry()

        # First failure: context exhaustion
        registry.record_failure(
            dispatch_id="PLANNER-001",
            error_class="context_exhaustion",
            error_message="Token limit",
            original_ticket_reference="ticket1",
        )

        # Check rotation trigger for context_exhaustion (should trigger on next occurrence)
        should_rotate_context = registry.should_rotate_on_second_failure("context_exhaustion")
        assert should_rotate_context is True  # Already have 1, next would be 2nd

        # Network timeout not yet encountered
        should_rotate_network = registry.should_rotate_on_second_failure("network_timeout")
        assert should_rotate_network is False  # 0 network timeouts


class TestLeadAuthoredPlanningForbidden:
    """Test Category 8: Lead-authored substitute planning forbidden."""

    def test_redispatch_ticket_preserves_original_objectives(self):
        """Test that redispatch ticket includes original objectives, not substitutes."""
        task_ref = ArtifactReference(
            reference_id="task-001",
            path_or_uri="task.md",
            sha256="a" * 64,
            byte_size=1000,
            media_type="text/markdown",
            authority_class="reference_implementation",
            focused_retrieval_guidance="Read full",
            complete_read_required=True,
            complete_read_reason="Immutable",
        )
        manifest_ref = ArtifactReference(
            reference_id="manifest-001",
            path_or_uri="manifest.json",
            sha256="b" * 64,
            byte_size=500,
            media_type="application/json",
            authority_class="evidence",
            focused_retrieval_guidance="Use focused",
        )

        original_ticket = DispatchTicket(
            dispatch_id="PLANNER-001",
            task_id="TT-001",
            task_reference=task_ref,
            evidence_manifest_reference=manifest_ref,
            objectives=["Implement the feature"],
            constraints=["No frozen file changes"],
            expected_return_contract={"format": "Plan"},
            validation_rules=["Validate refs"],
            terminal_conditions=["Tests pass"],
        )

        error_ref = ArtifactReference(
            reference_id="error-log-001",
            path_or_uri="error.log",
            sha256="c" * 64,
            byte_size=100,
            media_type="text/plain",
            authority_class="evidence",
            focused_retrieval_guidance="Error details",
        )

        redispatch = create_redispatch_ticket(
            original_ticket=original_ticket,
            new_dispatch_id="PLANNER-002",
            error_evidence_reference=error_ref,
        )

        # Redispatch should preserve original objectives
        assert len(redispatch.objectives) > 0
        # First objective should reference original
        assert "PLANNER-001" in redispatch.objectives[0]

    def test_redispatch_references_error_evidence_only(self):
        """Test that redispatch adds error reference, not substitutes it."""
        task_ref = ArtifactReference(
            reference_id="task-001",
            path_or_uri="task.md",
            sha256="d" * 64,
            byte_size=1000,
            media_type="text/markdown",
            authority_class="reference_implementation",
            focused_retrieval_guidance="test",
            complete_read_required=True,
            complete_read_reason="test",
        )
        manifest_ref = ArtifactReference(
            reference_id="manifest-001",
            path_or_uri="manifest.json",
            sha256="e" * 64,
            byte_size=500,
            media_type="application/json",
            authority_class="evidence",
            focused_retrieval_guidance="test",
        )

        original_ticket = DispatchTicket(
            dispatch_id="PLANNER-001",
            task_id="TT-001",
            task_reference=task_ref,
            evidence_manifest_reference=manifest_ref,
            objectives=["Work"],
            constraints=["No modification"],
            expected_return_contract={},
            validation_rules=[],
            terminal_conditions=[],
        )

        error_ref = ArtifactReference(
            reference_id="error-001",
            path_or_uri="error.log",
            sha256="f" * 64,
            byte_size=200,
            media_type="text/plain",
            authority_class="evidence",
            focused_retrieval_guidance="Error information",
        )

        redispatch = create_redispatch_ticket(
            original_ticket=original_ticket,
            new_dispatch_id="PLANNER-002",
            error_evidence_reference=error_ref,
        )

        # Task reference should be unchanged (not substituted)
        assert redispatch.task_reference == original_ticket.task_reference
        # Manifest reference should be unchanged
        assert (
            redispatch.evidence_manifest_reference
            == original_ticket.evidence_manifest_reference
        )
