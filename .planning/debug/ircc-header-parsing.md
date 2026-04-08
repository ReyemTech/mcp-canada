---
status: diagnosed
trigger: "Investigate IRCC XLSX multi-row header parsing blocker"
created: 2026-04-08T00:00:00Z
updated: 2026-04-08T00:00:00Z
---

## Current Focus

hypothesis: CONFIRMED — three distinct header layouts across IRCC datasets; parser has no multi-row header support
test: Downloaded and inspected 5 files from different dataset categories
expecting: Confirmed all three layout variants
next_action: Write up findings and recommended fix

## Symptoms

expected: Parsed data with meaningful column names (country, year-month combos, totals)
actual: 190 unnamed_* columns with garbage data
errors: No crash — silently produces wrong output
reproduction: Call fetch_and_parse on any IRCC XLSX URL with default skip_rows=0
started: Always broken — parser never handled multi-row headers

## Eliminated

- hypothesis: All IRCC files share the same header structure
  evidence: Three distinct layouts found (see Evidence below)
  timestamp: 2026-04-08

- hypothesis: pandas header=[list] MultiIndex would be sufficient
  evidence: Merged cells produce None values; pandas MultiIndex preserves the hierarchy but creates unusable tuple column names like (2015, Q1, Jan). The real need is to flatten into "2015_jan", "2015_q1_total", "2015_total" strings. Forward-fill of merged cells + manual join is required regardless.
  timestamp: 2026-04-08

## Evidence

- timestamp: 2026-04-08
  checked: PR country EN file (EN_ODP-PR-Citz.xlsx)
  found: |
    Layout A — "Standard quarterly" (5 header rows):
    Row 1: Title merged across all cols (A1:GI1)
    Row 2: Empty (merged A2:GI2)
    Row 3: Label col header ("Country of Citizenship") + Year labels (2015, 2016...) merged across 17 cols each
    Row 4: Quarter labels (Q1, Q2, Q3, Q4) merged across 4 cols + "Year Total" merged
    Row 5: Month labels (Jan, Feb, Mar, Q1 Total, Apr, ..., Q4 Total) — no merges
    Row 6+: Data — single label col (col A) + string numeric values ("90", "2,630")
    Total: 191 cols, 228 rows. Label columns: 1 (col A).
  implication: Need to skip 2 rows (title+blank), then combine 3 rows (year/quarter/month) into flat column names

- timestamp: 2026-04-08
  checked: Study country, EE admissions gender, Asylum province files
  found: |
    Layout B — "Two-label quarterly" (5 header rows, 2 label columns):
    Same as Layout A but with TWO label columns (A and B) merged in header region.
    Examples: EE admissions gender (A3:B5 merged = "Gender and Province/Territory"),
    Asylum (A3:B4 merged = "Claim Office Type and Province/Territory of Claim").
    EE/study files have quarter rows; asylum files do NOT have quarter rows (Layout B-monthly).

    Layout B sub-variant (asylum): Only 4 header rows — no quarter row.
    Row 3: Two label cols + Year labels
    Row 4: Month labels (Jan..Dec) + Year Total — NO quarter grouping
    Row 5+: Data with 2 label columns (group in A, sub-item in B)
  implication: Must detect number of label columns (1 or 2) and presence/absence of quarter row

- timestamp: 2026-04-08
  checked: OPS PR Intake file
  found: |
    Layout C — "Operational" (completely different):
    Rows 1-3: Empty
    Row 4: Title merged across all cols
    Rows 5-6: Empty
    Row 7: Label col (A, merged A7:A8) + Year labels (2023, 2024, 2025, 2026) merged across month spans
    Row 8: Month labels with trailing spaces ("January  ", "February ", etc.)
    Row 9+: Data — label in col A + numeric values (integers, not strings)
    Total: 42 cols, 219 rows. NO quarter grouping. Only 2 header rows (year + month).
    Date range: 2023-2026 (shorter than other datasets).
  implication: Completely different skip_rows and header structure; needs separate handling or auto-detection

