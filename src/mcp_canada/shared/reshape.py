"""Shared reshape utilities for converting flat data into nested output formats.

Two reshape strategies:
- reshape_observations: For series-based time-series (BOC, StatCan)
  Input: rows with date + series_name + value → grouped by series
- reshape_temporal_columns: For IRCC-style wide temporal columns
  Input: flat dicts with year_quarter_month keys → nested year > quarter > month
"""

from __future__ import annotations

import re
from typing import Any


# ---------------------------------------------------------------------------
# Series-based reshape (BOC, StatCan)
# ---------------------------------------------------------------------------


def reshape_observations(
    rows: list[Any],
    series_key: str = "series_name",
    date_key: str = "date",
    value_key: str = "value",
    label_key: str = "label",
    description_key: str = "description",
) -> dict[str, Any]:
    """Reshape flat observation rows into nested series > observations format.

    Groups by series, deduplicates metadata, creates date→value mapping.

    Input:  [{"date": "2026-01-15", "series_name": "FXUSDCAD", "value": 1.39, "label": "...", ...}]
    Output: {"FXUSDCAD": {"label": "...", "description": "...", "observations": {"2026-01-15": 1.39}}}
    """
    series: dict[str, Any] = {}
    for row in rows:
        # Support both dicts and Pydantic models
        if hasattr(row, "model_dump"):
            row = row.model_dump()

        name = row.get(series_key, "")
        if name not in series:
            series[name] = {
                "label": row.get(label_key, ""),
                "description": row.get(description_key, ""),
                "observations": {},
            }
        series[name]["observations"][row.get(date_key, "")] = row.get(value_key)
    return series


# ---------------------------------------------------------------------------
# Temporal column reshape (IRCC)
# ---------------------------------------------------------------------------

_RE_YEAR_QUARTER_MONTH = re.compile(r"^(\d{4})_([qt]\d)_(.+)$")
_RE_YEAR_TOTAL = re.compile(r"^(\d{4})_(?:year_)?total$")
_RE_YEAR_MONTH = re.compile(r"^(\d{4})_([a-z]+)$")
_RE_YEAR_NUMERIC_MONTH = re.compile(r"^(\d{4})_(\d{2})$")


def reshape_temporal_columns(
    flat_rows: list[dict[str, Any]],
    year: int | None = None,
    recent: int | None = None,
    filter_value: str | None = None,
) -> list[dict[str, Any]]:
    """Reshape flat rows with temporal column names into nested year > quarter > month dicts.

    Input keys like "2015_q1_jan", "2015_q1_total", "2015_year_total"
    become: {"years": {"2015": {"q1": {"jan": 90, "total": 435}, "total": 2630}}}

    Label columns (no year prefix) are preserved at the top level.

    Args:
        flat_rows: Flat dicts with temporal column names.
        year: If set, only include data for this year.
        recent: If set, only include the N most recent years.
        filter_value: If set, case-insensitive substring match on label columns.
    """
    result: list[dict[str, Any]] = []
    for row in flat_rows:
        nested: dict[str, Any] = {}
        years: dict[str, Any] = {}

        for key, value in row.items():
            m = _RE_YEAR_QUARTER_MONTH.match(key)
            if m:
                yr, qtr, month = m.group(1), m.group(2), m.group(3)
                years.setdefault(yr, {}).setdefault(qtr, {})[month] = value
                continue

            m = _RE_YEAR_TOTAL.match(key)
            if m:
                yr = m.group(1)
                years.setdefault(yr, {})["total"] = value
                continue

            m = _RE_YEAR_MONTH.match(key)
            if m:
                yr, month = m.group(1), m.group(2)
                if month != "total":
                    years.setdefault(yr, {})[month] = value
                else:
                    years.setdefault(yr, {})["total"] = value
                continue

            # Try year_MM numeric month (e.g. 2023_01 for citizenship data)
            m = _RE_YEAR_NUMERIC_MONTH.match(key)
            if m:
                yr, month = m.group(1), m.group(2)
                years.setdefault(yr, {})[month] = value
                continue

            nested[key] = value

        if filter_value is not None:
            needle = filter_value.lower()
            if not any(
                needle in str(v).lower()
                for v in nested.values()
                if v is not None
            ):
                continue

        if year is not None:
            year_str = str(year)
            years = {k: v for k, v in years.items() if k == year_str}

        if recent is not None and years:
            sorted_keys = sorted(years.keys(), reverse=True)[:recent]
            years = {k: years[k] for k in sorted_keys}

        if years:
            nested["years"] = years
        result.append(nested)

    # Detect 2-label rows and group hierarchically
    if result:
        label_keys_sets = [
            [k for k in row if k != "years"]
            for row in result
        ]
        if all(len(lk) == 2 for lk in label_keys_sets):
            key1, key2 = label_keys_sets[0][0], label_keys_sets[0][1]
            if all(lk[0] == key1 and lk[1] == key2 for lk in label_keys_sets):
                grouped: dict[str, dict[str, Any]] = {}
                for row in result:
                    group = str(row.get(key1) or "")
                    sub = row.get(key2)
                    years_data = row.get("years", {})

                    if not group:
                        continue

                    if group not in grouped:
                        grouped[group] = {}

                    if sub is not None:
                        grouped[group][str(sub)] = {"years": years_data} if years_data else {}
                    else:
                        grouped[group]["total"] = {"years": years_data} if years_data else {}

                # Clean group names: strip " Total" suffix from groups with sub-items
                cleaned: dict[str, dict[str, Any]] = {}
                for group_name, items in grouped.items():
                    name = group_name
                    has_subitems = any(k != "total" for k in items)
                    if has_subitems and name.endswith(" Total"):
                        name = name[: -len(" Total")]
                    if name in cleaned:
                        cleaned[name].update(items)
                    else:
                        cleaned[name] = items

                result = [
                    {"group": group_name, "items": items}
                    for group_name, items in cleaned.items()
                ]

    return result
