---
phase: 20-nova-scotia-government-open-data
plan: "05"
subsystem: nova-scotia-health-demographics-tools
tags:
  - socrata
  - soda-api
  - nova-scotia
  - health
  - demographics
  - dispatch
  - normalization
  - wave-4
dependency_graph:
  requires:
    - 20-01 (shared/socrata.py + module scaffold + _normalize_zone_field stub)
    - 20-04 (environment/air-quality client bodies)
  provides:
    - ns_get_health_facilities (facility_type dispatch: hospital + LTC)
    - ns_get_vital_statistics (county/year/rates)
    - ns_get_chronic_disease_prevalence (disease dispatch + zone normalization)
    - _normalize_zone_field fully implemented (health_zone→zone, agegroup→age_group)
  affects:
    - 20-06 (prompts/resources reference these 3 tools)
    - 17 ns_ tools total: 5 discovery + 12 curated
tech_stack:
  added: []
  patterns:
    - "Double-guard dispatch: tool INVALID_INPUT + client ValueError (mirrors Alberta ST3 / Saskatchewan mineral)"
    - "_normalize_zone_field: health_zone→zone (AMI), agegroup→age_group (diabetes/COPD), disease key injected"
    - "CHRONIC_DISEASE_HAS_SEX dict skips sex filter for AMI (no sex field in 24qf-ntke dataset)"
    - "year as TEXT column: $where=year='2020' string comparison (Pitfall 3)"
    - "counties field (not county) UPPERCASE in vital stats: $where=counties='ANNAPOLIS' (Pitfall 4)"
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/nova_scotia/client.py
    - src/mcp_canada/modules/nova_scotia/tools.py
    - src/mcp_canada/modules/nova_scotia/__tests__/test_client.py
    - src/mcp_canada/modules/nova_scotia/__tests__/test_tools.py
decisions:
  - "fetch_health_facilities normalizes both hospital and LTC rows to a common shape with facility_category set to the requested type; beds is None for hospitals (not in tmfr-3h8a schema)"
  - "Zone filter for chronic disease applied on SOURCE field name (health_zone for AMI, zone for others) before normalization; output always has zone"
  - "_normalize_zone_field accepts disease param for CHRONIC_DISEASE_ZONE_FIELD + CHRONIC_DISEASE_AGE_FIELD lookup (not the dataset-ID)"
  - "vital stats field is 'counties' (not 'county') matching the r794-fttm dataset schema"
metrics:
  duration: "6 minutes"
  completed_date: "2026-06-15"
  tasks_completed: 2
  files_modified: 4
---

# Phase 20 Plan 05: Nova Scotia Health & Demographics Tools Summary

3 curated tools (NS-13, NS-14, NS-17) + client bodies + _normalize_zone_field implementation + 60 new unit tests.

## What Was Built

### Task 1: 3 Health/Demographics Client Bodies (RED → GREEN)

Filled the 3 `NotImplementedError` stubs in `client.py`:

**`fetch_health_facilities(facility_type, county, limit)`**

| facility_type | Dataset | Dataset ID |
|--------------|---------|-----------|
| `"hospital"` | NS Hospitals | `tmfr-3h8a` |
| `"long_term_care"` | LTC / RCF Facilities | `x76a-axw2` |

Both normalized to a common shape:

```
facility_name, address, town, county, type, zone, beds, x_coordinate, y_coordinate, facility_category
```

- `type` = Regional/District/Community for hospitals; `None` for LTC
- `zone` = None for hospitals; Zone 1-4 for LTC
- `beds` = `nursing_homes_nh_no_of_beds` from x76a-axw2; `None` for hospitals
- `facility_category` = the requested `facility_type` string
- Invalid `facility_type` → `ValueError` (secondary guard)

**`fetch_vital_statistics(county, year, limit)`**

- Dataset: `r794-fttm` (NS Births and Deaths with Rates)
- `$select`: counties, year, population, live_births, birth_rate, deaths, death_rate, excess_of_births_over_deaths, natural_increase_rate
- `$order=year DESC`
- Pitfall 3: year is TEXT column → `year='2020'` (string comparison)
- Pitfall 4: county field is `counties` in UPPERCASE → `counties='ANNAPOLIS'`

