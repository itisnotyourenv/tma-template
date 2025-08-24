# Setup project

## 1. Prepare files

### 1. Copy `config-example.yaml` to `config-local.yaml`
```shell
cp config-example.yaml config-local.yaml
```

### 2. Paste BOT Token and init-data from your BOT to the `config-local.yaml`

## 2. Setup UV for this project

### 1. Create a virtual environment
```shell
uv venv
```

### 2. Install dependencies from `pyproject.toml`
```shell
uv sync
```


## 3. Ensure everything works
### 1 Run tests

With Just
```shell
just test
```

With shell command
```shell
docker compose -f docker-compose-test.yml up --build -d
pytest
docker compose -f docker-compose-test.yml down -v
```