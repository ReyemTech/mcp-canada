---
phase: 17-alberta-government-open-data
plan: "03"
subsystem: aer-energy
tags: [alberta, aer, st1, st3, st39, fixed-width, xlsx, static-files, pitfall-7, pitfall-8, bilingual]

requires:
  - phase: 17-alberta-government-open-data
    plan: "01"
    provides: "Locked AER client/tool signatures + AER constants (URLs, rate group, TTLs, ST3_PRODUCTS tuple, DAY_ABBR map) + conftest fixtures (sample_aer_st1_text, sample_aer_st3_xlsx_rows, sample_aer_st39_rows)"
provides:
  - "4 filled AER client functions: fetch_well_licences_today, fetch_well_licences_archive, fetch_pipeline_statistics, fetch_production_volumes"
  - "4 filled AER @tool bodies: alberta_get_well_licences_today, _archive, _pipeline_statistics, _production_volumes"
  - "_parse_st1_txt fixed-width TXT parser (~30 LOC, position-based column slicing with auto header-skip)"
  - "_aer_limiter module-level rate limiter (2 r/s — conservative for static-file downloads)"
  - "ST3 product validation at tool layer (Pitfall 8) with bilingual inline-ternary + valid=[...] list in error extras"
  - "17 new unit tests (7 client + 10 tool) — all green, plus test_quality.py still green"
affects: [17-09]

tech-stack:
  added: []
  patterns:
    - "AER static URL fetch via httpx.AsyncClient(follow_redirects=True) for 303 AER→static.aer.ca redirects (ST1 daily TXT)"
    - "XLSX/XLS static files fetched through shared/parsers.fetch_and_parse() (ST3 XLSX, ST39 XLS)"
    - "Discovery-only metadata tools for large archives (ST1 monthly ZIP — no auto-parse, agents download externally)"
    - "Fixed-width TXT parser with data-row autodetect (first line where cols 0-7 are digits) + numeric-licence-block termination on footer"

key-files:
  created: []
  modified:
    - src/mcp_canada/modules/alberta/client.py
    - src/mcp_canada/modules/alberta/tools.py
    - src/mcp_canada/modules/alberta/__tests__/test_client.py
    - src/mcp_canada/modules/alberta/__tests__/test_tools.py

key-decisions:
  - "ST1 column layout: 4 flat fields (licence_number, operator, well_name, field_code) at positions 0/9/35/63 — derived from the sample_aer_st1_text fixture. Live AER ST1 file should have same layout per AER ST1 user manual; parser uses relative slicing so rows shorter than the widest column slice return None for the missing tail (no IndexError)."
  - "No `len(line) < 80` filter from plan spec — fixture lines are ~68 chars and would be skipped. Instead, data rows are delimited by: starts-with-digit licence number in cols 0-7. Footer/summary rows naturally fall outside that rule and terminate the parse loop."
  - "Year validation range 1960-2100 for pipeline statistics — ST39 publication dates back to 1960s, generous upper bound for future years."
  - "Month validation 1-12 at tool layer for archive (client layer accepts None for annual ZIP). Keeps client contract uniform."
  - "ST3 INVALID_INPUT includes `valid=list(ST3_PRODUCTS)` as error extras so agents see the canonical 7 products without re-reading the docstring."
  - "ST57 incidents NOT included (Pitfall 7 — PDF-only since 2014, auth-walled OneStop). Deferred per user's scope constraint."
  - "No `shared/aer.py` extraction — research rejected as premature abstraction; AER tools use `fetch_and_parse()` + direct httpx for ~30 LOC of ST1 parsing. Reuse threshold not met."

requirements-completed: [AB-06, AB-07, AB-08, AB-09]

duration: ~5min
completed: 2026-04-17
---

# Phase 17 Plan 03: Alberta Energy Regulator (AER) Tools Summary

**Filled the 4 AER tools that surface Alberta's signature energy data — daily well licences (ST1 fixed-width TXT), monthly archive ZIP metadata, annual pipeline statistics (ST39 XLS), and monthly production volumes (ST3 XLSX per 7 products) — all fetched from static.aer.ca via shared utilities with 2 r/s rate limiting and case-sensitive product validation (Pitfall 8).**

## Performance

- **Duration:** ~5 min (single executor run, TDD RED→GREEN for both tasks)
- **Started:** 2026-04-17T18:49Z
- **Completed:** 2026-04-17T18:54Z
- **Tasks:** 2/2
- **Files modified:** 4

## Accomplishments

