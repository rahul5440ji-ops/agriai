import joblib
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from backend.ml.inference import YieldModelService


def test_predict_imputes_missing_numeric_features_from_training_mean(tmp_path):
    features = pd.DataFrame({"organic_carbon": [0.5, 1.0, 1.5, 2.0]})
    pipeline = Pipeline([
        ("preprocessor", ColumnTransformer([
            ("numeric", StandardScaler(), ["organic_carbon"]),
        ])),
        ("regressor", Ridge()),
    ])
    pipeline.fit(features, [1.0, 2.0, 3.0, 4.0])

    artifact_path = tmp_path / "yield_model.pkl"
    joblib.dump({
        "pipeline": pipeline,
        "metadata": {"version": "test", "metrics": {}},
    }, artifact_path)
    service = YieldModelService(str(artifact_path))

    result = service.predict({"organic_carbon": None})

    assert result["predicted_yield_tph"] == pytest.approx(2.5)
