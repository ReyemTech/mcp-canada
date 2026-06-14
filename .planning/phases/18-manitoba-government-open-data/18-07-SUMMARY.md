---
phase: 18-manitoba-government-open-data
plan: "07"
subsystem: manitoba-prompts-resources
tags: [prompts, resources, bilingual, manitoba, arcgis-hub, flood, transport, agriculture, health]
dependency_graph:
  requires: [18-06]
  provides: [MB-18-prompts-resources]
  affects: [mcp-discovery, prompts-list, resources-list]
tech_stack:
  added: []
  patterns:
    - "6 @prompt functions (standalone from fastmcp.prompts) with manitoba_ prefix and lang param"
    - "7 @resource functions (standalone from fastmcp.resources) with ZERO parameters"
    - "Bilingual content inline in both JSON data:// and markdown docs:// resources"
    - "data:// resources return json.dumps(); docs:// and template:// return raw markdown"
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/manitoba/prompts.py
    - src/mcp_canada/modules/manitoba/resources.py
    - src/mcp_canada/modules/manitoba/__tests__/test_prompts_resources.py
decisions:
  - "Resources have ZERO function parameters — lang param would promote to ResourceTemplate and drop from resources/list (established Phase 40 pattern, confirmed Phase 17 Alberta)"
  - "manitoba_explore_transport guided workflow explicitly documents NOT_CONFIGURED return for missing MANITOBA_511_KEY — same key-gated pattern as Plan 06"
  - "data://manitoba/major-rivers includes Red River Floodway as a sixth entry (distinct from rivers but critical flood infrastructure reference)"
  - "docs://manitoba/flood-data-guide explicitly distinguishes HFC PDF bulletins (not machine-readable) from ArcGIS Hub layers (authoritative machine-readable) — critical agent guidance"
  - "docs://manitoba/portal-guide documents MLI retirement (2022-02-09) and data.manitoba.ca unreachability — prevents common pitfalls documented in 18-RESEARCH.md"
metrics:
  duration: "7 minutes"
  completed_date: "2026-06-14"
  tasks_completed: 2
  tasks_total: 2
  files_created: 0
  files_modified: 3
---

# Phase 18 Plan 07: Manitoba Prompts and Resources Summary

**One-liner:** 6 bilingual Manitoba prompts (flood/transport/agriculture-health guided workflows + 3 quick lookups) and 7 zero-parameter resources (departments/health-regions/major-rivers data catalogs + flood/portal guide docs + 2 templates), all auto-discovered by FileSystemProvider.

## What Was Built

### Prompts (prompts.py — 6 functions)

**Guided workflows (list[Message]):**

| Prompt | Tools Chained | Purpose |
|--------|--------------|---------|
| `manitoba_explore_flood_or_water` | `manitoba_get_flood_alerts` → `manitoba_get_river_stations` → `manitoba_get_provincial_waterways` | Flood situational awareness with Watch/Warning context and HFC PDF caveat |
| `manitoba_explore_transport` | `manitoba_get_road_events` → `manitoba_get_winter_road_conditions` → `manitoba_get_traffic_cameras` | 511 road network; explicitly documents NOT_CONFIGURED for missing API key |
| `manitoba_explore_agriculture_or_health` | `manitoba_get_drought_status` / `manitoba_get_livestock_prices` (Option A) → `manitoba_get_surgical_wait_times` / `manitoba_get_health_facilities` (Option B) | Branched agriculture OR health workflow |

**Quick lookups (str):**

| Prompt | Tool Referenced | Key Guidance |
|--------|----------------|-------------|
| `manitoba_quick_dataset_search` | `manitoba_search_datasets` | ArcGIS Hub API (NOT CKAN); links to data://manitoba/departments |
| `manitoba_check_road_conditions` | `manitoba_get_winter_road_conditions` | NOT_CONFIGURED key guidance; area_name filter examples |
| `manitoba_flood_outlook_now` | `manitoba_get_flood_alerts` | Watch/Warning/Advisory type table; HYDAT redirect for levels |

### Resources (resources.py — 7 functions)

**Catalog resources (data://):**

| URI | Content | Key Data |
|-----|---------|---------|
| `data://manitoba/departments` | 6 provincial ministries | name_en/name_fr + data_domains per ministry |
| `data://manitoba/health-regions` | 5 RHAs | WRHA/PMH/IERHA/SHSS/NHR with coverage + major_hospitals list |
| `data://manitoba/major-rivers` | 6 river entries | Red/Assiniboine/Winnipeg/Souris rivers + Red River Floodway + Lake Manitoba with flood_risk levels |

**Documentation guides (docs://):**

| URI | Content |
|-----|---------|
| `docs://manitoba/flood-data-guide` | ArcGIS Hub layers vs HFC PDFs distinction; HYDAT note; alert type table (Watch/Warning/Advisory); flood season context |
| `docs://manitoba/portal-guide` | geoportal.gov.mb.ca ArcGIS Hub structure; tool-to-use table; data.manitoba.ca unreachability; MLI retirement (2022-02-09); OpenMB licence permissions |

**Templates (template://):**

| URI | Key Placeholders |
|-----|-----------------|
| `template://manitoba/dataset-report` | `{search_query}`, `{dataset_title}`, `{resource_url}`, `{sample_data_table}` |
| `template://manitoba/flood-report` | `{report_date}`, `{alert_count}`, `{warning_count}`, river status table |

## Test Results

- **36 unit tests** (16 prompt + 20 resource) — all pass
- **192 total Manitoba module tests** — all pass
- **Coverage: 97.99%** (well above 95% threshold)
- TDD approach: tests written first (RED), then implementation (GREEN)

## Zero-Parameter Resource Compliance

All 7 resources verified as ZERO-parameter:
- `manitoba_departments()` — no params
- `manitoba_health_regions()` — no params
- `manitoba_major_rivers()` — no params
- `manitoba_flood_data_guide()` — no params
- `manitoba_portal_guide()` — no params
- `manitoba_dataset_report_template()` — no params
- `manitoba_flood_report_template()` — no params

No `lang` parameter on any resource (would promote to ResourceTemplate, remove from resources/list).

## Deviations from Plan

None — plan executed exactly as written.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1: 6 bilingual prompts | e967bc1 | 6 prompts + 36 tests written first (TDD) |
| Task 2: 7 zero-parameter resources | 84e6bda | 7 resources; all 36 tests GREEN; 97.99% coverage |

## Self-Check: PASSED

| Item | Status |
|------|--------|
| `src/mcp_canada/modules/manitoba/prompts.py` | FOUND |
| `src/mcp_canada/modules/manitoba/resources.py` | FOUND |
| `src/mcp_canada/modules/manitoba/__tests__/test_prompts_resources.py` | FOUND |
| `.planning/phases/18-manitoba-government-open-data/18-07-SUMMARY.md` | FOUND |
| Commit e967bc1 (Task 1: prompts) | FOUND |
| Commit 84e6bda (Task 2: resources) | FOUND |
| 192 tests pass, 97.99% coverage | VERIFIED |
