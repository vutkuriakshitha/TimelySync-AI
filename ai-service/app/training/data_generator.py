"""
Synthetic-but-structured training data generation.

There is no historical production dataset available yet (this is a new
product), so we generate training data whose feature -> label relationships
mirror real-world time-management dynamics (tight deadlines + high effort +
low personal track record => higher failure risk, etc.), with random noise
mixed in so the relationship is *learnable* rather than deterministic. The
models below (RandomForest / LogisticRegression) then genuinely learn these
patterns from data via `.fit()` - at inference time there is no hand-written
if/else scoring, only `model.predict_proba(...)`.

As real users complete tasks, the Java backend calls POST /feedback/outcome,
and those real outcomes are stored in the `ai_outcome_feedback` MongoDB
collection so a future retraining job can blend real + synthetic data.
"""

import random

import numpy as np
import pandas as pd

CATEGORIES = ["ACADEMIC", "OPPORTUNITY", "PERSONAL_GOAL", "EVENT"]
LEVELS = ["HIGH", "MEDIUM", "LOW"]
CAUSE_TYPES = ["TIME_MANAGEMENT", "UNDERESTIMATED_EFFORT", "PRIORITY_CONFLICT", "EXTERNAL_BLOCKER", "PROCRASTINATION"]

_LEVEL_WEIGHT = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-x))


