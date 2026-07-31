---
phase: 21-new-brunswick-government-open-data
plan: 05
subsystem: api
tags: [arcgis-server, geonb, new-brunswick, parcels, civic-address, geocoding, mcp-tools]

# Dependency graph
requires:
  - phase: 21-new-brunswick-government-open-data
    provides: "Plan 04's _require_any_filter/FILTER_REQUIRED_TOOLS guard and _escape_sql_value helper, both already registered for nb_get_parcels/nb_get_civic_addresses; Plan 01's live-verified 21-SPIKE.md layer ids and locked 22-tool manifest"
provides:
  - "nb_get_parcels and nb_get_civic_addresses — New Brunswick's geocoding pair, both rejecting an unfiltered call before any network request (T-21-03) on GeoNB's two largest layers (604,520 parcels, 373,172 civic addresses)"
  - "_upper_contains_clause — a shared case-insensitive containment WHERE-clause helper (UPPER(field) LIKE '%VALUE%', both sides upper-cased) reusable by any future free-text GeoNB filter"
  - "Documented confirmation that the DNR pair (mineral occurrences, provincial parks) stays swapped to the long tail per the 21-01 checkpoint — no code shipped for either, both remain reachable via nb_query_geonb_layer"
affects: [21-06-health-education-511, 21-07-docs]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "_upper_contains_clause(field, value) — case-insensitive containment clause (UPPER(field) LIKE '%VALUE%', single-quote-escaped, both sides upper-cased) for any GeoNB free-text field a caller would substring-match rather than equality-match"
    - "Unquoted numeric WHERE clause for an integer-typed field (CIVIC_NUM={int(civic_number)}) — quoting an integer literal makes ArcGIS compare a number to a string and silently return nothing"

key-files:
  created: []
  modified:
    - src/mcp_canada/modules/new_brunswick/client.py
    - src/mcp_canada/modules/new_brunswick/tools.py
    - src/mcp_canada/modules/new_brunswick/__tests__/test_client.py
    - src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py

key-decisions:
  - "Task 1 (mineral occurrences / provincial parks) shipped no code — constants.ALL_NB_TOOL_NAMES was read first per the task's own precondition and confirmed the 21-01 checkpoint already swapped both tool names to the long tail (test_checkpoint_option_a_dropped_tools_are_not_in_manifest already asserted this). No client stub, no tool, no test additions were needed; this plan's file-scope stayed untouched for Task 1."
  - "Containment clauses use UPPER(field) LIKE '%VALUE%' with the value upper-cased in Python before single-quote-escaping — 'upper-casing both sides' per the plan's instruction, applied identically to COUNTY, COMMUNITY and STREET via the new shared _upper_contains_clause helper rather than three inline duplicates"
  - "PID stays an equality clause (identifier, not free text) while COUNTY/COMMUNITY/STREET use containment (free text) — matches the plan's explicit equality-for-identifiers-only rule and mirrors the wetlands/contaminated-sites precedent from Plan 04"
  - "CIVIC_NUM is interpolated as an unquoted Python int (int(civic_number)) rather than a formatted string, so a caller-supplied non-numeric value fails at Python's int() coercion (TypeError, caught by @upstream_guard) rather than silently producing a broken or SQL-injectable clause"

requirements-completed: [NB-15, NB-16, NB-17, NB-18, ERR-01, ERR-06, ERR-07]

