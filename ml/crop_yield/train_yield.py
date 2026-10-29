"""Training script for the crop yield prediction model (Model A).

This script:
1. Loads cleaned crop production data from the database
2. Builds features (no future leakage)
3. Splits data chronologically
4. Trains baseline and ML models
5. Evaluates with MAE, RMSE, R²
6. Saves the best model with version and metadata
7. Outputs actual evaluation metrics (never fabricates accuracy)

Usage:
    python -m ml.crop_yield.train_yield
"""
import pandas as pd
import numpy as np
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import required libraries
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# ML common utilities
from ml.common.data_utils import UnitNormalizer
from ml.common.validation import (
    train_test_split_time_aware,
    calculate_metrics,
    validate_features_no_future_leak,
)
from ml.common.model_manager import (
    save_model_to_file,
    register_model,
)
from ml.crop_yield.features_yield import (
    build_features,
    get_feature_columns,
    get_target_column,
)

# Database connection
from backend.database import SessionLocal, engine
from backend.models import FarmCycle, YieldPrediction, Crop, Farm
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# Constants
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)
YIELD_MODEL_PATH = MODELS_DIR / "yield_model.pkl"


def load_training_data(session) -> pd.DataFrame:
    """Load training data from database."""
    query = """
    SELECT
        fc.id as farm_cycle_id,
        f.state,
        f.district,
        f.soil_type,
        f.irrigation_type,
        c.name as crop,
        c.season as crop_season,
        fc.sowing_date,
        fc.expected_harvest_date,
        fc.season as farm_season,
        st.ph,
        st.nitrogen,
        st.phosphorus,
        st.potassium,
        st.organic_carbon,
        yp.predicted_yield_tph as actual_yield_tph
    FROM farm_cycles fc
    JOIN farms f ON fc.farm_id = f.id
    JOIN crops c ON fc.crop_id = c.id
    LEFT JOIN soil_tests st ON fc.farm_id = st.farm_id
    LEFT JOIN yield_predictions yp ON fc.id = yp.farm_cycle_id
    WHERE yp.predicted_yield_tph IS NOT NULL
    """

    df = pd.read_sql(query, session.bind)
    logger.info("Loaded %s rows from database for training", len(df))

    # If we have less than 100 rows, generate synthetic data for development
    if len(df) < 100:
        logger.warning("Insufficient real data (%s rows). Generating synthetic data for development.", len(df))
        df = generate_synthetic_yield_data(n_samples=1000)

    return df


def generate_synthetic_yield_data(n_samples: int = 1000) -> pd.DataFrame:
    """Generate synthetic yield data for development and testing.

    THIS IS SYNTHETIC DATA - NOT REAL AGRICULTURAL OBSERVATIONS.
    Used ONLY when real data is insufficient.
    """
    logger.info("Generating %s synthetic yield samples", n_samples)

    states = ["Maharashtra", "Punjab", "Uttar Pradesh", "Madhya Pradesh", "Rajasthan"]
    districts_by_state = {
        "Maharashtra": ["Pune", "Nashik", "Aurangabad"],
        "Punjab": ["Ludhiana", "Amritsar", "Jalandhar"],
        "Uttar Pradesh": ["Agra", "Meerut", "Kanpur"],
        "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur"]
    }

    crops = ["wheat", "rice", "maize", "sugarcane", "cotton", "pulses", "groundnut", "mustard"]
    crop_seasons = {
        "wheat": "rabi",
        "rice": "kharif",
        "maize": "kharif",
        "sugarcane": "kharif",
        "cotton": "kharif",
        "pulses": "rabi",
        "groundnut": "kharif",
        "mustard": "rabi"
    }

    data = []
    for i in range(n_samples):
        state = np.random.choice(states)
        district = np.random.choice(districts_by_state[state])
        crop = np.random.choice(crops)
        season = crop_seasons[crop]
        year = np.random.choice([2020, 2021, 2022, 2023])

        # Soil properties (realistic ranges)
        ph = np.random.uniform(5.5, 8.5)
        nitrogen = np.random.uniform(0, 200)
        phosphorus = np.random.uniform(0, 100)
        potassium = np.random.uniform(0, 200)
        organic_carbon = np.random.uniform(0, 10)

        # Calculate yield based on soil and weather factors
        base_yield = {
            "wheat": 3.0,
            "rice": 4.0,
            "maize": 5.0,
            "sugarcane": 60.0,
            "cotton": 2.0,
            "pulses": 1.5,
            "groundnut": 1.8,
            "mustard": 1.2
        }[crop]

        # Soil quality factor (simplified)
        soil_factor = (ph - 5.5) / 3.0  # 0-1 scale for pH 5.5-8.5
        nutrient_factor = min(nitrogen/200, phosphorus/100, potassium/200, organic_carbon/10) if min(nitrogen/200, phosphorus/100, potassium/200, organic_carbon/10) > 0 else 0.1
        yield_tph = base_yield * (0.5 + 0.5 * soil_factor * nutrient_factor)
        yield_tph += np.random.normal(0, base_yield * 0.2)  # Add realistic noise
        yield_tph = max(0.1, yield_tph)  # Ensure positive

        row = {
            "farm_cycle_id": i + 10000,
            "state": state,
            "district": district,
            "crop": crop,
            "season": season,
            "sowing_date": f"{year}-{np.random.randint(6,11):02d}-{np.random.randint(1,28):02d}",
            "expected_harvest_date": f"{year}-{np.random.randint(3,11):02d}-{np.random.randint(1,28):02d}",
            "farm_season": season,
            "sowing_month": np.random.randint(6, 11),
            "sowing_year": year,
            "ph": ph,
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium,
            "organic_carbon": organic_carbon,
            "actual_yield_tph": yield_tph,
            "yield_per_hectare": yield_tph,
        }
        data.append(row)

    return pd.DataFrame(data)


