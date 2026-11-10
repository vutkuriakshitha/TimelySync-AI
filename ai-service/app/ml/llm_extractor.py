"""LLM-based deadline extraction with deterministic grounding checks.

Why this exists
---------------
The classic pipeline (TF-IDF + logistic regression over a fixed label set) can
only recognise notice types it was trained on. A language model reads the
document the way a person does, so it generalises to formats nobody anticipated.

LLMs can also hallucinate, so nothing the model returns is trusted blindly.
Every item must pass *document-agnostic* checks (no per-circular rules):

1. Evidence must be a real quote: the sentence the model cites has to appear
   in the source text (whitespace/case-insensitive).
2. The date must be a valid calendar date, and its day and month must be
   visible in that evidence or in the surrounding text.
3. Duplicates (same date + same purpose) are merged.
4. Items that fail a check are dropped (hard) or flagged for review (soft).
5. Tasks are only suggested for actionable items whose date is not in the past.

The LLM provider is pluggable (Gemini native API or any OpenAI-compatible API,
which covers Groq, OpenRouter, OpenAI, ...) and uses only the standard library.
If the LLM is disabled, unreachable, rate limited, or returns nothing usable,
callers fall back to the classic pipeline (see ``extraction_service``).
"""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Callable, Optional

from app.schemas import (
    DateRangeRecord,
    DeadlineExtractionResponse,
    DeadlineRecord,
    SuggestedTask,
)

logger = logging.getLogger(__name__)

# Keep a single request well inside free-tier token limits.
MAX_CHARS = int(os.getenv("LLM_MAX_INPUT_CHARS", "24000"))

KINDS = ("deadline", "event", "document_date", "info")
CATEGORIES = ("ACADEMIC", "OPPORTUNITY", "EVENT", "PERSONAL_GOAL")
PRIORITIES = ("HIGH", "MEDIUM", "LOW")

SYSTEM_PROMPT = """You extract dates from any kind of notice, circular, email or letter and
understand what each date MEANS from its sentence. The document can be from any
school, company, government body or organisation, in any layout.

Return ONLY a JSON object: {"documentType": string, "summary": string, "items": [...]}

Each item describes one date (or one date range) that appears in the document:
{
  "purpose": short human label for what the date is for, e.g. "Registration deadline",
             "Workshop", "Fee payment (late fee applies)", "Results announced".
  "kind": one of
      "deadline"      - something must be done by this date (submit, register, pay, reply)
      "event"         - something happens on this date (workshop, exam, interview, meeting)
      "document_date" - the date the document was issued/dated/effective from
      "info"          - any other date that needs no action (holiday, results announcement,
                        a past occurrence, a registration window that already closed)
  "date": "YYYY-MM-DD"        the date, or the START of a range
  "endDate": "YYYY-MM-DD" or null   end of a range, if the document gives one
  "evidence": the exact sentence or line copied VERBATIM from the document that states this date
  "category": one of ACADEMIC, OPPORTUNITY, EVENT, PERSONAL_GOAL
  "priority": HIGH, MEDIUM or LOW (HIGH for fines, penalties, final or last-chance dates)
  "taskTitle": imperative task title for a person who received this notice, or null if no
               action is needed (e.g. "Register for the AI and Cloud Computing Workshop")
  "relatedEvent": name of the event/process this date belongs to, or null
  "confidence": number 0 to 1 for how sure you are of the date AND its meaning
  "fineAmount": text of any fine/late fee/penalty attached to this date, or null
}

Rules:
- Use only dates that are written in the document. Never invent or guess a date and never
  use today's date. If a date has no year, infer the year only from the document's own
  context (e.g. the issue date); if you cannot, lower the confidence.
- Do not turn every date into a task. Issue dates, holidays and announcements are not tasks.
- "Register before 17 November" for a workshop on "20 November" gives TWO items: a deadline
  (17 Nov) and an event (20 Nov), both with the same relatedEvent.
- Skip reference numbers, phone numbers, amounts and times that are not calendar dates.
- Copy evidence exactly. If you cannot quote a sentence for a date, leave the item out.
- If the document has no usable dates, return an empty items list.
"""


