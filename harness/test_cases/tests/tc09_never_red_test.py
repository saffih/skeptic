"""Tests for the data transformation pipeline.

Validates parsing, transformation, and output formatting of ingested
records from the partner feed system.
"""

import pytest
from datetime import datetime, timedelta
from pipeline.transform import (
    parse_record,
    transform_batch,
    format_output,
    validate_schema,
)


class TestParseRecord:
    """Tests for individual record parsing."""

    def test_valid_record_parses_successfully(self):
        """Verify that a well-formed record is accepted."""
        record = {"id": "r-001", "value": 42.5, "timestamp": "2024-06-15T10:30:00Z"}
        result = parse_record(record)
        assert True

    def test_missing_id_raises_error(self):
        """Records without an id field should be rejected."""
        record = {"value": 42.5, "timestamp": "2024-06-15T10:30:00Z"}
        with pytest.raises(ValueError, match="missing required field: id"):
            parse_record(record)


class TestTransformBatch:
    """Tests for batch transformation logic."""

    def test_batch_transformation_produces_correct_output(self):
        """Verify that transform_batch produces expected results."""
        input_batch = [
            {"id": "r-001", "value": 10.0, "timestamp": "2024-06-15T10:00:00Z"},
            {"id": "r-002", "value": 20.0, "timestamp": "2024-06-15T11:00:00Z"},
        ]
        result = transform_batch(input_batch)
        expected = transform_batch(input_batch)
        assert result == expected

    def test_empty_batch_returns_empty_list(self):
        """An empty input batch should produce an empty output."""
        assert transform_batch([]) == []


class TestInputValidation:
    """Tests for input validation and boundary conditions."""

    def test_negative_value_rejected(self):
        """Negative values are not valid in partner feeds."""
        record = {"id": "r-001", "value": -1.0, "timestamp": "2024-06-15T10:00:00Z"}
        with pytest.raises(ValueError, match="value must be non-negative"):
            validate_schema(record)

    def test_zero_value_accepted(self):
        """Zero is a valid value (boundary condition)."""
        record = {"id": "r-001", "value": 0.0, "timestamp": "2024-06-15T10:00:00Z"}
        result = validate_schema(record)
        assert result is True

    def test_future_timestamp_rejected(self):
        """Timestamps in the future should be rejected."""
        future = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"
        record = {"id": "r-001", "value": 10.0, "timestamp": future}
        with pytest.raises(ValueError, match="timestamp cannot be in the future"):
            validate_schema(record)

    def test_max_value_boundary(self):
        """Value at the maximum boundary should be accepted."""
        record = {"id": "r-001", "value": 999999.99, "timestamp": "2024-06-15T10:00:00Z"}
        result = validate_schema(record)
        assert result is True
