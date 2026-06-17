---
phase: quick-1
plan: 1
subsystem: integration-tests
tags: [testing, de-masking, integration, provincial, quality]
dependency_graph:
  requires: [phase-20-nova-scotia]
  provides: [loud-provincial-integration-failures]
  affects: [tests/integration/test_tool_scenarios.py]
tech_stack:
  added: []
  patterns: [loud-assert-with-data-in-message, empty-is-valid-preserved, error-set-allowance]
key_files:
  modified:
    - tests/integration/test_tool_scenarios.py
decisions:
  - "De-masked 24 SK+NS+QC+MB idiom-A/B tests; all passed live — masks were latent risk, not hiding current bugs"
  - "Reclassified AB road_events as PRESERVE-with-hardening: kept tolerance for unreachable 511 feed but added else-branch rejecting non-{UPSTREAM_ERROR,RATE_LIMITED} codes"
  - "17 pre-existing failures in BOC/Toronto/StatCan/IRCC/YorkRegion out of scope; deferred"
metrics:
  duration: "22min"
  completed_date: "2026-06-17"
  tasks: 3
  files_modified: 1
---

# Quick Task 1: Remove UPSTREAM_ERROR Escape-Hatch Pattern Summary

Remove the UPSTREAM_ERROR early-return masking pattern from all MB/SK/AB/QC/NS
provincial integration scenarios and verify the suite stays green — confirming the
masks were latent risk, not hiding current live failures.

## Objective

Prevent recurrence of the "ship broken, tests green" failure class (demonstrated by
the NS health-facilities 400 bug in Phase 20-08) across all provincial modules before
Phase 20 is pushed. Two masking idioms existed:

- Idiom A (SK+NS): `if "error" in data: assert code == "UPSTREAM_ERROR"; return`
- Idiom B (QC+MB): `if "_meta" in data: <assertions> # else silently passes`

Both idioms let a real upstream 4xx/5xx pass silently.

## Scenarios De-masked

### Task 1: Idiom A — SK + NS (16 changes)

| Test | Province | Was Masking |
|------|----------|-------------|
| `test_crop_yields_canola_field_present` | SK | early-return on UPSTREAM_ERROR |
| `test_grain_elevators_capacity_and_province` | SK | early-return on UPSTREAM_ERROR |
| `test_potash_mines_name_and_company` | SK | early-return on UPSTREAM_ERROR |
| `test_air_quality_aqhi_field_present` | SK | early-return on UPSTREAM_ERROR |
| `test_wsa_stations_hyperlink_graph_present` | SK | early-return on UPSTREAM_ERROR |
| `test_wsa_reservoirs_reservoir_name_proves_layer_26` | SK | early-return on UPSTREAM_ERROR |
| `test_search_datasets_returns_number_matched` | SK | early-return on UPSTREAM_ERROR |
| `test_marine_leases_license_le_and_no_the_geom` | NS | early-return on UPSTREAM_ERROR |
| `test_fish_hatchery_stocking_field_presence` | NS | early-return on UPSTREAM_ERROR |
| `test_aquaculture_production_kgs_and_total_value` | NS | early-return on UPSTREAM_ERROR |
| `test_water_quality_temperature_c_field_present` | NS | early-return on UPSTREAM_ERROR |
| `test_protected_areas_pro_name_and_no_the_geom` | NS | early-return on UPSTREAM_ERROR |
| `test_air_quality_stations_name_and_coordinates` | NS | early-return on UPSTREAM_ERROR |
| `test_vital_statistics_live_births_field_present` | NS | early-return on UPSTREAM_ERROR |
| `test_list_categories_20_plus_including_fishing` | NS | early-return on UPSTREAM_ERROR |
| `test_search_datasets_returns_h57h_p9mm` | NS | early-return on UPSTREAM_ERROR |
| NS AMI bare-ami follow-up | NS | early-return on UPSTREAM_ERROR in inner call |

Each replaced with `assert "_meta" in data, f"Expected live success from <tool>, got: {data}"`.
All existing field-presence assertions preserved unchanged.

### Task 2: Idiom B — QC + MB (9 changes); AB hardening (1 change)

