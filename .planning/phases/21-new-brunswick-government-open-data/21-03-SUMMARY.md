---
phase: 21-new-brunswick-government-open-data
plan: 03
subsystem: api
tags: [prompts, resources, bilingual, geonb, new-brunswick, mcp-guidance]

# Dependency graph
requires:
  - phase: 21-new-brunswick-government-open-data
    provides: "Plan 01 scaffold (locked 22-tool ALL_NB_TOOL_NAMES manifest, checkpoint option-a applied) and Plan 02's 7 shipped discovery tools (federal CKAN + gnb.socrata.com), which this plan's prompts/resources reference by name"
provides:
  - "6 nb_ prompts — 3 guided workflows (nb_flood_risk_assessment, nb_crown_land_report, nb_property_lookup) chaining 3-4 distinct tools each, 3 quick lookups (nb_quick_dataset_search, nb_health_facility_finder, nb_bilingual_dataset_lookup)"
  - "7 nb_ zero-parameter resources — data://nb/geonb-services (62-service catalogue), data://nb/counties, data://nb/health-regions, data://nb/school-districts, docs://nb/portal-guide, docs://nb/geonb-query-guide, template://nb/flood-risk-report"
  - "The corrected NB portal-architecture record (docs://nb/portal-guide) — overturns 21-CONTEXT.md's stale 'no provincial catalogue' claim now that gnb.socrata.com is documented as live"
affects: [21-04-flood-water, 21-05-crown-land-parcels, 21-06-health-education-511, 21-07-docs]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Manifest cross-check via regex token extraction in tests (\\bnb_[a-z0-9_]+\\b) rather than naive whitespace-splitting — catches tool names inside backtick/parenthetical prose reliably"
    - "@resource/@prompt decorators return the plain function, not a Prompt/Resource instance (confirmed again, same lesson as Nova Scotia/Saskatchewan) — URI/name verification must read decorator source text, not isinstance-check via inspect.getmembers"

key-files:
  created: []
  modified:
    - src/mcp_canada/modules/new_brunswick/prompts.py
    - src/mcp_canada/modules/new_brunswick/resources.py
    - src/mcp_canada/modules/new_brunswick/__tests__/test_prompts_resources.py

key-decisions:
  - "Mineral occurrences and provincial parks (dropped to the long tail by the 21-01 checkpoint) are never named as standalone nb_get_* tools anywhere in prompts.py — nb_crown_land_report routes to them exclusively through nb_get_geonb_service_layers + nb_query_geonb_layer, and a dedicated test (test_crown_land_report_never_names_dropped_curated_tools) pins this"
  - "data://nb/geonb-services classifies all 62 services into exactly 3 statuses (curated=9, excluded=18, long_tail=35) rather than the plan's original 11/18/33 split — the 2 checkpoint-dropped tools (mineral occurrences, provincial parks) moved from curated to long_tail, which is the correct post-checkpoint state, not a discrepancy"
  - "Resource URI/decorator verification (both my test file and the plan's own acceptance criteria) reads resources.py source text directly rather than isinstance-checking via inspect.getmembers, because @resource returns the plain function — an isinstance(obj, Resource) loop silently finds zero matches, the same trap the Nova Scotia test file works around"

requirements-completed: [NB-24, NB-25]

coverage:
  - id: D1
    description: "6 nb_ prompts are discoverable via __all__ (3 guided workflows returning list[Message] with >=2 messages and >=3 distinct tool names each, 3 quick lookups returning str), every referenced tool name is a member of the locked constants.ALL_NB_TOOL_NAMES manifest, and en/fr renderings differ for every prompt"
    requirement: "NB-24"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/test_prompts_resources.py#TestNbPrompts (27 tests)"
        status: pass
      - kind: other
        ref: "live command: PROMPTS OK 6 (plan's own <verify> block, 0 bad tool-name references)"
        status: pass
    human_judgment: false
  - id: D2
    description: "7 nb_ zero-parameter resources are discoverable via __all__ across data://nb/, docs://nb/, template://nb/ URIs; data://nb/geonb-services carries all 62 live-enumerated GeoNB services with department, curated-tool/layer-id, and exclusion reason; every cited curated_tool is a member of ALL_NB_TOOL_NAMES"
    requirement: "NB-25"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/test_prompts_resources.py#TestNbResources (29 tests)"
        status: pass
      - kind: other
        ref: "live command: RESOURCES OK 7 62 services (plan's own <verify> block)"
        status: pass
    human_judgment: false
  - id: D3
    description: "docs://nb/portal-guide records every verified dead end (data.gnb.ca/opendata.gnb.ca/nbopendata.ca DNS failure, GeoNB Hub HTTP 401) and every live surface (geonb.snb.ca, open.canada.ca, gnb.socrata.com 312 datasets, key-gated 511.gnb.ca/NEW_BRUNSWICK_511_KEY), overturning 21-CONTEXT.md's stale 'NB has no provincial catalogue' framing"
    verification:
      - kind: unit
        ref: "src/mcp_canada/modules/new_brunswick/__tests__/test_prompts_resources.py#TestNbResources::test_portal_guide_documents_every_surface, ::test_portal_guide_documents_dead_ends, ::test_portal_guide_does_not_claim_nb_has_no_provincial_catalogue"
        status: pass
    human_judgment: false

