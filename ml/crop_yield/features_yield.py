"""Feature engineering for the crop yield prediction model.

Features are derived ONLY from data available at sowing time.
No future information (harvest yield, future weather) is used.
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build feature matrix for yield prediction.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw data with columns:
        - state, district, crop, season, year
        - soil_type, irrigation_type
        - ph, nitrogen, phosphorus, potassium, organic_carbon
        - sowing_month, sowing_year
        - rainfall, temperature (optional)
        - yield_per_hectare (target)

    Returns
    -------
    pandas.DataFrame
        Feature matrix with one row per observation
    """
    df = df.copy()

    # --- Numeric features ---
    numeric_features = [
        "ph", "nitrogen", "phosphorus", "potassium", "organic_carbon",
        "rainfall", "temperature",
    ]
    for col in numeric_features:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- Categorical features ---
    categorical_features = [
        "state", "district", "crop", "season",
        "soil_type", "irrigation_type",
    ]
    for col in categorical_features:
        if col in df.columns:
            df[col] = df[col].astype(str)

    # --- Derived features ---
    if "sowing_month" in df.columns:
        # Cyclical encoding for month (1-12)
        df["sowing_month_sin"] = np.sin(2 * np.pi * df["sowing_month"] / 12)
        df["sowing_month_cos"] = np.cos(2 * np.pi * df["sowing_month"] / 12)

    # Soil nutrient balance
    if all(c in df.columns for c in ["nitrogen", "phosphorus", "potassium"]):
        # N-P-K ratio (relative balance)
        total = df["nitrogen"] + df["phosphorus"] + df["potassium"]
        df["n_ratio"] = np.where(total > 0, df["nitrogen"] / total, 0)
        df["p_ratio"] = np.where(total > 0, df["phosphorus"] / total, 0)
        df["k_ratio"] = np.where(total > 0, df["potassium"] / total, 0)

    # Soil quality score (simple aggregate)
    soil_cols = ["ph", "nitrogen", "phosphorus", "potassium", "organic_carbon"]
    available = [c for c in soil_cols if c in df.columns]
    if available:
        # Normalize each to 0-1 range (rough agricultural bounds)
        bounds = {
            "ph": (5.5, 8.5),
            "nitrogen": (0, 200),
            "phosphorus": (0, 100),
            "potassium": (0, 200),
            "organic_carbon": (0, 10),
        }
        scores = []
        for col in available:
            low, high = bounds[col]
            normalized = (df[col] - low) / (high - low)
            normalized = normalized.clip(0, 1)
            scores.append(normalized)
        df["soil_quality_score"] = np.mean(scores, axis=0)

    # Year as numeric feature (captures temporal trend)
    if "year" in df.columns:
        df["year_numeric"] = df["year"]

    logger.info("Built features: %d columns", len(df.columns))
    return df


def get_feature_columns(df: pd.DataFrame) -> list:
    """Return the list of feature columns (excluding target)."""
    exclude = [
        "yield_per_hectare", "yield_per_hectare_t",
        "total_production", "production",
        "date", "sowing_date", "harvest_date",
        "_source", "_retrieved_at", "_obs_date",
        "_geo_level", "_crop", "_validation_status",
        "_source_record_id",
    ]
    return [c for c in df.columns if c not in exclude]


def get_target_column(df: pd.DataFrame) -> str:
    """Return the target column name."""
    for col in ["yield_per_hectare", "yield_per_hectare_t", "yield_tph"]:
        if col in df.columns:
            return col
    raise ValueError("No target column found in DataFrame")