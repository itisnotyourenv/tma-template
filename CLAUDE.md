# CLAUDE.md

Telegram Mini App template: Telegram bot (aiogram) + REST API (Litestar) with PostgreSQL. Clean Architecture + DDD. Python 3.13, UV.

## Commands

```bash
# Install dependencies
uv sync

# Start dev database
just up                     # or: docker-compose up -d

# Run migrations
alembic upgrade head

# Run API server (dev)
just api                    # uvicorn src.presentation.api.app:create_app --factory --port 8080 --reload

# Run Telegram bot (dev)
just bot                    # python -m src.presentation.bot.main

# Run tests (starts test DB, runs pytest, tears down)
just test

# Start test DB only (for running pytest manually)
just test-db-up

# Run a single test file
docker compose -f docker-compose-test.yml up -d
pytest tests/unit/application/user/test_create.py -x

# Lint and format
just lint                   # ruff format src tests && ruff check src tests --fix

# Create a migration
alembic revision --autogenerate -m "description"

# Regenerate i18n type stubs
just generate-i18n
```

## Architecture

Four-layer Clean Architecture: `Presentation → Infrastructure → Application → Domain`

Details in `.claude/rules/architecture.md`. Patterns in `.claude/rules/patterns.md`. Testing in `.claude/rules/testing.md`.

## Critical Rules

IMPORTANT: These rules MUST be followed at all times.

- Business logic MUST live in Interactors only. Never put logic in routers, controllers, or repositories.
- NEVER use repositories directly outside of Interactors. All data access goes through use cases.
- NEVER pass ORM models to application/domain layers. Use mappers: `UserMapper.to_domain()` / `UserMapper.to_model()`.
- NEVER import from `infrastructure` in `domain` or `application` layers.

## Git Conventions

- Conventional commits with emoji prefix: ✨ feat, 🐛 fix, ♻️ refactor, 📝 docs, ✅ test, 🔧 chore
- Format: `<emoji> <type>(<scope>): <description>`
- Example: `✨ feat(user): add language selection`
- Always run `just lint` before committing

## Configuration

Two config files (both gitignored, copy from `config-example.yaml`):
- `config.yaml` — local dev (bot, API)
- `config-local.yaml` — tests

## Ruff

Target: Python 3.13, line length 88. Pre-commit hooks run ruff format + check.