- 4 AER client bodies filled with `cached_fetch` + module-level `_aer_limiter` wiring (per `.claude/rules/modules.md`)
- 4 `@tool` bodies filled with bilingual inline-ternary error handling (`make_response` / `make_error` envelopes)
- `_parse_st1_txt` helper written (~30 LOC) — auto-detects data-row start via `line[:7].strip().isdigit()`, terminates on footer rows, returns snake_case dicts
- Pitfall 7 respected: no `alberta_get_energy_incidents` tool (ST57 deferred — PDF-only since 2014)
- Pitfall 8 enforced: `ST3_PRODUCTS` tuple validated at BOTH client layer (raises `ValueError`) AND tool layer (returns `INVALID_INPUT` with bilingual message + `valid=[...]` extras)
- 17 new tests added (7 client + 10 tool) covering: fixed-width parsing, 303 redirect, day-of-week URL selection, discovery-only metadata, ST39 URL construction, ST3 valid + invalid products, French error messages, UPSTREAM_ERROR branches

## Task Commits

1. **Task 1: 4 AER client functions + ST1 fixed-width parser** — `2cbb316` (feat)
2. **Task 2: 4 AER @tool functions with bilingual errors** — `35fd01d` (feat)

## Files Modified

- `src/mcp_canada/modules/alberta/client.py` — filled 4 `fetch_*` bodies; added `_parse_st1_txt` + `_ST1_COLUMNS` + `_aer_limiter`; imported AER constants (AER_ST1_DAILY_BASE, AER_ST1_MONTHLY_BASE, AER_ST3_BASE, AER_ST39_BASE, CACHE_TTL_DAILY/MONTHLY/ANNUAL, DAY_ABBR, RATE_GROUP_AER, RATE_LIMIT_AER, ST3_PRODUCTS, USER_AGENT) + `datetime`
- `src/mcp_canada/modules/alberta/tools.py` — filled 4 `@tool` bodies calling `_client.fetch_*`; bilingual inline ternary; `make_response` / `make_error` envelopes; month/year range validation
- `src/mcp_canada/modules/alberta/__tests__/test_client.py` — filled 4 `TestAlberta{WellLicencesToday,WellLicencesArchive,PipelineStatistics,ProductionVolumes}` classes (7 tests total)
- `src/mcp_canada/modules/alberta/__tests__/test_tools.py` — filled 4 `TestAlberta{...}Tool` classes (10 tests total including `test_invalid_product_french_error`)

## Test Coverage

**Client tests (7 new):**

| Class | Tests |
|-------|-------|
| TestAlbertaWellLicencesToday | 3 (fixed-width parse, 303 redirect, day-of-week URL) |
| TestAlbertaWellLicencesArchive | 1 (discovery-only metadata, no fetch_and_parse call) |
| TestAlbertaPipelineStatistics | 1 (ST39-{year}.xls URL) |
| TestAlbertaProductionVolumes | 2 (valid product → Gas_current.xlsx URL, invalid product raises ValueError) |

**Tool tests (10 new):**

| Class | Tests |
|-------|-------|
| TestAlbertaWellLicencesTodayTool | 3 (envelope, French lang propagation, UPSTREAM_ERROR French message) |
| TestAlbertaWellLicencesArchiveTool | 1 (metadata envelope) |
| TestAlbertaPipelineStatisticsTool | 2 (envelope, UPSTREAM_ERROR English message) |
| TestAlbertaProductionVolumesTool | 4 (envelope, invalid product EN, invalid product FR + valid list, UPSTREAM_ERROR) |

## ST1 Column Layout

Discovered column layout (derived from fixture, validated against `sample_aer_st1_text`):

| Field | Position | Notes |
|-------|----------|-------|
| `licence_number` | cols 0-9 | 7-digit zero-padded licence number |
| `operator` | cols 9-35 | Space-padded operator name (~26 chars) |
| `well_name` | cols 35-63 | Space-padded well name (~28 chars) |
| `field_code` | cols 63-EOL | 4-digit field code (may be blank) |

Auto-detection rule: data rows start where `line[:7].strip().isdigit()` is True. Parse loop terminates when that rule no longer holds (trailing footer / summary lines skipped naturally).

If a future real AER ST1 file inspection reveals different column positions, adjust `_ST1_COLUMNS` in `client.py`. The parser is position-based, so the fix is a 4-line tuple update.

## Pitfalls Addressed in Code

| Pitfall | Where | How |
|---------|-------|-----|
| **Pitfall 7** (ST57 PDF-only) | No `alberta_get_energy_incidents` tool | Deferred per CONTEXT/research; not scaffolded |
| **Pitfall 8** (ST3 case-sensitive products) | `fetch_production_volumes` + `alberta_get_production_volumes` | Validated against `ST3_PRODUCTS` tuple at BOTH layers; bilingual `INVALID_INPUT` with `valid=[...]` list |

