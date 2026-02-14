# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Telegram Mini App template: a Telegram bot (aiogram) + REST API (Litestar) with PostgreSQL, following Clean Architecture and DDD principles. Python 3.13, managed with UV.

## Common Commands

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
```

## Architecture

Four-layer Clean Architecture with inward dependency rule:

```
Presentation → Infrastructure → Application → Domain
```

### Domain (`src/domain/`)
Entities as dataclasses, Value Objects with validation (e.g., `UserId`, `FirstName`, `LanguageCode`), repository protocols (abstract interfaces). No infrastructure dependencies.

### Application (`src/application/`)
Interactors (use cases) inherit from `Interactor[InputDTO, OutputDTO]` and implement `__call__`. DTOs live here, not in domain. `UserService` handles upsert logic to avoid duplication across interactors.

### Infrastructure (`src/infrastructure/`)
- **db/models/**: SQLAlchemy ORM models with custom types for Value Objects
- **db/mappers/**: Bidirectional domain entity ↔ ORM model conversion
- **db/repos/**: Repository implementations (implement domain protocols)
- **db/migrations/**: Alembic migrations (script location: `src/infrastructure/db/migrations`)
- **di/**: Dishka dependency injection providers (`DBProvider`, `AuthProvider`, `I18nProvider`)
- **config.py**: Pydantic config loaded from YAML (`config.yaml` for dev, `config-local.yaml` for tests)

### Presentation (`src/presentation/`)
- **api/**: Litestar REST API (controllers, auth middleware, health check)
- **bot/**: Aiogram Telegram bot (routers for commands/settings/onboarding/admin, middleware for user & locale)

## Key Patterns

- **Value Objects**: All domain fields use VOs with built-in validation. Custom SQLAlchemy types (`src/infrastructure/db/models/types/`) map VOs to DB columns.
- **Mappers**: Never pass ORM models to application/domain layers. Use `UserMapper.to_domain()` / `UserMapper.to_model()`.
- **Interactor pattern**: Each use case is a callable class. Create new ones by subclassing `Interactor[InputDTO, OutputDTO]`.
- **DI with Dishka**: Providers register dependencies by scope. Integrated into both aiogram and Litestar.
- **i18n**: Fluent format (`.ftl` files) in `locales/{en,ru}/`. `FluentTranslatorHub` with English fallback.

## Testing

- Tests use `config-local.yaml` (copy from `config-example.yaml`)
- Test DB runs on port 5435 via `docker-compose-test.yml`
- pytest-xdist runs tests in parallel (`-n auto`); workers get isolated databases
- Factory-boy factories in `tests/utils/model_factories/`
- 90% coverage minimum enforced
- `asyncio_mode = "auto"` — no need for `@pytest.mark.asyncio`

## Configuration

Two config files needed for development:
- `config.yaml` — local dev (bot, API)
- `config-local.yaml` — tests

Both are gitignored. Copy from `config-example.yaml` and fill in bot token + credentials.

## Ruff

Target: Python 3.13, line length 88. Enforces type annotations (`ANN`), security checks (`S`/bandit), import sorting (`I`). Tests are exempt from annotation and security rules. Pre-commit hooks run ruff format + check on commit.