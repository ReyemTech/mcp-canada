---
phase: 16
slug: quebec-government-open-data
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-11
---

# Phase 16 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (pytest-asyncio, pytest-cov) |
| **Config file** | `pyproject.toml` (existing — no install needed) |
| **Quick run command** | `uv run pytest src/mcp_canada/modules/quebec/__tests__/ -x -q` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Estimated runtime** | ~45 seconds (unit) / ~90 seconds (full w/ coverage) |

---

## Sampling Rate

- **After every task commit:** Run quick run command (module-scoped unit tests)
- **After every plan wave:** Run full suite command
- **Before `/gsd:verify-work`:** Full suite green AND integration tests pass (`-m integration --timeout=120 -k Quebec`)
- **Max feedback latency:** 90 seconds

---

## Per-Task Verification Map

*Populated by gsd-planner when plans are written. Every task must map to a test command — either an existing test file or a Wave 0 stub.*

| Task ID | Plan | Wave | Requirement/Concern | Test Type | Automated Command | File Exists | Status |
|---------|------|------|---------------------|-----------|-------------------|-------------|--------|
| 16-01-01 | 01 | 1 | quebec module skeleton | unit | `uv run python -c "from mcp_canada.modules import quebec; print(quebec.MODULE_NAME)"` | ✅ | ✅ green |
| 16-01-02 | 01 | 1 | Wave 0 test stubs collect | unit | `uv run pytest src/mcp_canada/modules/quebec/__tests__/ --collect-only -q` | ✅ | ✅ green |
| 16-02-01 | 02 | 2 | CKAN client functions | unit | `uv run pytest src/mcp_canada/modules/quebec/__tests__/test_client.py -x` | ❌ W0 | ⬜ pending |
| 16-02-02 | 02 | 2 | 5 discovery tools | unit | `uv run pytest src/mcp_canada/modules/quebec/__tests__/test_tools.py -x -k "TestQuebecSearch or TestQuebecGet or TestQuebecQuery or TestQuebecList"` | ❌ W0 | ⬜ pending |
| 16-02-03 | 02 | 2 | TestSharedApiGetContract (Phase 15 lesson) | unit | `uv run pytest src/mcp_canada/modules/quebec/__tests__/test_client.py::TestSharedApiGetContract -x` | ❌ W0 | ⬜ pending |
| 16-03-01 | 03 | 3 | Health/MSSS curated tools | unit | `uv run pytest src/mcp_canada/modules/quebec/__tests__/test_tools.py::TestQuebecGetHospitals -x` | ❌ W0 | ⬜ pending |
| 16-03-02 | 03 | 3 | MTQ transport curated tools | unit | `uv run pytest src/mcp_canada/modules/quebec/__tests__/test_tools.py::TestQuebecGetRoadEvents -x` | ❌ W0 | ⬜ pending |
| 16-04-01 | 04 | 4 | Environment + demographics tools | unit | `uv run pytest src/mcp_canada/modules/quebec/__tests__/test_tools.py -x -k "Air or Water or Population or Parks or Electricity or Forest"` | ❌ W0 | ⬜ pending |
| 16-04-02 | 04 | 4 | 6 bilingual prompts + 7 resources | unit | `uv run pytest src/mcp_canada/modules/quebec/__tests__/test_prompts_resources.py -x` | ❌ W0 | ⬜ pending |
| 16-04-03 | 04 | 4 | Integration tests via MCP Client | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestQuebecToolScenarios -m integration --timeout=120` | ❌ W0 | ⬜ pending |
| 16-04-04 | 04 | 4 | Prompts/resources integration | integration | `uv run pytest tests/integration/test_prompts_resources_scenarios.py::TestQuebecPromptsResources -m integration --timeout=120` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Test stubs that must exist before implementation tasks can run:

- [ ] `src/mcp_canada/modules/quebec/__tests__/__init__.py`
- [ ] `src/mcp_canada/modules/quebec/__tests__/conftest.py` — sample CKAN responses (package_search, package_show, org_list, group_list, datastore_search)
- [ ] `src/mcp_canada/modules/quebec/__tests__/test_client.py` — client function test class scaffolds + `TestSharedApiGetContract` stub
- [ ] `src/mcp_canada/modules/quebec/__tests__/test_tools.py` — 18 tool test class scaffolds (5 CKAN + 13 curated)
- [ ] `src/mcp_canada/modules/quebec/__tests__/test_prompts_resources.py` — prompt/resource class scaffolds
- [ ] `tests/integration/test_tool_scenarios.py::TestQuebecToolScenarios` — xfail placeholder methods
- [ ] `tests/integration/test_prompts_resources_scenarios.py::TestQuebecPromptsResources` — xfail placeholder methods

Framework already installed; Wave 0 = test file scaffolding only.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| README.md Quebec section added | modules.md rule | File-level doc assertion | `grep -c "quebec_" README.md` must match tool count (~18) |
| CLAUDE.md notes no new portal technology | CLAUDE.md rule | Documentation drift check | Visual review — CKAN already documented, no new row needed |
| Live Données Québec availability | curated tools | External dependency; can flake | Integration tests cover it with `-m integration`; manual re-run on red |
| Bilingual error messages (inline ternary pattern) | Phase 15 lesson | Verify French literal present in error guards | `grep -c '"fr"' src/mcp_canada/modules/quebec/tools.py` must be > 0 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] `TestSharedApiGetContract` test class added (Phase 15 lesson — patches `mcp_canada.shared.http.api_get` at shared layer)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
