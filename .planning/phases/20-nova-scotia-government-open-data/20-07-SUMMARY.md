---
phase: 20-nova-scotia-government-open-data
plan: "07"
subsystem: nova-scotia-tests-docs
tags:
  - nova-scotia
  - socrata
  - parametrized-tests
  - integration-tests
  - field-presence
  - docs-sync
  - coverage
dependency_graph:
  requires: [20-06]
  provides: [NS-18]
  affects: [README, CLAUDE.md, EXAMPLES.md, docs/modules/nova-scotia.md, coverage-gate]
tech_stack:
  added: []
  patterns:
    - ALL_NS_TOOLS parametrize list (16 entries) with (tool_name, client_fn, kwargs, client_return)
    - TestNsEnvelopes/TestNsLangParam parametrized cross-cutting tests over all ns_ tools
    - Live field-presence integration tests via MCP Client (not client functions directly)
    - Rule 1 bug fix: length_of_advisory → length_of_advisory_in_days (live schema mismatch)
    - Socrata documented as 4th Portal Technologies row in CLAUDE.md
key_files:
  created:
    - docs/modules/nova-scotia.md
  modified:
    - src/mcp_canada/modules/nova_scotia/__tests__/test_tools.py
    - tests/integration/test_tool_scenarios.py
    - tests/integration/test_prompts_resources_scenarios.py
    - src/mcp_canada/modules/nova_scotia/client.py
    - README.md
    - CLAUDE.md
    - EXAMPLES.md
decisions:
  - "ALL_NS_TOOLS has 16 entries (not 17): tools.py has 16 ns_ functions; plan said 17 but code is authoritative (same pattern as SK: plan said 14, code has 13)"
  - "length_of_advisory → length_of_advisory_in_days (Rule 1 bug fix): actual Socrata column is length_of_advisory_in_days; live 400 unmasked by integration test"
  - "vital stats integration test uses payload.get('statistics') fallback: client key is 'statistics' not 'vital_stats'"
  - "Prompts count assert update: 'real_prompts >= 55' already passes since NS adds 6 more prompts (total well above threshold)"
metrics:
  duration: "12min"
  completed_date: "2026-06-15"
  tasks: 2
  files: 7
---

# Phase 20 Plan 07: Nova Scotia Tests, Integration & Docs Summary

32 parametrized unit tests (envelope + lang) + 24 live integration tests asserting field presence against data.novascotia.ca + docs sync (README/CLAUDE.md/EXAMPLES.md/nova-scotia.md) + 97.07% coverage gate. Phase 20 (NS-18) complete.

## What Was Built

### Task 1: Parametrized Tests + Live Field-Presence Integration

#### Parametrized Unit Tests (test_tools.py)

**`ALL_NS_TOOLS`** — 16-entry parametrize list covering every ns_ tool with `(tool_name, client_fn, kwargs, client_return)`:
- 5 discovery tools (Plan 02)
- 4 aquaculture tools (Plan 03)
- 4 environment/water/air tools (Plan 04)
- 3 health/demographics tools (Plan 05)

**`TestNsEnvelopes`** (16 parametrized tests):
- Every ns_ tool returns `_meta` with `source.api == "nova-scotia-socrata"`, `source.url`, `cached`, `lang`, `timestamp`
- Uses mocked client function returning empty-but-valid payload

**`TestNsLangParam`** (16 parametrized tests):
- Every ns_ tool propagates `lang='fr'` to `_meta.lang`
- Uses mocked client function

#### Live Integration Tests (TestNovaScotiaToolScenarios — 16 tests)

All tests call tools through `call_tool(mcp_server, 'ns_xxx', {...})` — the same path an agent takes. Every test asserts FIELD PRESENCE + non-null (the Manitoba lesson):

