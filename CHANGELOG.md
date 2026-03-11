# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-03-11

### Added
- `envguard check` — validate `.env` file against a TOML schema
- `envguard audit` — security audit for placeholders, weak secrets, and test values
- `envguard diff` — show differences between `.env` and schema
- `envguard init` — auto-generate schema from an existing `.env` file
- Schema-based validation with `string`, `int`, `bool`, and `url` format validators
- Rich terminal output with tables and color-coded severity
- JSON output mode (`--json`) for CI/CD integration
- Proper exit codes: `0` (pass), `1` (fail), `2` (error)
- Auto-discovery of `.env` and `.env.schema.toml` files up to 5 directory levels up
- Sensitive value masking in output
- Full type hints and mypy strict mode
- Comprehensive test suite (95 tests across all modules)
- GitHub Actions CI/CD pipeline
- pre-commit hook support

[Unreleased]: https://github.com/Prabhath1403/envguard/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Prabhath1403/envguard/releases/tag/v0.1.0
