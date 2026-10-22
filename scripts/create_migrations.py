#!/usr/bin/env python3
"""
Create initial Alembic migrations for the AgriAI project.

This script creates the first migration that includes:
- All tables from backend.models (users, farms, soil_tests, etc.)
- Foreign key constraints and indexes
- Initial data (crops)

Uses SQLite by default. Set DATABASE_URL to a PostgreSQL URL to
target a different database.
"""
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from backend.models import Base

# Read the inline SQL init script from database/init.sql
with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "init.sql"), "r") as _f:
    INIT_SQL = _f.read()

# Database configuration (defaults to SQLite)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agriai.db")


def main():
    """Create database and apply initial schema."""
    print("=" * 60)
    print("AgriAI Database Migration - Initial Schema")
    print("=" * 60)

    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        print(f"Connecting to: {DATABASE_URL.split('@')[-1]}")

        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully")

        # Apply custom initialization SQL (if any)
        if INIT_SQL:
            print("Applying custom initialization SQL...")
            with engine.connect() as conn:
                conn.execute(text(INIT_SQL))
                conn.commit()
            print("Custom SQL applied")

        print("=" * 60)
        print("Database setup completed successfully!")
        print("=" * 60)

    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()