duration: ~45min
completed: 2026-07-30
status: complete
---

# Phase 21 Plan 03: New Brunswick Prompts and Resources Summary

**6 bilingual nb_ prompts (3 guided workflows chaining flood/Crown-land/property tool sequences, 3 quick lookups) and 7 zero-parameter nb_ resources — including the 62-service GeoNB catalogue and the corrected portal-architecture guide that documents gnb.socrata.com as a live 312-dataset surface, not the dead end 21-CONTEXT.md originally assumed.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-07-30T15:55:00Z (approx., following 21-01/21-02 wave-0/wave-1 context read)
- **Completed:** 2026-07-30T16:43:35Z
- **Tasks:** 2 (both TDD)
- **Files modified:** 3

## Accomplishments

- **6 prompts, every tool reference manifest-verified:** `nb_flood_risk_assessment` chains
  `nb_get_flood_hazard_areas` → `nb_get_historical_floods` → `nb_get_wetlands` →
  `nb_get_civic_addresses`, citing the `Technical_`/`Sheet_Numb` fields the plan's truths
  required. `nb_crown_land_report` chains `nb_get_crown_land` →
  `nb_get_geonb_service_layers` → `nb_query_geonb_layer` — routing mineral-occurrences and
  forestry data through the long-tail path since neither has a dedicated tool post-checkpoint.
  `nb_property_lookup` chains `nb_get_parcels` → `nb_get_civic_addresses` →
  `nb_get_geonb_service_layers`/`nb_query_geonb_layer` for the NB911 community boundary. All
  three quick lookups (`nb_quick_dataset_search`, `nb_health_facility_finder`,
  `nb_bilingual_dataset_lookup`) instruct exactly one primary tool call. A dedicated test
  (`test_every_referenced_tool_name_is_in_the_locked_manifest`) plus the plan's own live
  `PROMPTS OK` verification confirm zero tool names outside `constants.ALL_NB_TOOL_NAMES`.
- **7 zero-parameter resources, `data://nb/geonb-services` as the centerpiece:** all 62
  live-enumerated GeoNB services (from 21-SPIKE.md) are catalogued with department decode
  (ENV/ELG/DNR/SNB/DPS/EECD/ENB/PETL/Health/NRCan/DEM/Basemap), curated-tool/layer-id where a
  dedicated tool exists (9 after the checkpoint dropped mineral occurrences and provincial
  parks), and an exclusion reason for the 18 dead/non-attribute services (5 basemaps, retired
  wildlife refuges, 12 tile/index/telemetry services). The remaining 35 are long-tail —
  reachable only through `nb_list_geonb_services` → `nb_get_geonb_service_layers` →
  `nb_query_geonb_layer`.
