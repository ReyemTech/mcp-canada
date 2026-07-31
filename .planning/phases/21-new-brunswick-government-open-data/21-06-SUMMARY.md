---
phase: 21-new-brunswick-government-open-data
plan: 06
subsystem: api
tags: [arcgis-server, geonb, new-brunswick, health, education, transport-511, dispatch-tools, manifest-integrity]

# Dependency graph
requires:
  - phase: 21-new-brunswick-government-open-data
    provides: "Plan 01's live-verified 21-SPIKE.md layer ids, the Five11NotConfigured/_511_get Wave 0 helpers, HEALTH_FACILITY_LAYERS/SCHOOL_SECTOR_LAYERS constant maps, and Plan 05's _upper_contains_clause / _geonb_query shared helpers"
provides:
  - "nb_get_health_facilities — dispatches New Brunswick's 6 GeoNB_Health_Facilities layers (hospital_horizon, hospital_vitalite, after_hours_clinic, adult_residential_centre, nursing_home, pharmacy) by a locked constant map, with a per-layer name-field dispatch (_HEALTH_FACILITY_NAME_FIELD) discovered by this plan's own live field-schema probe"
  - "nb_get_public_schools — dispatches GeoNB_EECD_PublicSchools' anglophone/francophone layers, district= filtering on strDST with live-verified short codes"
  - "nb_get_road_events, nb_get_winter_road_conditions, nb_get_traffic_cameras — three key-gated NB 511 transport tools returning a bilingual NOT_CONFIGURED envelope (never an exception) when NEW_BRUNSWICK_511_KEY is absent, mirroring Manitoba's Five11NotConfigured pattern exactly"
  - "TestManifestMatchesShippedSurface — a genuine, falsifiable bidirectional set-equality test between constants.ALL_NB_TOOL_NAMES and the @tool objects actually registered in tools.py (orchestrator-directed addition, not in the original plan text)"
  - "The completed 22-tool New Brunswick manifest — every name in ALL_NB_TOOL_NAMES now resolves to a real, registered tool"
affects: [21-07-docs]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "_HEALTH_FACILITY_NAME_FIELD — a per-facility-type dispatch map (client.py) selecting the correct live-verified name field for a containment filter, because GeoNB_Health_Facilities' 6 layers do NOT share one field schema (hospitals use Name_E; after-hours clinics use USER_Clini; adult residential uses Name; nursing homes use Name___Nom; pharmacies use Pharmacy_Name) — a hardcoded Name_E filter against any non-hospital layer 400s upstream, live-confirmed during this plan"
    - "out_fields='*' for nb_get_health_facilities — used instead of an exact field list because the 6 layers' schemas differ too widely (compact 12-field hospital shape vs. a 70+ field Esri-geocoder-derived shape on layers 2-5) to express as one out_fields string"
    - "Bilingual NOT_CONFIGURED message constants live entirely in tools.py and read nothing from the environment — the environment is read only inside client.py's _511_get, verified by a live sentinel-key leakage test across all three 511 tools"

key-files:
  created: []
  modified:
    - src/mcp_canada/modules/new_brunswick/client.py
    - src/mcp_canada/modules/new_brunswick/tools.py
    - src/mcp_canada/modules/new_brunswick/__tests__/conftest.py
    - src/mcp_canada/modules/new_brunswick/__tests__/test_client.py
    - src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py

