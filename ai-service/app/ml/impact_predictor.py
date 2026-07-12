import pandas as pd

from app.ml.model_registry import get
from app.schemas import ConsequenceOut, ImpactPredictionResponse, TaskFeatures

_CONSEQUENCE_TEMPLATES = {
    "ACADEMIC": {
        "CRITICAL": "Risk of failing the course or losing significant grade credit",
        "HIGH": "Grade penalty and need to negotiate an extension with faculty",
        "MEDIUM": "Minor grade deduction for late submission",
        "LOW": "Negligible academic impact if submitted shortly after",
    },
    "OPPORTUNITY": {
        "CRITICAL": "Opportunity may be lost entirely (application window closes)",
        "HIGH": "Significantly reduced chance of selection or approval",
        "MEDIUM": "May need to follow up and explain the delay to the other party",
        "LOW": "Small chance of a slightly weaker impression",
    },
    "PERSONAL_GOAL": {
        "CRITICAL": "Meaningful setback to a personal habit or long-term goal streak",
        "HIGH": "Noticeable disruption to your personal routine and motivation",
        "MEDIUM": "Minor dip in personal progress that is easy to recover from",
        "LOW": "Almost no lasting impact on your personal goals",
    },
    "EVENT": {
        "CRITICAL": "Missing the event entirely or causing major logistics issues for others",
        "HIGH": "Scrambling to catch up on event preparation at the last minute",
        "MEDIUM": "Some avoidable stress coordinating event details late",
        "LOW": "Barely noticeable effect on the event outcome",
    },
}

_SECONDARY_CONSEQUENCE = "Increased stress and reduced time buffer for upcoming tasks"


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


def predict(features: TaskFeatures) -> ImpactPredictionResponse:
    artifact = get("impact_model")
    pipeline = artifact["pipeline"]
    classes = artifact["classes"]
    row = _feature_row(features)

    proba = pipeline.predict_proba(row)[0]
    ranked = sorted(zip(classes, proba), key=lambda x: x[1], reverse=True)
    top_severity, top_prob = ranked[0]

    templates = _CONSEQUENCE_TEMPLATES.get(features.category, _CONSEQUENCE_TEMPLATES["PERSONAL_GOAL"])
    consequences = [
        ConsequenceOut(description=templates.get(top_severity, templates["MEDIUM"]), probabilityPercent=int(round(top_prob * 100))),
    ]
    if len(ranked) > 1:
        second_severity, second_prob = ranked[1]
        consequences.append(ConsequenceOut(
            description=templates.get(second_severity, _SECONDARY_CONSEQUENCE),
            probabilityPercent=int(round(second_prob * 100)),
        ))

    return ImpactPredictionResponse(
        severityLevel=top_severity,
        consequences=consequences,
        modelVersion=artifact["version"],
    )