- **`docs://nb/portal-guide` corrects the record:** documents `geonb.snb.ca` as bare ArcGIS
  Server (62 MapServer, zero FeatureServer), the three permanently-dead hostnames
  (`data.gnb.ca`/`opendata.gnb.ca`/`nbopendata.ca`), the GeoNB Hub's HTTP 401, `open.canada.ca`
  (federal CKAN, `organization:nb`, 221 datasets, T-21-04's non-overridable scoping),
  `gnb.socrata.com` (312 datasets, keyless, the 21-01 Task 2 checkpoint's option-a outcome —
  explicitly flagged as contradicting 21-CONTEXT.md's original "no provincial catalogue"
  premise), and NB 511's key-gated state (`NEW_BRUNSWICK_511_KEY`). Also carries the D-12
  bilingual duplicate-FR/EN-record warning.
- **`docs://nb/geonb-query-guide`** walks the mandatory three-step GeoNB discovery path with a
  worked `GeoNB_DNR_Crown_Land` example (layer 3, not 0), WHERE-clause SQL-92 syntax, the
  record cap/truncation flag, the three filter-required layers (parcels/civic
  addresses/wetlands, T-21-03), truncated shapefile field names, and the Crown Land integer
  `HOLDER` code trap.
- **`data://nb/counties`** (15, bilingual), **`data://nb/health-regions`** (Horizon/Vitalité
  RHAs + the 6-value `HEALTH_FACILITY_LAYERS` dispatch), **`data://nb/school-districts`**
  (anglophone/francophone sectors + the 2-value `SCHOOL_SECTOR_LAYERS` dispatch, with the
  `strID`-style truncated-field warning) — all embedded statically, per D-07, replacing the
  un-curated `GeoNB_SNB_Counties`/`GeoNB_ENB_RegionalHealthAuthorities`/`GeoNB_ENB_SchoolDistricts`
  services.
- **`template://nb/flood-risk-report`** — 12-placeholder markdown skeleton covering location,
  hazard classification, historical events, wetland proximity, affected civic addresses,
  source map sheet, and data-retrieval date.

## Task Commits

Each task was committed atomically:

1. **Task 1: 6 prompts — 3 guided workflows + 3 quick lookups** - `9baae12` (feat) —
   `prompts.py` + `TestNbPrompts` (27 tests); `TestNbResources` left as the Wave-0 placeholder
   stub for this commit so the historical state is self-consistent (resources.py still
   import-only at this point).
2. **Task 2: 7 resources — GeoNB catalogue, static reference data, portal and query guides,
   report template** - `3b70258` (feat) — `resources.py` + `TestNbResources` filled in
   (29 tests); `test_prompts_resources.py` restored to its complete, final form.

**Plan metadata:** (this commit, immediately following)

## Files Created/Modified

- `src/mcp_canada/modules/new_brunswick/prompts.py` — 6 standalone `@prompt` functions
  (`nb_flood_risk_assessment`, `nb_crown_land_report`, `nb_property_lookup`,
  `nb_quick_dataset_search`, `nb_health_facility_finder`, `nb_bilingual_dataset_lookup`), all
  `nb_`-prefixed, all bilingual via `lang: Annotated[Literal["en","fr"], ...] = "en"`
- `src/mcp_canada/modules/new_brunswick/resources.py` — 7 standalone, zero-parameter
  `@resource` functions (`nb_geonb_services`, `nb_counties`, `nb_health_regions`,
  `nb_school_districts`, `nb_portal_guide`, `nb_geonb_query_guide`,
  `nb_flood_risk_report_template`), each URI type- and module-prefixed
  (`data://nb/...`, `docs://nb/...`, `template://nb/...`)
- `src/mcp_canada/modules/new_brunswick/__tests__/test_prompts_resources.py` — `TestNbPrompts`
  (27 tests: return shape, roles, tool-name membership, bilingual difference, and a
  manifest-wide cross-check) and `TestNbResources` (29 tests: count, zero-parameter signature,
  JSON validity, 62-entry catalogue integrity, curated-tool manifest membership, required
  guide substrings, template placeholders)

## Decisions Made

- Both `nb_get_mineral_occurrences` and `nb_get_provincial_parks` — which the plan's own
  action text tentatively named ("if the manifest contains it") — are absent from
  `constants.ALL_NB_TOOL_NAMES` after the 21-01 checkpoint. `nb_crown_land_report` therefore
  routes to them exclusively via `nb_get_geonb_service_layers` + `nb_query_geonb_layer`, never
  as standalone tool names, and a dedicated regression test pins this so a future edit can't
  silently reintroduce a dangling reference.
- `data://nb/geonb-services`'s three-way split landed at curated=9/excluded=18/long_tail=35
  rather than the plan's originally-described 11/18/33 — this is the correct post-checkpoint
  arithmetic (62 total, unchanged), not a discrepancy: the 2 services the checkpoint demoted
  moved from `curated` to `long_tail`, and `curated_layer_id` is still populated on both so an
  agent using `nb_query_geonb_layer` directly doesn't have to guess them.
- Resource-URI verification (in both the test file and by inspection here) reads the decorator
  call site's `uri=` argument from source text rather than `isinstance(obj, Resource)` via
  `inspect.getmembers` — `@resource` returns the plain function unchanged (confirmed by direct
  inspection: `type(nb_counties)` is `function`), matching the Nova Scotia/Saskatchewan
  precedent noted in this plan's own `<action>` text ("the Nova Scotia lesson").

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Overly literal `@mcp.` substring check produced a false-positive test failure**
- **Found during:** Task 1, first test run
- **Issue:** An initial `test_no_mcp_decorator_used` test asserted `"@mcp." not in line` for
  every source line. This matched the module docstring's own explanatory prose ("NEVER
  `@mcp.prompt`") — the exact same false-positive pattern the 21-01-SUMMARY.md documented for
  `tools.py`'s docstring ("Uses standalone @tool from fastmcp.tools (NEVER @mcp.tool)").
- **Fix:** Changed the assertion to `not line.strip().startswith("@mcp.")`, matching actual
  decorator usage rather than any substring occurrence. Applied to both the prompts and
  resources variants of the test.
- **Files modified:** `src/mcp_canada/modules/new_brunswick/__tests__/test_prompts_resources.py`
- **Verification:** Full suite green afterward; `grep -c "@prompt" prompts.py` / `grep -c
  "@resource" resources.py` both report 8 (6/7 real decorators + 2 docstring mentions) — an
  expected, pre-existing pattern also present verbatim in `nova_scotia/prompts.py` and
  `nova_scotia/resources.py` (both grep to 8 as well), not a defect.
- **Committed in:** `9baae12` (Task 1 commit)

**2. [Rule 1 - Bug] `isinstance(obj, Resource)` resource-URI test found zero matches**
- **Found during:** Task 2, first test run
- **Issue:** An initial `test_resource_uris_are_type_and_module_prefixed` test looped
  `inspect.getmembers(resources_module)` looking for `fastmcp.resources.Resource` instances,
  expecting 7. It found 0 — `@resource` returns the plain function, not a `Resource` instance
  (confirmed: `type(nb_counties)` is `function`), so the loop body never executed and the
  `assert checked == 7` failed vacuously.
- **Fix:** Rewrote the test to extract the 7 `uri="data://nb/..."` / `"docs://nb/..."` /
  `"template://nb/..."` arguments directly from the decorator call sites in source text via
  regex, matching the plan's own acceptance-criteria approach (`grep -c
  "data://nb/\|docs://nb/\|template://nb/"`).
- **Files modified:** `src/mcp_canada/modules/new_brunswick/__tests__/test_prompts_resources.py`
- **Verification:** `uv run pytest ... -k test_resource_uris_are_type_and_module_prefixed`
  passes; confirms all 7 URIs present and correctly prefixed.
- **Committed in:** `3b70258` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 — test-authoring bugs caught and fixed before
committing; no production code was affected by either).
**Impact on plan:** No scope creep. Both fixes are test-file-only corrections that align the
suite with patterns already established (and documented) in prior sibling-province plans.

## Issues Encountered

None beyond the deviations above.

## User Setup Required

None - no external service configuration required for this plan. This plan adds no new
upstream calls (prompts/resources are static/guidance content); the `NEW_BRUNSWICK_511_KEY`
requirement documented in `docs://nb/portal-guide` belongs to Plan 06, not this plan.

## Next Phase Readiness

- Plans 04-06 can now implement their `fetch_*`/`nb_get_*` bodies with the guidance layer
  already in place — `docs://nb/geonb-query-guide` and `data://nb/geonb-services` give those
  plans a single source of truth for layer ids, filter-required layers, and field-name traps
  they don't need to re-derive.
- Plan 07 (docs) can build on `docs://nb/portal-guide`'s architecture record when it updates
  CLAUDE.md's Socrata section — this plan's guide is scoped to the `nb/` resource namespace and
  does not touch CLAUDE.md itself, per this plan's explicit file-scope boundary.
- No blockers. `client.py`/`tools.py`/`constants.py`/`test_client.py`/`test_tools.py` are
  byte-identical to their state before this plan (`git diff --stat` confirms empty) — zero
  collision risk with the parallel/sequential 21-02, 21-04, 21-05, 21-06 work.

---
*Phase: 21-new-brunswick-government-open-data*
*Completed: 2026-07-30*

## Self-Check: PASSED

All 4 claimed files verified present on disk. Both claimed commit hashes verified present in
git log (`9baae12`, `3b70258`).