**`fetch_chronic_disease(disease, health_zone, sex, year, limit)`**

| disease | Dataset ID | zone field | age field | has sex |
|---------|-----------|-----------|----------|--------|
| `ami` | `24qf-ntke` | `health_zone`→`zone` | `age_group` | NO |
| `diabetes` | `cumi-sw99` | `zone` | `agegroup`→`age_group` | YES |
| `copd` | `ua9e-4pss` | `zone` | `agegroup`→`age_group` | YES |
| `hypertension` | `sztc-sewr` | `zone` | `age_group` | YES |
| `asthma` | `2bih-5dgk` | `zone` | `age_group` | YES |

- Dispatches via `CHRONIC_DISEASE_DATASETS[disease]`
- `CHRONIC_DISEASE_HAS_SEX['ami'] = False` → sex filter skipped for AMI
- Applies `_normalize_zone_field(row, disease)` to every row
- Injects `"disease"` key into every row
- `$order=year ASC`
- Invalid disease → `ValueError` (secondary guard)

**`_normalize_zone_field(row, disease)`** (was a stub; now fully implemented):

- `health_zone` → `zone` (AMI only)
- `agegroup` → `age_group` (diabetes, COPD)
- `zone` and `age_group` pass through unchanged (hypertension, asthma)
- Always injects `"disease"` key
- Returns new dict (does not mutate input)

36 new client tests added; 126 total client tests green.

### Task 2: 3 Curated @tool Functions (RED → GREEN)

Added to `tools.py`:

**`ns_get_health_facilities`**
- Double-guard: tool pre-checks `facility_type in ["hospital", "long_term_care"]` → `INVALID_INPUT` with `valid=` list; client `ValueError` caught as secondary guard
- Dispatches `api_url` to the correct dataset (tmfr-3h8a or x76a-axw2) in `_meta.source.url`
- Bilingual error message via `lang == 'fr'` inline ternary

**`ns_get_vital_statistics`**
- Forwards `county`, `year`, `limit` to client
- `api_url` → `r794-fttm`
- Docstring documents UPPERCASE county + year-as-string conventions

**`ns_get_chronic_disease_prevalence`**
- Double-guard: tool pre-checks `disease in CHRONIC_DISEASE_DATASETS` → `INVALID_INPUT` with `valid=` list; client `ValueError` caught as secondary guard
- `api_url` dispatched to the specific disease dataset ID
- Bilingual error message via `lang == 'fr'` inline ternary
- Docstring explains the 5 diseases, missing sex for AMI, and zone normalization

24 new tool tests added; 86 total tool tests green; 212 total nova_scotia tests green.

## Final Tool Count

| Category | Count |
|---------|-------|
| Discovery tools (Plans 02) | 5 |
| Aquaculture curated tools (Plans 03) | 4 |
| Environment curated tools (Plans 04) | 4 (water quality, boil water, protected areas, air quality) |
| Health/Demographics curated tools (Plan 05) | 3 |
| **Total ns_ tools** | **17** |

17 tools (5 discovery + 12 curated) — within the mid-band 14-18 target.

## Deviations from Plan

None — plan executed exactly as written.

The plan mentioned the LTC source field for beds as `nursing_homes_nh_no_of_beds`; this was confirmed during implementation from the conftest fixture fixtures (SAMPLE_LTC_ROWS already had `beds` as a key). The client maps `nursing_homes_nh_no_of_beds` from the Socrata response to `beds` in the normalized output.

## Self-Check

- `src/mcp_canada/modules/nova_scotia/client.py` — 3 stubs replaced; `_normalize_zone_field` takes `disease` param
- `src/mcp_canada/modules/nova_scotia/tools.py` — `ns_get_health_facilities`, `ns_get_vital_statistics`, `ns_get_chronic_disease_prevalence` defined
- `uv run pytest src/mcp_canada/modules/nova_scotia/__tests__/` — 212 passed
- `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` — 97.05% coverage, 2947 passed
- `uv run python -c "from mcp_canada.modules.nova_scotia import tools; assert all(hasattr(tools,n) for n in ['ns_get_health_facilities','ns_get_vital_statistics','ns_get_chronic_disease_prevalence']); print('OK')"` — OK

## Self-Check: PASSED
