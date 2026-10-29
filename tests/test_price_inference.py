from datetime import date, timedelta
from pathlib import Path

from backend.ml.inference import PriceModelService
from ml.market_price.inference_price import PriceForecastPipeline


def _historical_prices() -> list[dict]:
    today = date(2026, 10, 29)
    observations = []
    for offset in range(60, 0, -1):
        observed_date = today - timedelta(days=offset)
        price = 2200 + (60 - offset) * 2
        observations.append(
            {
                "date": observed_date.isoformat(),
                "state": "Maharashtra",
                "district": "Pune",
                "market": "Pune Mandi",
                "commodity": "wheat",
                "variety": "LOCAL",
                "grade": "FAQ",
                "modal_price": price,
                "min_price": price * 0.95,
                "max_price": price * 1.05,
                "arrivals": 300,
                "unit": "quintal",
            }
        )
    return observations


def test_price_model_artifact_loads_and_returns_prediction_interval():
    artifact = Path(__file__).parents[1] / "models" / "price_model.pkl"
    service = PriceModelService(str(artifact))

    assert service.is_available()
    result = service.predict(
        {
            "commodity": "wheat",
            "market": "Pune Mandi",
            "horizon_days": 7,
            "historical_data": _historical_prices(),
        }
    )

    assert result["available"]
    assert result["forecast_lower"] <= result["expected_midpoint"]
    assert result["expected_midpoint"] <= result["forecast_upper"]
    assert result["model_version"] == "price-v1-20261029"


def test_price_model_requires_historical_observations():
    pipeline = PriceForecastPipeline(series_models={"wheat_Pune Mandi": object()})

    result = pipeline.predict_single(
        {
            "commodity": "wheat",
            "market": "Pune Mandi",
            "historical_data": _historical_prices()[:59],
        }
    )

    assert result["available"] is False
    assert "Only 59 observations" in result["message"]
    assert "60 are required" in result["message"]
