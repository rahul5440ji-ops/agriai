"""Tests for market calculation logic."""
from datetime import date, timedelta

from backend.models import Crop, MarketPrice, MspPrice
from backend.services.market_service import (
    _data_freshness_days,
    _data_quality_score,
)
from scripts.seed_data import COMMODITY_PRICE_BASE, MARKET_DATA, seed_market_prices


def test_data_freshness_days():
    """Test data freshness calculation."""
    today = date.today()
    assert _data_freshness_days(today) == 0
    assert _data_freshness_days(today - timedelta(days=5)) == 5
    assert _data_freshness_days(today - timedelta(days=30)) == 30


def test_data_quality_score_complete():
    """Test data quality score for a complete market observation."""
    from unittest.mock import MagicMock

    item = MagicMock()
    item.modal_price = 2500
    item.min_price = 2400
    item.max_price = 2600
    item.arrivals = 100
    item.variety = "HD-2967"
    item.grade = "FAQ"
    item.date = date.today()

    score = _data_quality_score(item)
    assert score >= 0.9  # Should get most points


def test_data_quality_score_incomplete():
    """Test data quality score for an incomplete observation."""
    from unittest.mock import MagicMock

    item = MagicMock()
    item.modal_price = None  # Missing modal price
    item.min_price = 2400
    item.max_price = 2600
    item.arrivals = 100
    item.variety = "HD-2967"
    item.grade = "FAQ"
    item.date = date.today() - timedelta(days=60)  # Stale

    score = _data_quality_score(item)
    assert score < 0.5  # Should get fewer points


def test_synthetic_market_data_is_labeled_in_api(client, db):
    """Synthetic observations remain identifiable in public market responses."""
    crop = Crop(name="wheat", season="rabi", unit="tonne")
    db.add(crop)
    db.flush()
    db.add(MspPrice(
        crop_id=crop.id,
        marketing_season="2023-24",
        year=2023,
        msp_rs_per_quintal=2275,
        source="CACP/GoI 2023-24 official MSP",
    ))
    db.add(MarketPrice(
        date=date.today(),
        state="Maharashtra",
        district="Pune",
        market="Pune Mandi",
        commodity="wheat",
        modal_price=2400,
        min_price=2300,
        max_price=2500,
        arrivals=100,
        unit="quintal",
        source="synthetic-demo",
    ))
    db.add(MarketPrice(
        date=date.today() - timedelta(days=1),
        state="Maharashtra",
        district="Pune",
        market="Pune Mandi",
        commodity="wheat",
        modal_price=2300,
        min_price=2200,
        max_price=2400,
        arrivals=100,
        unit="quintal",
        source="synthetic-demo",
    ))
    db.commit()

    comparison = client.get(
        "/api/v1/markets/compare",
        params={"crop": "wheat", "state": "Maharashtra", "district": "Pune"},
    )
    assert comparison.status_code == 200
    assert len(comparison.json()) == 1
    assert comparison.json()[0]["is_synthetic"] is True
    assert comparison.json()[0]["modal_price_per_quintal"] == 2400
    assert comparison.json()[0]["data_quality"] == "synthetic"

    recommendations = client.post(
        "/api/v1/markets/recommend",
        json={"crop": "wheat", "state": "Maharashtra", "district": "Pune"},
    )
    assert recommendations.status_code == 200
    assert recommendations.json()[0]["is_synthetic"] is True
    assert "synthetic demo data" in recommendations.json()[0]["explanation"]


def test_synthetic_market_seed_is_idempotent(db):
    """Repeated seeding does not duplicate synthetic observations."""
    seed_market_prices(db, n_days=1)
    expected_count = len(MARKET_DATA) * len(COMMODITY_PRICE_BASE)
    first = (
        db.query(MarketPrice)
        .filter(MarketPrice.source == "synthetic-demo")
        .order_by(MarketPrice.market, MarketPrice.commodity)
        .first()
    )
    first_price = first.modal_price

    seed_market_prices(db, n_days=1)

    assert (
        db.query(MarketPrice)
        .filter(MarketPrice.source == "synthetic-demo")
        .count()
        == expected_count
    )
    repeated = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.source == "synthetic-demo",
            MarketPrice.market == first.market,
            MarketPrice.commodity == first.commodity,
        )
        .first()
    )
    assert repeated.modal_price == first_price