| Test | Province | Was Masking |
|------|----------|-------------|
| `test_search_datasets_live` | QC | silent else on error |
| `test_list_organizations_live` | QC | silent else on error |
| `test_list_categories_groups_not_tags` | QC | silent else on error |
| `test_get_er_wait_times_live` | QC | silent else on error |
| `test_get_health_installations_live` | QC | silent else on error |
| `test_get_road_works_wfs_csv` | QC | silent else on error (kept inner empty-is-valid check) |
| `test_provincial_parks` | MB | silent else on error |
| `test_surgical_wait_times_for_cardiac` | MB | silent else on error |
| `test_drought_status` | MB | silent else on error |
| `test_alberta_road_events` | AB | PRESERVE-with-hardening: added else asserting code in {UPSTREAM_ERROR,RATE_LIMITED} |

## Scenarios Preserved (PRESERVE List)

All PRESERVE-list tests left byte-for-byte unchanged:

| Test | Reason |
|------|--------|
| SK `test_fire_bans_empty_is_valid_not_error` | Empty list is documented valid off-season state |
| SK `test_invalid_mineral_returns_structured_error` | Error-path test by design |
| NS `test_boil_water_advisories_empty_is_valid_not_error` | Empty list valid (mirrors SK fire bans) |
| NS `test_invalid_disease_returns_structured_error` | Error-path test by design |
| NS `test_invalid_facility_type_returns_structured_error` | Error-path test by design |
| NS AMI sex="F" allowance | Documented-legitimate: AMI dataset has no sex field |
| AB `test_alberta_production_volumes_gas` | Documented AER republish flakiness |
| MB `test_flood_alerts_empty_is_success` | Empty features is valid off-season state |
| MB `test_511_not_configured_without_key` | Key-gated tool, NOT_CONFIGURED is correct |
| MB `test_search_datasets_live` / `list_organizations_live` / `list_categories_live` | Already loud (`assert "error" not in data`) |

## Live Integration Suite Results (Task 3)

Suite run: `uv run pytest tests/integration/ -v -m integration --timeout=120`

**Results: 314 passed, 17 failed in 219.64s**

### MB/SK/QC/NS/AB de-masked tests: ALL 25 PASSED

The masks were latent risk — they were not hiding any current live bug in the targeted provinces. All de-masked provincial tests passed on their first run with strict assertions.

### 17 Pre-existing Failures (Out of Scope)

All 17 failures are in modules outside this task's scope. They existed before the de-masking changes (confirmed: none are in MB/SK/AB/QC/NS sections). Deferred to separate tasks.

| Failure Cluster | Tests Failed | Root Cause |
|----------------|-------------|-----------|
| BOC exchange rates | 4 tests + 1 cross-module | `data["data"]` is now a dict keyed by series name, not a list — API response shape change |
| Toronto TTC GTFS | 2 tests | `UPSTREAM_ERROR: Failed to fetch TTC GTFS stop/route data` — live TTC GTFS endpoint unreachable |
| Toronto cross-module CKAN | 1 test | ReadTimeout on ckan_search_datasets during long suite run |
| StatCan coord API | 2 tests | Coordinate `1.1.0.0.0.0.0.0.0.0` returning null fields — Pydantic validation error |
| StatCan bulk_vector | 1 test | `data["data"]` is dict keyed by vector_id, not list — shape drift |
| SDMX data_last_n | 1 test | `INVALID_INPUT: Expecting ',' delimiter` — JSON parse error |
| IRCC invalid_breakdown | 1 test | ToolError raised (Pydantic Literal rejection) but test expects dict return |
| IRCC store_pr cross-module | 1 test | `type 'dict' is not supported` in datastore insert — IRCC row contains nested dict |
| York Region data shape | 3 tests | `data["data"]` is dict `{count, features, truncated}`, not list — shape drift |

## Deviations from Plan

None. Executed exactly as written. The plan correctly predicted that de-masking would reveal no hidden current bugs in the targeted provinces (the masks were preventive, not covering active failures).

## Self-Check: PASSED

All committed changes verified:
- File `/Users/mariomeyer/code/ReyemTech/ai/mcp-canada/tests/integration/test_tool_scenarios.py` exists and parses cleanly
- Commits 6d41766 (Task 1) and 7e0bf73 (Task 2) confirmed in git log
- Live suite run completed: 314 passed, 17 failed (all failures pre-existing, out of scope)
- No `== "UPSTREAM_ERROR"` + bare `return` remains in any SK/NS live-data test
- No `if "_meta" in data:` guard remains in QC live-data or MB parks/surgical/drought tests
