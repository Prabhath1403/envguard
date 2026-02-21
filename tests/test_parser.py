"""Tests for .env file parser."""

import tempfile
from pathlib import Path

import pytest
from envguard.parser import parse_env_file, mask_sensitive_value


def test_parse_simple_env() -> None:
    """Test parsing a simple .env file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("KEY1=value1\n")
        f.write("KEY2=value2\n")
        f.flush()

        result = parse_env_file(Path(f.name))
        assert result == {"KEY1": "value1", "KEY2": "value2"}

        Path(f.name).unlink()


def test_parse_env_with_comments() -> None:
    """Test parsing .env file with comments."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("# This is a comment\n")
        f.write("KEY1=value1\n")
        f.write("# Another comment\n")
        f.write("KEY2=value2\n")
        f.flush()

        result = parse_env_file(Path(f.name))
        assert result == {"KEY1": "value1", "KEY2": "value2"}

        Path(f.name).unlink()


def test_parse_env_with_quotes() -> None:
    """Test parsing .env file with quoted values."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write('KEY1="value with spaces"\n')
        f.write("KEY2='another value'\n")
        f.write("KEY3=no quotes\n")
        f.flush()

        result = parse_env_file(Path(f.name))
        assert result["KEY1"] == "value with spaces"
        assert result["KEY2"] == "another value"
        assert result["KEY3"] == "no quotes"

        Path(f.name).unlink()


def test_parse_env_with_blank_lines() -> None:
    """Test parsing .env file with blank lines."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("KEY1=value1\n")
        f.write("\n")
        f.write("\n")
        f.write("KEY2=value2\n")
        f.flush()

        result = parse_env_file(Path(f.name))
        assert result == {"KEY1": "value1", "KEY2": "value2"}

        Path(f.name).unlink()


def test_parse_env_file_not_found() -> None:
    """Test parsing non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        parse_env_file(Path("/nonexistent/file.env"))


def test_mask_sensitive_value() -> None:
    """Test masking of sensitive values."""
    result = mask_sensitive_value("PASSWORD", "secret123", show_length=4)
    assert result == "*****t123"
    assert len(result) == len("secret123")


def test_mask_sensitive_value_short() -> None:
    """Test masking short sensitive values."""
    result = mask_sensitive_value("API_KEY", "abc", show_length=4)
    assert result == "***"


def test_mask_non_sensitive_value() -> None:
    """Test non-sensitive values are not masked."""
    result = mask_sensitive_value("APP_NAME", "MyApp", show_length=4)
    assert result == "MyApp"


def test_mask_various_sensitive_keywords() -> None:
    """Test masking works for various sensitive keywords."""
    sensitive_keys = ["PASSWORD", "SECRET", "TOKEN", "API_KEY", "PRIVATE_KEY"]

    for key in sensitive_keys:
        result = mask_sensitive_value(key, "sensitive_data")
        assert result.startswith("*"), f"Failed for key: {key}"
