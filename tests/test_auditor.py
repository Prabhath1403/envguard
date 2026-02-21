"""Tests for the security auditor module."""

import pytest
from envguard.auditor import audit, is_placeholder, is_test_value, is_weak_secret
from envguard.models import Severity


# --- is_placeholder ---

def test_is_placeholder_changeme():
    assert is_placeholder("changeme") is True

def test_is_placeholder_xxxx():
    assert is_placeholder("xxxx") is True

def test_is_placeholder_todo():
    assert is_placeholder("todo") is True

def test_is_placeholder_sample():
    assert is_placeholder("sample") is True

def test_is_placeholder_real_value():
    assert is_placeholder("postgres://user:pass@localhost/db") is False

def test_is_placeholder_case_insensitive():
    assert is_placeholder("CHANGEME") is True


# --- is_test_value ---

def test_is_test_value_password():
    assert is_test_value("password") is True

def test_is_test_value_12345():
    assert is_test_value("12345") is True

def test_is_test_value_admin():
    assert is_test_value("admin") is True

def test_is_test_value_real_value():
    assert is_test_value("super-secure-random-string-xyz") is False

def test_is_test_value_case_sensitive():
    # TEST_VALUES are compared with lower(), so uppercase should still match
    assert is_test_value("PASSWORD") is True


# --- is_weak_secret ---

def test_is_weak_secret_short_token():
    assert is_weak_secret("API_TOKEN", "short") is True

def test_is_weak_secret_long_token():
    assert is_weak_secret("API_TOKEN", "this-is-a-long-enough-secret-value") is False

def test_is_weak_secret_non_sensitive_key():
    assert is_weak_secret("APP_NAME", "short") is False

def test_is_weak_secret_empty_value():
    assert is_weak_secret("API_KEY", "") is False

def test_is_weak_secret_exactly_16_chars():
    assert is_weak_secret("API_KEY", "1234567890123456") is False

def test_is_weak_secret_15_chars():
    assert is_weak_secret("API_KEY", "123456789012345") is True


# --- audit ---

def test_audit_clean_env():
    env = {"APP_NAME": "myapp", "PORT": "8000"}
    result = audit(env)
    assert result.total_vars == 2
    assert len(result.findings) == 0
    assert result.placeholders_found == 0
    assert result.weak_secrets_found == 0
    assert result.test_values_found == 0

def test_audit_detects_placeholder():
    env = {"DATABASE_URL": "changeme"}
    result = audit(env)
    assert result.placeholders_found == 1
    assert result.findings[0].severity == Severity.ERROR
    assert result.findings[0].category == "placeholder"

def test_audit_detects_test_value():
    env = {"DB_PASSWORD": "password"}
    result = audit(env)
    assert result.test_values_found == 1
    assert result.findings[0].category == "test-value"

def test_audit_detects_weak_secret():
    env = {"API_SECRET": "tooshort"}
    result = audit(env)
    assert result.weak_secrets_found == 1
    assert result.findings[0].category == "weak-secret"
    assert result.findings[0].severity == Severity.WARNING

def test_audit_detects_empty_sensitive():
    env = {"API_KEY": ""}
    result = audit(env)
    categories = [f.category for f in result.findings]
    assert "empty-sensitive" in categories

def test_audit_value_preview_truncated():
    long_value = "changeme" + "x" * 50
    env = {"SOME_VAR": long_value}
    result = audit(env)
    assert result.placeholders_found == 1
    assert result.findings[0].value_preview.endswith("...")

def test_audit_has_issues_property():
    env = {"API_KEY": "changeme"}
    result = audit(env)
    assert result.has_issues is True

def test_audit_critical_count():
    env = {"A": "changeme", "B": "todo"}
    result = audit(env)
    assert result.critical_count == 2