def generate_task_samples(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    hours_until_due = rng.uniform(-24, 400, n)
    priority = rng.choice(LEVELS, n, p=[0.3, 0.45, 0.25])
    category = rng.choice(CATEGORIES, n)
    impact = rng.choice(LEVELS, n, p=[0.3, 0.45, 0.25])
    effort = rng.choice(LEVELS, n, p=[0.25, 0.45, 0.3])
    user_completion_rate = np.clip(rng.beta(5, 2, n), 0, 1)
    user_on_time_rate = np.clip(rng.beta(4, 3, n), 0, 1)
    risk_score_at_creation = rng.uniform(0, 100, n)

    priority_w = np.array([_LEVEL_WEIGHT[p] for p in priority])
    effort_w = np.array([_LEVEL_WEIGHT[e] for e in effort])
    impact_w = np.array([_LEVEL_WEIGHT[i] for i in impact])

    urgency = np.where(hours_until_due < 12, 3.0,
               np.where(hours_until_due < 24, 2.2,
               np.where(hours_until_due < 72, 1.1, 0.0)))

    noise = rng.normal(0, 0.9, n)
    score = (
        -2.3
        + urgency
        + 0.55 * priority_w
        + 0.45 * effort_w
        - 2.1 * user_completion_rate
        - 1.6 * user_on_time_rate
        + 0.012 * risk_score_at_creation
        + noise
    )
    miss_probability = _sigmoid(score)
    missed = rng.binomial(1, miss_probability).astype(bool)

    days_late = np.where(
        missed,
        np.round(np.clip(rng.gamma(1.6, 1.4 + effort_w * 0.4, n), 0.2, 20), 1),
        0.0,
    )

    severity_score = (
        0.9 * impact_w
        + 0.6 * priority_w
        + np.where(np.isin(category, ["ACADEMIC", "OPPORTUNITY"]), 1.2, 0.2)
        - 0.01 * np.clip(hours_until_due, 0, None)
        + rng.normal(0, 0.7, n)
    )
    severity = pd.cut(
        severity_score,
        bins=[-np.inf, 1.5, 3.0, 4.5, np.inf],
        labels=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
    ).astype(str)

    cause = np.array([
        _sample_cause(rng, e, p, d, c)
        for e, p, d, c in zip(effort, priority, days_late, category)
    ])

    df = pd.DataFrame({
        "hoursUntilDue": hours_until_due,
        "priority": priority,
        "category": category,
        "impact": impact,
        "effort": effort,
        "userCompletionRate": user_completion_rate,
        "userOnTimeRate": user_on_time_rate,
        "riskScoreAtCreation": risk_score_at_creation,
        "missed": missed,
        "daysLate": days_late,
        "severity": severity,
        "cause": cause,
    })
    return df


def _sample_cause(rng, effort: str, priority: str, days_late: float, category: str) -> str:
    # Base weights kept low and deltas strong, so the dominant signal
    # clearly separates classes while still leaving room for noise.
    weights = np.array([0.4, 0.4, 0.4, 0.4, 0.4])
    if effort == "HIGH":
        weights[1] += 3.2  # underestimated effort
    elif effort == "MEDIUM":
        weights[1] += 1.0

    if priority == "HIGH":
        weights[2] += 2.6  # priority conflict (competing urgent tasks)
    elif priority == "MEDIUM":
        weights[2] += 0.8

    if days_late > 6:
        weights[3] += 3.0  # external blocker far more likely for long delays
    elif days_late > 3:
        weights[3] += 1.2

    if effort == "LOW" and priority != "HIGH":
        weights[4] += 3.0  # procrastination on low-effort, low-urgency tasks
    if category == "PERSONAL_GOAL":
        weights[4] += 1.0

    if days_late <= 2 and effort != "HIGH":
        weights[0] += 2.4  # plain time-management slip on a short delay

    probs = weights / weights.sum()
    return rng.choice(CAUSE_TYPES, p=probs)


# ---------------------------------------------------------------------------
# Smart-intake NLP training data: short natural-language task descriptions
# labelled with the category and priority a person would reasonably assign.
# ---------------------------------------------------------------------------

_SUBJECTS = ["Math", "Physics", "Data Structures", "Economics", "Chemistry", "History", "Biology", "English"]
_COMPANIES = ["Google", "Microsoft", "a local startup", "Amazon", "the research lab", "the design agency"]
_EVENTS = ["the hackathon", "the college fest", "the alumni meetup", "the workshop", "the concert", "the conference"]
_SKILLS = ["guitar", "coding", "public speaking", "painting", "chess", "yoga"]

_URGENT_WORDS = ["urgent", "asap", "immediately", "critical", "right now", "due tomorrow", "due today"]
_LOW_URGENCY_WORDS = ["whenever", "no rush", "someday", "eventually", "low priority", "when free"]

_TEMPLATES = {
    "ACADEMIC": [
        "Finish {subject} assignment", "Study for the {subject} exam", "Submit {subject} project report",
        "Prepare notes for {subject} class", "Complete {subject} homework", "Revise {subject} chapter 5",
        "Meet professor to discuss {subject} thesis",
    ],
    "OPPORTUNITY": [
        "Apply for the internship at {company}", "Submit scholarship application before deadline",
        "Prepare for the interview with {company}", "Follow up with {company} recruiter",
        "Update resume and portfolio for {company}", "Register for {event} networking session",
    ],
    "PERSONAL_GOAL": [
        "Go to the gym", "Read 30 pages of my book", "Meditate for 20 minutes",
        "Practice {skill} for an hour", "Plan my weekly budget", "Cook a healthy meal",
        "Journal about today", "Call my parents",
    ],
    "EVENT": [
        "Attend {event}", "Book tickets for {event}", "RSVP for {event}",
        "Organize logistics for {event}", "Prepare a speech for {event}", "Buy a gift for the party",
    ],
}


def generate_intake_samples(n: int = 3000, seed: int = 7) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        category = rng.choice(CATEGORIES)
        template = rng.choice(_TEMPLATES[category])
        text = template.format(
            subject=rng.choice(_SUBJECTS),
            company=rng.choice(_COMPANIES),
            event=rng.choice(_EVENTS),
            skill=rng.choice(_SKILLS),
        )

        priority_roll = rng.random()
        if priority_roll < 0.22:
            text = f"{text} {rng.choice(_URGENT_WORDS)}"
            priority = "HIGH"
        elif priority_roll < 0.40:
            text = f"{text}, {rng.choice(_LOW_URGENCY_WORDS)}"
            priority = "LOW"
        else:
            # No explicit urgency keyword - priority leans on category base rate + noise
            base = {"OPPORTUNITY": 0.55, "ACADEMIC": 0.4, "EVENT": 0.3, "PERSONAL_GOAL": 0.15}[category]
            priority = "HIGH" if rng.random() < base else rng.choice(["MEDIUM", "MEDIUM", "LOW"])

        rows.append({"text": text, "category": category, "priority": priority})

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Deadline-type NLP training data: notice/circular sentences labelled with
# the kind of actionable date they describe.
# ---------------------------------------------------------------------------

_DEADLINE_TYPE_TEMPLATES: dict[str, list[str]] = {
    "Submission Deadline": [
        "The last date for submission is {date}.",
        "Submit documents on or before {date}.",
        "Applications must be received not later than {date}.",
        "Last date to submit the form: {date}",
    ],
    "Last Date to Apply": [
        "Last date to apply is {date}.",
        "Apply before {date} to be considered.",
        "The final date for applications is {date}.",
    ],
    "Registration Start Date": [
        "Registration starts on {date}.",
        "Online registration opens from {date}.",
        "Registration commencing on {date}.",
    ],
    "Registration End Date": [
        "Registration closes on {date}.",
        "Last date for registration is {date}.",
        "Registration ends on {date}.",
    ],
    "Application Start Date": [
        "Applications are accepted from {date}.",
        "Application window opens on {date}.",
        "Apply online starting {date}.",
    ],
    "Application End Date": [
        "Applications close on {date}.",
        "Last date for online application is {date}.",
        "Application deadline: {date}",
    ],
    "Exam Date": [
        "Examination will be held on {date}.",
        "Written test scheduled for {date}.",
        "Exam date: {date}",
    ],
    "Interview Date": [
        "Interviews will be conducted on {date}.",
        "Personal interview on {date}.",
        "Shortlisted candidates interview date {date}.",
    ],
    "Document Verification Date": [
        "Document verification on {date}.",
        "Bring originals for verification on {date}.",
        "Certificate verification scheduled {date}.",
    ],
    "Correction Window Start": [
        "Correction window opens on {date}.",
        "Edit application form from {date}.",
    ],
    "Correction Window End": [
        "Correction window closes on {date}.",
        "Last date for corrections is {date}.",
    ],
    "Fee Payment Deadline": [
        "Fee payment last date {date}.",
        "Pay application fee before {date}.",
        "Last date for fee deposit is {date}.",
    ],
    "Bid Opening Date": [
        "Bids will be opened on {date}.",
        "Technical bid opening on {date}.",
    ],
    "Tender Submission Deadline": [
        "Tender must be submitted before {date}.",
        "Last date for tender submission is {date}.",
    ],
    "Event Date": [
        "The event will be held on {date}.",
        "Programme scheduled on {date}.",
    ],
    "Meeting Date": [
        "Meeting scheduled on {date}.",
        "Board meeting on {date} at 10 AM.",
    ],
    "Result Date": [
        "Results will be declared on {date}.",
        "Merit list publication date {date}.",
    ],
    "Notification Release Date": [
        "Notification released on {date}.",
        "Advertisement published on {date}.",
    ],
    "Effective Date": [
        "Effective from {date}.",
        "This order is effective from {date}.",
    ],
    "Valid From": [
        "Valid from {date}.",
        "Certificate valid from {date}.",
    ],
    "Valid Until": [
        "Valid until {date}.",
        "Valid up to {date}.",
    ],
    "Hearing Date": [
        "Hearing fixed on {date}.",
        "Next hearing date {date}.",
    ],
    "Renewal Deadline": [
        "Renewal must be completed by {date}.",
        "Last date for renewal is {date}.",
    ],
    "Expiry Date": [
        "Expires on {date}.",
        "License expiry date {date}.",
    ],
    "Other Important Date": [
        "Important date noted: {date}.",
        "Please note the date {date} for your records.",
    ],
}

_DATE_PHRASES = [
    "15 July 2026", "15/07/2026", "15-07-2026", "July 15, 2026",
    "20 August 2026", "01 June 2026", "10-12-2026", "2026-09-30",
]


def generate_deadline_samples(n: int = 6000, seed: int = 11) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    types = list(_DEADLINE_TYPE_TEMPLATES.keys())
    per_type = max(1, n // len(types))

    for dtype in types:
        templates = _DEADLINE_TYPE_TEMPLATES[dtype]
        for _ in range(per_type):
            template = rng.choice(templates)
            date_phrase = rng.choice(_DATE_PHRASES)
            text = template.format(date=date_phrase)
            if rng.random() < 0.15:
                text = f"NOTICE: {text}"
            if rng.random() < 0.10:
                text = f"{text} Candidates are advised to complete formalities early."
            rows.append({"text": text, "deadlineType": dtype})

    rng.shuffle(rows)
    return pd.DataFrame(rows[:n])
