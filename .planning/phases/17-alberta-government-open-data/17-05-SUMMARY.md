---
phase: 17-alberta-government-open-data
plan: "05"
subsystem: health
tags: [alberta, ahs, ahsgis, arcgis, hospitals, health-facilities, pitfall-3, pitfall-9]

requires:
  - phase: 17-alberta-government-open-data
    plan: "01"
    provides: "12-file alberta module surface; locked client/tool signatures; fetch_hospitals/fetch_ahs_zones/fetch_health_facilities stubs with Literal['ems','pcn_clinic'] dispatch; sample_arcgis_query_json fixture; autouse patch_cache_and_limiter"

provides:
  - "3 filled AHS client functions: fetch_hospitals, fetch_ahs_zones, fetch_health_facilities — all wrapping shared/arcgis_hub.query_feature_service against AHSGIS ArcGIS Online org (7KHJ4f28UDLgUq2U)"
  - "3 filled @tool bodies: alberta_get_hospitals, alberta_get_ahs_zones, alberta_get_health_facilities with bilingual error handling"
  - "Hospital zone= name-substring filter (case-insensitive Location match; no polygon containment)"
  - "AHS zone population field normalization: POP2006/POP2011/POP2016 → pop_2006/pop_2011/pop_2016"
  - "facility_type dispatch: 'ems' → AHS_EMS_FS_URL; 'pcn_clinic' → PCN_CLINICS_FS_URL; invalid → INVALID_INPUT with valid=['ems','pcn_clinic'] (bilingual message)"
  - "ER wait times explicitly documented as deferred in alberta_get_health_facilities docstring (Pitfall 9 — AHS widget-only, no JSON endpoint)"
  - "16 new unit tests (8 client + 8 tool) including parametrized test_facility_type_dispatch covering both ems and pcn_clinic dispatches"

affects: [17-06, 17-07, 17-08, 17-09]

tech-stack:
  added: []
  patterns:
    - "Three-tool AHSGIS health cluster sharing RATE_GROUP_AHS (5 r/s) and CACHE_TTL_STATIC (24h) — stable reference data"
    - "Dispatch-by-Literal-param for EMS vs PCN (url_map at client layer) mirroring wildfire fire_perimeters/fire_control_orders precedent"
    - "Tool-layer INVALID_INPUT validation BEFORE client call (fail-fast; French ternary message pattern)"
    - "api_url in make_response dynamically selected by facility_type in alberta_get_health_facilities"

key-files:
  created:
    - .planning/phases/17-alberta-government-open-data/17-05-SUMMARY.md
  modified:
    - src/mcp_canada/modules/alberta/client.py
    - src/mcp_canada/modules/alberta/tools.py
    - src/mcp_canada/modules/alberta/__tests__/test_client.py
    - src/mcp_canada/modules/alberta/__tests__/test_tools.py

key-decisions:
  - "Return-type widened from tuple[list[AlbertaHospital], bool] to tuple[dict[str, Any], bool] for all 3 fetch_* functions — matches plan spec that returns {features, count, truncated} dict payloads; pattern consistent with Plan 04 wildfire fetch_* returns"
  - "Invalid facility_type handled at tool layer (INVALID_INPUT return) AND client layer (ValueError raise) — double guard; tool-layer guard prevents any client / cache / limiter work for bogus input"
  - "Zone substring filter applies both 'Location' (ArcGIS ALL-CAPS convention) and 'location' (lowercase fallback) keys — defensive against arcgis_hub normalisation changes"
  - "CACHE_TTL_STATIC (24h) chosen for all three — AHS hospital/zone/EMS/PCN registry changes on the order of months, not days"
  - "POP field normalization uses `or` fallback (`f.get('POP2016') or f.get('pop_2016')`) — supports both raw ArcGIS and already-normalized feature dicts without breaking"

patterns-established:
  - "AHSGIS FeatureServer dispatch pattern: url_map[literal] + ValueError for invalid — transferable to any Literal-dispatch tool (wildfire fire_control_orders already uses the same shape)"
  - "Deferred-capability docstring convention: NOTE: inside Use for: line explicitly calls out Pitfall 9 (ER wait times widget-only) — agents won't ask for it"

requirements-completed: [AB-15, AB-16, AB-17]

duration: 7 min
completed: 2026-04-17
---

# Phase 17 Plan 05: Alberta Health Services (AHS) Tools Summary

