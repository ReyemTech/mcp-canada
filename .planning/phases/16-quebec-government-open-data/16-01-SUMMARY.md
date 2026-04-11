---
phase: 16-quebec-government-open-data
plan: 01
subsystem: api
tags: [ckan, quebec, fastmcp, pydantic, mcp-tools, wave0, skeleton]

# Dependency graph
requires:
  - phase: 15-british-columbia-government-open-data
    provides: "Post-15-05 _api_get dict-contract pattern; BC 7-file module structure reference"
provides:
  - "src/mcp_canada/modules/quebec/ — 7-file module skeleton (MODULE_NAME=quebec, FileSystemProvider-ready)"
  - "constants.py with all live-verified DQ CKAN constants, MTQ WFS CSV URLs, resource IDs"
  - "12 flat Pydantic v2 schemas for all curated dataset models"
  - "20 client stub functions (Plans 02/03/04 targets) with NotImplementedError"
  - "Wave 0 test scaffolds: 105 pytest stubs (42 client + 28 tools + 14 prompts/resources + 8+3 integration xfails)"
  - "TestSharedApiGetContract class stub in test_client.py — Phase 15 lesson preserved"
affects:
  - "16-02 (discovery tools), 16-03 (health/transport tools), 16-04 (env/energy/prompts/resources)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Quebec CKAN-only module: no WFS/ArcGIS secondary portal (deferred), all data via DQ CKAN + MTQ WFS-as-CSV + datastore_search"
    - "MTQ WFS CSV-only pattern: outputformat=csv (not GeoJSON — MapServer template missing on server, HTTP 400)"
    - "Wave 0 skeleton: 7 module files + 5 test files + 2 integration appends, all stubs, pytest collection green before any implementation"

key-files:
  created:
    - src/mcp_canada/modules/quebec/__init__.py
    - src/mcp_canada/modules/quebec/constants.py
    - src/mcp_canada/modules/quebec/schemas.py
    - src/mcp_canada/modules/quebec/client.py
    - src/mcp_canada/modules/quebec/tools.py
    - src/mcp_canada/modules/quebec/prompts.py
    - src/mcp_canada/modules/quebec/resources.py
    - src/mcp_canada/modules/quebec/__tests__/__init__.py
    - src/mcp_canada/modules/quebec/__tests__/conftest.py
    - src/mcp_canada/modules/quebec/__tests__/test_client.py
    - src/mcp_canada/modules/quebec/__tests__/test_tools.py
    - src/mcp_canada/modules/quebec/__tests__/test_prompts_resources.py
  modified:
    - tests/integration/test_tool_scenarios.py
    - tests/integration/test_prompts_resources_scenarios.py
    - .planning/phases/16-quebec-government-open-data/16-VALIDATION.md

key-decisions:
  - "Quebec module is CKAN-only: no secondary geospatial portal in Phase 16; Géoportail Québec/ArcGIS deferred"
  - "MTQ WFS CSV-only: always use outputformat=csv — GeoJSON returns HTTP 400 (MapServer json.tmpl missing)"
  - "DQ metadata is French-primary: title/notes are French-only, no title_translated field; lang param affects error messages only"
  - "group_list for categories: DQ has 10 thematic groups (unlike BC which returns HTTP 403); use group_list not tag_list"
  - "SOPFEU/Hydro-Québec moved to deferred: SOPFEU not on DQ CKAN, HQ has no outage data on DQ — replaced by road events + electricity production"
  - "USER_AGENT constant from Phase 15 lesson: set mcp-canada/1.0 for identified CKAN calls"
  - "TestSharedApiGetContract patches mcp_canada.modules.quebec.client.api_get (local binding) — Phase 15 dict-vs-Response contract lesson"

patterns-established:
  - "Quebec _api_get MUST follow post-15-05 pattern: treat api_get return as parsed dict, check isinstance+success, never .raise_for_status()/.json()"
  - "Bilingual ternary inline (not t() import): lang == 'fr' ternary for all error messages and MTQ CSV column selection"
  - "MTQ CSV bilingual columns: descriptionFrancais/descriptionAnglais for road works; DescriptionEtatChausseeFR/EN for road conditions"
  - "Bridge structures guard: require at least one filter before fetch (same pattern as bc_get_water_wells 130K guard)"

requirements-completed: []

# Metrics
duration: 5min
completed: 2026-04-11
---

# Phase 16 Plan 01: Quebec Module Skeleton Summary

**Quebec CKAN module skeleton with 7 files, 12 flat Pydantic schemas, 20 client stubs, and 105 Wave 0 pytest stubs targeting Plans 02/03/04 node IDs**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-11T05:32:45Z
- **Completed:** 2026-04-11T05:37:44Z
- **Tasks:** 2
- **Files modified:** 15

