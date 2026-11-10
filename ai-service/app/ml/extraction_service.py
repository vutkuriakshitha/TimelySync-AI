"""Single entry point for deadline extraction.

Strategy (graceful degradation, so a demo never shows an error page):

1. If an LLM is configured, ask it and validate the answer (llm_extractor).
2. If the LLM is off, rate limited, unreachable, or nothing survives validation,
   fall back to the classic TF-IDF + logistic regression pipeline.

The response says which engine produced it (``modelVersion``).
"""

from __future__ import annotations

import logging
from typing import Optional

from app.ml import deadline_extractor, llm_extractor
from app.schemas import DeadlineExtractionResponse

logger = logging.getLogger(__name__)


def extract(text: str, document_name: Optional[str] = None) -> DeadlineExtractionResponse:
    cfg = llm_extractor.load_config()
    if not cfg.enabled:
        logger.info("Deadline extraction engine: classic (LLM not configured: set LLM_PROVIDER, LLM_API_KEY, LLM_MODEL)")
    if cfg.enabled:
        try:
            result = llm_extractor.extract_with_llm(text, document_name, config=cfg)
            if result.totalDeadlines > 0:
                logger.info("Deadline extraction engine: LLM (%s, %s)", cfg.provider, cfg.model)
                return result
            logger.info("LLM returned no verified dates; using classic pipeline")
        except llm_extractor.LlmError as exc:
            logger.warning("LLM extraction failed, using classic pipeline: %s", exc)
        except Exception:  # never let a provider glitch break the upload flow
            logger.exception("Unexpected LLM extraction error, using classic pipeline")
    return deadline_extractor.extract_deadlines(text, document_name)
