#!/usr/bin/env python3
"""
Ingestion script for soil test data.

Supports two sources:
1. Farmer-entered (user input via API)
2. Government soil data (district-level, where permitted)

This script loads synthetic data for development/testing only.
"""
import pandas as pd
import sys
import os
from datetime import datetime, date

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.common.data_utils import (
    DataProvenanceTracker,
    ingest_soil_data,
    clean_soil_test_data,
    validate_and_clean_data,
)


def main():
    """Load soil test data for development/testing."""
    print("=" * 60)
    print("AgriAI: Soil Test Data Ingestion")
    print("=" * 60)
    print("WARNING: Loading synthetic data for development only.")
    print("Replace with real farmer-entered data via the API.")
    print("=" * 60)
    print()

    # 1. Generate synthetic soil data
    print("Step 1: Generating synthetic soil test data...")
    soil_data = [
        {
            "farm_id": 1,
            "ph": 7.2,
            "nitrogen": 12.5,
            "phosphorus": 8.3,
            "potassium": 45.0,
            "organic_carbon": 0.8,
            "test_date": "2024-09-15",
        },
        {
            "farm_id": 1,
            "ph": 6.8,
            "nitrogen": 15.0,
            "phosphorus": 10.2,
            "potassium": 52.0,
            "organic_carbon": 1.1,
            "test_date": "2024-09-15",
        },
        {
            "farm_id": 2,
            "ph": 5.8,
            "nitrogen": 8.2,
            "phosphorus": 6.5,
            "potassium": 30.0,
            "organic_carbon": 0.5,
            "test_date": "2024-09-20",
        },
    ]
    df = pd.DataFrame(soil_data)
    print(f"  - Generated {len(df)} soil test records")

    # 2. Validate and clean
    print("Step 2: Validating and cleaning soil data...")
    required = ["farm_id", "ph", "nitrogen", "phosphorus", "potassium", "organic_carbon"]
    df = validate_and_clean_data(df, source="user_entered", required_columns=required)
    cleaned = clean_soil_test_data(df, source="user_entered")

    # 3. Add provenance metadata
    print("Step 3: Adding provenance metadata...")
    for _, row in cleaned.iterrows():
        provenance = DataProvenanceTracker.wrap_provenance(
            record=row.to_dict(),
            source="user_entered",
            source_record_id=None,
            obs_date=row["test_date"],
            geo_level="farm",
            crop="unknown",
            validation_status="synthetic"
        )
        print(f"  - Farm {provenance['farm_id']}: pH={provenance['ph']}, "
              f"status={provenance['_validation_status']}")

    # 4. Ingest into database
    print("Step 4: Ingesting soil tests into database...")
    from sqlalchemy.orm import Session
    from backend.database import engine, Base
    from sqlalchemy.orm import sessionmaker

    # Create tables if not exist
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    count = ingest_soil_data(
        session=session,
        farm_id=1,
        soil_data=cleaned.to_dict(orient="records"),
        source="user_entered",
        validation_status="synthetic"
    )

    session.close()

    print()
    print("=" * 60)
    print(f"Ingested {count} soil test records successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()