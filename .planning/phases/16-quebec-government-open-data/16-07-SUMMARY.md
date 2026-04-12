---
phase: 16-quebec-government-open-data
plan: "07"
subsystem: quebec-module
tags: [gap-closure, tdd, int-str-coercion, pydantic-v2, xlsx-legend-filter, hydro-quebec, mask-privacy-compat]

# Dependency graph
requires:
  - phase: 16-quebec-government-open-data
    provides: "fetch_bridge_structures WFS paging + _normalize_route (16-06); fetch_electricity_data XLSX parsing + SECLEVEL=1 ssl_context (16-06)"
provides:
  - "_str_or_none helper scoped to quebec module (no shared parser change)"
  - "_flatten_bridge zero-padded route_num emission (matches filter normalization)"
  - "fetch_bridge_structures filter: _normalize_route roundtrip on int num_route"
  - "Replicate int->str coercion for _flatten_population_row / _flatten_road_work / _flatten_road_event"
  - "_is_real_electricity_row filter strips XLSX legend/formula rows"
affects: [quebec module, QuebecBridgeStructure, QuebecPopulationRow, QuebecRoadWork, QuebecRoadEvent, Hydro-Québec historique-production-consommation consumers]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-mapper stringify helper pattern for digit-only CSV ID columns (alternative to touching shared/_mask_privacy)"
    - "Domain-specific caller-side row filter for publisher quirks (legend rows) instead of generic parser hacks"
    - "Normalizer roundtrip in post-parse filter to compensate for _mask_privacy int coercion"

key-files:
  created: []
  modified:
    - src/mcp_canada/modules/quebec/client.py
    - src/mcp_canada/modules/quebec/__tests__/test_client.py
    - tests/integration/test_tool_scenarios.py

key-decisions:
  - "_str_or_none helper lives in quebec/client.py (not shared/) — fix is domain-specific, shared _mask_privacy behavior remains correct for the general case"
  - "_flatten_bridge emits _normalize_route(str(num_route)) so post-parse filter and emitted row both see '00020' (consistent, honors UAT assertion)"
  - "fetch_bridge_structures filter uses _normalize_route roundtrip on num_route — belt-and-suspenders nom_route substring fallback preserved"
  - "Apply _str_or_none to _flatten_population_row.mcode and MTQ chantiers/evenements identifiants as latent replicate-check (LATENT BUG — same root cause)"
  - "_is_real_electricity_row lives in quebec/client.py as a domain-specific caller filter — do NOT modify shared/parsers.py _parse_xlsx"
  - "Electricity filter discriminator: null rang/mois/jour/heure OR any cell containing '='-with-digit — reliable tells from live XLSX inspection"
  - "Existing electricity test fixtures augmented with rang/mois/jour/heure indexing cells to pass the new filter (regression prevention)"

patterns-established:
  - "Quebec int->str coercion: add `_str_or_none(v)` calls only to the CSV-column mappings where Pydantic schema declares `str | None` and _mask_privacy produces int"
  - "Bridge route filter: always _normalize_route on BOTH sides of the comparison — user input AND parsed num_route"
  - "Publisher-specific row filters belong in the module caller, not the generic parser"

requirements-completed: [QC-BRIDGES-INT-STR-COERCION, QC-ELECTRICITY-LEGEND-ROW]

# Metrics
duration: 8 min
completed: 2026-04-12
---

# Phase 16 Plan 07: Quebec Gap Closure Cycle 3 Summary

**Fixed bridge structures Pydantic int->str validation failure (primary + latent on population/road_works/road_events) and stripped Hydro-Québec XLSX formula legend row in fetch_electricity_data — both scoped to quebec module, no shared parser edits.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-12T03:36:44Z
- **Completed:** 2026-04-12T03:44:17Z
- **Tasks:** 3 (2 fix tasks + 1 verification task)
- **Files modified:** 3

## Accomplishments

