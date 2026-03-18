#!/bin/sh
set -e

echo "Starting Telegram Bot..."

exec uv run python -m src.presentation.bot.main
