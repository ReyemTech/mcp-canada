---
phase: 21-new-brunswick-government-open-data
plan: 01
subsystem: api
tags: [arcgis-server, ckan, socrata, geonb, new-brunswick, mcp-tools]

# Dependency graph
requires:
  - phase: 20-nova-scotia-government-open-data
    provides: shared/socrata.py (Socrata SODA API client), reused verbatim for gnb.socrata.com
provides:
  - shared/arcgis_hub.py list_arcgis_server_services + get_arcgis_server_layers (bare ArcGIS Server directory enumeration, D-06)
  - new_brunswick module scaffold — 7 files + 4 test files, locked 22-tool manifest, locked client signatures
  - nb_get_crown_land — live-verified, working end-to-end through GeoNB ArcGIS Server
  - 21-SPIKE.md — live 62-service GeoNB directory + 11/11 CONFIRMED curated layer ids
affects: [21-02-federal-ckan-discovery, 21-03-prompts-resources, 21-04-flood-water, 21-05-crown-land-parcels, 21-06-health-education-511, 21-07-docs]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "ArcGIS Server (bare MapServer) service-directory enumeration, standing in for the Hub Search API on portals with no Hub in front (GeoNB precedent for any future bare-ArcGIS-Server province)"
    - "Four-surface discovery module: federal CKAN + provincial Socrata + GeoNB ArcGIS Server + key-gated 511, each with its own rate-limiter group"

key-files:
  created:
    - src/mcp_canada/modules/new_brunswick/__init__.py
    - src/mcp_canada/modules/new_brunswick/constants.py
    - src/mcp_canada/modules/new_brunswick/schemas.py
    - src/mcp_canada/modules/new_brunswick/client.py
    - src/mcp_canada/modules/new_brunswick/tools.py
    - src/mcp_canada/modules/new_brunswick/prompts.py
    - src/mcp_canada/modules/new_brunswick/resources.py
    - src/mcp_canada/modules/new_brunswick/__tests__/conftest.py
    - src/mcp_canada/modules/new_brunswick/__tests__/test_client.py
    - src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py
    - src/mcp_canada/modules/new_brunswick/__tests__/test_prompts_resources.py
    - .planning/phases/21-new-brunswick-government-open-data/21-SPIKE.md
  modified:
    - src/mcp_canada/shared/arcgis_hub.py
    - src/mcp_canada/shared/__tests__/test_arcgis_hub.py

key-decisions:
  - "Checkpoint (Task 2, blocking): option-a selected — gnb.socrata.com (312 datasets, keyless, live-verified) joins the discovery surface via two new nb_ tools reusing shared/socrata.py verbatim; D-01's federal-CKAN discovery stays locked and untouched"
  - "To hold the tool budget at 22 (D-08's 18-22 band) after adding the two Socrata tools, nb_get_provincial_parks and nb_get_mineral_occurrences drop to the long tail — both remain reachable via nb_query_geonb_layer (Plan 04)"
  - "All 11 curated GeoNB layer ids in 21-RESEARCH.md's Code Examples table are live-CONFIRMED in 21-SPIKE.md — zero corrections needed to constants.py"
  - "Added a fourth module-level rate limiter (_socrata_limiter) beyond the plan's original three — gnb.socrata.com is a fourth upstream surface introduced by the checkpoint decision, and CLAUDE.md forbids skipping rate limiting on any upstream surface (Rule 2)"

requirements-completed: [NB-06, NB-14, NB-24, NB-25, ERR-01, ERR-05, ERR-06, ERR-07]

