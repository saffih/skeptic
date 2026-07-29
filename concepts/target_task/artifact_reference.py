"""Provider-neutral artifact reference contract for cross-agent handoff."""

from dataclasses import dataclass, field
from typing import Optional
import re


@dataclass(frozen=True)
class ArtifactReference:
    """Immutable reference to an artifact with integrity and retrieval metadata.

    Carries enough information to verify identity, accessibility, integrity,
    authority, size, media type, and retrieval conditions without requiring
    automatic inline expansion.
    """
    reference_id: str
    path_or_uri: str
    sha256: str
    byte_size: int
    media_type: str  # e.g., "text/markdown", "application/json", "text/x-python"
    authority_class: str  # e.g., "reference_implementation", "contract", "checkpoint", "evidence", "generated"
    focused_retrieval_guidance: str
    complete_read_required: bool = False
    complete_read_reason: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate reference fields at construction."""
        # Identity validation
        if not self.reference_id or not isinstance(self.reference_id, str):
            raise ValueError("reference_id must be non-empty string")
        if len(self.reference_id.encode("utf-8")) > 64:
            raise ValueError("reference_id exceeds 64-byte limit")

        # Path/URI validation
        if not self.path_or_uri or not isinstance(self.path_or_uri, str):
            raise ValueError("path_or_uri must be non-empty string")
        if len(self.path_or_uri.encode("utf-8")) > 512:
            raise ValueError("path_or_uri exceeds 512-byte limit")

        # SHA-256 validation
        if not isinstance(self.sha256, str) or not _is_valid_sha256(self.sha256):
            raise ValueError("sha256 must be lowercase hex string (64 chars)")

        # Size validation
        if not isinstance(self.byte_size, int) or self.byte_size < 0:
            raise ValueError("byte_size must be non-negative integer")

        # Authority class validation
        valid_classes = {
            "reference_implementation",
            "contract",
            "checkpoint",
            "evidence",
            "generated",
        }
        if self.authority_class not in valid_classes:
            raise ValueError(
                f"authority_class must be one of {valid_classes}, got {self.authority_class}"
            )

        # Media type validation
        if not self.media_type or not isinstance(self.media_type, str):
            raise ValueError("media_type must be non-empty string")
        if len(self.media_type.encode("utf-8")) > 256:
            raise ValueError("media_type exceeds 256-byte limit")

        # Focused retrieval guidance validation
        if not self.focused_retrieval_guidance or not isinstance(
            self.focused_retrieval_guidance, str
        ):
            raise ValueError("focused_retrieval_guidance must be non-empty string")
        if len(self.focused_retrieval_guidance.encode("utf-8")) > 512:
            raise ValueError("focused_retrieval_guidance exceeds 512-byte limit")

        # Complete read validation
        if self.complete_read_required and not self.complete_read_reason:
            raise ValueError(
                "complete_read_reason required when complete_read_required is True"
            )
        if not self.complete_read_required and self.complete_read_reason:
            raise ValueError(
                "complete_read_reason must be None when complete_read_required is False"
            )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "reference_id": self.reference_id,
            "path_or_uri": self.path_or_uri,
            "sha256": self.sha256,
            "byte_size": self.byte_size,
            "media_type": self.media_type,
            "authority_class": self.authority_class,
            "focused_retrieval_guidance": self.focused_retrieval_guidance,
            "complete_read_required": self.complete_read_required,
            "complete_read_reason": self.complete_read_reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ArtifactReference":
        """Construct from dictionary."""
        return cls(**data)


def _is_valid_sha256(value: str) -> bool:
    """Check if value is a valid lowercase hex SHA-256 (64 chars)."""
    if not isinstance(value, str):
        return False
    return bool(re.match(r"^[0-9a-f]{64}$", value))


def validate_artifact_reference(ref: ArtifactReference) -> tuple[bool, list[str]]:
    """Validate an ArtifactReference for correctness.

    Returns:
        (bool: is_valid, list: errors)
    """
    errors = []

    if not isinstance(ref, ArtifactReference):
        errors.append("Not an ArtifactReference instance")
        return False, errors

    # All validation happens in __post_init__, so if we got here, it's valid
    # This function exists for explicit external validation
    return True, []


def reject_oversize_or_invalid_reference(
    ref: ArtifactReference, max_bytes: int = 512
) -> tuple[bool, Optional[str]]:
    """Reject if reference or guidance exceeds size limits.

    Args:
        ref: ArtifactReference to check
        max_bytes: maximum path length (default 512)

    Returns:
        (bool: is_valid, str: error_reason or None)
    """
    if len(ref.path_or_uri.encode("utf-8")) > max_bytes:
        return False, f"path_or_uri exceeds {max_bytes}-byte limit"
    if len(ref.focused_retrieval_guidance.encode("utf-8")) > 512:
        return False, "focused_retrieval_guidance exceeds 512-byte limit"
    return True, None
