"""Tests for the LLM extraction layer using a fake model (no network needed).

They check the part we own: that hallucinated or ungrounded output is rejected,
tasks are only created for actionable future dates, and the service falls back
to the classic pipeline when the LLM fails.
"""

import json
import sys
import types
import unittest
from datetime import date
from unittest import mock

from app.ml import llm_extractor
from app.ml.llm_extractor import LlmConfig, LlmError, extract_with_llm

TODAY = date(2026, 11, 9)
CFG = LlmConfig(provider="gemini", api_key="test", model="fake-model")

CIRCULAR = """\
CIRCULAR No. ABC/2026/114
Date: 9 November 2026

Subject: Workshop on AI and Cloud Computing

All final year students are informed that a workshop on AI and Cloud Computing
will be held on 20 November 2026 from 11:00 AM to 2:00 PM at Seminar Hall, Block A.
Interested students must register before 17 November 2026.
Results of the previous workshop were announced on 25 October 2026.
"""


def fake_llm(items, **extra):
    payload = {"documentType": "Event circular", "summary": "Workshop notice", "items": items}
    payload.update(extra)
    return lambda cfg, text: json.dumps(payload)


GOOD_ITEMS = [
    {
        "purpose": "Circular issue date", "kind": "document_date", "date": "2026-11-09",
        "evidence": "Date: 9 November 2026", "category": "EVENT", "priority": "LOW",
        "taskTitle": None, "confidence": 0.95,
    },
    {
        "purpose": "Workshop registration deadline", "kind": "deadline", "date": "2026-11-17",
        "evidence": "Interested students must register before 17 November 2026.",
        "category": "OPPORTUNITY", "priority": "HIGH",
        "taskTitle": "Register for the AI and Cloud Computing Workshop",
        "relatedEvent": "AI and Cloud Computing Workshop", "confidence": 0.92,
    },
    {
        "purpose": "AI and Cloud Computing Workshop", "kind": "event", "date": "2026-11-20",
        "evidence": "will be held on 20 November 2026 from 11:00 AM to 2:00 PM at Seminar Hall, Block A.",
        "category": "EVENT", "priority": "MEDIUM", "taskTitle": "Attend the AI and Cloud Computing Workshop",
        "relatedEvent": "AI and Cloud Computing Workshop", "confidence": 0.9,
    },
    {
        "purpose": "Previous workshop results", "kind": "info", "date": "2026-10-25",
        "evidence": "Results of the previous workshop were announced on 25 October 2026.",
        "category": "EVENT", "priority": "LOW", "taskTitle": None, "confidence": 0.9,
    },
]


