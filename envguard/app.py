"""Application orchestration layer."""

from pathlib import Path
from rich.console import Console

from envguard import auditor, diff_engine, formatter, parser, schema, utils, validator
from envguard.models import AuditResult, DiffResult, SetupCIResult, ValidationResult


class EnvGuardApp:
    """Main application orchestrator."""

    def __init__(self, console: Console | None = None) -> None:
        """Initialize the application."""
        self.console = console or Console()

    def check(
        self,
        env_path: Path | None = None,
        schema_path: Path | None = None,
        output_json: bool = False,
    ) -> tuple[ValidationResult, int]:
        """
        Validate .env file against schema.

        Args:
            env_path: Path to .env file (auto-detected if None)
            schema_path: Path to schema file (auto-detected if None)
            output_json: Output as JSON instead of Rich format

        Returns:
            Tuple of (ValidationResult, exit_code)
                exit_code: 0 = success, 1 = validation failure, 2 = error
        """
        try:
            # Find files
            if env_path is None:
                env_path = utils.find_env_file()
                if env_path is None:
                    self.console.print("[red]Error:[/red] .env file not found", style="bold red")
                    return (
                        ValidationResult(valid=False, issues=[], env_data={}, schema={}),
                        2,
                    )

            if schema_path is None:
                schema_path = utils.find_schema_file()
                if schema_path is None:
                    # Auto-generate schema from .env
                    schema_path = env_path.parent / ".env.schema.toml"
                    env_data_for_init = parser.parse_env_file(env_path)
                    schema.create_default_schema(schema_path, env_data_for_init)
                    self.console.print(
                        f"[yellow]ℹ[/yellow]  No schema found. Auto-generated: {schema_path}",
                    )
                    self.console.print(
                        "[dim]Tip: Edit .env.schema.toml to set required fields, formats, and descriptions.[/dim]\n"
                    )

            # Parse and load
            env_data = parser.parse_env_file(env_path)
            schema_data = schema.load_schema(schema_path)

            # Validate
            result = validator.validate(env_data, schema_data)

            # Output
            if output_json:
                self.console.print(formatter.format_validation_json(result))
            else:
                formatter.format_validation_rich(result, self.console)

            # Determine exit code
            exit_code = 0 if result.valid else 1
            return result, exit_code

        except (FileNotFoundError, ValueError, PermissionError) as e:
            self.console.print(f"[red]Error:[/red] {e}", style="bold red")
            return (
                ValidationResult(valid=False, issues=[], env_data={}, schema={}),
                2,
            )

    def diff(
        self,
        env_path: Path | None = None,
        schema_path: Path | None = None,
        output_json: bool = False,
    ) -> tuple[DiffResult, int]:
        """
        Show differences between .env and schema.

        Args:
            env_path: Path to .env file (auto-detected if None)
            schema_path: Path to schema file (auto-detected if None)
            output_json: Output as JSON instead of Rich format

        Returns:
            Tuple of (DiffResult, exit_code)
        """
        try:
            # Find files
            if env_path is None:
                env_path = utils.find_env_file()
                if env_path is None:
                    self.console.print("[red]Error:[/red] .env file not found", style="bold red")
                    return DiffResult(), 2

            if schema_path is None:
                schema_path = utils.find_schema_file()
                if schema_path is None:
                    self.console.print(
                        "[red]Error:[/red] .env.schema.toml file not found", style="bold red"
                    )
                    return DiffResult(), 2

            # Parse and load
            env_data = parser.parse_env_file(env_path)
            schema_data = schema.load_schema(schema_path)

            # Compute diff
            result = diff_engine.compute_diff(env_data, schema_data)

            # Output
            if output_json:
                self.console.print(formatter.format_diff_json(result))
            else:
                formatter.format_diff_rich(result, self.console)

            return result, 0

        except (FileNotFoundError, ValueError, PermissionError) as e:
            self.console.print(f"[red]Error:[/red] {e}", style="bold red")
            return DiffResult(), 2

    def audit(
        self,
        env_path: Path | None = None,
        output_json: bool = False,
    ) -> tuple[AuditResult, int]:
        """
        Audit .env file for security issues.

        Args:
            env_path: Path to .env file (auto-detected if None)
            output_json: Output as JSON instead of Rich format

        Returns:
            Tuple of (AuditResult, exit_code)
        """
        try:
            # Find env file
            if env_path is None:
                env_path = utils.find_env_file()
                if env_path is None:
                    self.console.print("[red]Error:[/red] .env file not found", style="bold red")
                    return AuditResult(), 2

            # Parse
            env_data = parser.parse_env_file(env_path)

            # Audit
            result = auditor.audit(env_data)

            # Output
            if output_json:
                self.console.print(formatter.format_audit_json(result))
            else:
                formatter.format_audit_rich(result, self.console)

            # Exit with error if critical issues found
            exit_code = 1 if result.critical_count > 0 else 0
            return result, exit_code

        except (FileNotFoundError, ValueError, PermissionError) as e:
            self.console.print(f"[red]Error:[/red] {e}", style="bold red")
            return AuditResult(), 2

    def init(
        self,
        env_path: Path | None = None,
        schema_path: Path | None = None,
    ) -> int:
        """
        Initialize a new schema file from an existing .env file.

        Args:
            env_path: Path to .env file (auto-detected if None)
            schema_path: Path for output schema file (default: .env.schema.toml)

        Returns:
            Exit code (0 = success, 2 = error)
        """
        try:
            # Find env file
            if env_path is None:
                env_path = utils.find_env_file()
                if env_path is None:
                    self.console.print("[red]Error:[/red] .env file not found", style="bold red")
                    return 2

            # Determine output path
            if schema_path is None:
                schema_path = env_path.parent / ".env.schema.toml"

            # Check if schema already exists
            if schema_path.exists():
                self.console.print(
                    f"[yellow]Warning:[/yellow] {schema_path} already exists. Overwriting...",
                    style="yellow",
                )

            # Parse env file
            env_data = parser.parse_env_file(env_path)

            # Create schema
            schema.create_default_schema(schema_path, env_data)

            self.console.print(
                f"[green]✓[/green] Schema created: {schema_path}", style="bold green"
            )
            self.console.print(f"[dim]Generated schema for {len(env_data)} variables[/dim]")
            self.console.print(
                "\n[yellow]Note:[/yellow] Please review and customize the generated schema."
            )

            return 0

        except (FileNotFoundError, ValueError, PermissionError) as e:
            self.console.print(f"[red]Error:[/red] {e}", style="bold red")
            return 2

    # -----------------------------------------------------------------
    # Workflow YAML template
    # -----------------------------------------------------------------

    _CI_WORKFLOW_TEMPLATE = """\
name: Validate Environment

on:
  push:
    branches: [main, master, develop]
  pull_request:
    branches: [main, master]

jobs:
  envguard:
    name: envguard check & audit
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install envguard
        run: pip install envguard

      - name: Validate .env schema
        run: envguard check --json

      - name: Security audit
        run: envguard audit --json
"""

    _PRECOMMIT_CONFIG_TEMPLATE = """\
repos:
  - repo: https://github.com/Prabhath1403/envguard
    rev: v0.1.0  # replace with the latest tag
    hooks:
      - id: envguard-check
      - id: envguard-audit
"""

    def setup_ci(
        self,
        project_path: Path | None = None,
        setup_precommit: bool = False,
    ) -> tuple[SetupCIResult, int]:
        """
        Set up CI integration for the current project.

        Steps:
        1. Detect Git repository root
        2. Create .github/workflows/envguard.yml
        3. Optionally create .pre-commit-config.yaml

        Args:
            project_path: Root path to use (auto-detected via git root if None)
            setup_precommit: Whether to create a .pre-commit-config.yaml

        Returns:
            Tuple of (SetupCIResult, exit_code)
        """
        result = SetupCIResult()

        # -- 1. Detect Git root ------------------------------------------------
        start = (project_path or Path.cwd()).resolve()
        git_root = utils.find_git_root(start)

        if git_root is None:
            self.console.print(
                "[red]Error:[/red] No Git repository found. " "Run [bold]git init[/bold] first.",
                style="bold red",
            )
            return result, 2

        result.git_detected = True
        result.project_root = git_root
        self.console.print(f"[green]✓[/green] Git repository detected: [bold]{git_root}[/bold]")

        # -- 2. Create GitHub Actions workflow ----------------------------------
        workflows_dir = git_root / ".github" / "workflows"
        workflow_path = workflows_dir / "envguard.yml"

        if workflow_path.exists():
            self.console.print(
                f"[yellow]⚠[/yellow]  Workflow already exists, skipping: "
                f"[dim]{workflow_path}[/dim]"
            )
            result.skipped_existing.append(str(workflow_path))
        else:
            workflows_dir.mkdir(parents=True, exist_ok=True)
            workflow_path.write_text(self._CI_WORKFLOW_TEMPLATE)
            result.workflow_created = True
            result.workflow_path = workflow_path
            self.console.print(f"[green]✓[/green] Created workflow: [bold]{workflow_path}[/bold]")

        # -- 3. Optionally set up pre-commit ------------------------------------
        if setup_precommit:
            precommit_path = git_root / ".pre-commit-config.yaml"

            if precommit_path.exists():
                self.console.print(
                    f"[yellow]⚠[/yellow]  pre-commit config already exists, skipping: "
                    f"[dim]{precommit_path}[/dim]"
                )
                result.skipped_existing.append(str(precommit_path))
            else:
                precommit_path.write_text(self._PRECOMMIT_CONFIG_TEMPLATE)
                result.precommit_created = True
                result.precommit_path = precommit_path
                self.console.print(
                    f"[green]✓[/green] Created pre-commit config: " f"[bold]{precommit_path}[/bold]"
                )
                self.console.print(
                    "\n[dim]Run [bold]pip install pre-commit && pre-commit install[/bold] "
                    "to activate the hooks.[/dim]"
                )
        else:
            self.console.print(
                "\n[dim]Tip: Re-run with [bold]--pre-commit[/bold] to also set up "
                "pre-commit hooks.[/dim]"
            )

        self.console.print("\n[bold green]✓ CI setup complete![/bold green]")
        return result, 0
