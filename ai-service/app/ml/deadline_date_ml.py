"""ML calendar-date span detection for deadline extraction.

No regex date-discovery patterns. A char TF-IDF + LogisticRegression model
scores token windows; accepted spans are normalized with strptime / absolute
dateparser only (relative phrases like now/tomorrow do not survive).
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Optional

import dateparser

from app.ml.date_parsing import ParsedDate, safe_date
from app.ml.model_registry import get

logger = logging.getLogger("ai-service.deadline_date_ml")

_MIN_PROBA = 0.58
_MAX_WINDOW_TOKENS = 4
_MAX_CANDIDATES = 28
_PARSE_SETTINGS = {
    "PARSERS": ["absolute-time", "custom-formats"],
    "STRICT_PARSING": False,
    "RETURN_AS_TIMEZONE_AWARE": False,
}

# Academic / fiscal year labels are not calendar dates ("2026-27", "2026-2027").
_ACADEMIC_YEAR_SPAN = re.compile(
    r"""
    ^
    (?:
        (?:ay|a\.y\.|academic\s+year|academic\s+session|session|fy|f\.y\.)
        \s+
    )?
    (?:19|20)\d{2}
    \s*[-–—/]\s*
    (?:
        (?:19|20)\d{2}
        |
        \d{2}
    )
    $
    """,
    re.IGNORECASE | re.VERBOSE,
)

_MONTH_WORDS = {
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec",
}
_MONTH_NAME_TO_NUM = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}
_LEADING_NOISE = {
    "after", "before", "from", "between", "with", "by", "on", "until", "till",
    "and", "or", "the", "a", "an", "for", "due", "dated", "date", "last",
}

_STRPTIME_FORMATS = (
    "%d %B %Y",
    "%d %b %Y",
    "%d-%b-%Y",
    "%d/%b/%Y",
    "%d.%b.%Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%B %d %Y",
    "%b %d %Y",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d.%m.%Y",
    "%m/%d/%Y",
    "%m-%d-%Y",
    "%Y-%m-%d",
    "%Y.%m.%d",
    "%Y/%m/%d",
    "%d/%m/%y",
    "%d-%m-%y",
    "%d.%m.%y",
    "%d %B",
    "%d %b",
    "%B %d",
    "%b %d",
    "%d-%B-%Y",
    "%d/%B/%Y",
)


def _safe_get(name: str) -> Optional[dict]:
    try:
        return get(name)
    except RuntimeError as exc:
        logger.warning("ML date artifact unavailable (%s): %s", name, exc)
        return None


def _tokenize(text: str) -> list[tuple[str, int, int]]:
    tokens: list[tuple[str, int, int]] = []
    i = 0
    n = len(text)
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        j = i
        while j < n and not text[j].isspace():
            j += 1
        tokens.append((text[i:j], i, j))
        i = j
    return tokens


def _has_digit(s: str) -> bool:
    return any(ch.isdigit() for ch in s)


def _looks_dateish(token: str) -> bool:
    t = token.lower().strip(".,;:()[]\"'")
    if not t:
        return False
    if _has_digit(t):
        return True
    core = t.rstrip(".")
    return core in _MONTH_WORDS


def _day_explicit_in_span(span: str, day: int) -> bool:
    token = str(day)
    i = 0
    n = len(span)
    while i < n:
        if span[i].isdigit():
            j = i
            while j < n and span[j].isdigit():
                j += 1
            if span[i:j] == token or span[i:j].lstrip("0") == token:
                return True
            i = j
        else:
            i += 1
    return False


def _year_explicit_in_span(span: str, year: int) -> bool:
    token = str(year)
    i = 0
    n = len(span)
    while i < n:
        if span[i].isdigit():
            j = i
            while j < n and span[j].isdigit():
                j += 1
            if span[i:j] == token:
                return True
            i = j
        else:
            i += 1
    return False


def _month_explicit_in_span(span: str, month: int) -> bool:
    """Require month name or month number so parsers cannot invent 'today's month'."""
    lower = span.lower()
    for name, num in _MONTH_NAME_TO_NUM.items():
        if num == month and re.search(rf"\b{re.escape(name)}\b", lower):
            return True

    token = str(month)
    padded = f"{month:02d}"
    i = 0
    n = len(span)
    while i < n:
        if span[i].isdigit():
            j = i
            while j < n and span[j].isdigit():
                j += 1
            num = span[i:j]
            if len(num) <= 2 and (num == token or num == padded or num.lstrip("0") == token):
                return True
            i = j
        else:
            i += 1
    return False


