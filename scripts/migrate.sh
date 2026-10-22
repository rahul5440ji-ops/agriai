#!/bin/bash
# AgriAI database migration script
set -e

echo "Running AgriAI database migrations..."

# Activate Python environment
source .venv/bin/activate 2>/dev/null || true

# Set the DATABASE_URL env var (defaults to SQLite)
export DATABASE_URL="${DATABASE_URL:-sqlite:///./agriai.db}"

# Run Alembic upgrade to head
alembic upgrade head

echo "Migrations completed successfully."