class LlmExtractorTests(unittest.TestCase):
    def run_extract(self, items, text=CIRCULAR, **extra):
        return extract_with_llm(text, "c.pdf", config=CFG, llm_call=fake_llm(items, **extra), today=TODAY)

    def test_generic_circular_gets_correct_dates_and_only_actionable_tasks(self):
        res = self.run_extract(GOOD_ITEMS)
        self.assertEqual(res.totalDeadlines, 4)
        titles = sorted(t.title for t in res.suggestedTasks)
        self.assertEqual(
            titles,
            ["Attend the AI and Cloud Computing Workshop",
             "Register for the AI and Cloud Computing Workshop"],
        )
        by_purpose = {d.purpose: d for d in res.deadlines}
        self.assertFalse(by_purpose["Circular issue date"].isActionable)
        self.assertEqual(by_purpose["Circular issue date"].deadlineType, "Document Date")
        self.assertFalse(by_purpose["Previous workshop results"].isActionable)
        deadline = by_purpose["Workshop registration deadline"]
        self.assertEqual(deadline.dateIso, "2026-11-17")
        self.assertEqual(deadline.date, "17-11-2026")
        self.assertEqual(deadline.relatedEvent, "AI and Cloud Computing Workshop")
        self.assertIn("llm-gemini-fake-model", res.modelVersion)

    def test_hallucinated_evidence_is_dropped(self):
        fake = {
            "purpose": "Fee payment", "kind": "deadline", "date": "2026-12-01",
            "evidence": "Pay the semester fee by 1 December 2026.",
            "taskTitle": "Pay fee", "confidence": 0.9,
        }
        res = self.run_extract(GOOD_ITEMS[:2] + [fake])
        self.assertEqual(res.totalDeadlines, 2)
        self.assertIn("1 unverifiable", res.summary)
        self.assertNotIn("Pay fee", [t.title for t in res.suggestedTasks])

    def test_date_not_written_in_document_is_dropped(self):
        wrong = dict(GOOD_ITEMS[1], date="2026-12-30")  # quote is real, date is not
        res = self.run_extract([wrong])
        self.assertEqual(res.totalDeadlines, 0)

    def test_date_missing_from_quoted_sentence_is_low_confidence(self):
        item = dict(GOOD_ITEMS[1], evidence="Interested students must register before the date below.",
                    date="2026-11-17")
        text = CIRCULAR + "\nInterested students must register before the date below.\n"
        res = self.run_extract([item], text=text)
        self.assertEqual(res.totalDeadlines, 1)
        self.assertEqual(res.deadlines[0].confidence, "Low")
        self.assertIn("verify", res.deadlines[0].explanation.lower())

    def test_past_deadline_creates_no_task(self):
        res = extract_with_llm(CIRCULAR, config=CFG, llm_call=fake_llm(GOOD_ITEMS[1:3]),
                               today=date(2026, 11, 18))
        by_purpose = {d.purpose: d for d in res.deadlines}
        self.assertFalse(by_purpose["Workshop registration deadline"].isActionable)
        self.assertEqual([t.title for t in res.suggestedTasks],
                         ["Attend the AI and Cloud Computing Workshop"])

    def test_duplicates_are_merged(self):
        res = self.run_extract([GOOD_ITEMS[1], dict(GOOD_ITEMS[1])])
        self.assertEqual(res.totalDeadlines, 1)

    def test_date_range_is_reported(self):
        text = "Exams will be conducted from 3 December 2026 to 10 December 2026 for all branches."
        item = {
            "purpose": "End semester exams", "kind": "event", "date": "2026-12-03", "endDate": "2026-12-10",
            "evidence": "Exams will be conducted from 3 December 2026 to 10 December 2026 for all branches.",
            "taskTitle": "Prepare for end semester exams", "confidence": 0.9,
        }
        res = self.run_extract([item], text=text)
        self.assertEqual(res.totalDateRanges, 1)
        self.assertEqual(res.dateRanges[0].endDateIso, "2026-12-10")

    def test_invalid_values_are_sanitised(self):
        item = dict(GOOD_ITEMS[1], priority="URGENT!!", category="WEIRD", confidence="high")
        res = self.run_extract([item])
        self.assertEqual(res.deadlines[0].priority, "MEDIUM")
        self.assertEqual(res.deadlines[0].suggestedCategory, "ACADEMIC")

    def test_fenced_json_is_accepted(self):
        raw = "```json\n" + json.dumps({"items": GOOD_ITEMS[1:2]}) + "\n```"
        res = extract_with_llm(CIRCULAR, config=CFG, llm_call=lambda c, t: raw, today=TODAY)
        self.assertEqual(res.totalDeadlines, 1)

    def test_garbage_response_raises(self):
        with self.assertRaises(LlmError):
            extract_with_llm(CIRCULAR, config=CFG, llm_call=lambda c, t: "sorry, no", today=TODAY)

    def test_unconfigured_raises(self):
        with self.assertRaises(LlmError):
            extract_with_llm(CIRCULAR, config=LlmConfig())

    def test_config_from_env(self):
        env = {"LLM_PROVIDER": "groq", "LLM_API_KEY": "k", "LLM_MODEL": "m"}
        with mock.patch.dict("os.environ", env, clear=True):
            cfg = llm_extractor.load_config()
        self.assertTrue(cfg.enabled)
        self.assertEqual(cfg.provider, "openai")
        self.assertIn("groq.com", cfg.base_url)
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertFalse(llm_extractor.load_config().enabled)


class ServiceFallbackTests(unittest.TestCase):
    """extraction_service falls back to the classic pipeline instead of failing."""

    def setUp(self):
        self.classic = types.ModuleType("app.ml.deadline_extractor")
        self.classic.extract_deadlines = mock.Mock(return_value="CLASSIC")
        sys.modules.pop("app.ml.extraction_service", None)
        patcher = mock.patch.dict(sys.modules, {"app.ml.deadline_extractor": self.classic})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(sys.modules.pop, "app.ml.extraction_service", None)
        import app.ml as ml_pkg
        ml_pkg.deadline_extractor = self.classic
        from app.ml import extraction_service
        self.service = extraction_service

    def test_uses_classic_when_llm_disabled(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertEqual(self.service.extract("text"), "CLASSIC")

    def test_uses_classic_when_llm_fails(self):
        env = {"LLM_PROVIDER": "gemini", "LLM_API_KEY": "k"}
        with mock.patch.dict("os.environ", env, clear=True), mock.patch.object(
            llm_extractor, "extract_with_llm", side_effect=LlmError("429")
        ):
            self.assertEqual(self.service.extract("text"), "CLASSIC")

    def test_uses_classic_when_nothing_verified(self):
        env = {"LLM_PROVIDER": "gemini", "LLM_API_KEY": "k"}
        empty = mock.Mock(totalDeadlines=0)
        with mock.patch.dict("os.environ", env, clear=True), mock.patch.object(
            llm_extractor, "extract_with_llm", return_value=empty
        ):
            self.assertEqual(self.service.extract("text"), "CLASSIC")

    def test_returns_llm_result_when_verified(self):
        env = {"LLM_PROVIDER": "gemini", "LLM_API_KEY": "k"}
        good = mock.Mock(totalDeadlines=2)
        with mock.patch.dict("os.environ", env, clear=True), mock.patch.object(
            llm_extractor, "extract_with_llm", return_value=good
        ):
            self.assertIs(self.service.extract("text"), good)


if __name__ == "__main__":
    unittest.main()
