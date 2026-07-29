"""ML-only deadline type & document-category classification.

Uses scikit-learn TF-IDF + LogisticRegression (trained artifacts).
No regex type catalogs, no rule fusion — classification is entirely statistical.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.ml.model_registry import get

logger = logging.getLogger("ai-service.deadline_ml")

_MIN_DOC_PROBA = 0.30


def _safe_get(name: str) -> Optional[dict]:
    try:
        return get(name)
    except RuntimeError as exc:
        logger.warning("ML artifact unavailable (%s): %s", name, exc)
        return None


def predict_deadline_type(sentence: str) -> tuple[Optional[str], float, str]:
    """Return (label, probability, explanation) from the trained type classifier.

    Always returns the argmax class when the model is available (ML-only;
    no rule fallback). Low probability is still a valid soft label.
    """
    artifact = _safe_get("deadline_type_model")
    if not artifact or not sentence.strip():
        return None, 0.0, "ML type model unavailable."
    pipeline = artifact["pipeline"]
    version = artifact.get("version", "deadline-type-tfidf-lr")
    try:
        proba = pipeline.predict_proba([sentence])[0]
        classes = list(pipeline.named_steps["classifier"].classes_)
        idx = int(proba.argmax())
        label = str(classes[idx])
        confidence = float(proba[idx])
        return (
            label,
            confidence,
            f"ML type classifier ({version}, p={confidence:.2f})",
        )
    except Exception as exc:
        logger.warning("deadline type ML prediction failed: %s", exc)
        return None, 0.0, f"ML type error: {exc}"


def predict_document_category(text: str) -> tuple[Optional[str], float, str]:
    artifact = _safe_get("deadline_document_model")
    if not artifact or not text.strip():
        return None, 0.0, "ML document model unavailable."
    pipeline = artifact["pipeline"]
    version = artifact.get("version", "deadline-doc-tfidf-lr")
    try:
        snippet = text[:4000]
        proba = pipeline.predict_proba([snippet])[0]
        classes = list(pipeline.named_steps["classifier"].classes_)
        idx = int(proba.argmax())
        label = str(classes[idx])
        confidence = float(proba[idx])
        if confidence < _MIN_DOC_PROBA:
            return "General OCR Document", confidence, f"ML doc low confidence ({version})"
        return label, confidence, f"ML document classifier ({version}, p={confidence:.2f})"
    except Exception as exc:
        logger.warning("document category ML prediction failed: %s", exc)
        return "General OCR Document", 0.0, f"ML doc error: {exc}"