- timestamp: 2026-04-08
  checked: Adhoc PR XLS file (IRCC_PRadmiss_0002_E.xls)
  found: |
    Layout D — "Legacy annual" (simple, already works with skip_rows=2):
    Row 0: Title merged
    Row 1: Empty
    Row 2: Single header row — label col + year columns (1980, 1981, ...)
    Row 3+: Data with numeric values (floats)
    No merged cells. No multi-row headers.
  implication: These files would work today with skip_rows=2; no special handling needed

## Resolution

root_cause: |
  The shared parser `_parse_xlsx_pandas` and `_parse_xlsx_openpyxl` both treat a single row
  as the header (after skip_rows). IRCC XLSX files have 3-4 merged header rows that encode
  a Year > Quarter > Month hierarchy via merged cells. With skip_rows=0, row 0 (the title)
  becomes the "header", producing one real column name and 190 unnamed/None columns.
  Even with correct skip_rows, the parser cannot combine multiple header rows into
  meaningful flat column names like "2015_jan" or "2015_q1_total".

fix: |
  RECOMMENDED APPROACH: openpyxl-based merged-cell forward-fill (NOT pandas MultiIndex).

  Reasons against pandas header=[0,1,2]:
  - Creates MultiIndex with tuple column names like (2015, Q1, Jan) — unusable for flat dict output
  - Still requires flattening logic to join tuples into snake_case strings
  - Does not handle merged cells correctly (gets NaN instead of forward-filled values)
  - Would need .ffill(axis=1) on column levels anyway

  Recommended implementation:

  1. Add `header_rows: int | list[int] | None` parameter to parsers (backward compatible):
     - None (default): current behavior (single header row after skip_rows)
     - int: number of header rows to combine
     - list[int]: specific 0-based row indices to use as header

  2. New function `_resolve_ircc_headers(ws, header_row_indices, label_col_count)`:
     - Read specified rows from openpyxl worksheet
     - Forward-fill None values from merged cells (left-to-right per row)
     - Combine row values into flat column names: "2015_q1_jan", "2015_q1_total", "2015_total"
     - Normalize with _normalize_key()
     - First `label_col_count` columns get their own names from the merged header cell

  3. In client.py `_fetch_dataset()`, add per-dataset-key config in constants.py:
     ```python
     DATASET_PARSE_CONFIG = {
         "pr":           {"skip_rows": 2, "header_rows": 3, "label_cols": 1},
         "study":        {"skip_rows": 2, "header_rows": 3, "label_cols": 1},
         "work_imp":     {"skip_rows": 2, "header_rows": 3, "label_cols": 1},
         "work_tfwp":    {"skip_rows": 2, "header_rows": 3, "label_cols": 1},
         "ee_admissions":{"skip_rows": 2, "header_rows": 3, "label_cols": 2},
         "ee_invited":   {"skip_rows": 2, "header_rows": 3, "label_cols": 2},
         "tr_to_pr":     {"skip_rows": 2, "header_rows": 3, "label_cols": 2},
         "asylum":       {"skip_rows": 2, "header_rows": 2, "label_cols": 2},  # no quarter row
         "ops":          {"skip_rows": 6, "header_rows": 2, "label_cols": 1},
         "afghan":       {"skip_rows": 2, "header_rows": 3, "label_cols": 1},
         "adhoc_pr":     {"skip_rows": 2, "header_rows": 1, "label_cols": 1},  # simple, works today
     }
     ```

  4. Alternative (simpler but less flexible): Since ALL IRCC files follow the same general
     pattern of "title + blank + year/quarter/month rows", add an `ircc_mode=True` flag
     to fetch_and_parse that triggers the special header logic. This avoids over-generalizing
     the shared parser.

  RECOMMENDATION: Option 4 (ircc_mode flag) for minimal blast radius. The multi-row header
  logic is IRCC-specific and should not complicate the shared parser for other modules.
  Implement as a new `_parse_ircc_xlsx()` function in parsers.py that:
  - Uses openpyxl (not pandas) to access merged_cells metadata
  - Auto-detects the header structure by scanning for the first row with year values
  - Forward-fills merged cells
  - Builds flat column names
  - Returns standard list[dict] output

verification:
files_changed: []
