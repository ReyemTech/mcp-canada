---
status: resolved
trigger: "ns_get_health_facilities returns HTTP 400 (UPSTREAM_ERROR) live for both facility_type values (hospital, long_term_care)"
created: 2026-06-15T00:00:00Z
updated: 2026-06-15T00:00:00Z
goal: find_root_cause_only
---

## Current Focus

hypothesis: CONFIRMED — fetch_health_facilities builds its $select (and $order, and county filter) from assumed/normalized field names that do not exist on either raw Socrata dataset. Both dispatch paths 400.
test: Live curl against data.novascotia.ca /resource/{id}.json with current vs. proposed SoQL params.
expecting: current params → 400 (no-such-column); per-dataset corrected params → 200.
next_action: hand diagnosis to planner for a gap-closure plan (FIX SCOPE = health facilities only). Do NOT fix here.

## Symptoms

expected: ns_get_health_facilities(facility_type="hospital") and (facility_type="long_term_care") each return a _meta envelope with a non-empty facilities list (facility_name/county/type for hospitals; beds/zone for LTC).
actual: BOTH return {"error":{"code":"UPSTREAM_ERROR",...}} — upstream Socrata responds HTTP 400 "query.soql.no-such-column".
errors:
  - hospital: `No such column: facility_name` (HTTP 400)
  - long_term_care: `No such column: county` (HTTP 400)
reproduction:
  - call_tool("ns_get_health_facilities", {"facility_type":"hospital","limit":5})
  - call_tool("ns_get_health_facilities", {"facility_type":"long_term_care","limit":10})
started: shipped broken (latent since Plan 05 implementation). Live-confirmed 2026-06-15.

## Eliminated

- hypothesis: dataset IDs are wrong.
  evidence: tmfr-3h8a and x76a-axw2 both return 200 with default (no-$select) query; IDs are correct.
  timestamp: 2026-06-15
- hypothesis: shared/socrata.query_dataset mishandles $select pass-through.
  evidence: query_dataset forwards $select verbatim; the same function works for all 9 other NS curated tools (all live-200). The fault is the wrong column names supplied by the caller.
  timestamp: 2026-06-15

## Evidence

- timestamp: 2026-06-15
  checked: live raw schema of hospital dataset (GET /resource/tmfr-3h8a.json?$limit=2)
  found: real columns = facility, address, town, county, type, the_geom (the_geom is a Point geometry). NO facility_name, NO x_coordinate, NO y_coordinate.
  implication: hospital $select "facility_name,...,x_coordinate,y_coordinate" references 3 non-existent columns → 400.

- timestamp: 2026-06-15
  checked: live raw schema of LTC dataset (GET /resource/x76a-axw2.json?$limit=1)
  found: real columns = facility_id, facility_name, address, town, postal_code, facility_type, zone, nursing_homes_nh_no_of_beds, nursing_homes_nh_no_of_respite_beds, residential_care_facilities_rcf_no_of_beds, rcf_respite_beds, single_entry_access_sea_participating, x_coordinate, y_coordinate, location, the_geom. NO county, NO type.
  implication: LTC $select references county (missing) → 400. NOTE: the bug report said LTC also lacks zone — that is WRONG; LTC DOES have a `zone` column ("Northern", "Central", ...). LTC's missing columns are `county` and `type`.

- timestamp: 2026-06-15
  checked: current code $select strings, executed live.
  found:
    - hospital current `facility_name,address,town,county,type,x_coordinate,y_coordinate` → 400 (No such column: facility_name)
    - LTC current `facility_name,address,town,county,zone,nursing_homes_nh_no_of_beds,x_coordinate,y_coordinate` → 400 (No such column: county)
  implication: root cause confirmed for both paths.

- timestamp: 2026-06-15
  checked: $order and county-filter on LTC path (the second + third compounding failures).
  found: $order="county ASC" → 400 on LTC (no county column); $where="county='Halifax'" → 400 on LTC (no county column). Both are unconditionally applied in fetch_health_facilities.
  implication: the LTC path is broken in THREE places (select, order, where), not just $select. The hospital path's $order="county ASC" is fine (hospital HAS county).

- timestamp: 2026-06-15
  checked: proposed per-dataset SoQL, executed live.
  found:
    - hospital `$select=facility,address,town,county,type,the_geom` + `$order=county ASC` → 200
    - LTC `$select=facility_name,address,town,postal_code,facility_type,zone,nursing_homes_nh_no_of_beds,residential_care_facilities_rcf_no_of_beds,single_entry_access_sea_participating,x_coordinate,y_coordinate` + `$order=town ASC` → 200
  implication: per-dataset $select + per-dataset $order + per-dataset county handling fixes both paths.

