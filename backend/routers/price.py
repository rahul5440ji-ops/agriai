from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import PriceForecastRequest, PriceForecastResponse
from backend.ml.inference import PriceModelService
from backend.config import get_settings

router = APIRouter()
settings = get_settings()

_price_service = PriceModelService(settings.model_price_path)


@router.get("/price/forecast", response_model=PriceForecastResponse)
def price_forecast(
    commodity: str = Query(..., description="Crop/commodity name"),
    market: str = Query(..., description="Mandi/market name"),
    horizon_days: int = Query(7, ge=1, le=30, description="Forecast horizon in days"),
    db: Session = Depends(get_db),
):
    """Forecast future market price for a crop in a particular market.

    Returns a forecast range and midpoint only when sufficient
    historical data exists. Otherwise returns an explicit
    "insufficient data" message — never a fabricated forecast.
    """
    if not settings.enable_price_forecast:
        raise HTTPException(
            status_code=503,
            detail="Price forecasting is disabled in this environment.",
        )

    if not _price_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Price forecast model is not available. Train the model first.",
        )

    try:
        result = _price_service.predict({
            "commodity": commodity,
            "market": market,
            "horizon_days": horizon_days,
        })
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    if not result.get("available", False):
        return PriceForecastResponse(
            available=False,
            message=result.get("message", "Insufficient historical data for reliable forecast."),
            commodity=commodity,
            market=market,
        )

    return PriceForecastResponse(
        available=True,
        message=None,
        commodity=result.get("commodity", commodity),
        market=result.get("market", market),
        forecast_lower=result.get("forecast_lower"),
        forecast_upper=result.get("forecast_upper"),
        expected_midpoint=result.get("expected_midpoint"),
        forecast_horizon_days=result.get("forecast_horizon_days", horizon_days),
        confidence=result.get("confidence"),
        confidence_note=result.get("confidence_note"),
        model_version=result.get("model_version"),
    )