"""Tests for the application orchestration layer."""

import pytest
from io import StringIO
from pathlib import Path
from rich.console import Console

from envguard.app import EnvGuardApp


def make_app() -> tuple[EnvGuardApp, StringIO]:
    buf = StringIO()
    console = Console(file=buf, highlight=False, markup=False)
    return EnvGuardApp(console=console), buf


def write_env(path: Path, content: str) -> None:
    path.write_text(content)


def write_schema(path: Path, content: str) -> None:
    path.write_text(content)


# --- check ---

def test_check_valid(tmp_path):
    write_env(tmp_path / ".env", "PORT=8000\nDEBUG=true\n")
    write_schema(
        tmp_path / ".env.schema.toml",
        '[PORT]\nrequired = true\nformat = "int"\n\n[DEBUG]\nrequired = true\nformat = "bool"\n',
    )
    app, _ = make_app()
    result, code = app.check(
        env_path=tmp_path / ".env",
        schema_path=tmp_path / ".env.schema.toml",
    )
    assert code == 0
    assert result.valid is True


def test_check_missing_required(tmp_path):
    write_env(tmp_path / ".env", "DEBUG=true\n")
    write_schema(tmp_path / ".env.schema.toml", '[DB_URL]\nrequired = true\nformat = "url"\n')
    app, _ = make_app()
    result, code = app.check(
        env_path=tmp_path / ".env",
        schema_path=tmp_path / ".env.schema.toml",
    )
    assert code == 1
    assert result.valid is False


def test_check_env_not_found(tmp_path):
    app, buf = make_app()
    result, code = app.check(env_path=tmp_path / "nonexistent.env")
    assert code == 2


def test_check_schema_not_found(tmp_path):
    write_env(tmp_path / ".env", "A=1\n")
    app, buf = make_app()
    result, code = app.check(
        env_path=tmp_path / ".env",
        schema_path=tmp_path / "missing.toml",
    )
    assert code == 2


def test_check_json_output(tmp_path):
    write_env(tmp_path / ".env", "PORT=8000\n")
    write_schema(tmp_path / ".env.schema.toml", '[PORT]\nrequired = true\nformat = "int"\n')
    app, buf = make_app()
    app.check(
        env_path=tmp_path / ".env",
        schema_path=tmp_path / ".env.schema.toml",
        output_json=True,
    )
    import json
    data = json.loads(buf.getvalue())
    assert "valid" in data


# --- diff ---

def test_diff_no_differences(tmp_path):
    write_env(tmp_path / ".env", "A=1\n")
    write_schema(tmp_path / ".env.schema.toml", '[A]\nrequired = true\n')
    app, _ = make_app()
    result, code = app.diff(
        env_path=tmp_path / ".env",
        schema_path=tmp_path / ".env.schema.toml",
    )
    assert code == 0
    assert result.has_differences is False


def test_diff_missing_var(tmp_path):
    write_env(tmp_path / ".env", "A=1\n")
    write_schema(tmp_path / ".env.schema.toml", '[A]\nrequired = true\n\n[B]\nrequired = true\n')
    app, _ = make_app()
    result, code = app.diff(
        env_path=tmp_path / ".env",
        schema_path=tmp_path / ".env.schema.toml",
    )
    assert "B" in result.missing_in_env


def test_diff_env_not_found(tmp_path):
    app, _ = make_app()
    _, code = app.diff(env_path=tmp_path / "missing.env")
    assert code == 2


def test_diff_json_output(tmp_path):
    write_env(tmp_path / ".env", "A=1\n")
    write_schema(tmp_path / ".env.schema.toml", '[A]\nrequired = true\n')
    app, buf = make_app()
    app.diff(
        env_path=tmp_path / ".env",
        schema_path=tmp_path / ".env.schema.toml",
        output_json=True,
    )
    import json
    data = json.loads(buf.getvalue())
    assert "has_differences" in data


# --- audit ---

def test_audit_clean_env(tmp_path):
    write_env(tmp_path / ".env", "APP_NAME=myapp\nPORT=8000\n")
    app, _ = make_app()
    result, code = app.audit(env_path=tmp_path / ".env")
    assert code == 0
    assert result.has_issues is False


def test_audit_with_placeholder(tmp_path):
    write_env(tmp_path / ".env", "API_KEY=changeme\n")
    app, _ = make_app()
    result, code = app.audit(env_path=tmp_path / ".env")
    assert code == 1
    assert result.critical_count > 0


def test_audit_env_not_found(tmp_path):
    app, _ = make_app()
    _, code = app.audit(env_path=tmp_path / "missing.env")
    assert code == 2


def test_audit_json_output(tmp_path):
    write_env(tmp_path / ".env", "APP=myapp\n")
    app, buf = make_app()
    app.audit(env_path=tmp_path / ".env", output_json=True)
    import json
    data = json.loads(buf.getvalue())
    assert "findings" in data


# --- init ---

def test_init_creates_schema(tmp_path):
    write_env(tmp_path / ".env", "DATABASE_URL=postgres://localhost/db\nDEBUG=true\n")
    output = tmp_path / ".env.schema.toml"
    app, _ = make_app()
    code = app.init(env_path=tmp_path / ".env", schema_path=output)
    assert code == 0
    assert output.exists()
    content = output.read_text()
    assert "[DATABASE_URL]" in content
    assert "[DEBUG]" in content


def test_init_env_not_found(tmp_path):
    app, _ = make_app()
    code = app.init(env_path=tmp_path / "missing.env")
    assert code == 2


def test_init_overwrites_existing_schema(tmp_path):
    write_env(tmp_path / ".env", "NEW_VAR=1\n")
    schema_file = tmp_path / ".env.schema.toml"
    schema_file.write_text("old content")
    app, buf = make_app()
    code = app.init(env_path=tmp_path / ".env", schema_path=schema_file)
    assert code == 0
    assert "NEW_VAR" in schema_file.read_text()
    assert "Warning" in buf.getvalue()
