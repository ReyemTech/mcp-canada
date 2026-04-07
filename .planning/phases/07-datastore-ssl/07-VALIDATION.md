---
phase: 7
slug: datastore-ssl
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-07
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + pytest-asyncio |
| **Config file** | `pyproject.toml` (existing) |
| **Quick run command** | `uv run pytest src/mcp_canada/modules/datastore/__tests__/ -v` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest src/mcp_canada/modules/datastore/__tests__/ -v`
- **After every plan wave:** Run `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | DS-07, DS-08 | unit | `uv run pytest src/mcp_canada/modules/datastore/__tests__/test_client.py -v` | ❌ W0 | ⬜ pending |
| 07-02-01 | 02 | 2 | DS-01–DS-06 | unit | `uv run pytest src/mcp_canada/modules/datastore/__tests__/test_tools.py -v` | ❌ W0 | ⬜ pending |
| 07-03-01 | 03 | 1 | INF-01 | smoke | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_stub.py -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `src/mcp_canada/modules/datastore/__tests__/conftest.py` — shared fixtures (in-memory DB)
- [ ] `src/mcp_canada/modules/datastore/__tests__/test_client.py` — client function tests for DS-07, DS-08
- [ ] `src/mcp_canada/modules/datastore/__tests__/test_tools.py` — tool function tests for DS-01 through DS-06
- [ ] `src/mcp_canada/modules/statcan/__tests__/test_stub.py` — smoke test for INF-01

*Existing pytest infrastructure covers framework needs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| StatCan SSL probe against live endpoint | INF-01 | Requires network access to statcan.gc.ca | Run `uv run python -c "import httpx; r = httpx.get('https://www150.statcan.gc.ca/t1/wds/rest/getAllCubesListLite'); print(r.status_code)"` |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
