---
phase: 21
slug: new-brunswick-government-open-data
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-30
---

# Phase 21 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Seeded from `21-RESEARCH.md` § Validation Architecture.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 (via `uv run pytest`) |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `uv run pytest src/mcp_canada/modules/new_brunswick/__tests__/ -x` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Estimated runtime** | ~15 seconds (module unit tests); ~90 seconds (full suite with coverage) |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest src/mcp_canada/modules/new_brunswick/__tests__/ -x`
- **After every plan wave:** Run `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Before `/gsd-verify-work`:** Full suite must be green (unit + project-wide structural guards)
- **Before shipping:** Live integration suite run at least once —
  `uv run pytest tests/integration/ -v -m integration --timeout=120` (the "Live-integration
  mandate" in CONTEXT.md)
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

> Seeded at plan time from the phase's capability surface. Task IDs are bound to concrete
> `{phase}-{plan}-{task}` ids by `/gsd-validate-phase` once plans are executed.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 0 | NB-shared | — | N/A | unit | `uv run pytest src/mcp_canada/shared/__tests__/test_arcgis_hub.py -k ArcgisServer -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 1 | NB-ckan-search | — | N/A | unit + integration | `uv run pytest src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py -k search -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 1 | NB-ckan-bilingual | — | N/A | unit | `uv run pytest src/mcp_canada/modules/new_brunswick/__tests__/test_client.py -k bilingual -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | NB-geonb-curated | T-21-03 | Unfiltered query over Parcels / Civic_Address / Wetlands rejected with `INVALID_INPUT` before any network call | integration (live, `assert_rows`) | `uv run pytest tests/integration/test_tool_scenarios.py -k new_brunswick -m integration --timeout=120` | ❌ W0 | ⬜ pending |
| TBD | TBD | 2 | NB-511-stub | T-21-02 | `NOT_CONFIGURED` message never echoes the value of `NEW_BRUNSWICK_511_KEY` | unit | `uv run pytest src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py -k not_configured -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | all | ERR-01/ERR-06/ERR-07 | — | N/A | unit (structural, project-wide) | `uv run pytest tests/test_tool_error_handling.py tests/test_error_classification_defaults.py -x` | ✅ | ⬜ pending |
| TBD | TBD | all | ERR-upstream-decode | — | N/A | unit (structural, project-wide) | `uv run pytest tests/test_upstream_error_classification.py -x` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `src/mcp_canada/modules/new_brunswick/__tests__/conftest.py` — sample CKAN `package_search`
      fixture (NB-filtered), sample GeoNB `?f=json` service-directory fixture, sample MapServer
      layer `?f=json` fixture, sample GeoJSON feature-query fixture
- [ ] `src/mcp_canada/modules/new_brunswick/__tests__/test_client.py` — stubs for the CKAN and
      GeoNB client functions
- [ ] `src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py` — stubs for every `nb_` tool
      (happy path, 404/suggestions, catch-all, `NOT_CONFIGURED`)
- [ ] `src/mcp_canada/modules/new_brunswick/__tests__/test_prompts_resources.py` — stubs for the
      module's prompts and resources
- [ ] `src/mcp_canada/shared/__tests__/test_arcgis_hub.py` — add
      `TestListArcgisServerServices` / `TestGetArcgisServerLayers` classes for the two new
      functions, following the existing `TestSearchHubDatasets` / `TestQueryFeatureService`
      structure, asserting **outgoing params** not just the URL
- [ ] `tests/integration/test_tool_scenarios.py` — add NB scenarios per `.claude/rules/tests.md`
      (happy path, discovery, error handling, cross-module) using `assert_live_or_transient` +
      `assert_rows`; never a one-armed guard
- [ ] Framework install: **none** — `pytest`, `httpx`, `pydantic` already present

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| NB 511 tools return live road events with a valid key | NB-511-stub | No public NB 511 key-registration URL was located; CI has no key, so the live path cannot be exercised automatically | Set `NEW_BRUNSWICK_511_KEY` from a manually obtained key, then call `nb_get_road_events` and confirm a populated `data` array with a `_meta.source.api` of the 511 feed |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
