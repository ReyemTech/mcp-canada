---
phase: 40
slug: mcp-prompts-and-resources
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-09
---

# Phase 40 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 with pytest-asyncio |
| **Config file** | `pyproject.toml` (existing) |
| **Quick run command** | `uv run pytest src/mcp_canada/modules/{module}/__tests__/test_prompts_resources.py -x -v` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest src/mcp_canada/modules/{module}/__tests__/test_prompts_resources.py -x`
- **After every plan wave:** Run `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 40-01-01 | 01 | 1 | Infrastructure | unit | `uv run pytest src/mcp_canada/modules/_example/__tests__/ -x -v` | ❌ W0 | ⬜ pending |
| 40-01-02 | 01 | 1 | BoC prompts+resources | unit | `uv run pytest src/mcp_canada/modules/bank_of_canada/__tests__/test_prompts_resources.py -x -v` | ❌ W0 | ⬜ pending |
| 40-02-01 | 02 | 2 | Remaining module prompts+resources | unit | `uv run pytest src/mcp_canada/modules/ -x -v -k test_prompts_resources` | ❌ W0 | ⬜ pending |
| 40-02-02 | 02 | 2 | Integration + README | integration | `uv run pytest tests/integration/ -v -m integration -k prompt` | ❌ W0 | ⬜ pending |
| 40-02-03 | 02 | 2 | Coverage gate | coverage | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `src/mcp_canada/modules/{each module}/__tests__/test_prompts_resources.py` — one per module
- [ ] `tests/integration/test_prompts_resources_scenarios.py` — integration tests

*Existing infrastructure covers framework, coverage config, and quality gates.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Prompts appear as slash-commands in Claude Desktop | UX | Requires Claude Desktop client | Open Claude Desktop, connect to mcp-canada, verify prompt list |
| Resources browsable in Claude Desktop | UX | Requires Claude Desktop client | Open Claude Desktop, browse resources panel |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
