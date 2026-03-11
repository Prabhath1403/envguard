# Development Setup

## Quick Start

1. **Clone the repository**
   ```bash
   cd /home/prabhath/Documents/projects/envguard
   ```

2. **Create a virtual environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify installation**
   ```bash
   envguard --version
   ```

5. **Try with examples**
   ```bash
   cd examples/
   envguard check
   envguard audit
   envguard diff
   ```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=envguard --cov-report=html

# Run specific test file
pytest tests/test_validator.py
```

## Code Quality

```bash
# Format code
black envguard/

# Type checking
mypy envguard/

# Check formatting (without changing)
black --check envguard/
```

## Project Structure

```
envguard/
├── envguard/              # Main package
│   ├── __init__.py       # Package initialization
│   ├── cli.py            # CLI interface (Typer)
│   ├── app.py            # Application orchestration
│   ├── models.py         # Data models
│   ├── parser.py         # .env file parser
│   ├── schema.py         # Schema loader
│   ├── validator.py      # Validation logic
│   ├── diff_engine.py    # Diff computation
│   ├── auditor.py        # Security auditing
│   ├── formatter.py      # Output formatting
│   └── utils.py          # Utilities
├── examples/              # Example files
│   ├── .env              # Sample .env file
│   └── .env.schema.toml  # Sample schema
├── tests/                 # Test suite (to be added)
├── pyproject.toml        # Project configuration
├── README.md             # Documentation
└── LICENSE               # MIT License
```

## Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Pure Functions**: Business logic is separated from I/O
3. **Type Safety**: Full type hints throughout
4. **Testability**: All components designed for easy testing
5. **Professional Architecture**: Follows patterns from tools like flake8, black

## Adding New Format Validators

Edit `envguard/validator.py`:

```python
def validate_format(key: str, value: str, format_type: str) -> ValidationIssue | None:
    # Add your new format type
    elif format_type == "email":
        if "@" not in value:
            return ValidationIssue(...)
```

## Adding New Audit Rules

Edit `envguard/auditor.py`:

```python
def audit(env_data: dict[str, str]) -> AuditResult:
    # Add your new audit check
    if is_my_custom_check(key, value):
        findings.append(AuditFinding(...))
```

## Building for Distribution

```bash
# Build package
python -m build

# Install locally from wheel
pip install dist/envguard-0.1.0-py3-none-any.whl

# Check the package before publishing
twine check dist/*

# Upload to PyPI (when ready)
twine upload dist/*
```

## Releasing a New Version

1. **Update the version** in `envguard/__init__.py` and `pyproject.toml`
2. **Add a changelog entry** in `CHANGELOG.md` under `[Unreleased]`
3. **Commit your changes**
   ```bash
   git add .
   git commit -m "chore: bump version to v0.X.Y"
   ```
4. **Create and push a version tag** — this triggers the publish workflow automatically
   ```bash
   git tag v0.X.Y
   git push origin main --tags
   ```

The `publish.yml` GitHub Actions workflow will:
- Run the full test suite
- Build the distribution packages
- Publish to PyPI via OIDC trusted publishing (no API token needed)
- Create a GitHub Release with the changelog entry

### PyPI Trusted Publishing Setup

Before your first release, configure trusted publishing on PyPI:

1. Go to [pypi.org](https://pypi.org) → Your account → Publishing
2. Add a new publisher:
   - **Owner**: `Prabhath1403`
   - **Repository**: `envguard`
   - **Workflow**: `publish.yml`
   - **Environment**: `pypi`
3. Create a `pypi` environment in your GitHub repo settings → Environments

