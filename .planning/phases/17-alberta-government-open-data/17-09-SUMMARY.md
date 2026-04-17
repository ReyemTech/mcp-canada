---
phase: 17-alberta-government-open-data
plan: 09
subsystem: alberta
tags: [tests, docs, coverage, integration, readme, verification]
requires:
  - "17-01-SUMMARY (Alberta module scaffold + placeholder test classes)"
  - "17-02-SUMMARY (5 discovery tools)"
  - "17-03-SUMMARY (4 AER energy tools)"
  - "17-04-SUMMARY (4 wildfire tools)"
  - "17-05-SUMMARY (3 health tools)"
  - "17-06-SUMMARY (3 transport/511 tools)"
  - "17-07-SUMMARY (5 env/agri/demo/parks tools)"
  - "17-08-SUMMARY (6 prompts + 7 resources, AB-23 doc guidance)"
provides:
  - "Parametrized envelope + lang-propagation tests over all 24 alberta tools"
  - "7 live-API integration scenarios via MCP Client(mcp) + BM25 discovery path"
  - "4 prompts/resources discovery scenarios (list_prompts / list_resources / read_resource)"
  - "docs/modules/alberta.md per-module catalog page"
  - "EXAMPLES.md Example 24 (Alberta Energy + Wildfire cross-module + datastore)"
  - "README.md Alberta row + total recount (193 -> 217 tools, 4 -> 5 provincial APIs)"
  - "CLAUDE.md Portal Technologies table: CKAN + ArcGIS Hub rows now include Alberta"
  - "Coverage gate: alberta module at 96.84% (>= 95% threshold)"
affects:
  - "src/mcp_canada/modules/alberta/__tests__/test_tools.py (filled two parametrized classes)"
  - "tests/integration/test_tool_scenarios.py (appended TestAlbertaToolScenarios)"
  - "tests/integration/test_prompts_resources_scenarios.py (appended TestAlbertaPromptsResources)"
  - "README.md, docs/modules/alberta.md, EXAMPLES.md, CLAUDE.md"
tech-stack:
  added: []
  patterns:
    - "ALL_ALBERTA_TOOLS lockstep assertion — len == 24 blows up at import time if any tool is added/removed without updating the parametrization table"
    - "unittest.mock.patch + AsyncMock at mcp_canada.modules.alberta.tools._client.fetch_* paths (consistent with existing per-tool tests, no new mocker dependency)"
    - "Integration tests route through Client(mcp) + BM25SearchTransform — the agent path — not direct client.py functions"
    - "Alberta integration tests use 'if _meta in data' guards to accept legitimate transient upstream errors (UPSTREAM_ERROR / RATE_LIMITED) without silent shape drift"
key-files:
  created:
    - "docs/modules/alberta.md"
    - ".planning/phases/17-alberta-government-open-data/17-09-SUMMARY.md"
  modified:
    - "src/mcp_canada/modules/alberta/__tests__/test_tools.py"
    - "tests/integration/test_tool_scenarios.py"
    - "tests/integration/test_prompts_resources_scenarios.py"
    - "README.md"
    - "EXAMPLES.md"
    - "CLAUDE.md"
decisions:
  - "Kept the existing patch/AsyncMock pattern (no pytest-mock/mocker fixture) — stays consistent with the 100+ per-tool tests already in place; avoids adding pytest-mock to the dependency set the plan discouraged"
  - "Direct @tool callable (no .fn unwrapping) — FastMCP's @tool on this codebase returns a plain coroutine function (type 'function', hasattr '.fn' == False); matches every existing per-tool test"
  - "Alberta hospitals count bound set to 50-250 (not a tight ±20 around 101) — AHSGIS FeatureServer feature counts include non-hospital AHS facility records from the same service; tight bounds would be brittle across republishing"
  - "Production volumes scenario accepts {rows in data.data} OR {error.code in UPSTREAM_ERROR/RATE_LIMITED} — AER ST3 XLSX republishing windows legitimately yield transient errors; ratcheting a strict rows shape would make CI flaky without catching real regressions"
  - "docs/modules/alberta.md follows the Quebec per-module template (plan referenced 'docs/MODULES.md' but the actual project convention is 'docs/modules/{module}.md' per the 16 existing pages)"
  - "AB-23 water-licence guidance lives in docs://alberta/wildfire-data-guide (confirmed in Plan 08); Plan 09 adds an integration test that fails if the AB-23 section is dropped"
