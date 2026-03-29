# Testing

## Setup

- Tests use `config-local.yaml` (copy from `config-example.yaml`)
- Test DB runs on port 5435 via `docker-compose-test.yml`
- `just test` — starts test DB, runs pytest, tears down
- `just test-db-up` — start test DB only (for running pytest manually)

## Running Tests

```bash
# Full suite
just test

# Single file
docker compose -f docker-compose-test.yml up -d
pytest tests/unit/application/user/test_create.py -x
```

## Pytest Configuration

- `asyncio_mode = "auto"` — no need for `@pytest.mark.asyncio`
- pytest-xdist: parallel execution (`-n auto`, `--dist=worksteal`)
- Workers get isolated databases (`worker_db_{worker_id}`)
- 90% coverage minimum enforced (`--cov-fail-under=90`)
- Test timeout: 30 seconds
- Random order with fixed seed (`--randomly-seed=42`)

## Test Structure

- `tests/unit/` — unit tests with mocks
- `tests/integration/` — tests with real DB and DI container
- `tests/utils/model_factories/` — Factory-boy factories

## Patterns

- Class-based test organization (`class TestCreateUserInteractor`)
- Fixtures for mocks, DTOs, domain entities
- `AsyncMock` for async dependencies
- `@pytest.mark.parametrize` for multiple scenarios

## Factories

- Base: `BaseFactory(SQLAlchemyModelFactory)` in `tests/utils/model_factories/base.py`
- `create_entity()` async helper — creates ORM model and commits
- Factories registered as pytest plugins in `tests/conftest.py`
- Fixture `create_user` returns async factory callable with **kwargs

## Integration Test Fixtures

Key fixtures in `tests/integration/conftest.py`:
- `test_config` — loads `config-local.yaml`
- `sqlalchemy_engine` — worker-specific AsyncEngine
- `async_session_maker` — AsyncSession factory
- `dishka_container_for_tests` — full DI container
- `test_client` / `authenticated_client` — httpx AsyncClient
