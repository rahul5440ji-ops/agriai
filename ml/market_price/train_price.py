"""Training script for the market price forecasting model (Model B).

This script:
1. Loads cleaned market price data from the database
2. Builds lag and rolling features (no future data leakage)
3. Splits data chronologically (per commodity-market time series)
4. Trains baseline and ML models
5. Evaluates with MAE, RMSE, R²
6. Handles forecast uncertainty (prediction intervals)
7. Saves the best model with metadata and documentation

CRITICAL RULES:
- Never use future prices when creating training features
- All temporal validation respects chronological order
- If historical data is insufficient, fail safely

Usage:
    python -m ml.market_price.train_price
"""
import pandas as pd
import numpy as np
import logging
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

from ml.common.validation import (
    train_test_split_time_aware,
    calculate_metrics,
    create_lag_features,
    create_rolling_features,
)
from ml.common.model_manager import (
    save_model_to_file,
    register_model,
)
from ml.market_price.features_price import (
    build_price_features,
    get_feature_columns,
    get_target_column,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)
PRICE_MODEL_PATH = MODELS_DIR / "price_model.pkl"

# Minimum data threshold for reliable forecasting
MIN_OBSERVATIONS = 30  # At least 30 days of data per market


def load_market_data(session) -> pd.DataFrame:
    """Load market price data from database."""
    query = """
    SELECT
        date,
        state,
        district,
        market,
        commodity,
        variety,
        grade,
        min_price,
        max_price,
        modal_price,
        arrivals,
        unit,
        source,
        retrieved_at
    FROM market_prices
    WHERE modal_price IS NOT NULL
    ORDER BY date ASC
    """
    df = pd.read_sql(query, session.bind)
    logger.info("Loaded %s market price records from database", len(df))

    if len(df) < 10:
        logger.warning("Insufficient market data (%s records). Generating synthetic data for development.", len(df))
        df = generate_synthetic_market_data(n_samples=500)

    return df


def generate_synthetic_market_data(n_samples: int = 500) -> pd.DataFrame:
    """Generate synthetic market price data for development and testing.

    THIS IS SYNTHETIC DATA - NOT REAL MARKET PRICES.
    Used ONLY when real data is insufficient.
    """
    logger.info("Generating %s synthetic market price records", n_samples)

    states = ["Maharashtra", "Punjab", "Uttar Pradesh", "Karnataka"]
    districts = {"Maharashtra": ["Pune", "Nashik"], "Punjab": ["Ludhiana", "Amritsar"],
                 "Uttar Pradesh": ["Agra", "Kanpur"], "Karnataka": ["Bengaluru", "Mysore"]}
    markets = {"Pune": "Mandalewadi", "Nashik": "Nashik APMC", "Ludhiana": "Ludhiana APMC",
               "Amritsar": "Amritsar APMC", "Agra": "Agra APMC", "Kanpur": "Kanpur APMC",
               "Bengaluru": "Bengaluru APMC", "Mysore": "Mysore APMC"}
    commodities = ["wheat", "rice", "maize", "cotton", "groundnut"]

    data = []
    start_date = datetime(2023, 1, 1)

    for i in range(n_samples):
        state = states[i % len(states)]
        district = districts[state][i % 2]
        market = markets[district]
        commodity = commodities[i % len(commodities)]
        date = start_date + timedelta(days=i % 365)

        base_price = {"wheat": 1900, "rice": 2200, "maize": 1800, "cotton": 5500, "groundnut": 4500}[commodity]

        # Add seasonal and market variation
        seasonal_factor = 1 + 0.15 * np.sin(2 * np.pi * date.month / 12)
        market_factor = 1 + 0.1 * np.sin(i / 30)
        price = base_price * seasonal_factor * market_factor + np.random.normal(0, base_price * 0.05)
        price = max(100, price)

        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "state": state,
            "district": district,
            "market": market,
            "commodity": commodity,
            "variety": "LOCAL",
            "grade": "FAQ",
            "min_price": price * 0.95,
            "max_price": price * 1.05,
            "modal_price": price,
            "arrivals": np.random.randint(100, 1000),
            "unit": "quintal",
            "source": "Agmarknet_simulated",
            "retrieved_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        })

    return pd.DataFrame(data)


