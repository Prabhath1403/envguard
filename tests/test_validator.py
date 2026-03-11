"""Sample test file for envguard - demonstrates testing structure."""

import pytest
from envguard.models import SchemaEntry, Severity
from envguard.validator import validate, validate_format


def test_validate_format_int_valid() -> None:
    """Test integer format validation with valid input."""
    result = validate_format("PORT", "8000", "int")
    assert result is None


def test_validate_format_int_invalid() -> None:
    """Test integer format validation with invalid input."""
    result = validate_format("PORT", "not-a-number", "int")
    assert result is not None
    assert result.severity == Severity.ERROR
    assert result.key == "PORT"


def test_validate_format_bool_valid() -> None:
    """Test boolean format validation with valid input."""
    for value in ["true", "false", "1", "0", "yes", "no"]:
        result = validate_format("DEBUG", value, "bool")
        assert result is None, f"Failed for value: {value}"


def test_validate_format_bool_invalid() -> None:
    """Test boolean format validation with invalid input."""
    result = validate_format("DEBUG", "maybe", "bool")
    assert result is not None
    assert result.severity == Severity.ERROR


def test_validate_format_url_valid() -> None:
    """Test URL format validation with valid input."""
    result = validate_format("DATABASE_URL", "postgresql://localhost:5432/db", "url")
    assert result is None


def test_validate_format_url_invalid() -> None:
    """Test URL format validation with invalid input."""
    result = validate_format("DATABASE_URL", "not-a-url", "url")
    assert result is not None
    assert result.severity == Severity.ERROR


def test_validate_missing_required() -> None:
    """Test validation detects missing required variables."""
    env_data = {"KEY1": "value1"}
    schema = {
        "KEY1": SchemaEntry(key="KEY1", required=True),
        "KEY2": SchemaEntry(key="KEY2", required=True),
    }

    result = validate(env_data, schema)
    assert not result.valid
    assert result.error_count == 1
    assert any(issue.key == "KEY2" for issue in result.issues)


def test_validate_undocumented_variable() -> None:
    """Test validation warns about undocumented variables."""
    env_data = {"KEY1": "value1", "KEY2": "value2"}
    schema = {
        "KEY1": SchemaEntry(key="KEY1", required=True),
    }

    result = validate(env_data, schema)
    assert result.valid  # Should pass validation (warning only)
    assert result.warning_count == 1
    assert any(
        issue.key == "KEY2" and issue.severity == Severity.WARNING for issue in result.issues
    )


def test_validate_with_defaults() -> None:
    """Test validation with default values."""
    env_data = {"KEY1": "value1"}
    schema = {
        "KEY1": SchemaEntry(key="KEY1", required=True),
        "KEY2": SchemaEntry(key="KEY2", required=True, default="default_value"),
    }

    result = validate(env_data, schema)
    # KEY2 is missing but has default, so it should pass
    assert result.valid


def test_validate_format_validation() -> None:
    """Test format validation is applied."""
    env_data = {"PORT": "not-a-number"}
    schema = {
        "PORT": SchemaEntry(key="PORT", required=True, format="int"),
    }

    result = validate(env_data, schema)
    assert not result.valid
    assert result.error_count == 1
    assert any(
        issue.key == "PORT" and "integer" in issue.message.lower() for issue in result.issues
    )