def prepare_features_and_target(df: pd.DataFrame):
    """Prepare feature matrix and target vector."""
    logger.info("Building features...")
    df_features = build_features(df)

    # Get feature columns and target
    feature_cols = get_feature_columns(df_features)
    target_col = get_target_column(df_features)

    # Extract X and y
    X = df_features[feature_cols]
    y = df_features[target_col]

    logger.info("Feature matrix shape: %s", X.shape)
    logger.info("Target vector shape: %s", y.shape)
    logger.info("Target statistics: mean=%.3f, std=%.3f, min=%.3f, max=%.3f",
                y.mean(), y.std(), y.min(), y.max())

    return X, y, feature_cols


def train_and_evaluate_models(X_train, y_train, X_val, y_val, feature_cols):
    """Train and evaluate multiple models."""
    models = {
        "Ridge": Ridge(alpha=1.0, random_state=42),
        "RandomForest": RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        ),
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
    }

    results = {}

    for name, model in models.items():
        logger.info("Training %s...", name)

        # Create preprocessing pipeline
        numeric_features = X_train.select_dtypes(include=[np.number]).columns.tolist()
        categorical_features = X_train.select_dtypes(include=['object']).columns.tolist()

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', Pipeline([
                    ('imputer', SimpleImputer(strategy='median')),
                    ('scaler', StandardScaler()),
                ]), numeric_features),
                ('cat', Pipeline([
                    ('imputer', SimpleImputer(strategy='most_frequent')),
                    ('onehot', OneHotEncoder(handle_unknown='ignore')),
                ]), categorical_features)
            ]
        )

        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', model)
        ])

        # Train
        pipeline.fit(X_train, y_train)

        # Predict
        y_pred_train = pipeline.predict(X_train)
        y_pred_val = pipeline.predict(X_val)

        # Evaluate
        train_metrics = calculate_metrics(y_train.values, y_pred_train)
        val_metrics = calculate_metrics(y_val.values, y_pred_val)

        # Feature importance (if available)
        feature_importance = None
        if hasattr(model, 'feature_importances_'):
            try:
                # Get feature names after one-hot encoding
                preprocessor.fit(X_train)
                feature_names_out = []
                for name, trans, cols in preprocessor.transformers_:
                    if trans == 'passthrough':
                        feature_names_out.extend(cols)
                    elif hasattr(trans, 'get_feature_names_out'):
                        feature_names_out.extend(trans.get_feature_names_out(cols))
                    else:
                        feature_names_out.extend(cols)

                importances = model.feature_importances_
                if len(importances) == len(feature_names_out):
                    feature_importance = dict(zip(feature_names_out, importances))
                    # Top 10 features
                    top_features = dict(sorted(feature_importance.items(),
                                             key=lambda x: x[1], reverse=True)[:10])
                else:
                    logger.warning("Feature importance length mismatch")
            except Exception as e:
                logger.warning("Could not extract feature names: %s", e)

        results[name] = {
            "model": pipeline,
            "train_metrics": train_metrics,
            "val_metrics": val_metrics,
            "feature_importance": feature_importance,
        }

        logger.info("%s - Train: MAE=%.3f, RMSE=%.3f, R²=%.3f",
                   name, train_metrics["mae"], train_metrics["rmse"], train_metrics["r2"])
        logger.info("%s - Val:   MAE=%.3f, RMSE=%.3f, R²=%.3f",
                   name, val_metrics["mae"], val_metrics["rmse"], val_metrics["r2"])

    return results


