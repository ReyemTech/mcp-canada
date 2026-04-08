---
phase: 11
slug: ircc-immigration
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-08
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + pytest-asyncio (asyncio_mode = "auto") |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `uv run pytest src/mcp_canada/shared/__tests__/ src/mcp_canada/modules/ircc/__tests__/ -x -v` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest src/mcp_canada/shared/__tests__/ src/mcp_canada/modules/ircc/__tests__/ -x -v`
- **After every plan wave:** Run `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 1 | IRCC-01 | unit | `uv run pytest src/mcp_canada/shared/__tests__/test_parsers.py -x` | ❌ W0 | ⬜ pending |
| 11-01-02 | 01 | 1 | IRCC-02 | unit | `uv run pytest src/mcp_canada/shared/__tests__/test_parsers.py -x` | ❌ W0 | ⬜ pending |
| 11-01-03 | 01 | 1 | IRCC-03 | unit | `uv run pytest src/mcp_canada/shared/__tests__/test_parsers.py -x` | ❌ W0 | ⬜ pending |
| 11-02-01 | 02 | 1 | IRCC-04 | unit | `uv run pytest src/mcp_canada/modules/ircc/__tests__/test_tools.py -x` | ❌ W0 | ⬜ pending |
| 11-02-02 | 02 | 1 | IRCC-05 | unit | `uv run pytest src/mcp_canada/modules/ircc/__tests__/test_tools.py -x` | ❌ W0 | ⬜ pending |
| 11-02-03 | 02 | 1 | IRCC-06 | unit | `uv run pytest src/mcp_canada/modules/ircc/__tests__/test_tools.py -x` | ❌ W0 | ⬜ pending |
| 11-03-01 | 03 | 2 | IRCC-07 | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestIrccScenarios -v -m integration` | ❌ W0 | ⬜ pending |
| 11-03-02 | 03 | 2 | IRCC-08 | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestIrccScenarios::test_discover_ircc_tools -v -m integration` | ❌ W0 | ⬜ pending |
| 11-03-03 | 03 | 2 | IRCC-09 | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestIrccScenarios::test_store_pr_data_to_datastore -v -m integration` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `src/mcp_canada/shared/__tests__/test_parsers.py` — unit tests for `fetch_and_parse()`, `_parse_xlsx()`, `_parse_csv()`, `_mask_privacy()`
- [ ] `src/mcp_canada/modules/ircc/__tests__/__init__.py` — empty init
- [ ] `src/mcp_canada/modules/ircc/__tests__/conftest.py` — sample XLSX bytes fixtures (minimal synthetic workbook via openpyxl)
- [ ] `src/mcp_canada/modules/ircc/__tests__/test_client.py` — client function tests with mocked `fetch_and_parse`
- [ ] `src/mcp_canada/modules/ircc/__tests__/test_tools.py` — tool tests with mocked client functions
- [ ] `tests/integration/test_tool_scenarios.py::TestIrccScenarios` — integration tests class (append to existing file)
- [ ] Framework install: `uv add openpyxl` — add to base dependencies in `pyproject.toml`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Multi-sheet workbook navigation | IRCC-04 | Operational Processing files have unknown sheet structure | Download sample file, verify correct sheet selected |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
