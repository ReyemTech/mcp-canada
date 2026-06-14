---
phase: 18-manitoba-government-open-data
plan: "05"
subsystem: manitoba-module
tags: [arcgis-hub, featureserver, parks, fisheries, forests, health, wait-times, tdd, wave-4]
dependency_graph:
  requires:
    - phase: 18-01
      provides: "Manitoba module scaffold — all 5 client stubs for this plan, conftest fixtures, RURAL_HEALTH_FACILITIES_FS_URL (spike-resolved)"
    - phase: 18-02
      provides: "Discovery tools (fetch_search_datasets, etc.) — Pattern established for FeatureServer client bodies"
  provides:
    - "fetch_provincial_parks — bilingual NAME_E/NOM_F, TYPE_E filter, CACHE_TTL_META"
    - "fetch_fisheries_data — 9-field focused subset, Name LIKE + FishingDivision filters"
    - "fetch_provincial_forests — all fields, CACHE_TTL_STATIC"
    - "fetch_surgical_wait_times — Year= + IndicatorDataArea LIKE, CACHE_TTL_ANNUAL"
    - "fetch_health_facilities — Community_Name LIKE + emergency_only=True, spike-resolved FS URL"
    - "manitoba_get_provincial_parks — MB-06 — bilingual parks tool, park_type filter"
    - "manitoba_get_fisheries_data — MB-15 — waterbodies + species/regulations/Secchi"
    - "manitoba_get_provincial_forests — MB-16 (forests half) — forest management boundaries"
    - "manitoba_get_surgical_wait_times — MB-14 — annual averages by procedure/year"
    - "manitoba_get_health_facilities — MB-16 (rural health half) — RHA community filter, ED/PCH flags"
  affects:
    - 18-06 (Plan 06 transport tools — same module structure)
    - 18-08 (Plan 08 parametrized envelope/lang tests — will parametrize these 5 new tools)
tech_stack:
  added: []
  patterns:
    - "Focused field subset pattern: fetch_fisheries_data requests 9 of 26 available fields to minimize agent context cost"
    - "Compound WHERE clause builder: name LIKE + division equality, year equality + procedure LIKE built with list.join(' AND ')"
    - "Emergency-only boolean filter: maps to ArcGIS WHERE Emergency_Department_Availabili='Yes'"
    - "CACHE_TTL_ANNUAL (7d) for annual wait time data — matches source update cadence"
key-files:
  created: []
  modified:
    - src/mcp_canada/modules/manitoba/client.py
    - src/mcp_canada/modules/manitoba/tools.py
    - src/mcp_canada/modules/manitoba/__tests__/test_client.py
    - src/mcp_canada/modules/manitoba/__tests__/test_tools.py
key-decisions:
  - "fetch_fisheries_data requests focused 9-field subset (ID,Name,SurfaceArea,AvgDepth,SecchiDepth,FishingDivision,Species,Regulations,BoatLaunch) from 26-field layer — reduces agent context cost; agents can use manitoba_query_dataset for full schema"
  - "fetch_provincial_forests requests out_fields='*' — field names unknown from research; all-fields approach safe for low-record-count forest layer"
  - "manitoba_get_health_facilities passes rha= as community= to client — health_facilities client uses Community_Name LIKE filter; no separate RHA field exists in the layer (spike-confirmed field names)"
  - "fetch_health_facilities emergency_only maps to Emergency_Department_Availabili='Yes' — truncated field name is the actual ArcGIS layer column name (>10 chars truncated by ArcGIS)"
  - "PROVINCIAL_FORESTS_FS_URL uses CACHE_TTL_STATIC (24h same as META) — forest boundaries are static administrative data"
requirements-completed: [MB-06, MB-14, MB-15, MB-16]
duration: 15min
completed: 2026-06-14
---

# Phase 18 Plan 05: Manitoba Environment/Health/Parks Summary

**5 ArcGIS Hub FeatureServer tools completing the Manitoba environment + health domains: bilingual parks (93), fisheries waterbodies (350+), provincial forests, surgical wait times by procedure/year, and rural health facilities with ED/acute-care flags (spike-resolved URL)**

