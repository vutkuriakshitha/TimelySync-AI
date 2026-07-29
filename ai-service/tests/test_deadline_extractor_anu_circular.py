"""Regression tests: APEX NATIONAL UNIVERSITY odd-semester registration circular.

The old pipeline used dateparser.search_dates with RELATIVE_BASE=now, which
turned words like "now", "to", "are", "so", "any" into fake deadlines.
These tests lock the strict extractor to exactly two genuine dates.
"""

from __future__ import annotations

import unittest

from app.ml.deadline_extractor import clean_ocr_text, extract_deadlines

ANU_CIRCULAR = """
APEX NATIONAL UNIVERSITY
University Road, Sector 5, New Delhi - 110001

REF: ANU/EXAM/2026/041
Date: 20 July 2026

CIRCULAR: ODD SEMESTER EXAMINATION REGISTRATION

This is to inform all undergraduate and postgraduate students that the registration portal for the upcoming odd semester examinations is now officially open.

All eligible students must log in to the university student portal using their official credentials to complete the registration process.

Please ensure that all your academic details, elective choices, and personal information are correctly updated before final submission.

It is mandatory to clear any pending tuition or hostel fee dues to unlock the examination registration module.

The administration has noticed discrepancies in elective subject selection in previous years, so students are advised to cross-check their curriculum requirements carefully.

Failure to complete this process will result in the non-issuance of the examination admit card, preventing the student from appearing in the assessments.

All students must complete their examination registration by 15 August 2026.

The online portal will automatically stop accepting new submissions after this designated time, and no manual applications will be entertained under any circumstances.
"""


class AnuCircularDeadlineExtractionTests(unittest.TestCase):
    def setUp(self):
        self.result = extract_deadlines(ANU_CIRCULAR, document_name="anu_circular.pdf")

    def test_exactly_two_dates_extracted(self):
        self.assertEqual(
            self.result.totalDeadlines,
            2,
            f"Expected exactly 2 dates, got {self.result.totalDeadlines}: "
            f"{[(d.deadlineType, d.date, d.dateOriginal) for d in self.result.deadlines]}",
        )
        self.assertEqual(len(self.result.deadlines), 2)

    def test_no_date_ranges(self):
        self.assertEqual(self.result.totalDateRanges, 0)
        self.assertEqual(self.result.dateRanges, [])

    def test_document_date(self):
        doc = next(d for d in self.result.deadlines if d.deadlineType == "Document Date")
        self.assertEqual(doc.date, "20-07-2026")

    def test_registration_deadline(self):
        reg = next(
            d for d in self.result.deadlines if d.deadlineType == "Registration Deadline"
        )
        self.assertEqual(reg.date, "15-08-2026")
        self.assertIn("by 15 August 2026", reg.originalSentence)

    def test_forbidden_types_not_present(self):
        types = {d.deadlineType for d in self.result.deadlines}
        forbidden = {
            "Exam Date",
            "Fee Payment Deadline",
            "Admit Card Date",
            "Result Date",
            "Event Date",
            "Important Date",
            "Other",
        }
        self.assertTrue(types.isdisjoint(forbidden), f"Unexpected types: {types}")

    def test_no_hallucinated_word_dates(self):
        originals = {(d.dateOriginal or "").strip().lower() for d in self.result.deadlines}
        for word in ("to", "now", "are", "so", "any", "august 2026"):
            self.assertNotIn(word, originals)

        dates = {d.date for d in self.result.deadlines}
        # Old relative-base hallucinations clustered around "today"
        for fake in ("30-07-2026", "28-07-2026", "02-08-2026", "01-08-2026", "28-08-2026"):
            self.assertNotIn(fake, dates)

    def test_suggested_task_uses_registration_deadline(self):
        self.assertEqual(len(self.result.suggestedTasks), 1)
        task = self.result.suggestedTasks[0]
        self.assertEqual(task.title, "Complete Odd Semester Examination Registration")
        self.assertEqual(task.category, "ACADEMIC")
        self.assertEqual(task.priority, "MEDIUM")
        self.assertEqual(task.dueDate, "2026-08-15")
        self.assertEqual(task.dueDateDisplay, "15 August 2026")
        self.assertIn("examination registration before the deadline", task.description.lower())

    def test_clean_ocr_does_not_invent_text(self):
        cleaned = clean_ocr_text(ANU_CIRCULAR)
        self.assertIn("15 August 2026", cleaned)
        self.assertIn("Date: 20 July 2026", cleaned)
        self.assertNotIn("30-07-2026", cleaned)


if __name__ == "__main__":
    unittest.main()
