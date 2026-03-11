"""Tests for the setup-ci command."""

from io import StringIO
from pathlib import Path

from rich.console import Console

from envguard.app import EnvGuardApp


def make_app() -> tuple[EnvGuardApp, StringIO]:
    buf = StringIO()
    console = Console(file=buf, highlight=False, markup=False)
    return EnvGuardApp(console=console), buf


def make_git_repo(path: Path) -> Path:
    """Create a minimal fake git repo."""
    git_dir = path / ".git"
    git_dir.mkdir()
    return path


# --- Git detection ---


def test_setup_ci_no_git_repo(tmp_path):
    app, buf = make_app()
    result, code = app.setup_ci(project_path=tmp_path)
    assert code == 2
    assert result.git_detected is False
    assert "No Git repository" in buf.getvalue()


def test_setup_ci_detects_git(tmp_path):
    make_git_repo(tmp_path)
    app, _ = make_app()
    result, code = app.setup_ci(project_path=tmp_path)
    assert code == 0
    assert result.git_detected is True
    assert result.project_root == tmp_path


def test_setup_ci_detects_git_from_subdirectory(tmp_path):
    make_git_repo(tmp_path)
    sub = tmp_path / "src" / "deep"
    sub.mkdir(parents=True)
    app, _ = make_app()
    result, code = app.setup_ci(project_path=sub)
    assert code == 0
    assert result.git_detected is True
    assert result.project_root == tmp_path


# --- Workflow creation ---


def test_setup_ci_creates_workflow(tmp_path):
    make_git_repo(tmp_path)
    app, buf = make_app()
    result, code = app.setup_ci(project_path=tmp_path)
    assert code == 0
    assert result.workflow_created is True
    assert result.workflow_path is not None
    assert result.workflow_path.exists()


def test_setup_ci_workflow_content(tmp_path):
    make_git_repo(tmp_path)
    app, _ = make_app()
    result, _ = app.setup_ci(project_path=tmp_path)
    content = result.workflow_path.read_text()
    assert "envguard check" in content
    assert "envguard audit" in content
    assert "actions/checkout" in content
    assert "pip install envguard" in content


def test_setup_ci_workflow_path_is_correct(tmp_path):
    make_git_repo(tmp_path)
    app, _ = make_app()
    result, _ = app.setup_ci(project_path=tmp_path)
    expected = tmp_path / ".github" / "workflows" / "envguard.yml"
    assert result.workflow_path == expected


def test_setup_ci_skips_existing_workflow(tmp_path):
    make_git_repo(tmp_path)
    workflows_dir = tmp_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True)
    existing = workflows_dir / "envguard.yml"
    existing.write_text("# existing")
    app, buf = make_app()
    result, code = app.setup_ci(project_path=tmp_path)
    assert code == 0
    assert result.workflow_created is False
    assert str(existing) in result.skipped_existing
    assert existing.read_text() == "# existing"  # not overwritten


# --- Pre-commit setup ---


def test_setup_ci_no_precommit_by_default(tmp_path):
    make_git_repo(tmp_path)
    app, _ = make_app()
    result, _ = app.setup_ci(project_path=tmp_path, setup_precommit=False)
    assert result.precommit_created is False
    assert not (tmp_path / ".pre-commit-config.yaml").exists()


def test_setup_ci_creates_precommit(tmp_path):
    make_git_repo(tmp_path)
    app, _ = make_app()
    result, code = app.setup_ci(project_path=tmp_path, setup_precommit=True)
    assert code == 0
    assert result.precommit_created is True
    assert result.precommit_path is not None
    assert result.precommit_path.exists()


def test_setup_ci_precommit_content(tmp_path):
    make_git_repo(tmp_path)
    app, _ = make_app()
    result, _ = app.setup_ci(project_path=tmp_path, setup_precommit=True)
    content = result.precommit_path.read_text()
    assert "envguard-check" in content
    assert "envguard-audit" in content
    assert "Prabhath1403/envguard" in content


def test_setup_ci_skips_existing_precommit(tmp_path):
    make_git_repo(tmp_path)
    existing = tmp_path / ".pre-commit-config.yaml"
    existing.write_text("# existing precommit")
    app, _ = make_app()
    result, code = app.setup_ci(project_path=tmp_path, setup_precommit=True)
    assert code == 0
    assert result.precommit_created is False
    assert str(existing) in result.skipped_existing
    assert existing.read_text() == "# existing precommit"  # not overwritten


# --- Full run ---


def test_setup_ci_full_run_with_precommit(tmp_path):
    make_git_repo(tmp_path)
    app, buf = make_app()
    result, code = app.setup_ci(project_path=tmp_path, setup_precommit=True)
    assert code == 0
    assert result.git_detected is True
    assert result.workflow_created is True
    assert result.precommit_created is True
    assert "CI setup complete" in buf.getvalue()


def test_setup_ci_output_mentions_git(tmp_path):
    make_git_repo(tmp_path)
    app, buf = make_app()
    app.setup_ci(project_path=tmp_path)
    assert "Git repository detected" in buf.getvalue()
