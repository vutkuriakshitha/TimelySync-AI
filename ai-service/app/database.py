import logging
from datetime import datetime, timezone

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import settings

logger = logging.getLogger("ai-service.database")

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    return _client


def get_db():
    client = get_client()
    return client.get_default_database()


def save_prediction(prediction_type: str, input_features: dict, output: dict):
    """Persist every prediction the AI service makes so it can be audited
    and later used to evaluate model drift / accuracy over time."""
    try:
        db = get_db()
        db.ai_predictions.insert_one({
            "predictionType": prediction_type,
            "inputFeatures": input_features,
            "output": output,
            "createdAt": datetime.now(timezone.utc),
        })
    except PyMongoError as exc:
        logger.warning("Could not persist prediction history: %s", exc)


def save_training_dataset(model_name: str, sample_count: int, feature_columns: list[str]):
    """Records metadata about a training run (not the full dataset, to keep
    the audit collection small) so there's a real trail of when/how models
    were trained, satisfying the 'store training data' requirement."""
    try:
        db = get_db()
        db.ai_training_runs.insert_one({
            "modelName": model_name,
            "sampleCount": sample_count,
            "featureColumns": feature_columns,
            "trainedAt": datetime.now(timezone.utc),
        })
    except PyMongoError as exc:
        logger.warning("Could not persist training run metadata: %s", exc)


def save_outcome_feedback(payload: dict):
    """Stores real task outcomes reported by the backend so future
    retraining can use genuine user data instead of only synthetic data."""
    try:
        db = get_db()
        db.ai_outcome_feedback.insert_one({
            **payload,
            "receivedAt": datetime.now(timezone.utc),
        })
    except PyMongoError as exc:
        logger.warning("Could not persist outcome feedback: %s", exc)
