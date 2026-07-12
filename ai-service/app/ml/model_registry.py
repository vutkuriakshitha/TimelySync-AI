"""Lazily loads joblib model artifacts and keeps them cached in memory.
Call `reload()` after retraining to pick up new artifacts without restarting
the process."""

import logging
import threading

from app.training.common import load_artifact

logger = logging.getLogger("ai-service.model_registry")

_lock = threading.Lock()
_cache: dict[str, dict] = {}

_MODEL_NAMES = [
    "failure_model",
    "impact_model",
    "postanalysis_model",
    "intake_category_model",
    "intake_priority_model",
    "deadline_type_model",
]


def get(name: str) -> dict:
    if name not in _cache:
        with _lock:
            if name not in _cache:
                try:
                    _cache[name] = load_artifact(name)
                except FileNotFoundError as exc:
                    raise RuntimeError(
                        f"Model artifact '{name}' not found. Run `python -m app.training.train_all` first."
                    ) from exc
    return _cache[name]


def reload():
    with _lock:
        _cache.clear()
        for name in _MODEL_NAMES:
            try:
                _cache[name] = load_artifact(name)
            except FileNotFoundError:
                logger.warning("Model artifact '%s' missing during reload", name)
    return list(_cache.keys())


def is_ready() -> bool:
    try:
        for name in _MODEL_NAMES:
            get(name)
        return True
    except RuntimeError:
        return False
