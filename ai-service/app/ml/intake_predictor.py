from datetime import datetime, timedelta

from dateparser.search import search_dates

from app.ml.model_registry import get
from app.schemas import IntakeResponse


def _extract_due_date(text: str) -> str | None:
    """Uses dateparser's NLP-based date/time-expression search to find any
    natural-language date embedded within the free text (e.g. 'next
    Friday', 'in 3 days', 'before tomorrow', 'on August 15th') rather than
    simple keyword if/else matching."""
    settings = {"PREFER_DATES_FROM": "future", "RELATIVE_BASE": datetime.now()}
    try:
        matches = search_dates(text, settings=settings)
    except Exception:
        matches = None
    if not matches:
        return None
    _, parsed = matches[0]
    if parsed <= datetime.now():
        parsed = parsed + timedelta(days=1)
    return parsed.isoformat()


def _clean_title(text: str) -> str:
    title = text.strip()
    return title if len(title) <= 60 else title[:57] + "..."


def predict(text: str) -> IntakeResponse:
    category_artifact = get("intake_category_model")
    priority_artifact = get("intake_priority_model")

    category = category_artifact["pipeline"].predict([text])[0]
    priority = priority_artifact["pipeline"].predict([text])[0]

    due_date = _extract_due_date(text)

    return IntakeResponse(
        title=_clean_title(text),
        description=text.strip(),
        category=category,
        priority=priority,
        dueDate=due_date,
        modelVersion=f"{category_artifact['version']}",
    )
