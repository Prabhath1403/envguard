"""Diff engine for comparing .env files against schema."""

from envguard.models import DiffResult, SchemaEntry


def compute_diff(env_data: dict[str, str], schema: dict[str, SchemaEntry]) -> DiffResult:
    """
    Compare environment variables against schema.

    Args:
        env_data: Dictionary of environment variables from .env file
        schema: Dictionary of schema entries

    Returns:
        DiffResult showing missing and undocumented variables
    """
    env_vars = set(env_data.keys())
    schema_vars = set(schema.keys())

    # Variables in schema but not in env
    missing_in_env = sorted(schema_vars - env_vars)

    # Variables in env but not in schema
    undocumented_in_schema = sorted(env_vars - schema_vars)

    return DiffResult(
        missing_in_env=missing_in_env,
        undocumented_in_schema=undocumented_in_schema,
        env_vars=env_vars,
        schema_vars=schema_vars,
    )
