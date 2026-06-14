---
phase: 18-manitoba-government-open-data
plan: "08"
subsystem: manitoba-tests-docs-coverage
tags: [tests, parametrized, integration, docs, coverage, readme, claude, examples, mcp-client]
dependency_graph:
  requires: [18-07]
  provides: [MB-18]
  affects: [mcp-discovery, test-suite, readme, docs, coverage]
tech_stack:
  added: []
  patterns:
    - "ALL_MANITOBA_TOOLS 20-entry parametrized list — mirrors Alberta Plan 09 pattern exactly"
    - "TestManitobaEnvelopes + TestManitobaLangParam — phase-wide envelope/lang coverage"
    - "TestManitobaToolScenarios — 7 integration scenarios via MCP Client call_tool layer"
    - "TestManitobaPromptsResources — 9 integration tests for 6 prompts + 7 resources via MCP Client"
    - "docs/modules/manitoba.md — full module documentation in Alberta pattern"
key_files:
  created:
    - docs/modules/manitoba.md
  modified:
    - src/mcp_canada/modules/manitoba/__tests__/test_tools.py
    - tests/integration/test_tool_scenarios.py
    - tests/integration/test_prompts_resources_scenarios.py
    - README.md
    - CLAUDE.md
    - EXAMPLES.md
decisions:
  - "ALL_MANITOBA_TOOLS count = 20 (5 discovery + 3 flood + 4 agriculture + 5 environment/health + 3 transport) — matches tools.py __all__ list"
  - "511 NOT_CONFIGURED integration test pops MANITOBA_511_KEY env var to guarantee deterministic result without needing a real key"
  - "Manitoba docs referenced from README modules table as docs/modules/manitoba.md (not inline tool catalog) — same pattern as Alberta, BC, Quebec"
  - "EXAMPLES.md example 25 uses manitoba_get_surgical_wait_times + StatCan WDS + Datastore JOIN — showcases cross-module SQL pattern for health data"
metrics:
  duration: "7 minutes"
  completed_date: "2026-06-14"
  tasks_completed: 2
  tasks_total: 2
  files_created: 1
  files_modified: 6
---

# Phase 18 Plan 08: Manitoba Tests, Docs, and Coverage Summary

**One-liner:** Phase-wide parametrized envelope/lang tests (40 tests across 20 tools), 16 integration scenarios via MCP Client (7 tool + 9 prompts/resources), docs sync (README/MODULES/CLAUDE/EXAMPLES), and 96.75% coverage gate pass — closing MB-18.

## What Was Built

### Task 1: Parametrized Tests + Integration Scenarios

**Parametrized unit tests in `test_tools.py`:**

`ALL_MANITOBA_TOOLS` — 20-entry list covering all Manitoba tools:
- 5 discovery tools (Plan 02)
- 3 flood/hydrology tools (Plan 03)
- 4 agriculture/drought tools (Plan 04)
- 5 environment/parks/health tools (Plan 05)
- 3 transport/511 tools (Plan 06)

`TestManitobaEnvelopes` — 20 parametrized tests: every tool with mocked client returns `_meta` with `{source.api, source.url, cached, lang, timestamp}`.

`TestManitobaLangParam` — 20 parametrized tests: every tool propagates `lang='fr'` to `_meta.lang` on success.

**Integration scenarios in `tests/integration/test_tool_scenarios.py`:**

`TestManitobaToolScenarios` (7 tests):

| Test | Scenario |
|------|---------|
| `test_flood_alerts_empty_is_success` | Empty features list = off-season normal, NOT an error |
| `test_provincial_parks` | 93 Manitoba parks via live FeatureServer |
| `test_surgical_wait_times_for_cardiac` | Live wait times FeatureServer filter by procedure |
| `test_drought_status` | Continental drought monitor filtered to Manitoba bbox |
| `test_discover_flood_alerts_via_bm25` | BM25 surfaces `manitoba_get_flood_alerts` on natural query |
| `test_invalid_f_type_returns_structured_error` | `f_type='swamp'` → INVALID_INPUT with `valid=` list |
| `test_511_not_configured_without_key` | MANITOBA_511_KEY absent → NOT_CONFIGURED (deterministic, no key needed) |

**Integration scenarios in `tests/integration/test_prompts_resources_scenarios.py`:**

`TestManitobaPromptsResources` (9 tests):

| Test | What It Verifies |
|------|-----------------|
| `test_six_prompts_discoverable` | All 6 `manitoba_` prompts in `list_prompts()` |
| `test_seven_resources_discoverable` | All 7 Manitoba URIs in `list_resources()` |
| `test_departments_resource_returns_valid_json` | `data://manitoba/departments` → valid JSON |
| `test_health_regions_resource_returns_valid_json` | `data://manitoba/health-regions` → ≥3 RHAs |
| `test_major_rivers_resource_returns_valid_json` | `data://manitoba/major-rivers` → includes Floodway |
| `test_flood_data_guide_is_markdown` | `docs://manitoba/flood-data-guide` → markdown with alerts |
| `test_portal_guide_mentions_mli_retirement` | `docs://manitoba/portal-guide` → MLI warning present |
| `test_dataset_report_template_has_placeholders` | `template://manitoba/dataset-report` → {placeholder} |
| `test_flood_report_template_has_placeholders` | `template://manitoba/flood-report` → {placeholder} |

