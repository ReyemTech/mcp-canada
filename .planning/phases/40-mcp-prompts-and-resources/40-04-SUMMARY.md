---
phase: 40-mcp-prompts-and-resources
plan: "04"
subsystem: mcp-prompts-resources
tags: [prompts, resources, weather, ircc, ontario, toronto, fastmcp, bilingual]
dependency_graph:
  requires:
    - phase: 40-01
      provides: boc-prompts-reference-implementation
  provides:
    - weather-prompts-resources
    - ircc-prompts-resources
    - ontario-prompts-resources
    - toronto-prompts-resources
  affects:
    - src/mcp_canada/modules/weather/prompts.py
    - src/mcp_canada/modules/weather/resources.py
    - src/mcp_canada/modules/weather/__tests__/test_prompts_resources.py
    - src/mcp_canada/modules/ircc/prompts.py
    - src/mcp_canada/modules/ircc/resources.py
    - src/mcp_canada/modules/ircc/__tests__/test_prompts_resources.py
    - src/mcp_canada/modules/ontario/prompts.py
    - src/mcp_canada/modules/ontario/resources.py
    - src/mcp_canada/modules/ontario/__tests__/test_prompts_resources.py
    - src/mcp_canada/modules/toronto/prompts.py
    - src/mcp_canada/modules/toronto/resources.py
    - src/mcp_canada/modules/toronto/__tests__/test_prompts_resources.py
tech_stack:
  added: []
  patterns:
    - "Weather prompts.py at top-level weather/ — FileSystemProvider scans recursively so one file covers all 8 sub-modules"
    - "Guided workflow prompts (list[Message]) for multi-step tool chaining; quick lookups (str) for single-tool instructions"
    - "Zero-parameter resource functions — no lang param to stay FunctionResource not ResourceTemplate"
    - "Bilingual content embedded inline in resources (both languages in one JSON/Markdown)"
    - "Toronto neighbourhood-list: full 140-neighbourhood catalog embedded in resource function"
    - "Toronto ward-list: all 25 council wards with numbers and names"
key_files:
  created:
    - src/mcp_canada/modules/weather/__tests__/__init__.py
    - src/mcp_canada/modules/weather/__tests__/test_prompts_resources.py
    - src/mcp_canada/modules/weather/prompts.py
    - src/mcp_canada/modules/weather/resources.py
    - src/mcp_canada/modules/ircc/__tests__/test_prompts_resources.py
    - src/mcp_canada/modules/ircc/prompts.py
    - src/mcp_canada/modules/ircc/resources.py
    - src/mcp_canada/modules/ontario/__tests__/test_prompts_resources.py
    - src/mcp_canada/modules/ontario/prompts.py
    - src/mcp_canada/modules/ontario/resources.py
    - src/mcp_canada/modules/toronto/__tests__/test_prompts_resources.py
    - src/mcp_canada/modules/toronto/prompts.py
    - src/mcp_canada/modules/toronto/resources.py
  modified: []
decisions:
  - "Weather prompts.py at top-level weather/ (not in sub-modules) — FileSystemProvider recursively scans so one file avoids duplicate discovery"
  - "IRCC ircc_dataset_list resource maps all 10 dataset keys to tool names — provides complete discovery catalog for agents"
  - "Toronto neighbourhood-list embeds all 140 neighbourhoods inline — avoids HTTP call to retrieve static reference data"
key-decisions:
  - "Weather prompts.py at top-level weather/ (not in sub-modules) — FileSystemProvider recursively scans so one file avoids duplicate discovery"
  - "IRCC ircc_dataset_list resource maps all 10 dataset keys to tool names — provides complete discovery catalog for agents"
  - "Toronto neighbourhood-list embeds all 140 neighbourhoods inline — avoids HTTP call to retrieve static reference data"
requirements-completed:
  - PR-14
  - PR-15
  - PR-16
  - PR-17
duration: 12min
completed: "2026-04-09"
tasks_completed: 2
files_created: 13
tests_added: 139
coverage: "96.41%"
---

# Phase 40 Plan 04: Weather, IRCC, Ontario, Toronto Prompts and Resources Summary

**21 bilingual @prompt functions and 29 zero-parameter @resource functions completing prompt/resource coverage for Weather (all 8 sub-modules), IRCC, Ontario, and Toronto.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-04-09T19:47:09Z
- **Completed:** 2026-04-09T19:59:10Z
- **Tasks:** 2
- **Files created:** 13

## Accomplishments

- Weather: 6 prompts + 8 resources at top-level `weather/` covering all 8 sub-modules (~30 tools)
- IRCC: 5 prompts + 7 resources including full dataset catalog with tool name mappings
- Ontario: 4 prompts + 6 resources including ministry directory and population projections guide
- Toronto: 6 prompts + 8 resources including 140 neighbourhood list and 25 ward list
- 139 unit tests across all 4 modules — all passing at 96.41% coverage

## Task Commits

