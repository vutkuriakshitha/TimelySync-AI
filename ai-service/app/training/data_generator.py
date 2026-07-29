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
# production deadline/event types (ML classifier labels).
# ---------------------------------------------------------------------------

_DEADLINE_TYPE_TEMPLATES: dict[str, list[str]] = {
    "Document Date": [
        "Date: {date}",
        "Dated: {date}",
        "Date {date}",
    ],
    "Issue Date": [
        "Issued on {date}.",
        "Issue date: {date}",
    ],
    "Registration Opens": [
        "Registration opens on {date}.",
        "Online registration portal opens from {date}.",
    ],
    "Registration Starts": [
        "Registration starts on {date}.",
        "Semester registration starts on {date}.",
    ],
    "Registration Ends": [
        "Registration ends on {date}.",
        "Registration closes on {date}.",
    ],
    "Registration Deadline": [
        "All students must complete their examination registration by {date}.",
        "Last date for registration is {date}.",
        "Complete registration before {date}.",
        "Complete registration by {date}.",
        "Registration by {date}.",
        "Register by {date}.",
        "Last date without late fee: {date}",
        "Last date without late fee is {date}.",
        "Last date without late fee\n{date}",
        "Before {date} — Rs 0 fine",
        "Before {date} Rs 0 fine",
    ],
    "Course Registration Deadline": [
        "Course registration deadline is {date}.",
        "Complete course registration by {date}.",
    ],
    "Course Registration Opens": [
        "Course registration opens on {date}.",
    ],
    "Late Fee Deadline": [
        "With Rs 2,000 late fee: {date}",
        "With Rs 2000 late fee: {date}",
        "With Rs. 2,000 late fee: {date}",
        "With Rs 2,000 late fee\n{date}",
        "Late fee of Rs 2,000 applies until {date}.",
        "6 August - 10 August — Rs 2,000 fine",
        "{date} — Rs 2,000 fine",
        "Rs 2,000 late fee on {date}.",
    ],
    "Final Late Fee Deadline": [
        "Final late fee deadline is {date} with Rs 5,000 fine.",
        "With Rs 5,000 late fee: {date}",
        "With Rs 5000 late fee: {date}",
        "With Rs. 5,000 late fee: {date}",
        "With Rs 5,000 late fee\n{date}",
        "Final late fee Rs 5,000 on {date}.",
        "11 August - 15 August — Rs 5,000 fine",
        "{date} — Rs 5,000 fine",
        "Rs 5,000 late fee on {date}.",
    ],
    "Registration Closed": [
        "After {date} registration is not allowed.",
        "Registration is closed after {date}.",
        "After {date} registration is not allowed under any circumstances.",
        "After {date} — Not eligible",
        "After {date} Not eligible",
    ],
    "Quiz Date": [
        "Quiz is scheduled on {date}.",
        "CS201 Quiz 2 will be held on {date}.",
        "Quiz on {date}.",
    ],
    "Quiz Deadline": [
        "Complete the online quiz by {date}.",
        "Quiz submission deadline is {date}.",
    ],
    "Lab Schedule": [
        "Physics laboratory practical session is scheduled on {date}.",
        "Lab session on {date}.",
    ],
    "Lab Deadline": [
        "Lab report must be submitted before {date}.",
        "Submit laboratory work by {date}.",
    ],
    "Viva Date": [
        "Viva-voce will be held on {date}.",
        "Oral examination scheduled on {date}.",
        "Project presentation and viva voce starts from {date}.",
        "Final viva will be conducted starting from {date}.",
        "Departments will conduct vivas strictly starting from\n{date}.",
    ],
    "Assignment Deadline": [
        "Assignment must be submitted by {date}.",
        "CS101 Assignment due on {date}.",
        "Assignment deadline: {date}.",
    ],
    "Project Deadline": [
        "Project reports are due on {date}.",
        "Submit the final project before {date}.",
        "Project due by {date}.",
        "Project deadline is {date}.",
        "Draft project report must be uploaded by {date}.",
        "Upload the draft project report before {date}.",
        "Soft copy of the draft project report must be uploaded to the\nportal by {date}.",
        "Submission of draft project report by {date}.",
    ],
    "Scholarship Deadline": [
        "Last date to apply for the scholarship is {date}.",
        "Scholarship applications close on {date}.",
    ],
    "Internship Deadline": [
        "Apply for the internship before {date}.",
        "Internship application deadline {date}.",
    ],
    "Placement Deadline": [
        "Register for campus placement by {date}.",
        "Placement registration deadline is {date}.",
    ],
    "Campus Hiring Date": [
        "Campus hiring drive is scheduled on {date}.",
    ],
    "Job Application Deadline": [
        "Last date to apply for the post of Analyst is {date}.",
        "Job applications close on {date}.",
    ],
    "Application Starts": [
        "Applications start on {date}.",
        "Application window opens on {date}.",
    ],
    "Application Deadline": [
        "Application deadline is {date}.",
        "Applications close on {date}.",
    ],
    "Admission Deadline": [
        "Admission closes on {date}.",
        "Last date for admission is {date}.",
    ],
    "Hostel Deadline": [
        "Hostel fee payment deadline is {date}.",
        "Pay hostel dues before {date}.",
    ],
    "Library Deadline": [
        "Library books must be returned by {date}.",
        "Library due date {date}.",
    ],
    "Fee Payment Deadline": [
        "Tuition fee must be paid before {date}.",
        "Fee payment last date {date}.",
        "Fee payment due on {date}.",
        "Pay fees by {date}.",
        "The final deadline to complete the fee payment process is\n{date}.",
        "All outstanding fee dues must be cleared by {date}.",
        "Remit tuition and special fees on or before {date}.",
        "Fee payment for the academic session must be completed by {date}.",
    ],
    "Payment Deadline": [
        "Please pay your EMI on or before {date}.",
        "Payment due on {date}.",
    ],
    "Tender Submission Deadline": [
        "Last date for tender submission is {date}.",
        "Tender must be submitted before {date}.",
        "Last date to submit bids is {date}.",
        "Tender Notice\nLast date to submit bids is {date}.",
    ],
    "EMD Deadline": [
        "EMD must be submitted before {date}.",
        "Earnest money deposit due by {date}.",
    ],
    "Tender Opening Date": [
        "Technical bid opening on {date}.",
        "Bids will be opened on {date}.",
    ],
    "Hackathon Registration Deadline": [
        "Register for the hackathon by {date}.",
    ],
    "Hackathon Date": [
        "The hackathon starts on {date}.",
        "Hackathon scheduled on {date}.",
    ],
    "Competition Deadline": [
        "Register for the competition by {date}.",
    ],
    "Competition Date": [
        "Competition will be held on {date}.",
        "Olympiad scheduled on {date}.",
    ],
    "Club Event Date": [
        "Coding Club event is scheduled on {date}.",
    ],
    "Sports Event Date": [
        "Annual sports tournament kick-off is on {date}.",
    ],
    "Cultural Event Date": [
        "Cultural fest begins on {date}.",
    ],
    "Meeting Date": [
        "You are invited to a meeting on {date}.",
        "Meeting scheduled on {date}.",
    ],
    "Training Date": [
        "Onboarding training session is scheduled on {date}.",
    ],
    "Training Deadline": [
        "Register for training by {date}.",
    ],
    "Event Date": [
        "You are cordially invited to the alumni event on {date}.",
    ],
    "Workshop Date": [
        "Workshop on AI scheduled on {date}.",
    ],
    "Conference Date": [
        "The conference will be held on {date}.",
    ],
    "Seminar Date": [
        "Department seminar on {date}.",
    ],
    "Correction Deadline": [
        "Online correction facility closes on {date}.",
    ],
    "Hall Ticket Release": [
        "Hall tickets will be released on {date}.",
    ],
    "Admit Card Release": [
        "Admit cards will be available for download on {date}.",
    ],
    "Exam Date": [
        "End semester examination will be held on {date}.",
        "Written test scheduled for {date}.",
        "Exam will be held on {date}.",
        "Exam on {date}.",
        "The written exam is on {date}.",
    ],
    "Exam Schedule": [
        "Exam schedule: {date}.",
        "Examination schedule published for {date}.",
        "Revised exam schedule effective {date}.",
    ],
    "Interview Date": [
        "Interviews are scheduled on {date}.",
        "Personal interview on {date}.",
    ],
    "Counselling Date": [
        "Counselling will be held on {date}.",
    ],
    "Orientation Date": [
        "Orientation for freshers on {date}.",
    ],
    "Result Date": [
        "Results will be declared on {date}.",
    ],
    "Verification Date": [
        "Document verification will be conducted on {date}.",
    ],
    "Document Submission": [
        "Submit the documents by {date}.",
        "Submit documents by {date}.",
    ],
    "Timetable Update": [
        "Revised timetable is effective from {date}.",
        "Monday {date} 09:00-10:00 CS101",
        "Day Date Time Course\nMon {date} 09:00 CS101",
    ],
    "Academic Calendar Event": [
        "{date} | Commencement of classes",
        "Mid-semester break on {date}.",
    ],
    "Holiday": [
        "College will remain closed on {date} holiday.",
    ],
    "Approval Deadline": [
        "Manager approval must be obtained by {date}.",
        "Faculty review and approval must be completed on or before {date}.",
        "Plagiarism check and guide approval must be finished before {date}.",
        "Departmental review of the draft must finish by {date}.",
        "Supervisor approval is due by {date}.",
        "Review and approval of the draft must be done on or before\n{date}.",
    ],
    "Final Deadline": [
        "Final deadline is {date}.",
        "Absolute last date {date}.",
        "This is the final deadline: {date}.",
        "No further extensions; final deadline {date}.",
    ],
    "Submission Deadline": [
        "Please submit the form by {date}.",
        "Please submit by {date}.",
        "The last date for submission is {date}.",
        "Deadline: {date} for submission.",
        "Submit before {date}.",
        "Submit abstract by {date}.",
        "Apply by {date}.",
        "Full paper deadline: {date}.",
        "Camera-ready due on {date}.",
    ],
    "Policy Effective Date": [
        "This policy is effective from {date}.",
    ],
    "Policy Review Date": [
        "Next review date: {date}.",
    ],
    "Notification Date": [
        "Notification date: {date}.",
        "Notification issued on {date}.",
    ],
    "Circular Date": [
        "Circular date: {date}.",
        "This circular is dated {date}.",
    ],
    "Revaluation Deadline": [
        "Apply for revaluation before {date}.",
        "Revaluation application last date is {date}.",
    ],
    "Supplementary Exam Date": [
        "Supplementary examination will be held on {date}.",
        "Supply exam scheduled on {date}.",
    ],
    "Thesis Submission Deadline": [
        "Thesis must be submitted by {date}.",
        "Last date for thesis submission is {date}.",
        "Submit bound thesis hard copies by {date}.",
        "Hard copy of the bound thesis must be submitted no later than {date}.",
        "Three bound thesis copies must be submitted to the office by {date}.",
        "Bound reports must be submitted to the academic office no later than\n{date}.",
    ],
    "Convocation Date": [
        "Convocation ceremony will be held on {date}.",
    ],
    "Internship Start Date": [
        "Internship begins on {date}.",
    ],
    "Offer Acceptance Deadline": [
        "Accept the offer by {date}.",
        "Offer acceptance deadline is {date}.",
    ],
    "Visa Deadline": [
        "Visa application must be filed before {date}.",
    ],
    "Passport Submission Deadline": [
        "Submit passport copies by {date}.",
    ],
    "Medical Certificate Deadline": [
        "Medical certificate must be submitted by {date}.",
    ],
    "Attendance Deadline": [
        "Attendance shortage must be cleared before {date}.",
    ],
    "ID Card Collection Date": [
        "Collect ID cards on {date}.",
    ],
    "Bus Pass Deadline": [
        "Apply for bus pass before {date}.",
    ],
    "Alumni Meet Date": [
        "Alumni meet is scheduled on {date}.",
    ],
    "Webinar Date": [
        "Join the webinar on {date}.",
        "Webinar scheduled for {date}.",
    ],
    "Certificate Collection Date": [
        "Certificates can be collected from {date}.",
    ],
}

