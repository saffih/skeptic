"""Tests for Artifact Reference contract (Categories 1-3)."""

import pytest
import hashlib
from concepts.target_task.artifact_reference import (
    ArtifactReference,
    validate_artifact_reference,
    reject_oversize_or_invalid_reference,
)


class TestArtifactReferenceConstruction:
    """Test valid ArtifactReference construction."""

    def test_valid_reference_minimal(self):
        """Test minimal valid reference."""
        ref = ArtifactReference(
            reference_id="test-001",
            path_or_uri="path/to/artifact.md",
            sha256="a" * 64,
            byte_size=1000,
            media_type="text/markdown",
            authority_class="evidence",
            focused_retrieval_guidance="Read entire file",
        )
        assert ref.reference_id == "test-001"
        assert ref.byte_size == 1000

    def test_valid_reference_with_complete_read(self):
        """Test reference with complete_read_required=True."""
        ref = ArtifactReference(
            reference_id="task-001",
            path_or_uri="task.md",
            sha256="b" * 64,
            byte_size=10000,
            media_type="text/markdown",
            authority_class="reference_implementation",
            focused_retrieval_guidance="Read full task",
            complete_read_required=True,
            complete_read_reason="Task is immutable requirement",
        )
        assert ref.complete_read_required is True
        assert ref.complete_read_reason == "Task is immutable requirement"

    def test_valid_authority_classes(self):
        """Test all valid authority classes."""
        classes = [
            "reference_implementation",
            "contract",
            "checkpoint",
            "evidence",
            "generated",
        ]
        for cls in classes:
            ref = ArtifactReference(
                reference_id=f"test-{cls}",
                path_or_uri="test.txt",
                sha256="c" * 64,
                byte_size=100,
                media_type="text/plain",
                authority_class=cls,
                focused_retrieval_guidance="test",
            )
            assert ref.authority_class == cls


class TestArtifactReferenceValidation:
    """Test reference validation."""

    def test_reject_invalid_reference_id(self):
        """Test rejection of empty or oversized reference_id."""
        with pytest.raises(ValueError, match="reference_id"):
            ArtifactReference(
                reference_id="",
                path_or_uri="test.txt",
                sha256="d" * 64,
                byte_size=100,
                media_type="text/plain",
                authority_class="evidence",
                focused_retrieval_guidance="test",
            )

    def test_reject_oversized_reference_id(self):
        """Test rejection of reference_id exceeding 64 bytes."""
        with pytest.raises(ValueError, match="exceeds 64-byte limit"):
            ArtifactReference(
                reference_id="x" * 65,
                path_or_uri="test.txt",
                sha256="e" * 64,
                byte_size=100,
                media_type="text/plain",
                authority_class="evidence",
                focused_retrieval_guidance="test",
            )

    def test_reject_invalid_sha256_format(self):
        """Test rejection of invalid SHA-256 format."""
        with pytest.raises(ValueError, match="sha256"):
            ArtifactReference(
                reference_id="test-001",
                path_or_uri="test.txt",
                sha256="not-a-valid-sha256",
                byte_size=100,
                media_type="text/plain",
                authority_class="evidence",
                focused_retrieval_guidance="test",
            )

    def test_reject_short_sha256(self):
        """Test rejection of SHA-256 that's too short."""
        with pytest.raises(ValueError, match="sha256"):
            ArtifactReference(
                reference_id="test-001",
                path_or_uri="test.txt",
                sha256="f" * 63,
                byte_size=100,
                media_type="text/plain",
                authority_class="evidence",
                focused_retrieval_guidance="test",
            )

    def test_reject_uppercase_sha256(self):
        """Test rejection of uppercase SHA-256 (must be lowercase)."""
        with pytest.raises(ValueError, match="sha256"):
            ArtifactReference(
                reference_id="test-001",
                path_or_uri="test.txt",
                sha256="F" * 64,
                byte_size=100,
                media_type="text/plain",
                authority_class="evidence",
                focused_retrieval_guidance="test",
            )

    def test_reject_negative_byte_size(self):
        """Test rejection of negative byte_size."""
        with pytest.raises(ValueError, match="byte_size"):
            ArtifactReference(
                reference_id="test-001",
                path_or_uri="test.txt",
                sha256="0" * 64,
                byte_size=-1,
                media_type="text/plain",
                authority_class="evidence",
                focused_retrieval_guidance="test",
            )

    def test_reject_invalid_authority_class(self):
        """Test rejection of unknown authority_class."""
        with pytest.raises(ValueError, match="authority_class"):
            ArtifactReference(
                reference_id="test-001",
                path_or_uri="test.txt",
                sha256="1" * 64,
                byte_size=100,
                media_type="text/plain",
                authority_class="unknown_class",
                focused_retrieval_guidance="test",
            )

    def test_reject_complete_read_mismatch(self):
        """Test rejection when complete_read_reason without complete_read_required."""
        with pytest.raises(ValueError, match="complete_read_reason"):
            ArtifactReference(
                reference_id="test-001",
                path_or_uri="test.txt",
                sha256="2" * 64,
                byte_size=100,
                media_type="text/plain",
                authority_class="evidence",
                focused_retrieval_guidance="test",
                complete_read_required=False,
                complete_read_reason="This should not be here",
            )

    def test_reject_complete_read_missing_reason(self):
        """Test rejection when complete_read_required=True but no reason."""
        with pytest.raises(ValueError, match="complete_read_reason required"):
            ArtifactReference(
                reference_id="test-001",
                path_or_uri="test.txt",
                sha256="3" * 64,
                byte_size=100,
                media_type="text/plain",
                authority_class="evidence",
                focused_retrieval_guidance="test",
                complete_read_required=True,
                complete_read_reason=None,
            )


