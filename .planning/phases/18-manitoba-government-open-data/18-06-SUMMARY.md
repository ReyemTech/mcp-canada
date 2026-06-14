---
phase: 18-manitoba-government-open-data
plan: "06"
subsystem: manitoba-511-transport
tags: [transport, 511, not-configured, key-gated, wave-5]
dependency_graph:
  requires:
    - "18-01 — Five11NotConfigured exception, _511_get helper, module-level _511_limiter, RATE_GROUP_511/RATE_LIMIT_511 constants"
    - "18-05 — prior plan; all prior client functions complete"
  provides:
    - "fetch_road_events — client body via _511_get('events')"
    - "fetch_winter_road_conditions — client body via _511_get('winterroads') + client-side area_name filter"
    - "fetch_traffic_cameras — client body via _511_get('cameras'), CACHE_TTL_META (24h)"
    - "manitoba_get_road_events — @tool with NOT_CONFIGURED fallback"
    - "manitoba_get_winter_road_conditions — @tool with NOT_CONFIGURED fallback"
    - "manitoba_get_traffic_cameras — @tool with NOT_CONFIGURED fallback"
  affects:
    - "src/mcp_canada/modules/manitoba/client.py"
    - "src/mcp_canada/modules/manitoba/tools.py"
    - "src/mcp_canada/modules/manitoba/__tests__/test_client.py"
    - "src/mcp_canada/modules/manitoba/__tests__/test_tools.py"
tech_stack:
  added: []
  patterns:
    - "Five11NotConfigured exception catch at tool layer → make_error(NOT_CONFIGURED)"
    - "monkeypatch.delenv for key-absent test path"
    - "monkeypatch.setenv + AsyncMock(return_value=list) for key-present test path"
    - "Client-side filter on AreaName field (winter roads area_name= param)"
    - "511 cameras cached at CACHE_TTL_META (24h) — stable locations"
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/manitoba/client.py
    - src/mcp_canada/modules/manitoba/tools.py
    - src/mcp_canada/modules/manitoba/__tests__/test_client.py
    - src/mcp_canada/modules/manitoba/__tests__/test_tools.py
decisions:
  - "Manitoba 511 key is GATED (confirmed by Wave 0 spike) — tools ship with NOT_CONFIGURED fallback regardless"
  - "Live integration deferred — key requires account registration at manitoba511.ca plus explicit API key request; not instant"
  - "_511_limiter reused from Wave 0 module-level singleton (not per-call get_limiter()) — consistent with Wave 0 decision"
  - "area_name filter for winter roads is client-side (not a 511 query param) — 511 API does not support server-side area filtering"
  - "Traffic cameras cached at CACHE_TTL_META (24h) — locations are stable; consistent with Alberta Plan 06 pattern"
  - "NOT_CONFIGURED message includes exact env var name (MANITOBA_511_KEY) and registration URL"
metrics:
  duration: "4 minutes"
  completed_date: "2026-06-14"
  tasks_completed: 2
  files_created: 0
  files_modified: 4
---

# Phase 18 Plan 06: Manitoba Transport / 511 Summary

3 transport tools (road events, winter roads, traffic cameras) implemented with NOT_CONFIGURED fallback for missing Manitoba 511 API key, following the Five11NotConfigured exception pattern from Wave 0.

## What Was Built

### Manitoba 511 Key Verdict (from Wave 0 Spike)

| Finding | Detail |
|---------|--------|
| Status | GATED |
| Key type | Developer API key — requires account registration at `https://www.manitoba511.ca/my511/register` |
| Provisioning | NOT instant — account approval + explicit key request required |
| Cost | Appears free (no paywall mentioned) but not publicly confirmed |
| Live integration | DEFERRED until key is obtained and confirmed free |

Tools ship regardless of key status. When `MANITOBA_511_KEY` is absent, every tool returns `make_error("NOT_CONFIGURED", ...)` with key-acquisition instructions. When key is present, tools fetch live data via `_511_get()`.

### Task 1: Client Bodies (2 commits, 8 tests)

Filled 3 `NotImplementedError` stubs in `client.py`:

