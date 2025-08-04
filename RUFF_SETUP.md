# Ruff Code Quality Setup

This project uses [Ruff](https://docs.astral.sh/ruff/) as a fast Python linter and formatter. The configuration is set up to enforce code quality standards and maintain consistency across the codebase.

## Quick Start

### Check code quality issues:
```bash
ruff check src/
```

### Auto-fix issues where possible:
```bash
ruff check src/ --fix
```

### Format code:
```bash
ruff format src/
```

### Check both linting and formatting:
```bash
ruff check src/ && ruff format --check src/
```

## Configuration Overview

The Ruff configuration in `pyproject.toml` includes:

### Enabled Rule Sets
- **F**: Pyflakes (logical errors)
- **E/W**: pycodestyle (PEP 8 style)
- **I**: isort (import organization)
- **N**: pep8-naming (naming conventions)
- **UP**: pyupgrade (modern Python syntax)
- **B**: flake8-bugbear (common bugs)
- **SIM**: flake8-simplify (code simplification)
- **C4**: flake8-comprehensions (comprehension improvements)
- **S**: bandit (security vulnerabilities)
- **ANN**: flake8-annotations (type annotations)
- **ASYNC**: flake8-async (async/await best practices)
- **G**: flake8-logging-format (logging best practices)
- **PL**: Pylint (comprehensive code quality)
- **RUF**: Ruff-specific improvements

### Key Settings
- **Python version**: 3.13
- **Line length**: 88 characters
- **Quote style**: Double quotes
- **Import sorting**: Enabled with first-party package recognition

### Per-file Exceptions
- **Tests**: Allow asserts, magic values, no type annotations required
- **Migrations**: Relaxed naming and annotation rules
- **Config files**: Allow hardcoded values (to be replaced with env vars)
- **`__init__.py`**: Allow unused imports

## Current Code Quality Status

After configuration, the codebase has:
- **66 total issues** identified
- **27 auto-fixable** issues
- Main issue categories:
  - Missing type annotations (31 issues)
  - Unsorted imports (16 issues)
  - Code modernization opportunities (7 issues)
  - Exception handling improvements (5 issues)

## Next Steps

1. **Auto-fix what's possible**:
   ```bash
   ruff check src/ --fix
   ruff format src/
   ```

2. **Gradually add type annotations** to improve code quality

3. **Set up pre-commit hooks** to catch issues before commits

4. **Integrate with CI/CD** to enforce quality standards

## IDE Integration

### VS Code
Install the Ruff extension and add to `settings.json`:
```json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.organizeImports": true,
            "source.fixAll": true
        }
    }
}
```

### PyCharm
Configure Ruff as external tool or use the Ruff plugin when available.

## Benefits

- **Fast**: 10-100x faster than traditional tools
- **Comprehensive**: Replaces multiple tools (black, isort, flake8, etc.)
- **Configurable**: Tailored to project needs
- **Auto-fixing**: Reduces manual work
- **Security**: Built-in vulnerability detection