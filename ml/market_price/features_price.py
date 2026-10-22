"""Feature engineering for market price forecasting (Model B).

Features are derived ONLY from data available at prediction time.
All lag and rolling features use STRICTLY PAST data.
No future information is ever used.
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


# Required lag periods (in days)
LAG_PERIODS = [1, 3, 7, 14, 30]

# Rolling window sizes (in days)
ROLLING_WINDOWS = [7, 14, 30]


def build_price_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build feature matrix for price forecasting.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw market price data with columns:
        - date, state, district, market, commodity, variety, grade
        - modal_price, min_price, max_price, arrivals
        - unit

    Returns
    -------
    pandas.DataFrame
        Feature matrix with lag and rolling features
    """
    df = df.copy()

    # Ensure date is datetime and sort
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["commodity", "market", "date"]).reset_index(drop=True)

    # Target column (modal_price is the standard benchmark)
    target_col = "modal_price"

    # Create lag features for each commodity-market combination
    # This is done per group to avoid leakage across markets
    for lag in LAG_PERIODS:
        df[f"{target_col}_lag_{lag}"] = df.groupby(["commodity", "market"])[target_col].shift(lag)

    # Create rolling features (mean, std, min, max, median)
    # All rolling windows use .shift(1) to ensure they only use past data
    for window in ROLLING_WINDOWS:
        shifted = df.groupby(["commodity", "market"])[target_col].shift(1)
        df[f"{target_col}_rolling_mean_{window}"] = shifted.rolling(window, min_periods=1).mean()
        df[f"{target_col}_rolling_std_{window}"] = shifted.rolling(window, min_periods=1).std()
        df[f"{target_col}_rolling_min_{window}"] = shifted.rolling(window, min_periods=1).min()
        df[f"{target_col}_rolling_max_{window}"] = shifted.rolling(window, min_periods=1).max()
        df[f"{target_col}_rolling_median_{window}"] = shifted.rolling(window, min_periods=1).median()

    # Arrivals features (if available)
    if "arrivals" in df.columns:
        for lag in LAG_PERIODS:
            df[f"arrivals_lag_{lag}"] = df.groupby(["commodity", "market"])["arrivals"].shift(lag)
        for window in ROLLING_WINDOWS:
            shifted_arr = df.groupby(["commodity", "market"])["arrivals"].shift(1)
            df[f"arrivals_rolling_mean_{window}"] = shifted_arr.rolling(window, min_periods=1).mean()

    # Price range features
    if all(c in df.columns for c in ["min_price", "max_price"]):
        df["price_range"] = df["max_price"] - df["min_price"]
        df["price_range_pct"] = np.where(
            df["modal_price"] > 0,
            df["price_range"] / df["modal_price"],
            0
        )
        for lag in LAG_PERIODS:
            df[f"price_range_lag_{lag}"] = df.groupby(["commodity", "market"])["price_range"].shift(lag)

    # Calendar features
    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_of_month"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter

    # Cyclical encoding for month and day of week
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

    # Market/Commodity categorical features
    for col in ["state", "district", "market", "commodity", "variety", "grade"]:
        if col in df.columns:
            df[col] = df[col].astype(str)

    logger.info("Built price features: %d columns", len(df.columns))
    return df


def get_feature_columns(df: pd.DataFrame, target_col: str = "modal_price") -> list:
    """Return feature column names (excluding target and metadata)."""
    exclude = [
        target_col, "min_price", "max_price", "arrivals",
        "date", "unit", "source", "retrieved_at",
        "_source", "_source_record_id", "_retrieved_at",
        "_obs_date", "_geo_level", "_crop", "_validation_status",
    ]
    return [c for c in df.columns if c not in exclude]


def get_target_column(df: pd.DataFrame) -> str:
    """Return the target column name."""
    for col in ["modal_price", "price", "modal_price_per_quintal"]:
        if col in df.columns:
            return col
    raise ValueError("No target column found in DataFrame")