1. **Task 1 RED: Weather + IRCC failing tests** - `2b87b5c` (test)
2. **Task 1 GREEN: Weather + IRCC prompts/resources** - `304d479` (feat)
3. **Task 2 RED: Ontario + Toronto failing tests** - `d3e906f` (test)
4. **Task 2 GREEN: Ontario + Toronto prompts/resources** - `97af69d` (feat)

## Files Created

### Weather (top-level, covers all 8 sub-modules)

- `src/mcp_canada/modules/weather/__tests__/__init__.py` - New test directory marker
- `src/mcp_canada/modules/weather/__tests__/test_prompts_resources.py` - 37 tests
- `src/mcp_canada/modules/weather/prompts.py` — 6 prompts: wx_check_weather, wx_quick_forecast, wx_analyze_climate, wx_check_air_quality, wx_water_conditions, wx_severe_weather
- `src/mcp_canada/modules/weather/resources.py` — 8 resources: province-codes, common-stations, aqhi-scale, climate-normals-periods, station-guide, climate-data-guide, ogc-api-guide, forecast-report template

### IRCC

- `src/mcp_canada/modules/ircc/__tests__/test_prompts_resources.py` - 36 tests
- `src/mcp_canada/modules/ircc/prompts.py` — 5 prompts: ircc_explore_immigration, ircc_quick_pr, ircc_track_express_entry, ircc_compare_pathways, ircc_analyze_trends
- `src/mcp_canada/modules/ircc/resources.py` — 7 resources: immigration-categories, dataset-list, express-entry-streams, work-permit-types, data-guide, xlsx-quirks, immigration-report template

### Ontario

- `src/mcp_canada/modules/ontario/__tests__/test_prompts_resources.py` - 32 tests
- `src/mcp_canada/modules/ontario/prompts.py` — 4 prompts: ontario_explore_data, ontario_quick_search, ontario_browse_ministries, ontario_population_data
- `src/mcp_canada/modules/ontario/resources.py` — 6 resources: ministries, popular-datasets, resource-formats, ckan-guide, population-projections-guide, dataset-report template

### Toronto

- `src/mcp_canada/modules/toronto/__tests__/test_prompts_resources.py` - 34 tests
- `src/mcp_canada/modules/toronto/prompts.py` — 6 prompts: toronto_explore_city_data, toronto_quick_search, toronto_explore_neighbourhood, toronto_ttc_transit, toronto_check_311, toronto_rental_analysis
- `src/mcp_canada/modules/toronto/resources.py` — 8 resources: city-divisions, ward-list (25 wards), neighbourhood-list (140 neighbourhoods), 311-service-types, ckan-guide, neighbourhood-profiles-guide, gtfs-guide, neighbourhood-report template

## Decisions Made

- **Weather prompts at top level:** `weather/prompts.py` placed at the top-level `weather/` directory (not in sub-modules). FileSystemProvider scans recursively — placing here avoids having to create 8 separate prompts.py files across sub-modules.
- **IRCC dataset catalog resource:** `data://ircc/dataset-list` maps all 10 IRCC dataset keys to their tool names and available breakdowns — gives agents a complete discovery layer without calling any tool.
- **Toronto neighbourhood list embedded inline:** All 140 official Toronto neighbourhoods embedded directly in the resource function. This avoids a live HTTP call for a stable reference dataset that changes rarely.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All 4 modules (Weather, IRCC, Ontario, Toronto) now have complete prompt + resource coverage
- Combined with Plans 01-03 (BoC, StatCan/Datastore/CKAN, Open Parliament/Recalls), all 12 active modules have prompts and resources
- Phase 40 is now complete — agents have guided workflows for every major Canadian data source

## Self-Check

### Files Exist

- src/mcp_canada/modules/weather/prompts.py: FOUND
- src/mcp_canada/modules/weather/resources.py: FOUND
- src/mcp_canada/modules/weather/__tests__/test_prompts_resources.py: FOUND
- src/mcp_canada/modules/ircc/prompts.py: FOUND
- src/mcp_canada/modules/ircc/resources.py: FOUND
- src/mcp_canada/modules/ircc/__tests__/test_prompts_resources.py: FOUND
- src/mcp_canada/modules/ontario/prompts.py: FOUND
- src/mcp_canada/modules/ontario/resources.py: FOUND
- src/mcp_canada/modules/ontario/__tests__/test_prompts_resources.py: FOUND
- src/mcp_canada/modules/toronto/prompts.py: FOUND
- src/mcp_canada/modules/toronto/resources.py: FOUND
- src/mcp_canada/modules/toronto/__tests__/test_prompts_resources.py: FOUND

### Commits

- 2b87b5c: test(40-04): add failing tests for Weather and IRCC prompts and resources
- 304d479: feat(40-04): add Weather and IRCC prompts.py and resources.py
- d3e906f: test(40-04): add failing tests for Ontario and Toronto prompts and resources
- 97af69d: feat(40-04): add Ontario and Toronto prompts.py and resources.py

### Verification Results

- All 139 new prompt/resource unit tests: PASSED
- Full suite 1599 tests: PASSED (2 skipped)
- Coverage: 96.41% (above 95% threshold)

## Self-Check: PASSED
