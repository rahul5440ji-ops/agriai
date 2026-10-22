#!/usr/bin/env python3
"""
Seed development/test data for AgriAI.
All synthetic data is clearly labelled and never presented as real.
"""
import json
import os
from datetime import date, timedelta

# Mark this file as development-only seed data
SEED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "synthetic")
SEED_DIR = os.path.abspath(SEED_DIR)

def get_synthetic_soil_tests():
    """Synthetic soil test data for development/testing only."""
    return [
        {
            "farm_id": 1,
            "ph": 7.2,
            "nitrogen": 12.5,
            "phosphorus": 8.3,
            "potassium": 45.0,
            "organic_carbon": 0.8,
            "test_date": str(date.today()),
            "source": "synthetic_dev",
        },
        {
            "farm_id": 2,
            "ph": 6.8,
            "nitrogen": 15.0,
            "phosphorus": 10.2,
            "potassium": 52.0,
            "organic_carbon": 1.1,
            "test_date": str(date.today()),
            "source": "synthetic_dev",
        },
    ]

def get_synthetic_yield_predictions():
    """Synthetic yield predictions for development/testing only."""
    return [
        {
            "farm_cycle_id": 1,
            "predicted_yield_tph": 4.2,
            "lower_bound_tph": 3.6,
            "upper_bound_tph": 4.8,
            "total_production_t": 8.4,
            "model_version": "yield-v1",
            "confidence": 0.78,
            "created_at": str(date.today()),
        },
    ]

def main():
    print("Seeding development data...")
    print(f"Synthetic data directory: {SEED_DIR}")
    print(f"Soil tests: {len(get_synthetic_soil_tests())}")
    print(f"Yield predictions: {len(get_synthetic_yield_predictions())}")
    print("WARNING: This data is synthetic and for development ONLY.")
    print("Never present this data as real market/agricultural data.")

if __name__ == "__main__":
    main()