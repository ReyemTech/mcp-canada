---
phase: 19
slug: saskatchewan-government-open-data
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-15
---

# Phase 19 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + pytest-asyncio (existing project standard) |
| **Config file** | `pyproject.toml` (existing `[tool.pytest.ini_options]`) |
| **Quick run command** | `uv run pytest src/mcp_canada/modules/saskatchewan/__tests__/ -x -v` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Integration command** | `uv run pytest tests/integration/ -v -m integration --timeout=120 -k "Saskatchewan"` |
| **Estimated runtime** | ~30s unit (mocked); integration ~2 min live |

---

## Sampling Rate

- **After every task commit:** `uv run pytest src/mcp_canada/modules/saskatchewan/__tests__/ -x`
- **After every plan wave:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Before `/gsd:verify-work`:** Full suite + Saskatchewan live integration scenarios green
- **Max feedback latency:** ~30 seconds (unit suite)

---

## Per-Task Verification Map

| Req ID | Behavior | Test Type | Automated Command | File Exists | Status |
|--------|----------|-----------|-------------------|-------------|--------|
| SK-PRE | `shared/arcgis_hub.py` paginates with `startindex` (not `offset`) | unit (param assert) | `pytest src/mcp_canada/shared/__tests__/ -x -k "startindex or search_hub"` | ❌ W0 | ⬜ pending |
| SK-01 | Hub Search returns items; pagination via startindex | unit + live integ | `pytest .../saskatchewan/__tests__/test_tools.py::TestSaskSearchDatasets -x` | ❌ W0 | ⬜ pending |
| SK-02 | Hub item detail returns FeatureServer URL | unit | `pytest .../test_tools.py::TestSaskGetDatasetDetails -x` | ❌ W0 | ⬜ pending |
| SK-03 | Query auto-router: FeatureServer→ArcGIS, CSV/JSON→parsers | unit | `pytest .../test_tools.py::TestSaskQueryDataset -x` | ❌ W0 | ⬜ pending |
| SK-04 | Organizations list returns SK gov orgs | unit | `pytest .../test_tools.py::TestSaskListOrgs -x` | ❌ W0 | ⬜ pending |
| SK-05 | Categories list returns themes | unit | `pytest .../test_tools.py::TestSaskListCategories -x` | ❌ W0 | ⬜ pending |
| SK-06 | Crop yields: 16 crops, Provincial + 5-region dispatch | unit + live integ | `pytest .../test_tools.py::TestSaskGetCropYields -x` | ❌ W0 | ⬜ pending |
| SK-07 | Grain elevators: SK stations + capacity (PR='SK') | unit + live integ | `pytest .../test_tools.py::TestSaskGetGrainElevators -x` | ❌ W0 | ⬜ pending |
| SK-08 | Potash mines: Name/Company/Status/Mine_Type | unit + live integ | `pytest .../test_tools.py::TestSaskGetMineralMines -x -k potash` | ❌ W0 | ⬜ pending |
| SK-09 | Uranium mines: Name/Company/Status | unit + live integ | `pytest .../test_tools.py::TestSaskGetMineralMines -x` | ❌ W0 | ⬜ pending |
| SK-10 | Air quality: PM2_5/NO2/AQHI for communities | unit + live integ | `pytest .../test_tools.py::TestSaskGetAirQuality -x` | ❌ W0 | ⬜ pending |
| SK-11 | Fire bans: ban_scope dispatch (urban/rural/provincial/parks) | unit + live integ | `pytest .../test_tools.py::TestSaskGetFireBans -x` | ❌ W0 | ⬜ pending |
| SK-12 | Historic wildfires: YEAR/CAUSE1/HECTARES | unit | `pytest .../test_tools.py::TestSaskGetHistoricWildfires -x` | ❌ W0 | ⬜ pending |
| SK-13 | WSA stations: HyperLink_Graph present (catches layer-ID bug) | unit + live integ | `pytest .../test_tools.py::TestSaskGetWSAStations -x` | ❌ W0 | ⬜ pending |
| SK-14 | WSA reservoirs: layer 26, Reservoir_Name | unit + live integ | `pytest .../test_tools.py::TestSaskGetWSAReservoirs -x` | ❌ W0 | ⬜ pending |
| SK-15 | discover_tools finds saskatchewan_ tools; call_tool executes; 6 prompts + 7 resources auto-discovered | live integ | `pytest tests/integration/test_tool_scenarios.py::TestSaskatchewanToolScenarios -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] **`shared/arcgis_hub.py`** — fix `offset` → `startindex` in `search_hub_datasets` (1-line PREREQUISITE; confirmed bug). Add a param-level regression test. Run York + Alberta tests after to confirm no regression (this also fixes their latent live bug).
- [ ] `src/mcp_canada/modules/saskatchewan/__init__.py` — `MODULE_NAME`, `MODULE_DESCRIPTION`
- [ ] `src/mcp_canada/modules/saskatchewan/constants.py` — all FeatureServer URLs (two orgs: `zcv98lgAl8xQ04cW` + WSA `7MBdlVpjqbfBhQer`; SPSA `gis.saskatchewan.ca/egis`)
- [ ] `src/mcp_canada/modules/saskatchewan/__tests__/conftest.py` — Hub Search + FeatureServer fixtures (crop yields, fire bans, WSA stations, mineral mines, air quality)
- [ ] `src/mcp_canada/modules/saskatchewan/__tests__/{test_client,test_tools,test_prompts_resources}.py` — scaffolds
- [ ] `tests/integration/test_tool_scenarios.py` — append `TestSaskatchewanToolScenarios` (discovery + crop yields + fire bans + WSA stations live)
- [ ] Wave 0 spike: verify WSA Water Quality (layer 19, returned 0) + Petroleum FeatureServer (HTTP 400) before committing any tool to them — drop or discovery-only if unusable

---

## Manual-Only / Live-Required Verifications

| Behavior | Requirement | Why Manual/Live | Test Instructions |
|----------|-------------|-----------------|-------------------|
| Live FeatureServer schemas match fixtures; data is non-null | SK-06…SK-14 | Mocks masked Manitoba's live 400 — live runs are mandatory, not optional | Run `-m integration -k Saskatchewan`; assert FIELD PRESENCE + non-null values (e.g. `"Canola"` in crop yields, `HyperLink_Graph` in WSA stations), not just response shape |
| Pagination uses startindex end-to-end | SK-PRE, SK-01 | The exact class of bug that shipped in Manitoba | Param-level assertion on the outgoing request + a live paginated call returning `numberMatched > 0` |
| Fire bans empty in off-season is valid | SK-11 | Empty result is correct, not an error (like Manitoba flood alerts) | Live call returns a list (possibly empty) with valid `_meta`, never an error envelope |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers the shared/arcgis_hub.py fix + all MISSING fixtures
- [ ] Live integration tests assert FIELD PRESENCE + non-null (not just shape) — the Manitoba lesson
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
