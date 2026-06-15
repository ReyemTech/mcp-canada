---
status: complete
phase: 20-nova-scotia-government-open-data
source: [20-01-SUMMARY.md, 20-02-SUMMARY.md, 20-03-SUMMARY.md, 20-04-SUMMARY.md, 20-05-SUMMARY.md, 20-06-SUMMARY.md, 20-07-SUMMARY.md]
started: 2026-06-15T00:00:00Z
updated: 2026-06-15T00:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. New Socrata portal tech + discovery works live
expected: ns_search_datasets returns live results from data.novascotia.ca (Socrata SODA), _meta.source.api="nova-scotia-socrata".
result: pass
note: Live — 10 results, api=nova-scotia-socrata. The 4th portal technology (shared/socrata.py) works live.

### 2. list_categories — broken categories= param workaround
expected: 20+ categories incl. "Fishing and Aquaculture" via q= + client-side domain_category workaround.
result: pass
note: Live — 30 categories, "Fishing" present. Workaround confirmed live.

### 3. Marine aquaculture leases (signature) + geometry exclusion
expected: non-null license_le/ownership/species/county; the_geom ABSENT.
result: pass
note: Live — 23 Inverness leases; license_le present; the_geom absent.

### 4. Fish hatchery stocking
expected: non-null stock/county/number_released/stocking_date.
result: pass
note: Live — 5 records; number_released + stocking_date present.

### 5. Boil-water advisories — active filter + empty=valid
expected: active_only uses date_advisory_removed IS NULL; empty result valid.
result: pass
note: Live — 5 active advisories, site_name present; no error.

### 6. Protected areas — geometry exclusion
expected: non-null pro_name/protect1/owner/status; the_geom ABSENT.
result: pass
note: Live — 5 areas; pro_name present; the_geom absent.

### 7. Health facilities dispatch + chronic disease zone normalization
expected: ns_get_health_facilities dispatches hospital vs long_term_care; chronic disease normalizes health_zone→zone, returns crude_prevalence_rate; invalid → INVALID_INPUT.
result: issue
reported: "ns_get_health_facilities returns HTTP 400 (UPSTREAM_ERROR) for BOTH valid facility types live. The shared $select uses normalized field names (facility_name, county, type, x_coordinate, y_coordinate) but the two datasets have incompatible raw schemas: hospital tmfr-3h8a has 'facility' (not facility_name), county, type, the_geom (no x/y); LTC x76a-axw2 has facility_name, facility_type, x/y but NO county and NO type. So the $select references non-existent columns → 400 for both. Chronic disease dispatch + zone normalization + INVALID_INPUT all work correctly."
severity: major

### 8. Vital statistics + air quality + water quality
expected: vital returns live_births; air returns station_name; water returns temperature_c.
result: pass
note: Live — vital live_births present; air station_name present; water temperature_c present.

### 9. Prompts & resources; Socrata guide; deferred transport documented
expected: 6 prompts + 7 zero-parameter resources; docs://ns/socrata-guide; portal-guide documents deferred transport.
result: pass
note: Live — 6 prompts, 7 resources, socrata-guide present.

### 10. French language pass-through
expected: lang="fr" → _meta.lang="fr" and French messages.
result: pass
note: Live — chronic disease invalid disease lang=fr returned "Maladie inconnue 'bogus'".

## Summary

total: 10
passed: 9
issues: 1
pending: 0
skipped: 0

## Gaps

- truth: "ns_get_health_facilities returns hospital and long-term-care facilities with facility name, county/type, and location for both valid facility_type values"
  status: failed
  reason: "User reported: ns_get_health_facilities returns HTTP 400 for BOTH valid facility types live. The shared $select uses normalized field names but the hospital dataset (tmfr-3h8a) uses raw column 'facility' + the_geom (no x/y), and the LTC dataset (x76a-axw2) has no county/type columns. The single shared $select references non-existent columns on each dataset → 400. Mocked unit tests + integration tests passed because the mock/fixture used the normalized shape, not the real raw Socrata schema."
  severity: major
  test: 7
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""
