"""Tests for checkpoint and resume (Categories 9-13)."""

import pytest
from concepts.target_task.rotation_checkpoint import (
    RotationCheckpoint,
    validate_checkpoint_size,
    validate_checkpoint_content,
)
from concepts.target_task.resume_validator import (
    validate_checkpoint_integrity,
    validate_no_duplicate_execution,
    validate_repository_state_unchanged,
    validate_plan_unchanged,
    validate_resume_comprehensive,
)


class TestCheckpointSizeAndContent:
    """Test Categories 9-10: Checkpoint size cap and content restrictions."""

    def test_checkpoint_within_32kb_limit(self):
        """Test that checkpoint respects 32,768-byte cap."""
        checkpoint = RotationCheckpoint(
            checkpoint_id="ROTATION-001",
            task_id="TT-001",
            task_reference="task.md",
            task_sha256="a" * 64,
            plan_id="PLAN-001-v1",
            plan_reference="plan.md",
            plan_sha256="b" * 64,
            repository_base_commit="abc123",
            repository_base_tree="def456",
            candidate_branch="repair/test",
            candidate_commit="ghi789",
            current_step="PHASE_1",
            completed_steps=["PREFLIGHT"],
        )

        is_valid, error = validate_checkpoint_size(checkpoint, max_bytes=32768)
        assert is_valid is True
        assert error is None

    def test_checkpoint_rejects_oversized(self):
        """Test that oversized checkpoint is rejected."""
        checkpoint = RotationCheckpoint(
            checkpoint_id="ROTATION-001",
            task_id="TT-001",
            task_reference="task.md",
            task_sha256="c" * 64,
            plan_id="PLAN-001-v1",
            plan_reference="plan.md",
            plan_sha256="d" * 64,
            repository_base_commit="abc123",
            repository_base_tree="def456",
            candidate_branch="repair/test",
            candidate_commit="ghi789",
            current_step="PHASE_1",
            completed_steps=["PREFLIGHT"],
            validated_facts=[{"fact": "test fact", "evidence": "x" * 10000}]
            * 100,  # Bloat checkpoint
        )

        is_valid, error = validate_checkpoint_size(checkpoint, max_bytes=1000)  # Tiny limit
        assert is_valid is False
        assert error is not None

    def test_checkpoint_content_validation(self):
        """Test that checkpoint content is validated for forbidden material."""
        checkpoint = RotationCheckpoint(
            checkpoint_id="ROTATION-001",
            task_id="TT-001",
            task_reference="task.md",
            task_sha256="e" * 64,
            plan_id="PLAN-001-v1",
            plan_reference="plan.md",
            plan_sha256="f" * 64,
            repository_base_commit="abc123",
            repository_base_tree="def456",
            candidate_branch="repair/test",
            candidate_commit="ghi789",
            current_step="PHASE_1",
            completed_steps=["PREFLIGHT"],
        )

        is_valid, violations = validate_checkpoint_content(checkpoint)
        # Should pass (no forbidden content)
        assert is_valid is True or len(violations) == 0


class TestResumeValidation:
    """Test Categories 11-13: Fresh resume validation."""

    def test_checkpoint_integrity_validation_passes(self):
        """Test that valid checkpoint passes integrity check."""
        checkpoint = RotationCheckpoint(
            checkpoint_id="ROTATION-001",
            task_id="TT-001",
            task_reference="task.md",
            task_sha256="a" * 64,
            plan_id="PLAN-001-v1",
            plan_reference="plan.md",
            plan_sha256="b" * 64,
            repository_base_commit="abc123",
            repository_base_tree="def456",
            candidate_branch="repair/test",
            candidate_commit="ghi789",
            current_step="PHASE_1",
        )

        is_valid, errors = validate_checkpoint_integrity(checkpoint)
        assert is_valid is True
        assert len(errors) == 0

    def test_reject_checkpoint_missing_task_id(self):
        """Test rejection of checkpoint with missing task_id."""
        checkpoint = RotationCheckpoint(
            checkpoint_id="ROTATION-001",
            task_id="",  # Missing
            task_reference="task.md",
            task_sha256="c" * 64,
            plan_id="PLAN-001-v1",
            plan_reference="plan.md",
            plan_sha256="d" * 64,
        )

        is_valid, errors = validate_checkpoint_integrity(checkpoint)
        assert is_valid is False
        assert any("Task ID" in error for error in errors)

    def test_reject_stale_repository_base(self):
        """Test rejection when repository base has changed."""
        checkpoint = RotationCheckpoint(
            checkpoint_id="ROTATION-001",
            task_id="TT-001",
            task_reference="task.md",
            task_sha256="e" * 64,
            plan_id="PLAN-001-v1",
            plan_reference="plan.md",
            plan_sha256="f" * 64,
            repository_base_commit="old_commit_123",
            repository_base_tree="old_tree_456",
        )

        is_valid, error = validate_repository_state_unchanged(
            checkpoint, "new_commit_789", "old_tree_456"
        )
        assert is_valid is False
        assert error is not None

    def test_reject_changed_plan_hash(self):
        """Test rejection when accepted plan hash has changed."""
        checkpoint = RotationCheckpoint(
            checkpoint_id="ROTATION-001",
            task_id="TT-001",
            task_reference="task.md",
            task_sha256="a" * 64,
            plan_id="PLAN-001-v1",
            plan_reference="plan.md",
            plan_sha256="b" * 64,  # Original hash
        )

        current_plan_sha256 = "c" * 64  # Different hash

        is_valid, error = validate_plan_unchanged(checkpoint, current_plan_sha256)
        assert is_valid is False
        assert error is not None

    def test_reject_duplicate_execution(self):
        """Test rejection of duplicate execution ID."""
        checkpoint = RotationCheckpoint(
            checkpoint_id="ROTATION-001",
            task_id="TT-001",
            task_reference="task.md",
            task_sha256="d" * 64,
            plan_id="PLAN-001-v1",
            plan_reference="plan.md",
            plan_sha256="e" * 64,
            exactly_once_state={"EXEC-001": "2026-07-29T10:00:00"},
        )

        # Try to execute same ID again
        is_valid, error = validate_no_duplicate_execution(checkpoint, "EXEC-001")
        assert is_valid is False
        assert error is not None

    def test_accept_new_execution_id(self):
        """Test acceptance of new execution ID."""
        checkpoint = RotationCheckpoint(
            checkpoint_id="ROTATION-001",
            task_id="TT-001",
            task_reference="task.md",
            task_sha256="f" * 64,
            plan_id="PLAN-001-v1",
            plan_reference="plan.md",
            plan_sha256="a" * 64,
            exactly_once_state={},
        )

        is_valid, error = validate_no_duplicate_execution(checkpoint, "NEW-EXEC-001")
        assert is_valid is True
        assert error is None

    def test_comprehensive_resume_validation_passes(self):
        """Test comprehensive resume validation with all checks passing."""
        checkpoint = RotationCheckpoint(
            checkpoint_id="ROTATION-001",
            task_id="TT-001",
            task_reference="task.md",
            task_sha256="b" * 64,
            plan_id="PLAN-001-v1",
            plan_reference="plan.md",
            plan_sha256="c" * 64,
            repository_base_commit="base_commit",
            repository_base_tree="base_tree",
            exactly_once_state={},
        )

        is_valid, errors = validate_resume_comprehensive(
            checkpoint=checkpoint,
            current_base_commit="base_commit",
            current_base_tree="base_tree",
            current_plan_sha256="c" * 64,
            execution_id="NEW-EXEC-001",
        )

        assert is_valid is True
        assert len(errors) == 0
