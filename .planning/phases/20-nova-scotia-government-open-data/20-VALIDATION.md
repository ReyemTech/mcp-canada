---
phase: 20
slug: nova-scotia-government-open-data
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-15
---

# Phase 20 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + pytest-asyncio (existing project standard) |
| **Config file** | `pyproject.toml` (existing `[tool.pytest.ini_options]`) |
| **Quick run command** | `uv run pytest src/mcp_canada/modules/nova_scotia/__tests__/ src/mcp_canada/shared/__tests__/test_socrata.py -x -v` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Integration command** | `uv run pytest tests/integration/ -v -m integration --timeout=120 -k "NovaScotia"` |
| **Estimated runtime** | ~30s unit (mocked); integration ~3 min live |

---

## Sampling Rate

- **After every task commit:** `uv run pytest src/mcp_canada/modules/nova_scotia/__tests__/ src/mcp_canada/shared/__tests__/test_socrata.py -x`
- **After every plan wave:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Before `/gsd:verify-work`:** Full suite + Nova Scotia live integration scenarios green
- **Max feedback latency:** ~30 seconds (unit suite)

---

## Per-Task Verification Map

| Req ID | Behavior | Test Type | Automated Command | File Exists | Status |
|--------|----------|-----------|-------------------|-------------|--------|
| NS-01 (W0 prereq) | shared/socrata.py sends correct SoQL/catalog params (contract) | unit (contract) | `pytest src/mcp_canada/shared/__tests__/test_socrata.py::TestSharedSocrataContract -x` | ❌ W0 | ⬜ pending |
| NS-01 | search_catalog returns results + resultSetSize; query_dataset; get_dataset_metadata | unit | `pytest .../test_socrata.py -x` | ❌ W0 | ⬜ pending |
| NS-02 | ns_search_datasets returns id/name/category | unit + live integ | `pytest .../nova_scotia/__tests__/test_tools.py::TestNsSearchDatasets -x` | ❌ W0 | ⬜ pending |
| NS-03 | ns_get_dataset_details returns schema columns | unit | `pytest .../test_tools.py::TestNsGetDatasetDetails -x` | ❌ W0 | ⬜ pending |
| NS-04 | ns_query_dataset executes SoQL with _meta envelope | unit | `pytest .../test_tools.py::TestNsQueryDataset -x` | ❌ W0 | ⬜ pending |
| NS-05 | ns_list_organizations returns publisher/attribution names | unit | `pytest .../test_tools.py::TestNsListOrganizations -x` | ❌ W0 | ⬜ pending |
| NS-06 | ns_list_categories returns 20+ categories (client-side filter; categories= param is broken) | unit + live integ | `pytest .../test_tools.py::TestNsListCategories -x` | ❌ W0 | ⬜ pending |
| NS-07 | Marine leases: license_le/ownership/species/county non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetMarineAquacultureLeases -x` | ❌ W0 | ⬜ pending |
| NS-08 | Landbased licenses: license_le/speciestyp/county non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetLandbasedAquacultureLicenses -x` | ❌ W0 | ⬜ pending |
| NS-09 | Hatchery stocking: stock/county/number_released/stocking_date non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetFishHatcheryStocking -x` | ❌ W0 | ⬜ pending |
| NS-10 | Aquaculture production: year/county/kgs/total_value non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetAquacultureProduction -x` | ❌ W0 | ⬜ pending |
| NS-11 | Water quality: station_number/date/temperature_c non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetWaterQualityMonitoring -x` | ❌ W0 | ⬜ pending |
| NS-12 | Boil water: site_name/county/date_advisory_issued non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetBoilWaterAdvisories -x` | ❌ W0 | ⬜ pending |
| NS-13 | Health facilities: facility_name/county/type non-null; facility_type dispatch | unit + live integ | `pytest .../test_tools.py::TestNsGetHealthFacilities -x` | ❌ W0 | ⬜ pending |
| NS-14 | Vital stats: counties/year/population/live_births non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetVitalStatistics -x` | ❌ W0 | ⬜ pending |
| NS-15 | Protected areas: pro_name/protect1/owner/status non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetProtectedAreas -x` | ❌ W0 | ⬜ pending |
| NS-16 | Air quality stations: station_name/latitude/longitude non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetAirQualityStations -x` | ❌ W0 | ⬜ pending |
| NS-17 | Chronic disease: year/zone/crude_prevalence_rate non-null; invalid disease → INVALID_INPUT | unit + live integ | `pytest .../test_tools.py::TestNsGetChronicDiseasePrevalence -x` | ❌ W0 | ⬜ pending |
| NS-18 | discover_tools finds ns_ tools; 6 prompts + 7 resources auto-discovered | live integ | `pytest tests/integration/test_tool_scenarios.py::TestNovaScotiaToolScenarios -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] **`src/mcp_canada/shared/socrata.py`** — reusable SODA client (`search_catalog`, `get_dataset_metadata`, `query_dataset`, category helper). PREREQUISITE before any nova_scotia tool. Returns parsed dicts (api_get contract). 4th portal technology.
- [ ] **`src/mcp_canada/shared/__tests__/test_socrata.py`** — incl. `TestSharedSocrataContract` (assert outgoing SoQL/catalog params, not just URL — the Manitoba/Saskatchewan lesson)
- [ ] `src/mcp_canada/modules/nova_scotia/{__init__,constants,schemas,client,tools,prompts,resources}.py` + `__tests__/` scaffolds with dataset-ID constants
- [ ] `tests/integration/test_tool_scenarios.py` — append `TestNovaScotiaToolScenarios` (live field-presence)
- [ ] `tests/integration/test_prompts_resources_scenarios.py` — append NS prompts/resources
- [ ] **Wave 0 spikes** (resolve before curating those tools): rockweed leases `exhe-htib` (may be geometry-only → drop or discovery-only); boil-water active filter (`date_advisory_removed` NULL vs empty string); chronic-disease field-name normalization (`health_zone` vs `zone` across the 5 disease datasets)

---

## Manual-Only / Live-Required Verifications

| Behavior | Requirement | Why Live | Test Instructions |
|----------|-------------|----------|-------------------|
| SODA endpoints + SoQL params work against the real portal | NS-01…NS-17 | Mocks masked Manitoba's live 400; Socrata `categories=` param silently returns 0 | Run `-m integration -k NovaScotia`; assert FIELD PRESENCE + non-null on the documented columns (license_le, stock, number_released, crude_prevalence_rate, etc.) — NOT just `_meta` exists |
| list_categories returns 20+ real categories | NS-06 | The `categories=` catalog param is broken (returns 0) — must use `q=` + client-side `classification.domain_category` filter; only a live call proves the workaround | Live call asserts ≥20 category strings incl. "Fishing and Aquaculture" |
| Geometry columns excluded via explicit $select | NS-07, NS-15 | Geo-bearing datasets return huge `the_geom` blobs unless $select trims them | Live response asserts `the_geom` NOT in flattened rows |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers shared/socrata.py + contract test + all fixtures + the 3 spikes
- [ ] Live integration tests assert FIELD PRESENCE + non-null (the Manitoba lesson)
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
