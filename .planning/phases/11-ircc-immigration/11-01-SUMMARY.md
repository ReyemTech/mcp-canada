---
phase: 11-ircc-immigration
plan: "01"
subsystem: shared
tags: [parsers, xlsx, csv, xls, openpyxl, pandas, xlrd, file-parsing, caching]

# Dependency graph
requires:
  - phase: shared
    provides: cached_fetch() from shared/cache.py
provides:
  - fetch_and_parse(url, sheet, skip_rows, ttl) -> (list[dict], was_cached)
  - _normalize_key(header) -> snake_case identifier
  - _mask_privacy(value) -> None for '--', else passthrough
  - _parse_xlsx, _parse_xlsx_pandas, _parse_xlsx_openpyxl, _parse_csv, _parse_xls
affects:
  - 11-ircc-immigration (all plans depending on XLSX/CSV parsing)
  - any future module parsing tabular government files

# Tech tracking
tech-stack:
  added:
    - openpyxl>=3.1.5 (base dependency)
    - pandas>=3.0.2 (optional [ircc] extra)
    - xlrd>=2.0.2 (optional [ircc] extra)
  patterns:
    - Pandas-first XLSX parsing with openpyxl fallback on ImportError
    - Privacy masking: '--' strings converted to None at parse time
    - Column normalization: all headers -> IDENTIFIER_RE-safe snake_case
    - TTL caching via cached_fetch() with url+sheet+skip_rows cache key
    - Exceptions propagate from fetch; errors are never cached

key-files:
  created:
    - src/mcp_canada/shared/parsers.py
    - src/mcp_canada/shared/__tests__/test_parsers.py
  modified:
    - pyproject.toml (openpyxl to base deps, pandas+xlrd to [ircc] optional)
    - uv.lock

key-decisions:
  - "Parser uses pandas when available (better multi-sheet/encoding/types), falls back to openpyxl on ImportError — per user decision"
  - "openpyxl workbook closed in try/finally, not context manager — per plan constraint"
  - "Exceptions from _fetch() propagate; cached_fetch never caches errors"

patterns-established:
  - "fetch_and_parse: single entry point routing by URL suffix (.csv, .xls, else xlsx)"
  - "TDD: 23 tests written in RED phase before any implementation"

requirements-completed: [IRCC-01, IRCC-02, IRCC-03, IRCC-09]

# Metrics
duration: 8min
completed: 2026-04-08
---

# Phase 11 Plan 01: Shared File Parsers Summary

**Async XLSX/CSV/XLS parser with pandas-first approach, openpyxl fallback, privacy masking, and TTL caching via cached_fetch()**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-04-08T18:14:17Z
- **Completed:** 2026-04-08T18:22:00Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files modified:** 4

## Accomplishments

- `fetch_and_parse()` public API: downloads any government file URL and returns `(list[dict], was_cached)` with TTL caching
- Pandas-first XLSX parsing (`_parse_xlsx_pandas`) with automatic openpyxl fallback (`_parse_xlsx_openpyxl`) when pandas unavailable
- `_normalize_key()` converts any column header to IDENTIFIER_RE-safe snake_case (strips, lowercases, collapses non-alnum, prefixes digits)
- `_mask_privacy()` converts `'--'` privacy-masked values to `None` (including pandas NaN/NaT via try/except)
- BOM-aware CSV parsing via `utf-8-sig` decode with `skip_rows` support
- Legacy XLS support via xlrd with clear install error when unavailable
- 23 unit tests covering all paths including pandas/openpyxl fallback simulation

## Task Commits

TDD task committed in RED then GREEN phases:

1. **RED — Failing tests** - `a5c8...` (`test(11-01): add failing tests for shared file parsers`)
2. **GREEN — Implementation** - `618c69a` (`feat(11-01): implement shared file parsers (XLSX/CSV/XLS)`)

**Plan metadata:** (docs commit follows)

_Note: TDD task committed in two phases (test then implementation)_

## Files Created/Modified

- `src/mcp_canada/shared/parsers.py` - Public `fetch_and_parse()` + private parse/normalize/mask helpers
- `src/mcp_canada/shared/__tests__/test_parsers.py` - 23 unit tests covering all parsers and routing
- `pyproject.toml` - openpyxl added to base deps; pandas+xlrd added as `[ircc]` optional extras
- `uv.lock` - Updated lockfile

## Decisions Made

- Pandas-first pattern for XLSX: better handling of multi-sheet, encoding edge cases, and type inference; falls back to openpyxl on ImportError (per user decision from CONTEXT.md)
- openpyxl workbook closed in `try/finally` not context manager (per plan constraint, avoids context manager protocol issues in read_only mode)
- Errors from `_fetch()` propagate — `cached_fetch` only caches successful results; no silent `[]` on failures
- `_mask_privacy` handles pandas `NaN`/`NaT`/`NA` via `try: pd.isna(value)` with `except (ImportError, TypeError, ValueError)` to avoid noise when pandas unavailable

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required. Optional pandas/xlrd extras installable via `pip install mcp-canada[ircc]`.

## Next Phase Readiness

- `fetch_and_parse()` is ready for use by the IRCC module (Plans 11-02 through 11-04)
- openpyxl available in base install; pandas available after `pip install mcp-canada[ircc]`
- Cache key pattern: `parsers:{url}:{sheet}:{skip_rows}` — consistent with shared/cache.py conventions

---
*Phase: 11-ircc-immigration*
*Completed: 2026-04-08*