| Test | Field-presence assertion | Key invariant |
|------|--------------------------|---------------|
| `test_marine_leases_license_le_and_no_the_geom` | `license_le` non-null | `the_geom` ABSENT (geometry-exclusion proof) |
| `test_fish_hatchery_stocking_field_presence` | `stock`, `number_released`, `stocking_date` non-null | Hatchery catalog correctness |
| `test_aquaculture_production_kgs_and_total_value` | `kgs`, `total_value` in ≥1 row | Production dataset alive |
| `test_water_quality_temperature_c_field_present` | `station_number`, `date`, `temperature_c` non-null | Sensor data correctness |
| `test_boil_water_advisories_empty_is_valid_not_error` | `_meta` present, `error` absent | Empty-is-valid pattern |
| `test_protected_areas_pro_name_and_no_the_geom` | `pro_name`, `protect1`/`owner` non-null | `the_geom` ABSENT (geometry-exclusion proof) |
| `test_air_quality_stations_name_and_coordinates` | `station_name`, `latitude`, `longitude` non-null | Station catalog correctness |
| `test_health_facilities_hospital_field_presence` | `facility_name`, `county` non-null | Hospital dispatch correct |
| `test_health_facilities_ltc_beds_and_zone` | `beds` in ≥1 LTC row | LTC normalization correct |
| `test_vital_statistics_live_births_field_present` | `counties` (UPPERCASE), `live_births` non-null | Pitfall 4 schema correct |
| `test_chronic_disease_zone_and_prevalence_rate` | `zone` (NOT `health_zone`), `crude_prevalence_rate` | Zone normalization proof (AMI health_zone→zone) |
| `test_list_categories_20_plus_including_fishing` | ≥20 categories incl. "Fishing and Aquaculture" | categories= broken-param workaround proof |
| `test_discover_tools_finds_ns_search_datasets` | BM25 returns ≥1 `ns_` tool | MCP discoverability |
| `test_search_datasets_returns_h57h_p9mm` | `h57h-p9mm` in top 20 results, total≥10 | Catalog search + pagination |
| `test_invalid_disease_returns_structured_error` | `INVALID_INPUT` with `valid=` list | tuberculosis → structured error |
| `test_invalid_facility_type_returns_structured_error` | `INVALID_INPUT` with `valid=` list | clinic → structured error |

#### Nova Scotia Prompts/Resources Integration (TestNovaScotiaPromptsResources — 8 tests)

- `test_ns_prompts_discoverable`: all 6 NS prompts in `list_prompts()` (ns_explore_aquaculture_data, ns_health_zone_analysis, ns_water_quality_analysis, ns_quick_find_dataset, ns_quick_protected_areas, ns_quick_vital_stats)
- 7 resource read tests: 4 data:// JSON resources + 2 docs:// markdown resources + 1 template:// with `{placeholder}` syntax

#### Rule 1 Bug Fix: length_of_advisory column name

**Found during:** live integration test `test_boil_water_advisories_empty_is_valid_not_error`

**Issue:** `client.py` used `length_of_advisory` in the `$select` parameter but the actual Socrata column name on data.novascotia.ca is `length_of_advisory_in_days`. This caused a 400 Bad Request from the live API with message: `query.soql.no-such-column: No such column: length_of_advisory`.

**Fix:** Changed `select=` in `fetch_boil_water_advisories()` to use `length_of_advisory_in_days`.

**Files modified:** `src/mcp_canada/modules/nova_scotia/client.py`, `src/mcp_canada/modules/nova_scotia/__tests__/test_tools.py` (fixture updated)

### Task 2: Docs Sync + Coverage Gate

#### README.md

- Header: `250 tools` → `266 tools`, `7 provincial APIs` → `8 provincial APIs`
- Modules table: added Nova Scotia row (16 tools, 6 prompts, 7 resources, data.novascotia.ca Socrata)
- Total row: `250 → 266`
- Architecture section: added `nova_scotia/ # 16 tools — data.novascotia.ca Socrata SODA`
- License section: added Open Government Licence – Nova Scotia v1.1 attribution

#### docs/modules/nova-scotia.md (new file)

Full NS module documentation: tool catalog (5+4+4+3=16 tools), 6 prompts, 7 resources, Socrata quirks (categories= broken-param, geometry exclusion), deferred domains (transport/511, novagis ArcGIS Hub, rockweed leases), architecture notes (zone normalization, geometry exclusion dual-layer, cache TTLs).

#### CLAUDE.md

- Shared utilities: added `socrata.py` entry
- Portal Technologies: updated `(3)` → `(4)`, added **Socrata** row (`shared/socrata.py`, Phase 20, SODA API pattern)
- Added Socrata categories= workaround note + geometry exclusion + deferred NS domains note

#### EXAMPLES.md

- Added Example 27: NS aquaculture production + StatCan fisheries GDP — full 7-step Socrata→datastore→SQL JOIN workflow
- Updated tool count in "Getting Started": 250 → 266

#### Coverage Gate

`uv run pytest --cov=src/mcp_canada --cov-fail-under=95 -q` → **97.07%** (3021 passed, 2 skipped)

- `shared/socrata.py`: 95% coverage
- `modules/nova_scotia/`: above 95%

## NS-01…NS-18 Matrix Status

