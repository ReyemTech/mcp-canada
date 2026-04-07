---
phase: 8
slug: statcan-wds
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-07
---

# Phase 8 — Validation Strategy

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
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 08-01-01 | 01 | 1 | SC-01, SC-02, SC-03, INF-02, INF-03 | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py -x -v` | ❌ W0 | ⬜ pending |
| 08-02-01 | 02 | 1 | SC-04, SC-05, SC-06, SC-07, SC-08, SC-09, SC-13, SC-14 | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py -x -v` | ❌ W0 | ⬜ pending |
| 08-03-01 | 03 | 2 | INF-04, INF-05 | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_tools.py -x -v` | ❌ W0 | ⬜ pending |
| 08-03-02 | 03 | 2 | All | integration | `uv run pytest tests/integration/ -v -m integration -k statcan --timeout=120` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `src/mcp_canada/modules/statcan/__tests__/conftest.py` — WDS response fixtures
- [ ] `src/mcp_canada/modules/statcan/__tests__/test_client.py` — client function tests
- [ ] `src/mcp_canada/modules/statcan/__tests__/test_tools.py` — tool function tests
- [ ] `src/mcp_canada/modules/statcan/schemas.py` — Pydantic models (new file)
- [ ] `src/mcp_canada/modules/statcan/tools.py` — tool functions (new file)

*Existing pytest infrastructure covers framework needs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live WDS search returns results | SC-01 | Requires network | `uv run pytest tests/integration/ -v -m integration -k "statcan and search"` |
| WDS maintenance window 409 | INF-02 | Time-dependent | Only testable 00:00-08:30 EST |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