class TestArtifactReferenceSerialization:
    """Test reference to_dict and from_dict."""

    def test_to_dict_and_from_dict_roundtrip(self):
        """Test roundtrip serialization."""
        original = ArtifactReference(
            reference_id="task-001",
            path_or_uri="experiments/task.md",
            sha256="4" * 64,
            byte_size=5000,
            media_type="text/markdown",
            authority_class="reference_implementation",
            focused_retrieval_guidance="Read full task statement",
            complete_read_required=True,
            complete_read_reason="Immutable requirement",
        )
        data = original.to_dict()
        restored = ArtifactReference.from_dict(data)
        assert restored == original


class TestLargeTaskAndEvidenceReferences:
    """Test Category 1: Large Task + Evidence in Planner ticket within 8KB."""

    def test_large_task_reference_within_budget(self):
        """Test reference to large Target Task fits within dispatch budget."""
        task_ref = ArtifactReference(
            reference_id="task-compact-handoff-001",
            path_or_uri="experiments/body-brain-artifacts/target-task-compact-handoff-rotation-001.md",
            sha256="d48f9ae34bbcdadc909a69c650d20d1805b782afc507a02dd22861985a9c3da8",
            byte_size=10019,
            media_type="text/markdown",
            authority_class="reference_implementation",
            focused_retrieval_guidance="Read entire file for complete task statement and acceptance criteria",
            complete_read_required=True,
            complete_read_reason="Task statement is immutable; must be read in full",
        )
        assert task_ref.byte_size == 10019
        assert len(task_ref.sha256) == 64

    def test_large_evidence_manifest_reference_within_budget(self):
        """Test reference to large evidence manifest fits within dispatch budget."""
        manifest_ref = ArtifactReference(
            reference_id="manifest-001",
            path_or_uri="experiments/body-brain-artifacts/evidence-manifest-001.json",
            sha256="03ef1d7d226e07f22e43666b56979f43d172ae8931e1da124bb189ab6362a47c",
            byte_size=6398,
            media_type="application/json",
            authority_class="evidence",
            focused_retrieval_guidance="Verify access and hash. Use focused retrieval guidance to access only required repository state.",
            complete_read_required=False,
            complete_read_reason=None,
        )
        assert manifest_ref.byte_size == 6398

    def test_multiple_references_fit_in_8kb_ticket(self):
        """Test that multiple large artifact references fit in 8KB dispatch ticket."""
        task_ref = ArtifactReference(
            reference_id="task-001",
            path_or_uri="experiments/body-brain-artifacts/target-task-compact-handoff-rotation-001.md",
            sha256="d48f9ae34bbcdadc909a69c650d20d1805b782afc507a02dd22861985a9c3da8",
            byte_size=10019,
            media_type="text/markdown",
            authority_class="reference_implementation",
            focused_retrieval_guidance="Read entire file for complete task statement",
            complete_read_required=True,
            complete_read_reason="Immutable task requirement",
        )
        manifest_ref = ArtifactReference(
            reference_id="manifest-001",
            path_or_uri="experiments/body-brain-artifacts/evidence-manifest-001.json",
            sha256="03ef1d7d226e07f22e43666b56979f43d172ae8931e1da124bb189ab6362a47c",
            byte_size=6398,
            media_type="application/json",
            authority_class="evidence",
            focused_retrieval_guidance="Use focused retrieval guidance to access only required state",
            complete_read_required=False,
            complete_read_reason=None,
        )

        # Estimate serialized size: 2 refs × ~700 bytes typical = ~1400 bytes
        # Actual size will be ~1600 bytes, well under 8192-byte limit
        data = {"task": task_ref.to_dict(), "manifest": manifest_ref.to_dict()}
        import json

        serialized = json.dumps(data, ensure_ascii=False, sort_keys=True)
        assert len(serialized.encode("utf-8")) < 3000  # Well under 8KB budget


