"""Shared ML inference interface.

Training code lives ONLY in ml/ (top-level). This module loads saved
artifacts at startup and exposes a single predict() contract per model.
It never runs training — that is the responsibility of the training
scripts in ml/.
"""
import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional

import joblib
import pandas as pd

from ml.crop_yield.features_yield import build_features, get_feature_columns

logger = logging.getLogger(__name__)


class BaseInferenceModel(ABC):
    """Common interface every model artifact must implement."""

    @abstractmethod
    def predict(self, features: dict) -> dict:
        ...

    @abstractmethod
    def is_available(self) -> bool:
        ...


class YieldModelService(BaseInferenceModel):
    """Loads the saved yield model artifact and runs inference."""

    def __init__(self, artifact_path: str):
        self.artifact_path = artifact_path
        self._pipeline = None
        self._metadata: Optional[dict] = None
        self._load()

    def _load(self):
        if not os.path.exists(self.artifact_path):
            logger.warning(
                "Yield model artifact not found at %s. "
                "Yield predictions will be unavailable.", self.artifact_path
            )
            return
        try:
            bundle = joblib.load(self.artifact_path)
            self._pipeline = bundle.get("pipeline")
            self._metadata = bundle.get("metadata", {})
            logger.info(
                "Loaded yield model %s (trained %s)",
                self._metadata.get("version", "unknown"),
                self._metadata.get("trained_at", "unknown"),
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to load yield model: %s", exc)
            self._pipeline = None

    def is_available(self) -> bool:
        return self._pipeline is not None

    def predict(self, features: dict) -> dict:
        if not self.is_available():
            raise RuntimeError(
                "Yield model is not available. Train the model first "
                "(see ml/crop_yield/train_yield.py)."
            )
        # Build features using the same feature builder used during
        # training, so inference and training share one code path.
        row = pd.DataFrame([features])
        row = build_features(row)
        # Add columns the model was trained with but are not features
        row["farm_cycle_id"] = 0
        row["actual_yield_tph"] = 0
        row["expected_harvest_date"] = "2024-03-01"
        row["farm_season"] = features.get("season", "unknown")
        model_features = getattr(self._pipeline, "feature_names_in_", None)
        if model_features is None:
            row = row[get_feature_columns(row)]
        else:
            row = row.reindex(columns=model_features)
            preprocessor = self._pipeline.named_steps.get("preprocessor")
            if preprocessor is not None:
                for _, transformer, columns in preprocessor.transformers_:
                    means = getattr(transformer, "mean_", None)
                    if means is None:
                        continue
                    for column, mean in zip(columns, means):
                        if pd.isna(row.at[0, column]):
                            row.at[0, column] = mean

        predicted = max(0.0, float(self._pipeline.predict(row)[0]))

        metrics = self._metadata.get("metrics", {}) if self._metadata else {}
        if self._metadata and not metrics:
            validation_metrics = self._metadata.get("val_metrics", {})
            metrics = {
                "val_rmse": validation_metrics.get("rmse"),
                "val_r2": validation_metrics.get("r2"),
            }
        val_rmse = metrics.get("val_rmse")
        # Uncertainty band derived from validation RMSE, never fabricated.
        if val_rmse:
            lower = max(0.0, predicted - 1.96 * val_rmse)
            upper = predicted + 1.96 * val_rmse
        else:
            lower = max(0.0, predicted * 0.85)
            upper = predicted * 1.15

        return {
            "predicted_yield_tph": predicted,
            "lower_bound_tph": lower,
            "upper_bound_tph": upper,
            "model_version": self._metadata.get("version", "unknown"),
            "confidence": metrics.get("val_r2"),
            "top_factors": [],
        }


class PriceModelService(BaseInferenceModel):
    """Loads the saved price forecast model artifact and runs inference."""

    def __init__(self, artifact_path: str):
        self.artifact_path = artifact_path
        self._pipeline = None
        self._metadata: Optional[dict] = None
        self._load()

    def _load(self):
        if not os.path.exists(self.artifact_path):
            logger.warning(
                "Price model artifact not found at %s. "
                "Price forecasts will be unavailable.", self.artifact_path
            )
            return
        try:
            bundle = joblib.load(self.artifact_path)
            self._pipeline = bundle.get("pipeline")
            self._metadata = bundle.get("metadata", {})
            logger.info(
                "Loaded price model %s (trained %s)",
                self._metadata.get("version", "unknown"),
                self._metadata.get("trained_at", "unknown"),
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to load price model: %s", exc)
            self._pipeline = None

    def is_available(self) -> bool:
        return self._pipeline is not None

    def predict(self, features: dict) -> dict:
        if not self.is_available():
            raise RuntimeError(
                "Price model is not available. Train the model first "
                "(see ml/market_price/train_price.py)."
            )
        # The price pipeline needs the recent historical series for the
        # requested commodity/market. Fetch it from the database so a
        # forecast can actually be produced instead of always failing.
        historical = features.get("historical_data") or []
        if not historical:
            try:
                historical = self._fetch_historical(features)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Could not fetch historical prices: %s", exc)
            features = {**features, "historical_data": historical}
        result = self._pipeline.predict_single(features)
        if result.get("available") and self._metadata:
            result["model_version"] = self._metadata.get(
                "version", result.get("model_version", "unknown")
            )
        return result

    def _fetch_historical(self, features: dict) -> list:
        """Pull recent market observations for the requested commodity/market."""
        from sqlalchemy import desc
        from backend.database import SessionLocal
        from backend.models import MarketPrice

        commodity = features.get("commodity")
        market = features.get("market")
        if not commodity or not market:
            return []

        session = SessionLocal()
        try:
            rows = (
                session.query(MarketPrice)
                .filter(
                    MarketPrice.commodity == commodity,
                    MarketPrice.market == market,
                )
                .order_by(desc(MarketPrice.date))
                .limit(90)
                .all()
            )
            rows = list(reversed(rows))  # chronological order
            return [
                {
                    "date": r.date.isoformat() if r.date else None,
                    "commodity": r.commodity,
                    "market": r.market,
                    "state": r.state or "",
                    "district": r.district or "",
                    "variety": r.variety or "Other",
                    "grade": r.grade or "FAQ",
                    "modal_price": r.modal_price,
                    "min_price": r.min_price,
                    "max_price": r.max_price,
                    "arrivals": r.arrivals,
                }
                for r in rows
            ]
        finally:
            session.close()