key-decisions:
  - "Live-verified the real per-layer field schemas for GeoNB_Health_Facilities (all 6 layers, geonb.snb.ca ?f=json probe, 2026-07-30) beyond what 21-SPIKE.md's partial listing covered for layers 2-5 — SPIKE named only representative fields (Match_addr, LongLabel, Total__of_beds) for the wide-schema layers, not an exhaustive field list or the actual name/phone field per layer. This plan's own probe found the real name field per layer (Name_E / USER_Clini / Name / Name___Nom / Pharmacy_Name) and confirmed live that filtering layer 3 (adult_residential_centre) on Name_E returns an upstream HTTP 400 'Failed to execute query' — proving the field genuinely does not exist there rather than merely being undocumented."
  - "out_fields is always '*' for nb_get_health_facilities rather than an explicit per-layer field list, because the 6 layers' schemas diverge too widely (12 fields on layers 0-1 vs. 70+ Esri-geocoder-derived fields on layers 2-5) for one out_fields string to serve every dispatch key; the client still returns whatever the layer actually publishes."
  - "district= on nb_get_public_schools filters strDST using live-verified short codes (ASD-E/ASD-N/ASD-S/ASD-W anglophone; DSF-NE/DSF-NO/DSF-S francophone) rather than the plan's illustrative 'Anglophone East' example, which does not match the field's real values — confirmed by a live distinct-value query against both layers."
  - "Orchestrator-directed addition: TestManifestMatchesShippedSurface replaces the previously-tautological ALL_NB_TOOLS = ALL_NB_TOOL_NAMES framing with two genuinely falsifiable assertions — every manifest name resolves to a real @tool object (proven via the __fastmcp__ decorator marker, not merely hasattr), and no nb_-prefixed @tool exists outside the manifest. Manually verified the detector actually fires by injecting a decoy nb_fake_tool at runtime and confirming the drift is caught. The inaccurate ALL_NB_TOOLS comment (which claimed a cross-check that only verified count/membership/prefix, never resolution) was corrected to describe what is now actually enforced."
  - "Task-atomicity note: both plan tasks touch the same 4 files (client.py, tools.py, test_client.py, test_tools.py) with edits made in single batched passes per file. To preserve one commit per task, the Task 1 (health/schools) commit was constructed by reconstructing an intermediate file state with the 511 functions reverted to their original NotImplementedError stubs and the manifest-integrity test omitted (it cannot pass until all 22 tools exist), verified independently (243 tests green) before committing; the working tree was then restored to the full final state for the Task 2 commit. No code content differs from a normal sequential two-task execution — this only affects how the diff was split across commits."

requirements-completed: [NB-19, NB-20, NB-21, NB-22, NB-23, ERR-01, ERR-06, ERR-07]

