# Setup project

## 1. Prepare files

#### 1.1 Copy `config-example.yaml` to `config-local.yaml` (for tests)
```shell
cp config-example.yaml config-local.yaml
```

#### 1.2. Copy `config-example.yaml` to `config.yaml` (for local development)
```shell
cp config-example.yaml config.yaml
```

#### 1.3. Paste BOT Token and init-data from your BOT to the config files

#### 1.4. Create and configure .env file
```shell
cp .env.example .env
# Edit .env and set your database credentials if needed
```

## 2. Setup UV for this project

#### 2.1. Create a virtual environment
```shell
uv venv
```

#### 2.2. Install dependencies from `pyproject.toml`
```shell
uv sync
```


## 3. Ensure everything works
#### 3.1 Run tests
```shell
docker compose -f docker-compose-test.yml up --build -d
uv run pytest
docker compose -f docker-compose-test.yml down -v
```

## 4. Local Development

#### 4.1 Start Postgres
```shell
docker compose up -d
```

#### 4.2 Run migrations
```shell
uv run alembic upgrade head
```

#### 4.3 Run Litestar API
```shell
uv run uvicorn src.presentation.api.app:create_app --host 0.0.0.0 --port 8080
```

#### 4.4 Run Telegram Bot
```shell
uv run python -m src.presentation.bot.main
```

## 5. Production Deployment

#### 5.1 Create production config
```shell
cp config-example.yaml config-prod.yaml
# Edit config-prod.yaml with production values
```

#### 5.2 Start all services
```shell
docker compose -f docker-compose.prod.yml up -d
```

This starts:
- Postgres database
- Alembic migrations (runs automatically)
- Telegram Bot
- API server (port 8000)

#### 5.3 View logs
```shell
docker compose -f docker-compose.prod.yml logs -f
```

#### 5.4 Stop services
```shell
docker compose -f docker-compose.prod.yml down
```

# Setup Pre-Commit
### 1. Initialize pre-commit
```shell
pre-commit install
```
