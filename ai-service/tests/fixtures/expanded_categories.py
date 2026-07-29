"""Expanded category fixtures: quiz, lab, viva, calendars, events, tenders, etc."""

from __future__ import annotations

EXPANDED_FIXTURES: list[dict] = []


def _add(**kwargs):
    EXPANDED_FIXTURES.append(kwargs)


_add(
    id="quiz_schedule",
    category="Quiz Schedules",
    text="Date: 1 Sep 2026\nCS201 Quiz 2 is scheduled on 12 September 2026 in Room 204.",
    expect_types={"Quiz Date"},
    expect_dates={"12-09-2026"},
    expect_doc_type="Quiz Schedule",
    min_dates=1,
    max_dates=3,
)

_add(
    id="quiz_deadline",
    category="Quiz Schedules",
    text="Date: 1 Sep 2026\nComplete the online quiz by 15/09/2026.",
    expect_types={"Quiz Deadline"},
    expect_dates={"15-09-2026"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="lab_schedule",
    category="Lab Schedules",
    text="Date: 5 Jan 2026\nPhysics laboratory practical session is scheduled on 20 January 2026.",
    expect_types={"Lab Schedule"},
    expect_dates={"20-01-2026"},
    expect_doc_type="Lab Schedule",
    min_dates=1,
    max_dates=3,
)

_add(
    id="lab_deadline",
    category="Lab Schedules",
    text="Date: 5 Jan 2026\nLab report must be submitted before 28-01-2026.",
    expect_types={"Lab Deadline"},
    expect_dates={"28-01-2026"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="viva_notice",
    category="Viva / Oral Exam Notices",
    text="Date: 10 Apr 2026\nViva-voce for final year project will be held on 25 April 2026.",
    expect_types={"Viva Date"},
    expect_dates={"25-04-2026"},
    expect_doc_type="Viva Notice",
    min_dates=1,
    max_dates=3,
)

_add(
    id="academic_calendar",
    category="Academic Calendars",
    text="""
Academic Calendar Odd Semester 2026
01 August 2026 | Commencement of classes
15 September 2026 | Mid-semester break
20 November 2026 | End of classes
""",
    expect_types={"Academic Calendar Event"},
    expect_dates={"01-08-2026", "15-09-2026", "20-11-2026"},
    expect_doc_type="Academic Calendar",
    min_dates=3,
    max_dates=6,
)

_add(
    id="course_registration",
    category="Course Registration",
    text="""
Date: 1 July 2026
Course registration opens on 5 July 2026.
Course registration deadline is 20 July 2026.
""",
    expect_types={"Course Registration Opens", "Course Registration Deadline"},
    expect_dates={"05-07-2026", "20-07-2026"},
    expect_doc_type="Course Registration",
    min_dates=2,
    max_dates=4,
    require_relationships=True,
)

_add(
    id="hackathon",
    category="Hackathons",
    text="""
Date: 1 Oct 2026
Register for the campus hackathon by 10 October 2026.
The hackathon starts on 18 October 2026.
""",
    expect_types={"Hackathon Registration Deadline", "Hackathon Date"},
    expect_dates={"10-10-2026", "18-10-2026"},
    expect_doc_type="Hackathon Notice",
    min_dates=2,
    max_dates=4,
    require_tasks=True,
)

_add(
    id="competition",
    category="Competitions",
    text="Date: 1 Feb 2026\nMath olympiad competition will be held on 14 February 2026.\nRegister for the competition by 5 Feb 2026.",
    expect_types={"Competition Date", "Competition Deadline"},
    expect_dates={"14-02-2026", "05-02-2026"},
    min_dates=2,
    max_dates=4,
)

_add(
    id="club_event",
    category="Student Club Events",
    text="Date: 1 Mar 2026\nCoding Club event is scheduled on 12 March 2026 in the auditorium.",
    expect_types={"Club Event Date"},
    expect_dates={"12-03-2026"},
    expect_doc_type="Student Club Event",
    min_dates=1,
    max_dates=3,
)

_add(
    id="sports_event",
    category="Sports Events",
    text="Date: 1 Dec 2026\nAnnual sports tournament kick-off is on 8 December 2026.",
    expect_types={"Sports Event Date"},
    expect_dates={"08-12-2026"},
    expect_doc_type="Sports Event",
    min_dates=1,
    max_dates=3,
)

_add(
    id="cultural_event",
    category="Cultural Events",
    text="Date: 1 Jan 2027\nCultural fest begins on 20 January 2027.",
    expect_types={"Cultural Event Date"},
    expect_dates={"20-01-2027"},
    expect_doc_type="Cultural Event",
    min_dates=1,
    max_dates=3,
)

_add(
    id="timetable_update",
    category="Timetable / Schedule Updates",
    text="Date: 10 Aug 2026\nRevised timetable is effective from 18 August 2026.",
    expect_types={"Timetable Update"},
    expect_dates={"18-08-2026"},
    expect_doc_type="Timetable Update",
    min_dates=1,
    max_dates=3,
)

_add(
    id="timetable_grid",
    category="Timetable / Schedule Updates",
    text="""
Class Schedule Update
CS101 Lab | 22 August 2026 | 10:00 AM
EE200 Tutorial | 23 August 2026 | 02:00 PM
""",
    expect_dates={"22-08-2026", "23-08-2026"},
    min_dates=2,
    max_dates=5,
)

_add(
    id="campus_hiring",
    category="Campus Hiring",
    text="Date: 1 Sep 2026\nCampus hiring drive is scheduled on 15 September 2026. Register by 10 Sep 2026.",
    expect_types={"Campus Hiring Date"},
    expect_dates={"15-09-2026"},
    min_dates=1,
    max_dates=4,
)

_add(
    id="job_recruitment",
    category="Job Recruitment Notices",
    text="""
Recruitment Notification
Last date to apply for the post of Analyst is 30-09-2026.
Interviews are scheduled on 15 October 2026.
""",
    expect_types={"Job Application Deadline", "Interview Date"},
    expect_dates={"30-09-2026", "15-10-2026"},
    expect_doc_type="Job Recruitment Notice",
    min_dates=2,
    max_dates=4,
    require_relationships=True,
)

_add(
    id="tender_notice",
    category="Tender Notices",
    text="""
Tender Notice
EMD must be submitted before 05/10/2026.
Last date for tender submission is 10/10/2026.
Technical bid opening on 15/10/2026.
""",
    expect_types={"EMD Deadline", "Tender Submission Deadline", "Tender Opening Date"},
    expect_dates={"05-10-2026", "10-10-2026", "15-10-2026"},
    expect_doc_type="Tender Notice",
    min_dates=3,
    max_dates=5,
    require_relationships=True,
)

_add(
    id="govt_circular",
    category="Government Circulars",
    text="Government Order\nApplications close on 15th Oct 2026 for the citizen services portal.",
    expect_dates={"15-10-2026"},
    expect_doc_type="Government Circular",
    min_dates=1,
    max_dates=2,
)

_add(
    id="hr_announcement",
    category="HR Announcements",
    text="HR Department\nEmployees are informed that appraisal forms must be submitted by 31-03-2026.",
    expect_dates={"31-03-2026"},
    expect_doc_type="HR Announcement",
    min_dates=1,
    max_dates=2,
)

_add(
    id="company_policy",
    category="Company Policy Documents",
    text="""
Company Policy Document
This policy is effective from 01 January 2027.
Next review date: 01 January 2028.
""",
    expect_types={"Policy Effective Date", "Policy Review Date"},
    expect_dates={"01-01-2027", "01-01-2028"},
    expect_doc_type="Company Policy Document",
    min_dates=2,
    max_dates=3,
)

_add(
    id="training_schedule",
    category="Training Schedules",
    text="Date: 1 May 2026\nOnboarding training session is scheduled on 12 May 2026.\nRegister for training by 8 May 2026.",
    expect_types={"Training Date", "Training Deadline"},
    expect_dates={"12-05-2026", "08-05-2026"},
    expect_doc_type="Training Schedule",
    min_dates=2,
    max_dates=4,
)

_add(
    id="meeting_invite",
    category="Meeting Invitations",
    text="You are invited to a meeting on 22 July 2026 at 3 PM in Conference Room A.",
    expect_types={"Meeting Date"},
    expect_dates={"22-07-2026"},
    expect_doc_type="Meeting Invitation",
    min_dates=1,
    max_dates=2,
)

_add(
    id="event_invite",
    category="Event Invitations",
    text="You are cordially invited to the alumni event on 5 November 2026.",
    expect_types={"Event Date"},
    expect_dates={"05-11-2026"},
    expect_doc_type="Event Invitation",
    min_dates=1,
    max_dates=2,
)

_add(
    id="general_pdf_notice",
    category="General PDF Notices",
    text="Official Notice\nPlease submit the required form by 12-08-2026.",
    expect_types={"Submission Deadline"},
    expect_dates={"12-08-2026"},
    min_dates=1,
    max_dates=2,
)

_add(
    id="general_ocr_noisy",
    category="General OCR Documents",
    text="Date: 01 July 2026\nPlease submit by 15Augu5t2026 for verification.",
    expect_dates={"15-08-2026"},
    min_dates=1,
    max_dates=3,
)

_add(
    id="exam_circular_full",
    category="Examination Circulars",
    text="""
Examination Circular
Date: 1 March 2026
End semester examination will be held on 20 April 2026.
Admit cards will be available for download on 10 April 2026.
Results will be declared on 15 May 2026.
""",
    expect_types={"Exam Date", "Admit Card Release", "Result Date"},
    expect_dates={"20-04-2026", "10-04-2026", "15-05-2026"},
    min_dates=3,
    max_dates=5,
)

_add(
    id="multiline_mixed_formats",
    category="General PDF Notices",
    text="""
Date: 01/07/2026
Quiz on 15-Aug-2026.
Lab practical scheduled on August 20, 2026.
Viva voce on 2026-09-01.
Project due by 15.09.2026.
""",
    expect_types={"Quiz Date", "Lab Schedule", "Viva Date", "Project Deadline"},
    expect_dates={"15-08-2026", "20-08-2026", "01-09-2026", "15-09-2026"},
    min_dates=4,
    max_dates=6,
)

_add(
    id="no_false_positive_words",
    category="General OCR Documents",
    text="""
Date: 20 July 2026
The portal is now open so students are advised to clear any dues.
Submit registration by 15 August 2026.
""",
    expect_types={"Document Date", "Registration Deadline"},
    expect_dates={"20-07-2026", "15-08-2026"},
    forbid_originals={"to", "now", "are", "so", "any"},
    min_dates=2,
    max_dates=3,
)

# Uncovered ML type classes (audit gap: trained but not in fixtures)
_add(id="gap_revaluation", category="gaps", text="Date: 1 Aug 2026\nApply for revaluation before 20 August 2026.", expect_types={"Revaluation Deadline"}, expect_dates={"20-08-2026"}, min_dates=1, max_dates=3)
_add(id="gap_convocation", category="gaps", text="Date: 1 Nov 2026\nConvocation ceremony will be held on 15 December 2026.", expect_types={"Convocation Date"}, expect_dates={"15-12-2026"}, min_dates=1, max_dates=3)
_add(id="gap_thesis", category="gaps", text="Date: 1 Mar 2026\nThesis must be submitted by 30 April 2026.", expect_types={"Thesis Submission Deadline"}, expect_dates={"30-04-2026"}, min_dates=1, max_dates=3)
_add(id="gap_supply_exam", category="gaps", text="Date: 1 May 2026\nSupplementary examination will be held on 10 June 2026.", expect_types={"Supplementary Exam Date"}, expect_dates={"10-06-2026"}, min_dates=1, max_dates=3)
_add(id="gap_internship_start", category="gaps", text="Date: 1 Jun 2026\nInternship begins on 01 July 2026.", expect_types={"Internship Start Date"}, expect_dates={"01-07-2026"}, min_dates=1, max_dates=3)
_add(id="gap_offer_accept", category="gaps", text="Date: 1 Sep 2026\nAccept the offer by 15 September 2026.", expect_types={"Offer Acceptance Deadline"}, expect_dates={"15-09-2026"}, min_dates=1, max_dates=3)
_add(id="gap_visa", category="gaps", text="Date: 1 Jan 2026\nVisa application must be filed before 28 February 2026.", expect_types={"Visa Deadline"}, expect_dates={"28-02-2026"}, min_dates=1, max_dates=3)
_add(id="gap_passport", category="gaps", text="Date: 1 Feb 2026\nSubmit passport copies by 20 February 2026.", expect_types={"Passport Submission Deadline"}, expect_dates={"20-02-2026"}, min_dates=1, max_dates=3)
_add(id="gap_medical", category="gaps", text="Date: 1 Mar 2026\nMedical certificate must be submitted by 15 March 2026.", expect_types={"Medical Certificate Deadline"}, expect_dates={"15-03-2026"}, min_dates=1, max_dates=3)
_add(id="gap_attendance", category="gaps", text="Date: 1 Apr 2026\nAttendance shortage must be cleared before 10 April 2026.", expect_types={"Attendance Deadline"}, expect_dates={"10-04-2026"}, min_dates=1, max_dates=3)
_add(id="gap_id_card", category="gaps", text="Date: 1 Jul 2026\nCollect ID cards on 05 July 2026.", expect_types={"ID Card Collection Date"}, expect_dates={"05-07-2026"}, min_dates=1, max_dates=3)
_add(id="gap_bus_pass", category="gaps", text="Date: 1 Jul 2026\nApply for bus pass before 20 July 2026.", expect_types={"Bus Pass Deadline"}, expect_dates={"20-07-2026"}, min_dates=1, max_dates=3)
_add(id="gap_alumni", category="gaps", text="Date: 1 Dec 2026\nAlumni meet is scheduled on 20 December 2026.", expect_types={"Alumni Meet Date"}, expect_dates={"20-12-2026"}, min_dates=1, max_dates=3)
_add(id="gap_webinar", category="gaps", text="Date: 1 Aug 2026\nJoin the webinar on 12 August 2026.", expect_types={"Webinar Date"}, expect_dates={"12-08-2026"}, min_dates=1, max_dates=3)
_add(id="gap_certificate", category="gaps", text="Date: 1 Sep 2026\nCertificates can be collected from 10 September 2026.", expect_types={"Certificate Collection Date"}, expect_dates={"10-09-2026"}, min_dates=1, max_dates=3)
_add(id="gap_notification_date", category="gaps", text="Notification date: 08 August 2026\nApplications close later.", expect_types={"Notification Date"}, expect_dates={"08-08-2026"}, min_dates=1, max_dates=2)
_add(id="gap_circular_date", category="gaps", text="Circular date: 09 August 2026\nPlease note the schedule.", expect_types={"Circular Date"}, expect_dates={"09-08-2026"}, min_dates=1, max_dates=2)
_add(id="gap_issue_date", category="gaps", text="Issue date: 11 August 2026\nThis notice is issued for information.", expect_types={"Issue Date"}, expect_dates={"11-08-2026"}, min_dates=1, max_dates=2)
_add(id="gap_application_starts", category="gaps", text="Date: 1 Jun 2026\nApplications start on 05 June 2026.", expect_types={"Application Starts"}, expect_dates={"05-06-2026"}, min_dates=1, max_dates=3)
_add(id="gap_application_deadline", category="gaps", text="Date: 1 Jun 2026\nApplication deadline is 30 June 2026.", expect_types={"Application Deadline"}, expect_dates={"30-06-2026"}, min_dates=1, max_dates=3)
_add(id="gap_approval", category="gaps", text="Date: 1 Jul 2026\nManager approval must be obtained by 25 July 2026.", expect_types={"Approval Deadline"}, expect_dates={"25-07-2026"}, min_dates=1, max_dates=3)
_add(id="gap_final_deadline", category="gaps", text="Date: 1 Aug 2026\nFinal deadline is 31 August 2026.", expect_types={"Final Deadline"}, expect_dates={"31-08-2026"}, min_dates=1, max_dates=3)
_add(id="gap_registration_starts", category="gaps", text="Date: 1 Jul 2026\nRegistration starts on 05 July 2026.", expect_types={"Registration Starts"}, expect_dates={"05-07-2026"}, min_dates=1, max_dates=3)
_add(id="gap_exam_schedule", category="gaps", text="Date: 1 Apr 2026\nExam schedule: 20 April 2026.", expect_types={"Exam Schedule"}, expect_dates={"20-04-2026"}, min_dates=1, max_dates=3)
_add(id="gap_workshop", category="gaps", text="Date: 1 Nov 2026\nWorkshop on AI scheduled on 08 December 2026.", expect_types={"Workshop Date"}, expect_dates={"08-12-2026"}, min_dates=1, max_dates=3)

assert len(EXPANDED_FIXTURES) >= 40
