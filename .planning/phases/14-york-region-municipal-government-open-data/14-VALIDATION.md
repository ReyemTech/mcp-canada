---
phase: 14
slug: york-region-municipal-government-open-data
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-10
---

# Phase 14 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x with pytest-asyncio (existing) |
| **Config file** | `pyproject.toml` (existing) |
| **Quick run command** | `uv run pytest src/mcp_canada/modules/york_region/ src/mcp_canada/shared/__tests__/test_arcgis_hub.py -x -v` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest src/mcp_canada/modules/york_region/ src/mcp_canada/shared/__tests__/test_arcgis_hub.py -x`
- **After every plan wave:** Run `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 14-01-01 | 01 | 1 | Shared ArcGIS Hub client | unit | `uv run pytest src/mcp_canada/shared/__tests__/test_arcgis_hub.py -x -v` | ❌ W0 | ⬜ pending |
| 14-01-02 | 01 | 1 | York Region module skeleton + constants + client | unit | `uv run pytest src/mcp_canada/modules/york_region/__tests__/test_client.py -x -v` | ❌ W0 | ⬜ pending |
| 14-02-01 | 02 | 2 | Discovery tools (4 portals × 5 = 20 tools) | unit | `uv run pytest src/mcp_canada/modules/york_region/__tests__/test_tools.py::TestDiscoveryTools -x -v` | ❌ W0 | ⬜ pending |
| 14-02-02 | 02 | 2 | Curated tools (York Region 5 + Markham 2 = 7 tools) | unit | `uv run pytest src/mcp_canada/modules/york_region/__tests__/test_tools.py::TestCuratedTools -x -v` | ❌ W0 | ⬜ pending |
| 14-02-03 | 02 | 2 | Prompts + Resources + integration tests + README | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestYorkRegionToolScenarios -v -m integration` | ❌ W0 | ⬜ pending |
| 14-02-04 | 02 | 2 | Coverage gate | coverage | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `src/mcp_canada/shared/__tests__/test_arcgis_hub.py` — shared client unit tests
- [ ] `src/mcp_canada/modules/york_region/__tests__/__init__.py`
- [ ] `src/mcp_canada/modules/york_region/__tests__/conftest.py` — fixtures (sample Hub search response, sample FeatureServer GeoJSON, sample layer metadata)
- [ ] `src/mcp_canada/modules/york_region/__tests__/test_client.py`
- [ ] `src/mcp_canada/modules/york_region/__tests__/test_tools.py`
- [ ] `src/mcp_canada/modules/york_region/__tests__/test_prompts_resources.py`
- [ ] `tests/integration/test_tool_scenarios.py` — append `TestYorkRegionToolScenarios` class
- [ ] `tests/integration/test_prompts_resources_scenarios.py` — add york_region prompt/resource assertions

*Existing infrastructure covers framework and quality gates.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Hub Search API returns real data for all 4 portals | Discovery | Depends on live portal availability | Run integration tests with `-m integration --timeout=120` |
| YRT/Viva bus stops query returns 4,810 records | Curated | Depends on live Feature Service | Call `york_region_get_bus_stops()` via Client and verify count |
| York Region census data returns 2021 DA-level records | Curated | Depends on ArcGIS Online service | Call `york_region_get_census_demographics()` via Client |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
