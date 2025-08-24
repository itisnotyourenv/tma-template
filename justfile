# Docker Compose shortcuts
up:
    docker-compose up -d

down:
    docker-compose down

restart:
    docker-compose restart

# Database only
db-up:
    docker-compose up -d postgres

db-down:
    docker-compose stop postgres

db-logs:
    docker-compose logs -f postgres

# Application
app-up:
    docker-compose up -d app

app-logs:
    docker-compose logs -f app

# Development setup
setup:
    docker-compose up -d postgres
    @echo "PostgreSQL is starting up..."
    @echo "Database will be available at localhost:5432"
    @echo "Connection: postgresql://dev_user:dev_password@localhost:5432/ask_app"

# Clean up
clean:
    docker-compose down -v
    docker-compose rm -f

# View logs
logs:
    docker-compose logs -f

# Status
status:
    docker-compose ps

api:
    uvicorn src.presentation.api.app:create_app --factory --port 8080 --reload

test:
    docker compose -f docker-compose-test.yml up --build -d
    pytest -n auto -ss -vv --maxfail=1
    docker compose -f docker-compose-test.yml down -v

just test-db-up:
    docker compose -f docker-compose-test.yml up --build -d