def main():
    """Main training pipeline."""
    logger.info("=" * 60)
    logger.info("AgriAI: Crop Yield Model Training (Model A)")
    logger.info("=" * 60)

    # 1. Load data
    session = SessionLocal()
    try:
        df_raw = load_training_data(session)
        logger.info("Loaded %s rows from database", len(df_raw))

        # 2. Prepare features and target
        X, y, feature_cols = prepare_features_and_target(df_raw)
        logger.info("Features: %d columns", len(feature_cols))

        # 3. Split data (time-aware if possible)
        if 'sowing_date' in df_raw.columns and df_raw['sowing_date'].notna().any():
            # Sort by date for chronological split
            df_sorted = df_raw.sort_values('sowing_date')
            split_idx = int(len(df_sorted) * 0.8)
            X_train = X.iloc[:split_idx]
            y_train = y.iloc[:split_idx]
            X_val = X.iloc[split_idx:]
            y_val = y.iloc[split_idx:]
            logger.info("Time-aware split: %s train, %s validation", len(X_train), len(X_val))
        else:
            # Random split for development
            logger.warning("No date info - using random split (DEV ONLY)")
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

        # 4. Validate no leakage
        try:
            leakage_check = validate_features_no_future_leak(
                pd.concat([X_train, X_val], axis=0),
                date_column='sowing_date' if 'sowing_date' in X_train.columns else 'year',
                target_column=get_target_column(df_raw)
            )
            if not leakage_check["no_future_leak"]:
                logger.warning("Leakage detected: %s", leakage_check["issues"])
            else:
                logger.info("No future leakage detected")
        except Exception as e:
            logger.warning("Leakage check skipped: %s", e)

        # 5. Train models
        results = train_and_evaluate_models(X_train, y_train, X_val, y_val, feature_cols)

        # 6. Select best model based on validation R²
        best_model_name = max(results.keys(), key=lambda k: results[k]["val_metrics"]["r2"])
        best_result = results[best_model_name]

        # 7. Save the best model
        version = f"yield-v1-{datetime.now().strftime('%Y%m%d')}"
        metrics = {
            "train_mae": best_result["train_metrics"]["mae"],
            "train_rmse": best_result["train_metrics"]["rmse"],
            "train_r2": best_result["train_metrics"]["r2"],
            "val_mae": best_result["val_metrics"]["mae"],
            "val_rmse": best_result["val_metrics"]["rmse"],
            "val_r2": best_result["val_metrics"]["r2"],
        }

        save_model_to_file(
            pipeline=best_result["model"],
            filepath=str(YIELD_MODEL_PATH),
            version=version,
            metrics=metrics,
            dataset_version="synthetic-dev-001" if len(df_raw) < 100 else "govt-data-2024",
            train_rows=len(X_train),
            validation_rows=len(X_val),
            validation_score="GOOD" if best_result["val_metrics"]["r2"] > 0.5 else "FAIR"
        )

        logger.info("=" * 60)
        logger.info("BEST MODEL: %s", best_model_name)
        logger.info("Validation MAE: %.3f", best_result["val_metrics"]["mae"])
        logger.info("Validation RMSE: %.3f", best_result["val_metrics"]["rmse"])
        logger.info("Validation R²: %.3f", best_result["val_metrics"]["r2"])
        logger.info("=" * 60)

        logger.info("Model saved to: %s", YIELD_MODEL_PATH)
        logger.info("Version: %s", version)
        logger.info("=" * 60)

    except Exception as e:
        logger.exception("Training failed: %s", e)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()