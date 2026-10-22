#!/usr/bin/env python3
"""
Ingestion script for Agmarknet market price data.

NOTE: This script loads synthetic data for development and testing only.
Replace with real API calls to https://agmarknet.gov.in when access is available.

All data is stored with provenance metadata.
"""
import pandas as pd
import sys
import os
from datetime import datetime, date, timedelta

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.common.data_utils import (
    DataProvenanceTracker,
    UnitNormalizer,
    ingest_market_data,
    validate_and_clean_data,
)


def generate_synthetic_market_data(crop: str = "wheat", state: str = "Maharashtra", days: int = 30) -> pd.DataFrame:
    """Generate synthetic Agmarknet-like data for development/testing.

    This data MUST NOT be used as real market data.
    """
    dates = [date.today() - timedelta(days=i) for i in range(days, 0, -1)]

    base_price = 1900  # Base price per quintal
    data = {
        "date": dates,
        "state": [state] * days,
        "district": [state] * days,
        "market": ["Mandalewadi", "Katra", "Gandhi Nagar", "Fergusson College", "Pune City"] * (days // 5 + 1),
        "commodity": [crop] * days,
        "variety": ["AP-65", "HD-2967", "Kalyan Sona", "Lerma", "Lok-1"] * (days // 5 + 1),
        "grade": ["A", "FA", "B", "A", "FA"] * (days // 5 + 1),
        "min_price": [int(base_price * 0.9 + i) for i in range(days)],
        "max_price": [int(base_price * 1.1 + i) for i in range(days)],
        "modal_price": [int(base_price + i * 1.5) for i in range(days)],
        "arrivals": [100 + (i % 100) for i in range(days)],
        "unit": ["quintal"] * days,
    }
    return pd.DataFrame(data)


def main():
    """Load Agmarknet market data for development."""
    print("=" * 60)
    print("AgriAI: Agmarknet Market Data Ingestion")
    print("=" * 60)
    print("WARNING: Loading synthetic data for development only.")
    print("This data is NOT real market prices.")
    print("=" * 60)
    print()

    # 1. Generate synthetic data
    print("Step 1: Generating synthetic market data...")
    df = generate_synthetic_market_data(crop="wheat", days=30)
    print(f"  - Generated {len(df)} market observations")

    # 2. Validate and clean
    print("Step 2: Validating and cleaning data...")
    required = ["state", "district", "market", "commodity", "date", "modal_price"]
    df = validate_and_clean_data(df, source="Agmarknet", required_columns=required)

    # 3. Normalize units
    print("Step 3: Normalizing units...")
    df["price_quintal"] = df["modal_price"]  # Already in ₹/quintal

    # 4. Add provenance metadata
    print("Step 4: Adding provenance metadata...")
    for _, row in df.iterrows():
        provenance = DataProvenanceTracker.wrap_provenance(
            record=row.to_dict(),
            source="Agmarknet",
            source_record_id=None,
            obs_date=row["date"].isoformat() if isinstance(row["date"], date) else str(row["date"]),
            geo_level="district",
            crop=row["commodity"],
            validation_status="synthetic"
        )
        print(f"  - {provenance['_crop']} @ {provenance['_geo_level']}: "
              f"₹{provenance['price_quintal']} ({provenance['_validation_status']})")

    # 5. Ingest into database
    print("Step 5: Ingesting into database...")
    from sqlalchemy.orm import Session
    from backend.database import engine, Base
    from sqlalchemy.orm import sessionmaker

    # Create tables if not exist
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    count = ingest_market_data(
        session=session,
        source="Agmarknet",
        data=df,
        source_record_id="synthetic-agmarknet-dev-001",
        validation_status="synthetic"
    )

    session.close()

    print()
    print("=" * 60)
    print(f"Ingested {count} market price records successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()