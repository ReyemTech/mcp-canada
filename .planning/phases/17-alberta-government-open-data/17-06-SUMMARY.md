---
phase: 17-alberta-government-open-data
plan: "06"
subsystem: transport-511
tags: [alberta, 511, transport, wave-3, tdd, pitfall-5, pitfall-6]

requires:
  - phase: 17-alberta-government-open-data
    plan: "01"
    provides: "_511_get helper + 3 fetch_* stubs + sample_511_event_list / sample_511_winter_roads / sample_511_cameras fixtures + autouse patch_cache_and_limiter"
provides:
  - "3 filled transport client functions: fetch_road_events, fetch_winter_road_conditions, fetch_traffic_cameras (all use _511_get, NOT _api_get)"
  - "3 filled @tool bodies: alberta_get_road_events, alberta_get_winter_road_conditions, alberta_get_traffic_cameras with bilingual UPSTREAM_ERROR handling"
  - "10 unit tests covering 511 client (endpoint targeting, filter behaviour, TTL selection, rate group verification)"
  - "7 unit tests covering 511 tools (envelope shape, parameter pass-through, English and French error paths)"
  - "Client-side substring filtering for event_type (EventType field) and area_name (AreaName field) — 511 has no native filter params"
affects: [17-09]

tech-stack:
  added: []
  patterns:
    - "Client-side substring filtering on raw 511 JSON (case-insensitive lowercase match) — 511 v2 API has no filter params"
    - "TTL split by refresh cadence: LIVE (5min) for events/winter-roads, MONTHLY (24h) for cameras (stable locations)"
    - "Cache-key namespace 'alberta:511:{endpoint}:{filter}' isolates 511 cache from Alberta CKAN cache"

key-files:
  created: []
  modified:
    - src/mcp_canada/modules/alberta/client.py
    - src/mcp_canada/modules/alberta/tools.py
    - src/mcp_canada/modules/alberta/__tests__/test_client.py
    - src/mcp_canada/modules/alberta/__tests__/test_tools.py

key-decisions:
  - "Filter client-side (Python list comprehension with substring check) instead of passing to the server — 511 v2 endpoints accept no filter params; fetching the full list (142 events / 1121 winter roads / 376 cameras) once per TTL window is cheap and cached."
  - "TrafficCameras uses CACHE_TTL_MONTHLY (24h), not CACHE_TTL_LIVE, because camera locations are stable reference data; the snapshot image bytes refresh continuously upstream but the JSON listing of locations + Views URLs does not change."
  - "event_type and area_name filters operate on the uppercase field names ('EventType', 'AreaName') directly — schemas.py has snake_case flat models (Alberta511Event.event_type), but the 511 raw JSON still uses PascalCase; since fetch_* returns the raw dicts (not parsed Pydantic models), the filter hits the API field names."
  - "No /ferry or /traveltime tool — research Pitfall 5 confirmed those endpoints 404; only /event, /winterroads, /cameras are live."

requirements-completed: [AB-18, AB-19, AB-20]

duration: ~4min
completed: 2026-04-17
---

# Phase 17 Plan 06: Alberta 511 Transport Tools Summary

**Filled the 3 Alberta 511 transport tools — road events (closures + construction + incidents), winter road conditions, and traffic cameras — all using the `_511_get` helper seeded in Plan 01, with LIVE 5-minute TTL for events/conditions and MONTHLY 24-hour TTL for stable camera locations.**

## Performance

- **Duration:** ~4 min (single executor run)
- **Started:** 2026-04-17T19:09Z
- **Completed:** 2026-04-17T19:13Z
- **Tasks:** 2/2
- **Files modified:** 4

## Accomplishments

- Filled 3 client function bodies (`fetch_road_events`, `fetch_winter_road_conditions`, `fetch_traffic_cameras`) with `cached_fetch` + `get_limiter(RATE_GROUP_511, RATE_LIMIT_511)` wiring
- Filled 3 `@tool` bodies with bilingual inline-ternary UPSTREAM_ERROR handling and `make_response` / `make_error` envelopes
- Client-side substring filtering for `event_type` and `area_name` since 511 v2 has no native filter params
- `_511_get` used in all 3 client functions — Pitfall 6 honored (returns raw JSON list, not CKAN envelope)
- Pitfall 5 documented in tool docstrings (511 docs page 404s but API is live)
- All 17 Plan 06 tests green (10 client + 7 tool); BM25 `test_quality.py` green

## Task Commits

1. **Task 1 RED: Failing tests for 3 transport client functions** — `43cedbe` (test)
2. **Task 1 GREEN: 3 transport client functions** — `1aba8c6` (feat)
3. **Task 2 RED: Failing tests for 3 transport @tool bodies** — `539103d` (test)
4. **Task 2 GREEN: 3 transport @tool bodies** — `90263a4` (feat)

## Files Modified

