---
phase: 20-nova-scotia-government-open-data
plan: "03"
subsystem: nova-scotia-fishing-aquaculture-tools
tags:
  - socrata
  - soda-api
  - nova-scotia
  - aquaculture
  - geometry-exclusion
  - wave-2
dependency_graph:
  requires:
    - shared/socrata.py (Plan 01)
    - nova_scotia module scaffold (Plan 01)
    - _soql helper + all client stubs (Plan 01)
    - discovery client bodies (Plan 02)
  provides:
    - fetch_marine_aquaculture_leases (with the_geom defensive strip)
    - fetch_landbased_aquaculture_licenses
    - fetch_fish_hatchery_stocking
    - fetch_aquaculture_production
    - ns_get_marine_aquaculture_leases (@tool)
    - ns_get_landbased_aquaculture_licenses (@tool)
    - ns_get_fish_hatchery_stocking (@tool)
    - ns_get_aquaculture_production (@tool)
  affects:
    - Plans 04-06 (parallel curated tool waves; no dependency on Plan 03 outputs)
    - Integration tests (Plan 06 wave)
tech_stack:
  added: []
  patterns:
    - Geometry exclusion via explicit $select + defensive row-level strip (belt-and-suspenders)
    - SoQL text-field quoting: speciestyp='Shellfish', county='Inverness', year='2020'
    - year-as-text pitfall: fetch_aquaculture_production uses year='YYYY' (quoted string)
    - Dual TTL pattern: CACHE_TTL_META (24h) for leases/licenses/hatchery; CACHE_TTL_ANNUAL (7d) for production
    - SoQL $where parts joined with AND; None when no filters
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/nova_scotia/client.py
    - src/mcp_canada/modules/nova_scotia/tools.py
    - src/mcp_canada/modules/nova_scotia/__tests__/test_client.py
    - src/mcp_canada/modules/nova_scotia/__tests__/test_tools.py
decisions:
  - "Defensive the_geom strip applied at both client layer (row comprehension) and tool layer — belt-and-suspenders; the $select exclusion is the primary mechanism, the strip handles any future API anomaly"
  - "fetch_marine_aquaculture_leases strips the_geom from returned rows even though $select excludes it — test fixture provides rows WITH the_geom to verify the strip works; this mirrors the production invariant (API returns rows without the_geom when $select excludes it)"
  - "CACHE_TTL_ANNUAL (7d) for aquaculture production — annual dataset, very low update frequency; leases/licenses/hatchery use CACHE_TTL_META (24h)"
  - "fetch_landbased_aquaculture_licenses uses $order=county ASC (mirrors marine leases) — no explicit ordering requirement in plan spec, county ASC chosen for consistent browsing"
metrics:
  duration: "5 minutes"
  completed_date: "2026-06-15"
  tasks_completed: 2
  files_created: 0
  files_modified: 4
---

# Phase 20 Plan 03: Nova Scotia Fishing/Aquaculture Tools Summary

4 curated fishing/aquaculture tools implementing Nova Scotia's signature data domain via Socrata SODA.

## What Was Built

### Task 1: 4 Fishing/Aquaculture Client Bodies (RED→GREEN)

Client functions in `client.py` filling the Plan 01 stubs:

| Function | Dataset | $select columns | $order | Filters |
|----------|---------|-----------------|--------|---------|
| `fetch_marine_aquaculture_leases` | `h57h-p9mm` | license_le,ownership,species,waterbody,county,sitestatus,speciestyp,hectares,lat_dms,long_dms | county ASC | county, speciestyp |
| `fetch_landbased_aquaculture_licenses` | `yqwg-f62a` | license_le,species,speciestyp,county,ownership,sitestatus,lat_dms,long_dms | county ASC | county, speciestyp |
| `fetch_fish_hatchery_stocking` | `8e4a-m6fw` | county,name,type,stock,stock_strain,hatchery,fish_length_cm,fish_weight_g,number_released,stocking_date,mark,growth_stage | stocking_date DESC | stock, county |
| `fetch_aquaculture_production` | `v2ex-ev63` | year,county,kgs,total_value,full_time,pt_employ_6_mth,pt_employ_6_mth_1,total_employ | year DESC | year (text), county |

**Geometry exclusion (marine leases):**
- Primary: `$select` list explicitly omits `the_geom` — the API returns no geometry field
- Belt-and-suspenders: client strips `the_geom` from returned rows with a dict comprehension
- 2 tests assert: (a) `the_geom` NOT in the outgoing `$select` string, (b) `the_geom` NOT in any returned row (even when mock returns rows WITH it)

**Year-as-text (production, Pitfall 3):**
- `fetch_aquaculture_production(year="2020")` builds `$where=year='2020'` (quoted string)
- Test fixture `SAMPLE_PRODUCTION_ROWS` has `"year": "2022"` (string, not integer) — matches actual API response
- Test asserts `year='2020'` in where string AND that unquoted `year=2020` does NOT appear

