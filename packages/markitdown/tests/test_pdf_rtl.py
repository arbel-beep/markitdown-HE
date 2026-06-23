#!/usr/bin/env python3 -m pytest
"""Tests for RTL (Hebrew/Arabic) text handling in PDF conversion.

pdfminer.high_level.extract_text() mangles RTL text layout (reversed
words, fragmented lines) for some PDFs, while pdfplumber's per-page
extract_text() handles the same PDF correctly. The whole-document
pdfminer fallback (used when no page is form-style) must not discard
already-correct RTL text in favor of pdfminer's mangled output.
"""

import io
import os
from unittest.mock import patch, MagicMock

from markitdown import MarkItDown, StreamInfo
from markitdown.converters._pdf_converter import _is_rtl_dominant

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files")

HEBREW_SENTENCE = "המחלקה להנדסת תעשייה ונהול הפקולטה למדעי ההנדסה"
MANGLED_HEBREW = "הסדנהה\n\nיעדמל\n\nהטלוקפה"  # simulates pdfminer's broken output


def _make_plain_hebrew_page(text: str):
    page = MagicMock()
    page.width = 612
    page.close = MagicMock()
    page.extract_words.return_value = [
        {"text": text, "x0": 50, "x1": 550, "top": 10, "bottom": 20},
    ]
    page.extract_text.return_value = text
    return page


def _mock_pdfplumber_open(pages):
    def mock_open(stream):
        mock_pdf = MagicMock()
        mock_pdf.pages = pages
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        return mock_pdf

    return mock_open


class TestRtlDetection:
    def test_hebrew_text_is_rtl_dominant(self):
        assert _is_rtl_dominant(HEBREW_SENTENCE) is True

    def test_english_text_is_not_rtl_dominant(self):
        assert _is_rtl_dominant("This is a long paragraph of plain text.") is False

    def test_empty_text_is_not_rtl_dominant(self):
        assert _is_rtl_dominant("") is False


class TestRtlPdfConversion:
    def test_rtl_plain_pdf_uses_pdfplumber_text_not_mangled_pdfminer(self):
        """Plain-text Hebrew PDFs must use pdfplumber's correct extraction,
        not pdfminer's whole-document fallback which mangles RTL layout."""
        pages = [_make_plain_hebrew_page(HEBREW_SENTENCE) for _ in range(2)]

        with patch(
            "markitdown.converters._pdf_converter.pdfplumber"
        ) as mock_pdfplumber, patch(
            "markitdown.converters._pdf_converter.pdfminer"
        ) as mock_pdfminer:
            mock_pdfplumber.open.side_effect = _mock_pdfplumber_open(pages)
            mock_pdfminer.high_level.extract_text.return_value = MANGLED_HEBREW

            md = MarkItDown()
            buf = io.BytesIO(b"fake pdf content")
            result = md.convert_stream(
                buf,
                stream_info=StreamInfo(extension=".pdf", mimetype="application/pdf"),
            )

        assert HEBREW_SENTENCE in result.text_content
        assert "הסדנהה" not in result.text_content
        assert not mock_pdfminer.high_level.extract_text.called