- `src/mcp_canada/modules/alberta/client.py` — 3 `fetch_*` bodies filled (68 inserted / 9 removed); replaces the 3 Plan 01 `NotImplementedError` stubs.
- `src/mcp_canada/modules/alberta/tools.py` — 3 `@tool` bodies filled (61 inserted / 11 removed); docstrings expanded to document Pitfall 5 (undocumented API) + Pitfall 6 (raw JSON list).
- `src/mcp_canada/modules/alberta/__tests__/test_client.py` — `TestAlbertaRoadEvents` (4 tests), `TestAlbertaWinterRoadConditions` (3 tests), `TestAlbertaTrafficCameras` (3 tests) filled; 10 tests total.
- `src/mcp_canada/modules/alberta/__tests__/test_tools.py` — `TestAlbertaRoadEventsTool` (3 tests), `TestAlbertaWinterRoadConditionsTool` (2 tests), `TestAlbertaTrafficCamerasTool` (2 tests) filled; 7 tests total.

## Test Coverage

**Client tests (10):**

| Class | Tests |
|-------|-------|
| TestAlbertaRoadEvents | 4 (endpoint='event', event_type filter, no-filter returns all, CACHE_TTL_LIVE + RATE_GROUP_511) |
| TestAlbertaWinterRoadConditions | 3 (endpoint='winterroads', area_name filter, CACHE_TTL_LIVE) |
| TestAlbertaTrafficCameras | 3 (endpoint='cameras', Views array preserved, CACHE_TTL_MONTHLY) |

**Tool tests (7):**

| Class | Tests |
|-------|-------|
| TestAlbertaRoadEventsTool | 3 (envelope with api_name='alberta-511' + /event URL, event_type pass-through, French UPSTREAM_ERROR on HTTP 502) |
| TestAlbertaWinterRoadConditionsTool | 2 (envelope with /winterroads URL, area_name pass-through) |
| TestAlbertaTrafficCamerasTool | 2 (envelope with /cameras URL + Views preserved, English UPSTREAM_ERROR on HTTP 503) |

## Deviations from Plan

**None on scope or content.** Plan 06 executed as specified:

- The plan prescribed 3 client functions + 3 tool functions + 8 minimum test scenarios. Delivered 3+3 and 17 test scenarios (exceeded the minimum by adding Views-array preservation and English-error paths for better coverage).
- The plan described the canonical tool wrapper; all 3 tools follow it identically with per-tool api_url strings (`/event`, `/winterroads`, `/cameras`) and a single shared UPSTREAM_ERROR message template ("511 Alberta query failed: HTTP {status}" / "Échec de la requête 511 Alberta : HTTP {status}").
- Cache key prefix uses `alberta:511:{endpoint}:{filter}` per Plan 01 convention (not just `alberta:`) to cleanly isolate 511 cache entries from CKAN entries.

**Parallel-executor note:** During Plan 06 execution, parallel executors running Plans 07 (environment/agri/demographics/parks) committed additional test classes to the same `test_client.py` file. Those changes are outside Plan 06 scope and are not tracked here; they will be committed by their owning plan.

## Pitfalls Addressed in Code

| Pitfall | Where | How |
|---------|-------|-----|
| **Pitfall 5** (511 docs page 404, but API live) | All 3 tool docstrings | "The 511 Alberta v2 API is undocumented (Pitfall 5 — the docs page redirects to /notfound) but stable" |
| **Pitfall 6** (511 returns raw JSON list, not CKAN envelope) | `fetch_*` client bodies + tool docstrings | All 3 use `_511_get` (NOT `_api_get`); docstrings note "returns a raw JSON list (Pitfall 6), not a CKAN envelope" |
| **No /ferry or /traveltime** | Scope boundary honored | Only `/event`, `/winterroads`, `/cameras` touched — research confirmed the other endpoints 404. |

## Handoff to Next Plans

- **Plan 07 (Wave 3, parallel):** No dependency on Plan 06 — different portal (GeoDiscover vs 511).
- **Plan 08 (Wave 4 prompts/resources):** If a `alberta_check_road_conditions` quick-lookup prompt is added, it should reference `alberta_get_winter_road_conditions` (single tool call).
- **Plan 09 (Wave 5 parametrized tests):** `TestAlbertaEnvelopes` and `TestAlbertaLangParam` can now run against all 3 Plan 06 tools (envelope + lang propagation already verified per-tool).

## Self-Check: PASSED

- Commit `43cedbe` found in git log (Task 1 RED)
- Commit `1aba8c6` found in git log (Task 1 GREEN)
- Commit `539103d` found in git log (Task 2 RED)
- Commit `90263a4` found in git log (Task 2 GREEN)
- `src/mcp_canada/modules/alberta/client.py` modified — 3 client bodies filled
- `src/mcp_canada/modules/alberta/tools.py` modified — 3 `@tool` bodies filled
- `src/mcp_canada/modules/alberta/__tests__/test_client.py` modified — 10 Plan 06 tests added
- `src/mcp_canada/modules/alberta/__tests__/test_tools.py` modified — 7 Plan 06 tests added
- `uv run pytest src/mcp_canada/modules/alberta/__tests__/ tests/test_quality.py -x -k "RoadEvents or WinterRoad or TrafficCameras or test_quality"` → 22 passed
- `uv run python -c "from mcp_canada.modules.alberta.tools import alberta_get_road_events, alberta_get_winter_road_conditions, alberta_get_traffic_cameras"` → "3 transport tools importable"