coverage:
  - id: D1
    description: "nb_get_health_facilities dispatches all 6 GeoNB_Health_Facilities layers (hospital_horizon, hospital_vitalite, after_hours_clinic, adult_residential_centre, nursing_home, pharmacy) by the locked HEALTH_FACILITY_LAYERS constant map, rejecting an unrecognized facility_type with INVALID_INPUT and the valid list at both the tool and client layer before any network call"
    requirement: "NB-19"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/test_client.py#TestFetchHealthFacilities, __tests__/test_tools.py#TestNbGetHealthFacilities"
        status: pass
      - kind: other
        ref: "live command: nb_get_health_facilities(facility_type='not-a-real-type') -> INVALID_INPUT with valid list; nb_get_health_facilities(facility_type='adult_residential_centre', limit=50) -> 50 rows, no error"
        status: pass
    human_judgment: false
  - id: D2
    description: "A parametrized test pins the dispatched layer id for every key of HEALTH_FACILITY_LAYERS and SCHOOL_SECTOR_LAYERS, read from call_args rather than the mocked return value — the assertion class that would have caught the Saskatchewan wrong-layer bug"
    requirement: "NB-20"
    verification:
      - kind: unit
        ref: "test_client.py#TestFetchHealthFacilities::test_dispatches_correct_layer_id_for_every_key, TestFetchPublicSchools::test_dispatches_correct_layer_id_for_every_key"
        status: pass
    human_judgment: false
  - id: D3
    description: "nb_get_public_schools dispatches the anglophone/francophone layers by the locked SCHOOL_SECTOR_LAYERS constant map (default anglophone), rejecting an unrecognized sector with INVALID_INPUT before any network call, with district= filtering the live-verified strDST short codes"
    requirement: "NB-21"
    verification:
      - kind: unit
        ref: "test_client.py#TestFetchPublicSchools, test_tools.py#TestNbGetPublicSchools"
        status: pass
      - kind: other
        ref: "live command: nb_get_public_schools(sector='anglophone', limit=50, lang='fr') -> 50 rows, _meta.lang == 'fr'"
        status: pass
    human_judgment: false
  - id: D4
    description: "The three NB 511 transport tools (nb_get_road_events, nb_get_winter_road_conditions, nb_get_traffic_cameras) return a bilingual NOT_CONFIGURED envelope — never a raised exception — when NEW_BRUNSWICK_511_KEY is absent, and never echo a configured key's value into any serialised response"
    requirement: "NB-22"
    verification:
      - kind: unit
        ref: "test_client.py#TestFetchRoadEvents, TestFetchWinterRoadConditions, TestFetchTrafficCameras; test_tools.py#TestNbGetRoadEvents, TestNbGetWinterRoadConditions, TestNbGetTrafficCameras (including *_never_leaks_sentinel_key_in_serialised_response)"
        status: pass
      - kind: other
        ref: "live command: all three tools return NOT_CONFIGURED with distinct en/fr messages when unset; with NEW_BRUNSWICK_511_KEY='SENTINEL-DO-NOT-LEAK' set, the sentinel never appears in any tool's json.dumps output — prints '511 STUBS OK'"
        status: pass
    human_judgment: false
  - id: D5
    description: "All three 511 tools remain fully covered by the project-wide catch-all error-handling gate (@upstream_guard) — the NOT_CONFIGURED branch is one arm, not a replacement for timeout/connect-error/HTTP-error handling"
    requirement: "NB-23"
    verification:
      - kind: unit
        ref: "test_tools.py#TestNbGetRoadEvents::test_timeout_returns_upstream_error_envelope, ::test_connect_error_returns_upstream_error_envelope, ::test_http_500_returns_upstream_error_envelope (mirrored for winter roads and cameras)"
        status: pass
      - kind: other
        ref: "uv run pytest tests/test_tool_error_handling.py -q -> 10 passed (all three 511 tools covered by @upstream_guard)"
        status: pass
    human_judgment: false
  - id: D6
    description: "constants.ALL_NB_TOOL_NAMES is genuinely, falsifiably proven set-equal to the @tool objects registered in tools.py — both directions — replacing the prior tautological alias-equals-itself framing; the 22-tool manifest is complete and coverage/lint/type gates stay green with no new dependency and no constants.py edit"
    requirement: "ERR-01"
    verification:
      - kind: unit
        ref: "test_tools.py#TestManifestMatchesShippedSurface::test_every_manifest_name_resolves_to_a_registered_tool, ::test_no_nb_prefixed_tool_exists_outside_the_manifest"
        status: pass
      - kind: other
        ref: "uv run pytest --cov=src/mcp_canada --cov-fail-under=95 -> 97.36%; uv run pyright src/mcp_canada/modules/new_brunswick/ -> 0 errors; uv run ruff check src/ tests/ -> all checks passed; git diff --stat constants.py server.py pyproject.toml uv.lock -> empty; manual decoy-tool injection confirmed the detector actually fires on drift"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-07-30
status: complete
---

# Phase 21 Plan 06: Health/Education Dispatch Tools + NB 511 Transport Stubs Summary

**nb_get_health_facilities (6-layer GeoNB_Health_Facilities dispatch with a live-verified per-layer name-field map) and nb_get_public_schools (anglophone/francophone GeoNB_EECD_PublicSchools dispatch), plus three key-gated NB 511 transport tools returning a bilingual NOT_CONFIGURED envelope, closing New Brunswick's 22-tool manifest with a genuinely falsifiable manifest-integrity test.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-07-30T17:35:00Z (approx.)
- **Completed:** 2026-07-30T18:30:00Z (approx.)
- **Tasks:** 2 (`type="auto" tdd="true"`), both shipped code
- **Files modified:** 5

## Accomplishments