coverage:
  - id: D1
    description: "nb_get_parcels resolves a New Brunswick property by PID (equality) or lists parcels by county (case-insensitive containment), rejecting an unfiltered call with INVALID_INPUT before any network call over the 604,520-row Parcels layer"
    requirement: "NB-15"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/test_client.py#TestFetchParcels, __tests__/test_tools.py#TestNbGetParcels"
        status: pass
      - kind: other
        ref: "live command: nb_get_parcels() -> INVALID_INPUT, no network call; nb_get_parcels(county='YORK', limit=25) -> LIVE CADASTRE OK 25 parcels"
        status: pass
    human_judgment: false
  - id: D2
    description: "nb_get_civic_addresses resolves an address by community/street (containment, AND-able) or civic_number (unquoted numeric equality), surfacing both official-language street-type fields, over the 373,172-row Civic_Address layer, rejecting an unfiltered call with INVALID_INPUT before any network call"
    requirement: "NB-16"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/test_client.py#TestFetchCivicAddresses, __tests__/test_tools.py#TestNbGetCivicAddresses"
        status: pass
      - kind: other
        ref: "live command: nb_get_civic_addresses(lang='fr') -> INVALID_INPUT, no network call; nb_get_civic_addresses(community='FREDERICTON', limit=25) -> LIVE CADASTRE OK 25 addresses"
        status: pass
    human_judgment: false
  - id: D3
    description: "Both tools' unfiltered-call guards are proven not-awaited (T-21-03) at the tool layer, and the client's _require_any_filter is proven as the second line of defence"
    requirement: "NB-17"
    verification:
      - kind: unit
        ref: "test_tools.py#TestNbGetParcels::test_unfiltered_call_returns_invalid_input_without_network_call, TestNbGetCivicAddresses::test_unfiltered_call_returns_invalid_input_without_network_call; test_client.py#TestFetchParcels::test_no_filter_raises_invalid_input_before_any_network_call, TestFetchCivicAddresses::test_no_filter_raises_invalid_input_before_any_network_call"
        status: pass
    human_judgment: false
  - id: D4
    description: "Mineral occurrences and provincial parks are confirmed absent from the curated manifest (21-01 checkpoint), documented rather than silently skipped, and remain reachable through nb_query_geonb_layer"
    requirement: "NB-18"
    verification:
      - kind: unit
        ref: "test_tools.py#TestAllNbToolNamesManifest::test_checkpoint_option_a_dropped_tools_are_not_in_manifest (pre-existing, re-confirmed)"
        status: pass
      - kind: other
        ref: "live command: 'nb_get_provincial_parks' not in constants.ALL_NB_TOOL_NAMES and not hasattr(tools, 'nb_get_provincial_parks') -> DNR TOOLS SWAPPED OUT per 21-01 checkpoint"
        status: pass
    human_judgment: false
  - id: D5
    description: "Every WHERE clause on both tools is built server-side from typed parameters with string values single-quote-escaped; apostrophe-bearing county/community values produce well-formed escaped clauses; coverage stays >=95%, manifest and tools list agree at 22 entries, constants.py untouched, no new dependency"
    requirement: "ERR-01"
    verification:
      - kind: unit
        ref: "test_client.py#TestFetchParcels::test_apostrophe_in_county_is_escaped, TestFetchCivicAddresses::test_apostrophe_in_community_is_escaped, test_civic_number_sends_unquoted_numeric_comparison"
        status: pass
      - kind: other
        ref: "uv run pytest --cov=src/mcp_canada --cov-fail-under=95 -> 97.32%; uv run pyright src/mcp_canada/modules/new_brunswick/ -> 0 errors; uv run ruff check src/ tests/ -> all checks passed; git diff --stat constants.py server.py pyproject.toml uv.lock -> empty; ALL_NB_TOOL_NAMES set-equal to tools.ALL_NB_TOOLS, both length 22"
        status: pass
    human_judgment: false

duration: ~30min
completed: 2026-07-30
status: complete
---

# Phase 21 Plan 05: Crown Land Completion + Parcels/Civic Address Summary

**New Brunswick's geocoding pair — nb_get_parcels (604,520-row cadastre, PID equality / county containment) and nb_get_civic_addresses (373,172-row address points, community/street containment / unquoted numeric civic_number) — both rejecting an unfiltered call before any network request; the DNR pair (mineral occurrences, provincial parks) confirmed and documented as swapped to the long tail by the 21-01 checkpoint, shipping no code.**

## Performance

