"""Yield prediction service.

Orchestrates: input validation → ML inference → advisory rules.
ML training is NOT performed here — it lives in ml/.
"""
import logging
from datetime import date
from sqlalchemy.orm import Session
from backend.schemas import YieldPredictRequest, YieldOutput
from backend.ml.inference import YieldModelService
from backend.models import Farm

logger = logging.getLogger(__name__)


class YieldService:
    def __init__(self, model_service: YieldModelService):
        self.model = model_service

    def _get_baseline(self, crop: str, season: str, year: int) -> dict:
        """Get regional yield baseline as a reference point.

        Returns None if the baseline model is not available.
        """
        try:
            from ml.crop_yield.inference_baseline import predict_baseline
            return predict_baseline(
                crop=crop,
                season=season,
                year=year,
            )
        except Exception as exc:
            logger.warning("Baseline model not available: %s", exc)
            return None

    def predict(self, request: YieldPredictRequest, db: Session) -> YieldOutput:
        if not self.model.is_available():
            raise RuntimeError(
                "Yield model is not available. Train the model first."
            )

        # Look up the farm's state so the model can use regional context
        farm = db.query(Farm).filter(Farm.id == request.farm_id).first()
        state = farm.state if farm else "unknown"

        features = {
            "state": state,
            "district": farm.district if farm else "unknown",
            "crop": request.crop,
            "season": request.season,
            "area_hectare": request.area_hectare,
            "ph": request.soil.ph,
            "nitrogen": request.soil.nitrogen,
            "phosphorus": request.soil.phosphorus,
            "potassium": request.soil.potassium,
            "organic_carbon": request.soil.organic_carbon,
            "sowing_month": request.sowing_date.month,
            "sowing_year": request.sowing_date.year,
        }

        result = self.model.predict(features)

        predicted_yield = float(result["predicted_yield_tph"])
        lower = float(result.get("lower_bound_tph", predicted_yield))
        upper = float(result.get("upper_bound_tph", predicted_yield))
        total_production = predicted_yield * request.area_hectare

        # Get regional baseline as reference
        baseline = self._get_baseline(
            crop=request.crop,
            season=request.season,
            year=request.sowing_date.year,
        )

        return YieldOutput(
            predicted_yield_tph=predicted_yield,
            lower_bound_tph=lower,
            upper_bound_tph=upper,
            total_production_t=total_production,
            model_version=result.get("model_version", "unknown"),
            confidence=result.get("confidence"),
            top_factors=result.get("top_factors", []),
            regional_baseline_tph=baseline["baseline_yield_tph"] if baseline else None,
            regional_baseline_note=(
                baseline["disclaimer"] if baseline else None
            ),
        )