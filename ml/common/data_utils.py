"""Data ingestion adapters for AgriAI.

Handles ingestion from government datasets, market data providers, and weather APIs.
All data is normalized, validated, and retains provenance metadata.
"""
import pandas as pd
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session

import logging
from backend.models import MarketPrice
from backend.models import Crop, Farm, SoilTest


class UnitNormalizer:
    """Normalize units (kg, quintal, tonne, hectare, acre)."""

    MASS_TO_KG = {"kg": 1, "quintal": 100, "tonne": 1000}
    AREA_TO_HA = {"hectare": 1, "acre": 0.404686}

    @staticmethod
    def mass(value, unit):
        return value * UnitNormalizer.MASS_TO_KG.get(unit, 1)

    @staticmethod
    def area(value, unit):
        return value * UnitNormalizer.AREA_TO_HA.get(unit, 1)


class DataProvenanceTracker:
    """Track data provenance for every record."""

    @staticmethod
    def generate_record_id(record, source):
        import hashlib
        data = json.dumps(record, sort_keys=True, default=str)
        return hashlib.md5(f"{source}:{data}".encode()).hexdigest()

    @staticmethod
    def wrap_provenance(record, source, source_record_id, obs_date,
                        geo_level, crop, validation_status):
        record["_source"] = source
        record["_source_record_id"] = source_record_id
        record["_retrieved_at"] = datetime.utcnow().isoformat()
        record["_obs_date"] = obs_date
        record["_geo_level"] = geo_level
        record["_crop"] = crop
        record["_validation_status"] = validation_status
        return record


class DataIngestionError(Exception):
    """Custom exception for data ingestion errors."""
    pass


class DataSource:
    """Base class for data sources."""
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch(self, *args, **kwargs) -> pd.DataFrame:
        raise NotImplementedError
