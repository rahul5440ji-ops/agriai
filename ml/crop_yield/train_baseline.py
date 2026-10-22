"""Train a regional crop yield baseline model from the CSV dataset.

This model uses NATIONAL crop/season-level data (220 rows, 28 crops,
5 years). It provides a regional yield baseline that can be used as a
reference point alongside the field-level yield model.

IMPORTANT: This is a regional/statistical baseline, NOT a prediction
for an individual farm. It must never be presented as a field-level
prediction.

Usage:
    python -m ml.crop_yield.train_baseline
"""
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)
BASELINE_MODEL_PATH = MODELS_DIR / "yield_baseline_model.pkl"
DATA_PATH = Path("data/processed/crop_yield_training_processed.csv")


def extract_year(year_str):
    """Extract starting year from '2021-22' format."""
    return int(str(year_str).split("-")[0])


def load_data():
    """Load and prepare the CSV data."""
    if not DATA_PATH.exists():
        logger.error("Data file not found: %s", DATA_PATH)
        return None

    df = pd.read_csv(DATA_PATH)
    logger.info("Loaded %s rows from %s", len(df), DATA_PATH)

    # Extract year
    df["year"] = df["year"].apply(extract_year)

    # Convert yield from kg/ha to t/ha
    df["yield_tph"] = df["yield_kg_per_ha"] / 1000.0

    return df


def build_preprocessor():
    """Build a preprocessing pipeline for the baseline model."""
    numeric_features = ["area_source_value", "year"]
    categorical_features = ["crop", "season"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )
    return preprocessor


def train_and_evaluate(df):
    """Train models and evaluate using time series split."""
    feature_cols = ["crop", "season", "year", "area_source_value"]
    target_col = "yield_tph"

    X = df[feature_cols]
    y = df[target_col]

    # Use time series split to respect temporal order
    tscv = TimeSeriesSplit(n_splits=3)

    models = {
        "Ridge": Ridge(alpha=1.0, random_state=42),
        "RandomForest": RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
        ),
        "ExtraTrees": ExtraTreesRegressor(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
        ),
    }

    results = {}

    for name, model in models.items():
        logger.info("Training %s...", name)

        pipeline = Pipeline([
            ("preprocessor", build_preprocessor()),
            ("regressor", model),
        ])

        # Evaluate with time series split
        fold_metrics = {"mae": [], "rmse": [], "r2": []}

        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_val)

            fold_metrics["mae"].append(mean_absolute_error(y_val, y_pred))
            fold_metrics["rmse"].append(np.sqrt(mean_squared_error(y_val, y_pred)))
            fold_metrics["r2"].append(r2_score(y_val, y_pred))

        avg_metrics = {
            "mae": float(np.mean(fold_metrics["mae"])),
            "rmse": float(np.mean(fold_metrics["rmse"])),
            "r2": float(np.mean(fold_metrics["r2"])),
        }

        results[name] = {
            "pipeline": pipeline,
            "metrics": avg_metrics,
            "fold_metrics": fold_metrics,
        }

        logger.info(
            "  %s - MAE: %.3f, RMSE: %.3f, R2: %.3f",
            name, avg_metrics["mae"], avg_metrics["rmse"], avg_metrics["r2"]
        )

    return results


def save_model(pipeline, metrics, version):
    """Save the model artifact with metadata."""
    artifact = {
        "pipeline": pipeline,
        "metadata": {
            "model_type": "regional_yield_baseline",
            "version": version,
            "trained_at": datetime.now().isoformat(),
            "data_source": "agriculture_ai_integrated_project",
            "data_rows": 220,
            "crops": 28,
            "years": "2021-2025",
            "metrics": metrics,
            "disclaimer": (
                "This is a regional/statistical baseline model trained on "
                "national crop/season-level data. It is NOT a prediction for "
                "an individual farm. Use it only as a reference point."
            ),
        },
    }
    joblib.dump(artifact, BASELINE_MODEL_PATH)
    logger.info("Model saved to %s", BASELINE_MODEL_PATH)


def main():
    logger.info("=" * 60)
    logger.info("AgriAI: Regional Yield Baseline Model Training")
    logger.info("=" * 60)

    # 1. Load data
    df = load_data()
    if df is None:
        logger.error("Failed to load data. Exiting.")
        return

    logger.info("Data shape: %s", df.shape)
    logger.info("Crops: %s", df["crop"].nunique())
    logger.info("Years: %s", sorted(df["year"].unique()))

    # 2. Train and evaluate
    results = train_and_evaluate(df)

    # 3. Select best model by R2
    best_name = max(results.keys(), key=lambda k: results[k]["metrics"]["r2"])
    best_result = results[best_name]

    logger.info("=" * 60)
    logger.info("BEST MODEL: %s", best_name)
    logger.info("MAE: %.3f t/ha", best_result["metrics"]["mae"])
    logger.info("RMSE: %.3f t/ha", best_result["metrics"]["rmse"])
    logger.info("R2: %.3f", best_result["metrics"]["r2"])
    logger.info("=" * 60)

    # 4. Save model
    version = f"yield-baseline-v1-{datetime.now().strftime('%Y%m%d')}"
    save_model(best_result["pipeline"], best_result["metrics"], version)

    logger.info("Training complete!")


if __name__ == "__main__":
    main()