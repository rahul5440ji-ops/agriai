import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import (
    YieldPredictRequest,
    YieldOutput,
    SoilTestCreate,
    SoilTestResponse,
    FarmResponse,
)
from backend.services.yield_service import YieldService
from backend.ml.inference import YieldModelService
from backend.config import get_settings
from backend.models import Farm, SoilTest

router = APIRouter()
settings = get_settings()

_yield_service = YieldService(YieldModelService(settings.model_yield_path))


@router.post("/yield/predict", response_model=YieldOutput)
def predict_yield(request: YieldPredictRequest, db: Session = Depends(get_db)):
    """Predict expected crop yield for a field.

    Returns estimated yield, expected range, total production,
    model version, confidence, and top factors.
    """
    try:
        return _yield_service.predict(request, db)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:  # pragma: no cover - defensive
        logging.getLogger(__name__).exception("Unexpected error in predict_yield: %s", exc)
        raise HTTPException(status_code=500, detail="Internal prediction error")