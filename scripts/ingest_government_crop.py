#!/usr/bin/env python3
"""
Ingestion script for Government of India crop production data.

NOTE: This script loads synthetic data for development and testing only.
It is marked clearly so it can be replaced with real data.gov.in API calls
when access is obtained.

Always retains provenance metadata.
"""
import pandas as pd
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.common.data_utils import (
    DataProvenanceTracker,
    UnitNormalizer,
    ingest_crop_data,
    validate_and_clean_data,
)


def main():
    """Load government crop data for development."""
    print("=" * 60)
    print("AgriAI: Government Crop Data Ingestion")
    print("=" * 60)
    print("WARNING: Loading synthetic data for development only.")
    print("This data is NOT presented as real agricultural statistics.")
    print("=" * 60)
    print()

    # 1. Create synthetic dataset
    data = {
        "state": ["Maharashtra", "Rajasthan", "Uttar Pradesh", "Madhya Pradesh",
                  "Punjab", "Haryana", "Karnataka", "Tamil Nadu"],
        "district": ["Pune", "Jaipur", "Agra", "Bhopal", "Ludhiana",
                     "Karnal", "Bengaluru", "Chennai"],
        "crop": ["wheat", "wheat", "rice", "wheat", "rice",
                 "rice", "groundnut", "groundnut"],
        "season": ["rabi", "kharif", "rabi", "kharif", "rabi",
                   "kharif", "kharif", "kharif"],
        "year": [2023, 2023, 2023, 2023, 2023, 2023, 2023, 2023],
        "area_hectare": [1000, 1500, 2000, 1200, 1800, 2200, 900, 700],
        "production": [5000, 6000, 7000, 4500, 8000, 9500, 3800, 3100],
        "unit_area": "hectare",
        "unit_yield": "quintal/hectare",
        "unit_production": "quintal",
    }

    df = pd.DataFrame(data)

    # 2. Validate and clean
    print("Step 1: Validating and cleaning data...")
    required = ["state", "district", "crop", "area_hectare", "production"]
    df = validate_and_clean_data(df, source="data.gov.in", required_columns=required)

    # 3. Normalize units
    print("Step 2: Normalizing units...")
    df["area_hectare"] = df.apply(
        lambda row: UnitNormalizer.area(row["area_hectare"], row.get("unit_area", "hectare")),
        axis=1
    )
    print(f"  - Converted {len(df)} records to hectares")

    # 4. Add provenance metadata
    print("Step 3: Adding provenance metadata...")
    for _, row in df.iterrows():
        provenance = DataProvenanceTracker.wrap_provenance(
            record=row.to_dict(),
            source="data.gov.in",
            source_record_id=None,
            obs_date=datetime.now().date(),
            geo_level="district",
            crop=row["crop"],
            validation_status="synthetic"
        )
        print(f"  - {provenance['_crop']} / {provenance['_geo_level']}: "
              f"p={provenance['_retrieved_at'][:10]}, status={provenance['_validation_status']}")

    # 5. Ingest into database
    print("Step 4: Ingesting into database...")
    from sqlalchemy.orm import Session
    from backend.database import engine, Base
    Base.metadata.create_all(bind=engine)
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    ingest_crop_data(
        session=session,
        source="data.gov.in",
        data=df,
        source_record_id="synthetic-dev-001",
        validation_status="synthetic"
    )

    session.close()

    print()
    print("=" * 60)
    print(f"Ingested {len(df)} crop production records successfully.")
    print("All records marked as 'synthetic' — for development only.")
    print("=" * 60)
    print()
    print("To use real data.gov.in data:")
    print("1. Obtain API access from https://data.gov.in")
    print("2. Replace the synthetic dataset above with API fetch results")
    print("3. Remove the 'synthetic' validation_status markers")
    print("4. Re-run the ingestion script")
    print("=" * 60)


if __name__ == "__main__":
    main()