"""Resume validator for fresh invocation state checking."""

from typing import Tuple, List, Optional
import hashlib
from concepts.target_task.rotation_checkpoint import RotationCheckpoint


def validate_checkpoint_integrity(checkpoint: RotationCheckpoint) -> Tuple[bool, List[str]]:
    """Validate checkpoint schema, version, and essential fields.

    Returns:
        (is_valid, list of errors)
    """
    errors = []

    if not isinstance(checkpoint, RotationCheckpoint):
        errors.append("Checkpoint is not a RotationCheckpoint instance")
        return False, errors

    if checkpoint.schema_version != 1:
        errors.append(f"Unsupported schema version {checkpoint.schema_version}")

    if not checkpoint.checkpoint_id:
        errors.append("Checkpoint ID missing")
    if not checkpoint.task_id:
        errors.append("Task ID missing")
    if not checkpoint.task_reference:
        errors.append("Task reference missing")
    if not checkpoint.task_sha256:
        errors.append("Task SHA256 missing")
    if not checkpoint.plan_reference:
        errors.append("Plan reference missing")
    if not checkpoint.plan_sha256:
        errors.append("Plan SHA256 missing")

    return len(errors) == 0, errors


def validate_artifact_references_accessible(checkpoint: RotationCheckpoint) -> Tuple[bool, List[str]]:
    """Validate that all artifact references in checkpoint are accessible.

    In a real system, this would attempt file access. For now, check structure.

    Returns:
        (is_valid, list of errors)
    """
    errors = []

    # Check artifact_references list structure
    for i, ref in enumerate(checkpoint.artifact_references):
        if not isinstance(ref, dict):
            errors.append(f"Artifact reference {i} is not a dict")
        else:
            required_fields = {"reference_id", "path", "sha256"}
            missing = required_fields - set(ref.keys())
            if missing:
                errors.append(f"Artifact reference {i} missing fields: {missing}")

    return len(errors) == 0, errors


def validate_no_duplicate_execution(
    checkpoint: RotationCheckpoint, execution_id: str
) -> Tuple[bool, Optional[str]]:
    """Validate that execution_id has not already been executed.

    Uses exactly_once_state registry in checkpoint.

    Returns:
        (is_unique, error_message or None)
    """
    if execution_id in checkpoint.exactly_once_state:
        return False, f"Execution ID {execution_id} already executed at {checkpoint.exactly_once_state[execution_id]}"
    return True, None


def validate_repository_state_unchanged(
    checkpoint: RotationCheckpoint, current_base_commit: str, current_base_tree: str
) -> Tuple[bool, Optional[str]]:
    """Validate that repository base has not changed since checkpoint.

    Args:
        checkpoint: RotationCheckpoint
        current_base_commit: current main branch commit
        current_base_tree: current main branch tree

    Returns:
        (is_valid, error_message or None)
    """
    if checkpoint.repository_base_commit != current_base_commit:
        return (
            False,
            f"Repository base commit changed from {checkpoint.repository_base_commit} to {current_base_commit}",
        )
    if checkpoint.repository_base_tree != current_base_tree:
        return (
            False,
            f"Repository base tree changed from {checkpoint.repository_base_tree} to {current_base_tree}",
        )
    return True, None


def validate_plan_unchanged(
    checkpoint: RotationCheckpoint, current_plan_sha256: str
) -> Tuple[bool, Optional[str]]:
    """Validate that accepted Plan has not changed.

    Args:
        checkpoint: RotationCheckpoint
        current_plan_sha256: SHA-256 of current Plan file

    Returns:
        (is_valid, error_message or None)
    """
    if checkpoint.plan_sha256 != current_plan_sha256:
        return (
            False,
            f"Plan hash changed from {checkpoint.plan_sha256} to {current_plan_sha256}; "
            f"must reject resume and replan",
        )
    return True, None


def validate_resume_comprehensive(
    checkpoint: RotationCheckpoint,
    current_base_commit: str,
    current_base_tree: str,
    current_plan_sha256: str,
    execution_id: str,
) -> Tuple[bool, List[str]]:
    """Comprehensive validation before resuming from checkpoint.

    Args:
        checkpoint: RotationCheckpoint to validate
        current_base_commit: current repository base commit
        current_base_tree: current repository base tree
        current_plan_sha256: SHA-256 of current Plan
        execution_id: unique ID for this execution attempt

    Returns:
        (is_valid, list of errors)
    """
    errors = []

    # Checkpoint integrity
    is_valid, checkpoint_errors = validate_checkpoint_integrity(checkpoint)
    if not is_valid:
        errors.extend(checkpoint_errors)

    # Artifact references accessible
    is_valid, ref_errors = validate_artifact_references_accessible(checkpoint)
    if not is_valid:
        errors.extend(ref_errors)

    # Repository state unchanged
    is_valid, repo_error = validate_repository_state_unchanged(
        checkpoint, current_base_commit, current_base_tree
    )
    if not is_valid:
        errors.append(repo_error)

    # Plan unchanged
    is_valid, plan_error = validate_plan_unchanged(checkpoint, current_plan_sha256)
    if not is_valid:
        errors.append(plan_error)

    # No duplicate execution
    is_valid, dup_error = validate_no_duplicate_execution(checkpoint, execution_id)
    if not is_valid:
        errors.append(dup_error)

    return len(errors) == 0, errors
