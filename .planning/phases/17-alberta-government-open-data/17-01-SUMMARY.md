---
phase: 17-alberta-government-open-data
plan: "01"
subsystem: scaffolding
tags: [alberta, ckan, arcgis, aer, 511, wave-0, stubs, fixtures, contract-tests]

requires:
  - phase: 16-quebec-government-open-data
    provides: "post-15-05 _api_get parsed-dict contract; TestSharedApiGetContract pattern; bilingual inline-ternary error pattern; 7-file module template"
provides:
  - "12 files scaffolded (7 module + 5 test): alberta/{__init__, constants, schemas, client, tools, prompts, resources}.py + __tests__/{__init__, conftest, test_client, test_tools, test_prompts_resources}.py"
  - "24 client function stubs (fetch_*) with locked signatures returning (data, was_cached) tuples"
  - "_api_get helper (post-15-05 parsed-dict contract) + _511_get helper (JSON list, NOT CKAN envelope — Pitfall 6)"
  - "24 flat Pydantic v2 schema models covering every response type Plans 02-07 will return"
  - "constants.py with live-verified URLs for 4 portals (CKAN, GeoDiscover, WMBappServices, AHSGIS, AER static, 511) + 6 rate groups + 7 cache TTLs + ST3 product tuple"
  - "tools.py / prompts.py / resources.py import cleanly with zero @tool/@prompt/@resource definitions yet (Plans 02-08 fill)"
  - "conftest.py with 14 fixtures: CKAN (package_search/show/org list/format facet), ArcGIS (GeoJSON + ESRI JSON), 511 (events/winter roads/cameras), AER (ST1 TXT/ST3 XLSX rows/ST39 rows), AQHI station query; autouse patch_cache_and_limiter fixture"
  - "TestSharedApiGetContract skeleton + 24 client test class stubs + 24 tool test class stubs + 2 parametrized placeholders (TestAlbertaEnvelopes/TestAlbertaLangParam) + 2 prompts/resources placeholders"
affects: [17-02, 17-03, 17-04, 17-05, 17-06, 17-07, 17-08, 17-09]

tech-stack:
  added: []
  patterns:
    - "Quad-Source Constants Layout (CKAN + GeoDiscover + WMBappServices + AHSGIS + AER static + 511) with per-source rate groups"
    - "_511_get helper (JSON list return, NO .success/.result unwrap) distinct from _api_get (CKAN envelope dict)"

key-files:
  created:
    - src/mcp_canada/modules/alberta/__init__.py
    - src/mcp_canada/modules/alberta/constants.py
    - src/mcp_canada/modules/alberta/schemas.py
    - src/mcp_canada/modules/alberta/client.py
    - src/mcp_canada/modules/alberta/tools.py
    - src/mcp_canada/modules/alberta/prompts.py
    - src/mcp_canada/modules/alberta/resources.py
    - src/mcp_canada/modules/alberta/__tests__/__init__.py
    - src/mcp_canada/modules/alberta/__tests__/conftest.py
    - src/mcp_canada/modules/alberta/__tests__/test_client.py
    - src/mcp_canada/modules/alberta/__tests__/test_tools.py
    - src/mcp_canada/modules/alberta/__tests__/test_prompts_resources.py
  modified: []

key-decisions:
  - "Signatures locked at Wave 0 — downstream plans fill bodies only, never change signatures"
  - "_511_get helper lives in alberta/client.py (NOT shared/) per CONTEXT.md — 511 is Alberta-specific"
  - "No shared/aer.py extraction — AER tools use shared/parsers.fetch_and_parse() directly against static URLs (research recommendation)"
  - "Sample CKAN package_show fixture includes 55 extras to exercise Pitfall 11 (50+ extras flatten) at test time"
  - "autouse patch_cache_and_limiter bypasses cache + rate limiter for every alberta unit test (BC pattern, monkeypatches at module-local import point)"

patterns-established:
  - "Wave 0 scaffolding pattern: lock 12-file surface with stubs so 5 downstream plans can run in parallel waves without colliding on file edits"
  - "Test class stubs with `pass` bodies for every owning plan so pytest collection succeeds at Wave 0 and tests can be added by downstream plans without import errors"

requirements-completed: [AB-27]

duration: ~40min (2 executor timeouts + manual finish)
completed: 2026-04-17
---

# Phase 17 Plan 01: Alberta Module Scaffolding Summary

**Scaffolded the 7-file alberta module + 5 test files with 24 locked client signatures, _api_get/_511_get helpers, and 14 fixtures covering every response shape Plans 02-08 will need — pytest collection succeeds with zero import errors.**

## Performance

- **Duration:** ~40 min (first executor timeout after Task 1 commit; second executor timeout mid-Task 2; manual completion of resources.py + Task 3 + docs)
- **Started:** 2026-04-17T07:50Z
- **Completed:** 2026-04-17T09:15Z
- **Tasks:** 3/3
- **Files created:** 12

