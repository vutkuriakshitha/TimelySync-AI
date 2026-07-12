import pandas as pd

from app.ml.model_registry import get
from app.schemas import CauseOut, PostAnalysisRequest, PostAnalysisResponse

_CAUSE_DESCRIPTIONS = {
    "TIME_MANAGEMENT": "Time was likely underestimated relative to other commitments during this period.",
    "UNDERESTIMATED_EFFORT": "This task likely required more effort than initially planned for.",
    "PRIORITY_CONFLICT": "Other higher-urgency tasks may have competed for your attention.",
    "EXTERNAL_BLOCKER": "External factors outside your direct control may have caused the delay.",
    "PROCRASTINATION": "The task may have been repeatedly deprioritized until close to the deadline.",
}

_RECOMMENDATIONS = {
    "TIME_MANAGEMENT": "Try blocking dedicated time on your calendar for similar tasks well before the deadline.",
    "UNDERESTIMATED_EFFORT": "For similar tasks, pad your time estimate by 30-50% based on this experience.",
    "PRIORITY_CONFLICT": "Consider using the impact/effort fields to triage which task to tackle first next time.",
    "EXTERNAL_BLOCKER": "Where possible, start tasks earlier to leave a buffer for factors outside your control.",
    "PROCRASTINATION": "Break similar tasks into smaller subtasks with their own earlier due dates.",
}

_ON_TIME_RECOMMENDATION = "Great job staying on schedule - keep using whatever approach worked here!"


def _feature_row(features: PostAnalysisRequest) -> pd.DataFrame:
    return pd.DataFrame([{
        "hoursUntilDue": features.hoursUntilDue,
        "userCompletionRate": features.userCompletionRate,
        "userOnTimeRate": features.userOnTimeRate,
        "riskScoreAtCreation": features.riskScoreAtCreation,
        "daysLate": features.daysLate,
        "priority": features.priority,
        "category": features.category,
        "impact": features.impact,
        "effort": features.effort,
    }])


def predict(features: PostAnalysisRequest) -> PostAnalysisResponse:
    artifact = get("postanalysis_model")

    if features.completedOnTime:
        return PostAnalysisResponse(causes=[], recommendation=_ON_TIME_RECOMMENDATION, modelVersion=artifact["version"])

    pipeline = artifact["pipeline"]
    classes = artifact["classes"]
    row = _feature_row(features)

    proba = pipeline.predict_proba(row)[0]
    ranked = sorted(zip(classes, proba), key=lambda x: x[1], reverse=True)
    top = [c for c in ranked if c[1] > 0.08][:3] or ranked[:1]

    total = sum(p for _, p in top) or 1.0
    causes = [
        CauseOut(type=cause_type, percentage=int(round(p / total * 100)), description=_CAUSE_DESCRIPTIONS[cause_type])
        for cause_type, p in top
    ]

    top_cause_type = top[0][0]
    recommendation = _RECOMMENDATIONS[top_cause_type]

    return PostAnalysisResponse(causes=causes, recommendation=recommendation, modelVersion=artifact["version"])