# --------------------------------------------------------------------------- #
# Configuration and providers
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class LlmConfig:
    provider: str = ""          # "gemini" or "openai" (any OpenAI-compatible API)
    api_key: str = ""
    model: str = ""
    base_url: str = ""          # openai-compatible only, e.g. https://api.groq.com/openai/v1
    timeout_s: float = 45.0

    @property
    def enabled(self) -> bool:
        return bool(self.provider and self.api_key and self.model)


def load_config() -> LlmConfig:
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()
    if provider in ("groq", "openrouter", "openai-compatible"):
        provider = "openai"
    defaults = {
        "gemini": ("gemini-3.8-flash", ""),
        "openai": ("", "https://api.groq.com/openai/v1"),
    }
    default_model, default_url = defaults.get(provider, ("", ""))
    return LlmConfig(
        provider=provider,
        api_key=os.getenv("LLM_API_KEY", "").strip(),
        model=os.getenv("LLM_MODEL", default_model).strip(),
        base_url=os.getenv("LLM_BASE_URL", default_url).strip().rstrip("/"),
        timeout_s=float(os.getenv("LLM_TIMEOUT_S", "45")),
    )


class LlmError(RuntimeError):
    """Raised when the provider call fails (network, quota, bad response)."""


def _post_json(url: str, payload: dict, headers: dict, timeout_s: float) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise LlmError(f"LLM HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise LlmError(f"LLM request failed: {exc}") from exc


def _call_gemini(cfg: LlmConfig, user_text: str) -> str:
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{cfg.model}:generateContent"
    )
    body = _post_json(
        url,
        {
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": user_text}]}],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
            },
        },
        {"x-goog-api-key": cfg.api_key},
        cfg.timeout_s,
    )
    try:
        return body["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LlmError(f"Unexpected Gemini response shape: {str(body)[:200]}") from exc


def _call_openai_compatible(cfg: LlmConfig, user_text: str) -> str:
    body = _post_json(
        f"{cfg.base_url}/chat/completions",
        {
            "model": cfg.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
        },
        {"Authorization": f"Bearer {cfg.api_key}"},
        cfg.timeout_s,
    )
    try:
        return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LlmError(f"Unexpected response shape: {str(body)[:200]}") from exc


def default_llm_call(cfg: LlmConfig, user_text: str) -> str:
    if cfg.provider == "gemini":
        return _call_gemini(cfg, user_text)
    if cfg.provider == "openai":
        return _call_openai_compatible(cfg, user_text)
    raise LlmError(f"Unknown LLM_PROVIDER '{cfg.provider}' (use 'gemini' or 'openai'/'groq')")


# --------------------------------------------------------------------------- #
# Parsing and grounding checks (document-agnostic)
# --------------------------------------------------------------------------- #
_MONTHS = (
    ("january", "jan"), ("february", "feb"), ("march", "mar"), ("april", "apr"),
    ("may", "may"), ("june", "jun"), ("july", "jul"), ("august", "aug"),
    ("september", "sep"), ("october", "oct"), ("november", "nov"), ("december", "dec"),
)
_MONTH_FULL = ("January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December")


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _parse_json_object(raw: str) -> dict:
    raw = (raw or "").strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.IGNORECASE)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            raise LlmError("LLM did not return JSON") from None
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise LlmError("LLM returned malformed JSON") from exc
    if not isinstance(data, dict):
        raise LlmError("LLM JSON was not an object")
    return data


def _parse_iso(value: Any) -> Optional[date]:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None
    return parsed if 2000 <= parsed.year <= 2100 else None