## Performance

- **Duration:** 15 min
- **Started:** 2026-06-14T04:50:02Z
- **Completed:** 2026-06-14T05:05:00Z
- **Tasks:** 2 (TDD — both RED→GREEN cycles completed)
- **Files modified:** 4

## Accomplishments

- 5 client function bodies implemented (all were `NotImplementedError` stubs from Plan 01 Wave 0)
- 5 @tool functions added to tools.py with standalone @tool, lang, make_response/make_error, Use for: + 8+ Keywords:
- MB-06 (parks), MB-14 (wait times), MB-15 (fisheries), MB-16 (forests + health facilities) requirements fully implemented
- 23 client tests + 23 tool tests written TDD-style (RED first, then GREEN)
- 138 total Manitoba tests passing; 97.61% overall project coverage

## Task Commits

Each task was committed atomically:

1. **Task 1: Environment/health/parks client bodies + tests** - `d7752ed` (feat)
2. **Task 2: 5 environment/health/parks @tool functions + tool tests** - `73b97dc` (feat)

## Files Created/Modified

- `src/mcp_canada/modules/manitoba/client.py` — 5 Plan 05 client function bodies filled (lines ~820-1020)
- `src/mcp_canada/modules/manitoba/tools.py` — 5 @tool functions + 5 api_name constants + imports
- `src/mcp_canada/modules/manitoba/__tests__/test_client.py` — 23 new tests across TestManitobaGetParks, TestManitobaGetFisheriesData, TestManitobaGetForests, TestManitobaGetWaitTimes, TestManitobaGetHealthFacilities
- `src/mcp_canada/modules/manitoba/__tests__/test_tools.py` — 23 new tests across same 5 test classes

## Decisions Made

- fetch_fisheries_data focuses on 9 of 26 available fields — reduces agent context cost; full schema available via `manitoba_query_dataset(WATERBODY_DATA_FS_URL)`
- fetch_provincial_forests uses `out_fields='*'` — field names not confirmed in research; safe approach for low-record forest layer
- `manitoba_get_health_facilities` uses `rha=` parameter (community substring filter) — no dedicated RHA field exists in the Rural Health layer; community name search covers all RHA queries
- `Emergency_Department_Availabili` is the actual truncated ArcGIS field name (ArcGIS truncates field names >10 chars in some cases); matched exactly as spike-confirmed

## Deviations from Plan

None — plan executed exactly as written. All 5 client bodies + 5 tool functions implemented per spec. Health facilities degrades gracefully (FS URL was resolved in spike, not unresolved — full implementation provided, no degradation needed).

## Rural Health FeatureServer Resolution Status

RESOLVED. The `Rural_Health_Care_Facilities_in_Manitoba/FeatureServer/0` URL was resolved in Wave 0 spike (18-SPIKE.md). `RURAL_HEALTH_FACILITIES_FS_URL` constant was already set in constants.py. Plan 05 implemented the full client body without any degradation path.

## Fisheries Field Subset Chosen

From 26 available fields, the following 9 were selected as the focused subset:
`ID, Name, SurfaceArea, AvgDepth, SecchiDepth, FishingDivision, Species, Regulations, BoatLaunch`

Excluded fields include stocking records detail columns, additional water quality parameters, and administrative codes. Agents can request the full schema via `manitoba_query_dataset`.

## Park TYPE_E Values

From PARK_TYPES constant (confirmed in constants.py from research):
`Provincial`, `Heritage`, `Wilderness`, `Recreation`, `Natural`, `Park Reserve`, `Indigenous Traditional Use`

These are the exact values in the `TYPE_E` field used for the `park_type` WHERE clause filter.

## Issues Encountered

None.

## Next Phase Readiness

- Plans 02-05 complete; Manitoba module has 17 tools (5 discovery + 12 curated)
- Plan 06 (transport/511 tools) is the final implementation wave
- Plan 07 (prompts + resources) and Plan 08 (quality/tests) follow
- All 5 Plan 05 client function bodies verified passing against mocked fixtures

---
*Phase: 18-manitoba-government-open-data*
*Completed: 2026-06-14*

## Self-Check: PASSED
