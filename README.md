# envguard

A production-ready Python CLI tool for validating and auditing `.env` files using schema-based validation.

## Features

- ✅ **Schema-based validation** - Define expected environment variables in `.env.schema.toml`
- 🔍 **Format validation** - Validate URLs, integers, booleans, and strings
- 🔒 **Security auditing** - Detect placeholders, weak secrets, and test values
- 📊 **Rich CLI output** - Beautiful terminal output using Rich
- 🤖 **CI/CD friendly** - JSON output mode and proper exit codes
- 🎯 **Type-safe** - Full type hints and modern Python 3.11+ support

## Installation

### From PyPI (when published)

```bash
pip install envguard
```

### From source

```bash
git clone https://github.com/yourusername/envguard.git
cd envguard
pip install -e .
```

## Quick Start

### 1. Initialize a schema from your existing `.env` file

```bash
envguard init
```

This creates a `.env.schema.toml` file based on your current `.env` variables.

### 2. Validate your `.env` file

```bash
envguard check
```

### 3. Audit for security issues

```bash
envguard audit
```

### 4. Compare .env against schema

```bash
envguard diff
```

## Commands

### `envguard check`

Validate `.env` file against schema.

```bash
# Auto-detect .env and .env.schema.toml files
envguard check

# Specify file paths
envguard check --env .env.production --schema .env.schema.toml

# JSON output for CI/CD
envguard check --json
```

**Exit codes:**
- `0` - Validation passed
- `1` - Validation failed (missing required variables or format errors)
- `2` - Internal error (file not found, parse error, etc.)

### `envguard diff`

Show differences between `.env` and schema.

```bash
# Show missing and undocumented variables
envguard diff

# JSON output
envguard diff --json
```

### `envguard audit`

Audit `.env` file for security issues.

```bash
# Check for weak secrets, placeholders, test values
envguard audit

# JSON output
envguard audit --json
```

Detects:
- 🚨 Placeholder values (`changeme`, `todo`, `xxxx`)
- 🚨 Test/example values (`password`, `12345`, `example`)
- ⚠️  Weak secrets (short passwords/tokens)
- ⚠️  Empty sensitive variables

**Exit codes:**
- `0` - No critical issues found
- `1` - Critical issues found (placeholders or test values)
- `2` - Internal error

### `envguard init`

Initialize a new schema file from existing `.env`.

```bash
# Create .env.schema.toml
envguard init

# Custom paths
envguard init --env .env.production --output .env.prod.schema.toml
```

## Schema Format

The schema is defined in TOML format (`.env.schema.toml`):

```toml
[DATABASE_URL]
required = true
format = "url"
description = "PostgreSQL connection string"

[DEBUG]
required = false
format = "bool"
default = "false"
description = "Enable debug mode"

[PORT]
required = false
format = "int"
default = "8000"
description = "Application port"

[API_KEY]
required = true
format = "string"
description = "API authentication key"
```

### Schema Fields

- `required` (bool) - Whether the variable must be present in `.env`
- `format` (string) - Expected format: `string`, `int`, `bool`, `url`
- `default` (string) - Default value if not present in `.env`
- `description` (string) - Human-readable description

## Examples

See the [`examples/`](examples/) directory for sample `.env` and `.env.schema.toml` files.

## Use Cases

### Local Development

```bash
# Check your local .env file
envguard check

# Audit for accidentally committed secrets
envguard audit
```

### CI/CD Pipeline

```yaml
# .github/workflows/validate-env.yml
name: Validate Environment
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install envguard
        run: pip install envguard
      - name: Validate .env schema
        run: envguard check --env .env.example --json
      - name: Security audit
        run: envguard audit --env .env.example --json
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: envguard-check
        name: Validate .env files
        entry: envguard check
        language: system
        pass_filenames: false
      - id: envguard-audit
        name: Audit .env security
        entry: envguard audit
        language: system
        pass_filenames: false
```

## Architecture

envguard follows clean architecture principles with strict separation of concerns:

```
envguard/
├── cli.py           # CLI definitions (Typer)
├── app.py           # Application orchestration layer
├── parser.py        # .env file parsing
├── schema.py        # .env.schema.toml loading
├── models.py        # Data models (dataclasses)
├── validator.py     # Validation engine
├── diff_engine.py   # Diff computation
├── auditor.py       # Security auditing
├── formatter.py     # Output formatting (Rich/JSON)
└── utils.py         # Helper functions
```

## Development

### Install development dependencies

```bash
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Code formatting

```bash
black envguard/
```

### Type checking

```bash
mypy envguard/
```

## Requirements

- Python 3.11+
- typer >= 0.9.0
- rich >= 13.0.0

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Roadmap

- [ ] Support for `.env.local`, `.env.production` variants
- [ ] Custom validation rules via plugins
- [ ] Integration with popular secret managers
- [ ] Support for encrypted environment variables
- [ ] Auto-fix mode for common issues
- [ ] IDE extensions (VS Code, PyCharm)

## Credits

Built with:
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting

---

**envguard** - Keep your environment variables safe and validated! 🛡️