- timestamp: 2026-06-15
  checked: hospital the_geom shape for lat/long derivation.
  found: the_geom = {"type":"Point","coordinates":[lon, lat]} e.g. [-60.1741, 46.1130]. GeoJSON order is [longitude, latitude].
  implication: hospital x_coordinate/y_coordinate (currently null) can be derived from the_geom.coordinates[0]/[1] post-fetch; then the_geom is stripped from output (Pitfall 5).

- timestamp: 2026-06-15
  checked: blast radius — live $select validation of all 9 OTHER curated NS tools.
  found: marine_leases, landbased, hatchery, production, water_quality, boil_water, protected_areas, air_quality, vital_statistics — ALL return 200 with their current $select.
  implication: health facilities is the ONLY broken NS tool. No other NS tool needs a fix.

## Resolution

root_cause: |
  fetch_health_facilities (src/mcp_canada/modules/nova_scotia/client.py) dispatches to two
  datasets with INCOMPATIBLE raw Socrata schemas but builds SoQL from a single set of
  assumed/normalized field names that exist on NEITHER raw dataset:
    - Hospital (tmfr-3h8a) raw cols: facility, address, town, county, type, the_geom.
      Current $select references facility_name + x_coordinate + y_coordinate → none exist → 400.
    - LTC (x76a-axw2) raw cols: facility_name, address, town, postal_code, facility_type, zone,
      nursing_homes_nh_no_of_beds, ..., x_coordinate, y_coordinate, the_geom (NO county, NO type).
      Current $select references county → does not exist → 400. PLUS $order="county ASC" and the
      county= filter also reference the missing county column → both 400 on the LTC path.
  The normalization that should map each raw schema to the common output shape
  (facility_name, address, town, county, type, zone, beds, x_coordinate, y_coordinate,
  facility_category) is applied AFTER fetch using normalized keys, but the FETCH itself uses
  normalized keys in $select — so the request dies upstream before any row is returned.

  Why tests missed it (the mock-vs-real gap — same class as Manitoba Phase 18):
    - conftest fixtures SAMPLE_HOSPITALS_ROWS / SAMPLE_LTC_ROWS use the POST-NORMALIZATION shape
      (hospital rows already have facility_name/x_coordinate/y_coordinate; LTC rows already have
      county/zone/beds). Unit tests patch socrata.query_dataset to RETURN these fixtures, so the
      wrong $select string is never validated against a real schema.
    - test_tools.py patches fetch_health_facilities entirely (returns canned HOSPITALS_DATA/LTC_DATA),
      so the client's SoQL is never exercised.
    - The integration test (tests/integration/test_tool_scenarios.py
      test_health_facilities_hospital_field_presence / _ltc_beds_and_zone) DOES hit live, but it
      treats `error.code == "UPSTREAM_ERROR"` as an acceptable pass-through and `return`s early
      (lines ~2693-2695 and ~2719-2721). So the live 400 was swallowed as "acceptable" instead of
      failing the suite. The field-presence assertions are never reached on the 400 path.

