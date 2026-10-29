"""Train crop yield and market price models using rich synthetic data.

This script:
1. Generates synthetic data for India (19 states, 20 crops)
   - Incorporates agro-climatic zones, seasonal patterns, soil types
   - Adds realistic price seasonality, market-arrival dynamics
2. Trains both models (crop yield + market price forecasting)
3. Evaluates and saves models with full provenance

Usage:
    python scripts/train_with_synthetic_data.py
    python scripts/train_with_synthetic_data.py --yield-only
    python scripts/train_with_synthetic_data.py --price-only
    python scripts/train_with_synthetic_data.py --samples 5000
"""
import argparse
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.crop_yield.features_yield import build_features, get_target_column

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------
# Model output paths
# -----------------------------------------------------------------
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)
YIELD_MODEL_PATH = MODELS_DIR / "yield_model.pkl"
PRICE_MODEL_PATH = MODELS_DIR / "price_model.pkl"

# -----------------------------------------------------------------
# Rich India agricultural metadata
# -----------------------------------------------------------------
INDIA_DATA = {
    # state -> list of (district, agro_zone, avg_annual_rainfall_mm)
    "Maharashtra": [
        ("Pune", "Semi-arid", 700), ("Nashik", "Semi-arid", 750),
        ("Aurangabad", "Dryland", 630), ("Nagpur", "Vidarbha", 1050),
        ("Kolhapur", "Humid", 1500), ("Solapur", "Dryland", 580),
    ],
    "Punjab": [
        ("Ludhiana", "Indo-Gangetic", 750), ("Amritsar", "Indo-Gangetic", 680),
        ("Jalandhar", "Indo-Gangetic", 720), ("Patiala", "Indo-Gangetic", 700),
        ("Bathinda", "Semi-arid", 400),
    ],
    "Uttar Pradesh": [
        ("Agra", "Semi-arid", 680), ("Meerut", "Indo-Gangetic", 800),
        ("Kanpur", "Indo-Gangetic", 780), ("Lucknow", "Indo-Gangetic", 900),
        ("Varanasi", "Indo-Gangetic", 1100), ("Allahabad", "Indo-Gangetic", 1000),
    ],
    "Madhya Pradesh": [
        ("Bhopal", "Central Plateau", 1100), ("Indore", "Malwa", 900),
        ("Jabalpur", "Satpura", 1300), ("Gwalior", "Northern Plateau", 750),
        ("Sagar", "Vindhyan", 1150),
    ],
    "Rajasthan": [
        ("Jaipur", "Semi-arid", 580), ("Jodhpur", "Arid", 330),
        ("Udaipur", "Highland", 620), ("Kota", "Eastern", 750),
        ("Bikaner", "Arid", 270),
    ],
    "Karnataka": [
        ("Bengaluru", "Eastern Dry", 950), ("Mysuru", "Southern Dry", 750),
        ("Dharwad", "Northern Transition", 800), ("Belagavi", "North Moist", 1050),
        ("Tumkur", "Eastern Dry", 700),
    ],
    "Andhra Pradesh": [
        ("Guntur", "Krishna-Godavari Delta", 900), ("Kurnool", "Rayalaseema", 550),
        ("Visakhapatnam", "Northern Coastal", 1150), ("Kadapa", "Rayalaseema", 600),
    ],
    "Tamil Nadu": [
        ("Coimbatore", "Western Dry", 650), ("Madurai", "Southern Dry", 850),
        ("Chennai", "Northern Coastal", 1400), ("Tirunelveli", "Southern Coastal", 750),
    ],
    "Gujarat": [
        ("Ahmedabad", "Northern Dry", 750), ("Surat", "Southern Humid", 1350),
        ("Vadodara", "Central", 900), ("Rajkot", "Saurashtra", 600),
        ("Junagadh", "Saurashtra", 550),
    ],
    "Haryana": [
        ("Ambala", "Indo-Gangetic", 900), ("Hisar", "Semi-arid", 430),
        ("Rohtak", "Indo-Gangetic", 600), ("Karnal", "Indo-Gangetic", 800),
    ],
    "Bihar": [
        ("Patna", "Indo-Gangetic", 1100), ("Muzaffarpur", "North Bihar", 1250),
        ("Gaya", "Plateau", 1000), ("Bhagalpur", "Eastern", 1200),
    ],
    "West Bengal": [
        ("Kolkata", "Gangetic Delta", 1600), ("Bardhaman", "Gangetic Plain", 1400),
        ("Murshidabad", "North Bengal", 1500), ("Malda", "North Bengal", 1300),
    ],
    "Odisha": [
        ("Bhubaneswar", "Coastal Plain", 1450), ("Sambalpur", "Western Plateau", 1400),
        ("Cuttack", "Mahanadi Delta", 1550), ("Berhampur", "South Coastal", 1100),
    ],
    "Telangana": [
        ("Hyderabad", "Deccan Plateau", 800), ("Warangal", "Northern Plateau", 1000),
        ("Khammam", "Eastern", 1100), ("Nizamabad", "Northern", 950),
    ],
    "Assam": [
        ("Guwahati", "Brahmaputra Valley", 1700), ("Dibrugarh", "Upper Assam", 2100),
        ("Silchar", "Barak Valley", 2600),
    ],
    "Himachal Pradesh": [
        ("Shimla", "Mid Hills", 1100), ("Mandi", "Mid Hills", 1000),
        ("Kangra", "Outer Hills", 1400),
    ],
    "Jharkhand": [
        ("Ranchi", "Chota Nagpur", 1300), ("Dhanbad", "Plateau", 1250),
        ("Jamshedpur", "Eastern Plateau", 1200),
    ],
    "Chhattisgarh": [
        ("Raipur", "Chhattisgarh Plain", 1300), ("Bilaspur", "Northern", 1200),
        ("Jagdalpur", "Bastar", 1450),
    ],
    "Kerala": [
        ("Thiruvananthapuram", "Southern Coastal", 1750),
        ("Kozhikode", "Northern Coastal", 2600),
        ("Thrissur", "Midland", 2850),
    ],
}

