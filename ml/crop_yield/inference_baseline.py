"""Inference for the regional yield baseline model.

Provides regional yield baselines that can be used as a reference
point alongside the field-level yield prediction model.

IMPORTANT: This is a regional/statistical baseline, NOT a prediction
for an individual farm.

Usage:
    python -m ml.crop_yield.inference_baseline --crop Rice --season Kharif --year 2024
"""
import os
import sys
import json
import argparse
import joblib
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

MODEL_PATH = "models/yield_baseline_model.pkl"


def load_model():
    """Load the trained baseline model."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def predict_baseline(crop, season, year, area_source_value=None):
    """Predict a regional yield baseline for a crop/season/year.

    Parameters
    ----------
    crop : str
        Crop name (e.g., 'Rice', 'Wheat')
    season : str
        Season ('Kharif', 'Rabi', 'Summer')
    year : int or str
        Year (e.g., 2024 or '2024-25')
    area_source_value : float, optional
        Source area value (used as a feature)

    Returns
    -------
    dict
        Baseline prediction with disclaimer
    """
    # Extract year if in '2024-25' format
    if isinstance(year, str) and "-" in year:
        year = int(year.split("-")[0])
    else:
        year = int(year)

    # Default area if not provided
    if area_source_value is None:
        area_source_value = 300.0  # reasonable default

    model_artifact = load_model()
    pipeline = model_artifact["pipeline"]
    metadata = model_artifact["metadata"]

    # Build input row
    input_df = pd.DataFrame([{
        "crop": crop,
        "season": season,
        "year": year,
        "area_source_value": area_source_value,
    }])

    # Predict
    prediction = pipeline.predict(input_df)[0]

    # Get feature importances if available
    feature_importance = {}
    try:
        reg = pipeline.named_steps["regressor"]
        if hasattr(reg, "feature_importances_"):
            preprocessor = pipeline.named_steps["preprocessor"]
            feature_names = []
            for name, trans, cols in preprocessor.transformers_:
                if hasattr(trans, "get_feature_names_out"):
                    feature_names.extend(trans.get_feature_names_out(cols))
                else:
                    feature_names.extend(cols)
            importances = reg.feature_importances_
            if len(importances) == len(feature_names):
                feature_importance = dict(
                    sorted(
                        zip(feature_names, importances),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5]
                )
    except Exception:
        pass

    return {
        "crop": crop,
        "season": season,
        "year": year,
        "baseline_yield_tph": round(float(prediction), 3),
        "baseline_yield_kg_ha": round(float(prediction) * 1000, 1),
        "model_version": metadata["version"],
        "metrics": metadata["metrics"],
        "disclaimer": (
            "This is a regional/statistical baseline from national "
            "crop/season-level data. It is NOT a prediction for an "
            "individual farm. Use it only as a reference point."
        ),
        "feature_importance": feature_importance,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Predict regional crop yield baseline"
    )
    parser.add_argument("--crop", required=True, help="Crop name")
    parser.add_argument("--season", required=True, help="Season (Kharif/Rabi/Summer)")
    parser.add_argument("--year", required=True, help="Year (e.g., 2024 or 2024-25)")
    parser.add_argument(
        "--area-source-value", type=float, default=None,
        help="Source area value (optional)"
    )
    args = parser.parse_args()

    result = predict_baseline(
        crop=args.crop,
        season=args.season,
        year=args.year,
        area_source_value=args.area_source_value,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()