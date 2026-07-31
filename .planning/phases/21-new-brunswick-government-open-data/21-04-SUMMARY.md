---
phase: 21-new-brunswick-government-open-data
plan: 04
subsystem: api
tags: [arcgis-server, geonb, new-brunswick, flood, wetlands, mcp-tools]

# Dependency graph
requires:
  - phase: 21-new-brunswick-government-open-data
    provides: "Plan 01 scaffold (locked constants.py/client.py signatures, 22-tool manifest, live 21-SPIKE.md layer-id verification) and Wave 0's shared/arcgis_hub.py additions (list_arcgis_server_services, get_arcgis_server_layers)"
provides:
  - "Three GeoNB discovery tools (nb_list_geonb_services, nb_get_geonb_service_layers, nb_query_geonb_layer) standing in for the 401-ing ArcGIS Hub Search API"
  - "Four curated flood/water tools (nb_get_flood_hazard_areas, nb_get_historical_floods, nb_get_wetlands, nb_get_contaminated_sites) against live-verified GeoNB layer ids"
  - "Data-driven FILTER_REQUIRED_TOOLS guard (_require_any_filter) reusable by Plan 05's nb_get_parcels/nb_get_civic_addresses"
  - "_escape_sql_value single-quote-escaping helper for every server-built WHERE clause in this and future GeoNB plans"
affects: [21-05-crown-land-parcels, 21-06-health-education-511, 21-07-docs]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "GeoNB service-directory walk (list_arcgis_server_services + get_arcgis_server_layers, cached at CACHE_TTL_META) as the discovery substrate for any bare-ArcGIS-Server portal with no Hub Search API in front"
    - "Data-driven FILTER_REQUIRED_TOOLS guard: _require_any_filter(tool_name, *filters, layer_record_count) checked at both tool and client layers, reused across every large-layer curated fetcher rather than duplicated per function"
    - "Server-built WHERE clauses via _escape_sql_value (single-quote doubling) — only the long-tail nb_query_geonb_layer accepts a raw clause"

key-files:
  created: []
  modified:
    - src/mcp_canada/modules/new_brunswick/client.py
    - src/mcp_canada/modules/new_brunswick/tools.py
    - src/mcp_canada/modules/new_brunswick/__tests__/test_client.py
    - src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py

key-decisions:
  - "Department decoding, exclusion reasons and the curated-tool-name map live in client.py as local dicts/functions (_decode_geonb_department, _geonb_exclusion_reason, _GEONB_CURATED_TOOL_BY_SERVICE) rather than constants.py, honoring the plan's constants.py-untouched constraint across all three tasks"
  - "fetch_geonb_service_layers and fetch_geonb_layer_features validate service_name against the live (cached) service directory before proceeding, raising NotFound rather than trusting caller input to build a REST path (T-21-13)"
  - "fetch_historical_floods dispatches on event through a None|'2008'|'2018'|'1973' mapping — None/'2008'/'2018' all resolve to the shared main layer (0), '1973' resolves to the dedicated layer (8) — guarded at both tool (pre-check) and client (InvalidInput) layers per the Alberta/Saskatchewan double-guard convention"
  - "_require_any_filter is a single reusable client-layer helper keyed off constants.FILTER_REQUIRED_TOOLS rather than an inline wetlands-only check, so Plan 05's nb_get_parcels/nb_get_civic_addresses (also in FILTER_REQUIRED_TOOLS) can call it directly"

requirements-completed: [NB-07, NB-08, NB-09, NB-10, NB-11, NB-12, NB-13, ERR-01, ERR-05, ERR-06, ERR-07]