# crop -> (season, base_yield_tph, yield_std_fraction, msp_per_quintal, price_volatility)
CROP_PROFILES = {
    "wheat":      ("rabi",   3.5,  0.18, 2275,  0.08),
    "rice":       ("kharif", 4.2,  0.20, 2183,  0.10),
    "maize":      ("kharif", 5.1,  0.22, 1962,  0.12),
    "sugarcane":  ("kharif", 72.0, 0.15, 340,   0.06),
    "cotton":     ("kharif", 2.1,  0.25, 6620,  0.18),
    "soybean":    ("kharif", 1.8,  0.22, 4892,  0.14),
    "groundnut":  ("kharif", 2.0,  0.20, 6377,  0.13),
    "mustard":    ("rabi",   1.3,  0.20, 5650,  0.12),
    "chickpea":   ("rabi",   1.1,  0.25, 5440,  0.15),
    "lentil":     ("rabi",   0.9,  0.22, 6000,  0.14),
    "sunflower":  ("kharif", 1.4,  0.23, 6400,  0.13),
    "jowar":      ("kharif", 1.6,  0.25, 3180,  0.15),
    "bajra":      ("kharif", 1.8,  0.24, 2500,  0.14),
    "barley":     ("rabi",   2.5,  0.18, 1735,  0.10),
    "turmeric":   ("kharif", 4.5,  0.28, 7000,  0.22),
    "onion":      ("rabi",   20.0, 0.30, 800,   0.35),
    "potato":     ("rabi",   25.0, 0.25, 600,   0.30),
    "tomato":     ("kharif", 18.0, 0.35, 500,   0.40),
    "chilli":     ("kharif", 3.5,  0.28, 5600,  0.25),
    "garlic":     ("rabi",   5.0,  0.25, 3200,  0.28),
}

SOIL_TYPES = [
    "alluvial", "black cotton", "red laterite", "loamy",
    "sandy loam", "clay loam", "silty clay", "regur", "laterite",
]

