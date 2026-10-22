from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables.

    All values come from .env / deployment environment — nothing
    sensitive is hardcoded here.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    database_url: str
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: list = ["http://localhost:3000"]
    secret_key: str = "change-me-in-production"

    # ML
    ml_models_path: str = "./models"
    model_yield_path: str = "./models/yield_model.pkl"
    model_price_path: str = "./models/price_model.pkl"
    model_y_version: str = "yield-v1"
    model_p_version: str = "price-v1"

    # Feature flags
    enable_price_forecast: bool = True
    enable_advanced_analytics: bool = True

    # Source tokens
    data_gov_in_token: str = ""
    agmarknet_token: str = ""
    weather_api_key: str = ""


@lru_cache()
def get_settings() -> Settings:
    return Settings()