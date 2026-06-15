---
phase: 19-saskatchewan-government-open-data
plan: 04
subsystem: saskatchewan/environment
tags: [arcgis-hub, spsa, fire-bans, wildfire, air-quality, empty-is-valid, wave-3]
dependency_graph:
  requires: [19-03-PLAN.md (client stubs + conftest fixtures)]
  provides: [SK-10, SK-11, SK-12 — 3 curated environment tools callable]
  affects: [19-06 prompts/resources (wildfire + air-quality prompts), 19-07 integration tests]
tech_stack:
  added: []
  patterns: [SPSA-separate-REST-server dispatch, empty-is-valid pattern (ban_scope→layer), year+cause AND-composition WHERE clause]
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/saskatchewan/client.py
    - src/mcp_canada/modules/saskatchewan/tools.py
    - src/mcp_canada/modules/saskatchewan/__tests__/test_client.py
    - src/mcp_canada/modules/saskatchewan/__tests__/test_tools.py
decisions:
  - "fetch_fire_bans validates ban_scope before calling arcgis_hub (double-guard: tool INVALID_INPUT + client ValueError) — mirrors Alberta ST3 + mineral dispatch patterns"
  - "api_name='saskatchewan-spsa-firebans' for fire bans (distinguishes SPSA server from Hub in _meta envelope); historic wildfires + air quality use 'saskatchewan-geohub'"
  - "WHERE clause for historic wildfires: year-only='YEAR=N', cause-only='CAUSE1 LIKE %..%', both='YEAR=N AND CAUSE1 LIKE %..%', neither='1=1' — composed in client not tool"
  - "AQHI is a weather.gc.ca URL (not a numeric score) — documented in docstring where agents will see it"
  - "Empty fire bans payload (SAMPLE_ARCGIS_FIRE_BANS_EMPTY fixture) explicitly tested as valid success (count=0, _meta envelope) not error — same lesson as Manitoba flood alerts"
metrics:
  duration: "8 minutes"
  completed_date: "2026-06-15"
  tasks_completed: 2
  files_modified: 4
---

# Phase 19 Plan 04: Saskatchewan Environment Domain Summary

Implemented Saskatchewan's environment domain: 3 curated tools (SK-10, SK-11, SK-12) covering live fire bans via the SPSA separate REST server, historic wildfire boundaries, and hourly ambient air quality. The fire-ban tool is the architectural highlight — it dispatches `ban_scope` to 4 SPSA layers on a non-Hub server and explicitly handles the empty-is-valid off-season case.

## One-Liner

3 environment tools via TDD: fire bans (SPSA ban_scope→layer 0/2/3/8 dispatch, empty=valid), historic wildfire boundaries (year+cause WHERE composition), and live air quality (community filter; AQHI=weather.gc.ca URL).

## Tasks Completed

| Task | Commit | Description |
|------|--------|-------------|
| 1. Client bodies + client tests (TDD RED→GREEN) | e765b37 | fetch_fire_bans/fetch_historic_wildfires/fetch_air_quality; 22 client tests; empty-is-valid; layer dispatch asserted via call_args |
| 2. 3 environment @tool functions + tool tests (TDD RED→GREEN) | a245099 | saskatchewan_get_fire_bans/get_historic_wildfires/get_air_quality; 19 tool tests; INVALID_INPUT guard; empty-fire-ban-is-valid-make-response test |

## Task 1: Client Bodies

**fetch_fire_bans:**
- Validates `ban_scope` against `FIRE_BAN_LAYERS` dict before calling FeatureServer → raises `ValueError` for unknown scope
- Dispatches to `FIRE_BAN_FS_URL` (gis.saskatchewan.ca/egis) — NOT the Hub org — with correct layer_id
- Empty `features=[]` in off-season returns `{"features": [], "count": 0, "truncated": False, "scope": ban_scope}` — NEVER raises
- Uses `_spsa_limiter` (RATE_GROUP_SPSA, 5 r/s) + `CACHE_TTL_ALERTS` (5min)

**fetch_historic_wildfires:**
- WHERE clause composed: `YEAR={year}` for year, `CAUSE1 LIKE '%{cause}%'` for cause, joined with `AND` when both, `1=1` when neither
- `WILDFIRE_BOUNDARIES_FS_URL` layer 0; out_fields: `YEAR,FIRENAME,CAUSE1,HECTARES,STATUS,STARTDATE,OUTDATE,TYPE`
- Uses `_hub_limiter` + `CACHE_TTL_META` (24h)

**fetch_air_quality:**
- WHERE: `COMMUNITY='{community}'` when set, `1=1` otherwise
- `AIR_QUALITY_FS_URL` layer 0; out_fields include `AQHI` (weather.gc.ca URL) and `DATETIME`
- Uses `_hub_limiter` + `CACHE_TTL_LIVE` (15min — data refreshes hourly)

**Key call_args assertions in tests:**
- Fire ban tests assert `mock_qfs.call_args[0][0] == FIRE_BAN_FS_URL` and `mock_qfs.call_args[0][1] == <layer>` — pins SPSA-server + layer-dispatch contract
- `SAMPLE_ARCGIS_FIRE_BANS_EMPTY` fixture (`([], False)`) explicitly returns `count=0`, not an exception

## Task 2: Tool Functions

**saskatchewan_get_fire_bans:**
- `ban_scope: Literal["urban", "rural", "provincial", "parks"]` — pre-checked at tool layer before client call
- `api_name="saskatchewan-spsa-firebans"` — distinct from Hub tools for traceability
- Docstring notes: "An empty result means NO ACTIVE BANS (normal off-season state) — this is NOT an error"
- French error message via inline `lang == 'fr'` ternary

**saskatchewan_get_historic_wildfires:**
- `year: int | None`, `cause: str | None` — both optional, passed through to client
- `api_name="saskatchewan-geohub"`, `api_url=WILDFIRE_BOUNDARIES_FS_URL/0`

**saskatchewan_get_air_quality:**
- `community: str | None` — optional; docstring lists the 6 valid communities and notes AQHI is a URL
- `api_name="saskatchewan-geohub"`, `api_url=AIR_QUALITY_FS_URL/0`

All 3 tools: standalone `@tool`, `lang: Literal["en", "fr"] = "en"`, `make_response`/`make_error`, single-line `Use for:` + 8+ `Keywords:`, `saskatchewan_` prefix.

## Verification Results

```
uv run pytest src/mcp_canada/modules/saskatchewan/__tests__/ -x
→ 123 passed in 0.90s

uv run pytest --cov=src/mcp_canada --cov-fail-under=95
→ 96.76% total coverage (2635 passed)
```

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

Files verified:
- `src/mcp_canada/modules/saskatchewan/client.py` — fetch_fire_bans/fetch_historic_wildfires/fetch_air_quality bodies implemented
- `src/mcp_canada/modules/saskatchewan/tools.py` — 3 @tool functions added; __all__ updated
- `src/mcp_canada/modules/saskatchewan/__tests__/test_client.py` — TestSaskGetFireBans/TestSaskGetHistoricWildfires/TestSaskGetAirQuality filled (22 tests)
- `src/mcp_canada/modules/saskatchewan/__tests__/test_tools.py` — TestSaskGetFireBansTool/TestSaskGetHistoricWildfiresTool/TestSaskGetAirQualityTool filled (19 tests)

Commits: e765b37 (client) + a245099 (tools) both in git log.
