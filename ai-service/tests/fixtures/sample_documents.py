"""50+ diverse official-document fixtures for deadline extraction regression."""

from __future__ import annotations

# Each fixture:
#   id, category, text, expect_types (subset that must appear),
#   expect_dates (DD-MM-YYYY that must appear), forbid_types, min_dates, max_dates,
#   expect_ranges (optional), require_tasks (optional bool)

FIXTURES: list[dict] = []


def _add(**kwargs):
    FIXTURES.append(kwargs)


# ---------------------------------------------------------------------------
# 1–10: Single deadline / simple notices
# ---------------------------------------------------------------------------
_add(
    id="anu_circular",
    category="single_deadline",
    text="""
APEX NATIONAL UNIVERSITY
REF: ANU/EXAM/2026/041
Date: 20 July 2026
CIRCULAR: ODD SEMESTER EXAMINATION REGISTRATION
All students must complete their examination registration by 15 August 2026.
""",
    expect_types={"Document Date", "Registration Deadline"},
    expect_dates={"20-07-2026", "15-08-2026"},
    min_dates=2,
    max_dates=2,
    require_tasks=True,
)

_add(
    id="cvr_fee_circular",
    category="fee",
    text="""
CVR COLLEGE OF ENGINEERING
REF: CVR/FEE/2026-27/089 Date: 29 July 2026
CIRCULAR: PAYMENT OF TUITION FEE FOR ACADEMIC YEAR
2026-27
Special fees for the upcoming academic session 2026-27 are now due.
The final deadline to complete the fee payment process is 15-08-2026.
""",
    expect_types={"Document Date", "Fee Payment Deadline"},
    expect_dates={"29-07-2026", "15-08-2026"},
    forbid_dates={"27-07-2026"},
    min_dates=2,
    max_dates=2,
    require_tasks=True,
)

_add(
    id="assignment_due",
    category="assignment",
    text="Date: 01-09-2026\nCS101 Assignment 3 must be submitted by 20 September 2026.",
    expect_types={"Document Date", "Assignment Deadline"},
    expect_dates={"01-09-2026", "20-09-2026"},
    min_dates=2,
    max_dates=3,
)