coverage:
  - id: D1
    description: "nb_list_geonb_services walks the live GeoNB REST directory (62 services), hides 5 basemaps + the retired WildlifeRefuges service by default with a non-empty exclusion_reason when included, decodes department from the GeoNB_{DEPT}_ prefix, and names each service's curated_tool"
    requirement: "NB-07"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/test_client.py#TestFetchGeonbServices, __tests__/test_tools.py#TestNbListGeonbServices"
        status: pass
      - kind: other
        ref: "live command: nb_list_geonb_services(lang='en') -> LIVE GEONB DISCOVERY OK 56 services, zero basemaps leaked"
        status: pass
    human_judgment: false
  - id: D2
    description: "nb_get_geonb_service_layers enriches each layer with its live record count and real field names, proving Crown Land's layer id is 3 (not 0), and raises NOT_FOUND naming nb_list_geonb_services for an unknown service"
    requirement: "NB-08"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/test_client.py#TestFetchGeonbServiceLayers, __tests__/test_tools.py#TestNbGetGeonbServiceLayers"
        status: pass
      - kind: other
        ref: "live command: nb_get_geonb_service_layers(service_name='GeoNB_DNR_Crown_Land') -> layer id 3 present"
        status: pass
    human_judgment: false
  - id: D3
    description: "nb_query_geonb_layer is the long-tail escape hatch keeping all 51 un-curated GeoNB services reachable, passing where straight through to ArcGIS's own SQL-92 parser (T-21-12), rejecting limit>MAX_RECORDS and unknown service_name before any feature request"
    requirement: "NB-09"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/test_client.py#TestFetchGeonbLayerFeatures, __tests__/test_tools.py#TestNbQueryGeonbLayer"
        status: pass
    human_judgment: false
  - id: D4
    description: "nb_get_flood_hazard_areas queries GeoNB_ENV_FloodHazardIndex layer 0 with a server-built, single-quote-escaped equality clause on Sheet_Numb; returns non-zero live counts"
    requirement: "NB-10"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/test_client.py#TestFetchFloodHazardAreas, __tests__/test_tools.py#TestNbGetFloodHazardAreas"
        status: pass
      - kind: other
        ref: "live command: nb_get_flood_hazard_areas(limit=50) -> LIVE FLOOD OK count 50"
        status: pass
    human_judgment: false
  - id: D5
    description: "nb_get_historical_floods dispatches 2008/2018 to the main layer (0) and 1973 to the dedicated layer (8), rejecting any other event with INVALID_INPUT at both tool and client layers before any network call"
    requirement: "NB-11"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/test_client.py#TestFetchHistoricalFloods, __tests__/test_tools.py#TestNbGetHistoricalFloods"
        status: pass
      - kind: other
        ref: "live command: nb_get_historical_floods(limit=50, lang='fr') -> LIVE FLOOD OK, _meta.lang == 'fr'"
        status: pass
    human_judgment: false
  - id: D6
    description: "nb_get_wetlands rejects an unfiltered call with INVALID_INPUT before any network request (T-21-03, 163,206-row layer), proven by a test that patches query_feature_service and asserts it was never awaited; wetland_class/status filters both build escaped server-side clauses"
    requirement: "NB-12"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py#TestNbGetWetlands::test_unfiltered_call_returns_invalid_input_without_network_call"
        status: pass
      - kind: other
        ref: "live command: nb_get_wetlands(lang='en') -> INVALID_INPUT, no network call"
        status: pass
    human_judgment: false
  - id: D7
    description: "nb_get_contaminated_sites surfaces both Status_E (English) and Status_F (French) fields regardless of which the filter matched, from GeoNB_ELG_Contaminated_Sites layer 0"
    requirement: "NB-13"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/test_client.py#TestFetchContaminatedSites::test_features_carry_bilingual_status_and_pidtype_fields"
        status: pass
      - kind: other
        ref: "live command: nb_get_contaminated_sites(limit=50) -> LIVE WATER OK 50 sites"
        status: pass
    human_judgment: false
  - id: D8
    description: "Every new tool has catch-all error coverage via @upstream_guard; constants.py, server.py, prompts.py, resources.py, test_prompts_resources.py, pyproject.toml and uv.lock are all untouched by this plan; pyright and ruff are clean; full-suite coverage holds at 97.30%"
    requirement: "ERR-01"
    verification:
      - kind: unit
        ref: "tests/test_tool_error_handling.py, tests/test_quality.py, tests/test_error_classification_defaults.py, tests/test_upstream_error_classification.py — 39 passed"
        status: pass
      - kind: other
        ref: "git diff --stat constants.py server.py prompts.py resources.py test_prompts_resources.py pyproject.toml uv.lock -> empty across all 3 task commits; uv run pytest --cov=src/mcp_canada --cov-fail-under=95 -> 97.30%"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-07-30
status: complete
---

# Phase 21 Plan 04: GeoNB Discovery + Flood/Water Summary

