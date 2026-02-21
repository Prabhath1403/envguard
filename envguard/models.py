"""Data models for envguard."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class FormatType(str, Enum):
    """Supported format types for validation."""

    STRING = "string"
    INT = "int"
    BOOL = "bool"
    URL = "url"


class Severity(str, Enum):
    """Severity levels for findings."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class SchemaEntry:
    """Represents a single entry in the .env.schema.toml file."""

    key: str
    required: bool = False
    format: Optional[str] = None
    default: Optional[str] = None
    description: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate the schema entry after initialization."""
        if self.format and self.format not in [f.value for f in FormatType]:
            raise ValueError(f"Invalid format type: {self.format}")


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""

    key: str
    severity: Severity
    message: str
    expected: Optional[str] = None
    actual: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validating an .env file against a schema."""

    valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    env_data: dict[str, str] = field(default_factory=dict)
    schema: dict[str, SchemaEntry] = field(default_factory=dict)

    @property
    def error_count(self) -> int:
        """Count of error-level issues."""
        return sum(1 for issue in self.issues if issue.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        """Count of warning-level issues."""
        return sum(1 for issue in self.issues if issue.severity == Severity.WARNING)


@dataclass
class DiffResult:
    """Result of comparing .env file against schema."""

    missing_in_env: list[str] = field(default_factory=list)
    undocumented_in_schema: list[str] = field(default_factory=list)
    env_vars: set[str] = field(default_factory=set)
    schema_vars: set[str] = field(default_factory=set)

    @property
    def has_differences(self) -> bool:
        """Check if there are any differences."""
        return bool(self.missing_in_env or self.undocumented_in_schema)


@dataclass
class AuditFinding:
    """Represents a single audit finding."""

    key: str
    severity: Severity
    category: str
    message: str
    value_preview: Optional[str] = None


@dataclass
class AuditResult:
    """Result of auditing an .env file for security issues."""

    findings: list[AuditFinding] = field(default_factory=list)
    total_vars: int = 0
    placeholders_found: int = 0
    weak_secrets_found: int = 0
    test_values_found: int = 0

    @property
    def has_issues(self) -> bool:
        """Check if any issues were found."""
        return bool(self.findings)

    @property
    def critical_count(self) -> int:
        """Count of error-level findings."""
        return sum(1 for f in self.findings if f.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        """Count of warning-level findings."""
        return sum(1 for f in self.findings if f.severity == Severity.WARNING)
