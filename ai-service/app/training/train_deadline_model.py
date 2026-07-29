import json
import logging
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.database import save_training_dataset
from app.training.common import save_artifact
from app.training.data_generator import (
    generate_deadline_document_samples,
    generate_deadline_samples,
)
from app.training.date_data_generator import generate_calendar_date_samples

logger = logging.getLogger("ai-service.train.deadline")

TYPE_MODEL_VERSION = "deadline-type-tfidf-lr-v10"
DOC_MODEL_VERSION = "deadline-doc-tfidf-lr-v10"
DATE_MODEL_VERSION = "deadline-date-tfidf-lr-v3"
EVAL_REPORT_PATH = Path(__file__).resolve().parents[2] / "models" / "deadline_ml_evaluation_report.json"


def _train_text_classifier(texts, labels, *, ngram=(1, 3), max_features=15000, C=2.5):
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    pipeline = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(ngram_range=ngram, min_df=2, max_features=max_features),
            ),
            (
                "classifier",
                LogisticRegression(max_iter=2500, C=C, class_weight="balanced"),
            ),
        ]
    )
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    label_list = sorted(set(labels))
    acc = accuracy_score(y_test, y_pred)
    p_w, r_w, f1_w, _ = precision_recall_fscore_support(
        y_test, y_pred, average="weighted", zero_division=0
    )
    p_m, r_m, f1_m, _ = precision_recall_fscore_support(
        y_test, y_pred, average="macro", zero_division=0
    )
    p, r, f1, support = precision_recall_fscore_support(
        y_test, y_pred, labels=label_list, zero_division=0
    )
    cm = confusion_matrix(y_test, y_pred, labels=label_list)
    metrics = {
        "accuracy": float(acc),
        "precision_weighted": float(p_w),
        "recall_weighted": float(r_w),
        "f1_weighted": float(f1_w),
        "precision_macro": float(p_m),
        "recall_macro": float(r_m),
        "f1_macro": float(f1_m),
        "holdout": 0.2,
        "n_test": int(len(y_test)),
        "labels": label_list,
        "per_class": [
            {
                "label": label_list[i],
                "precision": float(p[i]),
                "recall": float(r[i]),
                "f1": float(f1[i]),
                "support": int(support[i]),
            }
            for i in range(len(label_list))
        ],
        "confusion_matrix": cm.tolist(),
        "classification_report": classification_report(
            y_test, y_pred, labels=label_list, zero_division=0
        ),
    }
    return pipeline, metrics


