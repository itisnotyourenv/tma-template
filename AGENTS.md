# Repository Guidelines

## Project Overview
TMA Template is a production-oriented Telegram Mini App starter. It combines:
- a Litestar REST API served by Granian
- an aiogram 3 Telegram bot
- shared PostgreSQL persistence via SQLAlchemy and Alembic
- Dishka dependency injection
- Fluent-based i18n

Primary entry points:
- `src/presentation/api/app.py` -> `create_app()` for the ASGI API
- `src/presentation/bot/main.py` -> `main()` for bot polling

## Architecture & Data Flow
The codebase follows a four-layer Clean Architecture with an inward dependency rule:

`presentation -> infrastructure -> application -> domain`

Core flow:
1. Presentation receives input from HTTP or Telegram handlers.
2. Handlers resolve interactors and services through Dishka.
3. Application interactors operate on DTOs and domain entities.
4. Domain defines entities, value objects, and repository protocols.
5. Infrastructure implements repositories, DB access, auth, config, and i18n.

Important architectural patterns:
- Domain entities are dataclasses, e.g. `src/domain/user/entity.py`.
- Domain value objects validate at the type boundary, e.g. `src/domain/user/vo.py`.
- Use cases are callable interactors implementing `Interactor[InputDTO, OutputDTO]` from `src/application/common/interactor.py`.
- Repositories are defined as domain/application protocols and implemented in `src/infrastructure/db/repos/`.
- ORM models do not cross into application/domain layers; use mappers in `src/infrastructure/db/mappers/`.
- DI is assembled at startup in `src/presentation/api/app.py` and `src/presentation/bot/main.py` using providers from `src/infrastructure/di/`.

## Key Directories
- `src/domain/` — core entities, value objects, repository interfaces
- `src/application/` — interactors, DTOs, application services, exceptions
- `src/infrastructure/` — config loading, auth, DI, SQLAlchemy models/repos/mappers, migrations, i18n
- `src/presentation/api/` — Litestar app, routers, auth/security, exception handlers
- `src/presentation/bot/` — aiogram routers, middleware, filters, keyboards/utilities
- `locales/` — Fluent translation files, currently `en/` and `ru/`
- `tests/unit/` — layer-oriented unit tests mirroring source structure
- `tests/integration/` — API and repository integration tests with real async DB setup
- `tests/utils/model_factories/` — factory-boy test data factories
- `scripts/` — helper scripts such as `scripts/generate_i18n_stubs.py`

## Development Commands
Canonical tooling is `uv` + `just`.

Setup:
```bash
uv venv
uv sync
cp config-example.yaml config.yaml
cp config-example.yaml config-test.yaml
cp .env.example .env
pre-commit install
```

Common commands:
```bash
just up             # start local services: postgres
uv run alembic upgrade head
just api            # run Litestar dev server on :8080
just bot            # run Telegram bot
just test           # start test DB, run pytest, tear down
just test-db-up     # start test DB without running tests
just lint           # ruff format + ruff check --fix
just type-check     # mypy src/
just generate-i18n  # regenerate i18n stubs
```

Direct equivalents are defined in `justfile` if `just` is unavailable.

## Runtime / Tooling Preferences
- Python `>=3.13` is required (`pyproject.toml`).
- Use `uv` as the package manager and runner; `uv.lock` is committed and CI validates it.
- Use `just` for repeatable local commands.
- Use Ruff for both formatting and linting; do not introduce Black/isort/flake8 side paths.
- API dev server uses Granian, not Uvicorn.
- Database is PostgreSQL via `asyncpg`; local/test containers are defined in `docker-compose*.yml`.
- Config is YAML loaded by `src/infrastructure/config.py`; development/test configs are local files, not environment-driven app config.

## Code Conventions & Common Patterns
### Layering rules
- Keep dependencies pointed inward.
- Do not pass SQLAlchemy ORM models outside infrastructure.
- Do not put transport concerns in domain/application layers.

### Interactors
- New use cases should follow the callable interactor pattern used in `src/application/`.
- Prefer explicit input/output DTOs over loose dicts.

### Value objects and mapping
- Preserve domain value objects instead of flattening to primitives too early.
- DB conversions belong in custom SQLAlchemy types and mappers under `src/infrastructure/db/models/types/` and `src/infrastructure/db/mappers/`.

### Dependency injection
- Register shared dependencies in Dishka providers under `src/infrastructure/di/`.
- Both API and bot startup compose provider instances plus config context.

### Async and error handling
- This is an async-first codebase; follow existing `async`/`await` patterns end-to-end.
- API exception handling is centralized in `src/presentation/api/exception.py` and wired in `src/presentation/api/app.py`.
- Prefer domain/application-specific exceptions over returning ambiguous failure values.

### i18n
- User-facing strings belong in Fluent files under `locales/`, not inline in handlers.
- Regenerate typed i18n helpers with `just generate-i18n` after changing translation files.

### Formatting and naming
- Ruff target is Python 3.13, line length 88, double quotes, spaces.
- Type annotations are expected broadly; tests have relaxed Ruff rules.
- Existing names are explicit and layer-oriented; follow file organization already present instead of inventing parallel abstractions.

## Testing & QA
Test stack from `pyproject.toml`:
- `pytest`
- `pytest-asyncio`
- `pytest-xdist`
- `pytest-cov`
- `pytest-timeout`
- `pytest-randomly`
- `factory-boy`
- `httpx` for API integration tests

Test expectations:
- Coverage floor is 90% (`--cov-fail-under=90`).
- Tests run in parallel by default with `-n auto --dist=worksteal`.
- Async tests use `asyncio_mode = auto`; usually no `@pytest.mark.asyncio` needed.
- Integration tests create worker-specific databases for xdist isolation in `tests/integration/conftest.py`.
- Coverage omits `src/presentation/bot/**/*`, so bot changes may need stronger targeted tests elsewhere to retain confidence.

Useful examples:
```bash
just test
uv run pytest tests/unit/application/user/test_service.py -x
uv run pytest tests/integration/api -x
```

## Important Files
- `pyproject.toml` — dependencies plus Ruff, pytest, and coverage configuration
- `justfile` — preferred local command entry points
- `config-example.yaml` — template for app config
- `.env.example` — Docker Compose environment defaults
- `docker-compose.yml` — local development PostgreSQL
- `docker-compose-test.yml` — test PostgreSQL
- `.github/workflows/ci.yml` — CI checks and execution order

## Assistant Notes
When helping in this repository:
- Start from `pyproject.toml`, `justfile`, and the relevant presentation entry point.
- Respect the clean-architecture boundary before proposing refactors.
- Search for an existing interactor, provider, mapper, or router pattern before adding a new one.
- Prefer commands through `uv run ...` and `just ...`.
- When changing behavior, check both the API and bot side if the change touches shared application/domain code.
