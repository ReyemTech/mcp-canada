---
phase: 17-alberta-government-open-data
plan: "08"
subsystem: alberta-prompts-resources
tags: [alberta, prompts, resources, bilingual, fastmcp, mcp-discovery, ab-23, ab-27]

requires:
  - phase: 17-alberta-government-open-data
    plan: "01"
    provides: "Prompt/resource scaffolds with locked imports and __all__ exports"
  - phase: 17-alberta-government-open-data
    plan: "02"
    provides: "5 CKAN discovery tool names for cross-referencing in guided prompts"
  - phase: 17-alberta-government-open-data
    plan: "03"
    provides: "4 AER energy tool names (alberta_get_well_licences_*, _pipeline_statistics, _production_volumes)"
  - phase: 17-alberta-government-open-data
    plan: "04"
    provides: "4 wildfire tool names (alberta_get_active_fires, _fire_perimeters, _fire_bans, _fire_control_orders)"
  - phase: 17-alberta-government-open-data
    plan: "05"
    provides: "3 AHS health tool names (alberta_get_hospitals, _ahs_zones, _health_facilities)"
  - phase: 17-alberta-government-open-data
    plan: "06"
    provides: "3 Alberta 511 transport tool names (alberta_get_road_events, _winter_road_conditions, _traffic_cameras)"
  - phase: 17-alberta-government-open-data
    plan: "07"
    provides: "5 environment/ag/demo/parks tool names for health-or-transport workflow"

provides:
  - "6 bilingual @prompt functions (3 guided list[Message] + 3 quick lookup str)"
  - "7 zero-parameter @resource functions (3 data:// + 2 docs:// + 2 template://)"
  - "data://alberta/ministries — 14 provincial ministry slugs with bilingual labels"
  - "data://alberta/forest-areas — all 10 wildfire FA_NAMEs with approximate hectares"
  - "data://alberta/ahs-zones — 5 AHS zones with POP2006/2011/2016 Statistics Canada values"
  - "docs://alberta/aer-data-guide — AER ST1/ST3/ST39 tool mapping, product slug casing, OneStop auth gate"
  - "docs://alberta/wildfire-data-guide — WMBappServices vs CKAN, fire status codes, FWI deferral, AB-23 water-licence guidance (requirement satisfied)"
  - "template://alberta/dataset-report + template://alberta/wildfire-report"
  - "TestAlbertaPrompts (10 tests) + TestAlbertaResources (8 tests) — 18/18 green"

affects: [17-09]

tech-stack:
  added: []
  patterns:
    - "Standalone @prompt / @resource from fastmcp.prompts / fastmcp.resources (never @mcp.*)"
    - "Bare @prompt decorator (no args) — bilingual content selected via lang Literal parameter"
    - "Zero-parameter @resource with URI + mime_type + name + title kwargs"
    - "Inline bilingual content in data:// (both en/fr keys in same JSON via ensure_ascii=False)"
    - "Inline bilingual content in docs:// (## English / ## Français sections in same markdown)"
    - "Guided prompts return list[Message] with user + assistant roles"
    - "Quick-lookup prompts return str with specific tool name + parameter guidance"

key-files:
  created:
    - .planning/phases/17-alberta-government-open-data/17-08-SUMMARY.md
  modified:
    - src/mcp_canada/modules/alberta/prompts.py
    - src/mcp_canada/modules/alberta/resources.py
    - src/mcp_canada/modules/alberta/__tests__/test_prompts_resources.py

key-decisions:
  - "Quick-lookup prompts kept parameter-free (lang only) — honors Plan 01 locked scaffold signatures, matches BC bc_quick_dataset_search / bc_wildfire_status_now precedent"
  - "Message content passed as positional string; role as kwarg — matches Quebec precedent, same shape works with FastMCP's FunctionPrompt.from_function"
  - "Bare @prompt decorator (no args) — discovered as function name, matches Quebec and Alberta Wave-0 scaffolds"
  - "data:// resources use ensure_ascii=False to preserve French accents in JSON bodies without \\u escapes"
  - "AB-23 water-licence-data guidance placed in docs://alberta/wildfire-data-guide (with explicit 'AB-23:' section heading) — cross-references the Alberta module's primary long-lived reference doc"
  - "Forest-areas hectares embedded inline with _meta note directing agents to alberta_get_fire_control_orders(category='forest_area') for live authoritative boundaries"
  - "AHS zones POP2006/2011/2016 embedded from plan's <required_data> block; note_en/note_fr directs agents to alberta_get_ahs_zones for live FeatureServer values"
  - "Direct await on prompt/resource functions in tests (Quebec pattern) — simpler than FunctionPrompt.from_function(bc pattern); both work with FastMCP"

