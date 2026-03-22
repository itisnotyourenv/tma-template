#!/bin/sh
set -e

API_WORKERS=${API_WORKERS:-4}

echo "Starting Granian with $API_WORKERS workers..."

if granian src.presentation.api.app:create_app \
    --factory \
    --host 0.0.0.0 --port 8080 \
    --interface asgi \
    --workers "$API_WORKERS" \
    --log --log-level info; then
    echo "Granian exited successfully."
else
    status=$?
    echo "Granian failed with exit code ${status}." >&2
    exit "$status"
fi