- Bridge structures now validate against `QuebecBridgeStructure` when `_mask_privacy` coerces digit-only CSV cells to int. Five ID columns (`structure_id`, `dossier_num`, `municipality_code`, `route_num`, `structure_type`) are stringified in the quebec mapper via a new `_str_or_none` helper. `route_num` is additionally passed through `_normalize_route` so the emitted value matches the filter's normalized form (`"00020"` for A-20) — agents see a consistent zero-padded code.
- Post-parse bridge filter now normalizes the int `num_route` via `_normalize_route` roundtrip before comparing to `norm`. The filter no longer depends on the brittle `nom_route` substring fallback when `num_route` comes back as int (which is the real production case after `_mask_privacy`).
- Three latent int-to-str bugs fixed replicate-style on the same root cause: `_flatten_population_row.mcode`, `_flatten_road_work.identifier` / `.chantier_id`, `_flatten_road_event.identifier`. All use the same `_str_or_none(r.get(...))` coercion. No other str-typed fields in these schemas come from a digit-only CSV column.
- Hydro-Québec historique-production-consommation XLSX files include a legend/formula row as the first data row (null `rang`/`mois`/`jour`/`heure`; cells containing formula strings like `'5=1-2+3+4'`, `'7=5-6'`, `'9=7-8'`, `'13=11x12'`). A new `_is_real_electricity_row` helper filters this row (and any sparse rows with null indexing cells) before slicing by `limit`. Agents now see `data[0]["rang"] == 1` — real data from the first returned row.
- Existing electricity test fixtures augmented with `{"rang": 1, "mois": 1, "jour": 1, "heure": 1}` indexing cells so they survive the new filter. No tests were removed.

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix bridge structures Pydantic int→str coercion (primary + latent mapper replicate-check)** — `bce827b` (fix)
2. **Task 2: Skip Hydro-Québec XLSX legend/formula row in fetch_electricity_data** — `baa6913` (fix)
3. **Task 3: Full test-suite + coverage + lint verification and phase retest trigger** — no commit (verification only)

**Plan metadata commit:** to follow (`docs(16-07): complete quebec gap closure cycle 3 plan`)

## Files Created/Modified

- `src/mcp_canada/modules/quebec/client.py` — Added `_str_or_none`; updated `_flatten_bridge` (5 field stringifies + `_normalize_route` on route_num); updated `fetch_bridge_structures` filter to normalize int `num_route`; replicate-check on `_flatten_population_row`, `_flatten_road_work`, `_flatten_road_event`; added `_is_real_electricity_row` and applied in `fetch_electricity_data._fetch()`.
- `src/mcp_canada/modules/quebec/__tests__/test_client.py` — Added 6 new test classes/methods for int→str coercion (`TestQuebecBridgeStructuresTypeCoercion` with 2 tests, `TestQuebecBridgeStructuresIntFilter`, `TestQuebecPopulationIntCoercion`, `TestQuebecRoadWorkIntCoercion`, `TestQuebecRoadEventIntCoercion`). Added 3 electricity filter tests (`test_skips_legend_formula_row`, `test_skips_row_with_null_indexing_cell`, `test_keeps_real_row_with_populated_indexing_cells`). Updated 5 existing electricity-test fixtures to include indexing cells. Updated `TestFetchBridgeStructures.test_returns_bridge_rows` to expect `route_num == "00010"` (normalized form).
- `tests/integration/test_tool_scenarios.py` — Added 2 new live integration tests: `test_bridges_route_filter_row_types` (strict type assertions + zero-padded route_num) and `test_electricity_first_row_is_real` (first row rang==1, no formula leakage).

## Decisions Made

