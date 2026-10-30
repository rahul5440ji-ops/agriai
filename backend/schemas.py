"""Pydantic schemas for all API requests and responses."""
from datetime import date

from pydantic import BaseModel, Field, field_validator


# --- Yield Prediction ---
class YieldOutput(BaseModel):
    predicted_yield_tph: float
    lower_bound_tph: float
    upper_bound_tph: float
    total_production_t: float
    model_version: str
    confidence: float | None = None
    top_factors: list = []
    regional_baseline_tph: float | None = None
    regional_baseline_note: str | None = None


class YieldPredictRequest(BaseModel):
    farm_id: int
    crop: str
    season: str
    area_hectare: float = Field(..., gt=0)
    soil: "SoilTestCreate"
    sowing_date: date
    rainfall_mm: float | None = None


# --- Soil Test ---
class SoilTestCreate(BaseModel):
    ph: float = Field(..., ge=0, le=14)
    nitrogen: float | None = Field(None, ge=0)
    phosphorus: float | None = Field(None, ge=0)
    potassium: float | None = Field(None, ge=0)
    organic_carbon: float | None = Field(None, ge=0)
    test_date: date


class SoilTestResponse(BaseModel):
    id: int
    farm_id: int
    ph: float
    nitrogen: float | None
    phosphorus: float | None
    potassium: float | None
    organic_carbon: float | None
    test_date: date | None
    source: str | None


# --- Farm ---
class FarmCreate(BaseModel):
    state: str = Field(..., min_length=2, max_length=64)
    district: str = Field(..., min_length=2, max_length=64)
    village: str | None = None
    area_hectare: float = Field(..., gt=0, description="Field area must be positive")
    soil_type: str | None = None
    irrigation_type: str | None = None

    @field_validator("area_hectare")
    @classmethod
    def validate_area(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("area_hectare must be greater than zero")
        return v


class FarmResponse(BaseModel):
    id: int
    state: str
    district: str
    village: str | None
    area_hectare: float
    soil_type: str | None
    irrigation_type: str | None
    created_at: str | None = None


# --- Farm Cycle ---
class FarmCycleCreate(BaseModel):
    farm_id: int
    crop: str
    season: str
    sowing_date: date
    expected_harvest_date: date | None = None


class FarmCycleResponse(BaseModel):
    id: int
    farm_id: int
    crop: str
    season: str
    sowing_date: date | None
    expected_harvest_date: date | None
    created_at: str | None = None


# --- Market Comparison ---
class MarketComparisonItem(BaseModel):
    market: str
    modal_price_per_quintal: float
    msp_reference_per_quintal: float
    estimated_transport_cost: float
    estimated_net_price: float
    distance_km: float | None = None
    data_freshness_days: int
    data_quality: str
    is_synthetic: bool = False
    forecast_available: bool = False
    forecast_confidence: float | None = None


# --- Market Recommendation ---
class MarketRecommendationRequest(BaseModel):
    crop: str
    state: str
    district: str | None = ""
    transport_cost_per_quintal: float = 0.0
    other_costs: float = 0.0
    max_distance_km: float = 500.0


class MarketRecommendationItem(BaseModel):
    rank: int
    market: str
    estimated_net_price: float
    modal_price_per_quintal: float
    msp_reference_per_quintal: float
    estimated_transport_cost: float
    distance_km: float | None = None
    data_freshness_days: int
    data_quality: str
    is_synthetic: bool = False
    explanation: str


# --- Price Forecast ---
class PriceForecastRequest(BaseModel):
    commodity: str
    market: str
    horizon_days: int = Field(7, ge=1, le=30)


class PriceForecastResponse(BaseModel):
    available: bool
    message: str | None = None
    commodity: str
    market: str
    forecast_lower: float | None = None
    forecast_upper: float | None = None
    expected_midpoint: float | None = None
    forecast_horizon_days: int | None = None
    confidence: float | None = None
    confidence_note: str | None = None
    model_version: str | None = None


# --- Health ---
class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: dict


# --- Reference Data ---
class CropResponse(BaseModel):
    id: int
    name: str
    season: str | None
    unit: str | None


class MspReferenceResponse(BaseModel):
    crop: str
    marketing_season: str
    year: int
    msp_rs_per_quintal: float
    source: str | None


# --- Advisory ---
class AdvisoryResponse(BaseModel):
    factors: list[str] = []
    recommendations: list[str] = []
    disclaimer: str = ""


# --- Error ---
class ErrorResponse(BaseModel):
    error: bool = True
    status_code: int
    detail: str
    path: str


# Resolve forward references
YieldPredictRequest.model_rebuild()