IRRIGATION_TYPES = ["canal", "borewell", "rainfed", "drip", "sprinkler", "tank"]

VARIETIES = {
    "wheat":  ["HD-3086", "GW-322", "Raj-4120"],
    "rice":   ["BPT-5204", "MTU-1010", "Swarna"],
    "maize":  ["DHM-117", "HQPM-1", "Ganga-5"],
    "cotton": ["Bt-Cotton", "DCH-32", "LRA-5166"],
    "default": ["LOCAL", "HYBRID", "IMPROVED"],
}

GRADES = ["FAQ", "Grade-A", "Grade-B", "Special"]


# =================================================================
# Synthetic data generation — Crop Yield
# =================================================================

def generate_synthetic_yield_data(n_samples: int = 3000, seed: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic crop yield data for India.

    Incorporates agro-climatic zones, seasonal patterns, soil
    nutrient interactions, rainfall, temperature, and year trend.
    """
    rng = np.random.default_rng(seed)
    logger.info("Generating %d synthetic yield samples ...", n_samples)

    sowing_months = {"kharif": (6, 8), "rabi": (10, 12), "zaid": (2, 4)}
    harvest_offsets = {"kharif": (10, 13), "rabi": (3, 5), "zaid": (5, 7)}

    optimal_rain = {
        "wheat": 500, "rice": 1200, "sugarcane": 1500,
        "cotton": 700, "potato": 600, "onion": 500,
        "default": 800,
    }

    irr_bonus = {
        "drip": 0.20, "sprinkler": 0.15, "canal": 0.12,
        "borewell": 0.10, "tank": 0.05, "rainfed": 0.0,
    }

    states = list(INDIA_DATA.keys())
    crops = list(CROP_PROFILES.keys())
    rows = []

    for _ in range(n_samples):
        state = str(rng.choice(states))
        _loc = INDIA_DATA[state][int(rng.integers(0, len(INDIA_DATA[state])))]
        district, agro_zone, avg_rainfall = str(_loc[0]), str(_loc[1]), float(_loc[2])
        crop = str(rng.choice(crops))
        _cp = CROP_PROFILES[crop]
        season, base_yield, std_frac, msp = str(_cp[0]), float(_cp[1]), float(_cp[2]), float(_cp[3])
        year = int(rng.choice([2020, 2021, 2022, 2023, 2024]))

        # Sowing / harvest dates
        sow_lo, sow_hi = sowing_months.get(season, (6, 8))
        sow_mo  = int(rng.integers(sow_lo, sow_hi + 1))
        sow_day = int(rng.integers(1, 28))
        harv_lo, harv_hi = harvest_offsets.get(season, (10, 13))
        harv_mo = (sow_mo + int(rng.integers(harv_lo, harv_hi))) % 12 or 12
        harv_yr = year + (1 if harv_mo < sow_mo else 0)

        soil_type  = str(rng.choice(SOIL_TYPES))
        irr_type   = str(rng.choice(IRRIGATION_TYPES))

        # Soil properties
        ph  = float(rng.uniform(5.5, 8.5))
        n   = float(rng.uniform(50, 280))
        p   = float(rng.uniform(10, 100))
        k   = float(rng.uniform(80, 350))
        oc  = float(rng.uniform(0.3, 2.8))

        # Rainfall & temperature
        rain = float(np.clip(rng.normal(avg_rainfall, avg_rainfall * 0.15), 200, None))
        temp_base = {"kharif": 28, "rabi": 18, "zaid": 32}.get(season, 25)
        temp = float(rng.normal(temp_base, 3.5))

        # Yield computation
        ph_factor   = max(0.0, 1 - abs(ph - 6.5) / 3.0)
        n_norm = float(np.clip(n / 280, 0, 1))
        p_norm = float(np.clip(p / 100, 0, 1))
        k_norm = float(np.clip(k / 350, 0, 1))
        oc_norm = float(np.clip(oc / 2.8, 0, 1))
        nutrient = 0.4 * n_norm + 0.25 * p_norm + 0.20 * k_norm + 0.15 * oc_norm
        opt_rain = optimal_rain.get(crop, optimal_rain["default"])
        rain_fac = max(0.3, 1 - abs(rain - opt_rain) / opt_rain)
        irr_fac  = irr_bonus.get(irr_type, 0.0)
        year_fac = 1 + 0.015 * (year - 2020)

        y = base_yield * (
            0.5 + 0.15 * ph_factor + 0.20 * nutrient + 0.10 * rain_fac + 0.05 * irr_fac * 2
        ) * year_fac
        y = max(0.05, y + float(rng.normal(0, base_yield * std_frac * 0.5)))

        rows.append({
            "state": state,
            "district": district,
            "agro_zone": agro_zone,
            "crop": crop,
            "season": season,
            "soil_type": soil_type,
            "irrigation_type": irr_type,
            "sowing_date":  f"{year}-{sow_mo:02d}-{sow_day:02d}",
            "sowing_month": sow_mo,
            "sowing_year":  year,
            "expected_harvest_date": f"{harv_yr}-{harv_mo:02d}-{sow_day:02d}",
            "ph": round(ph, 2),
            "nitrogen":       round(n, 1),
            "phosphorus":     round(p, 1),
            "potassium":      round(k, 1),
            "organic_carbon": round(oc, 2),
            "rainfall":       round(rain, 1),
            "temperature":    round(temp, 1),
            "year":           year,
            "yield_per_hectare": round(y, 3),
            "actual_yield_tph":  round(y, 3),
        })

    df = pd.DataFrame(rows)
    logger.info("Yield dataset: %d rows | crops=%d | states=%d",
                len(df), df["crop"].nunique(), df["state"].nunique())
    return df


# =================================================================
# Synthetic data generation — Market Prices
# =================================================================

def generate_synthetic_price_data(n_days: int = 730, seed: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic daily market price data for India.

    Incorporates seasonal price cycles (inverse to harvest), MSP floors,
    arrivals correlated with harvests, multi-year inflation drift, and
    commodity-specific volatility.
    """
    rng = np.random.default_rng(seed)

    combos = [
        ("wheat",     "Ludhiana APMC",      "Ludhiana",   "Punjab"),
        ("wheat",     "Kanpur Grain",        "Kanpur",     "Uttar Pradesh"),
        ("rice",      "Guntur Mandi",        "Guntur",     "Andhra Pradesh"),
        ("rice",      "Patna Mandi",         "Patna",      "Bihar"),
        ("maize",     "Indore APMC",         "Indore",     "Madhya Pradesh"),
        ("cotton",    "Guntur Mandi",        "Guntur",     "Andhra Pradesh"),
        ("cotton",    "Ahmedabad APMC",      "Ahmedabad",  "Gujarat"),
        ("soybean",   "Indore APMC",         "Indore",     "Madhya Pradesh"),
        ("groundnut", "Junagadh Mandi",      "Junagadh",   "Gujarat"),
        ("mustard",   "Jaipur Mandi",        "Jaipur",     "Rajasthan"),
        ("onion",     "Nashik APMC",         "Nashik",     "Maharashtra"),
        ("onion",     "Lasalgaon Mandi",     "Nashik",     "Maharashtra"),
        ("potato",    "Agra APMC",           "Agra",       "Uttar Pradesh"),
        ("tomato",    "Pune APMC",           "Pune",       "Maharashtra"),
        ("chilli",    "Guntur Mandi",        "Guntur",     "Andhra Pradesh"),
        ("chickpea",  "Indore APMC",         "Indore",     "Madhya Pradesh"),
        ("turmeric",  "Nizamabad Mandi",     "Nizamabad",  "Telangana"),
    ]

    start_date = datetime(2023, 1, 1)
    harvest_month = {
        "wheat": 4, "rice": 10, "maize": 10, "sugarcane": 1,
        "cotton": 10, "onion": 3, "potato": 3, "tomato": 10,
        "chilli": 1, "chickpea": 4, "turmeric": 2, "default": 11,
    }

    rows = []
    for commodity, market, district, state in combos:
        _, _, _, msp, volatility = CROP_PROFILES.get(
            commodity, ("kharif", 1.0, 0.2, 2000, 0.12)
        )
        msp = float(msp)
        price = msp * 0.90

        for day_idx in range(n_days):
            date = start_date + timedelta(days=day_idx)
            month = date.month

            # Seasonal: prices low just after harvest, high pre-harvest
            harv_mo = harvest_month.get(commodity, harvest_month["default"])
            months_from_harvest = abs((month - harv_mo + 6) % 12 - 6)
            season_mult = 1 + 0.12 * (months_from_harvest / 6.0)

            # Inflation drift (~4% annual)
            inflation_mult = 1 + 0.04 * (day_idx / 365.0)

            # Daily random walk
            daily_delta = float(rng.normal(0, msp * volatility * 0.02))
            price = max(msp * 0.70, price + daily_delta)
            price = min(price * season_mult * inflation_mult, msp * 2.5)

            min_p    = price * float(rng.uniform(0.92, 0.97))
            max_p    = price * float(rng.uniform(1.03, 1.08))
            modal_p  = price

            # Arrivals: high near harvest
            base_arr = 400 + 600 * max(0.0, 1 - months_from_harvest / 4.0)
            arrivals = max(10, int(rng.normal(base_arr, base_arr * 0.25)))

            variety = str(rng.choice(VARIETIES.get(commodity, VARIETIES["default"])))
            grade   = str(rng.choice(GRADES))

            rows.append({
                "date":        date.strftime("%Y-%m-%d"),
                "state":       state,
                "district":    district,
                "market":      market,
                "commodity":   commodity,
                "variety":     variety,
                "grade":       grade,
                "min_price":   round(min_p, 2),
                "max_price":   round(max_p, 2),
                "modal_price": round(modal_p, 2),
                "arrivals":    arrivals,
                "unit":        "quintal",
                "source":      "AgriAI_Synthetic_v2",
                "retrieved_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            })

    df = pd.DataFrame(rows)
    logger.info("Price dataset: %d rows | commodities=%d | markets=%d",
                len(df), df["commodity"].nunique(), df["market"].nunique())
    return df


# =================================================================
# Utilities
# =================================================================

def compute_metrics(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mae  = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2   = float(r2_score(y_true, y_pred))
    mape = float(
        np.mean(np.abs((y_true - y_pred) / np.clip(np.abs(y_true), 1e-6, None))) * 100
    )
    return {
        "mae": round(mae, 4), "rmse": round(rmse, 4),
        "r2": round(r2, 4), "mape_pct": round(mape, 2),
    }


def build_sklearn_pipeline(model, numeric_features, categorical_features):
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]), numeric_features),
            ("cat", Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]), categorical_features),
        ],
        remainder="drop",
    )
    return Pipeline([("preprocessor", preprocessor), ("regressor", model)])


