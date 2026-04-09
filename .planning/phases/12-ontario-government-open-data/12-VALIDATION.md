---
phase: 12
slug: ontario-government-open-data
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-09
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + pytest-asyncio (asyncio_mode = "auto") |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `uv run pytest src/mcp_canada/modules/ontario/__tests__/ -x -v` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest src/mcp_canada/modules/ontario/__tests__/ -x -v`
- **After every plan wave:** Run `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 1 | ONT-01 | unit | `uv run pytest src/mcp_canada/modules/ontario/__tests__/test_client.py -x` | ❌ W0 | ⬜ pending |
| 12-01-02 | 01 | 1 | ONT-02 | unit | `uv run pytest src/mcp_canada/modules/ontario/__tests__/test_client.py -x` | ❌ W0 | ⬜ pending |
| 12-02-01 | 02 | 1 | ONT-03 | unit | `uv run pytest src/mcp_canada/modules/ontario/__tests__/test_tools.py -x` | ❌ W0 | ⬜ pending |
| 12-02-02 | 02 | 1 | ONT-04 | unit | `uv run pytest src/mcp_canada/modules/ontario/__tests__/test_tools.py -x` | ❌ W0 | ⬜ pending |
| 12-02-03 | 02 | 1 | ONT-05 | unit | `uv run pytest src/mcp_canada/modules/ontario/__tests__/test_tools.py -x` | ❌ W0 | ⬜ pending |
| 12-03-01 | 03 | 2 | ONT-07 | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestOntarioScenarios -v -m integration` | ❌ W0 | ⬜ pending |
| 12-03-02 | 03 | 2 | ONT-08 | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestOntarioScenarios -v -m integration` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `src/mcp_canada/modules/ontario/__tests__/__init__.py` — empty init
- [ ] `src/mcp_canada/modules/ontario/__tests__/conftest.py` — sample CKAN API response fixtures
- [ ] `src/mcp_canada/modules/ontario/__tests__/test_client.py` — client function tests with mocked HTTP
- [ ] `src/mcp_canada/modules/ontario/__tests__/test_tools.py` — tool tests with mocked client functions
- [ ] `tests/integration/test_tool_scenarios.py::TestOntarioScenarios` — integration tests (append to existing file)

---

## Manual-Only Verifications

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