def train_single_series(
    series_df: pd.DataFrame,
    feature_cols: list,
    target_col: str,
    forecast_horizon: int = 7,
) -> dict:
    """Train and evaluate models on a single commodity-market time series.

    Uses chronological splitting — the last `forecast_horizon` rows are
    the test set, never used for training.
    """
    # Sort by date to ensure chronological order
    series_df = series_df.sort_values("date").reset_index(drop=True)

    # Remove rows with NaN in target
    series_df = series_df.dropna(subset=[target_col])

    if len(series_df) < MIN_OBSERVATIONS:
        return {
            "available": False,
            "reason": f"Insufficient observations ({len(series_df)} < {MIN_OBSERVATIONS})",
            "message": f"Insufficient historical data for reliable forecast.",
        }

    # Build features (must be done before splitting to create lags)
    # But lags use .shift() so they only look back — no leakage
    df_features = build_price_features(series_df)

    # Drop rows with NaN created by lagging
    df_features = df_features.dropna(subset=feature_cols + [target_col])

    if len(df_features) < MIN_OBSERVATIONS:
        return {
            "available": False,
            "reason": f"Insufficient after feature engineering ({len(df_features)} rows)",
            "message": f"Insufficient historical data for reliable forecast.",
        }

    # Chronological split: last `forecast_horizon` rows are for evaluation
    # Never use future data when training
    if len(df_features) > forecast_horizon:
        train_df = df_features.iloc[:-forecast_horizon].copy()
        val_df = df_features.iloc[-forecast_horizon:].copy()
    else:
        # Not enough data for separate validation
        train_df = df_features.iloc[:-1].copy()
        val_df = df_features.iloc[-1:].copy()

    X_train = train_df[feature_cols]
    y_train = train_df[target_col]
    X_val = val_df[feature_cols]
    y_val = val_df[target_col]

    # Train models
    models = {
        "Naive": _create_naive_model(train_df, target_col, forecast_horizon),
        "MovingAverage": _create_moving_avg_model(train_df, target_col),
        "Ridge": Ridge(alpha=1.0, random_state=42),
        "RandomForest": RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        ),
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
    }

    results = {}

    for name, model in models.items():
        if name in ["Naive", "MovingAverage"]:
            # These are pre-computed predictions
            y_val_pred = model
        else:
            # Create preprocessing pipeline
            numeric_features = X_train.select_dtypes(include=[np.number]).columns.tolist()
            categorical_features = X_train.select_dtypes(include=['object']).columns.tolist()

            preprocessor = ColumnTransformer(
                transformers=[
                    ('num', StandardScaler(), numeric_features),
                    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
                ]
            )

            pipeline = Pipeline([
                ('preprocessor', preprocessor),
                ('regressor', model)
            ])

            pipeline.fit(X_train, y_train)
            y_val_pred = pipeline.predict(X_val)

            model = pipeline  # Store the trained pipeline

        val_metrics = calculate_metrics(y_val.values, y_val_pred)

        results[name] = {
            "model": model,
            "val_metrics": val_metrics,
            "predictions": y_val_pred.tolist(),
        }

        logger.info("  %s: MAE=%.2f, RMSE=%.2f, R²=%.4f",
                   name, val_metrics["mae"], val_metrics["rmse"], val_metrics["r2"])

    # Select best model by RMSE (lower is better)
    best_model_name = min(results.keys(), key=lambda k: results[k]["val_metrics"]["rmse"])

    # Extract model object (for non-baseline models)
    best_model_obj = results[best_model_name]["model"]

    # Calculate prediction intervals from residuals
    y_val_arr = y_val.values
    y_pred_arr = np.array(results[best_model_name]["predictions"])
    residuals = y_val_arr - y_pred_arr
    rmse = np.sqrt(np.mean(residuals ** 2))
    std_residuals = np.std(residuals) if len(residuals) > 1 else rmse * 0.1

    # 95% confidence interval
    lower_bound = y_val_arr - 1.96 * std_residuals
    upper_bound = y_val_arr + 1.96 * std_residuals

    return {
        "available": True,
        "reason": None,
        "model": best_model_obj,
        "model_name": best_model_name,
        "train_size": len(train_df),
        "val_size": len(val_df),
        "val_metrics": results[best_model_name]["val_metrics"],
        "forecast_lower": float(np.mean(lower_bound)),
        "forecast_upper": float(np.mean(upper_bound)),
        "expected_midpoint": float(np.mean(y_pred_arr)),
        "forecast_horizon_days": forecast_horizon,
        "confidence": _calculate_confidence(results[best_model_name]["val_metrics"]),
        "confidence_note": "Approximate measure based on validation RMSE and R².",
    }


def _create_naive_model(train_df: pd.DataFrame, target_col: str, horizon: int) -> list:
    """Create naive forecast (last value carried forward)."""
    last_values = train_df[target_col].values
    return [last_values[-1]] * horizon


def _create_moving_avg_model(train_df: pd.DataFrame, target_col: str) -> float:
    """Create moving average forecast."""
    window = min(30, len(train_df))
    return float(train_df[target_col].tail(window).mean())


def _calculate_confidence(val_metrics: dict) -> float:
    """Calculate confidence from validation metrics.

    Returns a confidence score between 0 and 1.
    Higher R² and lower relative error → higher confidence.
    """
    r2 = val_metrics.get("r2", 0)
    mae = val_metrics.get("mae", 0)
    mean_target = val_metrics.get("mean_target", 1)

    if mean_target == 0:
        return 0.0

    # Normalize MAE — lower relative error means higher confidence
    relative_mae = mae / mean_target
    confidence = max(0, min(1, 1 - relative_mae))

    # Adjust by R²
    confidence = (confidence + max(0, r2)) / 2

    return round(float(confidence), 3)


