"""Output formatters for envguard."""

import json
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from envguard.models import (
    AuditResult,
    DiffResult,
    Severity,
    ValidationResult,
)


def format_validation_json(result: ValidationResult) -> str:
    """Format validation result as JSON."""
    data = {
        "valid": result.valid,
        "error_count": result.error_count,
        "warning_count": result.warning_count,
        "issues": [
            {
                "key": issue.key,
                "severity": issue.severity.value,
                "message": issue.message,
                "expected": issue.expected,
                "actual": issue.actual,
            }
            for issue in result.issues
        ],
    }
    return json.dumps(data, indent=2)


def format_validation_rich(result: ValidationResult, console: Console) -> None:
    """Format validation result using Rich."""
    if result.valid:
        console.print("[green]✓[/green] Validation passed!", style="bold green")
        if result.warning_count > 0:
            console.print(f"[yellow]⚠[/yellow]  {result.warning_count} warning(s) found")
    else:
        console.print("[red]✗[/red] Validation failed!", style="bold red")
        console.print(
            f"[red]✗[/red] {result.error_count} error(s), "
            f"[yellow]⚠[/yellow] {result.warning_count} warning(s)"
        )

    if result.issues:
        console.print()
        table = Table(title="Validation Issues", show_header=True)
        table.add_column("Severity", style="bold", width=10)
        table.add_column("Variable", style="cyan", width=25)
        table.add_column("Message", width=50)

        for issue in result.issues:
            severity_style = "red" if issue.severity == Severity.ERROR else "yellow"
            severity_symbol = "ERROR" if issue.severity == Severity.ERROR else "WARN"

            table.add_row(
                f"[{severity_style}]{severity_symbol}[/{severity_style}]",
                issue.key,
                issue.message,
            )

        console.print(table)


def format_diff_json(result: DiffResult) -> str:
    """Format diff result as JSON."""
    data = {
        "has_differences": result.has_differences,
        "missing_in_env": result.missing_in_env,
        "undocumented_in_schema": result.undocumented_in_schema,
        "summary": {
            "env_vars_count": len(result.env_vars),
            "schema_vars_count": len(result.schema_vars),
            "missing_count": len(result.missing_in_env),
            "undocumented_count": len(result.undocumented_in_schema),
        },
    }
    return json.dumps(data, indent=2)


def format_diff_rich(result: DiffResult, console: Console) -> None:
    """Format diff result using Rich."""
    console.print("[bold]Environment vs Schema Diff[/bold]\n")

    if not result.has_differences:
        console.print("[green]✓[/green] No differences found!", style="bold green")
        return

    if result.missing_in_env:
        console.print(
            f"[yellow]⚠[/yellow] [bold]{len(result.missing_in_env)}[/bold] "
            "variable(s) in schema but missing from .env:"
        )
        for var in result.missing_in_env:
            console.print(f"  [yellow]•[/yellow] {var}")
        console.print()

    if result.undocumented_in_schema:
        console.print(
            f"[cyan]ℹ[/cyan] [bold]{len(result.undocumented_in_schema)}[/bold] "
            "variable(s) in .env but not documented in schema:"
        )
        for var in result.undocumented_in_schema:
            console.print(f"  [cyan]•[/cyan] {var}")
        console.print()

    # Summary
    console.print(
        f"[dim]Total: {len(result.env_vars)} in .env, " f"{len(result.schema_vars)} in schema[/dim]"
    )


def format_audit_json(result: AuditResult) -> str:
    """Format audit result as JSON."""
    data = {
        "has_issues": result.has_issues,
        "total_vars": result.total_vars,
        "critical_count": result.critical_count,
        "warning_count": result.warning_count,
        "summary": {
            "placeholders_found": result.placeholders_found,
            "weak_secrets_found": result.weak_secrets_found,
            "test_values_found": result.test_values_found,
        },
        "findings": [
            {
                "key": finding.key,
                "severity": finding.severity.value,
                "category": finding.category,
                "message": finding.message,
                "value_preview": finding.value_preview,
            }
            for finding in result.findings
        ],
    }
    return json.dumps(data, indent=2)


def format_audit_rich(result: AuditResult, console: Console) -> None:
    """Format audit result using Rich."""
    console.print(f"[bold]Security Audit Results[/bold]\n")
    console.print(f"Total variables scanned: {result.total_vars}\n")

    if not result.has_issues:
        console.print("[green]✓[/green] No security issues found!", style="bold green")
        return

    # Summary
    if result.critical_count > 0:
        console.print(f"[red]✗[/red] {result.critical_count} critical issue(s)")
    if result.warning_count > 0:
        console.print(f"[yellow]⚠[/yellow] {result.warning_count} warning(s)")

    console.print()

    # Detailed findings
    if result.findings:
        table = Table(title="Security Findings", show_header=True)
        table.add_column("Severity", style="bold", width=10)
        table.add_column("Category", style="magenta", width=15)
        table.add_column("Variable", style="cyan", width=25)
        table.add_column("Message", width=40)

        for finding in result.findings:
            severity_style = "red" if finding.severity == Severity.ERROR else "yellow"
            severity_text = "ERROR" if finding.severity == Severity.ERROR else "WARN"

            table.add_row(
                f"[{severity_style}]{severity_text}[/{severity_style}]",
                finding.category,
                finding.key,
                finding.message,
            )

        console.print(table)

    # Summary counts
    console.print()
    if result.placeholders_found > 0:
        console.print(f"[red]•[/red] {result.placeholders_found} placeholder(s) detected")
    if result.test_values_found > 0:
        console.print(f"[red]•[/red] {result.test_values_found} test value(s) detected")
    if result.weak_secrets_found > 0:
        console.print(f"[yellow]•[/yellow] {result.weak_secrets_found} weak secret(s) detected")