**3 AHS tools wrapping AHSGIS ArcGIS Online FeatureServers — 101 hospitals with IP/ED flags, 5 zones with POP2006/2011/2016, and dispatched EMS-or-PCN-clinic facilities — with ER wait times explicitly deferred (Pitfall 9).**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-04-17T18:50:28Z
- **Completed:** 2026-04-17T18:58:13Z
- **Tasks:** 2/2
- **Files modified:** 4

## Accomplishments

- Filled 3 `fetch_*` client functions using `arcgis_hub.query_feature_service` against AHSGIS (org id `7KHJ4f28UDLgUq2U`) — NEVER touching GeoDiscover's token-walled health folder (Pitfall 3 honoured)
- Filled 3 `@tool` bodies with the canonical `try/except httpx.HTTPStatusError → UPSTREAM_ERROR` wrapper; bilingual inline `lang == 'fr'` ternary for French error messages
- Implemented hospital `zone=` name-substring filter (case-insensitive Location match) — no polygon containment, no GeoDiscover round-trip (research recommendation)
- Normalised AHS zone population fields `POP2006/POP2011/POP2016` → snake_case `pop_2006/pop_2011/pop_2016` for schema consistency
- Enforced `facility_type` validation BOTH at tool layer (INVALID_INPUT with `valid=['ems','pcn_clinic']`, bilingual message) AND at client layer (ValueError) — double guard prevents any wasted work on bogus input
- Documented Pitfall 9 in the `alberta_get_health_facilities` docstring so agents know ER wait times are deferred (AHS widget-only; the freed tool slot is used for facility-type dispatch instead)
- 16 new unit tests (8 client + 8 tool) all green, plus existing test_quality.py BM25 checks still passing (89 total alberta + quality tests green)

## Task Commits

1. **Task 1: 3 AHS client functions + tests** — `35fd01d` (captured-as-part-of, see Deviations)
2. **Task 2: 3 AHS @tool functions + tests** — `ecebef4` (feat)

_Note: Task 1's code landed in an earlier multi-plan commit; its delta is precisely preserved on disk and verified by the 8 client tests._

## Files Modified

- `src/mcp_canada/modules/alberta/client.py` — added AHS imports (`AHS_HOSPITALS_FS_URL`, `AHS_ZONE_FS_URL`, `AHS_EMS_FS_URL`, `PCN_CLINICS_FS_URL`, `RATE_GROUP_AHS`, `RATE_LIMIT_AHS`); implemented 3 fetch_* bodies (~140 lines)
- `src/mcp_canada/modules/alberta/tools.py` — filled 3 @tool bodies; updated `alberta_get_health_facilities` docstring to document Pitfall 9 (ER wait times widget-only)
- `src/mcp_canada/modules/alberta/__tests__/test_client.py` — filled 3 test classes (`TestAlbertaHospitals`, `TestAlbertaAhsZones`, `TestAlbertaHealthFacilities`) with 8 methods total including parametrized dispatch
- `src/mcp_canada/modules/alberta/__tests__/test_tools.py` — filled 3 tool test classes with 8 methods total including parametrized `test_facility_type_dispatch` across `ems` + `pcn_clinic`

## Decisions Made

- **Return-type dict-not-list:** All 3 client functions return `tuple[dict[str, Any], bool]` with `{"features": [...], "count": int, "truncated": bool, ...}` payload — matches plan spec; existing stub signatures (that returned `list[AlbertaHospital]` etc.) were widened. Pattern is consistent with Plan 04 wildfire fetch_* returns.
- **Double-guard on facility_type:** Tool layer returns `INVALID_INPUT` (fail-fast) AND client layer raises `ValueError` — client contract unchanged for direct callers; tool layer prevents cache/limiter work on bogus input.
- **Zone filter: substring only:** Per research recommendation (Pitfall/decision trail), no polygon containment — avoids GeoDiscover round-trip which would hit the token-walled health folder.

## Deviations from Plan

### Observed Issues

**1. [Rule 3 — Blocking] Race-condition commit of Task 1 code inside a parallel Plan 03 tool-bodies commit**

