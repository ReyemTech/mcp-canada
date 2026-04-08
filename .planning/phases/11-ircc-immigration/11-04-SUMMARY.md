---
phase: 11-ircc-immigration
plan: "04"
subsystem: shared/parsers + ircc/client
tags: [parser, ircc, xlsx, merged-headers, gap-closure]
dependency_graph:
  requires: [11-01, 11-02, 11-03]
  provides: [IRCC multi-row merged header parsing for all 11 dataset keys]
  affects: [ircc tools that call fetch_and_parse via _fetch_dataset]
tech_stack:
  added: []
  patterns:
    - openpyxl forward-fill for merged cells
    - per-dataset parse config dict (DATASET_PARSE_CONFIG)
    - backward-compatible kwarg extension (ircc_parse_config=None)
    - last-row-only raw-value guard for composite column name building
key_files:
  created: []
  modified:
    - src/mcp_canada/shared/parsers.py
    - src/mcp_canada/shared/__tests__/test_parsers.py
    - src/mcp_canada/modules/ircc/constants.py
    - src/mcp_canada/modules/ircc/client.py
    - src/mcp_canada/modules/ircc/__tests__/test_client.py
decisions:
  - "Last-row-only raw-value guard: forward-fill values in the final header row (months) are only included in composite names if the raw cell was explicitly set. This prevents Year Total columns from picking up spurious month-level forward-fill values."
  - "Label column suffix: when multiple label cols share a merged header cell, the second col gets a numeric suffix (e.g. gender_and_province_2) to avoid dict key collisions."
  - "Cache key includes config hash: ircc_parse_config is hashed into the cache key to prevent collisions when the same URL is parsed with different configs."
metrics:
  duration: "8 min"
  completed_date: "2026-04-08"
  tasks_completed: 2
  files_changed: 5
---

# Phase 11 Plan 04: IRCC Multi-Row Merged Header Parser Summary

openpyxl-based forward-fill parser with per-dataset config that converts IRCC's Year/Quarter/Month merged header rows into flat snake_case column names like `col_2015_q1_jan` and `col_2015_year_total`.

## What Was Built

### Task 1: _parse_ircc_xlsx + DATASET_PARSE_CONFIG (commit: 24c3f1a)

Added `_parse_ircc_xlsx()` to `src/mcp_canada/shared/parsers.py`:
- Uses openpyxl (not pandas) to access raw cell values including merged-cell None positions
- Forward-fills None values in each header row left-to-right (merged cells appear as None in non-anchor positions)
- Builds composite column names by joining values from each header row with "_", applying `_normalize_key()`
- For label columns (first N cols): uses first header row value with numeric suffix for duplicates
- For temporal columns: uses forward-filled values for all rows except the last; the last row (months) only contributes if the raw cell was explicitly non-None (guards against "Year Total" picking up spurious Q1 Total forward-fill)
- Strips trailing all-None data rows
- Applies `_mask_privacy()` to all values ("--" -> None)

Added `ircc_parse_config: dict | None = None` parameter to `fetch_and_parse()`:
- When provided and URL is .xlsx, routes to `_parse_ircc_xlsx(raw, **ircc_parse_config)`
- Existing callers that don't pass this kwarg get identical behavior
- Cache key includes a hash of the config to prevent collisions

Added `DATASET_PARSE_CONFIG` to `src/mcp_canada/modules/ircc/constants.py`:
- 11 dataset key mappings with `skip_rows`, `header_rows`, `label_cols` values
- Layout A (pr, study, work_imp, work_tfwp, afghan): skip_rows=2, header_rows=3, label_cols=1
- Layout B quarterly (ee_admissions, ee_invited, tr_to_pr): skip_rows=2, header_rows=3, label_cols=2
- Layout B-monthly (asylum): skip_rows=2, header_rows=2, label_cols=2
- Layout C ops (ops): skip_rows=6, header_rows=2, label_cols=1
- Layout D legacy (adhoc_pr): skip_rows=2, header_rows=1, label_cols=1

Added 10 unit tests in `TestParseIrccXlsx` covering all 4 layouts, privacy masking, forward-fill, trailing empty row stripping, backward compat.

### Task 2: client.py config pass-through (commit: cf47603)

Updated `_fetch_dataset()` in `src/mcp_canada/modules/ircc/client.py`:
- Imports `DATASET_PARSE_CONFIG` from constants
- Looks up `parse_config = DATASET_PARSE_CONFIG.get(dataset_key)`
- Passes `ircc_parse_config=parse_config` to `fetch_and_parse()`

Updated `src/mcp_canada/modules/ircc/__tests__/test_client.py`:
- All 11 existing URL-checking tests updated to assert the `ircc_parse_config` kwarg
- Added `TestFetchDatasetParseConfigPassthrough` with 4 representative tests (pr, asylum, ops, adhoc_pr)

## Verification

- All 1031 unit tests pass
- Coverage: 96.17% (above 95% threshold)
- pyright: 0 errors, 2 pre-existing warnings
- ruff: 0 errors

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Spurious forward-fill in last header row created wrong Year Total column names**
- **Found during:** Task 1 GREEN phase
- **Issue:** The "Year Total" column (e.g. col E) had no explicit value in the month row (row 5). After forward-fill, it picked up "Q1 Total" from col D. This produced `col_2015_year_total_q1_total` instead of `col_2015_year_total`.
- **Fix:** For the last header row only, values are included in composite names ONLY if the raw (pre-fill) cell was explicitly non-None. Upper rows always use forward-filled values.
- **Files modified:** src/mcp_canada/shared/parsers.py
- **Commit:** 24c3f1a

**2. [Rule 1 - Bug] Layout B label columns produced duplicate dict keys from merged header cell**
- **Found during:** Task 1 GREEN phase — layout B test
- **Issue:** Layout B has two label cols (A+B) merged under "Gender and Province". After normalizing both got `gender_and_province`, so the second column's value overwrote the first in the output dict.
- **Fix:** Second and subsequent label cols check if their base name already exists in headers; if so, append `_{col_idx + 1}` suffix (e.g. `gender_and_province_2`).
- **Files modified:** src/mcp_canada/shared/parsers.py
- **Commit:** 24c3f1a

**3. [Rule 2 - Missing test updates] Existing client tests asserted URL-only call signature**
- **Found during:** Task 2 GREEN phase — running full IRCC test suite
- **Issue:** All 11 existing `assert_called_once_with(expected_url)` assertions failed after client.py added the `ircc_parse_config` kwarg.
- **Fix:** Updated all 11 URL-checking tests and 6 French-variant tests to include `ircc_parse_config=DATASET_PARSE_CONFIG[dataset_key]`.
- **Files modified:** src/mcp_canada/modules/ircc/__tests__/test_client.py
- **Commit:** cf47603

## Self-Check: PASSED

- FOUND: src/mcp_canada/shared/parsers.py
- FOUND: src/mcp_canada/modules/ircc/constants.py
- FOUND: src/mcp_canada/modules/ircc/client.py
- FOUND: commit 24c3f1a (Task 1)
- FOUND: commit cf47603 (Task 2)