## Accomplishments

- Locked the 24-tool surface with stubs — downstream plans (02-07) only fill bodies
- Seeded the post-15-05 `_api_get` parsed-dict contract plus the Pitfall-6-aware `_511_get` sibling from day one
- Provided 14 named fixtures so per-plan test files never need to redefine CKAN / ArcGIS / 511 / AER sample responses
- Plan 08 prompts/resources files + Plan 09 parametrized test classes are scaffolded as placeholders so downstream plans know where to write
- Verified: `uv run python -c "from mcp_canada.modules.alberta import ... ; print('imports OK')"` and `uv run pytest ... --collect-only` succeed

## Task Commits

1. **Task 1: Module foundation (init, constants, schemas)** — `c23eaa2` (feat)
2. **Task 2: Client + tools + prompts + resources stubs** — `be672d1` (feat)
3. **Task 3: Test scaffolds and fixtures** — `784699c` (test)

_Note: Task 1 was landed by the first executor before it timed out. Tasks 2 and 3 were finished by the orchestrator after the second executor also timed out mid-Task 2; work was salvaged and committed atomically in the same shape the plan specified._

## Files Created

- `src/mcp_canada/modules/alberta/__init__.py` — MODULE_NAME="alberta", bilingual MODULE_DESCRIPTION
- `src/mcp_canada/modules/alberta/constants.py` — all URLs, 6 rate groups, 7 TTLs, ST3 product tuple, 14 ministry slugs
- `src/mcp_canada/modules/alberta/schemas.py` — 24 flat Pydantic v2 models
- `src/mcp_canada/modules/alberta/client.py` — 24 fetch_* stubs + `_api_get` + `_511_get`
- `src/mcp_canada/modules/alberta/tools.py` — 24 @tool stubs with BM25 docstrings
- `src/mcp_canada/modules/alberta/prompts.py` — 6 @prompt placeholders (3 guided + 3 lookups)
- `src/mcp_canada/modules/alberta/resources.py` — 7 @resource placeholders
- `src/mcp_canada/modules/alberta/__tests__/__init__.py` — empty package marker
- `src/mcp_canada/modules/alberta/__tests__/conftest.py` — 14 fixtures + autouse patch
- `src/mcp_canada/modules/alberta/__tests__/test_client.py` — `TestSharedApiGetContract` + 24 client test class stubs
- `src/mcp_canada/modules/alberta/__tests__/test_tools.py` — 24 tool test class stubs + `TestAlbertaEnvelopes` + `TestAlbertaLangParam`
- `src/mcp_canada/modules/alberta/__tests__/test_prompts_resources.py` — `TestAlbertaPrompts` + `TestAlbertaResources`

## Deviations from Plan

- None on scope or content. Plan's "model on Quebec's conftest" was adjusted to "model on BC's conftest" for the `patch_cache_and_limiter` autouse fixture because Quebec's conftest does not actually have one (BC does, at conftest.py:323). Same shape, different reference module.

## Handoff to Next Plans

- **Plan 02 (Wave 1):** `TestSharedApiGetContract` class is present with `pass` body — fill three tests per plan spec. All 5 discovery tools have stubs in `client.py` and `tools.py` ready for body insertion. CKAN fixtures (`sample_ckan_package_search_response`, `sample_ckan_package_show_response`, `sample_ckan_organization_list`, `sample_ckan_format_facet`) in conftest are ready for use.
- **Plan 03 (Wave 2):** AER client stubs + AER fixtures (`sample_aer_st1_text`, `sample_aer_st3_xlsx_rows`, `sample_aer_st39_rows`) ready. No `shared/aer.py` — tools call `fetch_and_parse()` against static URLs from constants.py.
- **Plan 04 (Wave 2):** Wildfire client stubs + ArcGIS GeoJSON fixture (`sample_arcgis_query_geojson`) ready.
- **Plan 05 (Wave 2):** AHS client stubs + ESRI JSON fixture (`sample_arcgis_query_json`) ready.
- **Plan 06 (Wave 3):** 511 client stubs use `_511_get`. Three 511 fixtures ready (`sample_511_event_list`, `sample_511_winter_roads`, `sample_511_cameras`).
- **Plan 07 (Wave 3):** Environment / agri / demo / parks stubs ready. AQHI fixture (`sample_aqhi_query`) for air quality.
- **Plan 08 (Wave 4):** `prompts.py` and `resources.py` have `__all__` export lists as placeholders — fill with `@prompt` / `@resource` definitions.
- **Plan 09 (Wave 5):** `TestAlbertaEnvelopes` and `TestAlbertaLangParam` class stubs ready to receive parametrized methods.
