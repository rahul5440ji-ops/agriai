
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Crop, MspPrice
from backend.schemas import (
    CropResponse,
    MarketComparisonItem,
    MarketRecommendationItem,
    MarketRecommendationRequest,
    MspReferenceResponse,
)
from backend.services.market_service import compare_markets, recommend_markets

router = APIRouter()


@router.get("/markets/compare", response_model=list[MarketComparisonItem])
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
    return compare_markets(
        db=db,
        crop_name=crop,
        state=state,
        district=district,
        transport_cost=transport_cost,
        other_costs=other_costs,
    )


@router.post(
    "/markets/recommend",
    response_model=list[MarketRecommendationItem],
)
def recommend_markets_endpoint(
    body: MarketRecommendationRequest | None = None,
    crop: str | None = None,
    state: str | None = None,
    district: str = "",
    transport_cost_per_quintal: float = 0.0,
    other_costs: float = 0.0,
    max_distance_km: float = 500.0,
    db: Session = Depends(get_db),
):
    """Rank potentially better selling markets.

    Accepts parameters via JSON body or query parameters.
    """
    target_crop = body.crop if body else (crop or "")
    target_state = body.state if body else (state or "")
    target_district = (body.district if body else district) or ""
    target_transport = (
        body.transport_cost_per_quintal if body else transport_cost_per_quintal
    )
    target_other = body.other_costs if body else other_costs
    target_max_dist = body.max_distance_km if body else max_distance_km

    if not target_crop or not target_state:
        raise HTTPException(status_code=422, detail="Crop and state are required")

    result = recommend_markets(
        db=db,
        crop_name=target_crop,
        state=target_state,
        district=target_district,
        transport_cost_per_quintal=target_transport,
        other_costs=target_other,
        max_distance_km=target_max_dist,
    )
    return [MarketRecommendationItem(**item) for item in result]


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
