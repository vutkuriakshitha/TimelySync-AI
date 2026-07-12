import numpy as np
import pandas as pd

from app.ml.model_registry import get
from app.schemas import FailurePredictionResponse, TaskFeatures


def _feature_row(features: TaskFeatures) -> pd.DataFrame:
    return pd.DataFrame([{
        "hoursUntilDue": features.hoursUntilDue,
        "userCompletionRate": features.userCompletionRate,
        "userOnTimeRate": features.userOnTimeRate,
        "riskScoreAtCreation": features.riskScoreAtCreation,
        "priority": features.priority,
        "category": features.category,
        "impact": features.impact,
        "effort": features.effort,
    }])


def _risk_level(probability: int) -> str:
    if probability >= 70:
        return "CRITICAL"
    if probability >= 40:
        return "WARNING"
    return "SAFE"


def _describe_top_factors(pipeline, row: pd.DataFrame, top_n: int = 3) -> list[str]:
    classifier = pipeline.named_steps["classifier"]
    preprocess = pipeline.named_steps["preprocess"]
    feature_names = preprocess.get_feature_names_out()
    importances = classifier.feature_importances_

    transformed = preprocess.transform(row)
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()
    active_values = transformed[0]

    contribution = importances * np.abs(active_values)
    top_idx = np.argsort(contribution)[::-1][:top_n]

    descriptions = []
    for idx in top_idx:
        if contribution[idx] <= 0:
            continue
        name = feature_names[idx]
        descriptions.append(_humanize_feature(name, row))
    return descriptions or ["No single dominant risk factor - overall pattern-based risk"]


def _humanize_feature(name: str, row: pd.DataFrame) -> str:
    if "hoursUntilDue" in name:
        hours = row["hoursUntilDue"].iloc[0]
        if hours < 24:
            return "Deadline is less than 24 hours away"
        if hours < 72:
            return "Deadline is within the next 3 days"
        return "Deadline timing is a contributing factor"
    if "userCompletionRate" in name:
        return f"Historical task completion rate is {row['userCompletionRate'].iloc[0] * 100:.0f}%"
    if "userOnTimeRate" in name:
        return f"Historical on-time rate is {row['userOnTimeRate'].iloc[0] * 100:.0f}%"
    if "priority_HIGH" in name:
        return "This is a high priority task"
    if "effort_HIGH" in name:
        return "This task requires high effort"
    if "riskScoreAtCreation" in name:
        return "Similar tasks have historically carried elevated risk"
    return name.replace("cat__", "").replace("remainder__", "").replace("_", " ").title() + " is a contributing factor"


def predict(features: TaskFeatures) -> FailurePredictionResponse:
    artifact = get("failure_model")
    pipeline = artifact["pipeline"]
    row = _feature_row(features)

    probability = float(pipeline.predict_proba(row)[0][1]) * 100
    probability_int = int(round(probability))
    risk_level = _risk_level(probability_int)
    factors = _describe_top_factors(pipeline, row)

    return FailurePredictionResponse(
        probability=probability_int,
        riskLevel=risk_level,
        riskFactors=factors,
        modelVersion=artifact["version"],
    )
