---
phase: 16-quebec-government-open-data
plan: "06"
subsystem: quebec-module
tags: [gap-closure, tdd, wfs-paging, snake-case-mapper, ssl-tls, hydro-quebec]
dependency_graph:
  requires: [16-05-SUMMARY.md]
  provides: [fetch_bridge_structures paging + route normalizer, fetch_road_conditions snake_case mapper, fetch_and_parse ssl_context + Hydro-Québec SECLEVEL=1]
  affects: [src/mcp_canada/shared/parsers.py, src/mcp_canada/modules/quebec/client.py]
tech_stack:
  added: [ssl (stdlib — no new dependency)]
  patterns: [WFS count+startIndex paging loop, route normalizer zfill(5), scoped SSLContext per-URL]
key_files:
  created: []
  modified:
    - src/mcp_canada/shared/parsers.py
    - src/mcp_canada/modules/quebec/client.py
    - src/mcp_canada/modules/quebec/__tests__/test_client.py
    - src/mcp_canada/shared/__tests__/test_parsers.py
    - tests/integration/test_tool_scenarios.py
decisions:
  - "_normalize_route extracts digits and zfill(5): 'A-20' -> '00020', '132' -> '00132'"
  - "Post-parse bridge filter: match num_route (zero-padded) OR nom_route contains raw digits substring"
  - "BRIDGES_PAGE_SIZE=500: ~24 requests for 11696 structures, acceptable for 24h-cached inventory"
  - "Road conditions mapper: all keys lowercased by _normalize_key — 'numerosegment' not 'NumeroSegment'"
  - "timestamp maps to 'envigueurdepuis' — 'DateEtHeureCondition' does not exist in live CSV"
  - "SECLEVEL=1 SSLContext scoped to hydroquebec.com only — no global ssl change, no changes to shared/http.py"
  - "ssl_flag appended to fetch_and_parse cache key to prevent default/relaxed SSL cache collision"
metrics:
  duration: "~9 minutes"
  completed: "2026-04-12T03:04:17Z"
  tasks_completed: 3
  files_modified: 5
---

# Phase 16 Plan 06: Quebec Gap Closure Cycle 2 Summary

Gap closure cycle 2 for Phase 16 (Quebec Government Open Data). Addresses three live-confirmed root causes from the 2026-04-11 UAT retest: WFS paging + route normalizer, road conditions snake_case mapper, and scoped SSLContext for Hydro-Québec TLS.

## What Was Built

**Task 1 — MTQ Bridge WFS Paging + Route Normalizer**

MTQ's WFS bridge server caps default responses at 30 rows and silently ignores CQL_FILTER. The fix: a `count=500&startIndex={offset}` paging loop collects all 11,696 structures before post-parse filtering. A `_normalize_route` helper converts user-friendly route strings ('A-20', 'Autoroute 20', '20') to zero-padded 5-digit codes ('00020') matching the WFS data. The filter matches on `num_route` (exact zero-padded) OR `nom_route` containing the raw digit substring.

**Task 2 — Road Conditions snake_case Mapper**

`_parse_csv` applies `_normalize_key` to all column headers, converting PascalCase to lowercase: `NumeroSegment` → `numerosegment`, `DescriptionEtatChausseeFR` → `descriptionetatchausseefr`. The original mapper used the original PascalCase keys (all returning None). Fixed all 8 mapper keys to use the normalized forms. Also fixed `timestamp`: the live CSV uses `EnVigueurDepuis` (normalized: `envigueurdepuis`), not the non-existent `DateEtHeureCondition`. Unit test fixture replaced with real PascalCase headers (which `_parse_csv` normalizes) to prevent regression.

**Task 3 — Scoped SSLContext for Hydro-Québec TLS**

Hydro-Québec's XLSX server uses TLSv1.2/AES128-GCM-SHA256, rejected by Python OpenSSL 3.x SECLEVEL=2. Fix: `fetch_and_parse` gains an optional `ssl_context: ssl.SSLContext | None = None` parameter, passed as `verify=ssl_ctx` to `httpx.AsyncClient`. `fetch_electricity_data` builds a `SECLEVEL=1` context only when `file_url` contains `hydroquebec.com`. Cache key includes an `ssl_flag` to prevent collision between default-SSL and relaxed-SSL cached entries. No changes to `shared/http.py` — fix is fully scoped to the Hydro-Québec code path.

## Tests Added

| Test | Location | Purpose |
|------|----------|---------|
| `TestFetchBridgeStructuresPaging` (5 tests) | test_client.py | Paging loop, route normalizer, loop termination, municipality regression |
| `TestFetchRoadConditions` (3 new tests) | test_client.py | Real-header fixture with snake_case keys, bilingual, timestamp mapping |
| `TestFetchElectricityData` (2 new tests) | test_client.py | hydroquebec.com gets SSLContext, non-hydroquebec.com gets None |
| `TestFetchAndParseSSLContext` (3 tests) | test_parsers.py | verify=ctx passthrough, verify=True default, cache key isolation |
| `test_bridges_route_filter_returns_rows` | integration | WFS paging reaches A-20 rows (timeout=120) |
| `test_road_conditions_fields_populated` | integration | non-null route_num/region/pavement_status |
| `test_electricity_data_returns_rows` | integration | SSL handshake succeeds, non-empty data |
| Strict `test_get_bridge_structures_requires_filter` | integration | Removes tolerant `_meta in x or error in x` assertion |

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check

Files created/modified:
- [x] src/mcp_canada/shared/parsers.py — `ssl_context` parameter + `ssl_flag` cache key
- [x] src/mcp_canada/modules/quebec/client.py — `_normalize_route`, paging loop, snake_case mapper, SSL ctx
- [x] src/mcp_canada/modules/quebec/__tests__/test_client.py — new paging/road/SSL tests
- [x] src/mcp_canada/shared/__tests__/test_parsers.py — `TestFetchAndParseSSLContext`
- [x] tests/integration/test_tool_scenarios.py — 3 new integration tests + strict assertion upgrade

Commits:
- [x] 970a93a feat(16-06): WFS paging loop and route normalizer for bridge structures
- [x] 6979468 fix(16-06): fix fetch_road_conditions snake_case mapper keys
- [x] 23b7a33 fix(16-06): scoped SECLEVEL=1 SSLContext for Hydro-Québec XLSX TLS fix

Metrics:
- 1984 unit tests pass (0 failures)
- Coverage: 96.57% (≥95% requirement met)
- Ruff: clean on all modified files
- Pyright: clean on all modified files (pre-existing pandas import warnings unchanged)

## Self-Check: PASSED