fix: |
  FIX SCOPE = health facilities only. Per-dataset SoQL (select + order + filter) built from
  LIVE-CONFIRMED raw column names, then normalize to the common output shape AFTER fetch.

  --- constants.py (add per-dataset field config) ---
  Add explicit per-dataset raw $select + $order + county-support flags, e.g.:
    HOSPITAL_SELECT = "facility,address,town,county,type,the_geom"
    HOSPITAL_ORDER  = "county ASC"
    LTC_SELECT = ("facility_name,address,town,postal_code,facility_type,zone,"
                  "nursing_homes_nh_no_of_beds,residential_care_facilities_rcf_no_of_beds,"
                  "single_entry_access_sea_participating,x_coordinate,y_coordinate")
    LTC_ORDER  = "town ASC"   # LTC has NO county column — cannot order by county
  (Keep them as Final constants alongside DS_HOSPITALS / DS_LTC_RCF_FACILITIES.)

  --- client.py fetch_health_facilities ---
  1. Branch select/order/where per facility_type using the constants above (no shared $select).
  2. county filter:
       - hospital: county column exists → keep `county='{county}'`.
       - LTC: NO county column → either (a) reject county filter for LTC with a clear note, or
         (b) skip it. Do NOT send county='...' to LTC (it 400s). Recommend documenting in the
         tool docstring that county filtering is hospital-only (LTC has zone, not county).
  3. Post-fetch normalization to the common shape:
       HOSPITAL raw → common:
         facility_name = row["facility"]          (rename)
         address, town, county, type              (pass through)
         zone   = None                            (hospital has no zone)
         beds   = None                            (hospital has no beds)
         x_coordinate = the_geom.coordinates[0]   (longitude) — derive, else None
         y_coordinate = the_geom.coordinates[1]   (latitude)  — derive, else None
         facility_category = "hospital"
         (strip the_geom from output — Pitfall 5)
       LTC raw → common:
         facility_name, address, town             (pass through)
         county = None                            (LTC has no county; zone carries the region)
         type   = row["facility_type"]            (rename: "Nursing Home" / RCF etc.)
         zone   = row["zone"]                     (pass through)
         beds   = row["nursing_homes_nh_no_of_beds"]  (consider int/float coercion)
         x_coordinate, y_coordinate               (pass through, coerce to float)
         facility_category = "long_term_care"
  4. Coerce coordinate + beds strings to numbers (schema expects float beds is int|None,
     x/y float|None — confirm coercion; current code passes raw strings through).

  --- schemas.py ---
  NovaScotiaHealthFacility already covers the common shape (facility_name, address, town,
  county, type, zone, beds, x_coordinate, y_coordinate, facility_category). No new fields
  required. (Optionally relax beds to allow the "190.0" float string → int|None coercion.)

  --- conftest.py (the test-gap fix) ---
  Replace SAMPLE_HOSPITALS_ROWS and SAMPLE_LTC_ROWS with the REAL RAW Socrata shapes so unit
  tests exercise the correct $select/normalization:
    SAMPLE_HOSPITALS_ROWS_RAW: keys = facility, address, town, county, type, the_geom (Point).
    SAMPLE_LTC_ROWS_RAW: keys = facility_name, address, town, postal_code, facility_type, zone,
      nursing_homes_nh_no_of_beds, residential_care_facilities_rcf_no_of_beds,
      single_entry_access_sea_participating, x_coordinate, y_coordinate (+ the_geom optional).

  --- test_client.py (add health facility client tests — currently MISSING) ---
  There is NO TestNsGetHealthFacilities client-level class. Add one that, with socrata patched:
    - asserts hospital $select == HOSPITAL_SELECT and does NOT contain facility_name/x_coordinate.
    - asserts LTC $select == LTC_SELECT and does NOT contain `county`.
    - asserts $order is "county ASC" for hospital and NOT "county ASC" for LTC.
    - asserts county filter is applied for hospital and NOT sent for LTC.
    - feeds RAW fixtures through and asserts normalized output: hospital facility→facility_name,
      hospital x/y derived from the_geom, the_geom stripped; LTC type=facility_type, beds set,
      county=None.

  --- tests/integration/test_tool_scenarios.py ---
  Remove the `if error.code == UPSTREAM_ERROR: return` early-out for BOTH NS health facility
  scenarios so a live 400 FAILS the suite (it currently masks exactly this bug). Keep the
  field-presence assertions (hospital: facility_name + county + type non-null; LTC: beds + zone
  present). This is what would have caught the ship.

verification: |
  Not applied (diagnose-only). Live evidence proves the fix direction:
    - hospital corrected SoQL → HTTP 200 (rows with facility/county/type/the_geom)
    - LTC corrected SoQL → HTTP 200 (rows with facility_name/zone/beds/x_coordinate/y_coordinate)
  After fix, both ns_get_health_facilities calls must return _meta + non-empty normalized
  facilities, and the de-masked integration tests must pass against live.

files_changed: []   # diagnose-only; planner will scope edits

blast_radius: |
  Isolated to ns_get_health_facilities (client.py fetch_health_facilities + its tests + the two
  integration scenarios). All 9 other curated Nova Scotia tools were live-validated 2026-06-15 —
  their $select strings return 200 and need no change. No cross-module impact.

at_risk_tools_for_planner: |
  None additional in Nova Scotia (all other NS $select live-200). The systemic lesson for the
  planner: any curated tool whose conftest fixture uses a POST-NORMALIZATION shape rather than
  the RAW portal schema, AND whose integration test treats UPSTREAM_ERROR as an acceptable
  pass-through, can ship a broken $select undetected. The de-masking of UPSTREAM_ERROR early-outs
  is worth auditing across other provinces' integration scenarios as a follow-up (out of scope
  for this fix).