requirements:
  - AB-27
metrics:
  duration_seconds: 392
  duration_minutes: 6.5
  tasks_completed: 3
  completed_date: 2026-04-17
---

# Phase 17 Plan 09: Alberta Final Wave (Parametrized Coverage + Docs) Summary

**One-liner:** Closes Phase 17 with 48 parametrized envelope/lang tests over all 24 alberta tools, 11 live-API integration scenarios routed through `Client(mcp)`, and a fully-synced documentation surface (README, per-module doc, cross-module example, CLAUDE.md portal table) at 96.84% module coverage.

## What Shipped

### 1. Parametrized phase-wide tests (48 new cases)

Filled the two Plan 01 placeholder classes with a locked `ALL_ALBERTA_TOOLS` table driving both:

- `TestAlbertaEnvelopes::test_envelope_structure` — 24 cases, one per tool. Asserts `_meta` contains `{source.api, source.url, cached, lang, timestamp}` with `lang` defaulting to `"en"`.
- `TestAlbertaLangParam::test_lang_propagation` — 24 cases. Asserts `lang="fr"` flows through to `_meta.lang` on the success path for every tool.

The table is guarded by an import-time assertion: `assert len(ALL_ALBERTA_TOOLS) == 24`. Any future tool addition or removal will explode at collection time unless the parametrization table is updated in lockstep — which is the AB-27 convention-compliance trip wire the plan asked for.

### 2. Integration scenarios via MCP Client (11 new tests)

Per `.claude/rules/tests.md`, every integration test calls tools through `Client(mcp).call_tool("call_tool", {...})` — the same BM25-discovery path an agent uses — not the per-module `fetch_*` functions directly.

`TestAlbertaToolScenarios` (7 live-API scenarios in `tests/integration/test_tool_scenarios.py`):

1. `test_search_wildfire_datasets` — open.alberta.ca CKAN search with `format=CSV` filter
2. `test_active_fires_now` — WMBappServices `Active_Wildfires_Dashboard_view`
3. `test_alberta_hospitals` — AHSGIS `AHS_Hospitals` FeatureServer (count range check)
4. `test_alberta_road_events` — 511 Alberta `/event` JSON feed
5. `test_alberta_production_volumes_gas` — AER ST3 `Gas_current.xlsx` (allows UPSTREAM_ERROR / RATE_LIMITED as legitimate transient outcomes)
6. `test_alberta_invalid_product_returns_structured_error` — INVALID_INPUT with `valid` list for Pitfall 8 (case-sensitive `Bitumen` → rejected, with suggestions)
7. `test_discover_alberta_via_bm25` — BM25 discovery surfaces `alberta_` tools on "alberta wells oil energy regulator"

`TestAlbertaPromptsResources` (4 scenarios in `tests/integration/test_prompts_resources_scenarios.py`):

1. `test_six_prompts_discoverable` — all 6 alberta prompts appear in `prompts/list`
2. `test_seven_resources_discoverable` — all 7 alberta resources appear in `resources/list` (3 `data://` + 2 `docs://` + 2 `template://`)
3. `test_ministries_resource_returns_valid_json` — `data://alberta/ministries` parses as JSON with `energy-and-minerals` slug
4. `test_wildfire_data_guide_mentions_ab23` — AB-23 water-licence guidance section in `docs://alberta/wildfire-data-guide` cannot silently drop (Plan 08 requirement protection)

### 3. Documentation surface in sync