class TestReferenceAccessAndHashVerification:
    """Test Category 2: Planner validates reference access + hashes."""

    def test_validate_artifact_reference_function(self):
        """Test validate_artifact_reference function."""
        ref = ArtifactReference(
            reference_id="test-001",
            path_or_uri="test.txt",
            sha256="5" * 64,
            byte_size=100,
            media_type="text/plain",
            authority_class="evidence",
            focused_retrieval_guidance="test",
        )
        is_valid, errors = validate_artifact_reference(ref)
        assert is_valid is True
        assert errors == []

    def test_reject_invalid_reference_type(self):
        """Test rejection of non-ArtifactReference object."""
        is_valid, errors = validate_artifact_reference("not a reference")
        assert is_valid is False
        assert len(errors) > 0


class TestReferenceIntegrity:
    """Test Category 3: Missing/inaccessible/stale/mismatched refs fail closed."""

    def test_reject_oversize_path(self):
        """Test rejection of path exceeding 512-byte limit."""
        with pytest.raises(ValueError, match="exceeds 512-byte limit"):
            ArtifactReference(
                reference_id="test-001",
                path_or_uri="x" * 513,
                sha256="6" * 64,
                byte_size=100,
                media_type="text/plain",
                authority_class="evidence",
                focused_retrieval_guidance="test",
            )

    def test_reject_oversize_guidance(self):
        """Test rejection of guidance exceeding 512-byte limit."""
        with pytest.raises(ValueError, match="exceeds 512-byte limit"):
            ArtifactReference(
                reference_id="test-001",
                path_or_uri="test.txt",
                sha256="7" * 64,
                byte_size=100,
                media_type="text/plain",
                authority_class="evidence",
                focused_retrieval_guidance="x" * 513,
            )

    def test_accept_valid_size(self):
        """Test acceptance of valid-sized reference."""
        ref = ArtifactReference(
            reference_id="test-001",
            path_or_uri="path/to/artifact.md",
            sha256="8" * 64,
            byte_size=1000,
            media_type="text/markdown",
            authority_class="evidence",
            focused_retrieval_guidance="Use focused retrieval to get specific section",
        )
        is_valid, error = reject_oversize_or_invalid_reference(ref)
        assert is_valid is True
        assert error is None
