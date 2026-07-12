import os

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

from app.config import settings

NUMERIC_FEATURES = ["hoursUntilDue", "userCompletionRate", "userOnTimeRate", "riskScoreAtCreation"]
CATEGORICAL_FEATURES = ["priority", "category", "impact", "effort"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ],
        remainder="passthrough",
    )


def save_artifact(name: str, artifact: dict):
    os.makedirs(settings.models_dir, exist_ok=True)
    path = os.path.join(settings.models_dir, f"{name}.joblib")
    joblib.dump(artifact, path)
    return path


def load_artifact(name: str) -> dict:
    path = os.path.join(settings.models_dir, f"{name}.joblib")
    return joblib.load(path)