_DOCUMENT_CATEGORY_TEMPLATES: dict[str, list[str]] = {
    "Examination Circular": [
        "Examination Circular\nEnd semester examination will be held on {date}.",
        "Exam notice: written test on {date}. Admit cards available soon.",
    ],
    "Assignment Notice": [
        "Assignment Notice\nSubmit assignment by {date}.",
    ],
    "Project Submission Notice": [
        "Project submission notice. Project reports due on {date}.",
    ],
    "Quiz Schedule": [
        "Quiz Schedule\nQuiz is scheduled on {date}.",
    ],
    "Lab Schedule": [
        "Lab Schedule\nLaboratory practical session on {date}.",
    ],
    "Viva Notice": [
        "Viva Notice\nViva-voce will be held on {date}.",
    ],
    "Academic Calendar": [
        "Academic Calendar\n{date} | Commencement of classes",
    ],
    "Timetable Update": [
        "Timetable Update\nRevised timetable effective from {date}.",
    ],
    "Course Registration": [
        "Course Registration\nCourse registration deadline is {date}.",
    ],
    "Semester Registration": [
        "Semester registration circular. Complete examination registration by {date}.",
        "APEX NATIONAL UNIVERSITY\nCIRCULAR: ODD SEMESTER EXAMINATION REGISTRATION\nAll students must complete their examination registration by {date}.",
        "REF: ANU/EXAM/2026/041\nDate: {date}\nCIRCULAR: ODD SEMESTER EXAMINATION REGISTRATION",
    ],
    "Fee Notice": [
        "Fee Notice\nTuition fee must be paid before {date}.",
    ],
    "Late Fee Notice": [
        "Late fee structure. Without late fee {date}. With late fee thereafter.",
        "Late Fee Notice\nLast date without late fee: {date}",
        "Fee Payment Schedule\nWith Rs 2,000 late fee: {date}",
    ],
    "Scholarship Notice": [
        "Scholarship Notice\nLast date to apply for scholarship is {date}.",
    ],
    "Internship Opportunity": [
        "Internship Opportunity\nApply for internship before {date}.",
    ],
    "Placement Drive": [
        "Placement Drive\nRegister for placement by {date}.",
    ],
    "Campus Hiring": [
        "Campus Hiring\nCampus hiring drive on {date}.",
    ],
    "Job Recruitment Notice": [
        "Recruitment Notification\nLast date to apply for the post is {date}.",
    ],
    "Hackathon Notice": [
        "Hackathon Notice\nRegister for the hackathon by {date}.",
    ],
    "Competition Notice": [
        "Competition Notice\nOlympiad competition on {date}.",
    ],
    "Student Club Event": [
        "Student Club Event\nClub event scheduled on {date}.",
    ],
    "Sports Event": [
        "Sports Event\nTournament on {date}.",
    ],
    "Cultural Event": [
        "Cultural Event\nCultural fest begins on {date}.",
    ],
    "Workshop Notice": [
        "Workshop Notice\nWorkshop scheduled on {date}.",
    ],
    "Seminar Notice": [
        "Seminar Notice\nDepartment seminar on {date}.",
    ],
    "Conference Announcement": [
        "Conference Announcement\nConference will be held on {date}.",
    ],
    "Meeting Invitation": [
        "Meeting Invitation\nYou are invited to a meeting on {date}.",
    ],
    "Event Invitation": [
        "Event Invitation\nYou are cordially invited to the event on {date}.",
    ],
    "Admission Notice": [
        "Admission Notice\nAdmission closes on {date}.",
    ],
    "Hostel Notice": [
        "Hostel Notice\nHostel fee deadline is {date}. Clear hostel dues.",
    ],
    "Library Notice": [
        "Library Notice\nReturn library books by {date}.",
    ],
    "Tender Notice": [
        "Tender Notice\nLast date for tender submission is {date}.",
    ],
    "Government Circular": [
        "Government Order\nApplications close on {date}.",
    ],
    "HR Announcement": [
        "HR Department\nEmployees are informed forms must be submitted by {date}.",
    ],
    "Company Policy Document": [
        "Company Policy Document\nThis policy is effective from {date}.",
    ],
    "Training Schedule": [
        "Training Schedule\nTraining session scheduled on {date}.",
    ],
    "Admit Card Notice": [
        "Admit Card Notice\nAdmit cards available for download on {date}.",
    ],
    "Result Announcement": [
        "Result Announcement\nResults will be declared on {date}.",
    ],
    "Document Verification Notice": [
        "Document Verification Notice\nVerification on {date}.",
    ],
    "Counseling Schedule": [
        "Counseling Schedule\nCounselling will be held on {date}.",
    ],
    "General PDF Notice": [
        "Official Notice\nPlease submit the required form by {date}.",
    ],
    "General OCR Document": [
        "Scanned notice OCR text. Please complete the process by {date}.",
    ],
    "University Circular": [
        "University Circular\nAll students must note the date {date}.",
        "University Circular\nDate: {date}\nAll students must complete their examination registration soon.",
        "Official University Circular dated {date} regarding semester formalities.",
    ],
    "Bank Notice": [
        "Bank Notice\nPay your EMI on or before {date}.",
    ],
    "Revaluation Notice": [
        "Revaluation Notice\nApply for revaluation before {date}.",
    ],
    "Convocation Notice": [
        "Convocation Notice\nConvocation ceremony on {date}.",
    ],
    "Thesis Submission Notice": [
        "Thesis Submission Notice\nThesis must be submitted by {date}.",
    ],
    "Supplementary Exam Notice": [
        "Supplementary Exam Notice\nSupply exam on {date}.",
    ],
    "Offer Letter": [
        "Offer Letter\nAccept the offer by {date}.",
    ],
    "Webinar Announcement": [
        "Webinar Announcement\nWebinar scheduled for {date}.",
    ],
    "Alumni Meet Notice": [
        "Alumni Meet Notice\nAlumni meet on {date}.",
    ],
}

_DATE_PHRASES = [
    "15 July 2026", "15/07/2026", "15-07-2026", "July 15, 2026",
    "20 August 2026", "01 June 2026", "10-12-2026", "2026-09-30",
    "15 Aug 2026", "15th August 2026", "2026-08-15", "08/15/2026",
]


def generate_deadline_samples(n: int = 8000, seed: int = 11) -> pd.DataFrame:
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


def generate_deadline_document_samples(n: int = 5000, seed: int = 17) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    types = list(_DOCUMENT_CATEGORY_TEMPLATES.keys())
    per_type = max(1, n // len(types))
    for dtype in types:
        templates = _DOCUMENT_CATEGORY_TEMPLATES[dtype]
        for _ in range(per_type):
            template = rng.choice(templates)
            text = template.format(date=rng.choice(_DATE_PHRASES))
            if rng.random() < 0.2:
                text = f"REF: ANU/EXAM/2026/041\n{text}"
            rows.append({"text": text, "documentType": dtype})
    rng.shuffle(rows)
    return pd.DataFrame(rows[:n])