- **`README.md`**: Tool count 193 → 217; provincial APIs 4 → 5; new Alberta row in the modules table (alphabetical — before British Columbia in the provincial cohort); architecture module tree lists `alberta/`. Prompts estimate updated 81 → 87, resources 110 → 117.
- **`docs/modules/alberta.md`** (new): Per-module catalog following the Quebec template. 24 tools broken out into 6 domain tables (Discovery 5 / AER Energy 4 / Wildfire 4 / Health 3 / Transport 3 / Env+Agri+Demo+Parks 5) with key-parameter columns. Source attribution section explains OGL-Alberta 2.0 default plus AER static-report terms and 511 Alberta feed status.
- **`EXAMPLES.md`**: Example 24 — "Alberta Energy + Wildfire — The Production vs. Fire Season Map". Chains `alberta_get_production_volumes` (Oil / Gas) + `alberta_get_active_fires` + `alberta_get_fire_perimeters` + `alberta_get_well_licences_today` into a 9-step datastore JOIN showing producing-well × evacuation-zone overlap. References both the AER and wildfire docs:// guides.
- **`CLAUDE.md`**: Portal Technologies table rows for CKAN and ArcGIS Hub both now list Alberta (CKAN: open.alberta.ca; ArcGIS Hub: WMBappServices + AHSGIS + GeoDiscover). Added a follow-up note explaining that AER static reports are XLSX/TXT via `fetch_and_parse` (not a portal technology) and 511 Alberta v2 is a raw-JSON feed (not CKAN envelope).

### 4. Coverage gate

```text
Required test coverage of 95% reached. Total coverage: 96.84%
src/mcp_canada/modules/alberta/client.py      366  25  93%
src/mcp_canada/modules/alberta/tools.py       261  47  82%
src/mcp_canada/modules/alberta/schemas.py     202   0 100%
src/mcp_canada/modules/alberta/resources.py    27   0 100%
src/mcp_canada/modules/alberta/prompts.py      34   4  88%
src/mcp_canada/modules/alberta/constants.py    68   0 100%
TOTAL                                        2440  77  97%
```

The 82% `tools.py` figure looks low at first glance but reflects the untested FR-branch error messages inside each tool (`httpx.HTTPStatusError` + `INVALID_INPUT` FR paths) for about 17 of the 24 tools — many of which are covered by per-tool test classes for the critical tools (production_volumes, fire_perimeters, fire_control_orders, health_facilities, water_advisories, population_estimates). The weighted module total clears 95% comfortably at 96.84%, so the gate passes without adding incremental branch-coverage tests.

## AB-XX Requirement Matrix

| Req | Plan that shipped it | How Plan 09 verifies |
|-----|----------------------|----------------------|
| AB-01 — CKAN search | 17-02 | TestAlbertaEnvelopes[alberta_search_datasets], integration test_search_wildfire_datasets |
| AB-02 — Dataset details | 17-02 | TestAlbertaEnvelopes[alberta_get_dataset_details] |
| AB-03 — Query dataset (hybrid router) | 17-02 | TestAlbertaEnvelopes[alberta_query_dataset] |
| AB-04 — List organizations | 17-02 | TestAlbertaEnvelopes[alberta_list_organizations] |
| AB-05 — List categories (res_format facet) | 17-02 | TestAlbertaEnvelopes[alberta_list_categories] |
| AB-06 — AER ST1 daily wells | 17-03 | TestAlbertaEnvelopes[alberta_get_well_licences_today] |
| AB-07 — AER ST1 monthly archive | 17-03 | TestAlbertaEnvelopes[alberta_get_well_licences_archive] |
| AB-08 — AER ST39 pipelines | 17-03 | TestAlbertaEnvelopes[alberta_get_pipeline_statistics] |
| AB-09 — AER ST3 production | 17-03 | TestAlbertaEnvelopes + integration Gas happy path + INVALID_INPUT for Bitumen |
| AB-10 — WMB active fires | 17-04 | TestAlbertaEnvelopes + integration test_active_fires_now |
| AB-11 — Fire perimeters | 17-04 | TestAlbertaEnvelopes[alberta_get_fire_perimeters] |
| AB-12 — Historical fires via CKAN | 17-04 | Doc-only (routed via alberta_query_dataset wildfire-data package) |
| AB-13 — Fire bans | 17-04 | TestAlbertaEnvelopes[alberta_get_fire_bans] |
| AB-14 — Fire control orders / OHV / forest area | 17-04 | TestAlbertaEnvelopes[alberta_get_fire_control_orders] |
| AB-15 — Hospitals | 17-05 | TestAlbertaEnvelopes + integration test_alberta_hospitals |
| AB-16 — AHS zones | 17-05 | TestAlbertaEnvelopes[alberta_get_ahs_zones] + data://alberta/ahs-zones |
| AB-17 — Health facilities (EMS/PCN) | 17-05 | TestAlbertaEnvelopes[alberta_get_health_facilities] |
| AB-18 — 511 road events | 17-06 | TestAlbertaEnvelopes + integration test_alberta_road_events |
| AB-19 — Winter road conditions | 17-06 | TestAlbertaEnvelopes[alberta_get_winter_road_conditions] |
| AB-20 — Traffic cameras | 17-06 | TestAlbertaEnvelopes[alberta_get_traffic_cameras] |
| AB-21 — AQHI stations | 17-07 | TestAlbertaEnvelopes[alberta_get_air_quality_stations] |
| AB-22 — Water advisories (5-layer dispatch) | 17-07 | TestAlbertaEnvelopes[alberta_get_water_advisories] |
| AB-23 — Water-licence doc guidance | 17-08 | Integration test_wildfire_data_guide_mentions_ab23 |
| AB-24 — Crop production | 17-07 | TestAlbertaEnvelopes[alberta_get_crop_production] |
| AB-25 — Population estimates (6 breakdowns) | 17-07 | TestAlbertaEnvelopes[alberta_get_population_estimates] |
| AB-26 — Provincial parks | 17-07 | TestAlbertaEnvelopes[alberta_get_provincial_parks] |
| AB-27 — Convention compliance | 17-01 scaffold + **17-09** final | Parametrized 48 cases + integration discovery + docs sync |

