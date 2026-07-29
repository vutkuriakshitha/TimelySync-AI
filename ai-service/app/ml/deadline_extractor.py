"""Production deadline extraction from OCR / official notice text.

Extracts every real calendar date with evidence, classifies purpose, preserves
fee/process relationships, and generates one task per actionable deadline.

Classification is ML-only (TF-IDF + LogisticRegression).
Calendar date spans are parsed structurally (no relative/fuzzy invention).
Never uses system/upload date as a deadline.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Optional

from app.ml.date_parsing import (
    clean_ocr_text,
    detect_document_year,
    find_explicit_dates,
    format_dd_mm_yyyy,
    format_iso,
    format_long,
)
from app.ml.deadline_catalog import META_TYPES, TASK_TITLES
from app.ml.deadline_ml import predict_deadline_type, predict_document_category
from app.schemas import (
    DateRangeRecord,
    DeadlineExtractionResponse,
    DeadlineRecord,
    DeadlineRelationship,
    SuggestedTask,
)

_MODEL_VERSION = "deadline-ml-v10"

# Re-export for callers / tests
__all__ = ["clean_ocr_text", "extract_deadlines"]

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")

_REF_NUMBER = re.compile(r"\b[A-Z]{2,}/[A-Z0-9/_\-]{3,}\b")

_IGNORE_LINE = re.compile(
    r"\b("
    r"ref(?:erence)?\.?\s*(?:no|number)?|file\s*no|letter\s*no|circular\s*no|"
    r"id\s*no|phone|mobile|contact|pin\s*code|sector\s*\d+|born\s+on|dob|"
    r"date\s+of\s+birth|gstin|pan\s*(?:no|number)?|aadhaar"
    r")\b",
    re.IGNORECASE,
)

_MONEY = re.compile(
    r"(?:₹|Rs\.?|INR|USD|\$)\s*([\d,]+(?:\.\d{1,2})?)"
    r"|([\d,]+(?:\.\d{1,2})?)\s*(?:rupees?|rs\.?)",
    re.IGNORECASE,
)

_ZERO_FINE = re.compile(
    r"(?:^|[^\d])(?:₹|Rs\.?|INR)?\s*0(?:\.0+)?\s*(?:fine|fee|penalty)?(?:$|[^\d])|"
    r"(?:no|nil|zero)\s+(?:fine|late\s+fee|penalty)|"
    r"without\s+late\s+fee|"
    r"no\s+late\s+fee",
    re.IGNORECASE,
)


def _extract_money(text: str) -> Optional[str]:
    match = _MONEY.search(text)
    if match:
        amount = match.group(1) or match.group(2)
        if amount:
            normalized = amount.replace(",", "")
            try:
                if float(normalized) == 0:
                    return "₹0"
            except ValueError:
                pass
            prefix = "₹"
            if re.search(r"\$|USD", match.group(0), re.I):
                prefix = "$"
            return f"{prefix}{normalized}"
    if _ZERO_FINE.search(text):
        return "₹0"
    return None

_RANGE_PATTERNS = []  # ranges are built from ML dates + separator gaps (see _extract_ranges)


_RANGE_GAP_TOKENS = {
    "-", "–", "—", "to", "until", "till", "and",
}


def _is_range_gap(gap: str) -> bool:
    """True if text between two ML dates is only a range connector."""
    raw = (gap or "").strip().lower()
    if not raw:
        return False
    # collapse whitespace
    parts = [p for p in raw.replace("\n", " ").split(" ") if p]
    if not parts:
        return False
    if len(parts) == 1 and parts[0] in _RANGE_GAP_TOKENS:
        return True
    if len(parts) <= 3 and all(p in _RANGE_GAP_TOKENS or p in {"from", "between"} for p in parts):
        return True
    # allow " - " style already covered; reject long prose gaps
    if len(raw) <= 12 and any(tok in raw for tok in ("-", "–", "—", " to ", " until ", " till ", " and ")):
        # ensure no extra letters beyond connectors
        cleaned = raw
        for tok in ("between", "from", "until", "till", "and", "to"):
            cleaned = cleaned.replace(tok, " ")
        for ch in ("-", "–", "—"):
            cleaned = cleaned.replace(ch, " ")
        return not any(c.isalpha() for c in cleaned)
    return False


def _range_purpose_from_ml(sentence: str) -> str:
    label, _score, _expl = predict_deadline_type(sentence or "date range")
    if not label:
        return "Date Range"
    mapping = {
        "Correction Deadline": "Correction Window",
        "Registration Deadline": "Registration Window",
        "Registration Opens": "Registration Window",
        "Registration Ends": "Registration Window",
        "Application Deadline": "Application Window",
        "Application Starts": "Application Window",
        "Exam Date": "Exam Schedule Window",
        "Exam Schedule": "Exam Schedule Window",
        "Late Fee Deadline": "Late Fee Window",
        "Final Late Fee Deadline": "Late Fee Window",
    }
    return mapping.get(label, "Date Range")



def _split_sentences(text: str) -> list[str]:
    return [c.strip() for c in _SENTENCE_SPLIT.split(text) if c and c.strip()]

def _sentence_covering(text: str, start: int, end: int) -> tuple[str, str, str]:
    sentences = _split_sentences(text)
    if not sentences:
        return "", text[max(0, start - 60) : end + 60], ""
    cursor = 0
    for i, sentence in enumerate(sentences):
        pos = text.find(sentence, cursor)
        if pos < 0:
            pos = cursor
        sentence_end = pos + len(sentence)
        # Strict containment — do not steal the next line via off-by-one.
        if start >= pos and start < sentence_end:
            prev_s = sentences[i - 1] if i > 0 else ""
            next_s = sentences[i + 1] if i + 1 < len(sentences) else ""
            return prev_s, sentence, next_s
        cursor = max(sentence_end, pos + 1)
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end < 0:
        line_end = len(text)
    return "", text[line_start:line_end].strip(), ""

def _local_context(text: str, start: int, end: int, window: int = 120) -> str:
    return text[max(0, start - window) : min(len(text), end + window)]


_DATE_ONLY_LINE = re.compile(
    r"^\s*\d{1,2}(?:st|nd|rd|th)?(?:\s+|[\-/.])"
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
    r"Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"(?:\s+\d{2,4})?\s*$"
    r"|^\s*\d{1,2}[/\-.]\d{1,2}(?:[/\-.]\d{2,4})?\s*$"
    r"|^\s*\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2}\s*$",
    re.I,
)


def _classify_type(
    sentence: str,
    local: str = "",
    prev_s: str = "",
    is_doc: bool = False,
) -> tuple[Optional[str], float, str]:
    """ML-only deadline/event type classification (no regex type rules)."""
    sent = (sentence or "").strip()
    # Date-only remnants still borrow the previous line (late-fee tables, wrapped dates).
    date_only = bool(_DATE_ONLY_LINE.match(sent.rstrip(" .;:,")))
    if prev_s and sent and date_only:
        blob = f"{prev_s.strip()}\n{sent}".strip()
    else:
        blob = sent or (local or "").strip()
    if not blob:
        return None, 0.0, "Empty sentence."

    primary = predict_deadline_type(blob)
    loc = (local or "").strip()
    # Prefer a wider local window when the sentence alone is low-confidence.
    if loc and loc != blob and (date_only or (primary[1] is not None and primary[1] < 0.35)):
        alt = predict_deadline_type(loc)
        if alt[0] and (primary[0] is None or (alt[1] or 0) > (primary[1] or 0)):
            return alt
    return primary


def _detect_document_type(text: str) -> str:
    """ML-only document category (no keyword rule catalog)."""
    label, _prob, _expl = predict_document_category(text)
    return label or "General OCR Document"


def _category_for(dtype: str) -> str:
    t = dtype.lower()
    if any(
        k in t
        for k in (
            "exam", "quiz", "lab", "viva", "registration", "assignment", "project",
            "fee", "admit", "hall ticket", "result", "hostel", "library", "orientation",
            "academic", "admission", "correction", "submission", "document", "verification",
            "late fee", "final", "payment", "timetable", "course",
        )
    ):
        return "ACADEMIC"
    if any(
        k in t
        for k in (
            "scholarship", "placement", "internship", "application", "tender", "interview",
            "job", "campus hiring", "emd", "hackathon", "competition",
        )
    ):
        return "OPPORTUNITY"
    if any(
        k in t
        for k in (
            "workshop", "conference", "seminar", "event", "holiday", "counselling",
            "club", "sports", "cultural", "meeting", "training",
        )
    ):
        return "EVENT"
    if "policy" in t:
        return "PERSONAL_GOAL"
    return "PERSONAL_GOAL"


def _priority_for(
    dtype: str,
    dt: datetime,
    *,
    fine: Optional[str],
    sentence: str,
    document_year: Optional[int],
) -> str:
    score = 0
    t = dtype.lower()
    if fine and fine not in {"₹0", "$0"}:
        score += 2
    if any(k in t for k in ("final", "closed", "exam", "viva", "eligibility", "late fee", "quiz", "lab")):
        score += 2
    if re.search(r"\b(?:not\s+eligible|not\s+allowed|admit\s+card|preventing)\b", sentence, re.I):
        score += 2
    if any(k in t for k in ("registration", "submission", "fee", "payment", "application", "admission", "tender")):
        score += 1
    if any(k in t for k in ("document date", "issue date", "circular date", "notification date", "policy effective", "holiday")):
        return "LOW"
    if score >= 3:
        return "HIGH"
    if score >= 1:
        return "MEDIUM"
    return "MEDIUM"


def _task_title(dtype: str, fine: Optional[str], sentence: str, full_text: str) -> Optional[str]:
    """Build a short action title from the ML type (+ light evidence cues)."""
    t = dtype.lower()
    sent = (sentence or "").lower()
    if dtype in META_TYPES or "document date" in t or "issue date" in t:
        if dtype == "Holiday":
            return None
        if dtype in META_TYPES and "policy review" not in t:
            return None
    if "policy review" in t:
        return "Review Company Policy"
    if "registration closed" in t:
        return "Registration Closed — No Further Action"
    if (
        "fee payment" in t
        or "payment deadline" in t
        or (("fee" in sent or "tuition" in sent) and ("payment" in sent or "pay" in sent))
    ):
        return "Pay Fee"
    if "final" in t and "late" in t:
        return "Final Opportunity for Registration"
    if "late fee" in t and fine and fine != "₹0":
        return f"Complete Registration with {fine} Late Fee"
    if "course registration deadline" in t:
        return "Complete Course Registration"
    if "course registration opens" in t:
        return "Start Course Registration"
    if "registration deadline" in t or "registration ends" in t:
        if "odd semester" in full_text.lower():
            return "Complete Odd Semester Examination Registration"
        if "examination registration" in full_text.lower() or "exam registration" in full_text.lower():
            return "Complete Examination Registration"
        if "semester" in full_text.lower():
            return "Complete Semester Registration"
        return "Complete Registration"
    if "registration opens" in t or "registration starts" in t:
        return "Start Examination Registration"
    # Prefer catalog titles, with small evidence refinements for common subtypes.
    if "viva" in t or "viva" in sent:
        return "Prepare for Viva / Oral Exam"
    if "thesis" in t or ("thesis" in sent and any(k in sent for k in ("submit", "submission", "bound"))):
        return "Submit Thesis"
    if "project" in t and "draft" in sent:
        return "Submit Draft Project Report"
    if "approval" in t or ("review" in sent and "approv" in sent) or "plagiarism" in sent:
        return "Complete Review / Approval"
    if dtype in TASK_TITLES:
        return TASK_TITLES[dtype]
    if "application deadline" in t or "job application" in t:
        return "Submit Application Before Deadline"
    if "assignment deadline" in t:
        return "Submit Assignment"
    if "project deadline" in t:
        return "Submit Project"
    if "scholarship" in t:
        return "Apply for Scholarship"
    if "placement" in t:
        return "Complete Placement Registration"
    if "internship" in t:
        return "Apply for Internship"
    if "exam date" in t or "exam schedule" in t:
        return "Prepare for Examination"
    if "admit card" in t or "hall ticket" in t:
        return "Download Admit Card / Hall Ticket"
    if "submission" in t or "document submission" in t:
        return "Submit Required Documents"
    if "final deadline" in t:
        return "Complete Action Before Final Deadline"
    return f"Action: {dtype}"


def _task_description(dtype: str, sentence: str, fine: Optional[str]) -> str:
    if fine and fine != "₹0" and "late" in dtype.lower():
        return f"Complete registration during the late window. Applicable late fee/fine: {fine}."
    if "registration" in dtype.lower() and "course" not in dtype.lower():
        return (
            "Complete the university examination registration before the deadline "
            "to avoid missing the examination."
        )
    return sentence.strip()


def _inside_span(pos: int, spans: list[tuple[int, int]]) -> bool:
    return any(s <= pos <= e for s, e in spans)


def _extract_ranges(
    text: str,
    default_year: Optional[int],
    hits: Optional[list] = None,
) -> tuple[list[DateRangeRecord], list[tuple[int, int]]]:
    """Build date ranges from consecutive ML-detected dates linked by separators.

    No regex date patterns — endpoints come from find_explicit_dates (ML).
    """
    if hits is None:
        hits = find_explicit_dates(text, default_year=default_year)
    ranges: list[DateRangeRecord] = []
    spans: list[tuple[int, int]] = []
    seen: set[tuple[str, str, str]] = set()

    for i in range(len(hits) - 1):
        left = hits[i]
        right = hits[i + 1]
        if right.dt < left.dt:
            continue
        gap = text[left.end : right.start]
        if not _is_range_gap(gap):
            continue
        window = text[max(0, left.start - 40) : min(len(text), right.end + 40)]
        purpose = _range_purpose_from_ml(window)
        key = (format_dd_mm_yyyy(left.dt), format_dd_mm_yyyy(right.dt), purpose)
        if key in seen:
            continue
        seen.add(key)
        spans.append((left.start, right.end))
        _, sentence, next_s = _sentence_covering(text, left.start, right.end)
        fine = _extract_money(window)
        ranges.append(
            DateRangeRecord(
                startDate=format_dd_mm_yyyy(left.dt),
                endDate=format_dd_mm_yyyy(right.dt),
                startDateIso=format_iso(left.dt),
                endDateIso=format_iso(right.dt),
                startDateOriginal=left.original,
                endDateOriginal=right.original,
                purpose=purpose,
                confidence="High",
                originalSentence=sentence or window.strip(),
                contextBefore="",
                contextAfter=next_s,
                fineAmount=fine if fine and fine != "₹0" else None,
                lateFee=fine if fine and fine != "₹0" else None,
            )
        )
    return ranges, spans



def _build_record(
    *,
    dtype: str,
    dt: datetime,
    original: str,
    sentence: str,
    prev_s: str,
    next_s: str,
    score: float,
    explanation: str,
    fine: Optional[str],
    group_id: Optional[str],
    role: Optional[str],
    order: Optional[int],
    full_text: str,
    default_year: Optional[int],
    needs_year: bool = False,
) -> DeadlineRecord:
    confidence = "High" if score >= 0.9 else ("Medium" if score >= 0.75 else "Low")
    priority = _priority_for(dtype, dt, fine=fine, sentence=sentence, document_year=default_year)
    title = _task_title(dtype, fine, sentence, full_text)
    meta_types = META_TYPES
    actionable = dtype not in meta_types and title is not None
    if dtype == "Registration Closed":
        actionable = False
    if dtype == "Holiday":
        actionable = False
    if dtype == "Policy Effective Date":
        actionable = False
    return DeadlineRecord(
        deadlineType=dtype,
        date=format_dd_mm_yyyy(dt),
        dateIso=format_iso(dt),
        dateOriginal=original.strip(),
        purpose=dtype,
        priority=priority,
        confidence=confidence,
        confidenceScore=round(score, 3),
        originalSentence=sentence.strip(),
        contextBefore=prev_s,
        contextAfter=next_s,
        needsReferenceDate=needs_year,
        explanation=explanation,
        relatedEvent=group_id,
        relationshipGroupId=group_id,
        relationshipRole=role,
        relationshipOrder=order,
        fineAmount=fine,
        lateFee=fine if fine and fine != "₹0" else None,
        penalty=fine if fine and fine != "₹0" else None,
        description=_task_description(dtype, sentence, fine),
        taskTitle=title,
        suggestedCategory=_category_for(dtype) if actionable else None,
        suggestedDueDate=format_iso(dt) if actionable else None,
        isActionable=actionable,
    )


def _link_registration_process(deadlines: list[DeadlineRecord]) -> list[DeadlineRelationship]:
    """Link multi-stage workflows (registration, recruitment, tender, etc.)."""
    relationships: list[DeadlineRelationship] = []

    process_groups = [
        (
            "Registration Process",
            [
                "Course Registration Opens",
                "Registration Opens",
                "Registration Starts",
                "Course Registration Deadline",
                "Registration Deadline",
                "Late Fee Deadline",
                "Final Late Fee Deadline",
                "Final Deadline",
                "Registration Ends",
                "Registration Closed",
            ],
        ),
        (
            "Recruitment Process",
            [
                "Application Starts",
                "Job Application Deadline",
                "Application Deadline",
                "Document Submission",
                "Verification Date",
                "Interview Date",
                "Result Date",
            ],
        ),
        (
            "Tender Process",
            [
                "EMD Deadline",
                "Tender Submission Deadline",
                "Tender Opening Date",
            ],
        ),
        (
            "Hackathon Process",
            [
                "Hackathon Registration Deadline",
                "Hackathon Date",
            ],
        ),
    ]

    used: set[int] = set()
    for process_name, process_types in process_groups:
        present = [
            (i, d)
            for i, d in enumerate(deadlines)
            if d.deadlineType in process_types and i not in used
        ]
        if len(present) < 2:
            continue
        gid = f"proc-{uuid.uuid4().hex[:8]}"
        role_map = {
            "Registration Opens": "opens",
            "Registration Starts": "opens",
            "Course Registration Opens": "opens",
            "Application Starts": "opens",
            "Registration Deadline": "normal",
            "Course Registration Deadline": "normal",
            "Late Fee Deadline": "late",
            "Final Late Fee Deadline": "final",
            "Final Deadline": "final",
            "Registration Ends": "final",
            "Registration Closed": "closed",
            "Job Application Deadline": "normal",
            "Application Deadline": "normal",
            "Interview Date": "interview",
            "Tender Submission Deadline": "normal",
            "EMD Deadline": "payment",
            "Tender Opening Date": "opening",
            "Hackathon Registration Deadline": "normal",
            "Hackathon Date": "event",
        }
        stages: list[str] = []
        for order, (idx, item) in enumerate(
            sorted(present, key=lambda x: (x[1].dateIso or "", process_types.index(x[1].deadlineType) if x[1].deadlineType in process_types else 99)),
            start=1,
        ):
            used.add(idx)
            if not item.relationshipGroupId:
                item.relationshipGroupId = gid
                item.relatedEvent = gid
                item.relationshipOrder = item.relationshipOrder or order
                item.relationshipRole = item.relationshipRole or role_map.get(item.deadlineType)
            if item.deadlineType not in stages:
                stages.append(item.deadlineType)
        relationships.append(
            DeadlineRelationship(
                groupId=gid,
                processName=process_name,
                stages=stages,
                description=" → ".join(stages),
            )
        )
    return relationships


def _classify_calendar_line(line: str) -> Optional[tuple[str, float, str]]:
    """ML-classify a calendar / timetable grid row."""
    dtype, score, explanation = _classify_type(line, line, False)
    if dtype:
        return dtype, score, explanation
    return None


def _extract_calendar_table_rows(
    text: str, default_year: Optional[int], occupied: list[tuple[int, int]]
) -> list[DeadlineRecord]:
    """Extract dates from pipe/tab/spaced calendar and timetable rows only."""
    records: list[DeadlineRecord] = []
    seen: set[tuple[str, str]] = set()
    for match in re.finditer(r"^[^\n]{6,160}$", text, re.M):
        line = match.group(0).strip()
        if not line or line.lower().startswith("date:"):
            continue
        if _inside_span(match.start(), occupied):
            continue
        # Only structured rows — avoid prose sentences that belong to the main loop
        is_tableish = bool(re.search(r"[|\t]", line) or re.search(r"\S+\s{2,}\S+", line))
        if not is_tableish:
            continue
        hits = find_explicit_dates(line, default_year=default_year)
        if not hits:
            continue
        classified = _classify_calendar_line(line)
        if not classified:
            continue
        dtype, score, explanation = classified
        for hit in hits:
            abs_start = match.start() + hit.start
            if _inside_span(abs_start, occupied):
                continue
            key = (format_dd_mm_yyyy(hit.dt), dtype)
            if key in seen:
                continue
            seen.add(key)
            occupied.append((abs_start, match.start() + hit.end))
            records.append(
                _build_record(
                    dtype=dtype,
                    dt=hit.dt,
                    original=hit.original,
                    sentence=line,
                    prev_s="",
                    next_s="",
                    score=score,
                    explanation=explanation,
                    fine=None,
                    group_id=None,
                    role=None,
                    order=None,
                    full_text=text,
                    default_year=default_year,
                    needs_year=hit.needs_year,
                )
            )
    return records


def _build_tasks(deadlines: list[DeadlineRecord]) -> list[SuggestedTask]:
    tasks: list[SuggestedTask] = []
    seen: set[tuple[str, str]] = set()
    for item in deadlines:
        if not item.isActionable or not item.suggestedDueDate or not item.taskTitle:
            continue
        key = (item.taskTitle, item.suggestedDueDate)
        if key in seen:
            continue
        seen.add(key)
        tasks.append(
            SuggestedTask(
                title=item.taskTitle,
                category=item.suggestedCategory or _category_for(item.deadlineType),
                priority=item.priority or "MEDIUM",
                dueDate=item.suggestedDueDate,
                dueDateDisplay=format_long(
                    datetime.strptime(item.suggestedDueDate, "%Y-%m-%d")
                ),
                description=item.description or item.originalSentence,
                sourceDeadlineType=item.deadlineType,
                relatedEvent=item.relatedEvent,
                relationshipGroupId=item.relationshipGroupId,
                fineAmount=item.fineAmount,
                lateFee=item.lateFee,
                penalty=item.penalty,
            )
        )
    return tasks


def extract_deadlines(text: str, document_name: Optional[str] = None) -> DeadlineExtractionResponse:
    text = clean_ocr_text(text or "")
    if not text:
        return DeadlineExtractionResponse(
            deadlines=[],
            dateRanges=[],
            suggestedTasks=[],
            relationships=[],
            summary="No readable text was provided.",
            totalDeadlines=0,
            totalDateRanges=0,
            modelVersion=_MODEL_VERSION,
        )

    working = _REF_NUMBER.sub(" ", text)
    default_year = detect_document_year(working)
    doc_type = _detect_document_type(working)

    date_hits = find_explicit_dates(working, default_year=default_year)
    ranges, range_spans = _extract_ranges(working, default_year, hits=date_hits)
    all_ranges = ranges
    occupied = list(range_spans)

    calendar_rows = _extract_calendar_table_rows(working, default_year, occupied)
    deadlines: list[DeadlineRecord] = list(calendar_rows)
    seen: set[tuple[str, str]] = {(d.date or "", d.deadlineType) for d in deadlines}

    for hit in date_hits:
        if _inside_span(hit.start, occupied):
            continue
        prev_s, sentence, next_s = _sentence_covering(working, hit.start, hit.end)
        if not sentence:
            continue
        if _IGNORE_LINE.search(sentence) and not re.search(r"\bdated?\b", sentence, re.I):
            continue

        local = _local_context(working, hit.start, hit.end)
        dtype, score, explanation = _classify_type(sentence, local, prev_s=prev_s)
        if not dtype:
            continue

        dedupe = (format_dd_mm_yyyy(hit.dt), dtype)
        if dedupe in seen:
            continue
        if dtype in {"Document Date", "Issue Date", "Notification Date", "Circular Date"}:
            if any(d.deadlineType == dtype for d in deadlines):
                continue

        fine = _extract_money(sentence)
        if not fine and prev_s and _DATE_ONLY_LINE.match(sentence.strip().rstrip(" .;:,")):
            fine = _extract_money(prev_s)
        if fine == "₹0":
            fine = None
        if dtype in {"Document Date", "Issue Date", "Notification Date", "Circular Date"}:
            fine = None

        seen.add(dedupe)
        deadlines.append(
            _build_record(
                dtype=dtype,
                dt=hit.dt,
                original=hit.original,
                sentence=sentence,
                prev_s=prev_s,
                next_s=next_s,
                score=score,
                explanation=explanation,
                fine=fine,
                group_id=None,
                role=None,
                order=None,
                full_text=working,
                default_year=default_year,
                needs_year=hit.needs_year,
            )
        )

    relationships = _link_registration_process(deadlines)

    suggested = _build_tasks(deadlines)

    summary = (
        f"Extracted {len(deadlines)} date(s) and {len(all_ranges)} date range(s)"
        f"{f' from {document_name}' if document_name else ''}"
        f" ({doc_type})."
    )
    if not deadlines and not all_ranges:
        summary = (
            "No explicit calendar deadlines were found. "
            "Only dates written as calendar dates with clear event/deadline language are extracted."
        )

    return DeadlineExtractionResponse(
        deadlines=deadlines,
        dateRanges=all_ranges,
        suggestedTasks=suggested,
        relationships=relationships,
        summary=summary,
        totalDeadlines=len(deadlines),
        totalDateRanges=len(all_ranges),
        modelVersion=_MODEL_VERSION,
        documentType=doc_type,
    )
