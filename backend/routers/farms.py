from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import FarmCreate, FarmResponse, SoilTestCreate, SoilTestResponse
from backend.models import Farm, SoilTest

router = APIRouter()


@router.post("/farms")
def create_farm(payload: FarmCreate, db: Session = Depends(get_db)):
    """Create a farm."""
    farm = Farm(
        state=payload.state,
        district=payload.district,
        village=payload.village,
        area_hectare=payload.area_hectare,
        soil_type=payload.soil_type,
        irrigation_type=payload.irrigation_type,
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return FarmResponse(
        id=farm.id,
        state=farm.state,
        district=farm.district,
        village=farm.village,
        area_hectare=farm.area_hectare,
        soil_type=farm.soil_type,
        irrigation_type=farm.irrigation_type,
        created_at=farm.created_at.isoformat() if farm.created_at else None,
    )


@router.get("/farms", response_model=list[FarmResponse])
def list_farms(db: Session = Depends(get_db)):
    """List all farms."""
    farms = db.query(Farm).order_by(Farm.id.desc()).all()
    return [
        FarmResponse(
            id=f.id,
            state=f.state,
            district=f.district,
            village=f.village,
            area_hectare=f.area_hectare,
            soil_type=f.soil_type,
            irrigation_type=f.irrigation_type,
            created_at=f.created_at.isoformat() if f.created_at else None,
        )
        for f in farms
    ]


@router.get("/farms/{farm_id}", response_model=FarmResponse)
def get_farm(farm_id: int, db: Session = Depends(get_db)):
    """Get farm details."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return FarmResponse(
        id=farm.id,
        state=farm.state,
        district=farm.district,
        village=farm.village,
        area_hectare=farm.area_hectare,
        soil_type=farm.soil_type,
        irrigation_type=farm.irrigation_type,
        created_at=farm.created_at.isoformat() if farm.created_at else None,
    )


@router.get("/farms/{farm_id}/soil-tests", response_model=list[SoilTestResponse])
def get_soil_tests(farm_id: int, db: Session = Depends(get_db)):
    """Get all soil tests for a farm."""
    tests = (
        db.query(SoilTest)
        .filter(SoilTest.farm_id == farm_id)
        .order_by(SoilTest.test_date.desc(), SoilTest.id.desc())
        .all()
    )
    return [
        SoilTestResponse(
            id=t.id,
            farm_id=t.farm_id,
            ph=t.ph,
            nitrogen=t.nitrogen,
            phosphorus=t.phosphorus,
            potassium=t.potassium,
            organic_carbon=t.organic_carbon,
            test_date=t.test_date,
            source=t.source,
        )
        for t in tests
    ]


@router.post("/farms/{farm_id}/soil-test")
def add_soil_test(farm_id: int, payload: SoilTestCreate, db: Session = Depends(get_db)):
    """Add a soil test for a farm."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    test = SoilTest(
        farm_id=farm_id,
        ph=payload.ph,
        nitrogen=payload.nitrogen,
        phosphorus=payload.phosphorus,
        potassium=payload.potassium,
        organic_carbon=payload.organic_carbon,
        test_date=payload.test_date,
        source="user_entered",
    )
    db.add(test)
    db.commit()
    db.refresh(test)
    return SoilTestResponse(
        id=test.id,
        farm_id=test.farm_id,
        ph=test.ph,
        nitrogen=test.nitrogen,
        phosphorus=test.phosphorus,
        potassium=test.potassium,
        organic_carbon=test.organic_carbon,
        test_date=test.test_date,
        source=test.source,
    )