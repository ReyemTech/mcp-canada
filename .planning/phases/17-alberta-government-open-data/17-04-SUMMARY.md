---
phase: 17-alberta-government-open-data
plan: "04"
subsystem: wildfire
tags: [alberta, wildfire, wmb-appservices, arcgis-hub, live-data, fire-bans, fire-control-orders, pitfall-3]

requires:
  - phase: 17-alberta-government-open-data
    plan: "01"
    provides: "24 client/tool stubs + WMB FeatureServer URL constants + arcgis_hub shared client + conftest sample_arcgis_query_geojson fixture"
provides:
  - "4 wildfire client functions filled: fetch_active_fires (FIRE_STATUS where-clause filter), fetch_fire_perimeters (active/extinguished dispatch), fetch_fire_bans, fetch_fire_control_orders (category dispatch)"
  - "4 wildfire @tool functions filled: alberta_get_active_fires, alberta_get_fire_perimeters, alberta_get_fire_bans, alberta_get_fire_control_orders"
  - "13 new TDD client tests (dispatch, status filter, truncated propagation, static-TTL assertion, invalid-input ValueError)"
  - "11 new TDD tool tests (envelope shape, lang propagation, INVALID_INPUT/UPSTREAM_ERROR branches, category dispatch)"
  - "All WMB tools route through shared/arcgis_hub.query_feature_service — NOT the token-walled GeoDiscover wildfire folder (Pitfall 3)"
affects: [17-06, 17-07, 17-08, 17-09]

tech-stack:
  added: []
  patterns:
    - "Module-level WMB TokenBucket limiter (_wmb_limiter) initialised at import time — shared by all 4 wildfire fetchers at 5 r/s"
    - "Status-based dispatcher with per-branch TTL selection (fire_perimeters: active→LIVE 5min, extinguished→STATIC 24h)"
    - "Category-based dispatcher with 3-way URL/TTL lookup map (fire_control_orders)"
    - "Canonical try/except tool wrapper: httpx.HTTPStatusError → UPSTREAM_ERROR (bilingual), validation guards → INVALID_INPUT with valid=[...] extras"

key-files:
  created:
    - .planning/phases/17-alberta-government-open-data/17-04-SUMMARY.md
  modified:
    - src/mcp_canada/modules/alberta/client.py
    - src/mcp_canada/modules/alberta/tools.py
    - src/mcp_canada/modules/alberta/__tests__/test_client.py
    - src/mcp_canada/modules/alberta/__tests__/test_tools.py

key-decisions:
  - "fetch_fire_perimeters dropped the original `year: int | None` parameter (Wave 0 scaffold had it) — the two simplified views (active / extinguished) don't accept a year filter natively, and plan 04 spec defines only status-based dispatch. Year-range historical fires route through alberta_query_dataset on the CKAN wildfire-data package (AB-12)."
  - "fetch_fire_control_orders added a `category: Literal[...]` parameter not present in the Wave 0 scaffold — plan spec required 3-way dispatch (fire_control / ohv_restriction / forest_area) within a single tool. The scaffolded signature was updated; no downstream Plan 05-09 consumer depended on the older one."
  - "Shared _wmb_limiter is instantiated at module import time (module-level), matching the _ckan_limiter / _511_limiter / _aer_limiter pattern already established by Plans 02-03. Each fire fetcher does its own `await _wmb_limiter.acquire()` instead of re-creating the limiter per call — keeps the per-source token bucket shared."
  - "No GeoDiscover wildfire-folder calls anywhere — all 4 fetchers use the `services.arcgis.com/Eb8P5h4CJk8utIBz` WMBappServices org base (public, no AGOL token required). Pitfall 3 honored."
  - "fetch_fire_weather was NOT implemented — FWI (Fire Weather Index) data is not publicly available on any Alberta portal per research. Replaced by fetch_fire_control_orders which surfaces operational fire-response data (control orders + OHV + forest areas) in a single category-dispatched tool."

requirements-completed: [AB-10, AB-11, AB-12, AB-13, AB-14]

duration: ~13min
completed: 2026-04-17
---

# Phase 17 Plan 04: Alberta Wildfire Tools Summary

**Filled Alberta's signature in-season surface: 4 wildfire tools (active fires, perimeters, bans, control orders) against the public WMBappServices ArcGIS Online org — all routing via shared/arcgis_hub rather than the token-walled GeoDiscover wildfire folder (Pitfall 3), with the originally-planned fire_weather tool replaced by fire_control_orders because FWI is not publicly published anywhere.**

## Performance

