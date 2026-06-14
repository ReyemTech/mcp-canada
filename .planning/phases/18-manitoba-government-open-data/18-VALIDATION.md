---
phase: 18
slug: manitoba-government-open-data
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-13
---

# Phase 18 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (existing project standard) |
| **Config file** | `pyproject.toml` (existing `[tool.pytest.ini_options]`) |
| **Quick run command** | `uv run pytest src/mcp_canada/modules/manitoba/__tests__/ -x -v` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Estimated runtime** | ~30 seconds (unit, mocked); integration ~2 min live |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest src/mcp_canada/modules/manitoba/__tests__/ -x`
- **After every plan wave:** Run `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Before `/gsd:verify-work`:** Full suite + Manitoba integration tests must be green
- **Max feedback latency:** ~30 seconds (unit suite)

---

## Per-Task Verification Map

| Req ID | Behavior | Test Type | Automated Command | File Exists | Status |
|--------|----------|-----------|-------------------|-------------|--------|
| MB-01 | Hub search returns datasets list | unit | `pytest .../manitoba/__tests__/test_tools.py::TestManitobaSearchDatasets -x` | ❌ W0 | ⬜ pending |
| MB-02 | Dataset details returns FeatureServer URLs | unit | `pytest .../test_tools.py::TestManitobaGetDatasetDetails -x` | ❌ W0 | ⬜ pending |
| MB-03 | Query dataset auto-routes to arcgis_hub | unit | `pytest .../test_tools.py::TestManitobaQueryDataset -x` | ❌ W0 | ⬜ pending |
| MB-04 | List organizations returns Hub orgs | unit | `pytest .../test_tools.py::TestManitobaListOrgs -x` | ❌ W0 | ⬜ pending |
| MB-05 | List categories returns Hub tags | unit | `pytest .../test_tools.py::TestManitobaListCategories -x` | ❌ W0 | ⬜ pending |
| MB-06 | Parks returns 93 parks w/ bilingual names | unit + integ | `pytest .../test_tools.py::TestManitobaGetParks -x` | ❌ W0 | ⬜ pending |
| MB-07 | Flood alerts returns polygons (or empty when none) | unit + integ | `pytest .../test_tools.py::TestManitobaGetFloodAlerts -x` | ❌ W0 | ⬜ pending |
| MB-08 | River stations returns points w/ flood status | unit | `pytest .../test_tools.py::TestManitobaGetRiverStations -x` | ❌ W0 | ⬜ pending |
| MB-09 | Provincial waterways returns typed features | unit | `pytest .../test_tools.py::TestManitobaGetWaterways -x` | ❌ W0 | ⬜ pending |
| MB-10 | Drought status returns D0–D4 polygons | unit | `pytest .../test_tools.py::TestManitobaGetDroughtStatus -x` | ❌ W0 | ⬜ pending |
| MB-11 | Ag weather stations returns 100+ w/ AgRegion+URL | unit + integ | `pytest .../test_tools.py::TestManitobaGetAgWeatherStations -x` | ❌ W0 | ⬜ pending |
| MB-12 | Livestock prices returns weekly cattle/hog prices | unit | `pytest .../test_tools.py::TestManitobaGetLivestockPrices -x` | ❌ W0 | ⬜ pending |
| MB-13 | Crop regions returns bilingual region polygons | unit | `pytest .../test_tools.py::TestManitobaGetCropRegions -x` | ❌ W0 | ⬜ pending |
| MB-14 | Surgical wait times returns procedure/year/days | unit + integ | `pytest .../test_tools.py::TestManitobaGetWaitTimes -x` | ❌ W0 | ⬜ pending |
| MB-15 | Fisheries data returns waterbodies w/ species/regs | unit | `pytest .../test_tools.py::TestManitobaGetFisheriesData -x` | ❌ W0 | ⬜ pending |
| MB-16 | Provincial forests returns admin forest boundaries | unit | `pytest .../test_tools.py::TestManitobaGetForests -x` | ❌ W0 | ⬜ pending |
| MB-17 (cond.) | 511 events returns road events (NOT_CONFIGURED w/o key) | unit (mocked) | `pytest .../test_tools.py::TestManitoba511 -x -k "not integration"` | ❌ W0 | ⬜ pending |
| MB-18 | All tools discoverable via discover_tools through MCP Client | integration | `uv run pytest tests/integration/ -m integration --timeout=120 -k "Manitoba"` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `src/mcp_canada/modules/manitoba/__tests__/conftest.py` — ArcGIS Hub JSON fixtures for all curated FeatureServers
- [ ] `src/mcp_canada/modules/manitoba/__tests__/test_client.py` — client unit tests + `TestSharedApiGetContract`
- [ ] `src/mcp_canada/modules/manitoba/__tests__/test_tools.py` — tool unit tests (incl. flood-alert empty-response edge case)
- [ ] `src/mcp_canada/modules/manitoba/__tests__/test_prompts_resources.py` — prompts/resources tests
- [ ] `tests/integration/test_tool_scenarios.py::TestManitobaToolScenarios` — integration via MCP Client
- [ ] `tests/integration/test_prompts_resources_scenarios.py::TestManitobaPromptsResources` — prompts/resources integration
- [ ] Wave 0 spike: confirm Manitoba 511 developer-key obtainability + resolve rural-health/hog-price/river-conditions FeatureServer URLs

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live FeatureServer schemas match mocked fixtures | MB-06…MB-16 | Upstream ArcGIS schemas can drift; live data changes daily | Run Manitoba integration tests with `-m integration`; assert on response shape, not values |
| Manitoba 511 live road events | MB-17 | Requires a provisioned developer key (env var) | If key obtained in Wave 0, run 511 integration test; else tool ships returning `NOT_CONFIGURED` and is verified via mocked unit test only |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
