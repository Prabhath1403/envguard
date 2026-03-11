"""Schema loading and management."""

import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        raise ImportError("Python < 3.11 requires 'tomli' package for TOML support")

from envguard.models import SchemaEntry


def load_schema(schema_path: Path) -> dict[str, SchemaEntry]:
    """
    Load and parse a .env.schema.toml file.

    Args:
        schema_path: Path to the schema file

    Returns:
        Dictionary mapping variable names to SchemaEntry objects

    Raises:
        FileNotFoundError: If the schema file does not exist
        ValueError: If the schema is malformed
    """
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, "rb") as f:
        try:
            data = tomllib.load(f)
        except Exception as e:
            raise ValueError(f"Failed to parse TOML schema: {e}") from e

    schema: dict[str, SchemaEntry] = {}

    for key, value in data.items():
        if not isinstance(value, dict):
            raise ValueError(f"Schema entry '{key}' must be a table/dict")

        try:
            schema[key] = SchemaEntry(
                key=key,
                required=value.get("required", False),
                format=value.get("format"),
                default=value.get("default"),
                description=value.get("description"),
            )
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid schema entry '{key}': {e}") from e

    return schema


def create_default_schema(output_path: Path, env_data: dict[str, str]) -> None:
    """
    Create a default schema file from an existing .env file.

    Args:
        output_path: Path where the schema should be written
        env_data: Environment variables from the .env file
    """
    lines = [
        "# .env.schema.toml",
        "# Generated schema - customize as needed",
        "",
    ]

    for key in sorted(env_data.keys()):
        lines.append(f"[{key}]")
        lines.append("required = true")
        lines.append('format = "string"')
        lines.append(f'description = "Description for {key}"')
        lines.append("")

    content = "\n".join(lines)
    output_path.write_text(content, encoding="utf-8")