coverage:
  - id: D1
    description: "nb_get_crown_land returns live GeoNB Crown Land rows in a _meta envelope, proving D-05 end to end through constants -> client -> @tool -> FileSystemProvider, using layer 3"
    requirement: "NB-06"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py#TestNbGetCrownLandTools"
        status: pass
      - kind: other
        ref: "live command: uv run python -c \"...nb_get_crown_land(lang='en', limit=25)...\" -> TRACER LIVE OK 25 rows"
        status: pass
    human_judgment: false
  - id: D2
    description: "shared/arcgis_hub.py gains list_arcgis_server_services + get_arcgis_server_layers (D-06), both decoding via decode_json, both pinned by outgoing-param contract tests, existing 5 functions untouched"
    requirement: "ERR-05"
    verification:
      - kind: unit
        ref: "src/mcp_canada/shared/__tests__/test_arcgis_hub.py#TestListArcgisServerServices"
        status: pass
      - kind: unit
        ref: "src/mcp_canada/shared/__tests__/test_arcgis_hub.py#TestGetArcgisServerLayers"
        status: pass
    human_judgment: false
  - id: D3
    description: "21-SPIKE.md live-verifies the 62-service GeoNB directory and re-verifies all 11 curated layer ids from 21-RESEARCH.md against live {service}/MapServer?f=json — 11/11 CONFIRMED"
    requirement: "NB-24"
    verification:
      - kind: other
        ref: ".planning/phases/21-new-brunswick-government-open-data/21-SPIKE.md (all sections populated from a live probe run, 2026-07-30)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The Task 2 blocking checkpoint (gnb.socrata.com discovery) is resolved and its outcome (option-a) is reflected in constants.py's docstring, ALL_NB_TOOL_NAMES, and client.py's stub set"
    requirement: "NB-25"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py#TestAllNbToolNamesManifest"
        status: pass
    human_judgment: false
  - id: D5
    description: "Full contract surface locked: 22-name manifest, ~20 flat schema models, 4 limiters, 5 fully-implemented private helpers, 21 NotImplementedError client stubs with locked signatures, prompts.py/resources.py import-only, all test scaffolds collect, pyright/ruff clean, no new dependency, server.py untouched"
    requirement: "NB-14"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/ (43 tests, all pass)"
        status: pass
      - kind: other
        ref: "uv run pyright src/mcp_canada/modules/new_brunswick/ src/mcp_canada/shared/arcgis_hub.py -> 0 errors"
        status: pass
      - kind: other
        ref: "uv run ruff check src/ tests/ -> All checks passed"
        status: pass
    human_judgment: false

duration: 24min
completed: 2026-07-30
status: complete
---

# Phase 21 Plan 01: New Brunswick Wave 0 Scaffold + GeoNB Directory Enumerator Summary

**Live-verified `nb_get_crown_land` proving D-05 end to end, a new bare-ArcGIS-Server directory
enumerator (`list_arcgis_server_services`/`get_arcgis_server_layers`) standing in for GeoNB's
unusable Hub Search API, an 11/11-CONFIRMED live layer-id re-verification in 21-SPIKE.md, and a
full `new_brunswick` module scaffold whose locked 22-tool manifest now includes two
`gnb.socrata.com` discovery tools per the Task 2 checkpoint decision (option-a).**

## Performance

- **Duration:** ~24 min (Task 1 tracer 15:38 → Task 4 scaffold complete 16:02)
- **Started:** 2026-07-30T15:38:32Z
- **Completed:** 2026-07-30T16:02:04Z
- **Tasks:** 4 (1 tracer, 1 blocking checkpoint, 2 auto — one TDD)
- **Files modified:** 15 (13 created, 2 modified)

## Accomplishments

- **Tracer proven live:** `nb_get_crown_land` returns real GeoNB Crown Land rows (layer 3, never
  layer 0) through `constants.py` → `client.py` → `@tool` → FileSystemProvider auto-registration,
  confirming D-05 — `shared/arcgis_hub.py:query_feature_service` works unchanged against a bare
  ArcGIS Server MapServer.
- **New shared capability:** `shared/arcgis_hub.py` gains exactly two additive functions
  (`list_arcgis_server_services`, `get_arcgis_server_layers`), both decoding via `decode_json`
  (ERR-05) and pinned by outgoing-param contract tests (the Manitoba/Saskatchewan lesson) — the
  five existing functions are untouched apart from the docstring's public-function list.
- **Blocking checkpoint resolved:** the user selected option-a — `gnb.socrata.com` (312 datasets,
  keyless, live-verified at plan time) joins the discovery surface via two new `nb_` tools reusing
  `shared/socrata.py` verbatim, while D-01's federal-CKAN discovery stays locked.
