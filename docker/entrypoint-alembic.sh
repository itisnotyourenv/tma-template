#!/bin/sh
set -e

echo "Running Alembic migrations..."

if alembic upgrade head; then
	echo "Migrations completed successfully."
else
	status=$?
	echo "Alembic migrations failed with exit code ${status}." >&2
	exit "$status"
fi
