"""Tests for market calculation logic."""
from backend.services.market_service import _data_freshness_days, _data_quality_score
from datetime import date, timedelta


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