- **Live layer-id re-verification:** `21-SPIKE.md` re-ran the new enumerator plus
  `get_layer_metadata`/`get_count` against all 11 curated services from 21-RESEARCH.md's Code
  Examples table — **11/11 CONFIRMED**, zero corrections needed. `GeoNB_DNR_WildlifeRefuges`
  reconfirmed as the retired 1-record placeholder.
- **Full scaffold locked:** 22-name tool manifest, ~20 flat Pydantic schemas, 4 rate-limiter
  groups, 5 fully-implemented private helpers, 21 `NotImplementedError` client stubs with LOCKED
  signatures for Plans 02-06, import-only `prompts.py`/`resources.py` skeletons for Plan 03.

## Task Commits

Each task was committed atomically:

1. **Task 1: TRACER — end-to-end "retrieve NB Crown Land parcels"** - `95fd2ba` (feat) — completed
   in the prior session before this checkpoint resume.
2. **Task 2: Blocking decision — gnb.socrata.com discovery surface** - checkpoint, no commit;
   resolved via user response (option-a) at the top of this resume.
3. **Task 3: Extend shared/arcgis_hub.py (TDD) + live 21-SPIKE.md:**
   - `a206b9d` (test) — RED: failing tests for `list_arcgis_server_services` /
     `get_arcgis_server_layers`
   - `978aae1` (feat) — GREEN: implemented both functions, additive only
   - `52ce8b0` (docs) — live probe run, 21-SPIKE.md written with 11/11 CONFIRMED verdicts
4. **Task 4: Expand the scaffold** - `625f128` (feat) — full constants/schemas/client/test surface,
   checkpoint option-a applied to the manifest

**Plan metadata:** (this commit, immediately following)

## Files Created/Modified

- `src/mcp_canada/shared/arcgis_hub.py` - +2 functions: `list_arcgis_server_services`,
  `get_arcgis_server_layers` (additive, existing 5 functions byte-identical apart from docstring)
- `src/mcp_canada/shared/__tests__/test_arcgis_hub.py` - +18 tests across
  `TestListArcgisServerServices` / `TestGetArcgisServerLayers`, outgoing-param assertions
- `src/mcp_canada/modules/new_brunswick/constants.py` - federal CKAN + gnb.socrata.com + 11
  live-verified GeoNB service/layer constants + 511 + cache TTLs + locked 22-name
  `ALL_NB_TOOL_NAMES`
- `src/mcp_canada/modules/new_brunswick/schemas.py` - 20 flat Pydantic v2 models using exact live
  GeoNB field names from 21-SPIKE.md §4
- `src/mcp_canada/modules/new_brunswick/client.py` - 4 limiters, 5 implemented private helpers
  (`_api_get`, `_build_fq`, `_shape_dataset`, `_geonb_query`, `_511_get`), `fetch_crown_land`
  (implemented), 21 locked-signature `NotImplementedError` stubs
- `src/mcp_canada/modules/new_brunswick/tools.py` - `nb_get_crown_land` (tracer, unchanged by
  Task 4)
- `src/mcp_canada/modules/new_brunswick/prompts.py` / `resources.py` - import-only skeletons
- `src/mcp_canada/modules/new_brunswick/__tests__/conftest.py` - fixtures for federal CKAN
  (bilingual + gnb.socrata.com resource url + FR/EN pair), gnb.socrata.com catalog/rows, GeoNB
  service-directory/MapServer-layer, per-curated-layer GeoJSON (exact SPIKE field names), empty
  FeatureCollection, and 511 event samples
- `src/mcp_canada/modules/new_brunswick/__tests__/test_client.py` - new; real tests for the 5
  private helpers + `fetch_crown_land`, placeholder classes for every remaining `fetch_*` stub,
  `NotImplementedError` contract tests
- `src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py` - extended: manifest tests
  (22 entries, checkpoint tools in/out, `nb_` prefix), placeholder classes per remaining tool
- `src/mcp_canada/modules/new_brunswick/__tests__/test_prompts_resources.py` - new; import checks
  + placeholder classes for Plan 03
- `.planning/phases/21-new-brunswick-government-open-data/21-SPIKE.md` - live 62-service directory
  dump + 11/11 CONFIRMED layer-id verdicts + field-name capture

