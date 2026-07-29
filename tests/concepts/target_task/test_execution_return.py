"""Tests for execution and compact returns (Categories 14-17)."""

import pytest
from concepts.target_task.artifact_reference import ArtifactReference
from concepts.target_task.return_envelope import (
    CompactReturn,
    validate_compact_return,
    reject_return_concealing_blockers,
)


class TestCompactReturn:
    """Test Categories 14-17: Execution, returns, regression."""

    def test_compact_return_success_with_plan_reference(self):
        """Test successful return with plan reference."""
        plan_ref = ArtifactReference(
            reference_id="plan-001-v1",
            path_or_uri="plan.md",
            sha256="a" * 64,
            byte_size=29049,
            media_type="text/markdown",
            authority_class="generated",
            focused_retrieval_guidance="Implementation plan",
        )

        ret = CompactReturn(
            status="SUCCESS",
            dispatch_id="PLANNER-002",
            task_id="TT-001",
            verdict="DONE",
            plan_reference=plan_ref,
            plan_sha256="a" * 64,
            material_findings=["Plan covers all 7 outcomes"],
            unresolved_blockers=[],
            validation_status="PASSED",
        )

        is_valid, errors = validate_compact_return(ret)
        assert is_valid is True

    def test_compact_return_conflict_requires_blocker(self):
        """Test that CONFLICT verdict requires unresolved_blockers."""
        ret = CompactReturn(
            status="CONFLICT",
            dispatch_id="PLANNER-001",
            task_id="TT-001",
            verdict="CONFLICT",
            material_findings=["Something went wrong"],
            unresolved_blockers=[],  # Missing blocker
            validation_status="FAILED",
        )

        is_valid, error = reject_return_concealing_blockers(ret, verdict="CONFLICT")
        assert is_valid is False
        assert error is not None

    def test_compact_return_conflict_with_blocker_passes(self):
        """Test that CONFLICT with blocker is valid."""
        ret = CompactReturn(
            status="CONFLICT",
            dispatch_id="PLANNER-001",
            task_id="TT-001",
            verdict="CONFLICT",
            material_findings=["Transport failure"],
            unresolved_blockers=["Second same-class failure detected"],
            validation_status="FAILED",
        )

        is_valid, error = reject_return_concealing_blockers(ret, verdict="CONFLICT")
        assert is_valid is True
        assert error is None

    def test_compact_return_within_4kb_budget(self):
        """Test that return fits within 4KB budget."""
        ret = CompactReturn(
            status="SUCCESS",
            dispatch_id="PLANNER-002",
            task_id="TT-001",
            verdict="DONE",
            material_findings=["All phases complete"],
            unresolved_blockers=[],
            retrieval_guidance=["See plan artifact for implementation details"],
            validation_status="PASSED",
        )

        is_valid, errors = validate_compact_return(ret, max_bytes=4096)
        assert is_valid is True

    def test_rotation_required_with_checkpoint_reference(self):
        """Test ROTATION_REQUIRED return with checkpoint reference."""
        checkpoint_ref = ArtifactReference(
            reference_id="checkpoint-001",
            path_or_uri="checkpoint.json",
            sha256="b" * 64,
            byte_size=4225,
            media_type="application/json",
            authority_class="checkpoint",
            focused_retrieval_guidance="Load checkpoint; validate schema/size/hashes before resume",
        )

        ret = CompactReturn(
            status="ROTATION_REQUIRED",
            dispatch_id="PLANNER-002",
            task_id="TT-001",
            verdict="ROTATION_REQUIRED",
            checkpoint_reference=checkpoint_ref,
            material_findings=["Context reserve insufficient for remaining phases"],
            unresolved_blockers=["Context pressure exceeds safe completion threshold"],
            retrieval_guidance=["Use checkpoint reference to continue in fresh Lead session"],
            validation_status="CHECKPOINT_CREATED",
        )

        is_valid, errors = validate_compact_return(ret)
        assert is_valid is True

    def test_compact_return_preserves_blockers(self):
        """Test that compact return preserves all blockers."""
        blockers = [
            "First blocker: missing file",
            "Second blocker: test failed",
            "Third blocker: hash mismatch",
        ]

        ret = CompactReturn(
            status="CONFLICT",
            dispatch_id="PLANNER-001",
            task_id="TT-001",
            verdict="CONFLICT",
            material_findings=["Multiple issues detected"],
            unresolved_blockers=blockers,
            validation_status="MULTIPLE_FAILURES",
        )

        assert ret.unresolved_blockers == blockers
        is_valid, errors = validate_compact_return(ret)
        assert is_valid is True
