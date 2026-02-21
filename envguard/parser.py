"""Parser for .env files."""

from pathlib import Path


def parse_env_file(file_path: Path) -> dict[str, str]:
    """
    Parse a .env file into a dictionary.

    Args:
        file_path: Path to the .env file

    Returns:
        Dictionary mapping environment variable names to values

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    env_data: dict[str, str] = {}

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            # Strip whitespace
            line = line.strip()

            # Skip blank lines and comments
            if not line or line.startswith("#"):
                continue

            # Parse KEY=VALUE
            if "=" not in line:
                # Skip malformed lines silently (or could log warning)
                continue

            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()

            # Remove quotes if present (optional enhancement)
            if value and value[0] in ('"', "'") and value[-1] == value[0]:
                value = value[1:-1]

            if key:
                env_data[key] = value

    return env_data


def mask_sensitive_value(key: str, value: str, show_length: int = 4) -> str:
    """
    Mask sensitive values for display.

    Args:
        key: The environment variable key
        value: The value to potentially mask
        show_length: Number of characters to show at the end

    Returns:
        Masked or original value
    """
    # List of keywords that indicate sensitive data
    sensitive_keywords = [
        "PASSWORD",
        "SECRET",
        "KEY",
        "TOKEN",
        "API",
        "PRIVATE",
        "CREDENTIAL",
        "AUTH",
    ]

    # Check if key contains any sensitive keyword
    key_upper = key.upper()
    is_sensitive = any(keyword in key_upper for keyword in sensitive_keywords)

    if not is_sensitive or not value:
        return value

    # Mask the value
    if len(value) <= show_length:
        return "*" * len(value)

    visible_part = value[-show_length:]
    masked_part = "*" * (len(value) - show_length)
    return f"{masked_part}{visible_part}"
