"""ML-assisted deadline extraction from OCR / notice text."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from dateparser.search import search_dates

from app.ml.model_registry import get
from app.schemas import DeadlineExtractionResponse, DeadlineRecord, DateRangeRecord

DEADLINE_TYPES = [
    "Submission Deadline",
    "Last Date to Apply",
    "Registration Start Date",
    "Registration End Date",
    "Application Start Date",
    "Application End Date",
    "Exam Date",
    "Interview Date",
    "Document Verification Date",
    "Correction Window Start",
    "Correction Window End",
    "Fee Payment Deadline",
    "Bid Opening Date",
    "Tender Submission Deadline",
    "Event Date",
    "Meeting Date",
    "Result Date",
    "Notification Release Date",
    "Effective Date",
    "Valid From",
    "Valid Until",
    "Hearing Date",
    "Renewal Deadline",
    "Expiry Date",
    "Other Important Date",
]

_RANGE_PATTERNS = [
    re.compile(
        r"\bfrom\s+(?P<start>.+?)\s+to\s+(?P<end>.+?)(?:[.,;]|\s*$)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bbetween\s+(?P<start>.+?)\s+and\s+(?P<end>.+?)(?:[.,;]|\s*$)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bfrom\s+(?P<start>.+?)\s+till\s+(?P<end>.+?)(?:[.,;]|\s*$)",
        re.IGNORECASE,
    ),
]

_PHRASE_ANCHORS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"last\s+date\s+(?:for|to)\s+(?:submit|submission)", re.I), "Submission Deadline"),
    (re.compile(r"last\s+date\s+(?:for|to)\s+apply", re.I), "Last Date to Apply"),
    (re.compile(r"registration\s+starts?", re.I), "Registration Start Date"),
    (re.compile(r"registration\s+(?:closes|ends|close)", re.I), "Registration End Date"),
    (re.compile(r"last\s+date\s+for\s+registration", re.I), "Registration End Date"),
    (re.compile(r"applications?\s+(?:are\s+)?accepted\s+from", re.I), "Application Start Date"),
    (re.compile(r"application\s+(?:window\s+)?opens?", re.I), "Application Start Date"),
    (re.compile(r"applications?\s+close", re.I), "Application End Date"),
    (re.compile(r"application\s+deadline", re.I), "Application End Date"),
    (re.compile(r"(?:written\s+)?(?:test|exam(?:ination)?)\s+(?:on|scheduled)", re.I), "Exam Date"),
    (re.compile(r"interview\s+(?:on|will|date|scheduled)", re.I), "Interview Date"),
    (re.compile(r"document\s+verification", re.I), "Document Verification Date"),
    (re.compile(r"correction\s+window\s+opens?", re.I), "Correction Window Start"),
    (re.compile(r"correction\s+window\s+closes?", re.I), "Correction Window End"),
    (re.compile(r"fee\s+payment", re.I), "Fee Payment Deadline"),
    (re.compile(r"bid(?:s)?\s+(?:will\s+be\s+)?opened", re.I), "Bid Opening Date"),
    (re.compile(r"tender\s+(?:must\s+be\s+)?submitted", re.I), "Tender Submission Deadline"),
    (re.compile(r"(?:the\s+)?event\s+(?:will\s+be\s+)?held", re.I), "Event Date"),
    (re.compile(r"meeting\s+(?:scheduled|on)", re.I), "Meeting Date"),
    (re.compile(r"results?\s+(?:will\s+be\s+)?declared", re.I), "Result Date"),
    (re.compile(r"notification\s+released", re.I), "Notification Release Date"),
    (re.compile(r"effective\s+from", re.I), "Effective Date"),
    (re.compile(r"valid\s+from", re.I), "Valid From"),
    (re.compile(r"valid\s+(?:until|up\s+to)", re.I), "Valid Until"),
    (re.compile(r"hearing\s+(?:fixed|on)", re.I), "Hearing Date"),
    (re.compile(r"renewal", re.I), "Renewal Deadline"),
    (re.compile(r"expir(?:y|es)\s+(?:on|date)", re.I), "Expiry Date"),
]

_IGNORE_PATTERNS = [
    re.compile(r"\b(ref(?:erence)?\.?\s*(?:no|number)|file\s*no|letter\s*no|id\s*no)\b", re.I),
    re.compile(r"\b(born on|date of birth|dob)\b", re.I),
    re.compile(r"\b(phone|mobile|contact)\s*(?:no|number)?\b", re.I),
]

_RELATIVE_ONLY = re.compile(
    r"\b(within\s+\d+\s+days?|after\s+publication|from\s+the\s+date\s+of\s+publication)\b",
    re.I,
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")

_MODEL_VERSION = "deadline-tfidf-lr-v1"


def _format_dd_mm_yyyy(dt: datetime) -> str:
    return dt.strftime("%d-%m-%Y")


def _split_sentences(text: str) -> list[str]:
    chunks = _SENTENCE_SPLIT.split(text)
    return [c.strip() for c in chunks if c and len(c.strip()) > 8]


def _sentence_for_position(text: str, start_idx: int) -> tuple[str, str, str]:
    """Return (previous, current, next) sentence around a character offset."""
    sentences = _split_sentences(text)
    if not sentences:
        return "", text[:300], ""

    cursor = 0
    idx = 0
    for i, sentence in enumerate(sentences):
        pos = text.find(sentence, cursor)
        if pos == -1:
            pos = cursor
        end = pos + len(sentence)
        if start_idx <= end:
            idx = i
            break
        cursor = end

    prev_s = sentences[idx - 1] if idx > 0 else ""
    cur_s = sentences[idx]
    next_s = sentences[idx + 1] if idx + 1 < len(sentences) else ""
    return prev_s, cur_s, next_s


def _section_heading(text: str, position: int) -> Optional[str]:
    lines = text[:position].splitlines()
    for line in reversed(lines[-8:]):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.isupper() and 4 < len(stripped) < 80:
            return stripped
        if stripped.endswith(":") and len(stripped) < 80:
            return stripped.rstrip(":")
    return None


def _should_ignore_context(context: str) -> bool:
    return any(p.search(context) for p in _IGNORE_PATTERNS)


def _classify_deadline_type(context: str) -> tuple[str, str, float]:
    """Returns (deadline_type, confidence_label, probability)."""
    lowered = context.lower()
    for pattern, dtype in _PHRASE_ANCHORS:
        if pattern.search(lowered):
            return dtype, "High", 0.92

    try:
        artifact = get("deadline_type_model")
        pipeline = artifact["pipeline"]
        probs = pipeline.predict_proba([context])[0]
        classes = pipeline.named_steps["classifier"].classes_
        best_idx = int(probs.argmax())
        best_prob = float(probs[best_idx])
        label = classes[best_idx]
    except Exception:
        label = "Other Important Date"
        best_prob = 0.35

    if best_prob >= 0.70:
        confidence = "High"
    elif best_prob >= 0.45:
        confidence = "Medium"
    else:
        confidence = "Low"
        if best_prob < 0.35:
            label = "Other Important Date"

    return label, confidence, best_prob


def _parse_date_fragment(fragment: str, settings: dict) -> Optional[datetime]:
    fragment = fragment.strip(" .,;:")
    if not fragment:
        return None
    try:
        matches = search_dates(fragment, settings=settings)
    except Exception:
        matches = None
    if not matches:
        return None
    return matches[0][1]


def _extract_ranges(text: str, settings: dict) -> tuple[list[DateRangeRecord], list[tuple[int, int]]]:
    ranges: list[DateRangeRecord] = []
    spans: list[tuple[int, int]] = []
    seen: set[tuple[str, str]] = set()

    for pattern in _RANGE_PATTERNS:
        for match in pattern.finditer(text):
            start_raw = match.group("start").strip(" .,;:")
            end_raw = match.group("end").strip(" .,;:")
            start_dt = _parse_date_fragment(start_raw, settings)
            end_dt = _parse_date_fragment(end_raw, settings)
            if not start_dt or not end_dt:
                continue

            key = (_format_dd_mm_yyyy(start_dt), _format_dd_mm_yyyy(end_dt))
            if key in seen:
                continue
            seen.add(key)
            spans.append((match.start(), match.end()))

            context = match.group(0).strip()
            _, sentence, next_s = _sentence_for_position(text, match.start())
            purpose, confidence, _ = _classify_deadline_type(sentence or context)
            if "accepted from" in (sentence or "").lower():
                purpose = "Application Window"
            elif "application" in (sentence or "").lower() or "registration" in (sentence or "").lower():
                purpose = "Application Window"
            elif "correction" in (sentence or "").lower():
                purpose = "Correction Window"

            _, sentence, next_s = _sentence_for_position(text, match.start())
            ranges.append(
                DateRangeRecord(
                    startDate=_format_dd_mm_yyyy(start_dt),
                    endDate=_format_dd_mm_yyyy(end_dt),
                    startDateOriginal=start_raw,
                    endDateOriginal=end_raw,
                    purpose=purpose,
                    confidence=confidence,
                    originalSentence=sentence or context,
                    contextBefore="",
                    contextAfter=next_s,
                    sectionHeading=_section_heading(text, match.start()),
                )
            )
    return ranges, spans


def _inside_range_span(position: int, spans: list[tuple[int, int]]) -> bool:
    return any(start <= position <= end for start, end in spans)


def extract_deadlines(text: str, document_name: Optional[str] = None) -> DeadlineExtractionResponse:
    settings = {"PREFER_DATES_FROM": "future", "RELATIVE_BASE": datetime.now(), "DATE_ORDER": "DMY"}

    ranges, range_spans = _extract_ranges(text, settings)

    deadlines: list[DeadlineRecord] = []
    seen: set[tuple[str, str, str]] = set()

    sentences = _split_sentences(text)
    if not sentences:
        sentences = [text]

    for sentence in sentences:
        sentence_offset = text.find(sentence)
        if sentence_offset < 0:
            sentence_offset = 0

        if _should_ignore_context(sentence):
            continue

        try:
            matches = search_dates(sentence, settings=settings) or []
        except Exception:
            matches = []

        for original_fragment, parsed_dt in matches:
            if not isinstance(parsed_dt, datetime):
                continue

            normalized = _format_dd_mm_yyyy(parsed_dt)
            local_pos = sentence.find(original_fragment)
            if local_pos < 0:
                local_pos = 0
            pos = sentence_offset + local_pos

            if _inside_range_span(pos, range_spans):
                continue

            if re.fullmatch(r"\d{4}", original_fragment.strip()):
                continue
            if re.fullmatch(r"\d{2,4}", original_fragment.strip()) and "notice" in sentence.lower():
                continue

            prev_idx = sentences.index(sentence) if sentence in sentences else 0
            prev_s = sentences[prev_idx - 1] if prev_idx > 0 else ""
            next_s = sentences[prev_idx + 1] if prev_idx + 1 < len(sentences) else ""
            context = " ".join(p for p in [prev_s, sentence, next_s] if p).strip()

            deadline_type, confidence, prob = _classify_deadline_type(sentence)

            relative_match = _RELATIVE_ONLY.search(sentence)
            needs_ref = False
            explanation = None
            if relative_match and not re.search(r"\d{1,2}[/\-.]\d{1,2}", original_fragment):
                needs_ref = True
                explanation = (
                    f"Relative expression '{relative_match.group(0)}' requires a reference date "
                    "such as publication or notification date."
                )

            dedupe_key = (normalized, deadline_type, sentence[:60])
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            deadlines.append(
                DeadlineRecord(
                    deadlineType=deadline_type,
                    date=normalized,
                    dateOriginal=original_fragment.strip(),
                    confidence=confidence,
                    confidenceScore=round(prob, 3),
                    originalSentence=sentence,
                    contextBefore=prev_s,
                    contextAfter=next_s,
                    sectionHeading=_section_heading(text, pos),
                    pageNumber=None,
                    needsReferenceDate=needs_ref,
                    explanation=explanation,
                )
            )

    # Relative-only mentions with no parseable calendar date (deduped)
    seen_relative: set[str] = set()
    for sentence in _split_sentences(text):
        if _RELATIVE_ONLY.search(sentence) and not search_dates(sentence, settings=settings):
            if _should_ignore_context(sentence):
                continue
            key = sentence[:80]
            if key in seen_relative:
                continue
            seen_relative.add(key)
            deadlines.append(
                DeadlineRecord(
                    deadlineType="Other Important Date",
                    date=None,
                    dateOriginal=None,
                    confidence="Low",
                    confidenceScore=0.2,
                    originalSentence=sentence,
                    contextBefore="",
                    contextAfter="",
                    sectionHeading=_section_heading(text, text.find(sentence)),
                    pageNumber=None,
                    needsReferenceDate=True,
                    explanation="Relative deadline could not be converted without a reference date.",
                )
            )

    summary = (
        f"Extracted {len(deadlines)} deadline(s) and {len(ranges)} date range(s)"
        f"{f' from {document_name}' if document_name else ''}."
    )
    if not deadlines and not ranges:
        summary = (
            "No actionable deadlines were found in the document. "
            "The text may not contain dated instructions, or dates may be in an unsupported format."
        )

    return DeadlineExtractionResponse(
        deadlines=deadlines,
        dateRanges=ranges,
        summary=summary,
        totalDeadlines=len(deadlines),
        totalDateRanges=len(ranges),
        modelVersion=_MODEL_VERSION,
    )
