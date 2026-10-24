"""Pydantic schemas for all API requests and responses."""
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional, List


# --- Yield Prediction ---
class YieldOutput(BaseModel):
    predicted_yield_tph: float
    lower_bound_tph: float
    upper_bound_tph: float
    total_production_t: float
    model_version: str
    confidence: Optional[float] = None
    top_factors: list = []
    regional_baseline_tph: Optional[float] = None
    regional_baseline_note: Optional[str] = None


class YieldPredictRequest(BaseModel):
    farm_id: int
    crop: str
    season: str
    area_hectare: float = Field(..., gt=0)
    soil: "SoilTestCreate"
    sowing_date: date


# --- Soil Test ---
class SoilTestCreate(BaseModel):
    ph: float = Field(..., ge=0, le=14)
    nitrogen: Optional[float] = Field(None, ge=0)
    phosphorus: Optional[float] = Field(None, ge=0)
    potassium: Optional[float] = Field(None, ge=0)
    organic_carbon: Optional[float] = Field(None, ge=0)
    test_date: date


class SoilTestResponse(BaseModel):
    id: int
    farm_id: int
    ph: float
    nitrogen: Optional[float]
    phosphorus: Optional[float]
    potassium: Optional[float]
    organic_carbon: Optional[float]
    test_date: Optional[date]
    source: Optional[str]


# --- Farm ---
class FarmCreate(BaseModel):
    state: str = Field(..., min_length=2, max_length=64)
    district: str = Field(..., min_length=2, max_length=64)
    village: Optional[str] = None
    area_hectare: float = Field(..., gt=0, description="Field area must be positive")
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None

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
    village: Optional[str]
    area_hectare: float
    soil_type: Optional[str]
    irrigation_type: Optional[str]
    created_at: Optional[str] = None


# --- Farm Cycle ---
class FarmCycleCreate(BaseModel):
    farm_id: int
    crop: str
    season: str
    sowing_date: date
    expected_harvest_date: Optional[date] = None


class FarmCycleResponse(BaseModel):
    id: int
    farm_id: int
    crop: str
    season: str
    sowing_date: Optional[date]
    expected_harvest_date: Optional[date]
    created_at: Optional[str] = None


# --- Market Comparison ---
class MarketComparisonItem(BaseModel):
    market: str
    modal_price_per_quintal: float
    msp_reference_per_quintal: float
    estimated_transport_cost: float
    estimated_net_price: float
    distance_km: Optional[float] = None
    data_freshness_days: int
    data_quality: str
    forecast_available: bool = False
    forecast_confidence: Optional[float] = None


# --- Market Recommendation ---
class MarketRecommendationRequest(BaseModel):
    crop: str
    state: str
    district: Optional[str] = ""
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
    distance_km: Optional[float] = None
    data_freshness_days: int
    data_quality: str
    explanation: str


# --- Price Forecast ---
class PriceForecastRequest(BaseModel):
    commodity: str
    market: str
    horizon_days: int = Field(7, ge=1, le=30)


class PriceForecastResponse(BaseModel):
    available: bool
    message: Optional[str] = None
    commodity: str
    market: str
    forecast_lower: Optional[float] = None
    forecast_upper: Optional[float] = None
    expected_midpoint: Optional[float] = None
    forecast_horizon_days: Optional[int] = None
    confidence: Optional[float] = None
    confidence_note: Optional[str] = None
    model_version: Optional[str] = None


# --- Health ---
class HealthResponse(BaseModel):
    status: str
    version: str
    models_loaded: dict


# --- Reference Data ---
class CropResponse(BaseModel):
    id: int
    name: str
    season: Optional[str]
    unit: Optional[str]


class MspReferenceResponse(BaseModel):
    crop: str
    marketing_season: str
    year: int
    msp_rs_per_quintal: float
    source: Optional[str]


# --- Advisory ---
class AdvisoryResponse(BaseModel):
    factors: List[str] = []
    recommendations: List[str] = []
    disclaimer: str = ""


# --- Error ---
class ErrorResponse(BaseModel):
    error: bool = True
    status_code: int
    detail: str
    path: str


# Resolve forward references
YieldPredictRequest.model_rebuild()