def _is_academic_year_span(span: str) -> bool:
    """True for labels like 2026-27 / 2026-2027 (not calendar dates)."""
    cleaned = re.sub(r"\s+", " ", span.strip(" .,;:()[]\"'"))
    return bool(_ACADEMIC_YEAR_SPAN.match(cleaned))


def _strip_ordinals(span: str) -> str:
    out: list[str] = []
    i = 0
    n = len(span)
    while i < n:
        if span[i].isdigit():
            j = i
            while j < n and span[j].isdigit():
                j += 1
            out.append(span[i:j])
            suf = span[j : j + 2].lower()
            if suf in {"st", "nd", "rd", "th"}:
                j += 2
            i = j
        else:
            out.append(span[i])
            i += 1
    return "".join(out)


def _leading_year(span: str) -> bool:
    i = 0
    n = len(span)
    while i < n and not span[i].isdigit():
        i += 1
    j = i
    while j < n and span[j].isdigit():
        j += 1
    return (j - i) == 4


def _clean_original(span: str) -> str:
    """Drop leading cue words / trailing separators so dateOriginal stays clean."""
    parts = span.strip().split()
    while parts:
        head = parts[0].lower().strip(".,;:()[]")
        if head in _LEADING_NOISE:
            parts = parts[1:]
            continue
        break
    while parts and parts[-1].strip(".,;:()[]") in {"-", "–", "—", "to", "until", "till", "and"}:
        parts = parts[:-1]
    cleaned = " ".join(parts).strip(" .,;:()[]\"'-–—")
    return cleaned or span.strip()


def _has_internal_range_sep(span: str) -> bool:
    """Reject windows that already contain a range connector (keep endpoints separate)."""
    padded = f" {span.strip()} "
    for sep in (" - ", " – ", " — ", " to ", " until ", " till ", " and "):
        if sep in padded:
            return True
    stripped = span.strip()
    return stripped.endswith(("-", "–", "—"))


def _leading_noise_penalty(span: str) -> int:
    parts = span.strip().split()
    if not parts:
        return 1
    head = parts[0].lower().strip(".,;:()[]")
    return 1 if head in _LEADING_NOISE else 0


def _parse_absolute(span: str) -> Optional[datetime]:
    cleaned = _strip_ordinals(span).strip()
    for fmt in _STRPTIME_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue

    base = dict(_PARSE_SETTINGS)
    # Prefer YMD when span starts with a 4-digit year; else DMY then MDY
    orders = ("YMD", "DMY", "MDY") if _leading_year(cleaned) else ("DMY", "MDY", "YMD")
    for order in orders:
        parsed = dateparser.parse(cleaned, settings={**base, "DATE_ORDER": order})
        if parsed is None:
            continue
        if _leading_year(cleaned):
            year_txt = "".join(ch for ch in cleaned if ch.isdigit())[:4]
            if str(parsed.year) != year_txt:
                continue
        return parsed
    return None


def _normalize_span(
    span: str,
    *,
    default_year: Optional[int],
) -> tuple[Optional[datetime], bool]:
    span = span.strip(" .,;:()[]\"'")
    if not span or not _has_digit(span):
        return None, False
    if _is_academic_year_span(span):
        return None, False

    parsed = _parse_absolute(span)
    needs_year = False

    if parsed is not None and parsed.year == 1900:
        if default_year is None:
            return None, False
        parsed = parsed.replace(year=default_year)
        needs_year = True
    elif parsed is None and default_year is not None:
        parsed = _parse_absolute(f"{span} {default_year}")
        needs_year = parsed is not None

    if parsed is None:
        return None, False

    if not _year_explicit_in_span(span, parsed.year):
        if default_year is None:
            return None, False
        parsed = parsed.replace(year=default_year)
        needs_year = True

    dt = safe_date(parsed.year, parsed.month, parsed.day)
    if dt is None:
        return None, False
    if dt.year < 1990 or dt.year > 2100:
        return None, False
    if not _day_explicit_in_span(span, dt.day):
        return None, False
    if not _month_explicit_in_span(span, dt.month):
        return None, False
    return dt, needs_year


