import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.database import save_training_dataset
from app.training.common import save_artifact
from app.training.data_generator import generate_deadline_samples

logger = logging.getLogger("ai-service.train.deadline")

MODEL_VERSION = "deadline-tfidf-lr-v1"


def train():
    df = generate_deadline_samples(n=7500)
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["deadlineType"], test_size=0.2, random_state=42, stratify=df["deadlineType"]
    )

    pipeline = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 3), min_df=2, max_features=12000)),
            ("classifier", LogisticRegression(max_iter=2000, C=2.5, class_weight="balanced")),
        ]
    )
    pipeline.fit(X_train, y_train)
    acc = accuracy_score(y_test, pipeline.predict(X_test))
    logger.info("Deadline type model accuracy=%.3f", acc)

    save_artifact(
        "deadline_type_model",
        {
            "pipeline": pipeline,
            "version": MODEL_VERSION,
            "classes": list(pipeline.named_steps["classifier"].classes_),
            "metrics": {"accuracy": acc},
        },
    )
    save_training_dataset(MODEL_VERSION, len(df), ["text", "deadlineType"])
    return {"accuracy": acc, "samples": len(df)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(train())
