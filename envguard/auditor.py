"""Security auditor for environment variables."""

from envguard.models import AuditFinding, AuditResult, Severity

# Placeholder patterns to detect
PLACEHOLDER_PATTERNS = [
    "changeme",
    "change_me",
    "change-me",
    "your-secret-here",
    "your_secret_here",
    "yoursecrethere",
    "todo",
    "to-do",
    "fixme",
    "fix-me",
    "xxx",
    "xxxx",
    "xxxxx",
    "replace-me",
    "replace_me",
    "placeholder",
    "sample",
    "example-value",
]

# Common test/weak values
TEST_VALUES = [
    "password",
    "12345",
    "123456",
    "12345678",
    "test",
    "example",
    "demo",
    "secret",
    "key",
    "token",
    "admin",
    "root",
    "qwerty",
    "abc123",
]

# Keywords indicating sensitive data
SENSITIVE_KEYWORDS = [
    "SECRET",
    "TOKEN",
    "KEY",
    "PASSWORD",
    "CREDENTIAL",
    "API",
    "PRIVATE",
    "AUTH",
]


def is_placeholder(value: str) -> bool:
    """Check if a value looks like a placeholder."""
    value_lower = value.lower().strip()
    return any(pattern in value_lower for pattern in PLACEHOLDER_PATTERNS)


def is_test_value(value: str) -> bool:
    """Check if a value looks like a test/example value."""
    value_lower = value.lower().strip()
    return value_lower in TEST_VALUES


def is_weak_secret(key: str, value: str) -> bool:
    """
    Check if a value is a weak secret.

    A secret is considered weak if:
    - The key suggests it's sensitive (contains SECRET, TOKEN, KEY, etc.)
    - The value is too short (< 16 characters)
    """
    key_upper = key.upper()
    is_sensitive_key = any(keyword in key_upper for keyword in SENSITIVE_KEYWORDS)

    if is_sensitive_key and value and len(value) < 16:
        return True

    return False


def audit(env_data: dict[str, str]) -> AuditResult:
    """
    Audit environment variables for security issues.

    Args:
        env_data: Dictionary of environment variables

    Returns:
        AuditResult with findings
    """
    findings: list[AuditFinding] = []
    placeholders_found = 0
    weak_secrets_found = 0
    test_values_found = 0

    for key, value in env_data.items():
        # Check for placeholders
        if is_placeholder(value):
            placeholders_found += 1
            findings.append(
                AuditFinding(
                    key=key,
                    severity=Severity.ERROR,
                    category="placeholder",
                    message="Placeholder value detected",
                    value_preview=value[:30] if len(value) <= 30 else f"{value[:27]}...",
                )
            )

        # Check for test values
        elif is_test_value(value):
            test_values_found += 1
            findings.append(
                AuditFinding(
                    key=key,
                    severity=Severity.ERROR,
                    category="test-value",
                    message="Test/example value detected",
                    value_preview=value,
                )
            )

        # Check for weak secrets
        elif is_weak_secret(key, value):
            weak_secrets_found += 1
            findings.append(
                AuditFinding(
                    key=key,
                    severity=Severity.WARNING,
                    category="weak-secret",
                    message=f"Weak secret detected (length: {len(value)}, recommended: 16+)",
                    value_preview="****",
                )
            )

        # Check for empty values in sensitive keys
        key_upper = key.upper()
        is_sensitive = any(keyword in key_upper for keyword in SENSITIVE_KEYWORDS)
        if is_sensitive and not value:
            findings.append(
                AuditFinding(
                    key=key,
                    severity=Severity.WARNING,
                    category="empty-sensitive",
                    message="Sensitive variable has empty value",
                    value_preview="(empty)",
                )
            )

    return AuditResult(
        findings=findings,
        total_vars=len(env_data),
        placeholders_found=placeholders_found,
        weak_secrets_found=weak_secrets_found,
        test_values_found=test_values_found,
    )
