#!/usr/bin/env python3 -m pytest
"""Tests for CSV-to-Markdown conversion, including UTF-8 BOM handling.

Excel always prepends a UTF-8 BOM when exporting CSV files containing
non-ASCII text (e.g. Hebrew), so that it can correctly round-trip the
encoding. charset_normalizer detects such files as plain "utf_8" (not
"utf-8-sig"), so a plain .decode("utf_8") leaves the BOM character
(U+FEFF) in the decoded string, leaking into the first cell's content.
"""

import io

from markitdown import StreamInfo
from markitdown.converters._csv_converter import CsvConverter

HEBREW_HEADER = "שם"
HEBREW_VALUE = "בדיקת תמיכה בעברית"


def _convert_csv_bytes(data: bytes, charset: str = "utf_8") -> str:
    converter = CsvConverter()
    result = converter.convert(
        io.BytesIO(data),
        StreamInfo(charset=charset, extension=".csv", mimetype="text/csv"),
    )
    return result.markdown


class TestCsvBomHandling:
    def test_utf8_bom_does_not_leak_into_first_cell(self):
        csv_bytes = f"{HEBREW_HEADER},ערך\n{HEBREW_VALUE},42\n".encode("utf-8-sig")

        markdown = _convert_csv_bytes(csv_bytes)

        assert "﻿" not in markdown
        assert HEBREW_HEADER in markdown

    def test_no_bom_still_works(self):
        csv_bytes = f"{HEBREW_HEADER},ערך\n{HEBREW_VALUE},42\n".encode("utf-8")

        markdown = _convert_csv_bytes(csv_bytes)

        assert "﻿" not in markdown
        assert HEBREW_HEADER in markdown
        assert HEBREW_VALUE in markdown