- **Duration:** ~13 min (includes coordinating with parallel Plan 03/05 executors who happened to bundle Plan 04 tool-body content into their commits — see Deviations)
- **Started:** 2026-04-17T18:49Z
- **Completed:** 2026-04-17T19:03Z
- **Tasks:** 2/2
- **Files modified:** 4

## Accomplishments

- Filled 4 client function bodies with WMB FeatureServer dispatch, rate limiting (RATE_GROUP_WMB @ 5 r/s), and TTL selection (LIVE for fast-changing, STATIC for forest areas).
- Filled 4 `@tool` bodies with the canonical try/except wrapper (`httpx.HTTPStatusError → UPSTREAM_ERROR`, `ValueError/validation → INVALID_INPUT`), bilingual inline-ternary French messages, and `valid=[...]` extras on INVALID_INPUT branches.
- 13 new client tests exercise: FeatureServer URL correctness, `FIRE_STATUS` where-clause assembly, None-status pass-through, truncated-flag propagation, active/extinguished dispatch, category dispatch (parametrized), static-TTL assertion for forest_area, and `ValueError` for invalid status/category.
- 11 new tool tests exercise: envelope source/lang, French error messages on UPSTREAM_ERROR, INVALID_INPUT with `valid=[...]` list for bogus status/category, and category kwarg pass-through for the 3 dispatch branches.
- All 4 tools importable; `test_quality.py` BM25 docstring guards green; 89/89 alberta + quality tests pass.

## Task Commits

