#!/bin/bash
# AgriAI backend runner
set -e

# Activate Python environment
source .venv/bin/activate 2>/dev/null || true

# Set the DATABASE_URL env var (defaults to SQLite)
export DATABASE_URL="${DATABASE_URL:-sqlite:///./agriai.db}"

# Run the FastAPI server
uvicorn backend.app:app --host "${APP_HOST:-0.0.0.0}" --port "${APP_PORT:-8000}" --reload

echo "Backend started on http://${APP_HOST:-localhost}:${APP_PORT:-8000}"