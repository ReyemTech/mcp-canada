---
phase: 9
slug: sdmx-composite
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-07
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + pytest-asyncio |
| **Config file** | `pyproject.toml` (existing) |
| **Quick run command** | `uv run pytest src/mcp_canada/modules/statcan/__tests__/ -x -v` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest src/mcp_canada/modules/statcan/__tests__/ -x -v`
- **After every plan wave:** Run `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 09-01-01 | 01 | 1 | SC-10, SC-11, SC-12 | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py -x -v -k sdmx` | ❌ W0 | ⬜ pending |
| 09-02-01 | 02 | 2 | SC-10, SC-11, SC-12, SC-15 | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_tools.py -x -v -k sdmx` | ❌ W0 | ⬜ pending |
| 09-02-02 | 02 | 2 | All | integration | `uv run pytest tests/integration/ -v -m integration -k sdmx --timeout=120` | ❌ W0 | ⬜ pending |

---

## Wave 0 Requirements

- [ ] SDMX client function tests in `test_client.py`
- [ ] SDMX + composite tool tests in `test_tools.py`
- [ ] Integration test scenarios in `test_tool_scenarios.py`

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity maintained
- [x] No watch-mode flags
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