| Function | Endpoint | Cache | Filter |
|----------|----------|-------|--------|
| `fetch_road_events` | `events` | CACHE_TTL_LIVE (5min) | optional event_type (client-side) |
| `fetch_winter_road_conditions` | `winterroads` | CACHE_TTL_LIVE (5min) | optional area_name (client-side) |
| `fetch_traffic_cameras` | `cameras` | CACHE_TTL_META (24h) | — |

All three:
- Use `_511_limiter.acquire()` then `_511_get(endpoint)` — rate-limited to 2 r/s
- Propagate `Five11NotConfigured` when `MANITOBA_511_KEY` env var is absent
- NEVER call `arcgis_hub.query_feature_service` (511 is a custom REST API, not FeatureServer)
- Return `(list[dict], bool)` tuple via `cached_fetch`

### Task 2: Tool Functions (1 commit, 10 tests)

Added 3 `@tool` functions at the bottom of `tools.py`:

| Tool | NOT_CONFIGURED | WITH_KEY | Keywords |
|------|---------------|----------|---------|
| `manitoba_get_road_events` | make_error("NOT_CONFIGURED", ...) | make_response(rows, ...) | road events closures construction incidents highway 511 transport... |
| `manitoba_get_winter_road_conditions` | make_error("NOT_CONFIGURED", ...) | make_response(rows, ...) | winter roads seasonal ice roads northern remote communities... |
| `manitoba_get_traffic_cameras` | make_error("NOT_CONFIGURED", ...) | make_response(rows, ...) | traffic cameras highway webcam snapshot images... |

All tools:
- Standalone `@tool` from `fastmcp.tools`
- `lang: Literal["en", "fr"] = "en"` parameter
- Bilingual NOT_CONFIGURED messages (EN/FR)
- `make_response()` / `make_error()` envelope
- `_API_NAME_511 = "manitoba-511"` in `_meta.source.api`
- 8+ Keywords in single-line docstring (BM25 requirement)
- `manitoba_` prefix

## Test Coverage

| Class | Tests | What is covered |
|-------|-------|----------------|
| `TestManitoba511` (client) | 8 | 3 key-absent raises, 3 mocked-key happy paths, 1 area_name filter, 1 anti-arcgis guard |
| `TestManitoba511RoadEvents` (tools) | 4 | NOT_CONFIGURED no-key, envelope mocked-key, lang passthrough, FR message |
| `TestManitoba511WinterRoads` (tools) | 3 | NOT_CONFIGURED no-key, envelope mocked-key, lang passthrough |
| `TestManitoba511Cameras` (tools) | 3 | NOT_CONFIGURED no-key, envelope mocked-key, lang passthrough |

Full suite: **156/156 Manitoba tests pass** (74 client + 82 tools). Coverage: **96.72%** (requirement ≥95%).

## Deviations from Plan

None — plan executed exactly as written.

Key clarification: The plan specified `max_records` as a parameter on the wave-0 stubs but the tool-layer functions only expose `lang` (keeping agent API clean). The client-layer functions accept `max_records` for flexibility.

## Authentication Gates

Manitoba 511 developer key is a known gate (documented in Wave 0 spike):
- Account registration: `https://www.manitoba511.ca/my511/register`
- Key request: explicit additional step after account creation
- Key not instantly provisioned (requires review/approval)
- Live integration test deferred — all unit tests use mocked keys

## Self-Check: PASSED

Files verified present:
- `src/mcp_canada/modules/manitoba/client.py` — fetch_road_events, fetch_winter_road_conditions, fetch_traffic_cameras bodies implemented
- `src/mcp_canada/modules/manitoba/tools.py` — manitoba_get_road_events, manitoba_get_winter_road_conditions, manitoba_get_traffic_cameras defined
- `src/mcp_canada/modules/manitoba/__tests__/test_client.py` — TestManitoba511 class with 8 tests
- `src/mcp_canada/modules/manitoba/__tests__/test_tools.py` — 3 test classes with 10 tests

Commits verified:
- 95e43a5: feat(18-06): implement 511 client bodies (key-gated) + 8 tests
- 0f58852: feat(18-06): add 3 transport @tool functions with NOT_CONFIGURED fallback + 10 tests