| Req | Description | Status |
|-----|-------------|--------|
| NS-01 | shared/socrata.py SODA client contract | ✅ Plan 01 |
| NS-02 | ns_search_datasets | ✅ Plan 02 |
| NS-03 | ns_get_dataset_details | ✅ Plan 02 |
| NS-04 | ns_query_dataset | ✅ Plan 02 |
| NS-05 | ns_list_organizations | ✅ Plan 02 |
| NS-06 | ns_list_categories (categories= workaround) | ✅ Plan 02 |
| NS-07 | ns_get_marine_aquaculture_leases | ✅ Plan 03 |
| NS-08 | ns_get_landbased_aquaculture_licenses | ✅ Plan 03 |
| NS-09 | ns_get_fish_hatchery_stocking | ✅ Plan 03 |
| NS-10 | ns_get_aquaculture_production | ✅ Plan 03 |
| NS-11 | ns_get_water_quality_monitoring | ✅ Plan 04 |
| NS-12 | ns_get_boil_water_advisories | ✅ Plan 04 |
| NS-13 | ns_get_health_facilities | ✅ Plan 05 |
| NS-14 | ns_get_vital_statistics | ✅ Plan 05 |
| NS-15 | ns_get_protected_areas | ✅ Plan 04 |
| NS-16 | ns_get_air_quality_stations | ✅ Plan 04 |
| NS-17 | ns_get_chronic_disease_prevalence | ✅ Plan 05 |
| NS-18 | integration tests + docs sync | ✅ Plan 07 (this plan) |

## Deferred Items

| Item | Reason |
|------|--------|
| Transport/511 | NS 511 portal is HTML-only; no machine-readable API or JSON feed |
| NS ArcGIS Hub (novagis) | No public no-auth FeatureServers confirmed on novagis |
| Rockweed leases (exhe-htib) | Geometry-only dataset (3 tabular fields); discoverable via ns_query_dataset |
| Per-station air quality time series | 20+ datasets per pollutant/station; routed to ns_query_dataset; documented in docs://ns/portal-guide and docs://ns/air-quality-guide |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed length_of_advisory column name (live schema mismatch)**
- **Found during:** Task 1 live integration test (test_boil_water_advisories_empty_is_valid_not_error)
- **Issue:** `fetch_boil_water_advisories()` requested `length_of_advisory` in `$select` but actual NS Socrata column is `length_of_advisory_in_days` — causing HTTP 400 `query.soql.no-such-column`
- **Fix:** Updated `select=` in client.py + fixture in test_tools.py
- **Files modified:** `src/mcp_canada/modules/nova_scotia/client.py`, `src/mcp_canada/modules/nova_scotia/__tests__/test_tools.py`
- **Commit:** 0dfabd1

**2. [Rule 1 - Bug] Fixed vital statistics key in integration test**
- **Found during:** Task 1 live integration test (test_vital_statistics_live_births_field_present)
- **Issue:** Integration test accessed `data["data"]["vital_stats"]` but client returns `{"statistics": rows, ...}` (key is "statistics")
- **Fix:** Updated integration test to use `payload.get("statistics") or payload.get("vital_stats")`
- **Files modified:** `tests/integration/test_tool_scenarios.py`
- **Commit:** 0dfabd1

**Note on tool count:** ALL_NS_TOOLS has 16 entries. The plan spec says "17 tools" but the implementation (tools.py) has 16 `async def ns_` functions. Code is authoritative. The 20-05-SUMMARY table says 5+4+4+3=16; the "17" in the narrative is incorrect. This matches the Saskatchewan precedent (plan said 14, code has 13, code wins).

## Self-Check: PASSED

- `src/mcp_canada/modules/nova_scotia/__tests__/test_tools.py`: FOUND (TestNsEnvelopes + TestNsLangParam with 16 parametrized cases each)
- `tests/integration/test_tool_scenarios.py`: FOUND (TestNovaScotiaToolScenarios with 16 tests)
- `tests/integration/test_prompts_resources_scenarios.py`: FOUND (TestNovaScotiaPromptsResources with 8 tests)
- `docs/modules/nova-scotia.md`: FOUND
- `README.md`: FOUND (Nova Scotia section + 266 tool count)
- `CLAUDE.md`: FOUND (Socrata as 4th Portal Technologies row)
- `EXAMPLES.md`: FOUND (Example 27 NS cross-module SQL)
- Commit 0dfabd1 (Task 1): FOUND
- Commit 38d6744 (Task 2): FOUND
- Coverage: 97.07% ≥ 95% required
- All 24 NovaScotia live integration tests: PASSED against real data.novascotia.ca
- All 32 parametrized unit tests: PASSED
- Total nova_scotia suite: 286 tests PASSED