### Task 2: Docs Sync + Coverage Gate

**README.md:**
- Header: 217 → **237 tools**, 5 → **6 provincial APIs**, added Manitoba description to summary line
- Modules table: added Manitoba row (20 tools, 6 prompts, 7 resources)
- Architecture tree: added `├── manitoba/ # 20 tools — geoportal.gov.mb.ca ArcGIS Hub + 511 Manitoba`
- Total row: 217 → **237**

**docs/modules/manitoba.md** (new file):
- Full module documentation covering all 20 tools (with parameters), 6 prompts, 7 resources
- Portal notes: Hub Search API path, data.manitoba.ca unreachability, MLI retirement
- OpenMB licence attribution
- 511 key requirement note

**CLAUDE.md:**
- ArcGIS Hub row: added "Phase 18: Manitoba (geoportal.gov.mb.ca, org mMUesHYPkXjaFGfS)"
- Added Manitoba paragraph documenting: Hub API path, MLI retirement, 511 key gate, River Conditions CSV, `docs://manitoba/portal-guide` reference

**EXAMPLES.md:**
- Example 25: Manitoba Surgical Wait Times + StatCan Population JOIN in Datastore
  - `manitoba_get_surgical_wait_times` (Cardiac + Hip procedures)
  - `sc_get_data_from_cube_pid_coord` (StatCan table 17-10-0005-01)
  - `ds_create_table` + `ds_insert_data` + `ds_query` (year-over-year trend)

**Coverage gate:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95 -q`
- **96.75%** total coverage (gate: 95%)
- **2506 tests pass**, 2 skipped, 285 deselected

## MB-01…MB-18 Matrix Status

| Req ID | Description | Status |
|--------|-------------|--------|
| MB-01 | Hub search/discovery | DONE (Plan 02) |
| MB-02 | Dataset details | DONE (Plan 02) |
| MB-03 | Dataset query (FeatureServer + file router) | DONE (Plan 02) |
| MB-04 | Organizations list | DONE (Plan 02) |
| MB-05 | Categories list | DONE (Plan 02) |
| MB-06 | Flood alerts (empty = normal) | DONE (Plan 03) |
| MB-07 | River stations CSV | DONE (Plan 03) |
| MB-08 | Provincial waterways | DONE (Plan 03) |
| MB-09 | Drought status (bbox-filtered) | DONE (Plan 04) |
| MB-10 | Ag weather stations | DONE (Plan 04) |
| MB-11 | Livestock prices (cattle + hog graceful) | DONE (Plan 04) |
| MB-12 | Crop regions | DONE (Plan 04) |
| MB-13 | Provincial parks (bilingual) | DONE (Plan 05) |
| MB-14 | Fisheries data | DONE (Plan 05) |
| MB-15 | Provincial forests | DONE (Plan 05) |
| MB-16 | Surgical wait times | DONE (Plan 05) |
| MB-17 | Health facilities | DONE (Plan 05) |
| MB-18 | 511 transport (key-gated NOT_CONFIGURED) | DONE (Plan 06) |
| MB-18 prompts | 6 bilingual prompts | DONE (Plan 07) |
| MB-18 resources | 7 zero-parameter resources | DONE (Plan 07) |
| MB-18 tests | Parametrized envelope/lang + integration | DONE (Plan 08) |
| MB-18 docs | README/MODULES/CLAUDE/EXAMPLES | DONE (Plan 08) |

## Deferred Items

**511 live integration:** `MANITOBA_511_KEY` is gated (account + explicit key request). The NOT_CONFIGURED path is tested deterministically. Live 511 scenario can be added once a key is available — add to `test_511_not_configured_without_key` test (the `if key is not None` branch already handles the live case).

**Pre-existing lint issues (out of scope):**
- `test_client.py:17` — unused `Five11NotConfigured` import in test file (pre-existing from Plan 01 scaffold)
- `prompts.py` pyright false positive on `fastmcp.prompts.prompt` (import works at runtime, confirmed by 36 Plan 07 tests)

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1: parametrized + integration tests | ab5cdba | 40 parametrized tests + 16 integration scenarios |
| Task 2: docs sync + coverage gate | 25f77a9 | README/MODULES/CLAUDE/EXAMPLES + 96.75% coverage |

## Self-Check: PASSED

| Item | Status |
|------|--------|
| `src/mcp_canada/modules/manitoba/__tests__/test_tools.py` (TestManitobaEnvelopes + TestManitobaLangParam) | FOUND |
| `tests/integration/test_tool_scenarios.py` (TestManitobaToolScenarios) | FOUND |
| `tests/integration/test_prompts_resources_scenarios.py` (TestManitobaPromptsResources) | FOUND |
| `docs/modules/manitoba.md` | FOUND |
| `README.md` (Manitoba row, 237 total) | FOUND |
| `CLAUDE.md` (Manitoba in ArcGIS Hub row) | FOUND |
| `EXAMPLES.md` (example 25) | FOUND |
| Commit ab5cdba (Task 1) | FOUND |
| Commit 25f77a9 (Task 2) | FOUND |
| 40 parametrized tests pass | VERIFIED |
| 232 Manitoba unit tests pass | VERIFIED |
| 16 Manitoba integration tests collectable | VERIFIED |
| Coverage 96.75% >= 95% | VERIFIED |
| 2506 total tests pass | VERIFIED |