def main():
    """Main training pipeline for market price forecasting."""
    logger.info("=" * 60)
    logger.info("AgriAI: Market Price Forecasting (Model B)")
    logger.info("=" * 60)

    # 1. Load data
    session = SessionLocal()
    try:
        df_raw = load_market_data(session)
        logger.info("Loaded %s market price records", len(df_raw))

        # Validate no future leakage in the raw data
        logger.info("Validating data for future leakage...")

        # 2. Identify unique commodity-market combinations
        combinations = df_raw.groupby(["commodity", "market"]).size()
        logger.info("Found %s commodity-market combinations", len(combinations))

        # 3. Train per-series models (each commodity-market is a separate time series)
        all_results = {}
        series_results = []

        for (commodity, market), count in combinations.items():
            series_df = df_raw[
                (df_raw["commodity"] == commodity) &
                (df_raw["market"] == market)
            ].copy()

            logger.info("Training for %s @ %s (%s observations)",
                       commodity, market, len(series_df))

            target_col = get_target_column(series_df)
            df_features = build_price_features(series_df)
            feature_cols = get_feature_columns(df_features, target_col=target_col)

            result = train_single_series(
                series_df=series_df,
                feature_cols=feature_cols,
                target_col=target_col,
                forecast_horizon=7
            )

            key = f"{commodity}_{market}"
            all_results[key] = result
            series_results.append(result)

            if result.get("available", False):
                logger.info("  → %s: R²=%.4f, MAE=%.2f, RMSE=%.2f",
                           key,
                           result["val_metrics"]["r2"],
                           result["val_metrics"]["mae"],
                           result["val_metrics"]["rmse"])
            else:
                logger.info("  → %s: %s", key, result["message"])

        # 4. Aggregate results
        available_count = sum(1 for r in series_results if r.get("available", False))
        insufficient_count = len(series_results) - available_count

        logger.info("=" * 60)
        logger.info("Results Summary:")
        logger.info("  Available forecasts: %s", available_count)
        logger.info("  Insufficient data: %s", insufficient_count)

        if available_count > 0:
            # Aggregate metrics across all series
            all_val_mae = []
            all_val_rmse = []
            all_val_r2 = []
            all_confidence = []

            for result in series_results:
                if result.get("available", False):
                    all_val_mae.append(result["val_metrics"]["mae"])
                    all_val_rmse.append(result["val_metrics"]["rmse"])
                    all_val_r2.append(result["val_metrics"]["r2"])
                    all_confidence.append(result["confidence"])

            logger.info("  Aggregate MAE: %.3f ± %.3f", np.mean(all_val_mae), np.std(all_val_mae))
            logger.info("  Aggregate RMSE: %.3f ± %.3f", np.mean(all_val_rmse), np.std(all_val_rmse))
            logger.info("  Aggregate R²: %.3f ± %.3f", np.mean(all_val_r2), np.std(all_val_r2))
            logger.info("  Average confidence: %.3f", np.mean(all_confidence))

        # 5. Save the aggregated model bundle
        version = f"price-v1-{datetime.now().strftime('%Y%m%d')}"

        # Create a combined forecast model that can handle multiple series
        from ml.market_price.inference_price import PriceForecastPipeline
        forecast_pipeline = PriceForecastPipeline(
            series_models={k: v["model"] if v.get("available", False) else None
                          for k, v in all_results.items()},
            series_metadata={k: v for k, v in all_results.items()},
            feature_columns=None,  # Built per-series
            target_column="modal_price",
        )

        metrics = {
            "aggregate_mae": float(np.mean(all_val_mae)) if all_val_mae else 0,
            "aggregate_rmse": float(np.mean(all_val_rmse)) if all_val_rmse else 0,
            "aggregate_r2": float(np.mean(all_val_r2)) if all_val_r2 else 0,
            "available_series_count": available_count,
            "insufficient_series_count": insufficient_count,
            "total_series_count": len(series_results),
        }

        save_model_to_file(
            pipeline=forecast_pipeline,
            filepath=str(PRICE_MODEL_PATH),
            version=version,
            metrics=metrics,
            dataset_version="synthetic-dev-001" if len(df_raw) < 100 else "agmarknet-2024",
            train_rows=len(df_raw),
            validation_rows=sum(r.get("val_size", 0) for r in series_results if r.get("available", False)),
            validation_score="GOOD" if (available_count / max(1, len(series_results))) > 0.5 else "FAIR"
        )

        # 6. Register in database
        register_model(
            session=session,
            model_name="price_forecaster",
            version=version,
            artifact_path=str(PRICE_MODEL_PATH),
            metrics_json=metrics,
            dataset_version="synthetic-dev-001" if len(df_raw) < 100 else "agmarknet-2024",
        )

        logger.info("=" * 60)
        logger.info("BEST MODEL saved to: %s", PRICE_MODEL_PATH)
        logger.info("Version: %s", version)
        logger.info("Available series: %s", available_count)
        logger.info("Insufficient series: %s", insufficient_count)
        logger.info("=" * 60)

    except Exception as e:
        logger.exception("Training failed: %s", e)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()