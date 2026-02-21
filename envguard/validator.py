"""Validation engine for environment variables."""

import re
from urllib.parse import urlparse

from envguard.models import SchemaEntry, Severity, ValidationIssue, ValidationResult


def validate_format(key: str, value: str, format_type: str) -> ValidationIssue | None:
    """
    Validate a value against a format type.

    Args:
        key: Environment variable key
        value: Value to validate
        format_type: Expected format (string, int, bool, url)

    Returns:
        ValidationIssue if validation fails, None if valid
    """
    if format_type == "string":
        # All values are valid strings
        return None

    elif format_type == "int":
        try:
            int(value)
            return None
        except ValueError:
            return ValidationIssue(
                key=key,
                severity=Severity.ERROR,
                message=f"Value must be an integer",
                expected="integer",
                actual=value[:50],
            )

    elif format_type == "bool":
        valid_bool_values = {"true", "false", "1", "0", "yes", "no", "on", "off"}
        if value.lower() not in valid_bool_values:
            return ValidationIssue(
                key=key,
                severity=Severity.ERROR,
                message=f"Value must be a boolean",
                expected="true/false/1/0/yes/no/on/off",
                actual=value[:50],
            )
        return None

    elif format_type == "url":
        try:
            result = urlparse(value)
            if not all([result.scheme, result.netloc]):
                return ValidationIssue(
                    key=key,
                    severity=Severity.ERROR,
                    message=f"Value must be a valid URL with scheme and netloc",
                    expected="http://example.com or https://example.com",
                    actual=value[:50],
                )
            return None
        except Exception:
            return ValidationIssue(
                key=key,
                severity=Severity.ERROR,
                message=f"Value must be a valid URL",
                expected="http://example.com",
                actual=value[:50],
            )

    else:
        # Unknown format type - treat as warning
        return ValidationIssue(
            key=key,
            severity=Severity.WARNING,
            message=f"Unknown format type: {format_type}",
            expected=None,
            actual=None,
        )


def validate(env_data: dict[str, str], schema: dict[str, SchemaEntry]) -> ValidationResult:
    """
    Validate environment data against a schema.

    Args:
        env_data: Dictionary of environment variables
        schema: Dictionary of schema entries

    Returns:
        ValidationResult with validation issues
    """
    issues: list[ValidationIssue] = []

    # Check for missing required variables
    for key, entry in schema.items():
        if entry.required and key not in env_data:
            # Check if default is available
            if entry.default is None:
                issues.append(
                    ValidationIssue(
                        key=key,
                        severity=Severity.ERROR,
                        message=f"Required variable missing",
                        expected="present in .env file",
                        actual="missing",
                    )
                )

    # Check for undocumented variables (warning only)
    for key in env_data:
        if key not in schema:
            issues.append(
                ValidationIssue(
                    key=key,
                    severity=Severity.WARNING,
                    message=f"Variable not documented in schema",
                    expected=None,
                    actual="present in .env but missing in schema",
                )
            )

    # Validate formats for present variables
    for key, value in env_data.items():
        if key in schema:
            entry = schema[key]
            if entry.format:
                format_issue = validate_format(key, value, entry.format)
                if format_issue:
                    issues.append(format_issue)

    # Determine if validation passed
    has_errors = any(issue.severity == Severity.ERROR for issue in issues)
    valid = not has_errors

    return ValidationResult(
        valid=valid,
        issues=issues,
        env_data=env_data,
        schema=schema,
    )


def apply_defaults(env_data: dict[str, str], schema: dict[str, SchemaEntry]) -> dict[str, str]:
    """
    Apply default values from schema to environment data.

    Args:
        env_data: Current environment variables
        schema: Schema with potential defaults

    Returns:
        New dictionary with defaults applied
    """
    result = env_data.copy()

    for key, entry in schema.items():
        if key not in result and entry.default is not None:
            result[key] = entry.default

    return result