**Three GeoNB discovery tools replacing the 401-ing ArcGIS Hub Search API via live REST-directory enumeration, and four curated flood/water tools (flood hazard index, historical flood limits including the 1973 event, wetlands with a 163,206-row unfiltered-call guard, and bilingual contaminated sites) — every WHERE clause server-built and single-quote-escaped, every layer id traced to 21-SPIKE.md.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-07-30T16:50:00Z (approx.)
- **Completed:** 2026-07-30T17:15:25Z
- **Tasks:** 3 (all `type="auto" tdd="true"`)
- **Files modified:** 4

## Accomplishments

- **GeoNB discovery trio ships D-06 end to end:** `nb_list_geonb_services` walks the live 62-service
  REST directory (56 non-excluded services returned live), decodes the department from the
  `GeoNB_{DEPT}_` prefix, hides the 5 basemap tile services and the retired
  `GeoNB_DNR_WildlifeRefuges` placeholder by default (each carrying a non-empty
  `exclusion_reason` when `include_excluded=True`), and names each service's curated tool.
  `nb_get_geonb_service_layers` enriches every layer with its live record count and real field
  names — a fan-out of `get_count`/`get_layer_metadata` per layer, cached at `CACHE_TTL_META` and
  serialized by the GeoNB limiter (T-21-14) — and the live run confirmed Crown Land's layer id is
  3, exactly as the Wave 0 tracer proved. `nb_query_geonb_layer` is the long-tail escape hatch: its
  `where` argument reaches ArcGIS's own SQL-92 parser directly (T-21-12), documented as the trust
  boundary in the docstring, matching every prior ArcGIS-backed province.
- **Flood — New Brunswick's signature domain:** `nb_get_flood_hazard_areas` queries
  `GeoNB_ENV_FloodHazardIndex` layer 0 with a server-built, single-quote-escaped equality clause on
  `Sheet_Numb`. `nb_get_historical_floods` dispatches `event` through a `None|"2008"|"2018"|"1973"`
  mapping — the first three share the main layer (0, "2008 and 2018 Flood Limits"), `"1973"`
  resolves to the dedicated layer (8) — with `InvalidInput` raised at both the tool's own pre-check
  and the client as a second line of defence (the Alberta/Saskatchewan double-guard). Both tools
  returned non-zero live counts.
- **Wetlands guard proven not-awaited:** `nb_get_wetlands` rejects a call with neither
  `wetland_class` nor `status` with `INVALID_INPUT` **before any network request** — enforced by a
  new reusable `_require_any_filter(tool_name, *filters, layer_record_count)` client helper keyed
  off `constants.FILTER_REQUIRED_TOOLS` (data-driven rather than a hardcoded per-function
  condition), and a dedicated test patches `arcgis_hub.query_feature_service` and asserts
  `assert_not_awaited()`. The live run confirmed the guard fires exactly as designed
  (`GeoNB_ENV_Wetlands` layer 2 holds 163,206 rows).
- **Contaminated sites, bilingual by default:** `nb_get_contaminated_sites` always returns both
  `Status_E` and `Status_F` from `GeoNB_ELG_Contaminated_Sites` layer 0, regardless of which field
  the `status` filter matched against — live count 50 (capped by `limit`).
- **Every layer id traced to 21-SPIKE.md, never guessed:** `FLOOD_HAZARD_LAYER=0`,
  `HISTORICAL_FLOODS_LAYER=0` / `HISTORICAL_FLOODS_1973_LAYER=8`, `WETLANDS_LAYER=2`,
  `CONTAMINATED_SITES_LAYER=0` — all CONFIRMED live in 21-SPIKE.md section 2, all consumed from the
  locked `constants.py` constants, never inlined (`grep -n "layer_id=0\b" client.py` returns no
  lines).

## Task Commits

Each task was committed atomically:

1. **Task 1: GeoNB discovery — 3 tools standing in for the unavailable Hub Search API** -
   `5c7e718` (feat)
2. **Task 2: Flood — hazard index and historical flood limits** - `fa8ad43` (feat)
3. **Task 3: Water — wetlands (filter-required, 163K rows) and contaminated sites** - `9adaaf8`
   (feat)

**Plan metadata:** (this commit, immediately following)

## Files Created/Modified

