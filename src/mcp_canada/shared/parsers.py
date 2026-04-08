"""Shared file parser for XLSX, XLS, and CSV files from government URLs.

Public API:
    fetch_and_parse(url, sheet, skip_rows, ttl) -> (list[dict], was_cached)
"""

from __future__ import annotations

import csv
import re
from io import BytesIO, StringIO
from typing import Any

import httpx

from mcp_canada.shared.cache import cached_fetch

# Regex to collapse non-alphanumeric runs to underscores
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _normalize_key(header: str) -> str:
    """Normalize a column header to a snake_case identifier.

    Examples:
        "Country of Citizenship" -> "country_of_citizenship"
        "  Year " -> "year"
        "123col" -> "col_123col"
        "" -> "col"
        "a/b-c d" -> "a_b_c_d"
    """
    key = header.strip().lower()
    key = _NON_ALNUM.sub("_", key)
    key = key.strip("_")
    if not key:
        return "col"
    if key[0].isdigit():
        key = f"col_{key}"
    return key


def _mask_privacy(value: Any) -> Any:
    """Convert privacy-masked '--' values to None.

    Returns None for '--' strings (with optional surrounding whitespace),
    and None for pandas NaN/NaT/NA if pandas is available. All other
    values are returned unchanged.
    """
    if value is None:
        return None
    if isinstance(value, str):
        if value.strip() == "--":
            return None
        return value
    # Handle pandas NA types if pandas is available
    try:
        import pandas as pd  # noqa: PLC0415

        if pd.isna(value):
            return None
    except (ImportError, TypeError, ValueError):
        pass
    return value


def _parse_xlsx_pandas(
    content: bytes,
    sheet: str | int = 0,
    skip_rows: int = 0,
) -> list[dict[str, Any]]:
    """Parse XLSX bytes using pandas.

    Args:
        content: Raw XLSX file bytes.
        sheet: Sheet name or 0-based index.
        skip_rows: Number of rows to skip before the header row.

    Returns:
        list of dicts with normalized snake_case keys and privacy-masked values.
    """
    import pandas as pd  # noqa: PLC0415

    df = pd.read_excel(BytesIO(content), sheet_name=sheet, skiprows=skip_rows)
    # Rename columns to normalized keys
    df.columns = [_normalize_key(str(col)) for col in df.columns]
    records = df.to_dict(orient="records")
    return [{k: _mask_privacy(v) for k, v in row.items()} for row in records]


def _parse_xlsx_openpyxl(
    content: bytes,
    sheet: str | int = 0,
    skip_rows: int = 0,
) -> list[dict[str, Any]]:
    """Parse XLSX bytes using openpyxl (fallback when pandas is unavailable).

    Args:
        content: Raw XLSX file bytes.
        sheet: Sheet name or 0-based index.
        skip_rows: Number of rows to skip before the header row.

    Returns:
        list of dicts with normalized snake_case keys and privacy-masked values.
    """
    import openpyxl  # noqa: PLC0415

    wb = openpyxl.load_workbook(BytesIO(content), read_only=True, data_only=True)
    try:
        if isinstance(sheet, int):
            ws = wb.worksheets[sheet]
        else:
            ws = wb[sheet]

        rows = list(ws.iter_rows(values_only=True))
    finally:
        wb.close()

    if not rows:
        return []

    # Apply skip_rows before header
    rows = rows[skip_rows:]
    if not rows:
        return []

    headers = [_normalize_key(str(h) if h is not None else "") for h in rows[0]]
    result: list[dict[str, Any]] = []
    for row in rows[1:]:
        record = {headers[i]: _mask_privacy(v) for i, v in enumerate(row) if i < len(headers)}
        result.append(record)
    return result


def _parse_xlsx(
    content: bytes,
    sheet: str | int = 0,
    skip_rows: int = 0,
) -> list[dict[str, Any]]:
    """Parse XLSX bytes using pandas (preferred) or openpyxl fallback.

    Attempts pandas first for better multi-sheet, encoding, and type handling.
    Falls back to openpyxl + stdlib if pandas is not installed.
    """
    try:
        import pandas  # noqa: F401, PLC0415

        return _parse_xlsx_pandas(content, sheet, skip_rows)
    except ImportError:
        return _parse_xlsx_openpyxl(content, sheet, skip_rows)


def _parse_xls(
    content: bytes,
    sheet: str | int = 0,
    skip_rows: int = 0,
) -> list[dict[str, Any]]:
    """Parse legacy XLS bytes using xlrd.

    Raises:
        ImportError: If xlrd is not installed.
    """
    try:
        import xlrd  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "Install xlrd for .xls support: pip install mcp-canada[ircc]"
        ) from exc

    wb = xlrd.open_workbook(file_contents=content)
    if isinstance(sheet, int):
        ws = wb.sheet_by_index(sheet)
    else:
        ws = wb.sheet_by_name(sheet)

    if ws.nrows <= skip_rows:
        return []

    headers = [_normalize_key(str(ws.cell_value(skip_rows, c))) for c in range(ws.ncols)]
    result: list[dict[str, Any]] = []
    for r in range(skip_rows + 1, ws.nrows):
        record = {headers[c]: _mask_privacy(ws.cell_value(r, c)) for c in range(ws.ncols)}
        result.append(record)
    return result


def _parse_csv(content: bytes, skip_rows: int = 0) -> list[dict[str, Any]]:
    """Parse CSV bytes (including BOM-prefixed) into a list of dicts.

    Args:
        content: Raw CSV file bytes (UTF-8 or UTF-8-BOM).
        skip_rows: Number of lines to skip before the header row.

    Returns:
        list of dicts with normalized snake_case keys and privacy-masked values.
    """
    text = content.decode("utf-8-sig")
    lines = text.splitlines(keepends=True)
    lines = lines[skip_rows:]
    reader = csv.DictReader(StringIO("".join(lines)))
    result: list[dict[str, Any]] = []
    for row in reader:
        normalized = {_normalize_key(k): _mask_privacy(v) for k, v in row.items()}
        result.append(normalized)
    return result


async def fetch_and_parse(
    url: str,
    sheet: str | int = 0,
    skip_rows: int = 0,
    ttl: int = 86400,
) -> tuple[list[dict[str, Any]], bool]:
    """Fetch a remote file and parse it into a list of dicts.

    Supports XLSX, XLS, and CSV files. Results are cached via cached_fetch()
    with the given TTL. Exceptions from the HTTP fetch or parsing are NOT
    cached — they propagate to the caller.

    Args:
        url: Remote file URL. Routing by suffix: .csv -> CSV, .xls -> XLS,
             anything else (including .xlsx) -> XLSX.
        sheet: Sheet name or 0-based index (XLSX/XLS only).
        skip_rows: Rows to skip before the header row.
        ttl: Cache TTL in seconds (default: 86400 = 24 hours).

    Returns:
        (list[dict], was_cached) where was_cached=True if served from cache.
    """
    cache_key = f"parsers:{url}:{sheet}:{skip_rows}"

    async def _fetch() -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            raw = response.content

        lower_url = url.lower().split("?")[0]
        if lower_url.endswith(".csv"):
            return _parse_csv(raw, skip_rows)
        elif lower_url.endswith(".xls"):
            return _parse_xls(raw, sheet, skip_rows)
        else:
            return _parse_xlsx(raw, sheet, skip_rows)

    return await cached_fetch(cache_key, ttl, _fetch)
