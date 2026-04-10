---
phase: 15
slug: british-columbia-government-open-data
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-10
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (with pytest-asyncio, pytest-cov) |
| **Config file** | `pyproject.toml` (existing — no install needed) |
| **Quick run command** | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/ -x -q` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Estimated runtime** | ~45 seconds (unit) / ~90 seconds (full w/ coverage) |

---

## Sampling Rate

- **After every task commit:** Run quick run command (module-scoped unit tests)
- **After every plan wave:** Run full suite command
- **Before `/gsd:verify-work`:** Full suite must be green AND integration tests pass (`-m integration --timeout=120`)
- **Max feedback latency:** 90 seconds

---

## Per-Task Verification Map

*To be populated by gsd-planner when plans are written. Every task must map to a test command — either an existing test file or a Wave 0 stub.*

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 15-01-01 | 01 | 1 | shared/ogc.py | unit | `uv run pytest src/mcp_canada/shared/__tests__/test_ogc.py -x` | ❌ W0 | ⬜ pending |
| 15-02-01 | 02 | 2 | bc_search_datasets | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_client.py -x` | ❌ W0 | ⬜ pending |
| 15-03-01 | 03 | 3 | curated WFS tools | unit | `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py -x` | ❌ W0 | ⬜ pending |
| 15-04-01 | 04 | 4 | prompts/resources/integration | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestBcToolScenarios -m integration --timeout=120` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Test stubs that must exist before implementation tasks can run:

- [ ] `src/mcp_canada/shared/__tests__/test_ogc.py` — WFS client unit tests (GetCapabilities, GetFeature, CQL, pagination, XML error parsing)
- [ ] `src/mcp_canada/modules/british_columbia/__tests__/__init__.py`
- [ ] `src/mcp_canada/modules/british_columbia/__tests__/conftest.py` — sample CKAN + WFS responses
- [ ] `src/mcp_canada/modules/british_columbia/__tests__/test_client.py` — client function tests
- [ ] `src/mcp_canada/modules/british_columbia/__tests__/test_tools.py` — tool envelope/error tests (5 CKAN + ~15 curated)
- [ ] `src/mcp_canada/modules/british_columbia/__tests__/test_prompts_resources.py` — prompts + resources
- [ ] `tests/integration/test_tool_scenarios.py::TestBcToolScenarios` — MCP Client happy-path/discovery/error scenarios
- [ ] `tests/integration/test_prompts_resources_scenarios.py` — append BC prompt/resource assertions

Framework is already installed; Wave 0 = test file scaffolding only.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| README.md tool catalog updated | modules.md rule | File-level assertion, not functional | `grep -c "bc_" README.md` must match tool count |
| CLAUDE.md notes WFS as third portal tech | CLAUDE.md rule | Documentation drift | Visual review during PR |
| Live WFS endpoint availability | curated tools | External dependency; can flake | Integration tests cover it with `-m integration`; manual re-run on red |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