def save_model(pipeline_or_bundle, path: Path, metadata: dict):
    artifact = {"pipeline": pipeline_or_bundle, "metadata": metadata}
    joblib.dump(artifact, path)
    size_kb = path.stat().st_size / 1024
    logger.info("Saved -> %s  (%.1f KB)", path, size_kb)


# =================================================================
# Crop Yield Training
# =================================================================

def train_yield_model(df: pd.DataFrame) -> dict:
    """Train crop yield prediction model on synthetic data."""
    logger.info("=" * 60)
    logger.info("CROP YIELD MODEL TRAINING")
    logger.info("=" * 60)

    df = build_features(df)

    numeric_features = [
        "ph", "nitrogen", "phosphorus", "potassium", "organic_carbon",
        "sowing_month_sin", "sowing_month_cos",
        "n_ratio", "p_ratio", "k_ratio", "soil_quality_score", "year_idx",
        "rainfall_log",
    ]
    if "temperature" in df.columns:
        numeric_features.append("temperature")

    categorical_features = [
        "state", "district", "crop", "season", "soil_type", "irrigation_type",
    ]
    numeric_features    = [c for c in numeric_features    if c in df.columns]
    categorical_features = [c for c in categorical_features if c in df.columns]
    target_col = get_target_column(df)

    df = df.dropna(subset=[target_col] + numeric_features).reset_index(drop=True)

    # Chronological split
    df = df.sort_values(["sowing_year", "sowing_month"]).reset_index(drop=True)
    split = int(len(df) * 0.80)
    X_train = df.iloc[:split][numeric_features + categorical_features]
    y_train = df.iloc[:split][target_col]
    X_val   = df.iloc[split:][numeric_features + categorical_features]
    y_val   = df.iloc[split:][target_col]
    logger.info("Train: %d rows  |  Val: %d rows", len(X_train), len(X_val))

    candidates = {
        "Ridge": Ridge(alpha=10.0, random_state=42),
        "RandomForest": RandomForestRegressor(
            n_estimators=200, max_depth=12, min_samples_split=4,
            min_samples_leaf=2, random_state=42, n_jobs=-1,
        ),
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=200, learning_rate=0.08, max_depth=6,
            subsample=0.8, random_state=42,
        ),
    }

    results = {}
    for name, model in candidates.items():
        pipe = build_sklearn_pipeline(model, numeric_features, categorical_features)
        pipe.fit(X_train, y_train)
        train_m = compute_metrics(y_train, pipe.predict(X_train))
        val_m   = compute_metrics(y_val,   pipe.predict(X_val))
        results[name] = {"pipeline": pipe, "train": train_m, "val": val_m}
        logger.info(
            "  %-20s  train R2=%.3f  val R2=%.3f  val MAE=%.3f  val MAPE=%.1f%%",
            name, train_m["r2"], val_m["r2"], val_m["mae"], val_m["mape_pct"],
        )

    best_name = max(results, key=lambda k: results[k]["val"]["r2"])
    best = results[best_name]
    logger.info("Best yield model: %s  (val R2=%.3f)", best_name, best["val"]["r2"])

    version = f"yield-synthetic-v2-{datetime.now().strftime('%Y%m%d')}"
    metadata = {
        "model_type": "crop_yield_predictor",
        "algorithm": best_name,
        "version": version,
        "trained_at": datetime.utcnow().isoformat(),
        "dataset": "AgriAI_Synthetic_v2",
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "crops": sorted(df["crop"].unique().tolist()),
        "states": sorted(df["state"].unique().tolist()),
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "target": target_col,
        "train_metrics": best["train"],
        "val_metrics": best["val"],
        "all_models": {k: {"train": v["train"], "val": v["val"]} for k, v in results.items()},
        "disclaimer": (
            "Trained on SYNTHETIC data. "
            "Replace with real field observations before production use."
        ),
    }

    save_model(best["pipeline"], YIELD_MODEL_PATH, metadata)

    logger.info("--- Yield Model Final Metrics ---")
    logger.info(
        "  Train  MAE=%.3f  RMSE=%.3f  R2=%.3f  MAPE=%.1f%%",
        best["train"]["mae"], best["train"]["rmse"],
        best["train"]["r2"],  best["train"]["mape_pct"],
    )
    logger.info(
        "  Val    MAE=%.3f  RMSE=%.3f  R2=%.3f  MAPE=%.1f%%",
        best["val"]["mae"],   best["val"]["rmse"],
        best["val"]["r2"],    best["val"]["mape_pct"],
    )

    return {"pipeline": best["pipeline"], "metadata": metadata}


