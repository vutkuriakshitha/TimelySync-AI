"""API + PDF integration tests for deadline extraction."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.ml.deadline_extractor import extract_deadlines
from app.ml.ocr_reader import extract_text
from app.ml.model_registry import reload

# Minimal PDF with embedded Helvetica text
_MIN_PDF = b"""%PDF-1.4
1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj
2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj
3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj
4 0 obj<< /Length 140 >>stream
BT /F1 12 Tf 72 720 Td (Date: 20 July 2026) Tj 0 -24 Td (Registration by 15 August 2026.) Tj ET
endstream
endobj
5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000458 00000 n 
trailer<< /Size 6 /Root 1 0 R >>
startxref
537
%%EOF"""


class DeadlineApiIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        reload()
        cls.client = TestClient(app)
        cls.headers = {}
        if settings.internal_api_key:
            cls.headers["x-internal-api-key"] = settings.internal_api_key

    def test_health(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body.get("status"), "ok")
        self.assertTrue(body.get("modelsReady"))

    def test_deadline_extraction_endpoint_uses_ml(self):
        payload = {
            "text": "Date: 20 July 2026\nRegistration by 15 August 2026.",
            "documentName": "api-test.txt",
        }
        resp = self.client.post(
            "/predict/deadline-extraction",
            json=payload,
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 200, resp.text)
        data = resp.json()
        self.assertEqual(data["modelVersion"], "deadline-ml-v10")
        types = {d["deadlineType"]: d for d in data["deadlines"]}
        self.assertIn("Document Date", types)
        self.assertIn("Registration Deadline", types)
        self.assertEqual(types["Document Date"]["date"], "20-07-2026")
        self.assertEqual(types["Registration Deadline"]["date"], "15-08-2026")
        for d in data["deadlines"]:
            self.assertIn("ML", d.get("explanation") or "")
        self.assertGreaterEqual(len(data.get("suggestedTasks") or []), 1)

    def test_pdf_embedded_text_then_extract(self):
        ocr = extract_text("notice.pdf", "application/pdf", _MIN_PDF)
        self.assertEqual(ocr["extractionMethod"], "embedded_text")
        self.assertGreaterEqual(ocr["characterCount"], 20)
        self.assertIn("15 August 2026", ocr["text"])
        result = extract_deadlines(ocr["text"], "notice.pdf")
        types = {d.deadlineType: d.date for d in result.deadlines}
        self.assertEqual(types.get("Document Date"), "20-07-2026")
        self.assertEqual(types.get("Registration Deadline"), "15-08-2026")
        self.assertTrue(all("ML" in (d.explanation or "") for d in result.deadlines))

    def test_document_deadlines_multipart(self):
        resp = self.client.post(
            "/predict/document-deadlines",
            headers=self.headers,
            files={"file": ("notice.pdf", _MIN_PDF, "application/pdf")},
        )
        self.assertEqual(resp.status_code, 200, resp.text)
        data = resp.json()
        self.assertEqual(data["modelVersion"], "deadline-ml-v10")
        self.assertEqual(data.get("extractionMethod"), "embedded_text")
        self.assertTrue(data.get("extractedText"))
        types = {d["deadlineType"]: d["date"] for d in data["deadlines"]}
        self.assertEqual(types.get("Registration Deadline"), "15-08-2026")

    def test_reload_models_endpoint(self):
        resp = self.client.post("/admin/reload-models", headers=self.headers)
        self.assertEqual(resp.status_code, 200, resp.text)
        body = resp.json()
        loaded = body.get("reloaded") or []
        self.assertIn("deadline_type_model", loaded)
        self.assertIn("deadline_date_model", loaded)


if __name__ == "__main__":
    unittest.main()