patterns-established:
  - "Alberta prompts docstrings reference specific tool names AND specific resource URIs (e.g., 'See data://alberta/forest-areas') — enables MCP-level discovery chains where a prompt → resource chain is self-documenting"
  - "AB-23 requirement documented, not coded: the water-licence data is too large for alberta_query_dataset so the docs:// guide tells agents to use external download tools instead"

requirements-completed:
  - AB-23
  - AB-27

duration: 6min
completed: 2026-04-17
---

# Phase 17 Plan 08: Alberta Prompts and Resources Summary

**Added 6 bilingual prompts (3 guided workflows + 3 quick lookups) and 7 zero-parameter resources (3 data catalogs + 2 docs guides + 2 response templates) that turn Alberta's 24 raw tools into agent-discoverable workflows and provide the AB-23 water-licence documentation without requiring a (too-large) CKAN fetch.**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-04-17T19:19:58Z
- **Completed:** 2026-04-17T19:25:58Z
- **Tasks:** 2/2 green
- **Tests:** 18 new (10 prompts + 8 resources), 150 alberta module tests pass overall

## Accomplishments

- Filled all 6 @prompt placeholders with bilingual content chained to specific alberta_ tool names
- Filled all 7 @resource placeholders with inline bilingual content (no `lang` parameter — preserves FunctionResource over ResourceTemplate)
- Embedded the 10 Alberta Wildfire Forest Areas and 5 AHS zones from the plan's `<required_data>` block directly in `data://` resources; AREA_HECTARES and POP2006/2011/2016 present and spot-check verified (Calgary zone POP2016 = 1,544,495)
- Documented AB-23 water-licence guidance in `docs://alberta/wildfire-data-guide` with an explicit section explaining why `alberta_query_dataset` should not be used against the 87MB+ active and 169MB+ inactive CSV resources
- Cross-referenced `data://alberta/forest-areas` inside `docs://alberta/wildfire-data-guide` so agents following the documentation chain can pivot between static reference data and live FeatureServer queries
- TestAlbertaResources includes a dedicated AB-23 assertion that fails if the wildfire-data-guide drops the water-licence section

## Task Commits

1. **Task 1: 6 @prompt functions (3 guided + 3 quick lookups)** — `1a904a9` (feat)
2. **Task 2: 7 @resource functions (3 data + 2 docs + 2 templates)** — `a53c187` (feat)

## Files Modified

- `src/mcp_canada/modules/alberta/prompts.py` — 6 @prompt bodies filled; imports unchanged
- `src/mcp_canada/modules/alberta/resources.py` — 7 @resource functions + json import + @resource kwargs (uri/mime_type/name/title)
- `src/mcp_canada/modules/alberta/__tests__/test_prompts_resources.py` — TestAlbertaPrompts (10 tests) + TestAlbertaResources (8 tests) fully implemented

## Deviations from Plan

- **Prompt signatures:** Plan task 1 suggested giving `alberta_quick_dataset_search` and `alberta_check_road_conditions` additional parameters (`query: str`, `area_name: str = ""`). I kept them at `lang`-only per Plan 01's "signatures locked at Wave 0 — downstream plans fill bodies only, never change signatures" invariant, which also matches the BC and Quebec quick-lookup precedent. The parameter-free tool names are still specified in the body text, so agents can copy-paste them with their own arguments.
- **Resource decorator kwargs:** Plan showed `@resource(uri="...", name="...")` but the Quebec/BC precedent uses positional URI + `mime_type`, `name`, `title` kwargs. Adopted the richer form for better resources/list surfacing.
- **Test accessor pattern:** Plan suggested `.fn` accessor (`fn.fn()`). Quebec (the post-15-05 reference) calls functions directly (`await q_prompts.quebec_explore_health()`). Used Quebec's direct-call pattern — works because bare `@prompt` preserves the callable signature.

## Handoff to Plan 09

- Prompts and resources are registered; Plan 09's `TestAlbertaEnvelopes` + `TestAlbertaLangParam` parametrized tests can ignore them (they test @tool output shapes, not @prompt/@resource).
- The AB-23 documentation-only requirement is now satisfied via the wildfire-data-guide; Plan 09 does NOT need to add a water-licence tool.
- `docs://alberta/wildfire-data-guide` mentions the FWI deferral; Plan 09 integration tests should NOT expect an `alberta_get_fire_weather` tool.

## Self-Check: PASSED

- All 4 files present: prompts.py, resources.py, test_prompts_resources.py, 17-08-SUMMARY.md
- Both commits found: 1a904a9 (Task 1), a53c187 (Task 2)
- Full alberta module tests: 150/150 green
- Plan test suite: 18/18 green (10 prompts + 8 resources)
- test_quality.py: 5/5 green (no regressions)