def predict_is_calendar_date(text: str) -> tuple[bool, float]:
    artifact = _safe_get("deadline_date_model")
    if not artifact or not text.strip():
        return False, 0.0
    pipeline = artifact["pipeline"]
    try:
        proba = pipeline.predict_proba([text.strip()])[0]
        classes = list(pipeline.named_steps["classifier"].classes_)
        idx = classes.index("calendar_date") if "calendar_date" in classes else int(proba.argmax())
        confidence = float(proba[idx])
        label = str(classes[idx])
        return label == "calendar_date" and confidence >= _MIN_PROBA, confidence
    except Exception as exc:
        logger.warning("calendar date ML prediction failed: %s", exc)
        return False, 0.0


def find_ml_dates(
    text: str,
    *,
    default_year: Optional[int] = None,
) -> list[ParsedDate]:
    """Find calendar dates using ML window scoring + absolute normalize."""
    if not text or not text.strip():
        return []

    artifact = _safe_get("deadline_date_model")
    if not artifact:
        return []

    pipeline = artifact["pipeline"]
    tokens = _tokenize(text)
    if not tokens:
        return []

    windows: list[tuple[int, int, str]] = []
    for i in range(len(tokens)):
        # Skip windows that cannot start a date-like phrase (speed)
        if not _looks_dateish(tokens[i][0]):
            continue
        for width in range(1, _MAX_WINDOW_TOKENS + 1):
            if i + width > len(tokens):
                break
            start = tokens[i][1]
            end = tokens[i + width - 1][2]
            span = text[start:end]
            if "\n" in span:
                continue
            if not _has_digit(span) or len(span) > 36:
                continue
            if _has_internal_range_sep(span):
                continue
            if _is_academic_year_span(span.strip(" .,;:()[]\"'")):
                continue
            windows.append((start, end, span))

    if not windows:
        return []

    texts = [w[2].strip() for w in windows]
    try:
        proba = pipeline.predict_proba(texts)
        classes = list(pipeline.named_steps["classifier"].classes_)
        if "calendar_date" not in classes:
            return []
        cal_idx = list(classes).index("calendar_date")
    except Exception as exc:
        logger.warning("batch date ML failed: %s", exc)
        return []

    candidates: list[tuple[float, int, int, str]] = []
    for (start, end, span), row in zip(windows, proba):
        conf = float(row[cal_idx])
        if conf >= _MIN_PROBA:
            candidates.append((conf, start, end, span))

    candidates.sort(key=lambda c: (c[0], c[2] - c[1]), reverse=True)
    candidates = candidates[:_MAX_CANDIDATES]

    scored: list[tuple[float, int, int, int, str, datetime, bool]] = []
    for conf, start, end, span in candidates:
        cleaned = _clean_original(span)
        if _is_academic_year_span(cleaned) or _is_academic_year_span(span):
            continue
        dt, needs_year = _normalize_span(cleaned, default_year=None)
        if dt is not None:
            scored.append((conf, len(cleaned), start, end, cleaned, dt, False))
        elif default_year is not None:
            dt2, needs_year = _normalize_span(cleaned, default_year=default_year)
            if dt2 is not None:
                scored.append((conf, len(cleaned), start, end, cleaned, dt2, needs_year))
            else:
                # also try original if cleaning removed too much
                dt3, needs_year = _normalize_span(span, default_year=default_year)
                if dt3 is not None:
                    scored.append((conf, end - start, start, end, _clean_original(span), dt3, needs_year))

    # Prefer: full year present, no leading cue words, longer span, higher conf
    scored.sort(
        key=lambda c: (
            0 if not c[6] else 1,
            _leading_noise_penalty(c[4]),
            -c[1],
            -c[0],
        )
    )
    occupied: list[tuple[int, int]] = []
    found: list[ParsedDate] = []

    def overlaps(a: int, b: int) -> bool:
        return any(not (b <= s or a >= e) for s, e in occupied)

    resolved_year = default_year
    for conf, _length, start, end, span, dt, needs_year in scored:
        if overlaps(start, end):
            continue
        occupied.append((start, end))
        found.append(
            ParsedDate(
                dt=dt,
                original=span.strip(),
                start=start,
                end=end,
                needs_year=needs_year,
            )
        )
        if resolved_year is None:
            resolved_year = dt.year

    if resolved_year is not None:
        for conf, start, end, span in candidates:
            if overlaps(start, end):
                continue
            cleaned = _clean_original(span)
            dt, needs_year = _normalize_span(cleaned, default_year=resolved_year)
            if dt is None or not needs_year:
                continue
            occupied.append((start, end))
            found.append(
                ParsedDate(
                    dt=dt,
                    original=cleaned.strip(),
                    start=start,
                    end=end,
                    needs_year=True,
                )
            )

    found.sort(key=lambda item: item.start)
    return found
