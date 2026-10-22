from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Crop, MspPrice
from backend.schemas import MarketComparisonItem, MarketRecommendationItem, CropResponse, MspReferenceResponse
from backend.services.market_service import compare_markets, recommend_markets

router = APIRouter()


@router.get("/markets/compare")
def compare_markets_endpoint(
    crop: str,
    state: str,
    district: str = "",
    transport_cost: float = 0.0,
    other_costs: float = 0.0,
    db: Session = Depends(get_db),
):
    """Compare Government MSP reference with local/nearby mandi prices.

    Returns a list of market comparison items with net price calculations.
    """
    try:
        result = compare_markets(
            db=db,
            crop_name=crop,
            state=state,
            district=district,
            transport_cost=transport_cost,
            other_costs=other_costs,
        )
        # Convert to MarketComparisonItem objects for response
        return [
            MarketComparisonItem(
                market=item.get("market", ""),
                modal_price_per_quintal=item.get("modal_price_per_quintal", 0),
                msp_reference_per_quintal=item.get("msp_reference_per_quintal", 0),
                estimated_transport_cost=item.get("estimated_transport_cost", 0),
                estimated_net_price=item.get("estimated_net_price", 0),
                distance_km=item.get("distance_km"),
                data_freshness_days=item.get("data_freshness_days", 0),
                data_quality=item.get("data_quality", "limited"),
                forecast_available=item.get("forecast_available", False),
                forecast_confidence=item.get("forecast_confidence"),
            )
            for item in result
        ]
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="Market comparison failed")


@router.post("/markets/recommend")
def recommend_markets_endpoint(
    crop: str,
    state: str,
    district: str = "",
    transport_cost_per_quintal: float = 0.0,
    other_costs: float = 0.0,
    max_distance_km: float = 500.0,
    db: Session = Depends(get_db),
):
    """Rank potentially better selling markets.

    Returns ranked market recommendations based on net price,
    distance, data freshness, quality, and forecast confidence.
    """
    try:
        result = recommend_markets(
            db=db,
            crop_name=crop,
            state=state,
            district=district,
            transport_cost_per_quintal=transport_cost_per_quintal,
            other_costs=other_costs,
            max_distance_km=max_distance_km,
        )
        return [MarketRecommendationItem(**item) for item in result]
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="Market recommendation failed")


@router.get("/crops")
def get_crops(db: Session = Depends(get_db)):
    """Get list of available crops."""
    crops = db.query(Crop).all()
    return [CropResponse(id=c.id, name=c.name, season=c.season, unit=c.unit) for c in crops]


@router.get("/msp-reference")
def get_msp_reference(crop: str, db: Session = Depends(get_db)):
    """Get MSP reference for a crop."""
    crop_record = db.query(Crop).filter(Crop.name.ilike(crop)).first()
    if not crop_record:
        raise HTTPException(status_code=404, detail="MSP reference not found")

    msp = (
        db.query(MspPrice)
        .filter(MspPrice.crop_id == crop_record.id)
        .order_by(MspPrice.year.desc())
        .first()
    )
    if not msp:
        raise HTTPException(status_code=404, detail="MSP reference not found")
    return MspReferenceResponse(
        crop=crop_record.name,
        marketing_season=msp.marketing_season,
        year=msp.year,
        msp_rs_per_quintal=msp.msp_rs_per_quintal,
        source=msp.source,
    )


