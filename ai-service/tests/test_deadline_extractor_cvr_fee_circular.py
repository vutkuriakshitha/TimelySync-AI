"""Regression: CVR tuition-fee circular must not treat academic year as a deadline.

Bug: dateparser turned \"2026-27\" into 27-07-2026 (invented current month),
missed the real fee deadline 15-08-2026, and suggested Pay Fee for the fake date.
"""

from __future__ import annotations

import unittest

from app.ml.deadline_extractor import extract_deadlines

CVR_FEE_CIRCULAR = """
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
"""


class CvrFeeCircularDeadlineExtractionTests(unittest.TestCase):
    def setUp(self):
        self.result = extract_deadlines(CVR_FEE_CIRCULAR, document_name="cvr_fee_circular.pdf")

    def test_exactly_two_dates(self):
        self.assertEqual(
            self.result.totalDeadlines,
            2,
            f"Expected exactly 2 dates, got {self.result.totalDeadlines}: "
            f"{[(d.deadlineType, d.date, d.dateOriginal) for d in self.result.deadlines]}",
        )

    def test_document_date(self):
        doc = next(d for d in self.result.deadlines if d.deadlineType == "Document Date")
        self.assertEqual(doc.date, "29-07-2026")

    def test_fee_deadline_is_15_august(self):
        fee = next(
            d for d in self.result.deadlines if d.deadlineType == "Fee Payment Deadline"
        )
        self.assertEqual(fee.date, "15-08-2026")
        self.assertIn("15-08-2026", fee.dateOriginal.replace(" ", "") or fee.originalSentence)

    def test_academic_year_not_parsed_as_deadline(self):
        dates = {d.date for d in self.result.deadlines}
        self.assertNotIn("27-07-2026", dates)
        originals = {(d.dateOriginal or "").strip().lower() for d in self.result.deadlines}
        self.assertNotIn("2026-27", originals)

    def test_suggested_task_uses_real_fee_deadline(self):
        self.assertGreaterEqual(len(self.result.suggestedTasks), 1)
        task = self.result.suggestedTasks[0]
        self.assertEqual(task.dueDate, "2026-08-15")
        self.assertEqual(task.dueDateDisplay, "15 August 2026")
        self.assertIn("fee", task.title.lower())


if __name__ == "__main__":
    unittest.main()