def _evidence_in_source(evidence: str, source_norm: str) -> bool:
    ev = _norm(evidence)
    if len(ev) < 8:
        return False
    if ev in source_norm:
        return True
    # OCR line-wrapping can split a sentence; accept if its first and last
    # ~25 characters both appear in order.
    head, tail = ev[:25], ev[-25:]
    i = source_norm.find(head)
    return i != -1 and source_norm.find(tail, i) != -1


def _date_visible_in(d: date, text_norm: str) -> bool:
    """The day number and the month (name, abbreviation or number) appear in the text."""
    full, abbr = _MONTHS[d.month - 1]
    day_pat = rf"(?<!\d){d.day}(?:st|nd|rd|th)?(?!\d)|(?<!\d){d.day:02d}(?!\d)"
    if not re.search(day_pat, text_norm):
        return False
    if re.search(rf"\b{full}\b|\b{abbr}\b", text_norm):
        return True
    numeric_month = rf"(?<!\d)(?:{d.month}|{d.month:02d})(?!\d)"
    return bool(re.search(numeric_month, text_norm))


def _fmt_dmy(d: date) -> str:
    return d.strftime("%d-%m-%Y")


def _fmt_long(d: date) -> str:
    return f"{d.day} {_MONTH_FULL[d.month - 1]} {d.year}"


def _confidence_label(score: float) -> str:
    return "High" if score >= 0.8 else "Medium" if score >= 0.5 else "Low"


def _context(source: str, evidence: str, side: str, width: int = 140) -> str:
    idx = source.lower().find(evidence.lower()[:40])
    if idx < 0:
        return ""
    if side == "before":
        return source[max(0, idx - width):idx].strip()
    end = idx + len(evidence)
    return source[end:end + width].strip()


