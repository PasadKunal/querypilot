"""
Tests for the CSV/Excel parsing helper.

No database or network calls needed here. We feed raw bytes directly to
parse_csv() and check that column names are cleaned, types are inferred
correctly, and edge cases do not crash.
"""

from __future__ import annotations

import io

import pandas as pd
import pytest

from datasets.csv_processor import clean_column_name, parse_csv


class TestCleanColumnName:
    def test_spaces_become_underscores(self):
        assert clean_column_name("First Name") == "first_name"

    def test_leading_digit_gets_prefix(self):
        assert clean_column_name("2024_revenue").startswith("col_")

    def test_special_chars_stripped(self):
        assert clean_column_name("price ($)") == "price"

    def test_consecutive_underscores_collapsed(self):
        result = clean_column_name("order  date")
        assert "__" not in result

    def test_empty_string_returns_col(self):
        assert clean_column_name("") == "col"

    def test_long_name_truncated(self):
        assert len(clean_column_name("a" * 100)) <= 63


class TestParseCsvTypes:
    def _make_csv(self, rows: list[str]) -> bytes:
        return "\n".join(rows).encode()

    def test_integer_column(self):
        csv = self._make_csv(["id,name", "1,Alice", "2,Bob", "3,Carol"])
        _, _, types = parse_csv(csv)
        assert types["id"] == "BIGINT"
        assert types["name"] == "TEXT"

    def test_float_column(self):
        csv = self._make_csv(["price", "9.99", "14.99", "24.99"])
        _, _, types = parse_csv(csv)
        assert types["price"] == "NUMERIC"

    def test_boolean_column(self):
        csv = self._make_csv(["active", "true", "false", "true"])
        _, _, types = parse_csv(csv)
        assert types["active"] == "BOOLEAN"

    def test_row_count_matches(self):
        csv = self._make_csv(["x", "1", "2", "3", "4", "5"])
        _, rows, _ = parse_csv(csv)
        assert len(rows) == 5

    def test_null_values_become_none(self):
        csv = self._make_csv(["name,score", "Alice,90", "Bob,", "Carol,85"])
        _, rows, _ = parse_csv(csv)
        assert rows[1]["score"] is None

    def test_bom_utf8_handled(self):
        csv = b"\xef\xbb\xbfname,age\nAlice,30\n"
        headers, rows, _ = parse_csv(csv)
        assert headers[0] == "name"

    def test_duplicate_headers_deduplicated(self):
        csv = self._make_csv(["name,name,name", "a,b,c"])
        headers, _, _ = parse_csv(csv)
        assert len(set(headers)) == len(headers)

    def test_empty_csv_raises(self):
        csv = b"name,age\n"
        with pytest.raises(ValueError):
            parse_csv(csv)

    def test_excel_bytes_parsed(self):
        df = pd.DataFrame({"product": ["Widget", "Gadget"], "price": [9.99, 19.99]})
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        buf.seek(0)
        headers, rows, types = parse_csv(buf.read(), filename="test.xlsx")
        assert "product" in headers
        assert types["price"] == "NUMERIC"
        assert len(rows) == 2
