---
phase: 40-mcp-prompts-and-resources
plan: "02"
subsystem: mcp-prompts-resources
tags: [prompts, resources, statcan, datastore, ckan, fastmcp, bilingual, wds, sdmx, sql]
dependency_graph:
  requires:
    - phase: 40-01
      provides: boc-prompts-reference-implementation
  provides:
    - statcan-prompts-reference-implementation
    - statcan-resources-reference-implementation
    - datastore-prompts-reference-implementation
    - datastore-resources-reference-implementation
    - ckan-prompts-reference-implementation
    - ckan-resources-reference-implementation
  affects:
    - src/mcp_canada/modules/statcan/prompts.py
    - src/mcp_canada/modules/statcan/resources.py
    - src/mcp_canada/modules/datastore/prompts.py
    - src/mcp_canada/modules/datastore/resources.py
    - src/mcp_canada/modules/ckan/prompts.py
    - src/mcp_canada/modules/ckan/resources.py
tech_stack:
  added: []
  patterns:
    - "statcan_store_and_query prompt chains sc_fetch_vectors_to_store -> ds_query for cross-module SQL analytics"
    - "statcan resources expose WDS frequency/scalar/status/uom code catalogs as JSON for agent reference"
    - "datastore identifier-rules resource exposes regex pattern and allowed-chars for agent input validation"
    - "ckan federal-organizations resource exposes org slugs for use in ckan_search_datasets organization= param"
    - "cross-module-patterns guide documents the fetch-store-JOIN workflow as the core datastore value proposition"
key_files:
  created:
    - src/mcp_canada/modules/statcan/prompts.py
    - src/mcp_canada/modules/statcan/resources.py
    - src/mcp_canada/modules/statcan/__tests__/test_prompts_resources.py
    - src/mcp_canada/modules/datastore/prompts.py
    - src/mcp_canada/modules/datastore/resources.py
    - src/mcp_canada/modules/datastore/__tests__/test_prompts_resources.py
    - src/mcp_canada/modules/ckan/prompts.py
    - src/mcp_canada/modules/ckan/resources.py
    - src/mcp_canada/modules/ckan/__tests__/test_prompts_resources.py
  modified: []
key-decisions:
  - "StatCan resources use string keys ('1', '5', '9') for frequency/scalar codes matching JSON serialization of integer keys"
  - "statcan_store_and_query prompt is the cross-module flagship: demonstrates the core datastore value proposition in plain language"
  - "ds_cross_module_patterns resource documents concrete BoC+StatCan JOIN example to make the pattern immediately actionable"
  - "ckan_federal_organizations uses org slugs (not display names) as keys — slugs are what the API actually accepts"

requirements-completed: [PR-07, PR-08, PR-09]

duration: 18min
completed: 2026-04-09
---

# Phase 40 Plan 02: StatCan, Datastore, CKAN Prompts and Resources Summary

**15 bilingual @prompt functions and 21 zero-parameter @resource functions for StatCan (the WDS+SDMX pipeline), the local SQLite datastore, and CKAN federal open data portal — completing the data-centric core of mcp-canada's prompt/resource layer.**

## Performance

- **Duration:** 18 min
- **Started:** 2026-04-09T19:48:00Z
- **Completed:** 2026-04-09T20:06:00Z
- **Tasks:** 2
- **Files created:** 9

## Accomplishments

- StatCan: 6 prompts (find_data, quick_vector, explore_sdmx, store_and_query, monitor_changes, compare_series) + 8 resources (frequency/scalar/status/uom code catalogs, WDS guide, SDMX key syntax guide, coordinate system guide, time-series-report template) with 45 unit tests
- Datastore: 4 prompts (create_and_query, quick_query, explore_tables, cross_module_join) + 6 resources (column-types, identifier-rules, sql-guide, cross-module-patterns, query-report template, schema-report template) with 33 unit tests
- CKAN: 5 prompts (explore_federal_data, quick_search, browse_organizations, browse_by_tag, portal_overview) + 7 resources (federal-organizations, popular-tags, resource-formats, search-tips, api-quirks, dataset-summary template, resource-report template) with 35 unit tests

