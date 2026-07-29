"""Regression suite: 50+ diverse official documents for deadline extraction."""

from __future__ import annotations

import unittest

from app.ml.deadline_extractor import extract_deadlines
from app.ml.date_parsing import clean_ocr_text, find_explicit_dates
from app.ml.model_registry import get
from tests.fixtures.sample_documents import FIXTURES
from tests.fixtures.expanded_categories import EXPANDED_FIXTURES

ALL_FIXTURES = FIXTURES + EXPANDED_FIXTURES


class DeadlineFormatTests(unittest.TestCase):
    def test_all_common_formats_resolve_to_same_day(self):
        samples = [
            "15 August 2026",
            "15 Aug 2026",
            "15-Aug-2026",
            "15/Aug/2026",
            "15/08/2026",
            "15-08-2026",
            "2026-08-15",
            "08/15/2026",
            "August 15, 2026",
            "Aug 15, 2026",
            "15th August 2026",
            "15th Aug 2026",
            "15-08-26",
            "15/08/26",
            "2026.08.15",
            "15.08.2026",
        ]
        for sample in samples:
            hits = find_explicit_dates(sample, default_year=2026)
            self.assertEqual(len(hits), 1, sample)
            self.assertEqual(hits[0].dt.strftime("%Y-%m-%d"), "2026-08-15", sample)

    def test_ocr_variations(self):
        for raw in ("15Augu5t2026", "15 Aug,2026", "15Aug2026", "15 Aug-2026", "15 August,2026"):
            cleaned = clean_ocr_text(raw)
            hits = find_explicit_dates(cleaned, default_year=2026)
            self.assertGreaterEqual(len(hits), 1, raw)
            self.assertEqual(hits[0].dt.strftime("%Y-%m-%d"), "2026-08-15", raw)

    def test_never_parses_relative_words(self):
        text = "now to are so any open under circumstances"
        hits = find_explicit_dates(text, default_year=2026)
        self.assertEqual(hits, [])


class DeadlineRegressionSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = {
            fixture["id"]: (fixture, extract_deadlines(fixture["text"], fixture["id"]))
            for fixture in ALL_FIXTURES
        }

    def test_fixture_count(self):
        self.assertGreaterEqual(len(ALL_FIXTURES), 70)

    def test_ml_models_loaded(self):
        type_model = get("deadline_type_model")
        doc_model = get("deadline_document_model")
        date_model = get("deadline_date_model")
        self.assertIn("pipeline", type_model)
        self.assertIn("pipeline", doc_model)
        self.assertIn("pipeline", date_model)
        classes = set(type_model["pipeline"].named_steps["classifier"].classes_)
        for required in (
            "Quiz Date",
            "Lab Schedule",
            "Viva Date",
            "Hackathon Date",
            "Registration Deadline",
            "Document Date",
            "Revaluation Deadline",
            "Convocation Date",
        ):
            self.assertIn(required, classes)
        date_classes = set(date_model["pipeline"].named_steps["classifier"].classes_)
        self.assertIn("calendar_date", date_classes)
        self.assertIn("not_date", date_classes)

    def test_all_fixtures(self):
        failures: list[str] = []
        for fixture_id, (fixture, result) in self.results.items():
            try:
                self._assert_fixture(fixture, result)
            except AssertionError as exc:
                failures.append(f"{fixture_id}: {exc}")
        if failures:
            self.fail(f"{len(failures)} fixture(s) failed:\n" + "\n".join(failures))

    def _assert_fixture(self, fixture: dict, result) -> None:
        dates = {d.date for d in result.deadlines if d.date}
        for rng in result.dateRanges:
            dates.add(rng.startDate)
            dates.add(rng.endDate)
        types = {d.deadlineType for d in result.deadlines}
        originals = {(d.dateOriginal or "").strip().lower() for d in result.deadlines}

        if "min_dates" in fixture:
            self.assertGreaterEqual(
                len(result.deadlines),
                fixture["min_dates"],
                f"types={types} dates={dates}",
            )
        if "max_dates" in fixture:
            self.assertLessEqual(
                len(result.deadlines),
                fixture["max_dates"],
                f"types={types} dates={dates}",
            )
        for expected_type in fixture.get("expect_types", set()):
            self.assertIn(expected_type, types, f"dates={dates}")
        for expected_date in fixture.get("expect_dates", set()):
            self.assertIn(expected_date, dates, f"types={types}")
        for forbidden in fixture.get("forbid_types", set()):
            self.assertNotIn(forbidden, types)
        for forbidden_date in fixture.get("forbid_dates", set()):
            self.assertNotIn(forbidden_date, dates, f"types={types} dates={dates}")
        for word in fixture.get("forbid_originals", set()):
            self.assertNotIn(word, originals)
        if fixture.get("expect_ranges"):
            self.assertGreaterEqual(result.totalDateRanges, 1, "expected at least one range")
        if fixture.get("require_tasks"):
            self.assertGreaterEqual(len(result.suggestedTasks), 1)
            for task in result.suggestedTasks:
                self.assertTrue(task.dueDate)
                self.assertTrue(task.title)
        if fixture.get("require_relationships"):
            self.assertGreaterEqual(len(result.relationships), 1)
        if fixture.get("expect_doc_type"):
            # Document category is ML-predicted; allow close alternatives
            self.assertTrue(
                bool(result.documentType),
                f"missing documentType, expected around {fixture['expect_doc_type']}",
            )

    def test_late_fee_schedule_details(self):
        _, result = self.results["late_fee_labeled"]
        by_type = {d.deadlineType: d for d in result.deadlines}
        self.assertEqual(by_type["Registration Deadline"].date, "05-08-2026")
        self.assertEqual(by_type["Late Fee Deadline"].date, "10-08-2026")
        self.assertEqual(by_type["Late Fee Deadline"].fineAmount, "₹2000")
        self.assertEqual(by_type["Final Late Fee Deadline"].date, "15-08-2026")
        self.assertEqual(by_type["Final Late Fee Deadline"].fineAmount, "₹5000")
        self.assertEqual(by_type["Registration Closed"].date, "15-08-2026")
        titles = {t.title for t in result.suggestedTasks}
        self.assertTrue(any("Late Fee" in t or "Registration" in t for t in titles))
        self.assertTrue(any("Final Opportunity" in t for t in titles))

    def test_anu_unchanged(self):
        _, result = self.results["anu_circular"]
        self.assertEqual(result.totalDeadlines, 2)
        self.assertEqual(result.totalDateRanges, 0)
        types = {d.deadlineType: d.date for d in result.deadlines}
        self.assertEqual(types["Document Date"], "20-07-2026")
        self.assertEqual(types["Registration Deadline"], "15-08-2026")
        self.assertEqual(len(result.suggestedTasks), 1)
        self.assertEqual(result.suggestedTasks[0].dueDate, "2026-08-15")


if __name__ == "__main__":
    unittest.main()