# =================================================================
# Market Price Training
# =================================================================

MIN_OBS = 30


def _build_price_features(series_df: pd.DataFrame) -> pd.DataFrame:
    """Build lag/rolling features for one commodity-market time series."""
    df = series_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    t = "modal_price"

    for lag in [1, 3, 7, 14, 30]:
        df[f"price_lag_{lag}"] = df[t].shift(lag)

    shifted = df[t].shift(1)
    for w in [7, 14, 30]:
        df[f"price_roll_mean_{w}"] = shifted.rolling(w, min_periods=1).mean()
        df[f"price_roll_std_{w}"]  = shifted.rolling(w, min_periods=1).std().fillna(0)
        df[f"price_roll_min_{w}"]  = shifted.rolling(w, min_periods=1).min()
        df[f"price_roll_max_{w}"]  = shifted.rolling(w, min_periods=1).max()

    if "arrivals" in df.columns:
        for lag in [1, 7]:
            df[f"arrivals_lag_{lag}"] = df["arrivals"].shift(lag)

    df["month"]   = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["dow"]     = df["date"].dt.dayofweek
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["dow_sin"]   = np.sin(2 * np.pi * df["dow"] / 7)
    df["dow_cos"]   = np.cos(2 * np.pi * df["dow"] / 7)

    if "min_price" in df.columns and "max_price" in df.columns:
        df["price_spread"]      = df["max_price"] - df["min_price"]
        df["price_spread_lag1"] = df["price_spread"].shift(1)

    return df


