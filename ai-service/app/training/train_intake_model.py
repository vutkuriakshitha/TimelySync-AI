import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.database import save_training_dataset
from app.training.common import save_artifact
from app.training.data_generator import generate_intake_samples

logger = logging.getLogger("ai-service.train.intake")

MODEL_VERSION = "intake-tfidf-lr-v1"


def _train_text_classifier(texts, labels):
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42, stratify=labels)
    pipeline = Pipeline(steps=[
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=5000)),
        ("classifier", LogisticRegression(max_iter=1000, C=3.0)),
    ])
    pipeline.fit(X_train, y_train)
    acc = accuracy_score(y_test, pipeline.predict(X_test))
    return pipeline, acc


def train():
    df = generate_intake_samples(n=4000)

    category_pipeline, category_acc = _train_text_classifier(df["text"], df["category"])
    priority_pipeline, priority_acc = _train_text_classifier(df["text"], df["priority"])

    logger.info("Intake category model accuracy=%.3f, priority model accuracy=%.3f", category_acc, priority_acc)

    save_artifact("intake_category_model", {
        "pipeline": category_pipeline,
        "version": MODEL_VERSION,
        "classes": list(category_pipeline.named_steps["classifier"].classes_),
        "metrics": {"accuracy": category_acc},
    })
    save_artifact("intake_priority_model", {
        "pipeline": priority_pipeline,
        "version": MODEL_VERSION,
        "classes": list(priority_pipeline.named_steps["classifier"].classes_),
        "metrics": {"accuracy": priority_acc},
    })
    save_training_dataset(MODEL_VERSION, len(df), ["text"])
    return {"category_accuracy": category_acc, "priority_accuracy": priority_acc, "samples": len(df)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(train())