- **`nb_get_health_facilities` — 6-layer dispatch tool over a locked constant map:** `fetch_health_facilities`/`nb_get_health_facilities` queries `GeoNB_Health_Facilities`, dispatching `hospital_horizon` (layer 0), `hospital_vitalite` (1), `after_hours_clinic` (2), `adult_residential_centre` (3), `nursing_home` (4) and `pharmacy` (5) purely by `HEALTH_FACILITY_LAYERS[facility_type]` — never positionally. An unrecognized `facility_type` returns `INVALID_INPUT` with the sorted valid list at both the tool's own pre-check and the client's second-line-of-defence check, before any network call. `out_fields` is always `"*"` because the 6 layers do not share one schema.
- **Live-verified the real per-layer field schemas** (this plan's own probe against `geonb.snb.ca/arcgis/rest/services/GeoNB_Health_Facilities/MapServer/{0..5}?f=json`, 2026-07-30) beyond what `21-SPIKE.md`'s partial listing covered for layers 2-5. Found the real name field per layer — `Name_E` (hospitals, layers 0-1), `USER_Clini` (after-hours clinics), `Name` (adult residential), `Name___Nom` (nursing homes), `Pharmacy_Name` (pharmacies) — and encoded them in a new `_HEALTH_FACILITY_NAME_FIELD` dispatch map so `name=` filtering never sends a WHERE clause referencing a field that layer doesn't have. Confirmed live: filtering layer 3 on `Name_E` returns upstream HTTP 400 `"Failed to execute query"` — the field genuinely does not exist there, not merely undocumented.
- **`nb_get_public_schools` — anglophone/francophone dispatch:** `fetch_public_schools`/`nb_get_public_schools` queries `GeoNB_EECD_PublicSchools`, dispatching `sector` (default `"anglophone"`) through `SCHOOL_SECTOR_LAYERS`. Both layers share one field schema (`strID`, `strDST`, `strNM`, `strAD1`, `strGR`, `strURL`). `district=` builds a case-insensitive containment clause on `strDST`; live-verified real values are short codes `ASD-E`/`ASD-N`/`ASD-S`/`ASD-W` (anglophone) and `DSF-NE`/`DSF-NO`/`DSF-S` (francophone) — not the plan's illustrative "Anglophone East" example, which doesn't match the field's actual values.
- **A parametrized layer-id test for both dispatch maps** — `TestFetchHealthFacilities::test_dispatches_correct_layer_id_for_every_key` and the same for schools — asserts the dispatched `layer_id` from `call_args` for every key in `HEALTH_FACILITY_LAYERS`/`SCHOOL_SECTOR_LAYERS`, the assertion class that would have caught the Saskatchewan wrong-layer bug.
- **Three NB 511 transport tools, key-gated (D-09/D-10):** `nb_get_road_events`, `nb_get_winter_road_conditions` and `nb_get_traffic_cameras` mirror Manitoba's `Five11NotConfigured` pattern exactly. Each catches `Five11NotConfigured` explicitly and returns `make_error("NOT_CONFIGURED", ...)` with a bilingual message naming `NEW_BRUNSWICK_511_KEY` and `https://511.gnb.ca` — a normal, deterministic envelope, never a raised exception. `tools.py` reads nothing from the environment itself (the message constants are static strings); only `client.py`'s `_511_get` reads `NEW_BRUNSWICK_511_KEY`. Road events and winter roads cache at `CACHE_TTL_LIVE`; cameras cache at `CACHE_TTL_META` since camera locations are stable infrastructure.
- **Key-leakage proven live:** with `NEW_BRUNSWICK_511_KEY` set to the sentinel `SENTINEL-DO-NOT-LEAK`, none of the three tools echo it in their serialised response — confirmed both via a unit test (`json.dumps(result)` assertion on each tool's `NOT_CONFIGURED` path) and via the plan's live verify script hitting the real, unkeyed-tolerant `511.gnb.ca/api/v2/get/{event,winterroads,cameras}` endpoints, which return HTTP 400 `<Error><Message>Invalid Key</Message></Error>` — `@upstream_guard`'s `httpx.HTTPStatusError` handler reports only the status code, never `str(exc)` (which would otherwise carry the full request URL including the query-string key, confirmed live).
- **Manifest integrity test (orchestrator-directed addition):** `TestManifestMatchesShippedSurface` replaces the previously tautological `ALL_NB_TOOLS = ALL_NB_TOOL_NAMES` framing — an alias can never be unequal to what it aliases, so the old comment's claim of a "cross-check" was unfalsifiable. The new test asserts, bidirectionally: every name in `constants.ALL_NB_TOOL_NAMES` resolves to a real, callable `@tool` object in `tools.py` (proven via the `__fastmcp__` decorator marker, not merely `hasattr`), and no `nb_`-prefixed `@tool` exists in the module outside the manifest. Manually verified the detector actually fires by injecting a decoy `nb_fake_tool` at runtime and confirming the drift is caught (`shipped - manifest == {'nb_fake_tool'}`). The inaccurate `ALL_NB_TOOLS` comment was corrected to describe what is actually enforced.

## Task Commits

1. **Task 1: Health facilities and public schools — layer-dispatch tools** - `29de32e` (feat)
2. **Task 2: NB 511 — three key-gated transport tools returning a structured unconfigured envelope (+ manifest integrity test)** - `dbd3b23` (feat)

**Plan metadata:** (this commit, immediately following)

## Files Created/Modified

- `src/mcp_canada/modules/new_brunswick/client.py` - `fetch_health_facilities` and `fetch_public_schools` filled (were `NotImplementedError` stubs); new private `_HEALTH_FACILITY_NAME_FIELD` dispatch map; `fetch_road_events`, `fetch_winter_road_conditions`, `fetch_traffic_cameras` filled; import block extended with `CACHE_TTL_LIVE`, `HEALTH_FACILITIES_SERVICE`, `HEALTH_FACILITY_LAYERS`, `PUBLIC_SCHOOLS_SERVICE`, `SCHOOL_SECTOR_LAYERS`
- `src/mcp_canada/modules/new_brunswick/tools.py` - `nb_get_health_facilities`, `nb_get_public_schools`, `nb_get_road_events`, `nb_get_winter_road_conditions`, `nb_get_traffic_cameras` added; `_API_NAME_511`, `_NOT_CONFIGURED_MSG_EN`/`_NOT_CONFIGURED_MSG_FR` added; `__all__` extended with all 5 new tool names; `ALL_NB_TOOLS` comment corrected to describe the actual enforcement mechanism
- `src/mcp_canada/modules/new_brunswick/__tests__/conftest.py` - `HEALTH_FACILITY_GEOJSON` and `PUBLIC_SCHOOL_GEOJSON` fixtures added (live-verified field names)
- `src/mcp_canada/modules/new_brunswick/__tests__/test_client.py` - `TestFetchHealthFacilities`, `TestFetchPublicSchools`, `TestFetchRoadEvents`, `TestFetchWinterRoadConditions`, `TestFetchTrafficCameras` filled with real tests (were placeholders); `TestStubsRaiseNotImplementedError` removed entirely (no locked-signature stubs remain — all 22 `fetch_*` functions are now implemented)
- `src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py` - `TestNbGetHealthFacilities`, `TestNbGetPublicSchools`, `TestNbGetRoadEvents`, `TestNbGetWinterRoadConditions`, `TestNbGetTrafficCameras` filled with real tests (were placeholders); new `TestManifestMatchesShippedSurface` class added

## Decisions Made

- Live-verified the actual field schemas for all 6 `GeoNB_Health_Facilities` layers (a fresh probe beyond `21-SPIKE.md` section 4, which named only representative fields for layers 2-5) to build a per-layer name-field dispatch map, confirming live that a hardcoded `Name_E` filter against a non-hospital layer 400s upstream.
- `out_fields="*"` for health facilities (rather than an explicit field list) because the 6 layers' schemas diverge too widely for one field list to serve every dispatch key.
- `district=` on public schools filters the live-verified real short codes (`ASD-*`/`DSF-*`), not the plan's illustrative long-form example.
- The manifest-integrity test asserts drift bidirectionally via the `__fastmcp__` decorator marker rather than a plain string-membership check, and its detection was manually proven (decoy-tool injection) rather than merely asserted to pass.
- To preserve one commit per task despite both tasks touching the same 4 files with edits applied in batched passes, the Task 1 commit was constructed from a reconstructed intermediate file state (511 functions reverted to their pre-plan `NotImplementedError` stubs, manifest test omitted since it cannot pass until all 22 tools exist) and independently verified (243 tests green) before committing, then the working tree was restored to the full final state for Task 2. The shipped code is byte-identical to a normal sequential execution; only the commit split required this reconstruction.

## Deviations from Plan

### Auto-fixed Issues

None — both `fetch_health_facilities`/`fetch_public_schools` and the three 511 tools were genuinely absent (`raise NotImplementedError` stubs / no code) before this plan, matching the plan's premise exactly.

### Documentation notes (not deviations)

**1. Acceptance criterion's literal grep vs. its stated intent.** Task 2's acceptance criteria include `grep -n "environ" src/mcp_canada/modules/new_brunswick/tools.py` returning no lines, annotated "the environment is read only in the client." Taken completely literally, this substring-matches the English word "environment" inside docstrings and `Keywords:` lines (the wetlands and contaminated-sites tools already used "environment" in their `Keywords:` line before this plan touched the file, so the literal grep was never zero even pre-plan). The actual intent — no `os.environ`/`os.getenv` access inside `tools.py` — holds: `grep -n "os\.environ\|os\.getenv\|environ\["` returns zero matches. Recorded here per Plan 05's precedent for the same class of literal-vs-intent acceptance-criterion nuance.

**2. SPIKE.md field-schema gap for `GeoNB_Health_Facilities` layers 2-5, filled by this plan's own live probe.** `21-SPIKE.md` section 4 named only representative fields for the wide-schema layers (`Match_addr`, `LongLabel`, `Total__of_beds`, etc.), not an exhaustive field list or the name/phone field per layer. Rather than guess (which the plan explicitly forbids for layer ids and by extension for any load-bearing field reference), this plan probed `geonb.snb.ca/arcgis/rest/services/GeoNB_Health_Facilities/MapServer/{0..5}?f=json` live and confirmed the real name field per layer, documented in `client.py`'s `_HEALTH_FACILITY_NAME_FIELD` comment and above. `21-SPIKE.md` itself was not edited (out of this plan's file scope).

---

**Total deviations:** 0 auto-fixed; 2 documentation notes recorded for transparency.
**Impact on plan:** None — both tasks executed as specified, with the health-facility field-schema gap resolved via live verification rather than guessing, consistent with the plan's own "never guess a layer id" principle extended to field names.

## Issues Encountered

None.

## User Setup Required

**NB 511 requires a developer key for live use, but no code changes are needed to obtain it.** `NEW_BRUNSWICK_511_KEY` must be set for `nb_get_road_events`, `nb_get_winter_road_conditions` and `nb_get_traffic_cameras` to return live data — without it, all three deterministically return a `NOT_CONFIGURED` envelope (this is the intended behavior, not a bug). No public self-serve registration page was found for NB 511 during planning or this plan's execution; a key must be requested from the NB Department of Transportation and Infrastructure via https://511.gnb.ca. A live keyed run (beyond the unconfigured-path and sentinel-leakage tests already verified) is recorded as manual-only verification, per the plan's own `<precondition>` on Task 2.

## Next Phase Readiness

- All 22 names in `constants.ALL_NB_TOOL_NAMES` now resolve to a real, registered `@tool` in `tools.py` — verified both by the new `TestManifestMatchesShippedSurface` and live at the interpreter level.
- Health, education and transport are the phase's remaining curated domains — Plan 07 (docs) is the only work left in this phase.
- Coverage stays at 97.36% (project-wide), well above the 95% gate; `pyright`/`ruff` clean on the module; no new dependency; `constants.py`/`server.py`/`pyproject.toml`/`uv.lock` untouched.
- No blockers.

---
*Phase: 21-new-brunswick-government-open-data*
*Completed: 2026-07-30*

## Self-Check: PASSED

Claimed files (`src/mcp_canada/modules/new_brunswick/client.py`,
`src/mcp_canada/modules/new_brunswick/tools.py`,
`src/mcp_canada/modules/new_brunswick/__tests__/conftest.py`) verified present on
disk with the new functions/fixtures. Claimed commit hashes `29de32e` and
`dbd3b23` verified present in `git log --oneline --all`.
