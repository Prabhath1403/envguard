"""Utility functions for envguard."""

from pathlib import Path


def find_env_file(start_path: Path = Path.cwd()) -> Path | None:
    """
    Find .env file in current directory or parent directories.

    Args:
        start_path: Directory to start searching from

    Returns:
        Path to .env file or None if not found
    """
    current = start_path.resolve()

    # Check up to 5 levels up
    for _ in range(5):
        env_file = current / ".env"
        if env_file.exists():
            return env_file

        # Move up one directory
        parent = current.parent
        if parent == current:
            # Reached root
            break
        current = parent

    return None


def find_schema_file(start_path: Path = Path.cwd()) -> Path | None:
    """
    Find .env.schema.toml file in current directory or parent directories.

    Args:
        start_path: Directory to start searching from

    Returns:
        Path to schema file or None if not found
    """
    current = start_path.resolve()

    # Check up to 5 levels up
    for _ in range(5):
        schema_file = current / ".env.schema.toml"
        if schema_file.exists():
            return schema_file

        # Move up one directory
        parent = current.parent
        if parent == current:
            # Reached root
            break
        current = parent

    return None


def find_git_root(start_path: Path = Path.cwd()) -> Path | None:
    """
    Find the root of the Git repository by walking up directories.

    Args:
        start_path: Directory to start searching from

    Returns:
        Path to directory containing .git, or None if not a git repo
    """
    current = start_path.resolve()

    for _ in range(20):
        if (current / ".git").is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent

    return None


def ensure_path(path: Path | str | None, default_name: str) -> Path:
    """
    Ensure a path exists or use default.

    Args:
        path: Optional path
        default_name: Default filename to use in current directory

    Returns:
        Resolved Path object
    """
    if path is None:
        return Path.cwd() / default_name
    return Path(path).resolve()