## Accomplishments

- Created full 7-file Quebec module skeleton with `MODULE_NAME = "quebec"` — auto-registers via FileSystemProvider
- Materialized all live-verified constants from 16-RESEARCH.md: DQ CKAN BASE_URL, MTQ WFS CSV URLs, datastore resource IDs, org slugs, USER_AGENT
- Defined 12 flat Pydantic v2 models covering all curated dataset types (installations, ER waits, population, road works/events/bridges/conditions, AQ stations, organizations, categories)
- Created 105 Wave 0 pytest stubs (42 client + 28 tools + 14 prompts/resources + 11 integration xfails) with concrete class names Plans 02/03/04 can reference as node IDs
- Applied Phase 15 lessons from day 1: `TestSharedApiGetContract` stub in test_client.py, `prompts.py` import fixed to match BC pattern (`from fastmcp.prompts import Message, prompt`)

## Task Commits

1. **Task 1: Quebec module skeleton** - `9140462` (feat)
2. **Task 2: Wave 0 test scaffolds** - `0ebccdc` (test)

## Files Created/Modified

- `src/mcp_canada/modules/quebec/__init__.py` — MODULE_NAME=quebec, MODULE_DESCRIPTION
- `src/mcp_canada/modules/quebec/constants.py` — BASE_URL, MTQ_WFS_BASE, USER_AGENT, DEFAULT_HEADERS, RATE_GROUP/LIMIT, CACHE_TTL_*, ORG_* slugs, resource IDs, MTQ WFS CSV URLs
- `src/mcp_canada/modules/quebec/schemas.py` — 12 flat Pydantic v2 models
- `src/mcp_canada/modules/quebec/client.py` — 20 stub async functions (NotImplementedError + Plan breadcrumbs); real api_get import
- `src/mcp_canada/modules/quebec/tools.py` — empty scaffold with standalone @tool import
- `src/mcp_canada/modules/quebec/prompts.py` — empty scaffold with `from fastmcp.prompts import Message, prompt`
- `src/mcp_canada/modules/quebec/resources.py` — empty scaffold with standalone @resource import
- `src/mcp_canada/modules/quebec/__tests__/conftest.py` — 11 fixtures (CKAN search/show/org/group, datastore ER/installations/AQ, MTQ CSV road works/events/bridges, MAMH municipalities, CKAN error)
- `src/mcp_canada/modules/quebec/__tests__/test_client.py` — TestSharedApiGetContract (3 stubs) + 17 client test class stubs
- `src/mcp_canada/modules/quebec/__tests__/test_tools.py` — 18 tool test class stubs (5 discovery + 13 curated)
- `src/mcp_canada/modules/quebec/__tests__/test_prompts_resources.py` — 2 class stubs (6 prompts + 7 resources)
- `tests/integration/test_tool_scenarios.py` — TestQuebecToolScenarios appended (8 xfail stubs)
- `tests/integration/test_prompts_resources_scenarios.py` — TestQuebecPromptsResources appended (3 xfail stubs)
- `.planning/phases/16-quebec-government-open-data/16-VALIDATION.md` — wave_0_complete flipped to true, tasks 16-01-01/02 marked green

## Decisions Made

- `fastmcp.prompts.prompt.Message` import path doesn't resolve in this project — corrected to `from fastmcp.prompts import Message, prompt` (matches BC reference)
- Wave 0 `TestQuebecResources` has sync `def test_*` methods under `pytestmark = pytest.mark.asyncio` (matching BC pattern) — 7 pytest warnings, no failures

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed prompts.py Message import path**
- **Found during:** Task 1 (pyright verification)
- **Issue:** Plan specified `from fastmcp.prompts.prompt import Message` — pyright reported `Import "fastmcp.prompts.prompt" could not be resolved`
- **Fix:** Changed to `from fastmcp.prompts import Message, prompt` matching the BC reference module
- **Files modified:** `src/mcp_canada/modules/quebec/prompts.py`
- **Verification:** `uv run pyright src/mcp_canada/modules/quebec/` → 0 errors
- **Committed in:** `9140462` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Necessary for pyright green. No scope creep.

## Issues Encountered

None beyond the import path fix documented above.

## Next Phase Readiness

- All 7 module files exist and import cleanly
- 105 Wave 0 test stubs with concrete pytest node IDs ready for Plans 02/03/04 to target
- All constants materialized from 16-RESEARCH.md — Plans 02/03/04 import directly
- wave_0_complete: true in 16-VALIDATION.md

---
*Phase: 16-quebec-government-open-data*
*Completed: 2026-04-11*
