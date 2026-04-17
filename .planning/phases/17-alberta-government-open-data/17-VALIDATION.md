---
phase: 17
slug: alberta-government-open-data
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-17
---

# Phase 17 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Sourced from `17-RESEARCH.md` § "Validation Architecture".

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio (existing) |
| **Config file** | `pyproject.toml` (existing) |
| **Quick run command** | `uv run pytest src/mcp_canada/modules/alberta/__tests__/ -x -v` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada/modules/alberta --cov-fail-under=95` |
| **Integration run** | `uv run pytest tests/integration/ -v -m integration --timeout=120 -k Alberta` |
| **Estimated runtime** | ~15 seconds (unit) / ~90 seconds (integration) |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest src/mcp_canada/modules/alberta/__tests__/ -x -v`
- **After every plan wave:** Run `uv run pytest src/mcp_canada/modules/alberta/__tests__/ src/mcp_canada/__tests__/test_quality.py -x`
- **Before `/gsd:verify-work`:** Full suite green AND integration tests green
- **Max feedback latency:** ~15 seconds (unit suite turnaround)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 17-01-XX | 01 | 0 | Wave 0 fixtures + stubs | unit | `uv run pytest src/mcp_canada/modules/alberta/__tests__/ -x` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-01 search_datasets shape | unit (mocked api_get) | `...::TestAlbertaSearchDatasets` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-01 format= filter via fq=res_format: | unit | `...::TestAlbertaSearchDatasets::test_format_filter` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-02 get_dataset_details flattens 50+ extras | unit | `...::TestAlbertaGetDatasetDetails` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-03 query_dataset routes ESRI REST → arcgis_hub | unit (mocked) | `...::TestAlbertaQueryDataset::test_routes_esri_rest_to_feature_server` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-03 query_dataset routes CSV → fetch_and_parse | unit (mocked) | `...::TestAlbertaQueryDataset::test_routes_csv_to_fetch_and_parse` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-03 query_dataset returns metadata-only for PDF/ZIP | unit | `...::TestAlbertaQueryDataset::test_pdf_returns_metadata_only` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-04 list_organizations returns 370 orgs | unit | `...::TestAlbertaListOrganizations` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-05 list_categories uses package_search facet (NOT group_list) | unit | `...::TestAlbertaListCategories::test_uses_format_facet` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-06..AB-09 AER tools (ST1, ST3, ST39 fetch from static URLs) | unit (mocked fetch_and_parse) | `...::TestAlbertaAER` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-08 ST3 invalid product → INVALID_INPUT (FR when lang=fr) | unit | `...::TestAlbertaProduction::test_invalid_product_french_error` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-10 active_fires calls correct WMB FeatureServer | unit (mocked arcgis_hub) | `...::TestAlbertaActiveFires` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-10 fire status filter passes through CQL/WHERE | unit | `...::TestAlbertaActiveFires::test_status_filter` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-11 fire_perimeters dispatches by status Literal | unit | `...::TestAlbertaFirePerimeters` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-13 fire_bans returns ban registry | unit | `...::TestAlbertaFireBans` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-15 hospitals returns 101 with IP/ED flags | unit | `...::TestAlbertaHospitals` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-17 ahs_zones returns 5 zones with population | unit | `...::TestAlbertaAhsZones` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-18 road_events calls 511 v2 endpoint correctly | unit (mocked api_get) | `...::TestAlbertaRoadEvents` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-18 road_events event_type= filter | unit | `...::TestAlbertaRoadEvents::test_event_type_filter` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-19 winter_road_conditions correct endpoint | unit | `...::TestAlbertaWinterRoadConditions` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-20 traffic_cameras returns 376 cameras | unit | `...::TestAlbertaTrafficCameras` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-21 air_quality_stations returns 75 stations | unit | `...::TestAlbertaAirQuality` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-22 water_advisories dispatches by advisory_type | unit | `...::TestAlbertaWaterAdvisories` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-25 population_estimates defaults to CSD breakdown | unit | `...::TestAlbertaPopulation` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 1+ | AB-26 provincial_parks calls GeoDiscover FeatureServer | unit | `...::TestAlbertaProvincialParks` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | last | AB-27 all 22 tools return _meta envelope | unit (parametrized) | `...::TestAlbertaEnvelopes` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | last | AB-27 all 22 tools propagate lang parameter | unit (parametrized) | `...::TestAlbertaLangParam` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 0+1 | INF _api_get treats api_get return as parsed dict | unit | `...::TestSharedApiGetContract` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | 0+1 | INF _api_get raises on success=False | unit | `...::TestSharedApiGetContract::test_ckan_success_false_raises` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | last | INF all 22 tools have 8+ Keywords + Use-for | quality (auto-discovered) | `uv run pytest src/mcp_canada/__tests__/test_quality.py -x` | ✅ exists | ⬜ pending |
| 17-XX-XX | XX | last | AB-01 INTEGRATION live search returns wildfire results | integration | `...::TestAlbertaToolScenarios -v -m integration --timeout=30 -k search` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | last | AB-10 INTEGRATION live active_fires returns _meta envelope | integration | `...::TestAlbertaToolScenarios -k active_fires` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | last | AB-15 INTEGRATION live hospitals returns ~101 hospitals | integration | `...::TestAlbertaToolScenarios -k hospitals` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | last | AB-18 INTEGRATION live road_events returns event list | integration | `...::TestAlbertaToolScenarios -k road_events` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | last | AB-09 INTEGRATION live AER ST3 Gas_current.xlsx parses | integration | `...::TestAlbertaToolScenarios -k production_volumes` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | last | AB-27 INTEGRATION discover_tools finds Alberta via BM25 | integration | `...::TestAlbertaToolScenarios -k discover` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | last | AB-27 INTEGRATION 6 prompts via client.list_prompts() | integration | `tests/integration/test_prompts_resources_scenarios.py::TestAlbertaPromptsResources` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | last | AB-27 INTEGRATION 7 resources via client.read_resource() | integration | `...::TestAlbertaPromptsResources -k resources` | ❌ W0 | ⬜ pending |
| 17-XX-XX | XX | last | INF coverage ≥ 95% for alberta module | coverage | `uv run pytest --cov=src/mcp_canada/modules/alberta --cov-fail-under=95` | runs at end | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*Task IDs (`17-XX-XX`) are placeholders — gsd-planner assigns them when PLAN.md files are created.*

