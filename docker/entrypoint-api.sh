#!/bin/sh
set -e

# Get workers count from environment variable, default to 4
API_WORKERS=${API_WORKERS:-4}

echo "Starting Gunicorn with $API_WORKERS workers..."

exec uv run granian src.presentation.api.app:create_app \
    --factory \
    --host 0.0.0.0 --port 8080 \
    --interface asgi \
    --workers "$API_WORKERS" \
    --log --log-level info
