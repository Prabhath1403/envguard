"""Command-line interface for envguard."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from envguard import __version__
from envguard.app import EnvGuardApp

# Create Typer app
app = typer.Typer(
    name="envguard",
    help="A production-ready CLI tool for validating and auditing .env files",
    add_completion=False,
)

# Create console
console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"envguard version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """envguard - Validate and audit .env files with schema-based validation."""
    pass


@app.command()
def check(
    env_file: Optional[Path] = typer.Option(
        None,
        "--env",
        "-e",
        help="Path to .env file (auto-detected if not specified)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    schema_file: Optional[Path] = typer.Option(
        None,
        "--schema",
        "-s",
        help="Path to .env.schema.toml file (auto-detected if not specified)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
) -> None:
    """
    Validate .env file against schema.

    Checks that all required variables are present and validates formats.
    Returns exit code 0 for success, 1 for validation failure, 2 for errors.
    """
    app_instance = EnvGuardApp(console=console)
    _, exit_code = app_instance.check(
        env_path=env_file,
        schema_path=schema_file,
        output_json=json_output,
    )
    raise typer.Exit(code=exit_code)


@app.command()
def diff(
    env_file: Optional[Path] = typer.Option(
        None,
        "--env",
        "-e",
        help="Path to .env file (auto-detected if not specified)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    schema_file: Optional[Path] = typer.Option(
        None,
        "--schema",
        "-s",
        help="Path to .env.schema.toml file (auto-detected if not specified)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
) -> None:
    """
    Show differences between .env and schema.

    Displays variables that are:
    - Defined in schema but missing from .env
    - Present in .env but not documented in schema
    """
    app_instance = EnvGuardApp(console=console)
    _, exit_code = app_instance.diff(
        env_path=env_file,
        schema_path=schema_file,
        output_json=json_output,
    )
    raise typer.Exit(code=exit_code)


@app.command()
def audit(
    env_file: Optional[Path] = typer.Option(
        None,
        "--env",
        "-e",
        help="Path to .env file (auto-detected if not specified)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results as JSON",
    ),
) -> None:
    """
    Audit .env file for security issues.

    Detects:
    - Placeholder values (changeme, todo, xxxx, etc.)
    - Weak secrets (short passwords/tokens)
    - Test/example values (password, 12345, etc.)
    - Empty sensitive variables
    """
    app_instance = EnvGuardApp(console=console)
    _, exit_code = app_instance.audit(
        env_path=env_file,
        output_json=json_output,
    )
    raise typer.Exit(code=exit_code)


@app.command()
def init(
    env_file: Optional[Path] = typer.Option(
        None,
        "--env",
        "-e",
        help="Path to .env file (auto-detected if not specified)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output path for schema file (default: .env.schema.toml)",
        file_okay=True,
        dir_okay=False,
    ),
) -> None:
    """
    Initialize a new schema file from existing .env file.

    Generates a .env.schema.toml file based on the variables found
    in your .env file. You should review and customize the generated
    schema to add descriptions, set required flags, and define formats.
    """
    app_instance = EnvGuardApp(console=console)
    exit_code = app_instance.init(
        env_path=env_file,
        schema_path=output,
    )
    raise typer.Exit(code=exit_code)


@app.command()
def setup_ci(
    pre_commit: Optional[bool] = typer.Option(
        None,
        "--pre-commit/--no-pre-commit",
        help="Set up .pre-commit-config.yaml (prompted if not specified)",
    ),
) -> None:
    """
    Set up CI integration for the current project.

    Detects your Git repository root, creates a GitHub Actions workflow
    (.github/workflows/envguard.yml) that runs envguard check and audit
    on every push and pull request, and optionally creates a
    .pre-commit-config.yaml to enforce checks on every commit.
    """
    app_instance = EnvGuardApp(console=console)

    # If flag not explicitly passed, ask interactively
    if pre_commit is None:
        pre_commit = typer.confirm("Also set up pre-commit hooks?", default=False)

    _, exit_code = app_instance.setup_ci(setup_precommit=pre_commit)
    raise typer.Exit(code=exit_code)


if __name__ == "__main__":
    app()