## Deviations from Plan

**[Rule 3 - Blocking] Return type annotation on `fetch_well_licences_archive`.**

- **Found during:** Task 1 RED phase
- **Issue:** Wave 0 stub declared `fetch_well_licences_archive(year, month=None) -> tuple[list[AlbertaWellLicence], bool]` but the plan's explicit behavior requires returning a metadata dict (`{"url", "year", "month", "note"}`), not a list of licence rows.
- **Root cause:** Plan 03's behavior specification (discovery-only, no auto-parse of large ZIPs) is incompatible with the Wave 0 signature. The plan itself calls this out indirectly by specifying the metadata dict shape.
- **Fix:** Changed the return type annotation from `tuple[list[AlbertaWellLicence], bool]` to `tuple[dict[str, Any], bool]`. Function name, parameters, and default values are preserved. This matches the plan's explicit `<behavior>` block.
- **Files modified:** `src/mcp_canada/modules/alberta/client.py`
- **Commit:** `2cbb316`

**[Rule 1 - Bug] ST1 parser length filter.**

- **Found during:** Task 1 GREEN phase (first test run)
- **Issue:** The plan's reference `_parse_st1_txt` implementation included `if len(line) < 80: continue` to skip footers, but the sample fixture lines are ~68 chars wide. Applying the filter would skip all 3 data rows in the fixture.
- **Fix:** Replaced the length heuristic with a semantic rule: data rows start where `line[:7].strip().isdigit()` is True, and the parse loop terminates when that stops being True (non-numeric prefix = footer). This is more robust and fixture-compatible.
- **Files modified:** `src/mcp_canada/modules/alberta/client.py`
- **Commit:** `2cbb316`

**[Rule 2 - Critical] Year validation on `alberta_get_pipeline_statistics`.**

- **Found during:** Task 2 GREEN phase
- **Issue:** Plan didn't specify year-range validation, but passing year=1950 or year=9999 would construct an invalid URL and get a 404 from AER — better to fail fast with `INVALID_INPUT`.
- **Fix:** Added `if year < 1960 or year > 2100` check at tool layer with bilingual message. Updated the `test_upstream_error_english_message` test to use `year=2009` (valid range) so the HTTPStatusError branch is actually exercised rather than hitting the new validation.
- **Files modified:** `src/mcp_canada/modules/alberta/tools.py`, `__tests__/test_tools.py`
- **Commit:** `35fd01d`

No other deviations. Plan text executed as specified.

## Handoff to Next Plans

- **Plan 04 (Wave 2 Wildfire):** Already in progress in parallel (commits `fe7ecdb`, `08acf4e` landed during this plan's window). No file conflicts — separate tool surface.
- **Plan 05 (Wave 2 Health), Plan 06 (Wave 3 Transport), Plan 07 (Wave 3 Environment):** Independent — no dependency on AER tools. Can proceed unblocked.
- **Plan 09 (Wave 5 Parametrized tests):** `TestAlbertaEnvelopes` / `TestAlbertaLangParam` stubs can now run against the 4 AER tools (envelope + lang propagation verified per-tool here, so parametrized version should pass).

## Self-Check: PASSED

- Commit `2cbb316` found in `git log --oneline -10` (Task 1)
- Commit `35fd01d` found in `git log --oneline -10` (Task 2)
- `src/mcp_canada/modules/alberta/client.py` modified — 4 AER bodies filled, `_parse_st1_txt` added, `_aer_limiter` added
- `src/mcp_canada/modules/alberta/tools.py` modified — 4 `@tool` bodies filled
- `src/mcp_canada/modules/alberta/__tests__/test_client.py` modified — 7 new AER client tests
- `src/mcp_canada/modules/alberta/__tests__/test_tools.py` modified — 10 new AER tool tests
- `uv run pytest src/mcp_canada/modules/alberta/__tests__/ tests/test_quality.py -k "WellLicence or Pipeline or Production or quality"` → 22 passed
- `uv run python -c "from mcp_canada.modules.alberta.tools import alberta_get_well_licences_today, alberta_get_well_licences_archive, alberta_get_pipeline_statistics, alberta_get_production_volumes; print('4 AER tools importable')"` → "4 AER tools importable"
- `uv run ruff check src/mcp_canada/modules/alberta/client.py src/mcp_canada/modules/alberta/tools.py src/mcp_canada/modules/alberta/__tests__/test_client.py src/mcp_canada/modules/alberta/__tests__/test_tools.py` → All checks passed!
