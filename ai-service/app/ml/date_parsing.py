"""Calendar-date helpers for deadline extraction.

Date *finding* is ML-based (`deadline_date_ml.find_ml_dates`).
This module keeps OCR cleanup, formatting, and safe datetime construction.
"""

from __future__ import annotations

import calendar
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

_MONTH_NAMES = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)
_MONTH_ABBR = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Sept", "Oct", "Nov", "Dec",
)
_MONTHS = "|".join(_MONTH_NAMES + _MONTH_ABBR)

# Light OCR cleanup only (not date-type rules)
_OCR_MONTH_FIXES = [
    (re.compile(r"Augu5t", re.I), "August"),
    (re.compile(r"Augu5", re.I), "Aug"),
    (re.compile(r"Septembcr", re.I), "September"),
    (re.compile(r"0ctober", re.I), "October"),
    (re.compile(r"0ct(?=[^a-z]|$)", re.I), "Oct"),
    (re.compile(r"Februaxy", re.I), "February"),
    (re.compile(r"Juiy", re.I), "July"),
    (re.compile(r"Jui(?=[^a-z]|$)", re.I), "Jul"),
    (re.compile(r"Januaxy", re.I), "January"),
]


@dataclass(frozen=True)
class ParsedDate:
    dt: datetime
    original: str
    start: int
    end: int
    needs_year: bool = False


_LABELED_ITEM_LINE = re.compile(
    r"^[A-Z][\w\s/&()'.,\-]{0,90}:\s+\S",
)
_BULLET_OR_ENUM = re.compile(r"^(?:[-•*]|\d+[.)])\s+\S")
_DATE_ONLY_CONTINUATION = re.compile(
    r"^\d{1,2}(?:st|nd|rd|th)?(?:\s+|[\-/.])"
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
    r"Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"(?:\s+\d{2,4})?\s*[.]?\s*$"
    r"|^\d{1,2}[/\-.]\d{1,2}(?:[/\-.]\d{2,4})?\s*[.]?\s*$"
    r"|^\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2}\s*[.]?\s*$",
    re.I,
)


def join_soft_wrapped_lines(text: str) -> str:
    """Join mid-sentence OCR/PDF wraps without merging the next item/paragraph.

    Only continues a line when the next line is clearly a wrap remnant:
    lowercase start, or a date-only leftover line. Never glues a new
    capitalized sentence/item onto the previous line.
    """
    if not text:
        return ""
    merged: list[str] = []
    for raw in text.split("\n"):
        stripped = raw.strip()
        if not stripped:
            merged.append("")
            continue
        prev = merged[-1].strip() if merged else ""
        can_continue = bool(prev) and not re.search(r"[.!?]$", prev)
        is_wrap_remnant = stripped[:1].islower() or bool(
            _DATE_ONLY_CONTINUATION.match(stripped)
        )
        starts_new_block = bool(
            _BULLET_OR_ENUM.match(stripped) or _LABELED_ITEM_LINE.match(stripped)
        )
        if can_continue and is_wrap_remnant and not starts_new_block:
            merged[-1] = prev + " " + stripped
        else:
            merged.append(stripped)
    out: list[str] = []
    for line in merged:
        if line == "" and out and out[-1] == "":
            continue
        out.append(line)
    return "\n".join(out)


def clean_ocr_text(text: str) -> str:
    if not text:
        return ""
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = cleaned.replace("\u00a0", " ").replace("\t", " ")
    for pattern, replacement in _OCR_MONTH_FIXES:
        cleaned = pattern.sub(replacement, cleaned)

    # Space jammed month tokens so the ML windower sees readable spans
    cleaned = re.sub(
        rf"(?<=\d)(?P<month>{_MONTHS})(?=\d|,|-|/)",
        lambda m: f" {m.group('month')} ",
        cleaned,
        flags=re.I,
    )
    cleaned = re.sub(
        rf"(?<=\d)(?P<month>{_MONTHS})\b",
        lambda m: f" {m.group('month')}",
        cleaned,
        flags=re.I,
    )
    cleaned = re.sub(
        rf"\b(?P<month>{_MONTHS})(?=\d)",
        lambda m: f"{m.group('month')} ",
        cleaned,
        flags=re.I,
    )
    cleaned = re.sub(
        rf"(\d{{1,2}}(?:st|nd|rd|th)?)\s*({_MONTHS})\s*[,/\-]\s*(\d{{4}})\b",
        r"\1 \2 \3",
        cleaned,
        flags=re.I,
    )
    cleaned = re.sub(
        rf"\b({_MONTHS})\s+(\d{{1,2}}(?:st|nd|rd|th)?)\s*[,/\-]\s*(\d{{4}})\b",
        r"\1 \2, \3",
        cleaned,
        flags=re.I,
    )
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = join_soft_wrapped_lines(cleaned)
    return cleaned.strip()


def _expand_year(year: int) -> Optional[int]:
    if 1900 <= year <= 2100:
        return year
    if 0 <= year <= 99:
        return 2000 + year
    return None


def safe_date(year: int, month: int, day: int) -> Optional[datetime]:
    year = _expand_year(year) if year < 100 else year
    if year is None or year < 1900 or year > 2100:
        return None
    if not (1 <= month <= 12):
        return None
    try:
        max_day = calendar.monthrange(year, month)[1]
        if not (1 <= day <= max_day):
            return None
        return datetime(year, month, day)
    except Exception:
        return None


def format_dd_mm_yyyy(dt: datetime) -> str:
    return dt.strftime("%d-%m-%Y")


def format_iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def format_long(dt: datetime) -> str:
    return f"{dt.day} {dt.strftime('%B')} {dt.year}"


def find_explicit_dates(
    text: str,
    *,
    default_year: Optional[int] = None,
) -> list[ParsedDate]:
    """ML calendar-date finder (no regex date patterns)."""
    from app.ml.deadline_date_ml import find_ml_dates

    return find_ml_dates(text or "", default_year=default_year)


def parse_date_fragment(fragment: str, default_year: Optional[int] = None) -> Optional[datetime]:
    fragment = (fragment or "").strip(" .,;:()[]")
    if not fragment or len(fragment) < 3:
        return None
    hits = find_explicit_dates(fragment, default_year=default_year)
    if not hits:
        return None
    return max(hits, key=lambda h: h.end - h.start).dt


def detect_document_year(text: str) -> Optional[int]:
    """Year from the earliest full ML-detected calendar date near the top."""
    head = (text or "")[:500]
    for hit in find_explicit_dates(head, default_year=None):
        return hit.dt.year
    return None
