# Docker Setup Design

## Overview

Add bot and API services to Docker configuration, with separate files for local development and production.

## Decisions

- **Local dev**: Only Postgres in Docker; bot, API, and alembic run locally
- **Production**: Full stack in Docker (Postgres, Alembic, Bot, API)
- **Migrations**: One-shot alembic service runs before bot/API start
- **Configuration**: Mount `config.yaml` files as volumes
- **Dockerfiles**: Separate files for bot and API

## File Changes

| Action | File |
|--------|------|
| Delete | `Dockerfile.dev` |
| Create | `Dockerfile.bot` |
| Create | `Dockerfile.api` |
| Create | `docker-compose.prod.yml` |
| No change | `docker-compose.yml` |
| No change | `docker-compose-test.yml` |

## Implementation

### Dockerfile.bot

```dockerfile
FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

ENV PYTHONPATH=/app/src

CMD ["uv", "run", "python", "-m", "src.presentation.bot.main"]
```

### Dockerfile.api

```dockerfile
FROM python:3.13-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.presentation.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.prod.yml

```yaml
version: '3.8'
name: "production"

services:
  postgres:
    image: postgres:17-alpine
    container_name: prod_postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 3

  alembic:
    build:
      context: .
      dockerfile: Dockerfile.bot
    command: ["uv", "run", "alembic", "upgrade", "head"]
    volumes:
      - ./config-prod.yaml:/app/config.yaml:ro
    depends_on:
      postgres:
        condition: service_healthy

  bot:
    build:
      context: .
      dockerfile: Dockerfile.bot
    volumes:
      - ./config-prod.yaml:/app/config.yaml:ro
    depends_on:
      alembic:
        condition: service_completed_successfully

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    volumes:
      - ./config-prod.yaml:/app/config.yaml:ro
    depends_on:
      alembic:
        condition: service_completed_successfully

volumes:
  postgres_data:
```

## Workflows

### Local Development

```bash
docker compose up -d                        # Start Postgres
alembic upgrade head                        # Run migrations locally
python -m src.presentation.bot.main         # Run bot
uvicorn src.presentation.api.app:app --reload  # Run API (separate terminal)
```

### Production

```bash
docker compose -f docker-compose.prod.yml up -d
# Alembic runs automatically, then bot + API start
```
