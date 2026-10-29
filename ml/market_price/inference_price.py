"""Inference pipeline for market price forecasting (Model B).

Handles loading trained models and making forecasts for specific
commodity-market combinations.

Fails safely when data is insufficient — never fabricates forecasts.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional

from ml.common.model_manager import load_model_from_file
from ml.market_price.features_price import build_price_features, get_feature_columns, get_target_column

logger = logging.getLogger(__name__)

MIN_HISTORICAL_OBSERVATIONS = 60


class PriceForecastPipeline:
    """Inference pipeline for market price forecasting.

    Loads trained models and makes forecasts for specific
    commodity-market combinations.

    Fails safely when data is insufficient — never fabricates forecasts.
    """

    def __init__(
        self,
        series_models: Dict[str, Any] = None,
        series_metadata: Dict[str, Any] = None,
        feature_columns: list = None,
        target_column: str = "modal_price",
    ):
        self.series_models = series_models or {}
        self.series_metadata = series_metadata or {}
        self.feature_columns = feature_columns
        self.target_column = target_column

    def predict_single(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Make a forecast for a single commodity-market combination.

        Parameters
        ----------
        features : dict
            Must include:
            - commodity: str
            - market: str
            - horizon_days: int (default 7)
            - historical_data: list of dicts with 'date', 'modal_price', etc.

        Returns
        -------
        dict
            Forecast result with:
            - available: bool
            - message: str (if not available)
            - forecast_lower: float
            - forecast_upper: float
            - expected_midpoint: float
            - forecast_horizon_days: int
            - confidence: float
            - confidence_note: str
            - model_version: str
        """
        commodity = features.get("commodity")
        market = features.get("market")
        horizon_days = features.get("horizon_days", 7)
        historical_data = features.get("historical_data", [])

        key = f"{commodity}_{market}"

        # Check if we have a model for this combination
        if key not in self.series_models or self.series_models[key] is None:
            return {
                "available": False,
                "message": f"Insufficient historical data for reliable forecast. "
                          f"No trained model for {commodity} @ {market}.",
                "commodity": commodity,
                "market": market,
            }

        # Check if there's enough historical data
        if len(historical_data) < MIN_HISTORICAL_OBSERVATIONS:
            return {
                "available": False,
                "message": f"Insufficient historical data for reliable forecast. "
                          f"Only {len(historical_data)} observations available; "
                          f"{MIN_HISTORICAL_OBSERVATIONS} are required.",
                "commodity": commodity,
                "market": market,
            }

        # Build features from historical data
        df = pd.DataFrame(historical_data)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        # Build features
        df_features = build_price_features(df)

        # Get feature columns
        feature_cols = get_feature_columns(df_features, target_col=self.target_column)

        # Get the last row of features for prediction
        last_row = df_features.iloc[-1:].copy()

        # Make prediction
        model = self.series_models[key]
        try:
            prediction = max(0.0, float(model.predict(last_row[feature_cols])[0]))
        except Exception as e:
            logger.warning("Prediction failed for %s: %s", key, e)
            return {
                "available": False,
                "message": f"Prediction failed for {commodity} @ {market}.",
                "commodity": commodity,
                "market": market,
            }

        # Get metadata for confidence
        metadata = self.series_metadata.get(key, {})
        val_metrics = metadata.get("val_metrics", {})
        confidence = metadata.get("confidence", 0.5)
        rmse = val_metrics.get("rmse")
        interval = 1.96 * rmse if rmse and rmse > 0 else prediction * 0.1
        forecast_lower = max(0.0, prediction - interval)
        forecast_upper = prediction + interval

        return {
            "available": True,
            "commodity": commodity,
            "market": market,
            "forecast_lower": float(forecast_lower),
            "forecast_upper": float(forecast_upper),
            "expected_midpoint": float(prediction),
            "forecast_horizon_days": horizon_days,
            "confidence": float(confidence),
            "confidence_note": metadata.get(
                "confidence_note",
                "Approximate measure based on validation RMSE and R²."
            ),
            "model_version": "price-v1",
        }


def load_price_model(filepath: str) -> PriceForecastPipeline:
    """Load a saved price forecasting pipeline from disk.

    Returns
    -------
    PriceForecastPipeline
        The loaded pipeline ready for inference
    """
    pipeline, metadata = load_model_from_file(filepath)
    return pipeline