_add(
    id="project_deadline",
    category="assignment",
    text="Final year project reports are due on 30/11/2026. Late submissions will not be accepted.",
    expect_types={"Project Deadline"},
    expect_dates={"30-11-2026"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="scholarship",
    category="scholarship",
    text="Merit Scholarship Notice\nLast date to apply for the scholarship is 12 August 2026.",
    expect_types={"Scholarship Deadline"},
    expect_dates={"12-08-2026"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="internship",
    category="internship",
    text="Internship Circular\nStudents must apply for the summer internship before 15-04-2026.",
    expect_types={"Internship Deadline"},
    expect_dates={"15-04-2026"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="placement",
    category="placement",
    text="Placement Notice\nRegister for campus placement by Aug 25, 2026.",
    expect_types={"Placement Deadline"},
    expect_dates={"25-08-2026"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="hostel_fee",
    category="fee",
    text="Hostel office: hostel fee payment deadline is 10 October 2026.",
    expect_types={"Hostel Deadline"},
    expect_dates={"10-10-2026"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="library_return",
    category="library",
    text="Library books must be returned by 5th Jan 2027.",
    expect_types={"Library Deadline"},
    expect_dates={"05-01-2027"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="admission",
    category="admissions",
    text="Admission Notification\nAdmission closes on 2026-06-30.",
    expect_types={"Admission Deadline"},
    expect_dates={"30-06-2026"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="bank_emi",
    category="bank",
    text="Bank Notice\nPlease pay your EMI on or before 07/08/2026 to avoid penalty.",
    expect_types={"Payment Deadline"},
    expect_dates={"07-08-2026"},
    min_dates=1,
    max_dates=2,
)

# ---------------------------------------------------------------------------
# 11–20: Date formats
# ---------------------------------------------------------------------------
for i, (label, date_str, expected) in enumerate(
    [
        ("dmy_long", "Submit the form by 15 August 2026.", "15-08-2026"),
        ("dmy_abbr", "Submit the form by 15 Aug 2026.", "15-08-2026"),
        ("dmy_dash_mon", "Submit the form by 15-Aug-2026.", "15-08-2026"),
        ("dmy_slash_mon", "Submit the form by 15/Aug/2026.", "15-08-2026"),
        ("numeric_dmy", "Submit the form by 15/08/2026.", "15-08-2026"),
        ("numeric_dash", "Submit the form by 15-08-2026.", "15-08-2026"),
        ("iso", "Submit the form by 2026-08-15.", "15-08-2026"),
        ("mdy_us", "Submit the form by 08/15/2026.", "15-08-2026"),
        ("mdy_text", "Submit the form by August 15, 2026.", "15-08-2026"),
        ("ordinal", "Submit the form by 15th August 2026.", "15-08-2026"),
    ],
    start=1,
):
    _add(
        id=f"format_{label}",
        category="formats",
        text=f"Date: 01 July 2026\n{date_str}",
        expect_types={"Submission Deadline"},
        expect_dates={expected},
        min_dates=1,
        max_dates=3,
    )

# ---------------------------------------------------------------------------
# 21–28: OCR variations + short year + dotted ISO
# ---------------------------------------------------------------------------
_add(
    id="ocr_merged",
    category="ocr",
    text="Date: 01 July 2026\nPlease submit by 15Augu5t2026.",
    expect_dates={"15-08-2026"},
    expect_types={"Submission Deadline"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="ocr_comma",
    category="ocr",
    text="Date: 01 July 2026\nDeadline: 15 Aug,2026 for submission.",
    expect_dates={"15-08-2026"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="ocr_nospace",
    category="ocr",
    text="Date: 01 July 2026\nSubmit before 15Aug2026.",
    expect_dates={"15-08-2026"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="ocr_dash_year",
    category="ocr",
    text="Date: 01 July 2026\nComplete registration by 15 Aug-2026.",
    expect_dates={"15-08-2026"},
    expect_types={"Registration Deadline"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="short_year",
    category="formats",
    text="Date: 01-07-2026\nApply by 15/08/26.",
    expect_dates={"15-08-2026"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="dotted_iso",
    category="formats",
    text="Date: 01.07.2026\nExam will be held on 2026.08.15.",
    expect_dates={"15-08-2026"},
    expect_types={"Exam Date"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="dotted_dmy",
    category="formats",
    text="Date: 01.07.2026\nFee payment due on 15.08.2026.",
    expect_dates={"15-08-2026"},
    expect_types={"Fee Payment Deadline"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="partial_date_with_doc_year",
    category="formats",
    text="Date: 20 July 2026\nAssignment deadline: 15 August.",
    expect_dates={"15-08-2026"},
    expect_types={"Assignment Deadline"},
    min_dates=2,
    max_dates=3,
)

# ---------------------------------------------------------------------------
# 29–35: Date ranges
# ---------------------------------------------------------------------------
_add(
    id="range_from_to",
    category="ranges",
    text="Date: 1 May 2026\nApplications are accepted from 1 June to 15 June 2026.",
    expect_ranges=True,
    expect_dates={"01-06-2026", "15-06-2026"},
    min_dates=0,
    max_dates=5,
)

_add(
    id="range_between",
    category="ranges",
    text="Date: 1 May 2026\nCorrection window between 1st June and 15th June 2026.",
    expect_dates={"01-06-2026", "15-06-2026"},
    min_dates=1,
    max_dates=5,
)

_add(
    id="range_numeric",
    category="ranges",
    text="Date: 01/05/2026\nRegistration window: 01/06/2026 - 15/06/2026.",
    expect_ranges=True,
    min_dates=0,
    max_dates=5,
)

_add(
    id="range_until",
    category="ranges",
    text="Date: 1 May 2026\nFrom 1 June until 15 June 2026 applications will be accepted.",
    expect_ranges=True,
    min_dates=0,
    max_dates=5,
)

_add(
    id="range_dash_text",
    category="ranges",
    text="Date: 1 May 2026\nExam schedule: 1st June - 15th June 2026.",
    expect_dates={"01-06-2026", "15-06-2026"},
    min_dates=1,
    max_dates=5,
)

_add(
    id="multi_dates_one_sentence",
    category="multiple",
    text="Date: 1 Aug 2026\nSubmit documents by 10 August 2026 and pay fees by 12 August 2026.",
    expect_dates={"10-08-2026", "12-08-2026"},
    min_dates=2,
    max_dates=5,
)

_add(
    id="exam_and_result",
    category="exam",
    text="""Date: 5 March 2026
End semester examination will be held on 20 April 2026.
Results will be declared on 15 May 2026.
""",
    expect_types={"Exam Date", "Result Date"},
    expect_dates={"20-04-2026", "15-05-2026"},
    min_dates=2,
    max_dates=4,
)

# ---------------------------------------------------------------------------
# 36–42: Late fee schedules / penalties
# ---------------------------------------------------------------------------
_add(
    id="late_fee_labeled",
    category="late_fee",
    text="""
Date: 1 July 2026
Last date without late fee:
5 August
With Rs 2,000 late fee:
10 August
With Rs 5,000 late fee:
15 August
After 15 August registration is not allowed.
""",
    expect_types={
        "Document Date",
        "Registration Deadline",
        "Late Fee Deadline",
        "Final Late Fee Deadline",
        "Registration Closed",
    },
    expect_dates={"05-08-2026", "10-08-2026", "15-08-2026", "01-07-2026"},
    min_dates=4,
    max_dates=6,
    require_tasks=True,
    require_relationships=True,
)

_add(
    id="late_fee_table",
    category="late_fee",
    text="""
Date: 1 July 2026
Fee structure for examination registration:
Before 5 August — Rs 0 fine
6 August - 10 August — Rs 2,000 fine
11 August - 15 August — Rs 5,000 fine
After 15 August — Not eligible
""",
    expect_types={"Registration Deadline", "Registration Closed"},
    expect_ranges=True,
    min_dates=2,
    max_dates=8,
    require_relationships=True,
)

_add(
    id="fee_payment_only",
    category="fee",
    text="Date: 10/01/2026\nTuition fee must be paid before 28 February 2026.",
    expect_types={"Fee Payment Deadline"},
    expect_dates={"28-02-2026"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="admit_card",
    category="exam",
    text="Date: 1 Sep 2026\nAdmit cards will be available for download on 10 September 2026.",
    expect_types={"Admit Card Release"},
    expect_dates={"10-09-2026"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="hall_ticket",
    category="exam",
    text="Date: 1 Sep 2026\nHall tickets will be released on 12-09-2026.",
    expect_types={"Hall Ticket Release"},
    expect_dates={"12-09-2026"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="interview",
    category="recruitment",
    text="Recruitment Notification\nInterviews are scheduled on 22 August 2026.",
    expect_types={"Interview Date"},
    expect_dates={"22-08-2026"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="counselling",
    category="admissions",
    text="Date: 1 June 2026\nCounselling will be held on 18 June 2026.",
    expect_types={"Counselling Date"},
    expect_dates={"18-06-2026"},
    min_dates=1,
    max_dates=3,
)

# ---------------------------------------------------------------------------
# 43–50+: Document types, hallucination guards, mixed
# ---------------------------------------------------------------------------
_add(
    id="tender",
    category="tender",
    text="Tender Notice\nLast date to submit bids is 30-09-2026.",
    expect_types={"Tender Submission Deadline"},
    expect_dates={"30-09-2026"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="govt_order",
    category="government",
    text="Government Order\nApplications close on 15th Oct 2026.",
    expect_dates={"15-10-2026"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="conference",
    category="conference",
    text="Conference Brochure\nThe conference will be held on 5 November 2026.",
    expect_types={"Conference Date"},
    expect_dates={"05-11-2026"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="workshop",
    category="conference",
    text="Workshop on AI scheduled on 8 Dec 2026. Register by 1 Dec 2026.",
    expect_dates={"08-12-2026", "01-12-2026"},
    min_dates=2,
    max_dates=4,
)

_add(
    id="seminar",
    category="conference",
    text="Department seminar on 14-03-2026. All students are invited.",
    expect_types={"Seminar Date"},
    expect_dates={"14-03-2026"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="holiday",
    category="holiday",
    text="Circular\nCollege will remain closed on 15 August 2026 (Independence Day holiday).",
    expect_types={"Holiday"},
    expect_dates={"15-08-2026"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="orientation",
    category="academic",
    text="Date: 1 July 2026\nOrientation for freshers on 20 July 2026.",
    expect_types={"Orientation Date"},
    expect_dates={"20-07-2026"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="correction_deadline",
    category="academic",
    text="Date: 1 Aug 2026\nOnline correction facility closes on 8 August 2026.",
    expect_types={"Correction Deadline"},
    expect_dates={"08-08-2026"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="no_hallucination_words",
    category="guards",
    text="""
Date: 20 July 2026
This is to inform students that the portal is now open.
Students are advised to update details so that records are correct.
Clear any dues to unlock modules under any circumstances.
Registration by 15 August 2026.
""",
    expect_types={"Document Date", "Registration Deadline"},
    expect_dates={"20-07-2026", "15-08-2026"},
    forbid_originals={"to", "now", "are", "so", "any"},
    min_dates=2,
    max_dates=3,
)

_add(
    id="ignore_ref_number",
    category="guards",
    text="""
REF: ANU/EXAM/2026/041
Date: 20 July 2026
University Road, Sector 5, New Delhi - 110001
Phone: 011-23456789
Complete registration by 15/08/2026.
""",
    expect_dates={"20-07-2026", "15-08-2026"},
    min_dates=2,
    max_dates=3,
    forbid_types={"Exam Date"},
)

_add(
    id="registration_opens_and_ends",
    category="multiple",
    text="""
Date: 1 July 2026
Registration opens on 5 July 2026.
Registration ends on 15 August 2026.
""",
    expect_types={"Registration Opens", "Registration Ends"},
    expect_dates={"05-07-2026", "15-08-2026"},
    min_dates=2,
    max_dates=4,
    require_relationships=True,
)

_add(
    id="hr_announcement",
    category="corporate",
    text="HR Department\nEmployees are informed that appraisal forms must be submitted by 31-03-2026.",
    expect_dates={"31-03-2026"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="grant",
    category="grant",
    text="Grant Notification\nResearch grant applications are due on September 30, 2026.",
    expect_dates={"30-09-2026"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="mixed_formats_doc",
    category="formats",
    text="""
Date: 01/07/2026
Submit abstract by 15-Aug-2026.
Full paper deadline: August 30, 2026.
Camera-ready due on 2026-09-15.
""",
    expect_dates={"15-08-2026", "30-08-2026", "15-09-2026"},
    min_dates=3,
    max_dates=5,
)

_add(
    id="verification",
    category="academic",
    text="Date: 2 Jan 2026\nDocument verification will be conducted on 10 January 2026.",
    expect_types={"Verification Date"},
    expect_dates={"10-01-2026"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="document_submission",
    category="academic",
    text="Date: 2 Jan 2026\nSubmit the documents by 20/01/2026 at the admin office.",
    expect_types={"Document Submission"},
    expect_dates={"20-01-2026"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="cvr_tuition_fee_circular",
    category="fee",
    text="""
CVR COLLEGE OF ENGINEERING
Vastunagar, Mangalpalli (V), Ibrahimpatnam (M), Rangareddy (D), Telangana 501510
An Autonomous Institution, Accredited by NAAC with 'A' Grade

REF: CVR/FEE/2026-27/089 Date: 29 July 2026

CIRCULAR: PAYMENT OF TUITION FEE FOR ACADEMIC YEAR

2026-27

This circular is to formally notify all B.Tech II, III, and IV year students that the tuition and
special fees for the upcoming academic session 2026-27 are now due. The fee structure
conforms to the directives issued by the Telangana Admission and Fee Regulatory Committee
(TAFRC).

Fee Category Amount (INR)
Annual Tuition Fee 1,50,000/-
Special Fee & NBA/NAAC Fee 5,500/-
Total Payable Amount 1,55,500/-

Students and parents are advised to remit the fee exclusively through the official college
online payment portal available on the CVR College website. Alternatively, payments can be
made via Demand Draft drawn in favor of "CVR College of Engineering" payable at
Hyderabad, which should be submitted to the Accounts Section during regular working hours.
To avoid any late payment penalties or disruption in academic access, it is mandatory that all
outstanding dues are cleared in full. The final deadline to complete the fee payment process is
15-08-2026.
No extensions will be granted beyond this date, and a late fee penalty of Rs. 100/- per day will
be applicable for payments made after the stipulated deadline.

Principal
CVR College of Engineering
""",
    expect_types={"Document Date", "Fee Payment Deadline"},
    expect_dates={"29-07-2026", "15-08-2026"},
    forbid_dates={"27-07-2026"},
    min_dates=2,
    max_dates=3,
    require_tasks=True,
)

_add(
    id="nitw_major_project_phase2",
    category="project",
    text="""
NATIONAL INSTITUTE OF TECHNOLOGY, WARANGAL
National Institute of Technology Campus, Warangal, Telangana 506004
An Institute of National Importance under Ministry of Education, Govt. of India

REF: NITW/ACAD/2026/104 Date: 29 July 2026

CIRCULAR: FINAL YEAR B.TECH MAJOR PROJECT PHASE-II SCHEDULE

This circular is to inform all final-year B.Tech students and faculty guides regarding the
mandatory schedule and phased deadlines for the Major Project Phase-II submissions for the
ongoing academic semester.
To ensure a structured evaluation process and timely assessment, the Departmental Project
Evaluation Committee (DPEC) has finalized the following submission and review deadlines:
Submission of Draft Project Report (Soft Copy): Must be uploaded to the
department portal by 12 August 2026.
First Plagiarism Check & Faculty Review: Completion of faculty review and
approval of the draft must be done on or before 22 August 2026.
Final Project Presentation & Viva-Voce: The respective departments will conduct the
final vivas strictly starting from 05 September 2026.
Hard Copy Submission of Bound Reports: Three copies of the final bound thesis
must be submitted to the academic office no later than 15 September 2026.
Students failing to adhere to any of these stipulated deadlines will not be permitted to
participate in the final Viva-Voce examination and will be awarded an 'F' grade for the Major
Project component.
""",
    expect_types={
        "Document Date",
        "Project Deadline",
        "Approval Deadline",
        "Viva Date",
        "Thesis Submission Deadline",
    },
    expect_dates={"29-07-2026", "12-08-2026", "22-08-2026", "05-09-2026", "15-09-2026"},
    forbid_types={"Seminar Date", "Fee Payment Deadline", "Final Deadline"},
    min_dates=5,
    max_dates=6,
    require_tasks=True,
)

assert len(FIXTURES) >= 50, f"Need >=50 fixtures, have {len(FIXTURES)}"
