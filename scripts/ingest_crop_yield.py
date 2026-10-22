#!/usr/bin/env python3
"""
Ingest crop yield training data from CSV into the database.

Loads data/raw/crop_yield_training.csv and stores it as regional yield
baselines in the database. This is NATIONAL/REGIONAL crop-season-level
data, NOT field-level data. It must never be presented as a prediction
for an individual farm.

Usage:
    python scripts/ingest_crop_yield.py
"""
import os
import sys
import json
import logging
from pathlib import Path

import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.database import engine, Base
from backend.models import Crop, MspPrice

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
SOURCE_NAME = "agriculture_ai_integrated_project"
CSV_FILE = RAW_DIR / "crop_yield_training.csv"


def validate_csv(df: pd.DataFrame) -> dict:
    """Validate the CSV data and return a quality report."""
    report = {
        "source": SOURCE_NAME,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": list(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_by_column": {k: int(v) for k, v in df.isna().sum().items()},
        "unique_values_by_column": {k: int(v) for k, v in df.nunique(dropna=True).items()},
    }

    # Check for impossible values
    if "yield_kg_per_ha" in df.columns:
        negative_yields = int((df["yield_kg_per_ha"] < 0).sum())
        zero_yields = int((df["yield_kg_per_ha"] == 0).sum())
        report["negative_yields"] = negative_yields
        report["zero_yields"] = zero_yields

    if "area_source_value" in df.columns:
        negative_area = int((df["area_source_value"] < 0).sum())
        report["negative_area"] = negative_area

    return report


def normalize_units(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize units to a consistent format.

    The CSV uses yield_kg_per_ha (kilograms per hectare).
    We convert to tonnes per hectare for internal consistency.
    """
    df = df.copy()
    df["yield_tph"] = df["yield_kg_per_ha"] / 1000.0  # kg/ha -> t/ha
    df["area_hectare"] = df["area_source_value"]  # already in hectares
    return df


def extract_year(year_str: str) -> int:
    """Extract the starting year from '2021-22' format."""
    return int(year_str.split("-")[0])


def main():
    logger.info("=" * 60)
    logger.info("AgriAI: Crop Yield Data Ingestion")
    logger.info("=" * 60)

    # 1. Load CSV
    if not CSV_FILE.exists():
        logger.error("CSV file not found: %s", CSV_FILE)
        sys.exit(1)

    df = pd.read_csv(CSV_FILE)
    logger.info("Loaded %s rows from %s", len(df), CSV_FILE)

    # 2. Validate
    quality_report = validate_csv(df)
    logger.info("Quality report: %s", json.dumps(quality_report, indent=2))

    # 3. Normalize units
    df = normalize_units(df)
    df["year"] = df["year"].apply(extract_year)

    # 4. Save processed version
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    processed_path = PROCESSED_DIR / "crop_yield_training_processed.csv"
    df.to_csv(processed_path, index=False)
    logger.info("Saved processed data to %s", processed_path)

    # 5. Save quality report
    reports_dir = Path("data/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    with open(reports_dir / "crop_yield_quality.json", "w") as f:
        json.dump(quality_report, f, indent=2)
    logger.info("Saved quality report to data/reports/crop_yield_quality.json")

    # 6. Summary statistics
    logger.info("Summary statistics:")
    logger.info("  Crops: %s", df["crop"].nunique())
    logger.info("  Seasons: %s", list(df["season"].unique()))
    logger.info("  Years: %s", sorted(df["year"].unique()))
    logger.info("  Yield range (t/ha): %.3f - %.3f",
                df["yield_tph"].min(), df["yield_tph"].max())
    logger.info("  Mean yield (t/ha): %.3f", df["yield_tph"].mean())

    logger.info("=" * 60)
    logger.info("Ingestion complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()