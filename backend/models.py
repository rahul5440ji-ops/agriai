from sqlalchemy import (
    Column, Integer, String, ForeignKey, TIMESTAMP,
    Float, Date, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.sql import func
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    phone_email = Column(String(255))  # nullable — PII minimized
    language = Column(String(10), nullable=False, default="en")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_users_phone", "phone_email"),
    )


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    state = Column(String(64), nullable=False)
    district = Column(String(64), nullable=False)
    village = Column(String(128))
    area_hectare = Column(Float, nullable=False)
    soil_type = Column(String(64))
    irrigation_type = Column(String(64))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_farms_user", "user_id"),
        Index("idx_farms_location", "state", "district"),
    )


class SoilTest(Base):
    __tablename__ = "soil_tests"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    ph = Column(Float, CheckConstraint("ph BETWEEN 0 AND 14"))
    nitrogen = Column(Float)
    phosphorus = Column(Float)
    potassium = Column(Float)
    organic_carbon = Column(Float, CheckConstraint("organic_carbon >= 0"))
    test_date = Column(Date)
    source = Column(String(128))

    __table_args__ = (
        Index("idx_soiltests_farm", "farm_id"),
    )


class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, unique=True)
    season = Column(String(32))
    unit = Column(String(16), default="tonne")


class FarmCycle(Base):
    __tablename__ = "farm_cycles"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    sowing_date = Column(Date)
    expected_harvest_date = Column(Date)
    season = Column(String(32))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_cycles_farm", "farm_id"),
    )


class YieldPrediction(Base):
    __tablename__ = "yield_predictions"

    id = Column(Integer, primary_key=True, index=True)
    farm_cycle_id = Column(Integer, ForeignKey("farm_cycles.id"), nullable=False)
    predicted_yield_tph = Column(Float, nullable=False)
    lower_bound_tph = Column(Float)
    upper_bound_tph = Column(Float)
    total_production_t = Column(Float)
    model_version = Column(String(64))
    confidence = Column(Float)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_yield_farm_cycle", "farm_cycle_id"),
    )


class MspPrice(Base):
    __tablename__ = "msp_prices"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    marketing_season = Column(String(32), nullable=False)
    year = Column(Integer, nullable=False)
    msp_rs_per_quintal = Column(Float, CheckConstraint("msp_rs_per_quintal >= 0"))
    source = Column(String(255))
    verified_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("crop_id", "marketing_season", "year",
                         name="uq_msp_crop_season_year"),
    )


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    state = Column(String(64), nullable=False)
    district = Column(String(64), nullable=False)
    market = Column(String(128), nullable=False)
    commodity = Column(String(128), nullable=False)
    variety = Column(String(128))
    grade = Column(String(64))
    min_price = Column(Float)
    max_price = Column(Float)
    modal_price = Column(Float)
    arrivals = Column(Float)
    unit = Column(String(16))  # kg, quintal, tonne
    source = Column(String(128))
    retrieved_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_market_prices_lookup", "state", "district", "commodity", "date"),
        UniqueConstraint("source", "market", "commodity", "date", "variety", "grade",
                         name="uq_market_obs"),
    )


class MarketRecommendation(Base):
    __tablename__ = "market_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    farm_cycle_id = Column(Integer, ForeignKey("farm_cycles.id"), nullable=False)
    market_price_id = Column(Integer, ForeignKey("market_prices.id"), nullable=False)
    estimated_transport_cost = Column(Float)
    estimated_net_price = Column(Float)
    rank = Column(Integer)
    explanation = Column(String(512))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_market_rec_farm_cycle", "farm_cycle_id"),
        Index("idx_market_rec_rank", "rank"),
    )


class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(64), nullable=False)
    version = Column(String(64), nullable=False)
    artifact_path = Column(String(512))
    metrics_json = Column(String(2048))
    trained_at = Column(TIMESTAMP(timezone=True))
    dataset_version = Column(String(64))

    __table_args__ = (
        UniqueConstraint("model_name", "version",
                         name="uq_model_name_version"),
    )