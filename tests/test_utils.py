"""Tests for utility functions."""

import pytest
from pathlib import Path
from envguard.utils import find_env_file, find_schema_file, ensure_path


def test_find_env_file_found(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")
    result = find_env_file(tmp_path)
    assert result == env_file


def test_find_env_file_not_found(tmp_path):
    result = find_env_file(tmp_path)
    assert result is None


def test_find_env_file_in_parent(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    result = find_env_file(subdir)
    assert result == env_file


def test_find_schema_file_found(tmp_path):
    schema_file = tmp_path / ".env.schema.toml"
    schema_file.write_text("[A]\nrequired = true\n")
    result = find_schema_file(tmp_path)
    assert result == schema_file


def test_find_schema_file_not_found(tmp_path):
    result = find_schema_file(tmp_path)
    assert result is None


def test_find_schema_file_in_parent(tmp_path):
    schema_file = tmp_path / ".env.schema.toml"
    schema_file.write_text("[A]\nrequired = true\n")
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    result = find_schema_file(subdir)
    assert result == schema_file


def test_ensure_path_with_none(tmp_path):
    # When path is None, returns cwd / default_name
    result = ensure_path(None, ".env")
    assert result.name == ".env"


def test_ensure_path_with_string(tmp_path):
    result = ensure_path(str(tmp_path / ".env"), ".env")
    assert result == (tmp_path / ".env").resolve()


def test_ensure_path_with_path_object(tmp_path):
    p = tmp_path / "custom.env"
    result = ensure_path(p, ".env")
    assert result == p.resolve()
