"""Non-rule helpers for deadline extraction: meta types and task titles.

Type / document classification is ML-only (see deadline_ml.py).
This module only stores display/action metadata keyed by ML labels.
"""

from __future__ import annotations

META_TYPES = {
    "Document Date",
    "Issue Date",
    "Notification Date",
    "Circular Date",
    "Holiday",
    "Registration Closed",
    "Policy Effective Date",
}

TASK_TITLES: dict[str, str] = {
    "Quiz Deadline": "Complete Quiz Before Deadline",
    "Quiz Date": "Prepare for Quiz",
    "Lab Deadline": "Submit Lab Work / Report",
    "Lab Schedule": "Attend Lab Session",
    "Viva Date": "Prepare for Viva / Oral Exam",
    "Course Registration Deadline": "Complete Course Registration",
    "Course Registration Opens": "Start Course Registration",
    "Hackathon Registration Deadline": "Register for Hackathon",
    "Hackathon Date": "Attend Hackathon",
    "Competition Deadline": "Register / Submit for Competition",
    "Competition Date": "Attend Competition",
    "Club Event Date": "Attend Club Event",
    "Sports Event Date": "Attend Sports Event",
    "Cultural Event Date": "Attend Cultural Event",
    "Meeting Date": "Attend Meeting",
    "Training Date": "Attend Training Session",
    "Training Deadline": "Register for Training",
    "Event Date": "Attend Event",
    "Campus Hiring Date": "Attend Campus Hiring Drive",
    "Job Application Deadline": "Submit Job Application",
    "Tender Submission Deadline": "Submit Tender / Bid",
    "EMD Deadline": "Submit Earnest Money Deposit",
    "Tender Opening Date": "Note Tender Opening Date",
    "Timetable Update": "Review Updated Timetable",
    "Academic Calendar Event": "Note Academic Calendar Date",
    "Policy Review Date": "Review Company Policy",
    "Approval Deadline": "Obtain Required Approval",
    "Interview Date": "Attend Interview",
    "Counselling Date": "Attend Counselling",
    "Orientation Date": "Attend Orientation",
    "Result Date": "Check Results",
    "Verification Date": "Attend Document Verification",
    "Document Submission": "Submit Required Documents",
    "Workshop Date": "Attend Workshop",
    "Conference Date": "Attend Conference",
    "Seminar Date": "Attend Seminar",
    "Holiday": None,  # type: ignore[dict-item]
    "Registration Closed": None,  # type: ignore[dict-item]
    "Registration Deadline": "Complete Registration",
    "Late Fee Deadline": "Register with Late Fee",
    "Final Late Fee Deadline": "Final Opportunity for Registration",
    "Final Deadline": "Complete Action Before Final Deadline",
    "Assignment Deadline": "Submit Assignment",
    "Project Deadline": "Submit Project",
    "Thesis Submission Deadline": "Submit Thesis",
    "Fee Payment Deadline": "Pay Fee",
    "Payment Deadline": "Complete Payment",
    "Submission Deadline": "Submit Required Form",
    "Scholarship Deadline": "Apply for Scholarship",
    "Internship Deadline": "Apply for Internship",
    "Placement Deadline": "Register for Placement",
    "Admission Deadline": "Complete Admission",
    "Hostel Deadline": "Pay Hostel Dues",
    "Library Deadline": "Return Library Books",
    "Application Deadline": "Submit Application",
    "Correction Deadline": "Complete Online Correction",
    "Exam Date": "Prepare for Exam",
    "Admit Card Release": "Download Admit Card",
    "Hall Ticket Release": "Download Hall Ticket",
}
