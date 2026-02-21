"""Tests for output formatters."""

import json
import pytest
from io import StringIO
from rich.console import Console

from envguard.formatter import (
    format_audit_json,
    format_audit_rich,
    format_diff_json,
    format_diff_rich,
    format_validation_json,
    format_validation_rich,
)
from envguard.models import (
    AuditFinding,
    AuditResult,
    DiffResult,
    SchemaEntry,
    Severity,
    ValidationIssue,
    ValidationResult,
)


def make_console() -> tuple[Console, StringIO]:
    buf = StringIO()
    console = Console(file=buf, highlight=False, markup=False)
    return console, buf


# --- Validation JSON ---

def test_format_validation_json_valid():
    result = ValidationResult(valid=True, issues=[], env_data={}, schema={})
    output = format_validation_json(result)
    data = json.loads(output)
    assert data["valid"] is True
    assert data["error_count"] == 0
    assert data["issues"] == []


def test_format_validation_json_with_issues():
    issue = ValidationIssue(
        key="DB_URL", severity=Severity.ERROR, message="Missing required variable"
    )
    result = ValidationResult(valid=False, issues=[issue], env_data={}, schema={})
    data = json.loads(format_validation_json(result))
    assert data["valid"] is False
    assert len(data["issues"]) == 1
    assert data["issues"][0]["key"] == "DB_URL"
    assert data["issues"][0]["severity"] == "error"


# --- Validation Rich ---

def test_format_validation_rich_passed():
    result = ValidationResult(valid=True, issues=[], env_data={}, schema={})
    console, buf = make_console()
    format_validation_rich(result, console)
    assert "passed" in buf.getvalue().lower()


def test_format_validation_rich_failed():
    issue = ValidationIssue(key="X", severity=Severity.ERROR, message="Missing")
    result = ValidationResult(valid=False, issues=[issue], env_data={}, schema={})
    console, buf = make_console()
    format_validation_rich(result, console)
    assert "failed" in buf.getvalue().lower()


# --- Diff JSON ---

def test_format_diff_json_no_diff():
    result = DiffResult(missing_in_env=[], undocumented_in_schema=[], env_vars=set(), schema_vars=set())
    data = json.loads(format_diff_json(result))
    assert data["has_differences"] is False
    assert data["missing_in_env"] == []


def test_format_diff_json_with_diff():
    result = DiffResult(
        missing_in_env=["DB_URL"],
        undocumented_in_schema=["EXTRA"],
        env_vars={"EXTRA"},
        schema_vars={"DB_URL"},
    )
    data = json.loads(format_diff_json(result))
    assert data["has_differences"] is True
    assert "DB_URL" in data["missing_in_env"]
    assert "EXTRA" in data["undocumented_in_schema"]


# --- Diff Rich ---

def test_format_diff_rich_no_differences():
    result = DiffResult(missing_in_env=[], undocumented_in_schema=[], env_vars=set(), schema_vars=set())
    console, buf = make_console()
    format_diff_rich(result, console)
    assert "No differences" in buf.getvalue()


def test_format_diff_rich_with_differences():
    result = DiffResult(
        missing_in_env=["MISSING_VAR"],
        undocumented_in_schema=[],
        env_vars=set(),
        schema_vars={"MISSING_VAR"},
    )
    console, buf = make_console()
    format_diff_rich(result, console)
    assert "MISSING_VAR" in buf.getvalue()


# --- Audit JSON ---

def test_format_audit_json_clean():
    result = AuditResult(findings=[], total_vars=3)
    data = json.loads(format_audit_json(result))
    assert data["has_issues"] is False
    assert data["total_vars"] == 3
    assert data["findings"] == []


def test_format_audit_json_with_findings():
    finding = AuditFinding(
        key="API_KEY",
        severity=Severity.ERROR,
        category="placeholder",
        message="Placeholder value",
        value_preview="changeme",
    )
    result = AuditResult(findings=[finding], total_vars=1, placeholders_found=1)
    data = json.loads(format_audit_json(result))
    assert data["has_issues"] is True
    assert len(data["findings"]) == 1
    assert data["findings"][0]["category"] == "placeholder"


# --- Audit Rich ---

def test_format_audit_rich_no_issues():
    result = AuditResult(findings=[], total_vars=5)
    console, buf = make_console()
    format_audit_rich(result, console)
    assert "No security issues" in buf.getvalue()


def test_format_audit_rich_with_findings():
    finding = AuditFinding(
        key="DB_PASS",
        severity=Severity.ERROR,
        category="placeholder",
        message="Placeholder detected",
        value_preview="changeme",
    )
    result = AuditResult(findings=[finding], total_vars=1, placeholders_found=1)
    console, buf = make_console()
    format_audit_rich(result, console)
    assert "DB_PASS" in buf.getvalue()