- **Duration:** ~30 min
- **Started:** 2026-07-30T16:58:00Z (approx.)
- **Completed:** 2026-07-30T17:28:12Z
- **Tasks:** 2 (`type="auto" tdd="true"`); Task 1 was a documented no-op, Task 2 shipped code
- **Files modified:** 4

## Accomplishments

- **Task 1 confirmed and documented, no code shipped:** read `constants.ALL_NB_TOOL_NAMES` first per
  the task's own precondition and confirmed neither `nb_get_mineral_occurrences` nor
  `nb_get_provincial_parks` is a manifest member — the 21-01 checkpoint (option-a) already swapped
  both to the long tail to hold the 22-tool budget, and `test_checkpoint_option_a_dropped_tools_are_not_in_manifest`
  already asserted this in the existing suite. Both stay reachable through `nb_query_geonb_layer`
  (`GeoNB_DNR_MineralOccurrences` / `GeoNB_DNR_ProvincialParks`, both layer 0, per `21-SPIKE.md`
  section 2). No `fetch_*`, no `nb_get_*`, no test additions for this task — the plan's own action
  explicitly permits a no-op recording when the manifest omits the tool names.
- **`nb_get_parcels` — the province's largest layer, guarded:** `fetch_parcels`/`nb_get_parcels`
  queries `GeoNB_SNB_Parcels` layer 0 (604,520 rows). `pid` builds a single-quote-escaped equality
  clause on `PID` (an identifier); `county` builds a case-insensitive containment clause via the new
  `_upper_contains_clause` helper. An unfiltered call is rejected with `INVALID_INPUT` before any
  network call, enforced at both the tool's own pre-check and the client's `_require_any_filter`
  (the Alberta/Saskatchewan double-guard, both proven by dedicated not-awaited tests). Live run:
  `nb_get_parcels(county='YORK', limit=25)` returned 25 parcels; the unfiltered call returned
  `INVALID_INPUT` with zero network calls.
- **`nb_get_civic_addresses` — the province's second-largest layer, guarded, bilingual:**
  `fetch_civic_addresses`/`nb_get_civic_addresses` queries `GeoNB_DPS_Civic_Address` layer 0
  (373,172 rows). `community` and `street` each build a containment clause via
  `_upper_contains_clause` and AND together when both are supplied; `civic_number` builds a numeric
  equality clause on `CIVIC_NUM` with the integer interpolated **unquoted** (`CIVIC_NUM=160`, not
  `CIVIC_NUM='160'`) — quoting it would make ArcGIS compare a number to a string and silently return
  nothing. The response always carries both `ST_TYPE_E` and `ST_TYPE_F` (bilingual street-type
  fields). Same double-guard as parcels. Live run: `nb_get_civic_addresses(community='FREDERICTON',
  limit=25)` returned 25 address points; the unfiltered call (with `lang='fr'`) returned
  `INVALID_INPUT` with zero network calls.
- **New shared clause-building helper:** `_upper_contains_clause(field, value)` in `client.py`
  builds `UPPER(field) LIKE '%VALUE%'`, upper-casing both the SQL field expression and the Python
  string before single-quote-escaping — used identically by `COUNTY`, `COMMUNITY` and `STREET`
  rather than three separately-written inline containment clauses. This is now available for any
  future free-text GeoNB filter.
- **Escaping proven with apostrophe-bearing values:** `fetch_parcels(county="Queen's")` produces
  `UPPER(COUNTY) LIKE '%QUEEN''S%'`; `fetch_civic_addresses(community="St. Martin's")` produces a
  clause containing `ST. MARTIN''S` — both well-formed, neither broken.

## Task Commits

1. **Task 1: Crown land and forestry completion — mineral occurrences and provincial parks** -
   no-op, no code changed, no commit (confirmed absent from `constants.ALL_NB_TOOL_NAMES`, recorded
   here and in the existing test suite)
2. **Task 2: Parcels and civic addresses — the two largest layers, both filter-required** -
   `910727b` (feat)

**Plan metadata:** (this commit, immediately following)

## Files Created/Modified

