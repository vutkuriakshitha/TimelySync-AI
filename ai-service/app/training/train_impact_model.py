import logging

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.database import save_training_dataset
from app.training.common import FEATURE_COLUMNS, build_preprocessor, save_artifact
from app.training.data_generator import generate_task_samples

logger = logging.getLogger("ai-service.train.impact")

MODEL_VERSION = "impact-rf-v1"


def train():
    df = generate_task_samples(n=6000)
    X = df[FEATURE_COLUMNS]
    y = df["severity"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    pipeline = Pipeline(steps=[
        ("preprocess", build_preprocessor()),
        ("classifier", RandomForestClassifier(n_estimators=160, max_depth=9, min_samples_leaf=4, random_state=42)),
    ])
    pipeline.fit(X_train, y_train)

    preds = pipeline.predict(X_test)
    acc = accuracy_score(y_test, preds)
    logger.info("Impact severity model trained - accuracy=%.3f", acc)

    save_artifact("impact_model", {
        "pipeline": pipeline,
        "version": MODEL_VERSION,
        "feature_columns": FEATURE_COLUMNS,
        "classes": list(pipeline.named_steps["classifier"].classes_),
        "metrics": {"accuracy": acc},
    })
    save_training_dataset(MODEL_VERSION, len(df), FEATURE_COLUMNS)
    return {"accuracy": acc, "samples": len(df)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(train())