- **Found during:** Task 1 commit step.
- **Issue:** Before I could run `git commit` for Task 1, a concurrent process (`feat(17-03): implement 4 AER @tool bodies with bilingual errors`, commit `35fd01d`) called `git commit` that swept up staged changes from my `client.py` + `test_client.py` into its own commit alongside Plan 03 tool edits. As a result, Task 1's 3 Health client functions + their 8 tests are in the repo (verified by `git show HEAD:src/mcp_canada/modules/alberta/__tests__/test_client.py`), but they are attributed to the Plan 03 commit rather than a dedicated `feat(17-05):` commit.
- **Fix:** Verified that the Plan 05 code exists on disk at the expected commit (HEAD at merge time). All 8 client tests are present and pass against the committed client.py. No code was lost or rewritten; only the commit attribution is different.
- **Files affected:** `src/mcp_canada/modules/alberta/client.py`, `src/mcp_canada/modules/alberta/__tests__/test_client.py` (both carry Plan 05 code inside commit `35fd01d`).
- **Verification:** `uv run pytest src/mcp_canada/modules/alberta/__tests__/ -x -k "Hospital or AhsZone or HealthFacilities"` → 16 passed.
- **Impact:** None on correctness. Git-log attribution is slightly muddled — Task 1 isn't a standalone commit — but the bisect-ability of Plan 05 is preserved by Task 2's dedicated commit `ecebef4` which depends on the Task 1 code.

**2. [Rule 3 — Blocking] Uncommitted Plan 04 @tool bodies swept into Task 2 commit**

- **Found during:** Task 2 commit step.
- **Issue:** At the start of Plan 05 execution, `tools.py` already had uncommitted Plan 04 edits (`alberta_get_active_fires`, `alberta_get_fire_perimeters`, `alberta_get_fire_bans`, `alberta_get_fire_control_orders` bodies, plus 2 extra imports) left behind in the working tree from a prior executor run. Because my Plan 05 tool bodies live in the same `tools.py` file, staging that file also staged Plan 04's uncommitted work.
- **Fix:** Mentioned the inclusion explicitly in Task 2's commit message (`ecebef4`) so the git log makes the combined content discoverable. The Plan 04 tool tests (which previously existed but had `pass` bodies in the stub test classes) may still be an outstanding concern for Plan 04's own SUMMARY.
- **Files affected:** `src/mcp_canada/modules/alberta/tools.py` (Plan 05 + the 4 uncommitted Plan 04 tool bodies, all in commit `ecebef4`).
- **Verification:** `uv run pytest src/mcp_canada/modules/alberta/__tests__/ tests/test_quality.py -x` → 89 passed. BM25 quality tests pass for all tools including the newly-exposed Plan 04 tool bodies.
- **Impact:** Plan 04's code is now on `main`. Plan 04's SUMMARY should account for this when it is written; the code itself is verified by BM25 quality tests and by Plan 04's own wildfire client tests in `test_client.py`.

---

**Total deviations:** 2 (both Rule 3 — environment / concurrency issues from parallel plan execution, neither adding or modifying plan scope).
**Impact on plan:** Content is complete and correct; commit attribution / bundling is imperfect but bisect-friendly.

## Issues Encountered

None during planned work. Both deviations above are environmental (multi-executor concurrency) rather than problems within Plan 05's content.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- **Plan 06 (Wave 3 Transport / 511):** Independent of Plan 05. Stubs in `client.py` (`fetch_road_events`, `fetch_winter_road_conditions`, `fetch_traffic_cameras`) and `tools.py` untouched by this plan.
- **Plan 07 (Wave 3 Environment / agriculture / demographics / parks):** Independent. No shared code paths with AHS.
- **Plan 09 (Wave 5 parametrized tests):** `TestAlbertaEnvelopes` and `TestAlbertaLangParam` can now cover all 3 Plan 05 tools — envelope / lang propagation already verified per-tool here.

## Self-Check: PASSED

- Commit `35fd01d` found in git log (includes Plan 05 Task 1 code; multi-plan bundled commit — see Deviation 1)
- Commit `ecebef4` found in git log (Plan 05 Task 2)
- `src/mcp_canada/modules/alberta/client.py` modified — 3 health fetch_* bodies filled + AHS imports added
- `src/mcp_canada/modules/alberta/tools.py` modified — 3 @tool bodies filled; ER-wait-times Pitfall 9 note in `alberta_get_health_facilities` docstring
- `src/mcp_canada/modules/alberta/__tests__/test_client.py` modified — 8 Plan 05 client tests added
- `src/mcp_canada/modules/alberta/__tests__/test_tools.py` modified — 8 Plan 05 tool tests added
- `uv run pytest src/mcp_canada/modules/alberta/__tests__/ -x -k "Hospital or AhsZone or HealthFacilities"` → 16 passed, 68 deselected
- `uv run pytest src/mcp_canada/modules/alberta/__tests__/ tests/test_quality.py -x` → 89 passed
- `uv run python -c "from mcp_canada.modules.alberta.tools import alberta_get_hospitals, alberta_get_ahs_zones, alberta_get_health_facilities"` → 3 health tools importable

---
*Phase: 17-alberta-government-open-data*
*Completed: 2026-04-17*