- `src/mcp_canada/modules/new_brunswick/client.py` - `fetch_parcels` and `fetch_civic_addresses`
  filled (were `NotImplementedError` stubs); new private helper `_upper_contains_clause`; import
  block extended with `PARCELS_SERVICE`, `PARCELS_LAYER`, `CIVIC_ADDRESS_SERVICE`,
  `CIVIC_ADDRESS_LAYER`
- `src/mcp_canada/modules/new_brunswick/tools.py` - `nb_get_parcels` and `nb_get_civic_addresses`
  added; `__all__` and constants import extended with `PARCELS_SERVICE`, `CIVIC_ADDRESS_SERVICE`
- `src/mcp_canada/modules/new_brunswick/__tests__/test_client.py` - `TestFetchParcels` and
  `TestFetchCivicAddresses` filled with real tests (were placeholders); the two stub-contract tests
  removed from `TestStubsRaiseNotImplementedError` since neither function raises
  `NotImplementedError` anymore
- `src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py` - `TestNbGetParcels` and
  `TestNbGetCivicAddresses` filled with real tests (were placeholders), including not-awaited guard
  tests, double-guard tests and an unquoted-civic-number assertion

## Decisions Made

- Task 1 shipped no code: `constants.ALL_NB_TOOL_NAMES` was read first (the task's own precondition)
  and confirmed the 21-01 checkpoint's option-a resolution already dropped both `nb_get_mineral_occurrences`
  and `nb_get_provincial_parks` to the long tail. Recording this here rather than silently skipping it.
- Containment clauses (`COUNTY`, `COMMUNITY`, `STREET`) share one helper (`_upper_contains_clause`)
  rather than three inline duplicates, upper-casing both the SQL field via `UPPER()` and the Python
  value before escaping — the literal "upper-casing both sides" instruction from the plan.
- `PID` stayed equality (identifier) while `COUNTY`/`COMMUNITY`/`STREET` use containment (free text)
  — matches the plan's explicit equality-for-identifiers-only rule and the Plan 04 wetlands/
  contaminated-sites precedent.
- `CIVIC_NUM` is interpolated via `int(civic_number)` (unquoted) rather than a string-formatted
  literal, so a non-numeric value would fail at Python's own coercion rather than producing an
  ambiguous or unsafe clause; the type annotation (`civic_number: int | None`) already constrains
  the caller-supplied value before this line runs.

## Deviations from Plan

None — plan executed exactly as written, including Task 1's explicit no-op branch. One
documentation note (not a deviation this plan introduced): the plan's Task 1 acceptance criterion
`grep -c "nb_get_provincial_parks" tools.py` is 0 is worded for the tool-definition case, but
`nb_query_geonb_layer`'s docstring (added by Plan 04, commit `5c7e718`, predating this plan) already
mentions `nb_get_provincial_parks` by name as an example of what the long-tail escape hatch reaches
— so the literal grep count is 1, not 0. `grep -c "async def nb_get_provincial_parks"` (the actual
tool-definition check) is 0, confirming no tool was ever added. Recorded here so it doesn't read as
a missed acceptance criterion.

## Issues Encountered

None.

## User Setup Required

None — GeoNB is a keyless, publicly reachable ArcGIS Server; no external service configuration
required for this plan.

## Next Phase Readiness

- `_upper_contains_clause` is available in `client.py` for any future free-text GeoNB filter.
- `constants.ALL_NB_TOOL_NAMES` (22 entries) and `tools.ALL_NB_TOOLS` remain set-equal — verified
  live.
- Plan 06 (health/education + 511) can proceed; parcels and civic addresses are New Brunswick's
  complete geocoding surface for this phase.
- No blockers.

---
*Phase: 21-new-brunswick-government-open-data*
*Completed: 2026-07-30*

## Self-Check: PASSED

Both claimed files (`src/mcp_canada/modules/new_brunswick/client.py`,
`src/mcp_canada/modules/new_brunswick/tools.py`) verified present on disk with the new functions.
Claimed commit hash `910727b` verified present in `git log --oneline --all`.