- `src/mcp_canada/modules/new_brunswick/client.py` - 7 functions implemented
  (`fetch_geonb_services`, `fetch_geonb_service_layers`, `fetch_geonb_layer_features`,
  `fetch_flood_hazard_areas`, `fetch_historical_floods`, `fetch_wetlands`,
  `fetch_contaminated_sites`); new private helpers `_decode_geonb_department`,
  `_geonb_exclusion_reason`, `_escape_sql_value`, `_require_any_filter`,
  `_GEONB_CURATED_TOOL_BY_SERVICE`, `_GEONB_NAMED_EXCLUSION_REASONS`,
  `_HISTORICAL_FLOOD_LAYERS_BY_EVENT`, `_HISTORICAL_FLOOD_FIELDS_BY_LAYER`
- `src/mcp_canada/modules/new_brunswick/tools.py` - 7 tools added (`nb_list_geonb_services`,
  `nb_get_geonb_service_layers`, `nb_query_geonb_layer`, `nb_get_flood_hazard_areas`,
  `nb_get_historical_floods`, `nb_get_wetlands`, `nb_get_contaminated_sites`); `__all__` and
  imports extended
- `src/mcp_canada/modules/new_brunswick/__tests__/test_client.py` - one real test class per
  function above, plus `TestGeonbHelpers` covering the private helpers directly (was:
  placeholders)
- `src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py` - one real test class per tool
  above, including the not-awaited wetlands guard test and the double-guard second-line-of-defence
  tests for historical floods and wetlands (was: placeholders)

## Decisions Made

- Kept department decoding, exclusion reasons and the curated-tool-name map as local
  dicts/functions in `client.py` rather than adding them to `constants.py`, since every task's
  acceptance criteria require `git diff --stat constants.py` to stay empty.
- `fetch_geonb_service_layers` and `fetch_geonb_layer_features` both validate `service_name`
  against the live (cached) service directory before building any REST path, raising `NotFound`
  rather than trusting a caller-supplied service name (T-21-13 mitigation, applied consistently to
  both consumers of the pattern rather than just one).
- `_require_any_filter` was designed as a single, generic, reusable helper (not a wetlands-only
  inline check) so Plan 05's `nb_get_parcels`/`nb_get_civic_addresses` — also registered in
  `FILTER_REQUIRED_TOOLS` — can call it directly without duplicating the guard logic.

## Deviations from Plan

None — plan executed exactly as written. All layer ids came from `21-SPIKE.md`/`constants.py`;
`constants.py`, `server.py`, `prompts.py`, `resources.py`, `test_prompts_resources.py`,
`pyproject.toml` and `uv.lock` were never touched.

## Issues Encountered

- `gsd_run query requirements.mark-complete NB-07..NB-13` reported all seven as `not_found` — none
  of the Phase 21 `NB-XX` requirement IDs are registered in `.planning/REQUIREMENTS.md` (only
  `ERR-*` are, and those were already marked complete by prior phases). This is a pre-existing gap
  in this project's requirements tracking predating this plan (Phase 21's requirements live in the
  phase's own PLAN.md frontmatter, not in the global REQUIREMENTS.md traceability table) — not
  something this plan's execution caused or can fix within its file-scope boundary. Documented here
  so it doesn't silently look like a missed step.

## User Setup Required

None — GeoNB is a keyless, publicly reachable ArcGIS Server; no external service configuration
required for this plan.

## Next Phase Readiness

- Plan 05 (parcels/civic address) can call the now-shipped `_require_any_filter` client helper
  directly for `nb_get_parcels`/`nb_get_civic_addresses` — both already registered in
  `constants.FILTER_REQUIRED_TOOLS`.
- `_escape_sql_value` is available in `client.py` for any future server-built WHERE clause on a
  GeoNB layer.
- `constants.ALL_NB_TOOL_NAMES` (22 entries) and `tools.ALL_NB_TOOLS` remain set-equal — verified
  live (`MANIFEST OK 22`).
- No blockers.

---
*Phase: 21-new-brunswick-government-open-data*
*Completed: 2026-07-30*

## Self-Check: PASSED

All 5 claimed files verified present on disk. All 3 claimed commit hashes verified present in
git log (`5c7e718`, `fa8ad43`, `9adaaf8`).
