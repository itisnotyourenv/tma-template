#!/bin/sh
set -e

echo "Starting Telegram Bot..."

if python -m src.presentation.bot.main; then
	echo "Telegram Bot exited successfully."
else
	status=$?
	echo "Telegram Bot failed with exit code ${status}." >&2
	exit "$status"
fi
