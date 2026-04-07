---
phase: 7
slug: datastore-ssl
status: draft
nyquist_compliant: false
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
| **Quick run command** | `uv run pytest tests/test_datastore.py -v` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/test_datastore.py -v`
- **After every plan wave:** Run `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | DS-07 | unit | `uv run pytest tests/test_datastore.py::TestValidateIdentifier -v` | ❌ W0 | ⬜ pending |
| 07-01-02 | 01 | 1 | DS-01 | unit | `uv run pytest tests/test_datastore.py::TestCreateTable -v` | ❌ W0 | ⬜ pending |
| 07-01-03 | 01 | 1 | DS-02 | unit | `uv run pytest tests/test_datastore.py::TestInsertData -v` | ❌ W0 | ⬜ pending |
| 07-01-04 | 01 | 1 | DS-03 | unit | `uv run pytest tests/test_datastore.py::TestQuery -v` | ❌ W0 | ⬜ pending |
| 07-01-05 | 01 | 1 | DS-04 | unit | `uv run pytest tests/test_datastore.py::TestListTables -v` | ❌ W0 | ⬜ pending |
| 07-01-06 | 01 | 1 | DS-05 | unit | `uv run pytest tests/test_datastore.py::TestGetSchema -v` | ❌ W0 | ⬜ pending |
| 07-01-07 | 01 | 1 | DS-06 | unit | `uv run pytest tests/test_datastore.py::TestDropTable -v` | ❌ W0 | ⬜ pending |
| 07-01-08 | 01 | 1 | DS-08 | unit | `uv run pytest tests/test_datastore.py -v` | ❌ W0 | ⬜ pending |
| 07-02-01 | 02 | 1 | INF-01 | unit | `uv run pytest tests/test_statcan_ssl.py -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_datastore.py` — test stubs for DS-01 through DS-08
- [ ] `tests/test_statcan_ssl.py` — test stubs for INF-01

*Existing pytest infrastructure covers framework needs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| StatCan SSL probe against live endpoint | INF-01 | Requires network access to statcan.gc.ca | Run `uv run python -c "import httpx; r = httpx.get('https://www150.statcan.gc.ca/t1/wds/rest/getAllCubesListLite'); print(r.status_code)"` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
