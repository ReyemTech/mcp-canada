---
phase: 20-nova-scotia-government-open-data
plan: "08"
type: gap-closure
subsystem: nova_scotia
tags: [socrata, health-facilities, bug-fix, normalization, tdd, test-quality]
dependency_graph:
  requires: [20-05-SUMMARY.md]
  provides: [NS-13 restored, per-dataset SoQL pattern, mock-vs-real test gap closed]
  affects: [tests/integration/test_tool_scenarios.py]
tech_stack:
  added: []
  patterns:
    - Per-dataset SoQL constants (HOSPITAL_SELECT/LTC_SELECT) for datasets with incompatible schemas
    - Post-fetch normalization via _normalize_hospital_row / _normalize_ltc_row pure helpers
    - _coerce_int / _coerce_float helpers for safe string→number coercion (never raise)
    - RED-scoped import placement (constants imported inside test methods to isolate RED failure)
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/nova_scotia/constants.py
    - src/mcp_canada/modules/nova_scotia/client.py
    - src/mcp_canada/modules/nova_scotia/__tests__/conftest.py
    - src/mcp_canada/modules/nova_scotia/__tests__/test_client.py
    - tests/integration/test_tool_scenarios.py
decisions:
  - HOSPITAL_SELECT/HOSPITAL_ORDER + LTC_SELECT/LTC_ORDER as Final constants alongside dataset IDs
  - county filter is hospital-only — LTC has no county column; where=None for LTC always
  - _normalize_hospital_row: facility->facility_name, derive x/y from the_geom.coordinates[0]/[1], strip the_geom
  - _normalize_ltc_row: facility_type->type, county=None, beds=_coerce_int(nursing_homes_nh_no_of_beds)
  - RED-scoped constants import: placed inside test method bodies so ImportError stays in TestNsGetHealthFacilities class only
  - UPSTREAM_ERROR early-out removed from both NS health integration scenarios (de-masking — prevents same bug class recurring)
metrics:
  duration: "5min"
  completed_date: "2026-06-16"
  tasks_completed: 3
  files_modified: 5
---

# Phase 20 Plan 08: Nova Scotia Health Facilities Gap Closure Summary

One-liner: Per-dataset SoQL branching + post-fetch normalization restoring both hospital and LTC `ns_get_health_facilities` live-200 paths, with real-raw-schema unit tests and de-masked integration scenarios.

## What Was Built

Closed the single major Phase 20 UAT gap (NS-13): `ns_get_health_facilities` was returning HTTP 400 for both `facility_type="hospital"` and `facility_type="long_term_care"`. The root cause was diagnosed 2026-06-15 in `.planning/debug/ns-health-facilities-400.md`.

### Root Cause

`fetch_health_facilities` dispatched to two Socrata datasets with incompatible raw schemas but built ONE shared `$select`/`$order`/`county=` filter from normalized field names that exist on neither raw dataset:

- Hospital `tmfr-3h8a` raw cols: `facility`, `address`, `town`, `county`, `type`, `the_geom`. The function requested `facility_name`, `x_coordinate`, `y_coordinate` → HTTP 400 ("No such column: facility_name").
- LTC `x76a-axw2` raw cols: `facility_name`, `address`, `town`, `postal_code`, `facility_type`, `zone`, `nursing_homes_nh_no_of_beds`, `x_coordinate`, `y_coordinate`. The function requested `county` → HTTP 400 ("No such column: county"). The `$order=county ASC` and `$where=county='...'` also referenced the missing column.

Tests missed it for two reasons:
1. Conftest fixtures used the POST-normalization shape (already had `facility_name`/`x_coordinate`/`county`), so the wrong `$select` was never validated against a real schema.
2. Integration tests treated `error.code == "UPSTREAM_ERROR"` as an acceptable pass-through and returned early, swallowing the live 400.

### Fix Applied

**Task 1 (RED):** Replaced conftest fixtures with REAL RAW Socrata schemas. Added `TestNsGetHealthFacilities` with 19 explicitly-named tests asserting per-dataset `$select`/`$order`/filter + raw→normalized mapping. Constants import placed inside test methods so RED ImportError scope was limited to this class only.

**Task 2 (GREEN):**
- `constants.py`: Added `HOSPITAL_SELECT`, `HOSPITAL_ORDER`, `LTC_SELECT`, `LTC_ORDER` as `Final[str]` constants (live-confirmed 2026-06-15 SoQL strings).
- `client.py`: Rewrote `fetch_health_facilities` to branch per `facility_type` for `dataset_id`/`select`/`order`/`where`. Hospital applies county filter; LTC NEVER sends county filter (column absent → 400). Added `_normalize_hospital_row` (derives x/y from `the_geom.coordinates`, strips `the_geom`, renames `facility`→`facility_name`) and `_normalize_ltc_row` (`facility_type`→`type`, `county=None`, beds coerced from `"190.0"`→int 190). Added `_coerce_int`/`_coerce_float` helpers that handle `None`/`""`/float-strings and never raise.

**Task 3 (De-mask + Verify):**
- Removed the `if "error" in data: assert ... == "UPSTREAM_ERROR"; return` early-out from both `test_health_facilities_hospital_field_presence` and `test_health_facilities_ltc_beds_and_zone`.
- Replaced with hard `assert "_meta" in data` so a live 400 fails the suite.
- Strengthened field-presence assertions: hospital now asserts `type` non-null; LTC now asserts `zone` non-null and `facility_name` non-null.
- LIVE run: both scenarios passed against `data.novascotia.ca` with real `_meta` envelope.

## Verification Results

- All 297 Nova Scotia unit tests pass.
- Full suite: 3032 passed, coverage 97.07% (≥95% gate passed).
- LIVE: `test_health_facilities_hospital_field_presence` PASSED — real hospitals with `facility_name`/`county`/`type` non-null.
- LIVE: `test_health_facilities_ltc_beds_and_zone` PASSED — real LTC facilities with `beds`/`zone`/`facility_name` non-null.
- Pyright clean on all touched files.
- NS-13 restored.

## Deviations from Plan

None — plan executed exactly as written.

## Deferred Items

**Cross-province UPSTREAM_ERROR early-out audit (out of scope for this gap closure):**

Other provinces' integration scenarios (e.g. Manitoba, Quebec, Saskatchewan, Alberta) likely contain the same `if error.code == "UPSTREAM_ERROR": return` early-out that masked this NS bug. This is a known mock-vs-real masking pattern (same class as Manitoba Phase 18). Flag for a future cross-module integration-test audit — OUT OF SCOPE for this gap closure.

The deferred audit file: `.planning/debug/ns-health-facilities-400.md` documents the systemic lesson under "at_risk_tools_for_planner".

## Commits

| Task | Commit | Message |
|------|--------|---------|
| 1 (RED) | `5705597` | `test(20-08): RED — real raw Socrata schema fixtures + per-dataset SoQL assertion tests` |
| 2 (GREEN) | `a1467a2` | `feat(20-08): GREEN — per-dataset SoQL constants + branched fetch_health_facilities with normalization` |
| 3 (De-mask + Verify) | `092b6da` | `fix(20-08): remove UPSTREAM_ERROR escape-hatch from NS health integration scenarios` |

## Self-Check: PASSED

All key files exist, all 3 commits found, HOSPITAL_SELECT/LTC_SELECT/HOSPITAL_ORDER/LTC_ORDER constants present in constants.py.