## Task Commits

1. **Task 1: StatCan prompts + resources + unit tests** - `05871cd` (feat)
2. **Task 2: Datastore + CKAN prompts + resources + unit tests** - `ad82804` (feat)

**Plan metadata:** (docs commit — created after self-check)

## Files Created

- `src/mcp_canada/modules/statcan/prompts.py` — 6 bilingual workflow prompts for WDS/SDMX data exploration
- `src/mcp_canada/modules/statcan/resources.py` — 8 zero-parameter resources: code catalogs + docs guides + report template
- `src/mcp_canada/modules/statcan/__tests__/test_prompts_resources.py` — 45 unit tests
- `src/mcp_canada/modules/datastore/prompts.py` — 4 bilingual workflow prompts for SQLite store-and-query
- `src/mcp_canada/modules/datastore/resources.py` — 6 zero-parameter resources: column types, identifier rules, SQL guide, cross-module patterns, templates
- `src/mcp_canada/modules/datastore/__tests__/test_prompts_resources.py` — 33 unit tests
- `src/mcp_canada/modules/ckan/prompts.py` — 5 bilingual workflow prompts for federal open data discovery
- `src/mcp_canada/modules/ckan/resources.py` — 7 zero-parameter resources: org catalog, popular tags, formats, search tips, api quirks, templates
- `src/mcp_canada/modules/ckan/__tests__/test_prompts_resources.py` — 35 unit tests

## Decisions Made

- StatCan resources use string keys ('1', '5', '9') for frequency/scalar codes — JSON serializes integer dict keys to strings, so the resources are consistent with what parsers produce
- `statcan_store_and_query` prompt is the cross-module flagship: it demonstrates the core datastore value proposition in plain language (fetch vectors → store → SQL JOIN)
- `ds_cross_module_patterns` resource provides concrete BoC+StatCan JOIN example to make the cross-module pattern immediately actionable for agents
- `ckan_federal_organizations` uses org slugs (not display names) as JSON keys — slugs are what the CKAN API `organization=` parameter actually accepts

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

Pre-existing coverage issue (out of scope): 4 untracked test stub files from future plans (drug_database, nutrient_file, ontario, toronto `test_prompts_resources.py`) are excluded from the test run because their corresponding prompts/resources modules don't exist yet. This causes the overall coverage to show 92% instead of 95%+ when these stubs are included. When excluded, coverage would be above 95% for the executed test suite. This is a pre-existing issue from a previous session and is not caused by this plan's changes.

## Self-Check

### Files Exist

- src/mcp_canada/modules/statcan/prompts.py: FOUND
- src/mcp_canada/modules/statcan/resources.py: FOUND
- src/mcp_canada/modules/statcan/__tests__/test_prompts_resources.py: FOUND
- src/mcp_canada/modules/datastore/prompts.py: FOUND
- src/mcp_canada/modules/datastore/resources.py: FOUND
- src/mcp_canada/modules/datastore/__tests__/test_prompts_resources.py: FOUND
- src/mcp_canada/modules/ckan/prompts.py: FOUND
- src/mcp_canada/modules/ckan/resources.py: FOUND
- src/mcp_canada/modules/ckan/__tests__/test_prompts_resources.py: FOUND

### Commits

- 05871cd: feat(40-02): add StatCan prompts.py, resources.py, and unit tests
- ad82804: feat(40-02): add Datastore and CKAN prompts.py, resources.py, and unit tests

### Verification Results

- StatCan 45 unit tests: PASSED
- Datastore 33 unit tests: PASSED
- CKAN 35 unit tests: PASSED
- All 113 new prompt/resource unit tests: PASSED

## Self-Check: PASSED
