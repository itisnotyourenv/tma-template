#!/bin/sh
set -e

# Get workers count from environment variable, default to 4
API_WORKERS=${API_WORKERS:-4}

echo "Starting Gunicorn with $API_WORKERS workers..."

exec uv run gunicorn src.presentation.api.app:create_app \
    --bind 0.0.0.0:8000 \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers "$API_WORKERS" \
    --access-logfile - \
    --error-logfile - \
    --preload