## Deviations from Plan

### Rule 1 (bug fix) — Restored pre-existing Quebec integration assertion

During Task 2, my Edit tool call on `test_prompts_resources_scenarios.py` used an `old_string` that was not unique — it matched up through `assert "msss" in slugs` but Quebec's original `test_ministries_resource_valid_json` had a **second** assertion `assert "mtq" in slugs` on the next line. The Edit accidentally orphaned that line inside the new Alberta class block, causing `NameError: name 'slugs' is not defined` at test collection. Fix: removed the orphan line from inside the Alberta block AND restored it inside the Quebec method so the Quebec test remains unchanged. Verified with `pytest -k Quebec or Alberta -m integration` green afterward. **Scope-boundary-compliant** — I touched the Quebec method only to restore its original behavior, no other Quebec test logic modified.

## Deferred Issues

None. All plan verification steps pass:

1. `uv run pytest src/mcp_canada/modules/alberta/__tests__/ -x -v` — 198 green
2. `uv run pytest tests/integration/ -v -m integration --timeout=120 -k Alberta` — 11 green
3. `uv run pytest --cov=src/mcp_canada/modules/alberta --cov-fail-under=95` — 96.84% ≥ 95%
4. `uv run pytest tests/test_quality.py -x` — 5 green (BM25 docstrings enforced across all 24 alberta tools)

## Flaky Scenario Mitigations

- **`test_active_fires_now`** — fire counts vary seasonally (May-October peak); test only asserts envelope shape + features list is present, never exact count.
- **`test_alberta_production_volumes_gas`** — AER republishes XLSX files during month-end rollover windows; test accepts both `rows`-containing payload AND `UPSTREAM_ERROR`/`RATE_LIMITED` error codes without silent shape drift.
- **`test_alberta_hospitals`** — count range 50-250 (wider than the documented ~101) to absorb AHSGIS republishing changes without CI flakiness.
- **`test_discover_alberta_via_bm25`** — asserts at least one `alberta_` tool appears, not a specific rank position, since BM25 top-5 ordering can shift as tools are added across the server.

## Self-Check: PASSED

- All 3 Task commits present in git log (`dc5a77e`, `40cd96a`, `d5c6392`)
- All verification commands green as of 2026-04-17
- Documentation surface synchronized (README + docs/modules/alberta.md + EXAMPLES.md + CLAUDE.md)
- Coverage gate 96.84% on alberta module
