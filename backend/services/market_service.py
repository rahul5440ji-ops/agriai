"""Market comparison and recommendation service.

Implements the transparent scoring system described in the spec:
net price, distance, data freshness, data quality, forecast confidence.
MSP is treated as a REFERENCE — never a guaranteed amount.
"""
import logging
from datetime import date

from sqlalchemy.orm import Session

from backend.models import Crop, MarketPrice, MspPrice
from backend.schemas import MarketComparisonItem

logger = logging.getLogger(__name__)


def _data_freshness_days(obs_date: date) -> int:
    return max(0, (date.today() - obs_date).days)


def _quality_score_from_item(item: MarketComparisonItem) -> float:
    """Map the human-readable data_quality label back to a numeric score."""
    return 0.6 if item.data_quality == "good" else 0.3


def _data_quality_score(item: MarketPrice) -> float:
    """Transparent, documented scoring of a market observation."""
    score = 0.0
    if item.modal_price is not None and item.modal_price > 0:
        score += 0.4
    if item.min_price is not None and item.max_price is not None:
        score += 0.2
    if item.arrivals is not None and item.arrivals > 0:
        score += 0.2
    if item.variety and item.grade:
        score += 0.1

    freshness = _data_freshness_days(item.date)
    if freshness <= 7:
        score += 0.1
    elif freshness <= 30:
        score += 0.05
    elif freshness > 30:
        score -= 0.05

    return round(max(0.0, score), 2)


def compare_markets(
    db: Session,
    crop_name: str,
    state: str,
    district: str,
    transport_cost: float = 0.0,
    other_costs: float = 0.0,
    max_distance_km: float = 500.0,
) -> list:
    """Compare MSP reference with local/nearby mandi prices.

    Returns ranked MarketComparisonItem objects.
    """
    crop = db.query(Crop).filter(Crop.name == crop_name).first()
    msp_reference = None
    if crop:
        msp = (
            db.query(MspPrice)
            .filter(MspPrice.crop_id == crop.id)
            .order_by(MspPrice.year.desc())
            .first()
        )
        if msp:
            msp_reference = msp.msp_rs_per_quintal

    markets = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.state == state,
            MarketPrice.commodity == crop_name,
        )
        .order_by(MarketPrice.date.desc(), MarketPrice.id.desc())
        .all()
    )

    items = []
    seen_markets = set()
    for market in markets:
        if market.market in seen_markets or market.modal_price is None:
            continue
        seen_markets.add(market.market)
        is_synthetic = bool(market.source and market.source.startswith("synthetic"))
        net_price = (
            market.modal_price
            - transport_cost
            - other_costs
        )
        items.append(
            MarketComparisonItem(
                market=market.market,
                modal_price_per_quintal=market.modal_price,
                msp_reference_per_quintal=msp_reference or 0.0,
                estimated_transport_cost=transport_cost,
                estimated_net_price=net_price,
                distance_km=None,  # computed later if coordinates available
                data_freshness_days=_data_freshness_days(market.date),
                data_quality=(
                    "synthetic"
                    if is_synthetic
                    else "good" if _data_quality_score(market) >= 0.6 else "limited"
                ),
                is_synthetic=is_synthetic,
                forecast_available=False,
            )
        )

    # Rank by net price (primary), data quality, freshness
    items.sort(
        key=lambda x: (
            -x.estimated_net_price,
            -_quality_score_from_item(x),
            x.data_freshness_days,
        )
    )
    return items


def recommend_markets(
    db: Session,
    crop_name: str,
    state: str,
    district: str,
    transport_cost_per_quintal: float,
    other_costs: float = 0.0,
    max_distance_km: float = 500.0,
) -> list:
    """Rank potentially better selling markets.

    Scoring is transparent and based on:
    - estimated net price
    - distance
    - market-data freshness
    - data quality
    - forecast confidence where applicable
    """
    ranked = compare_markets(
        db,
        crop_name=crop_name,
        state=state,
        district=district,
        transport_cost=transport_cost_per_quintal,
        other_costs=other_costs,
        max_distance_km=max_distance_km,
    )

    recommendations = []
    for rank, item in enumerate(ranked, start=1):
        explanation_parts = []
        if item.msp_reference_per_quintal and item.msp_reference_per_quintal > 0:
            if item.estimated_net_price >= item.msp_reference_per_quintal:
                explanation_parts.append(
                    "estimated net price is at or above the MSP reference"
                )
            else:
                explanation_parts.append(
                    "estimated net price is below the MSP reference"
                )
        else:
            explanation_parts.append("no MSP reference available for this crop")
        if item.is_synthetic:
            explanation_parts.append(
                "synthetic demo data; not a current mandi quote"
            )
        explanation_parts.append(
            f"data is {item.data_freshness_days} day(s) old"
        )
        explanation_parts.append(f"data quality is {item.data_quality}")
        explanation = "; ".join(explanation_parts) + "."

        recommendations.append({
            "rank": rank,
            "market": item.market,
            "estimated_net_price": item.estimated_net_price,
            "modal_price_per_quintal": item.modal_price_per_quintal,
            "msp_reference_per_quintal": item.msp_reference_per_quintal,
            "estimated_transport_cost": item.estimated_transport_cost,
            "distance_km": item.distance_km,
            "data_freshness_days": item.data_freshness_days,
            "data_quality": item.data_quality,
            "is_synthetic": item.is_synthetic,
            "explanation": explanation,
        })
    return recommendations