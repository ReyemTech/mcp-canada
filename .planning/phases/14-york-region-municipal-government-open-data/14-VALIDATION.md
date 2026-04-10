---
phase: 14
slug: york-region-municipal-government-open-data
status: approved
nyquist_compliant: true
wave_0_complete: true
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
| 14-01-01 | 01 | 1 | Shared ArcGIS Hub client (TDD) | unit | `uv run pytest src/mcp_canada/shared/__tests__/test_arcgis_hub.py -x -v` | TDD-created | ⬜ pending |
| 14-01-02 | 01 | 1 | York Region module skeleton + constants + client (TDD) | unit | `uv run pytest src/mcp_canada/modules/york_region/__tests__/test_client.py -x -v` | TDD-created | ⬜ pending |
| 14-02-01 | 02 | 2 | 28 tools: 20 discovery + 6 YR curated + 2 Markham curated (TDD) | unit | `uv run pytest src/mcp_canada/modules/york_region/__tests__/test_tools.py -x -v` | TDD-created | ⬜ pending |
| 14-02-02 | 02 | 2 | Quality gate for tool docstrings + coverage | coverage | `uv run pytest src/mcp_canada/shared/__tests__/test_quality.py -x -v && uv run pytest --cov=src/mcp_canada --cov-fail-under=95` | ✅ | ⬜ pending |
| 14-03-01 | 03 | 3 | Prompts + Resources unit tests (TDD) | unit | `uv run pytest src/mcp_canada/modules/york_region/__tests__/test_prompts_resources.py -x -v` | TDD-created | ⬜ pending |
| 14-03-02 | 03 | 3 | Integration tests + README + REQUIREMENTS.md | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestYorkRegionToolScenarios tests/integration/test_prompts_resources_scenarios.py -v -m integration --timeout=120 && uv run pytest --cov=src/mcp_canada --cov-fail-under=95` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All test files are created via TDD **inside** the same task that implements the code (tdd="true" on every task). Wave 0 is satisfied inline — no separate stub plan needed.

- [x] `src/mcp_canada/shared/__tests__/test_arcgis_hub.py` — created in Plan 01 Task 1 (TDD)
- [x] `src/mcp_canada/modules/york_region/__tests__/__init__.py` — created in Plan 01 Task 2
- [x] `src/mcp_canada/modules/york_region/__tests__/conftest.py` — created in Plan 01 Task 2 (fixtures: Hub search response, FeatureServer GeoJSON, layer metadata)
- [x] `src/mcp_canada/modules/york_region/__tests__/test_client.py` — created in Plan 01 Task 2 (TDD)
- [x] `src/mcp_canada/modules/york_region/__tests__/test_tools.py` — created in Plan 02 Task 1 (TDD)
- [x] `src/mcp_canada/modules/york_region/__tests__/test_prompts_resources.py` — created in Plan 03 Task 1 (TDD)
- [x] `tests/integration/test_tool_scenarios.py` — append `TestYorkRegionToolScenarios` in Plan 03 Task 2
- [x] `tests/integration/test_prompts_resources_scenarios.py` — add york_region assertions in Plan 03 Task 2

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

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (TDD in-task creation)
- [x] No watch-mode flags
- [x] Feedback latency < 20s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-10