**SoQL $where building pattern:**
```python
where_parts = []
if county: where_parts.append(f"county='{county}'")
if species_type: where_parts.append(f"speciestyp='{species_type}'")
where = " AND ".join(where_parts) or None
```
- `None` when no filters → socrata.py omits `$where` param entirely (clean requests)
- Tests verify: single filter, combined AND, no-filter=None

**33 new client tests** all green. All 4 test classes verified:
- Returns dict with correct key (`leases`, `licenses`, `stocking_records`, `production`)
- `count` = `len(rows)`, `truncated` = `len(rows) >= limit`
- Correct dataset ID passed to `socrata.query_dataset`
- Filter strings correct and properly quoted
- `$order` correct per dataset

### Task 2: 4 Curated @tool Functions + Tool Tests (RED→GREEN)

4 `@tool` functions added to `tools.py`:

| Tool | Client function | api_url dataset ID |
|------|----------------|-------------------|
| `ns_get_marine_aquaculture_leases` | `fetch_marine_aquaculture_leases` | h57h-p9mm |
| `ns_get_landbased_aquaculture_licenses` | `fetch_landbased_aquaculture_licenses` | yqwg-f62a |
| `ns_get_fish_hatchery_stocking` | `fetch_fish_hatchery_stocking` | 8e4a-m6fw |
| `ns_get_aquaculture_production` | `fetch_aquaculture_production` | v2ex-ev63 |

All tools: standalone `@tool`, `lang: Literal["en", "fr"] = "en"`, `make_response`/`make_error`, `ns_` prefix, single-line `Use for:` + 8+ `Keywords:`.

**Docstring-documented quirks (where agents bite):**
- Marine leases: "geometry (the_geom MultiPolygon) is excluded; use ns_query_dataset + the_geom in $select for polygons"
- Production: "year is stored as a text field — use year as a string (e.g., year='2022')"
- Hatchery: "Records ordered newest-first; data current to 2025-11"

**22 new tool tests** all green. Per tool: envelope shape, geometry-exclusion assertion, param forwarding, error path (UPSTREAM_ERROR), lang passthrough, api_url contains dataset ID.

## $select Column Lists Used (Confirming the_geom Exclusion)

```
marine leases:   license_le,ownership,species,waterbody,county,sitestatus,speciestyp,hectares,lat_dms,long_dms
landbased:       license_le,species,speciestyp,county,ownership,sitestatus,lat_dms,long_dms
hatchery:        county,name,type,stock,stock_strain,hatchery,fish_length_cm,fish_weight_g,number_released,stocking_date,mark,growth_stage
production:      year,county,kgs,total_value,full_time,pt_employ_6_mth,pt_employ_6_mth_1,total_employ
```

`the_geom` does not appear in any of these lists. Marine leases additionally strips `the_geom` defensively at the row level.

## SoQL Filter/Quoting Rules

| Filter | Field | SoQL form | Pitfall |
|--------|-------|-----------|---------|
| county | `county` | `county='Inverness'` | Title case in stored data |
| species_type | `speciestyp` | `speciestyp='Shellfish'` | Field name is `speciestyp` (no 'e') |
| stock | `stock` | `stock='Brook Trout'` | Title case + spaces |
| year | `year` | `year='2020'` | TEXT field — quoted string (Pitfall 3) |
| Multiple | — | `field1='X' AND field2='Y'` | `or None` when empty |

## Verification

- `uv run pytest src/mcp_canada/modules/nova_scotia/__tests__/ -x` — 97 passed
- `python -c "from ... import tools; assert all(hasattr(tools,n) for n in [...]); print('OK')"` — OK
- `uv run pyright src/mcp_canada/modules/nova_scotia/` — 0 new errors (1 pre-existing in prompts.py stub)
- Project-wide coverage: 96.90% (above 95% threshold)

## Deviations from Plan

**Auto-fixed [Rule 1 - Bug] Defensive the_geom row strip added to fetch_marine_aquaculture_leases**
- **Found during:** Task 1 GREEN phase (test `test_returned_rows_have_no_the_geom`)
- **Issue:** The plan stated "Rows never contain the_geom" as a truth, but the client was relying solely on `$select` to exclude geometry. When the mock returned rows WITH `the_geom`, the client passed them through.
- **Fix:** Added `rows = [{k: v for k, v in row.items() if k != "the_geom"} for row in rows]` after the `_soql` call in `fetch_marine_aquaculture_leases`. Also applied at the tool layer as belt-and-suspenders.
- **Files modified:** client.py, tools.py
- **Commits:** 9a1ee00, 5a764ea

No other deviations — plan executed as written.

## Self-Check

- `src/mcp_canada/modules/nova_scotia/client.py` — 4 bodies implemented (no NotImplementedError for Plan 03 stubs)
- `src/mcp_canada/modules/nova_scotia/tools.py` — 4 @tool functions defined
- 97 tests pass, 0 failures
- Project-wide coverage: 96.90% (above 95% threshold)
- Commits: 9a1ee00 (client), 5a764ea (tools)

## Self-Check: PASSED
