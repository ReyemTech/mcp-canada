"""Unit tests for shared/parsers.py."""

from __future__ import annotations

import csv
import io
from io import BytesIO
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import openpyxl
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_xlsx_bytes(
    headers: list[str],
    rows: list[list[Any]],
    sheet_name: str = "Sheet1",
) -> bytes:
    """Create minimal XLSX bytes using openpyxl for test fixtures."""
    wb = openpyxl.Workbook()
    ws = wb.active
    assert ws is not None
    ws.title = sheet_name
    ws.append(headers)
    for row in rows:
        ws.append(row)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _make_csv_bytes(headers: list[str], rows: list[list[Any]], bom: bool = False) -> bytes:
    """Create CSV bytes for test fixtures."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    text = buf.getvalue()
    if bom:
        text = "\ufeff" + text
    return text.encode("utf-8")


# ---------------------------------------------------------------------------
# _normalize_key
# ---------------------------------------------------------------------------


class TestNormalizeKey:
    def test_simple_header(self) -> None:
        from mcp_canada.shared.parsers import _normalize_key

        assert _normalize_key("Country of Citizenship") == "country_of_citizenship"

    def test_strips_whitespace(self) -> None:
        from mcp_canada.shared.parsers import _normalize_key

        assert _normalize_key("  Year ") == "year"

    def test_leading_digit_prefixed(self) -> None:
        from mcp_canada.shared.parsers import _normalize_key

        assert _normalize_key("123col") == "col_123col"

    def test_empty_returns_col(self) -> None:
        from mcp_canada.shared.parsers import _normalize_key

        assert _normalize_key("") == "col"

    def test_special_chars_to_underscore(self) -> None:
        from mcp_canada.shared.parsers import _normalize_key

        assert _normalize_key("a/b-c d") == "a_b_c_d"

    def test_multiple_underscores_collapsed(self) -> None:
        from mcp_canada.shared.parsers import _normalize_key

        assert _normalize_key("a  b") == "a_b"


# ---------------------------------------------------------------------------
# _mask_privacy
# ---------------------------------------------------------------------------


class TestMaskPrivacy:
    def test_double_dash_returns_none(self) -> None:
        from mcp_canada.shared.parsers import _mask_privacy

        assert _mask_privacy("--") is None

    def test_double_dash_with_whitespace_returns_none(self) -> None:
        from mcp_canada.shared.parsers import _mask_privacy

        assert _mask_privacy(" -- ") is None

    def test_numeric_string_unchanged(self) -> None:
        from mcp_canada.shared.parsers import _mask_privacy

        assert _mask_privacy("123") == "123"

    def test_int_unchanged(self) -> None:
        from mcp_canada.shared.parsers import _mask_privacy

        assert _mask_privacy(42) == 42

    def test_none_returns_none(self) -> None:
        from mcp_canada.shared.parsers import _mask_privacy

        assert _mask_privacy(None) is None


# ---------------------------------------------------------------------------
# _parse_xlsx via pandas path
# ---------------------------------------------------------------------------


class TestParseXlsxPandasPath:
    def test_uses_pandas_when_importable(self) -> None:
        """_parse_xlsx() calls pandas.read_excel when pandas is available."""
        import pandas as pd

        from mcp_canada.shared.parsers import _parse_xlsx

        content = _make_xlsx_bytes(["Year", "Count"], [[2020, 100]])
        df = pd.DataFrame([{"Year": 2020, "Count": 100}])

        with patch("pandas.read_excel", return_value=df) as mock_read:
            result = _parse_xlsx(content, sheet=0, skip_rows=0)

        mock_read.assert_called_once()
        call_args = mock_read.call_args
        # First positional arg should be a BytesIO
        assert isinstance(call_args[0][0], BytesIO)
        assert call_args[1]["sheet_name"] == 0
        assert call_args[1]["skiprows"] == 0
        assert isinstance(result, list)

    def test_parse_xlsx_pandas_normalized_keys(self) -> None:
        """_parse_xlsx_pandas returns list[dict] with normalized keys."""
        import pandas as pd

        from mcp_canada.shared.parsers import _parse_xlsx_pandas

        content = _make_xlsx_bytes(
            ["Country of Citizenship", "Total"],
            [["Canada", 1000], ["USA", "--"]],
        )
        df = pd.DataFrame(
            [
                {"Country of Citizenship": "Canada", "Total": 1000},
                {"Country of Citizenship": "USA", "Total": "--"},
            ]
        )
        with patch("pandas.read_excel", return_value=df):
            result = _parse_xlsx_pandas(content)

        assert len(result) == 2
        assert "country_of_citizenship" in result[0]
        assert "total" in result[0]
        assert result[1]["total"] is None  # '--' masked


# ---------------------------------------------------------------------------
# _parse_xlsx via openpyxl fallback
# ---------------------------------------------------------------------------


class TestParseXlsxOpenpyxlPath:
    def test_falls_back_to_openpyxl_on_pandas_import_error(self) -> None:
        """_parse_xlsx() uses openpyxl when pandas import fails."""
        content = _make_xlsx_bytes(["Year", "Count"], [[2020, 100]])

        import builtins

        real_import = builtins.__import__

        def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
            if name == "pandas":
                raise ImportError("no pandas")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            from mcp_canada.shared import parsers as parsers_mod

            # Patch _parse_xlsx_openpyxl on the module to verify it's called
            with patch.object(parsers_mod, "_parse_xlsx_openpyxl", return_value=[]) as mock_oxl:
                parsers_mod._parse_xlsx(content, sheet=0, skip_rows=0)
                mock_oxl.assert_called_once_with(content, 0, 0)

    def test_parse_xlsx_openpyxl_normalized_keys(self) -> None:
        """_parse_xlsx_openpyxl returns list[dict] with normalized keys and masked values."""
        from mcp_canada.shared.parsers import _parse_xlsx_openpyxl

        content = _make_xlsx_bytes(
            ["Country of Citizenship", "Total"],
            [["Canada", 1000], ["USA", "--"]],
        )
        result = _parse_xlsx_openpyxl(content)

        assert len(result) == 2
        assert result[0]["country_of_citizenship"] == "Canada"
        assert result[0]["total"] == 1000
        assert result[1]["total"] is None  # '--' masked

    def test_parse_xlsx_openpyxl_skip_rows(self) -> None:
        """_parse_xlsx_openpyxl with skip_rows=1 skips first row before header."""
        from mcp_canada.shared.parsers import _parse_xlsx_openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        assert ws is not None
        ws.append(["metadata row"])
        ws.append(["Year", "Count"])
        ws.append([2020, 100])
        buf = BytesIO()
        wb.save(buf)
        content = buf.getvalue()

        result = _parse_xlsx_openpyxl(content, skip_rows=1)

        assert len(result) == 1
        assert "year" in result[0]
        assert result[0]["year"] == 2020

    def test_parse_xlsx_openpyxl_sheet_by_index(self) -> None:
        """_parse_xlsx_openpyxl selects the correct sheet by index."""
        from mcp_canada.shared.parsers import _parse_xlsx_openpyxl

        wb = openpyxl.Workbook()
        ws0 = wb.active
        assert ws0 is not None
        ws0.title = "First"
        ws0.append(["A"])
        ws0.append([1])
        ws1 = wb.create_sheet("Second")
        ws1.append(["B"])
        ws1.append([2])
        buf = BytesIO()
        wb.save(buf)
        content = buf.getvalue()

        result = _parse_xlsx_openpyxl(content, sheet=1)
        assert result[0]["b"] == 2

    def test_parse_xlsx_openpyxl_empty_workbook(self) -> None:
        """_parse_xlsx_openpyxl with empty workbook returns []."""
        from mcp_canada.shared.parsers import _parse_xlsx_openpyxl

        wb = openpyxl.Workbook()
        buf = BytesIO()
        wb.save(buf)
        content = buf.getvalue()

        result = _parse_xlsx_openpyxl(content)
        assert result == []


# ---------------------------------------------------------------------------
# _parse_csv
# ---------------------------------------------------------------------------


class TestParseCsv:
    def test_bom_prefixed_csv_normalized_keys(self) -> None:
        """_parse_csv with BOM-prefixed CSV returns list[dict] with normalized keys."""
        from mcp_canada.shared.parsers import _parse_csv

        content = _make_csv_bytes(
            ["Country of Citizenship", "Year"],
            [["Canada", 2020]],
            bom=True,
        )
        result = _parse_csv(content)

        assert len(result) == 1
        assert "country_of_citizenship" in result[0]
        assert result[0]["year"] == "2020"

    def test_privacy_masking_in_csv(self) -> None:
        """_parse_csv with '--' values returns None in output."""
        from mcp_canada.shared.parsers import _parse_csv

        content = _make_csv_bytes(
            ["Name", "Count"],
            [["Alice", "--"], ["Bob", "5"]],
        )
        result = _parse_csv(content)

        assert result[0]["count"] is None
        assert result[1]["count"] == "5"


# ---------------------------------------------------------------------------
# fetch_and_parse
# ---------------------------------------------------------------------------


class TestFetchAndParse:
    @pytest.mark.asyncio
    async def test_calls_cached_fetch_and_returns_tuple(self) -> None:
        """fetch_and_parse calls cached_fetch with correct key and returns (list[dict], bool)."""
        fake_data = [{"year": 2020}]

        with patch(
            "mcp_canada.shared.parsers.cached_fetch",
            new_callable=AsyncMock,
            return_value=(fake_data, True),
        ) as mock_cf:
            from mcp_canada.shared.parsers import fetch_and_parse

            result, was_cached = await fetch_and_parse(
                "https://example.com/data.xlsx", sheet=0, skip_rows=0, ttl=86400
            )

        mock_cf.assert_called_once()
        call_key = mock_cf.call_args[0][0]
        assert "data.xlsx" in call_key
        assert result == fake_data
        assert was_cached is True

    @pytest.mark.asyncio
    async def test_routes_csv_to_parse_csv(self) -> None:
        """fetch_and_parse detects .csv suffix and routes to _parse_csv."""
        csv_bytes = _make_csv_bytes(["Year"], [[2020]])

        async def fake_cached_fetch(key: str, ttl: int, fetcher: Any) -> tuple[Any, bool]:
            data = await fetcher()
            return data, False

        mock_response = MagicMock()
        mock_response.content = csv_bytes
        mock_response.raise_for_status = MagicMock()

        with (
            patch("mcp_canada.shared.parsers.cached_fetch", side_effect=fake_cached_fetch),
            patch("httpx.AsyncClient") as mock_client_cls,
            patch("mcp_canada.shared.parsers._parse_csv", return_value=[{"year": "2020"}]) as mock_csv,
        ):
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            from mcp_canada.shared.parsers import fetch_and_parse

            result, _ = await fetch_and_parse("https://example.com/data.csv")

        mock_csv.assert_called_once_with(csv_bytes, 0)

    @pytest.mark.asyncio
    async def test_routes_xlsx_to_parse_xlsx(self) -> None:
        """fetch_and_parse detects .xlsx suffix and routes to _parse_xlsx."""
        xlsx_bytes = _make_xlsx_bytes(["Year"], [[2020]])

        async def fake_cached_fetch(key: str, ttl: int, fetcher: Any) -> tuple[Any, bool]:
            data = await fetcher()
            return data, False

        mock_response = MagicMock()
        mock_response.content = xlsx_bytes
        mock_response.raise_for_status = MagicMock()

        with (
            patch("mcp_canada.shared.parsers.cached_fetch", side_effect=fake_cached_fetch),
            patch("httpx.AsyncClient") as mock_client_cls,
            patch("mcp_canada.shared.parsers._parse_xlsx", return_value=[{"year": 2020}]) as mock_xlsx,
        ):
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            from mcp_canada.shared.parsers import fetch_and_parse

            result, _ = await fetch_and_parse("https://example.com/data.xlsx")

        mock_xlsx.assert_called_once_with(xlsx_bytes, 0, 0)