PRICE_FEATURE_COLS = [
    "price_lag_1", "price_lag_3", "price_lag_7", "price_lag_14", "price_lag_30",
    "price_roll_mean_7", "price_roll_mean_14", "price_roll_mean_30",
    "price_roll_std_7", "price_roll_std_14", "price_roll_std_30",
    "price_roll_min_7", "price_roll_max_7",
    "arrivals_lag_1", "arrivals_lag_7",
    "month_sin", "month_cos", "dow_sin", "dow_cos",
    "price_spread_lag1",
]


def train_price_model(df: pd.DataFrame) -> dict:
    """Train per-series market price forecasting models."""
    logger.info("=" * 60)
    logger.info("MARKET PRICE MODEL TRAINING")
    logger.info("=" * 60)

    FORECAST_HORIZON = 7
    combos = df.groupby(["commodity", "market"])
    all_results = {}
    series_models = {}

    for (commodity, market), series_df in combos:
        key = f"{commodity}_{market}"
        logger.info("  Training: %s @ %s (%d obs)", commodity, market, len(series_df))

        df_feat = _build_price_features(series_df)
        avail_feats = [c for c in PRICE_FEATURE_COLS if c in df_feat.columns]
        df_feat = df_feat.dropna(subset=avail_feats + ["modal_price"])

        if len(df_feat) < MIN_OBS:
            logger.warning("    Skip %s: only %d rows", key, len(df_feat))
            all_results[key] = {"available": False,
                                 "reason": f"< {MIN_OBS} obs after feature eng."}
            series_models[key] = None
            continue

        train_df = df_feat.iloc[:-FORECAST_HORIZON]
        val_df   = df_feat.iloc[-FORECAST_HORIZON:]
        X_train  = train_df[avail_feats]
        y_train  = train_df["modal_price"]
        X_val    = val_df[avail_feats]
        y_val    = val_df["modal_price"]

        candidates = {
            "Ridge": Ridge(alpha=1.0, random_state=42),
            "RandomForest": RandomForestRegressor(
                n_estimators=100, max_depth=8,
                min_samples_split=3, random_state=42, n_jobs=-1,
            ),
            "GradientBoosting": GradientBoostingRegressor(
                n_estimators=100, learning_rate=0.1,
                max_depth=5, subsample=0.8, random_state=42,
            ),
        }

        best_pipe, best_rmse, best_model_name, best_val_m = None, float("inf"), None, None

        for name, model in candidates.items():
            preprocessor = ColumnTransformer(
                [("num", StandardScaler(), avail_feats)], remainder="drop"
            )
            pipe = Pipeline([("preprocessor", preprocessor), ("regressor", model)])
            pipe.fit(X_train, y_train)
            val_pred = pipe.predict(X_val)
            val_m = compute_metrics(y_val, val_pred)
            if val_m["rmse"] < best_rmse:
                best_rmse = val_m["rmse"]
                best_pipe = pipe
                best_model_name = name
                best_val_m = val_m

        naive_m = compute_metrics(y_val, np.full(len(y_val), y_train.iloc[-1]))
        logger.info(
            "    Best: %-18s  val RMSE=%.1f  R2=%.3f  MAPE=%.1f%%  (naive RMSE=%.1f)",
            best_model_name, best_rmse, best_val_m["r2"],
            best_val_m["mape_pct"], naive_m["rmse"],
        )

        series_models[key] = best_pipe
        all_results[key] = {
            "available": True,
            "model_name": best_model_name,
            "feature_cols": avail_feats,
            "val_metrics": best_val_m,
            "naive_rmse": naive_m["rmse"],
            "train_size": len(train_df),
            "val_size": len(val_df),
        }

    available = [v for v in all_results.values() if v.get("available")]
    agg_r2   = float(np.mean([v["val_metrics"]["r2"]      for v in available])) if available else 0
    agg_rmse = float(np.mean([v["val_metrics"]["rmse"]     for v in available])) if available else 0
    agg_mape = float(np.mean([v["val_metrics"]["mape_pct"] for v in available])) if available else 0

    logger.info("--- Price Model Summary (%d/%d series trained) ---",
                len(available), len(all_results))
    logger.info("  Agg  R2=%.3f  RMSE=%.1f  MAPE=%.1f%%", agg_r2, agg_rmse, agg_mape)

    version = f"price-synthetic-v2-{datetime.now().strftime('%Y%m%d')}"
    metadata = {
        "model_type": "market_price_forecaster",
        "version": version,
        "trained_at": datetime.utcnow().isoformat(),
        "dataset": "AgriAI_Synthetic_v2",
        "forecast_horizon_days": FORECAST_HORIZON,
        "series_count": len(all_results),
        "available_series": len(available),
        "commodities": sorted(df["commodity"].unique().tolist()),
        "markets": sorted(df["market"].unique().tolist()),
        "aggregate_metrics": {
            "r2": round(agg_r2, 4),
            "rmse": round(agg_rmse, 2),
            "mape_pct": round(agg_mape, 2),
        },
        "series_results": all_results,
        "disclaimer": (
            "Trained on SYNTHETIC data. "
            "Replace with real APMC/Agmarknet data before production use."
        ),
    }

    # Save bundle: {series_models, metadata}
    bundle_path = PRICE_MODEL_PATH
    joblib.dump({"series_models": series_models, "metadata": metadata}, bundle_path)
    size_kb = bundle_path.stat().st_size / 1024
    logger.info("Saved price bundle -> %s  (%.1f KB)", bundle_path, size_kb)

    return {"series_models": series_models, "metadata": metadata}