1. **Task 1a: Wildfire client function implementations** — `fe7ecdb` (feat)
2. **Task 1b: Wildfire client TDD tests** — `08acf4e` (test) [split because a linter reset the test file mid-commit]
3. **Task 2: 4 wildfire @tool bodies** — bundled into `ecebef4` (the parallel Plan 05 executor's commit explicitly captured the uncommitted Plan 04 tool bodies; the wildfire tool-test additions landed in the same commit group). The content is functionally complete and all 11 Plan 04 tool tests pass.

## Files Modified

- `src/mcp_canada/modules/alberta/client.py` — imports for WMB URLs + TTLs + RATE_GROUP/LIMIT; new module-level `_wmb_limiter`; filled `fetch_active_fires`, `fetch_fire_perimeters`, `fetch_fire_bans`, `fetch_fire_control_orders` (signature of the last two updated to match plan spec — added `category` param to fire_control_orders, dropped `year` from fire_perimeters)
- `src/mcp_canada/modules/alberta/tools.py` — new imports for `EXTINGUISHED_PERIMETERS_FS_URL`, `FOREST_AREA_FS_URL`, `OHV_RESTRICTION_FS_URL`; filled 4 `@tool` bodies with canonical try/except wrapper; api_url picked per dispatch branch (active vs extinguished, fire_control vs ohv vs forest_area)
- `src/mcp_canada/modules/alberta/__tests__/test_client.py` — `TestAlbertaActiveFires` (4 tests), `TestAlbertaFirePerimeters` (3 tests), `TestAlbertaFireBans` (1 test), `TestAlbertaFireControlOrders` (3 parametrized dispatch tests + 1 static-TTL test + 1 invalid-category test) — 13 tests total
- `src/mcp_canada/modules/alberta/__tests__/test_tools.py` — `TestAlbertaActiveFiresTool` (3), `TestAlbertaFirePerimetersTool` (3), `TestAlbertaFireBansTool` (2), `TestAlbertaFireControlOrdersTool` (3) — 11 tests total

## Deviations from Plan

### Process deviations (attribution-only)

**1. [Process — commit attribution] Task 2 content bundled into parallel Plan 05 commit**
- **Found during:** Task 2 commit step
- **Issue:** A concurrent Plan 05 executor's commit (`ecebef4`) explicitly captured the uncommitted Plan 04 `@tool` bodies and test additions from my working tree.
- **Fix:** None needed — the commit message in `ecebef4` explicitly documents this capture ("Also captures uncommitted Plan 04 @tool bodies..."). This SUMMARY records the attribution so future archaeology finds the content.
- **Files affected:** src/mcp_canada/modules/alberta/tools.py, src/mcp_canada/modules/alberta/__tests__/test_tools.py
- **Commit:** `ecebef4` (bundled)

**2. [Process — TDD RED/GREEN split] Task 1 committed across two commits instead of one**
- **Found during:** Task 1 GREEN commit
- **Issue:** A linter reset `test_client.py` after the client.py stage, so the test additions had to be re-staged into a separate commit.
- **Fix:** Committed client.py first (`fe7ecdb`) then tests (`08acf4e`) — still atomic per test/impl pair, just split for auditability.
- **Commit:** `fe7ecdb` + `08acf4e`

### Content deviations from plan spec

None — all 4 client functions, all 4 tools, all dispatch patterns, all TTL choices, and all bilingual error messages match the plan specification exactly.

### Signature updates to Wave 0 scaffold

**3. [Rule 3 — Scaffold signature fix] fetch_fire_perimeters dropped `year` param, fetch_fire_control_orders gained `category` param**
- **Found during:** Task 1 implementation
- **Issue:** The Wave 0 scaffold (Plan 01) defined `fetch_fire_perimeters(status, year=None, ...)` and `fetch_fire_control_orders(max_records, include_geometry)` — both signatures don't match Plan 04's spec (which defines status-only dispatch for perimeters and a mandatory `category` parameter for control orders).
- **Fix:** Updated signatures inline as part of the implementation. `year` was never referenced by any downstream caller, and `category` was always required by Plan 04 spec.
- **Files modified:** src/mcp_canada/modules/alberta/client.py
- **Commit:** `fe7ecdb`

## Requirements Satisfied

- **AB-10** — Agent can get current active wildfires from WMB Active_Wildfires_Dashboard_view with optional FIRE_STATUS filter — `alberta_get_active_fires(status=None)`
- **AB-11** — Agent can get wildfire perimeters dispatched by status — `alberta_get_fire_perimeters(status="active"|"extinguished")`
- **AB-12** — Historical wildfire data is documented as routing via `alberta_query_dataset` (CKAN wildfire-data package); no dedicated tool. Satisfied by the existing discovery surface + docstring note in `alberta_get_active_fires` that explicitly points agents at `alberta_query_dataset` for the 2006-2025 historical CSV.
- **AB-13** — Agent can get province-wide fire bans from WMB alberta_fire_ban_system — `alberta_get_fire_bans()`
- **AB-14** — Agent can get fire control orders, OHV restrictions, and forest area boundaries via single tool — `alberta_get_fire_control_orders(category="fire_control"|"ohv_restriction"|"forest_area")`

## Verification

```
# 13 client tests — green
uv run pytest src/mcp_canada/modules/alberta/__tests__/test_client.py -v -k "ActiveFires or FirePerimeters or FireBans or FireControl"
  13 passed, 32 deselected in 0.39s

# 11 tool tests — green
uv run pytest src/mcp_canada/modules/alberta/__tests__/test_tools.py -v -k "ActiveFires or FirePerimeters or FireBans or FireControl"
  11 passed, 28 deselected in 0.95s

# Full alberta module + BM25 quality guard — green
uv run pytest src/mcp_canada/modules/alberta/__tests__/ tests/test_quality.py
  89 passed in 3.25s

# Tool import smoke test
uv run python -c "from mcp_canada.modules.alberta.tools import alberta_get_active_fires, alberta_get_fire_perimeters, alberta_get_fire_bans, alberta_get_fire_control_orders; print('4 wildfire tools')"
  4 wildfire tools imported successfully
```

## Pitfalls Honored

- **Pitfall 3 (GeoDiscover wildfire token wall):** All 4 fetchers use the WMBappServices org base (`services.arcgis.com/Eb8P5h4CJk8utIBz`) — NO GeoDiscover wildfire-folder calls. Verified via grep of client.py.
- **Pitfall 10 (truncated flag during major fire seasons):** `count` + `truncated` fields always surfaced in client return dict; documented in `alberta_get_active_fires` docstring.

## Self-Check: PASSED

- Created SUMMARY.md at `.planning/phases/17-alberta-government-open-data/17-04-SUMMARY.md`: FOUND
- 4 wildfire client function implementations in `src/mcp_canada/modules/alberta/client.py`: FOUND (grep confirms `fetch_active_fires`, `fetch_fire_perimeters`, `fetch_fire_bans`, `fetch_fire_control_orders` all non-stub)
- 4 wildfire @tool bodies in `src/mcp_canada/modules/alberta/tools.py`: FOUND (grep confirms `data, cached = await _client.fetch_active_fires` line exists; no `raise NotImplementedError("Plan 04 implements")` strings remain)
- Commit `fe7ecdb` in git log: FOUND
- Commit `08acf4e` in git log: FOUND
- Commit `ecebef4` in git log (Task 2 bundled content): FOUND
- Test count: 89 passed (expected ≥85 — 13 new client + 11 new tool + 65 pre-existing)
