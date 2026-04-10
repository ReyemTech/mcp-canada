---
phase: 15
slug: british-columbia-government-open-data
status: wave-0-complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-10
updated: 2026-04-10
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (with pytest-asyncio, pytest-cov) |
| **Config file** | `pyproject.toml` (existing — no install needed) |
| **Quick run command** | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/ -x -q` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Estimated runtime** | ~45 seconds (unit) / ~90 seconds (full w/ coverage) |

---

## Sampling Rate

- **After every task commit:** Run quick run command (module-scoped unit tests)
- **After every plan wave:** Run full suite command
- **Before `/gsd:verify-work`:** Full suite must be green AND integration tests pass (`-m integration --timeout=120`)
- **Max feedback latency:** 90 seconds

---

## Per-Task Verification Map

*Populated by Plan 01 Wave 0 execution. Every task maps to a test command.*

| Task ID | Plan | Wave | Requirement/Concern | Test Type | Automated Command | File Exists | Status |
|---------|------|------|---------------------|-----------|-------------------|-------------|--------|
| 15-01-01 | 01 | 1 | shared/ogc.py WFS client | unit | `uv run pytest src/mcp_canada/shared/__tests__/test_ogc.py -x` | ✅ | ✅ green |
| 15-01-02 | 01 | 1 | bc module skeleton imports | unit | `uv run python -c "from mcp_canada.modules import british_columbia; print(british_columbia.MODULE_NAME)"` | ✅ | ✅ green |
| 15-01-03 | 01 | 1 | Wave 0 test stubs collect | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/ --collect-only -q` | ✅ | ✅ green |
| 15-02-01 | 02 | 2 | bc_search_datasets tool | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcSearchDatasets -x` | ✅ | ✅ green |
| 15-02-02 | 02 | 2 | bc_get_dataset_details + queryable_via_wfs | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetDatasetDetails -x` | ✅ | ✅ green |
| 15-02-03 | 02 | 2 | bc_query_features routing | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcQueryFeatures -x` | ✅ | ✅ green |
| 15-02-04 | 02 | 2 | bc_list_organizations | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcListOrganizations -x` | ✅ | ✅ green |
| 15-02-05 | 02 | 2 | bc_list_categories | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcListCategories -x` | ✅ | ✅ green |
| 15-02-06 | 02 | 2 | fetch_search_datasets client | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_client.py::TestFetchSearchDatasets -x` | ✅ | ✅ green |
| 15-02-07 | 02 | 2 | fetch_dataset_details + WFS detection | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_client.py::TestQueryableViaWfsDetection -x` | ✅ | ✅ green |
| 15-03-01 | 03 | 3 | bc_get_active_fires | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetActiveFires -x` | ✅ | ⬜ pending |
| 15-03-02 | 03 | 3 | bc_get_fire_perimeters | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetFirePerimeters -x` | ✅ | ⬜ pending |
| 15-03-03 | 03 | 3 | bc_get_forest_tenure | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetForestTenure -x` | ✅ | ⬜ pending |
| 15-03-04 | 03 | 3 | bc_get_cut_blocks | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetCutBlocks -x` | ✅ | ⬜ pending |
| 15-03-05 | 03 | 3 | bc_get_protected_areas | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetProtectedAreas -x` | ✅ | ⬜ pending |
| 15-03-06 | 03 | 3 | bc_get_water_wells (130K guard) | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetWaterWells -x` | ✅ | ⬜ pending |
| 15-03-07 | 03 | 3 | bc_get_wildfire_weather_stations | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetWildfireWeatherStations -x` | ✅ | ⬜ pending |
| 15-03-08 | 03 | 3 | bc_get_local_parks | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetLocalParks -x` | ✅ | ⬜ pending |
| 15-03-09 | 03 | 3 | bc_get_mining_tenure | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetMiningTenure -x` | ✅ | ⬜ pending |
| 15-03-10 | 03 | 3 | bc_get_fish_habitat | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetFishHabitat -x` | ✅ | ⬜ pending |
| 15-03-11 | 03 | 3 | bc_get_emergency_rooms | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetEmergencyRooms -x` | ✅ | ⬜ pending |
| 15-03-12 | 03 | 3 | bc_get_walk_in_clinics | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetWalkInClinics -x` | ✅ | ⬜ pending |
| 15-03-13 | 03 | 3 | bc_get_highway_profiles | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetHighwayProfiles -x` | ✅ | ⬜ pending |
| 15-03-14 | 03 | 3 | bc_get_road_structures | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetRoadStructures -x` | ✅ | ⬜ pending |
| 15-03-15 | 03 | 3 | bc_get_climate_stations | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py::TestBcGetClimateStations -x` | ✅ | ⬜ pending |
| 15-03-16 | 03 | 3 | _wfs_fetch shared helper | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_client.py::TestWfsFetchShared -x` | ✅ | ⬜ pending |
| 15-04-01 | 04 | 4 | bc prompts (6) | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_prompts_resources.py::TestBcPrompts -x` | ✅ | ⬜ pending |
| 15-04-02 | 04 | 4 | bc resources (7) | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_prompts_resources.py::TestBcResources -x` | ✅ | ⬜ pending |
| 15-04-03 | 04 | 4 | bc integration scenarios | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestBcToolScenarios -m integration --timeout=120` | ✅ | ⬜ pending |
| 15-04-04 | 04 | 4 | bc prompts/resources integration | integration | `uv run pytest tests/integration/test_prompts_resources_scenarios.py::TestBcPromptsResources -m integration --timeout=120` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Test stubs that must exist before implementation tasks can run:

- [x] `src/mcp_canada/shared/__tests__/test_ogc.py` — WFS client unit tests (GetFeature, CQL, pagination, XML error parsing)
- [x] `src/mcp_canada/modules/british_columbia/__tests__/__init__.py`
- [x] `src/mcp_canada/modules/british_columbia/__tests__/conftest.py` — sample CKAN + WFS responses (12 fixtures)
- [x] `src/mcp_canada/modules/british_columbia/__tests__/test_client.py` — 6 client function test class scaffolds
- [x] `src/mcp_canada/modules/british_columbia/__tests__/test_tools.py` — 20 tool test class scaffolds (5 CKAN + 15 curated)
- [x] `src/mcp_canada/modules/british_columbia/__tests__/test_prompts_resources.py` — 2 prompt/resource class scaffolds
- [x] `tests/integration/test_tool_scenarios.py::TestBcToolScenarios` — 8 xfail placeholder methods
- [x] `tests/integration/test_prompts_resources_scenarios.py::TestBcPromptsResources` — 3 xfail placeholder methods

Wave 0 complete as of Plan 01 execution on 2026-04-10.

Framework is already installed; Wave 0 = test file scaffolding only.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| README.md tool catalog updated | modules.md rule | File-level assertion, not functional | `grep -c "bc_" README.md` must match tool count |
| CLAUDE.md notes WFS as third portal tech | CLAUDE.md rule | Documentation drift | Visual review during PR |
| Live WFS endpoint availability | curated tools | External dependency; can flake | Integration tests cover it with `-m integration`; manual re-run on red |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 90s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** Plan 01 Wave 0 complete — 2026-04-10
