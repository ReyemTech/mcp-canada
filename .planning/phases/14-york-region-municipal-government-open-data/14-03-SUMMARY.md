---
phase: 14-york-region-municipal-government-open-data
plan: 03
subsystem: york_region
tags: [arcgis-hub, prompts, resources, mcp-prompts, york-region, markham, integration-tests, readme]
dependency_graph:
  requires:
    - phase: 14-02
      provides: [modules/york_region/tools.py — 27 @tool functions]
    - phase: 14-01
      provides: [modules/york_region/client.py, shared/arcgis_hub.py]
  provides:
    - modules/york_region/prompts.py — 5 bilingual @prompt functions
    - modules/york_region/resources.py — 8 zero-parameter @resource functions
    - tests/integration/TestYorkRegionToolScenarios — 8 integration test scenarios
    - tests/integration/TestYorkRegionPromptsResources — 3 integration test scenarios
    - README.md York Region section with 27 tools listed
    - REQUIREMENTS.md YR-01..YR-14 definitions + traceability rows
  affects: [Phase 15 (BC Open Data), future ArcGIS Hub modules]
tech_stack:
  added: []
  patterns: [Zero-parameter resources with inline bilingual content, guided workflow prompts with list[Message], quick lookup prompts returning str]
key_files:
  created:
    - src/mcp_canada/modules/york_region/prompts.py
    - src/mcp_canada/modules/york_region/resources.py
    - src/mcp_canada/modules/york_region/__tests__/test_prompts_resources.py
  modified:
    - tests/integration/test_tool_scenarios.py
    - tests/integration/test_prompts_resources_scenarios.py
    - README.md
    - .planning/REQUIREMENTS.md
key-decisions:
  - "york_region_quick_dataset_search takes an extra query: str parameter — quick lookups can accept parameters alongside lang"
  - "Resources embed bilingual content inline (all 10 portals catalog, EN+FR notes per entry) — avoids lang parameter which would make them ResourceTemplate"
  - "pyright errors in test files are pre-existing pattern identical to toronto tests (FunctionResource.read() type ambiguity) — production code has 0 errors"
requirements-completed: [YR-12, YR-13, YR-14]
duration: 10min
completed: "2026-04-10"
---

# Phase 14 Plan 03: York Region Prompts, Resources, and Documentation Summary

**5 bilingual @prompt functions + 8 zero-parameter @resource functions completing the 7-file York Region module, with 11 integration test scenarios, README York Region section, and YR-01..YR-14 requirements defined.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-04-10T16:15:00Z
- **Completed:** 2026-04-10T16:25:30Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- Created prompts.py with 5 bilingual @prompt functions (4 guided workflows + 1 quick lookup) covering transit, census, health, and Markham infrastructure workflows
- Created resources.py with 8 zero-parameter @resource functions across all three URI schemes (data://, docs://, template://)
- Added 17 unit tests for prompts and resources — all passing
- Added TestYorkRegionToolScenarios (8 integration scenarios) and TestYorkRegionPromptsResources (3 scenarios)
- Updated README with York Region section (27 tools, 5 prompts, 8 resources) and incremented counts
- Defined YR-01..YR-14 requirements in REQUIREMENTS.md with 14 traceability rows
- Full test suite: 1,754 tests passing, coverage 96.56%

## Task Commits

1. **Task 1: Create prompts.py + resources.py + unit tests** - `41af6cc` (feat)
2. **Task 2: Integration tests + README + REQUIREMENTS.md finalization** - `1df0b71` (feat)

## Files Created/Modified

- `src/mcp_canada/modules/york_region/prompts.py` — 5 @prompt functions: york_region_explore_transit, york_region_explore_census, york_region_explore_health, york_region_quick_dataset_search, markham_explore_infrastructure
- `src/mcp_canada/modules/york_region/resources.py` — 8 @resource functions: portals catalog, municipalities list, feature_services catalog, esri-field-naming guide, portal-landscape guide, census-variables guide, arcgis-query-patterns guide, transit response template
- `src/mcp_canada/modules/york_region/__tests__/test_prompts_resources.py` — 17 unit tests covering all prompts and resources
- `tests/integration/test_tool_scenarios.py` — TestYorkRegionToolScenarios class with 8 integration scenarios
- `tests/integration/test_prompts_resources_scenarios.py` — TestYorkRegionPromptsResources class with 3 scenarios
- `README.md` — York Region section (tool catalog + prompt catalog + resource catalog); tool count updated to 155; ArcGIS Hub noted as first module
- `.planning/REQUIREMENTS.md` — YR-01..YR-14 requirement definitions + 14 traceability rows + coverage count updated

## Decisions Made

- `york_region_quick_dataset_search` takes both `query: str` and `lang` — quick lookup prompts can accept content parameters alongside lang, unlike resources which must be zero-parameter
- Resources embed bilingual content inline (e.g., name_en + name_fr fields per portal entry, note_en + note_fr) — avoids adding lang parameter which would convert FunctionResource to ResourceTemplate and remove from resources/list
- pyright test file errors are the same pre-existing pattern as Toronto module tests (FunctionResource.read() returns bytes | str | ResourceResult type ambiguity in newer FastMCP) — production code pyright: 0 errors, 0 warnings

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

York Region module is complete with the full 7-file pattern. Phase 14 is done. Phase 15 (British Columbia Government Open Data) can begin — it will reuse `shared/arcgis_hub.py` if BC publishes via ArcGIS Hub.

---
*Phase: 14-york-region-municipal-government-open-data*
*Completed: 2026-04-10*

## Self-Check

### Files Created

- [x] `src/mcp_canada/modules/york_region/prompts.py` — created (5 @prompt functions)
- [x] `src/mcp_canada/modules/york_region/resources.py` — created (8 @resource functions)
- [x] `src/mcp_canada/modules/york_region/__tests__/test_prompts_resources.py` — created (17 tests)

### Commits

- [x] 41af6cc — feat(14-03): add york_region prompts.py + resources.py with unit tests
- [x] 1df0b71 — feat(14-03): add integration tests, update README and REQUIREMENTS.md

### Verification

- [x] 136 york_region unit tests pass
- [x] 1,754 total tests pass
- [x] Coverage 96.56% (>= 95% required)
- [x] ruff: all checks passed
- [x] pyright production code: 0 errors, 0 warnings

## Self-Check: PASSED
