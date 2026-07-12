"""Extract plain text from uploaded PDFs and images for deadline analysis."""

from __future__ import annotations

import io
import logging
from typing import Optional

logger = logging.getLogger("ai-service.ocr")

_MAX_PAGES = 50
_MIN_TEXT_CHARS = 20


def _extract_pdf_text(data: bytes) -> str:
    import pdfplumber

    parts: list[str] = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for i, page in enumerate(pdf.pages):
            if i >= _MAX_PAGES:
                break
            text = page.extract_text() or ""
            if text.strip():
                parts.append(text.strip())
    return "\n\n".join(parts)


def _ocr_image_bytes(data: bytes) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "Image OCR requires Pillow and pytesseract. Install system Tesseract OCR as well."
        ) from exc

    image = Image.open(io.BytesIO(data))
    return pytesseract.image_to_string(image)


def _ocr_pdf_pages(data: bytes) -> str:
    try:
        import pytesseract
        from pdf2image import convert_from_bytes
    except ImportError as exc:
        raise RuntimeError(
            "Scanned PDF OCR requires pdf2image and pytesseract with Poppler installed."
        ) from exc

    images = convert_from_bytes(data, first_page=1, last_page=_MAX_PAGES)
    parts: list[str] = []
    for image in images:
        parts.append(pytesseract.image_to_string(image))
    return "\n\n".join(p for p in parts if p.strip())


def extract_text(filename: str, content_type: Optional[str], data: bytes) -> dict:
    """Return OCR/text-extraction output with metadata."""
    if not data:
        raise ValueError("Uploaded file is empty")

    name = (filename or "").lower()
    mime = (content_type or "").lower()

    is_pdf = name.endswith(".pdf") or mime == "application/pdf"
    is_image = (
        name.endswith((".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"))
        or mime.startswith("image/")
    )

    if not is_pdf and not is_image:
        raise ValueError("Unsupported file type. Upload a PDF or image (PNG, JPG, WEBP).")

    method = "embedded_text"
    text = ""

    if is_pdf:
        try:
            text = _extract_pdf_text(data)
        except Exception as exc:
            logger.warning("PDF text extraction failed: %s", exc)
            text = ""

        if len(text.strip()) < _MIN_TEXT_CHARS:
            method = "ocr"
            try:
                text = _ocr_pdf_pages(data)
            except Exception as exc:
                if text.strip():
                    method = "embedded_text_partial"
                    logger.warning("PDF OCR fallback failed, using partial embedded text: %s", exc)
                else:
                    raise RuntimeError(
                        "Could not extract text from this PDF. "
                        "If it is scanned, install Tesseract OCR and Poppler."
                    ) from exc
    else:
        method = "ocr"
        text = _ocr_image_bytes(data)

    cleaned = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if len(cleaned) < 5:
        raise ValueError("No readable text was found in the uploaded document.")

    page_count = max(1, cleaned.count("\f") + 1) if "\f" in cleaned else max(1, cleaned.count("\n\n") // 3 + 1)

    return {
        "text": cleaned,
        "extractionMethod": method,
        "characterCount": len(cleaned),
        "estimatedPages": page_count,
    }
