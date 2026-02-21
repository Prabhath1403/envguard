"""Tests for the diff engine module."""

from envguard.diff_engine import compute_diff
from envguard.models import SchemaEntry


def _entry(key: str) -> SchemaEntry:
    return SchemaEntry(key=key, required=True, format="string")


def test_diff_no_differences():
    env = {"A": "1", "B": "2"}
    schema = {"A": _entry("A"), "B": _entry("B")}
    result = compute_diff(env, schema)
    assert result.missing_in_env == []
    assert result.undocumented_in_schema == []
    assert result.has_differences is False


def test_diff_missing_in_env():
    env = {"A": "1"}
    schema = {"A": _entry("A"), "B": _entry("B")}
    result = compute_diff(env, schema)
    assert "B" in result.missing_in_env
    assert result.has_differences is True


def test_diff_undocumented_in_schema():
    env = {"A": "1", "EXTRA": "val"}
    schema = {"A": _entry("A")}
    result = compute_diff(env, schema)
    assert "EXTRA" in result.undocumented_in_schema
    assert result.has_differences is True


def test_diff_sorted_results():
    env = {"Z": "1", "A": "2"}
    schema = {"M": _entry("M"), "B": _entry("B")}
    result = compute_diff(env, schema)
    assert result.missing_in_env == sorted(result.missing_in_env)
    assert result.undocumented_in_schema == sorted(result.undocumented_in_schema)


def test_diff_empty_env_and_schema():
    result = compute_diff({}, {})
    assert result.has_differences is False
    assert len(result.env_vars) == 0
    assert len(result.schema_vars) == 0


def test_diff_env_vars_and_schema_vars_sets():
    env = {"A": "1"}
    schema = {"B": _entry("B")}
    result = compute_diff(env, schema)
    assert result.env_vars == {"A"}
    assert result.schema_vars == {"B"}
