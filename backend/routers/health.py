from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.database import get_db
from backend.config import get_settings
from backend.schemas import HealthResponse

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health endpoint for deployment checks.

    Returns status, version, and model load state.
    Never exposes secrets or filesystem paths.
    """
    # Check database connectivity using a portable query
    db.execute(text("SELECT 1"))

    # Check model artifacts exist
    import os
    yield_loaded = os.path.exists(settings.model_yield_path)
    price_loaded = os.path.exists(settings.model_price_path)

    return HealthResponse(
        status="healthy",
        version="0.1.0",
        models_loaded={
            "yield_model": yield_loaded,
            "price_model": price_loaded,
        }
    )