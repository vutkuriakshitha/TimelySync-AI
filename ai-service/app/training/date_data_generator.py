"""Synthetic training data for ML calendar-date span detection.

Positive = explicit calendar dates in many formats.
Negative = relative words, prose, OCR noise that is NOT a calendar date.
No handcrafted extraction rules — the classifier learns the distinction.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Iterable

import pandas as pd

# Wide format coverage for generation (strftime templates).
_FORMATS = [
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
    "%d%b%Y",
    "%d %B, %Y",
    "%d %b, %Y",
    "%d-%B-%Y",
    "%d/%B/%Y",
]

_ORDINAL_FORMATS = [
    ("{day}{suf} {month} {year}", True),
    ("{day}{suf} {month_abbr} {year}", True),
    ("{day}{suf} {month}, {year}", True),
]

_PARTIAL_FORMATS = [
    "%d %B",
    "%d %b",
    "%B %d",
    "%b %d",
    "%d-%b",
    "%d/%b",
]

_OCR_VARIANTS = [
    lambda s: s.replace("August", "Augu5t").replace("Aug", "Augu5"),
    lambda s: s.replace(" ", ""),
    lambda s: s.replace(", ", ","),
    lambda s: s.replace(" ", "").replace("August", "August"),
]


def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return suf


def _iter_sample_dates(rng: random.Random, n: int) -> Iterable[datetime]:
    base = datetime(2024, 1, 1)
    for _ in range(n):
        yield base + timedelta(days=rng.randint(0, 365 * 4))


_NEGATIVE_PHRASES = [
    "now",
    "to",
    "are",
    "so",
    "any",
    "tomorrow",
    "yesterday",
    "today",
    "next week",
    "last month",
    "in 3 days",
    "within a week",
    "as soon as possible",
    "immediately",
    "soon",
    "later",
    "end of the month",
    "mid September",
    "beginning of next year",
    "portal is now open",
    "students are advised",
    "under any circumstances",
    "clear any dues",
    "update details so that",
    "REF ANU EXAM 2026",
    "Controller of Examinations",
    "odd semester registration",
    "please submit the form",
    "all students must complete",
    "Rs 2000 late fee",
    "not eligible",
    "Hall Ticket",
    "examination circular",
    "Monday",
    "Tuesday morning",
    "Q1 2026",
    "FY 2025-26",
    "2026-27",
    "2025-26",
    "AY 2026-27",
    "academic year 2026-27",
    "academic session 2026-2027",
    "session 2026-27",
    "version 2.0",
    "page 15",
    "room 204",
    "batch 2026",
    "CS101",
    "15 marks",
    "2000 rupees",
    "section 15",
    "clause 8",
]


def generate_calendar_date_samples(n: int = 12000, seed: int = 23) -> pd.DataFrame:
    """Balanced-ish binary dataset: calendar_date vs not_date."""
    rng = random.Random(seed)
    rows: list[dict] = []
    target_pos = n // 2
    target_neg = n - target_pos

    dates = list(_iter_sample_dates(rng, target_pos + 200))
    i = 0
    while len([r for r in rows if r["label"] == "calendar_date"]) < target_pos and i < len(dates) * 3:
        dt = dates[i % len(dates)]
        i += 1
        mode = rng.random()
        if mode < 0.72:
            fmt = rng.choice(_FORMATS)
            try:
                text = dt.strftime(fmt)
            except ValueError:
                continue
        elif mode < 0.88:
            suf = _ordinal(dt.day)
            tmpl, _ = rng.choice(_ORDINAL_FORMATS)
            text = tmpl.format(
                day=dt.day,
                suf=suf,
                month=dt.strftime("%B"),
                month_abbr=dt.strftime("%b"),
                year=dt.year,
            )
        else:
            fmt = rng.choice(_PARTIAL_FORMATS)
            text = dt.strftime(fmt)

        if rng.random() < 0.12:
            text = rng.choice(_OCR_VARIANTS)(text)
        if rng.random() < 0.08:
            text = f" {text} "
        rows.append({"text": text.strip(), "label": "calendar_date"})

    while len([r for r in rows if r["label"] == "not_date"]) < target_neg:
        if rng.random() < 0.55:
            text = rng.choice(_NEGATIVE_PHRASES)
        elif rng.random() < 0.75:
            text = " ".join(
                rng.choice(
                    [
                        "students",
                        "must",
                        "submit",
                        "registration",
                        "before",
                        "deadline",
                        "fee",
                        "exam",
                        "notice",
                        "circular",
                        "official",
                        "portal",
                        "open",
                        "complete",
                        "form",
                        "details",
                    ]
                )
                for _ in range(rng.randint(2, 6))
            )
        else:
            # Numeric noise that is not a calendar date
            text = rng.choice(
                [
                    str(rng.randint(1, 99)),
                    f"Rs {rng.randint(100, 9000)}",
                    f"page {rng.randint(1, 40)}",
                    f"room {rng.randint(100, 400)}",
                    f"{rng.randint(2020, 2030)}",
                    f"v{rng.randint(1, 9)}.{rng.randint(0, 9)}",
                    f"{rng.randint(2020, 2030)}-{str(rng.randint(0, 99)).zfill(2)}",
                    f"AY {rng.randint(2020, 2030)}-{str(rng.randint(0, 99)).zfill(2)}",
                ]
            )
        rows.append({"text": text, "label": "not_date"})

    rng.shuffle(rows)
    return pd.DataFrame(rows[:n])
