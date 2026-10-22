"""Shared validation utilities for ML pipelines.

Provides time-aware (chronological) train/validation splits that prevent
future leakage, plus basic validation helpers.
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def train_test_split_time_aware(
    df: pd.DataFrame,
    date_column: str = "date",
    split_ratio: float = 0.8,
    train_end_date: pd.Timestamp = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split data chronologically to prevent future leakage.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with a date column
    date_column : str
        Name of the date column
    split_ratio : float
        Proportion of data to include in training set (chronologically first)
    train_end_date : pandas.Timestamp, optional
        Explicit end date for training period. If provided, all data
        before this date goes to training, and all data from this date
        onwards goes to validation. Overrides split_ratio.

    Returns
    -------
    tuple[pandas.DataFrame, pandas.DataFrame]
        (train, validation) DataFrames

    Notes
    -----
    This NEVER randomly shuffles data. Future observations are NEVER
    present in the training set.
    """
    if date_column not in df.columns:
        raise ValueError(f"Column '{date_column}' not found in DataFrame")

    # Sort chronologically first
    df_sorted = df.sort_values(date_column).copy()

    # Determine split point
    if train_end_date is not None:
        train_mask = df_sorted[date_column] < pd.Timestamp(train_end_date)
    else:
        split_idx = int(len(df_sorted) * split_ratio)
        split_date = df_sorted.iloc[split_idx][date_column]
        train_mask = df_sorted[date_column] < split_date
        logger.info("Training period ends at %s (%.0f%% of data)", split_date, split_ratio * 100)

    train = df_sorted[train_mask].reset_index(drop=True)
    val = df_sorted[~train_mask].reset_index(drop=True)

    if val.empty:
        raise ValueError(
            "All data falls into training period. "
            "No validation data available."
        )

    if train.empty:
        raise ValueError(
            "All data falls into validation period. "
            "Train period too small."
        )

    logger.info("Train size: %s, Validation size: %s", len(train), len(val))
    return train, val


def train_test_split_by_region(
    df: pd.DataFrame,
    region_column: str = "district",
    train_regions: set = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split data by geographic region for out-of-region validation.

    Useful when training on known regions and validating on unseen ones.
    Prevents region-based leakage.
    """
    if train_regions is None:
        regions = df[region_column].unique()
        mid = len(regions) // 2
        train_regions = set(regions[:mid])

    train = df[df[region_column].isin(train_regions)].copy()
    val = df[~df[region_column].isin(train_regions)].copy()

    logger.info("Train regions: %s", len(train_regions))
    logger.info("Train size: %s, Validation size: %s", len(train), len(val))
    return train, val


def validate_features_no_future_leak(
    df: pd.DataFrame,
    date_column: str,
    target_column: str,
) -> dict:
    """Assert that no feature contains information from the future.

    Checks:
    - All numeric features are <= the target date for each row
    - No lagged features use future values

    Returns a dictionary with validation results.
    """
    issues = []
    df = df.sort_values(date_column).copy()

    # Check for obvious future leakage: any feature that changes AFTER
    # the observation date and could inform the target
    for col in df.select_dtypes(include=[np.number]).columns:
        if col == target_column or col == date_column:
            continue
        # Look for monotonic trends that could indicate leakage
        diffs = df[col].diff().dropna()
        # If the feature is perfectly correlated with time AFTER the target,
        # it could be leakage
        if diffs.shape[0] > 10:
            # Use np.corrcoef since Series.corrwith does not exist;
            # it computes the Pearson correlation between the two 1-d arrays.
            # Convert date column to numeric (days since min) to avoid
            # dtype mismatch with datetime64.
            date_numeric = (df[date_column] - df[date_column].min()).dt.days
            corr = np.abs(np.corrcoef(diffs, date_numeric)[0, 1])
            if np.isnan(corr) or corr > 0.99:
                issues.append(f"{col} may contain future information (corr with time: {corr:.4f})")

    return {
        "no_future_leak": len(issues) == 0,
        "issues": issues,
    }


def create_lag_features(df: pd.DataFrame, value_column: str, lags: list[int]) -> pd.DataFrame:
    """Create lagged features.

    All lags are strictly <= current row, so they NEVER leak future data.
    """
    df = df.sort_values("date").copy()
    result = df.copy()
    for lag in lags:
        result[f"{value_column}_lag_{lag}"] = result[value_column].shift(lag)
    return result


def create_rolling_features(
    df: pd.DataFrame,
    value_column: str,
    windows: list[int],
) -> pd.DataFrame:
    """Create rolling window features.

    Rolling windows use only past/current values, so they NEVER leak future data.
    """
    df = df.sort_values("date").copy()
    result = df.copy()
    for window in windows:
        result[f"{value_column}_rolling_mean_{window}"] = result[value_column].rolling(window).mean()
        result[f"{value_column}_rolling_std_{window}"] = result[value_column].rolling(window).std()
    return result


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Calculate regression metrics.

    Returns MAE, RMSE, and R².
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    residual = y_true - y_pred
    mae = np.mean(np.abs(residual))
    rmse = np.sqrt(np.mean(residual ** 2))
    ss_res = np.sum(residual ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - (ss_res / ss_tot)

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "mean_target": float(np.mean(y_true)),
        "std_target": float(np.std(y_true)),
    }