- **Scoped fix pattern:** All coercion lives in quebec/client.py. `shared/parsers.py:_mask_privacy` behavior is correct for the general case (digit-only cells that are semantically numeric — populations, areas, counts). Only the ID columns in this module are semantically strings that happen to be digit-only, so the fix is module-local.
- **Preferred zero-padded emission for `route_num`:** Per the plan's explicit decision and the UAT "route_num is a string containing '0020' or equals '00020'" assertion, the mapper calls `_normalize_route(str(raw_num_route))` so emitted value and filter-comparison value are identical. Alternative (raw stringify `"20"`) rejected — filter and output would diverge.
- **Replicate-check additive, not refactored:** Three additional mappers get the same `_str_or_none` call on the same root-cause bug. No shared helper extraction — the fix is pure substitution of `r.get(...)` with `_str_or_none(r.get(...))`.
- **Electricity filter belongs in caller, not parser:** `_parse_xlsx` correctly returns whatever the XLSX file contains. The legend row is a Hydro-Québec publication artifact, not a general parser concern. Filter at the domain level (`fetch_electricity_data`), not the generic level (`fetch_and_parse`).
- **Filter discriminator is rang/mois/jour/heure nullness:** Live XLSX inspection (confirmed in the plan's interfaces block) shows these four indexing cells are the reliable tell — real data always populates them, the legend row leaves them all null. The formula-string heuristic (`'='` + digit) is secondary/defensive.

## Deviations from Plan

None — plan executed exactly as written. One in-scope adjustment occurred: `TestFetchBridgeStructures.test_returns_bridge_rows` used fixture value `num_route: "10"` and asserted `result[0].route_num == "10"`. After the Fix 1A change (`_normalize_route` on emission), the emitted value is `"00010"`. Updated the existing assertion to `"00010"` — this is not a deviation, it's a direct consequence of the plan's explicit decision to emit zero-padded form. Documented with inline comment referencing 16-07.

## Issues Encountered

None. Both fixes landed on first attempt. RED baseline confirmed Pydantic ValidationError for bridges and 3-row legacy list for electricity — both expected. GREEN achieved without iteration. No coverage drop (96.58% overall, unchanged from 16-06 baseline).

## Verification Results

| Check | Command | Result |
|-------|---------|--------|
| Targeted tests | `pytest -k "TypeCoercion or IntFilter or IntCoercion or Bridge or Population or RoadWork or RoadEvent or Electricity" -v` | 29 passed |
| Quebec module suite | `pytest src/mcp_canada/modules/quebec/` | 149 passed, 2 warnings (pre-existing) |
| Full unit suite | `pytest src/ -x --tb=short -q` | 1993 passed, 2 skipped |
| Coverage | `pytest --cov=src/mcp_canada --cov-fail-under=95 -q` | **96.58%** (pass) |
| Lint | `ruff check src/mcp_canada/modules/quebec/ tests/integration/test_tool_scenarios.py` | All checks passed |
| Type check | `pyright src/mcp_canada/modules/quebec/client.py` | 0 errors, 0 warnings, 0 informations |

Integration tests (live, marked `@pytest.mark.integration`) were not executed in this run — they require live MTQ/DQ/Hydro-Québec connectivity and run as part of the Phase 16 UAT retest 3. The new assertions (`test_bridges_route_filter_row_types`, `test_electricity_first_row_is_real`) are wired into the same class as the existing Quebec integration tests and will execute on the next UAT retest.

## User Setup Required

None — no external service configuration required. The existing SECLEVEL=1 scoped SSLContext from 16-06 continues to service Hydro-Québec XLSX downloads unchanged.

## Next Phase Readiness

- Phase 16 Quebec module is ready for UAT retest 3 (cycle 4). Expected outcome:
  - **Test 8** (bridge structures filter): flips from `issue` to `pass` — rows validate against QuebecBridgeStructure, string IDs throughout, `route_num == "00020"` for A-20 query.
  - **Test 11** (electricity data): flips from `minor_issues` to `pass` — first row is real data with `rang == 1`, no formula strings leak.
- No further gap-closure cycles anticipated for Phase 16 pending retest outcome. The last two UAT-visible defects have been root-caused and fixed.
- `shared/parsers.py` is untouched and remains in the 16-06 state. No behavioral change for any other module (York Region, BC, Ontario, Toronto, IRCC) since they use different Pydantic schemas and/or fetch paths.

## Self-Check

Files modified (verified on disk):
- [x] src/mcp_canada/modules/quebec/client.py
- [x] src/mcp_canada/modules/quebec/__tests__/test_client.py
- [x] tests/integration/test_tool_scenarios.py

Commits (verified via `git log`):
- [x] bce827b — fix(16-07): stringify numeric ID fields in quebec mappers for Pydantic str schemas
- [x] baa6913 — fix(16-07): skip Hydro-Québec XLSX formula legend row in fetch_electricity_data

Scope boundary (verified):
- [x] src/mcp_canada/shared/parsers.py NOT touched
- [x] No schemas modified
- [x] No tools/prompts/resources added
- [x] README.md NOT modified (no tool count change)

## Self-Check: PASSED

---
*Phase: 16-quebec-government-open-data*
*Completed: 2026-04-12*
