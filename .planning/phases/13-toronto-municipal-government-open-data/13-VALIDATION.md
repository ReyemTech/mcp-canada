---
phase: 13
slug: toronto-municipal-government-open-data
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-09
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (existing) |
| **Config file** | `pyproject.toml` (existing) |
| **Quick run command** | `uv run pytest src/mcp_canada/modules/toronto/ -x -v` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest src/mcp_canada/modules/toronto/ src/mcp_canada/shared/__tests__/test_parsers.py -x`
- **After every plan wave:** Run `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 13-01-01 | 01 | 1 | TOR-08 | unit | `uv run pytest src/mcp_canada/shared/__tests__/test_parsers.py::TestGeoJSON -x` | ❌ W0 | ⬜ pending |
| 13-01-02 | 01 | 1 | TOR-09 | unit | `uv run pytest src/mcp_canada/shared/__tests__/test_parsers.py::TestParseJSON -x` | ❌ W0 | ⬜ pending |
| 13-01-03 | 01 | 1 | TOR-01 | unit | `uv run pytest src/mcp_canada/modules/toronto/__tests__/test_tools.py::TestTorontoDiscovery -x` | ❌ W0 | ⬜ pending |
| 13-01-04 | 01 | 1 | TOR-02 | unit | `uv run pytest src/mcp_canada/modules/toronto/__tests__/test_tools.py::TestTorontoDatasetDetails -x` | ❌ W0 | ⬜ pending |
| 13-02-01 | 02 | 2 | TOR-03 | unit | `uv run pytest src/mcp_canada/modules/toronto/__tests__/test_client.py::TestGTFSClient -x` | ❌ W0 | ⬜ pending |
| 13-02-02 | 02 | 2 | TOR-04 | unit | `uv run pytest src/mcp_canada/modules/toronto/__tests__/test_tools.py::TestNeighbourhood -x` | ❌ W0 | ⬜ pending |
| 13-02-03 | 02 | 2 | TOR-05 | unit | `uv run pytest src/mcp_canada/modules/toronto/__tests__/test_tools.py::TestNeighbourhood -x` | ❌ W0 | ⬜ pending |
| 13-02-04 | 02 | 2 | TOR-06 | unit | `uv run pytest src/mcp_canada/modules/toronto/__tests__/test_client.py::Test311Client -x` | ❌ W0 | ⬜ pending |
| 13-02-05 | 02 | 2 | TOR-07 | unit | `uv run pytest src/mcp_canada/modules/toronto/__tests__/test_tools.py::TestRentSafe -x` | ❌ W0 | ⬜ pending |
| 13-02-03 | 02 | 2 | TOR-10 | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestTorontoToolScenarios -v -m integration` | ❌ W0 | ⬜ pending |
| 13-02-04 | 02 | 2 | TOR-11 | quality | `uv run pytest src/mcp_canada/shared/__tests__/test_quality.py -x` | ✅ | ⬜ pending |
| 13-02-05 | 02 | 2 | TOR-12 | coverage | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `src/mcp_canada/modules/toronto/__tests__/__init__.py` — package init
- [ ] `src/mcp_canada/modules/toronto/__tests__/conftest.py` — CKAN fixtures, GTFS bytes, datastore records
- [ ] `src/mcp_canada/modules/toronto/__tests__/test_client.py` — client unit tests
- [ ] `src/mcp_canada/modules/toronto/__tests__/test_tools.py` — tool unit tests
- [ ] `tests/integration/test_tool_scenarios.py` — append `TestTorontoToolScenarios` class

*Existing infrastructure covers framework and quality gates.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GTFS ZIP download works with live TTC data | TOR-03 | Depends on live 35.9MB download | Run integration test with `--timeout=120` |
| 311 ZIP year discovery works for current year | TOR-06 | Year availability changes annually | Run integration test checking current year |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