def train():
    type_df = generate_deadline_samples(n=12000)
    type_pipeline, type_metrics = _train_text_classifier(
        type_df["text"], type_df["deadlineType"]
    )
    logger.info(
        "Deadline type model accuracy=%.3f f1_w=%.3f samples=%d",
        type_metrics["accuracy"],
        type_metrics["f1_weighted"],
        len(type_df),
    )

    save_artifact(
        "deadline_type_model",
        {
            "pipeline": type_pipeline,
            "version": TYPE_MODEL_VERSION,
            "classes": list(type_pipeline.named_steps["classifier"].classes_),
            "metrics": {
                "accuracy": type_metrics["accuracy"],
                "f1_weighted": type_metrics["f1_weighted"],
                "f1_macro": type_metrics["f1_macro"],
            },
            "approach": "tfidf_logistic_regression",
        },
    )
    save_training_dataset(TYPE_MODEL_VERSION, len(type_df), ["text", "deadlineType"])

    doc_df = generate_deadline_document_samples(n=6000)
    doc_pipeline, doc_metrics = _train_text_classifier(
        doc_df["text"], doc_df["documentType"], ngram=(1, 2), max_features=10000, C=3.0
    )
    logger.info(
        "Deadline document model accuracy=%.3f f1_w=%.3f samples=%d",
        doc_metrics["accuracy"],
        doc_metrics["f1_weighted"],
        len(doc_df),
    )

    save_artifact(
        "deadline_document_model",
        {
            "pipeline": doc_pipeline,
            "version": DOC_MODEL_VERSION,
            "classes": list(doc_pipeline.named_steps["classifier"].classes_),
            "metrics": {
                "accuracy": doc_metrics["accuracy"],
                "f1_weighted": doc_metrics["f1_weighted"],
                "f1_macro": doc_metrics["f1_macro"],
            },
            "approach": "tfidf_logistic_regression",
        },
    )
    save_training_dataset(DOC_MODEL_VERSION, len(doc_df), ["text", "documentType"])

    date_df = generate_calendar_date_samples(n=12000)
    date_pipeline = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(2, 5),
                    min_df=2,
                    max_features=25000,
                ),
            ),
            (
                "classifier",
                LogisticRegression(max_iter=2500, C=2.0, class_weight="balanced"),
            ),
        ]
    )
    Xtr, Xte, ytr, yte = train_test_split(
        date_df["text"], date_df["label"], test_size=0.2, random_state=42, stratify=date_df["label"]
    )
    date_pipeline.fit(Xtr, ytr)
    ypred = date_pipeline.predict(Xte)
    d_acc = float(accuracy_score(yte, ypred))
    d_pw, d_rw, d_f1w, _ = precision_recall_fscore_support(
        yte, ypred, average="weighted", zero_division=0
    )
    logger.info(
        "Deadline date model accuracy=%.3f f1_w=%.3f samples=%d",
        d_acc,
        d_f1w,
        len(date_df),
    )
    save_artifact(
        "deadline_date_model",
        {
            "pipeline": date_pipeline,
            "version": DATE_MODEL_VERSION,
            "classes": list(date_pipeline.named_steps["classifier"].classes_),
            "metrics": {
                "accuracy": d_acc,
                "f1_weighted": float(d_f1w),
                "precision_weighted": float(d_pw),
                "recall_weighted": float(d_rw),
            },
            "approach": "char_wb_tfidf_logistic_regression",
        },
    )
    save_training_dataset(DATE_MODEL_VERSION, len(date_df), ["text", "label"])

    type_counts = type_df["deadlineType"].value_counts().to_dict()
    doc_counts = doc_df["documentType"].value_counts().to_dict()
    confused = []
    labels = type_metrics["labels"]
    cm = type_metrics["confusion_matrix"]
    for i, a in enumerate(labels):
        for j, b in enumerate(labels):
            if i != j and cm[i][j] > 0:
                confused.append({"count": int(cm[i][j]), "true": a, "pred": b})
    confused.sort(key=lambda x: x["count"], reverse=True)

    report = {
        "type": {
            "version": TYPE_MODEL_VERSION,
            "n_samples": int(len(type_df)),
            "n_classes": len(type_counts),
            "samples_per_class": {k: int(v) for k, v in sorted(type_counts.items())},
            **{k: v for k, v in type_metrics.items() if k != "classification_report"},
            "confusion_top": confused[:20],
        },
        "document": {
            "version": DOC_MODEL_VERSION,
            "n_samples": int(len(doc_df)),
            "n_classes": len(doc_counts),
            "samples_per_class": {k: int(v) for k, v in sorted(doc_counts.items())},
            **{k: v for k, v in doc_metrics.items() if k != "classification_report"},
        },
        "date": {
            "version": DATE_MODEL_VERSION,
            "n_samples": int(len(date_df)),
            "n_classes": 2,
            "accuracy": d_acc,
            "f1_weighted": float(d_f1w),
            "precision_weighted": float(d_pw),
            "recall_weighted": float(d_rw),
            "formats_trained": "25+ strftime / ordinal / partial / OCR variants",
        },
        "architecture": {
            "classification": "TF-IDF (1-3 grams) + LogisticRegression",
            "date_extraction": (
                "ML calendar-date span classifier (char_wb TF-IDF + LR) "
                "+ dateparser absolute-time normalization only"
            ),
            "why_ml_dates": (
                "Learns many calendar formats from data; rejects relative words "
                "because they are labeled not_date and absolute-time parse fails."
            ),
            "retrain": "python -m app.training.train_deadline_model",
        },
    }
    EVAL_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVAL_REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info("Wrote evaluation report to %s", EVAL_REPORT_PATH)

    return {
        "type_accuracy": type_metrics["accuracy"],
        "type_f1_weighted": type_metrics["f1_weighted"],
        "document_accuracy": doc_metrics["accuracy"],
        "document_f1_weighted": doc_metrics["f1_weighted"],
        "date_accuracy": d_acc,
        "date_f1_weighted": float(d_f1w),
        "type_samples": len(type_df),
        "document_samples": len(doc_df),
        "date_samples": len(date_df),
        "type_version": TYPE_MODEL_VERSION,
        "document_version": DOC_MODEL_VERSION,
        "date_version": DATE_MODEL_VERSION,
        "evaluation_report": str(EVAL_REPORT_PATH),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(train())