# =================================================================
# Main
# =================================================================

def parse_args():
    p = argparse.ArgumentParser(description="Train AgriAI models with synthetic data")
    p.add_argument("--yield-only",  action="store_true", help="Train only yield model")
    p.add_argument("--price-only",  action="store_true", help="Train only price model")
    p.add_argument("--samples",     type=int, default=3000,
                   help="Yield samples to generate (default: 3000)")
    p.add_argument("--price-days",  type=int, default=730,
                   help="Days of price history per series (default: 730)")
    p.add_argument("--seed",        type=int, default=42, help="Random seed")
    return p.parse_args()


def main():
    args = parse_args()
    both = not args.yield_only and not args.price_only

    logger.info("=" * 60)
    logger.info("AgriAI -- Synthetic Data Training Pipeline")
    logger.info("Timestamp: %s", datetime.now().isoformat())
    logger.info("=" * 60)

    if both or args.yield_only:
        yield_df = generate_synthetic_yield_data(n_samples=args.samples, seed=args.seed)
        train_yield_model(yield_df)

    if both or args.price_only:
        price_df = generate_synthetic_price_data(n_days=args.price_days, seed=args.seed)
        train_price_model(price_df)

    logger.info("=" * 60)
    logger.info("Training complete!")
    if both or args.yield_only:
        logger.info("  Yield model -> %s", YIELD_MODEL_PATH)
    if both or args.price_only:
        logger.info("  Price model -> %s", PRICE_MODEL_PATH)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