## Decisions Made

- **Checkpoint option-a** (blocking, Task 2): `gnb.socrata.com` joins discovery as two new `nb_`
  tools (`nb_search_gnb_socrata_datasets`, `nb_query_gnb_socrata_dataset`); D-01's federal-CKAN
  discovery is untouched.
- **Manifest tradeoff**: `nb_get_provincial_parks` and `nb_get_mineral_occurrences` drop to the
  long tail (reachable via `nb_query_geonb_layer`) to hold the 22-tool budget inside D-08's 18-22
  band — this is the mechanism 21-05-PLAN.md was written to expect.
- **Fourth rate-limiter group added** (`_socrata_limiter`, `RATE_GROUP_SOCRATA`): the checkpoint
  turned this into a 4-surface module (federal CKAN + gnb.socrata.com + GeoNB + 511), and every
  upstream surface must be rate-limited per CLAUDE.md — not adding one would have been Rule 2
  (missing critical functionality).
- **All 11 curated GeoNB layer ids CONFIRMED live** — no `constants.py` correction was needed,
  simplifying the constants file relative to what a REVISED-id branch would have required.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `prompts.py`'s planned import path does not exist**
- **Found during:** Task 4 (`uv run pyright` verification step)
- **Issue:** The plan's action text specified
  `from fastmcp.prompts.prompt import Message`, but `fastmcp.prompts.prompt` is not an importable
  submodule — pyright reported `reportMissingImports`. Every other shipped module (verified against
  `nova_scotia/prompts.py`) imports `Message` from `fastmcp.prompts` directly.
- **Fix:** Changed to `from fastmcp.prompts import Message, prompt`, matching the working
  convention used across every prior province module.
- **Files modified:** `src/mcp_canada/modules/new_brunswick/prompts.py`
- **Verification:** `uv run pyright src/mcp_canada/modules/new_brunswick/` → 0 errors
- **Committed in:** `625f128` (Task 4 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix — corrected import path)
**Impact on plan:** No scope creep; the fix aligns the new module with the codebase's existing,
working convention.

## Issues Encountered

- **False-positive `@mcp\.` grep hit** (not a real issue): the Task 4 acceptance criteria grep
  `grep -rn "@mcp\." src/mcp_canada/modules/new_brunswick/` matches a line inside `tools.py`'s
  module docstring — `"Uses standalone @tool from fastmcp.tools (NEVER @mcp.tool)"` — which
  documents what NOT to do, not an actual `@mcp.tool` decorator usage. Verified this exact pattern
  is present verbatim in `manitoba/tools.py`, `saskatchewan/tools.py`, and `nova_scotia/tools.py`
  (all shipped, reviewed modules), so this is expected and not a deviation requiring a fix.

## User Setup Required

None - no external service configuration required for this plan. `NEW_BRUNSWICK_511_KEY` is only
needed when Plan 06 implements the 511 tools; the `Five11NotConfigured` path (`NOT_CONFIGURED`
envelope) is the expected default behavior with no key set.

## Next Phase Readiness

- `constants.py`, `schemas.py`, and `client.py`'s locked signatures are ready for Plans 02-06 to
  fill bodies without touching each other's territory.
- Plan 02 must implement `fetch_search_datasets`/`fetch_dataset_details`/`fetch_query_dataset`/
  `fetch_organizations`/`fetch_categories` (federal CKAN) AND the two new
  `fetch_gnb_socrata_search`/`fetch_gnb_socrata_query` stubs (checkpoint option-a) — both surfaces
  are now Plan 02's responsibility per the updated manifest.
- Plan 05's expectation that `constants.ALL_NB_TOOL_NAMES` omits `nb_get_mineral_occurrences`/
  `nb_get_provincial_parks` when the checkpoint drops them is now satisfied — no further action
  needed there.
- No blockers. `21-SPIKE.md`'s 11/11 CONFIRMED layer ids mean Plans 04-06 can implement directly
  against the constants in this plan without re-verifying layer ids themselves.

---
*Phase: 21-new-brunswick-government-open-data*
*Completed: 2026-07-30*