---

## Wave 0 Requirements

- [ ] `src/mcp_canada/modules/alberta/__init__.py` — `MODULE_NAME = "alberta"`, bilingual `MODULE_DESCRIPTION`
- [ ] `src/mcp_canada/modules/alberta/constants.py` — all URLs (CKAN, GeoDiscover, WMB, AHS, AER, 511), rate groups, TTLs, slugs from research § "Pattern 1: Quad-Source Constants Layout"
- [ ] `src/mcp_canada/modules/alberta/schemas.py` — flat Pydantic v2 models for: dataset summary, organization, ESRI feature properties (active fire, perimeter, hospital, EMS, AHS zone, etc.), AER well licence, AER production row, AER pipeline row, 511 event, 511 winter road, 511 camera, AQHI station, water advisory, crop production row, population estimate row, provincial park
- [ ] `src/mcp_canada/modules/alberta/client.py` — 22 client functions returning `(data, was_cached)` tuples, all using `cached_fetch` + `get_limiter`
- [ ] `src/mcp_canada/modules/alberta/tools.py` — 22 `@tool` functions with BM25 docstrings (8+ keywords each), `lang: Literal["en", "fr"] = "en"` on every tool
- [ ] `src/mcp_canada/modules/alberta/prompts.py` — 6 standalone `@prompt` functions (3 guided + 3 quick lookups), bilingual
- [ ] `src/mcp_canada/modules/alberta/resources.py` — 7 zero-parameter `@resource` functions (catalogs, docs, templates), bilingual content inline
- [ ] `src/mcp_canada/modules/alberta/__tests__/conftest.py` — fixtures: sample CKAN `package_search` response (with Alberta extras quirks), sample CKAN `package_show`, sample ArcGIS REST query response (geojson + json), sample 511 event JSON list, sample AER ST1 TXT (5 lines), sample AER ST3 XLSX bytes, autouse cache+limiter patch
- [ ] `src/mcp_canada/modules/alberta/__tests__/test_client.py` — 22+ classes including `TestSharedApiGetContract`
- [ ] `src/mcp_canada/modules/alberta/__tests__/test_tools.py` — 22 test classes (5 discovery + 17 curated) plus parametrized envelope/lang tests (`TestAlbertaEnvelopes`, `TestAlbertaLangParam`)
- [ ] `src/mcp_canada/modules/alberta/__tests__/test_prompts_resources.py` — `TestAlbertaPrompts` + `TestAlbertaResources`
- [ ] `tests/integration/test_tool_scenarios.py` — append `TestAlbertaToolScenarios` class (~8 scenarios initially as xfail stubs)
- [ ] `tests/integration/test_prompts_resources_scenarios.py` — append `TestAlbertaPromptsResources` class (3 xfail stubs)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| MCP Inspector / Claude Desktop end-to-end UAT | All AB-XX | UAT requires a real MCP client; happens via `/gsd:verify-work 17` | Configure server in MCP client, run conversational test scenarios from `17-UAT.md` |
| README / docs/MODULES.md catalog accuracy | INF (docs sync) | Manual review of generated catalog formatting | Diff README against committed tool list; verify per-module docs page exists |
| BM25 discoverability of natural-language queries | AB-27 | BM25 ranking quality is qualitative, not pass/fail | Run `discover_tools(q="oil wells alberta")` etc., confirm Alberta tools rank in top 5 |

*All other phase behaviors have automated verification via the table above.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies (planner sets exact task IDs)
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (12 files listed above)
- [ ] No watch-mode flags (pytest runs once, exits)
- [ ] Feedback latency < 30s for unit suite
- [ ] `nyquist_compliant: true` set in frontmatter (after planner finalizes task IDs)

**Approval:** pending — gsd-planner replaces `17-XX-XX` task IDs with real plan/task IDs and flips `nyquist_compliant: true`
