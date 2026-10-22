"""Shared model management for ML pipelines.

Handles model version tracking, artifact saving/loading, and metadata registry.
Ensures all models are saved with proper provenance.
"""
import os
import json
import joblib
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.models import ModelRegistry

logger = logging.getLogger(__name__)


def save_model_to_file(
    pipeline,
    filepath: str,
    version: str,
    metrics: Dict[str, Any],
    dataset_version: str,
    train_rows: int,
    validation_rows: int,
    validation_score: str = "OK",
) -> None:
    """Save a trained model pipeline to disk with metadata.

    Parameters
    ----------
    pipeline : object
        Scikit-learn pipeline or compatible object
    filepath : str
        Path to save the model file
    version : str
        Model version identifier
    metrics : dict
        Evaluation metrics (MAE, RMSE, R², etc.)
    dataset_version : str
        Identifier for the dataset used for training
    train_rows : int
        Number of training samples used
    validation_rows : int
        Number of validation samples used
    validation_score : str
        Validation status description (e.g., "OK", "LOW_DATA", "UNSTABLE")
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    artifact = {
        "pipeline": pipeline,
        "metadata": {
            "version": version,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "dataset_version": dataset_version,
            "train_samples": train_rows,
            "validation_samples": validation_rows,
            "validation_score": validation_score,
        },
    }

    joblib.dump(artifact, filepath)
    logger.info("Model saved to %s (v%s)", filepath, version)


def load_model_from_file(
    filepath: str,
) -> tuple[Any, Dict[str, Any]]:
    """Load a saved model pipeline from disk.

    Returns
    -------
    tuple[pipeline, metadata]
        The pipeline and its metadata dict
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Model artifact not found: {filepath}")

    artifact = joblib.load(filepath)
    metadata = artifact["metadata"]
    logger.info(
        "Model loaded from %s (v%s) trained on %s samples",
        filepath,
        metadata["version"],
        metadata["train_samples"],
    )
    return artifact["pipeline"], metadata


def register_model(
    session: Session,
    model_name: str,
    version: str,
    artifact_path: str,
    metrics_json: Dict[str, Any],
    dataset_version: str,
    trained_at: datetime = None,
) -> ModelRegistry:
    """Register a model in the database.

    Returns
    -------
    ModelRegistry
        The created model registry entry
    """
    existing = (
        session.query(ModelRegistry)
        .filter_by(model_name=model_name, version=version)
        .first()
    )
    if existing:
        logger.warning("Model registry entry already exists for %s:%s", model_name, version)
        return existing

    model = ModelRegistry(
        model_name=model_name,
        version=version,
        artifact_path=artifact_path,
        metrics_json=json.dumps(metrics_json, default=str),
        trained_at=trained_at or datetime.utcnow(),
        dataset_version=dataset_version,
    )
    session.add(model)
    session.commit()
    logger.info("Model registered: %s:%s", model_name, version)
    return model


def get_latest_model(
    session: Session,
    model_name: str,
    version: str = None,
) -> Optional[ModelRegistry]:
    """Get the latest version of a model (or specific version)."""
    query = session.query(ModelRegistry).filter_by(model_name=model_name)
    if version:
        query = query.filter_by(version=version)
    else:
        query = query.order_by(ModelRegistry.trained_at.desc())
    return query.first()


def predict_with_model(
    pipeline,
    features: Dict[str, Any],
) -> Dict[str, Any]:
    """Make prediction with a trained pipeline.

    The pipeline must have a predict_single method that accepts a
    dictionary of features.

    Returns
    -------
    dict
        Prediction result with metadata
    """
    # Convert features to format expected by pipeline
    # This is pipeline-specific — different models may expect different formats
    # For scikit-learn pipelines with feature names, we might need to
    # construct a pandas DataFrame with a single row

    import pandas as pd

    features_df = pd.DataFrame([features])
    prediction = pipeline.predict(features_df)[0]

    # Most pipelines also have predict_proba or predict_* methods for intervals
    # Extract prediction intervals or uncertainty estimates

    result = {
        "prediction": float(prediction),
        "timestamp": datetime.utcnow().isoformat(),
    }
    return result