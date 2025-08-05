# GitHub Actions CI/CD Configuration

This directory contains GitHub Actions workflows for automated testing, code quality enforcement, and deployment processes.

## Workflows Overview

### 🔄 Main CI Pipeline (`ci.yml`)

Runs on every push to `main`/`develop` branches and all pull requests.

**Jobs:**
1. **Code Quality** - Ruff linting and formatting verification
2. **Tests** - Full test suite with PostgreSQL database
3. **Security** - Security vulnerability scanning
4. **Type Checking** - MyPy static type analysis
5. **Build Check** - Application import and startup verification

**Features:**
- ⚡ **Fast builds** with uv dependency caching
- 🐘 **PostgreSQL integration** for realistic test environment  
- 🛡️ **Security scanning** with Bandit via Ruff
- 📊 **Code coverage** reporting with Codecov integration
- 🐍 **Python 3.13** support with matrix testing capability

### ✅ PR Validation (`pr-validation.yml`)  

Runs additional validation checks on pull requests.

**Jobs:**
1. **PR Format** - Semantic commit message validation
2. **Dependencies** - Lock file synchronization verification
3. **Security** - Enhanced security checks for configuration files
4. **Required Files** - Ensures essential files are present

**Requirements:**
- 📝 Semantic commit messages (feat, fix, docs, etc.)
- 🔒 Synchronized uv.lock file
- 📁 Required configuration files present
- 🔐 No secrets in configuration files

## Status Checks

All pull requests must pass these checks before merging:

| Check | Description | Command |
|-------|-------------|---------|
| 🧹 **Linting** | Code style and error detection | `ruff check src/ tests/` |
| 🎨 **Formatting** | Code formatting consistency | `ruff format --check src/ tests/` |
| 🧪 **Tests** | Unit and integration tests | `pytest tests/ -v` |
| 🛡️ **Security** | Security vulnerability scan | `ruff check --select=S src/` |
| 🏗️ **Build** | Application can start successfully | Import verification |

## Local Development

### Run CI Checks Locally

```bash
# Install dependencies
uv sync --extra dev

# Run all checks that CI runs
ruff check src/ tests/ --output-format=github
ruff format src/ tests/ --check
pytest tests/ -v --cov=src

# Run security scan
ruff check src/ --select=S

# Type checking (optional)
mypy src/ --ignore-missing-imports
```

### Pre-commit Hooks

Set up pre-commit hooks to catch issues before committing:

```bash
# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

## Performance Optimizations

### Dependency Caching
- **uv caching** reduces build times by ~60%
- **Cache key** based on `uv.lock` for reliability
- **Automatic invalidation** when dependencies change

### Parallel Execution
- **Jobs run in parallel** where possible
- **Matrix builds** for multiple environments
- **Fail-fast disabled** to see all issues

### Selective Execution
- **Path filtering** to skip unnecessary jobs
- **Draft PR exclusion** for PR validation
- **Conditional steps** based on file changes

## Security Features

### Automated Scanning
- **Bandit integration** via Ruff for Python security issues
- **Configuration file scanning** for potential secrets
- **Dependency vulnerability** checking (planned)

### Access Control
- **Read-only permissions** for most jobs
- **Minimal token usage** where required
- **Environment isolation** between jobs

## Branch Protection

Recommended branch protection settings for `main` branch:

```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Code Quality (Ruff)",
      "Tests",
      "Security Scan (Bandit)",
      "Build Check",
      "Validate PR Format"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null
}
```

## Troubleshooting

### Common Issues

**Ruff formatting failures:**
```bash
# Fix formatting locally
ruff format src/ tests/
git add . && git commit -m "fix: format code"
```

**Test failures:**
```bash
# Run tests with verbose output
pytest tests/ -v --tb=long

# Run specific test
pytest tests/path/to/test.py::test_name -v
```

**Lock file out of sync:**
```bash
# Update lock file
uv lock
git add uv.lock && git commit -m "chore: update dependencies"
```

### CI Performance Issues

1. **Check dependency cache** - Ensure `uv.lock` hasn't changed unnecessarily
2. **Review test efficiency** - Long-running tests slow down feedback
3. **Monitor resource usage** - Jobs may need more memory/CPU

## Contributing

When adding new workflows:

1. **Test locally** with `act` or similar tools
2. **Use minimal permissions** for security
3. **Add comprehensive comments** for complex logic
4. **Update this documentation** with changes
5. **Consider performance impact** on CI/CD pipeline

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Ruff Configuration](https://docs.astral.sh/ruff/)
- [Pre-commit Hooks](https://pre-commit.com/)