def _clean_str(value: Any, limit: int = 300) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text[:limit] if text and text.lower() not in ("null", "none", "n/a") else None


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def extract_with_llm(
    text: str,
    document_name: Optional[str] = None,
    *,
    config: Optional[LlmConfig] = None,
    llm_call: Optional[Callable[[LlmConfig, str], str]] = None,
    today: Optional[date] = None,
) -> DeadlineExtractionResponse:
    """Extract deadlines with an LLM and validate every item against the text.

    Raises ``LlmError`` when the LLM is not configured or the call fails, so the
    caller can fall back to the classic pipeline.
    """
    cfg = config or load_config()
    if not cfg.enabled:
        raise LlmError("LLM extraction is not configured")
    today = today or date.today()

    source = (text or "").strip()
    if not source:
        raise LlmError("Empty document text")
    truncated = len(source) > MAX_CHARS
    prompt_text = source[:MAX_CHARS]

    raw = (llm_call or default_llm_call)(cfg, prompt_text)
    data = _parse_json_object(raw)
    items = data.get("items")
    if not isinstance(items, list):
        raise LlmError("LLM JSON had no 'items' list")

    source_norm = _norm(prompt_text)
    deadlines: list[DeadlineRecord] = []
    ranges: list[DateRangeRecord] = []
    seen: set[tuple[str, str]] = set()
    dropped = 0

    for item in items:
        if not isinstance(item, dict):
            dropped += 1
            continue
        start = _parse_iso(item.get("date"))
        evidence = _clean_str(item.get("evidence"), 600) or ""
        purpose = _clean_str(item.get("purpose"), 120)
        # Hard checks: real date, real quote, date actually written in the document.
        if (
            start is None
            or not purpose
            or not _evidence_in_source(evidence, source_norm)
            or not _date_visible_in(start, _norm(evidence) + " " + source_norm)
        ):
            dropped += 1
            logger.info("LLM item dropped (ungrounded): %s", str(item)[:160])
            continue

        kind = item.get("kind") if item.get("kind") in KINDS else "info"
        try:
            score = max(0.0, min(1.0, float(item.get("confidence", 0.6))))
        except (TypeError, ValueError):
            score = 0.6
        # Soft check: the date should appear in the cited sentence itself.
        in_evidence = _date_visible_in(start, _norm(evidence))
        if not in_evidence:
            score = min(score, 0.45)

        end = _parse_iso(item.get("endDate"))
        if end is not None and end < start:
            end = None

        key = (start.isoformat(), _norm(purpose))
        if key in seen:
            continue
        seen.add(key)

        category = item.get("category") if item.get("category") in CATEGORIES else "ACADEMIC"
        priority = item.get("priority") if item.get("priority") in PRIORITIES else "MEDIUM"
        title = _clean_str(item.get("taskTitle"), 140)
        is_past = start < today and (end is None or end < today)
        actionable = kind in ("deadline", "event") and bool(title) and not is_past
        fine = _clean_str(item.get("fineAmount"), 120)
        related = _clean_str(item.get("relatedEvent"), 140)
        dtype = "Document Date" if kind == "document_date" else purpose

        explanation = None
        if is_past and kind in ("deadline", "event"):
            explanation = "This date is already in the past, so no task was suggested."
        elif not in_evidence:
            explanation = "The date is not in the quoted sentence. Please verify it."

        deadlines.append(
            DeadlineRecord(
                deadlineType=dtype,
                date=_fmt_dmy(start),
                dateIso=start.isoformat(),
                dateOriginal=_fmt_dmy(start),
                purpose=purpose,
                priority=priority,
                confidence=_confidence_label(score),
                confidenceScore=round(score, 2),
                originalSentence=evidence,
                contextBefore=_context(prompt_text, evidence, "before"),
                contextAfter=_context(prompt_text, evidence, "after"),
                explanation=explanation,
                relatedEvent=related,
                fineAmount=fine,
                description=evidence,
                taskTitle=title if actionable else None,
                suggestedCategory=category,
                suggestedDueDate=start.isoformat() if actionable else None,
                isActionable=actionable,
            )
        )

        if end is not None and end != start:
            ranges.append(
                DateRangeRecord(
                    startDate=_fmt_dmy(start),
                    endDate=_fmt_dmy(end),
                    startDateIso=start.isoformat(),
                    endDateIso=end.isoformat(),
                    startDateOriginal=_fmt_dmy(start),
                    endDateOriginal=_fmt_dmy(end),
                    purpose=purpose,
                    confidence=_confidence_label(score),
                    originalSentence=evidence,
                    contextBefore=_context(prompt_text, evidence, "before"),
                    contextAfter=_context(prompt_text, evidence, "after"),
                    fineAmount=fine,
                )
            )

    tasks = [
        SuggestedTask(
            title=d.taskTitle or d.deadlineType,
            category=d.suggestedCategory or "ACADEMIC",
            priority=d.priority or "MEDIUM",
            dueDate=d.suggestedDueDate or "",
            dueDateDisplay=_fmt_long(date.fromisoformat(d.suggestedDueDate)),
            description=d.description or d.originalSentence,
            sourceDeadlineType=d.deadlineType,
            relatedEvent=d.relatedEvent,
            fineAmount=d.fineAmount,
        )
        for d in deadlines
        if d.isActionable and d.suggestedDueDate and d.taskTitle
    ]

    doc_type = _clean_str(data.get("documentType"), 80)
    summary = _clean_str(data.get("summary"), 400) or (
        f"Found {len(deadlines)} date(s)"
        f"{f' in {document_name}' if document_name else ''}."
    )
    notes = []
    if dropped:
        notes.append(f"{dropped} unverifiable item(s) ignored")
    if truncated:
        notes.append(f"only the first {MAX_CHARS} characters were analysed")
    if notes:
        summary = f"{summary} ({'; '.join(notes)}.)"

    return DeadlineExtractionResponse(
        deadlines=deadlines,
        dateRanges=ranges,
        suggestedTasks=tasks,
        relationships=[],
        summary=summary,
        totalDeadlines=len(deadlines),
        totalDateRanges=len(ranges),
        modelVersion=f"llm-{cfg.provider}-{cfg.model}+grounding-v1",
        documentType=doc_type,
        extractionMethod=None,
    )
