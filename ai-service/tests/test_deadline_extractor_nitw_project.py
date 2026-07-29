"""Regression: NIT Warangal Major Project Phase-II multi-deadline circular."""

from __future__ import annotations

import unittest

from app.ml.deadline_extractor import extract_deadlines

NITW_PROJECT_CIRCULAR = """
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
Project component. Faculty guides are requested to strictly monitor the progress of their
respective batches.
"""


class NitwProjectCircularDeadlineExtractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = extract_deadlines(NITW_PROJECT_CIRCULAR, document_name="nitw_project.pdf")

    def test_key_dates_present(self):
        dates = {d.date for d in self.result.deadlines}
        self.assertTrue({"29-07-2026", "12-08-2026", "22-08-2026", "05-09-2026", "15-09-2026"} <= dates)

    def test_types_are_phase_specific(self):
        by_date = {d.date: d.deadlineType for d in self.result.deadlines}
        self.assertEqual(by_date["29-07-2026"], "Document Date")
        self.assertEqual(by_date["12-08-2026"], "Project Deadline")
        self.assertEqual(by_date["22-08-2026"], "Approval Deadline")
        self.assertEqual(by_date["05-09-2026"], "Viva Date")
        self.assertEqual(by_date["15-09-2026"], "Thesis Submission Deadline")

    def test_suggested_task_titles(self):
        tasks = {t.dueDate: t.title.lower() for t in self.result.suggestedTasks}
        self.assertTrue(any(k in tasks["2026-08-12"] for k in ("draft", "project")))
        self.assertTrue(any(k in tasks["2026-08-22"] for k in ("review", "approval", "plagiarism")))
        self.assertIn("viva", tasks["2026-09-05"])
        self.assertIn("thesis", tasks["2026-09-15"])
        for title in tasks.values():
            self.assertNotIn("seminar", title)
            self.assertNotIn("pay fee", title)


if __name__ == "__main__":
    unittest.main()
