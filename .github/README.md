# TMA Template

Production-ready Telegram Mini App template. Ships a **Litestar** REST API (served by Granian) and an **aiogram 3** Telegram bot with shared PostgreSQL storage, Alembic migrations, Dishka DI, and Fluent i18n.

**Requirements:** Python 3.13+, [uv](https://docs.astral.sh/uv/), Docker, [`just`](https://github.com/casey/just) (optional but recommended)

---

## 1. Prepare files

### 1.1. Copy config template

```shell
# For local development (API + bot)
cp config-example.yaml config.yaml

# For running tests (points to the test database)
cp config-example.yaml config-local.yaml
```

Edit both files and set `bot_token`, `admin_ids`, `bot_username`, and `auth.secret_key`.

### 1.2. Copy environment file

```shell
cp .env.example .env
```

`.env` controls Docker Compose variables (Postgres credentials, ports, `API_WORKERS`). The defaults in `.env.example` match `config-example.yaml`, so no changes are needed for a first run.

---

## 2. Install dependencies

```shell
uv venv
uv sync
```

---

## 3. Set up pre-commit

```shell
pre-commit install
```

Hooks run `ruff check --fix`, `ruff format`, and a security-only ruff pass on every commit.

---

## 4. Run tests

```shell
docker compose -f docker-compose-test.yml up -d
uv run pytest -n auto -ss -vv --maxfail=1
docker compose -f docker-compose-test.yml down -v
```

Or with `just`:

```shell
just test
```

Coverage threshold is 90%.

---

## 5. Local development

### 5.1. Start Postgres

```shell
docker compose up -d
# or
just db-up
```

### 5.2. Apply migrations

```shell
uv run alembic upgrade head
```

### 5.3. Run the API server

```shell
uv run granian src.presentation.api.app:create_app --factory --port 8080 --interface asgi --log --access-log --reload
# or
just api
```

Listens on `http://localhost:8080`.

### 5.4. Run the Telegram bot

```shell
uv run python -m src.presentation.bot.main
# or
just bot
```

---

## 6. Production deployment

### 6.1. Create production config

```shell
cp config-example.yaml config-prod.yaml
# Edit config-prod.yaml with production values
```

### 6.2. Start all services

```shell
docker compose -f docker-compose.prod.yml up -d
```

This starts:

- Postgres (no exposed port)
- Alembic migration runner (one-shot, runs before app starts)
- Telegram bot
- API server (host port **8000**)

### 6.3. View logs

```shell
docker compose -f docker-compose.prod.yml logs -f
```

### 6.4. Stop services

```shell
docker compose -f docker-compose.prod.yml down
```

---

## Linting

```shell
uv run ruff format src tests
uv run ruff check src tests --fix
# or
just lint
```
