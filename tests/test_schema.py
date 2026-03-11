"""Tests for the schema loader module."""

import pytest
from pathlib import Path
from envguard.schema import load_schema, create_default_schema


def test_load_schema_valid(tmp_path):
    schema_file = tmp_path / ".env.schema.toml"
    schema_file.write_text(
        '[DATABASE_URL]\nrequired = true\nformat = "url"\ndescription = "DB connection"\n'
    )
    schema = load_schema(schema_file)
    assert "DATABASE_URL" in schema
    assert schema["DATABASE_URL"].required is True
    assert schema["DATABASE_URL"].format == "url"
    assert schema["DATABASE_URL"].description == "DB connection"


def test_load_schema_optional_fields(tmp_path):
    schema_file = tmp_path / ".env.schema.toml"
    schema_file.write_text('[PORT]\nrequired = false\ndefault = "8000"\n')
    schema = load_schema(schema_file)
    assert schema["PORT"].required is False
    assert schema["PORT"].default == "8000"
    assert schema["PORT"].format is None


def test_load_schema_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_schema(tmp_path / "nonexistent.toml")


def test_load_schema_invalid_toml(tmp_path):
    schema_file = tmp_path / ".env.schema.toml"
    schema_file.write_text("[[invalid toml content ][[\n")
    with pytest.raises(ValueError, match="Failed to parse TOML schema"):
        load_schema(schema_file)


def test_load_schema_non_table_entry(tmp_path):
    schema_file = tmp_path / ".env.schema.toml"
    schema_file.write_text("MY_VAR = 42\n")
    with pytest.raises(ValueError, match="must be a table"):
        load_schema(schema_file)


def test_load_schema_multiple_entries(tmp_path):
    schema_file = tmp_path / ".env.schema.toml"
    schema_file.write_text('[A]\nrequired = true\n\n[B]\nrequired = false\nformat = "int"\n')
    schema = load_schema(schema_file)
    assert len(schema) == 2
    assert schema["B"].format == "int"


def test_create_default_schema(tmp_path):
    output = tmp_path / ".env.schema.toml"
    env_data = {"DATABASE_URL": "postgres://localhost/db", "DEBUG": "true"}
    create_default_schema(output, env_data)
    content = output.read_text()
    assert "[DATABASE_URL]" in content
    assert "[DEBUG]" in content
    assert "required = true" in content
    assert 'format = "string"' in content


def test_create_default_schema_sorted_keys(tmp_path):
    output = tmp_path / ".env.schema.toml"
    env_data = {"Z_VAR": "1", "A_VAR": "2"}
    create_default_schema(output, env_data)
    content = output.read_text()
    assert content.index("[A_VAR]") < content.index("[Z_VAR]")
