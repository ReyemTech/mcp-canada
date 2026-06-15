---
phase: 20-nova-scotia-government-open-data
plan: "06"
subsystem: nova-scotia-prompts-resources
tags: [nova-scotia, prompts, resources, socrata, bilingual, mcp-discovery]
dependency_graph:
  requires: [20-05]
  provides: [NS-18-prompts-resources]
  affects: [FileSystemProvider-prompts-list, FileSystemProvider-resources-list]
tech_stack:
  added: []
  patterns:
    - standalone @prompt from fastmcp.prompts (ns_ prefix, lang param, Annotated)
    - standalone @resource from fastmcp.resources (zero-parameter, type-prefixed URIs)
    - guided workflow prompts returning list[Message] with user + assistant roles
    - quick lookup prompts returning str with tool + param instructions
    - data:// resources returning json.dumps with bilingual content inline
    - docs:// resources returning raw markdown (bilingual sections inline)
    - template:// resources returning markdown with {placeholder} syntax
key_files:
  created: []
  modified:
    - src/mcp_canada/modules/nova_scotia/prompts.py
    - src/mcp_canada/modules/nova_scotia/resources.py
    - src/mcp_canada/modules/nova_scotia/__tests__/test_prompts_resources.py
decisions:
  - "@prompt count test uses __all__ (len==6) — @prompt decorator returns callable, not Prompt instance; inspect.getmembers with isinstance(obj, Prompt) finds 0"
  - "@resource count test uses __all__ (len==7) — same pattern; @resource decorator returns callable, not Resource instance"
  - "ns_socrata_guide placed in docs://ns/ not docs://socrata/ — module-prefixed URI keeps NS resources grouped; future Socrata portals (PEI, NB) will add their own module-prefixed guides that can cross-reference this canonical one"
  - "portal-guide omits air-quality-guide as separate resource — consolidated all air quality pattern into portal-guide (20+ per-station datasets pattern) to stay at 7 resources as planned"
metrics:
  duration: 8min
  completed_date: "2026-06-15"
  tasks: 2
  files: 3
---

# Phase 20 Plan 06: Nova Scotia Prompts and Resources Summary

6 bilingual prompts + 7 zero-parameter resources adding full MCP discoverability for Nova Scotia's Socrata SODA portal (first Socrata portal in mcp-canada).

## What Was Built

### 6 Bilingual Prompts (`src/mcp_canada/modules/nova_scotia/prompts.py`)

| Prompt | Type | Tools Chained |
|--------|------|---------------|
| `ns_explore_aquaculture_data` | Guided workflow (list[Message]) | ns_get_marine_aquaculture_leases → ns_get_landbased_aquaculture_licenses → ns_get_fish_hatchery_stocking → ns_get_aquaculture_production |
| `ns_health_zone_analysis` | Guided workflow (list[Message]) | ns_get_health_facilities(hospital) → ns_get_health_facilities(long_term_care) → ns_get_chronic_disease_prevalence → ns_get_vital_statistics |
| `ns_water_quality_analysis` | Guided workflow (list[Message]) | ns_get_air_quality_stations → ns_get_water_quality_monitoring → ns_get_boil_water_advisories |
| `ns_quick_find_dataset` | Quick lookup (str) | ns_search_datasets (categories= workaround, q= instead) |
| `ns_quick_protected_areas` | Quick lookup (str) | ns_get_protected_areas (status filter; geometry via ns_query_dataset) |
| `ns_quick_vital_stats` | Quick lookup (str) | ns_get_vital_statistics (UPPERCASE county + year-as-string pitfalls) |

### 7 Zero-Parameter Resources (`src/mcp_canada/modules/nova_scotia/resources.py`)

| URI | Type | Content |
|-----|------|---------|
| `data://ns/categories` | JSON | 26 NS Socrata domain categories with bilingual labels; categories= broken-param warning |
| `data://ns/health-zones` | JSON | 4 NS health zones (Western/Northern/Eastern/Central) with member counties and zone filter values |
| `data://ns/fishing-areas` | JSON | speciestyp values (Shellfish/Finfish/Marine Plant); hatchery stocks; county case note |
| `data://ns/departments` | JSON | 8 NS government departments publishing on data.novascotia.ca with related tools |
| `docs://ns/socrata-guide` | Markdown | Canonical SODA/SoQL how-to (FIRST Socrata portal): $where/$select/$order/$group/$limit/$offset with NS examples; categories= workaround; geometry control; X-App-Token |
| `docs://ns/portal-guide` | Markdown | Socrata as 4th portal technology; transport/511 deferred (HTML-only); novagis ArcGIS Hub deferred; air quality 20+ per-station pattern; NS Open Government Licence v1.1 |
| `template://ns/aquaculture-report` | Markdown template | Aquaculture sector analysis with {placeholder} fields for lease counts, production, employment |

### Zero-Parameter Compliance Verified

All 7 resources take ZERO function parameters. `lang` param is absent — adding it would promote functions to ResourceTemplate and drop them from `resources/list`. Bilingual content is embedded inline in JSON/markdown bodies.

### Socrata/SoQL Knowledge Location

The canonical Socrata SODA how-to lives at `docs://ns/socrata-guide`:
- All 7 SoQL parameters documented with NS-specific examples
- categories= broken-param workaround fully explained
- Geometry control via $select documented
- Rate limiting and X-App-Token slot documented

### Deferred Domain Documentation Location

Documented in `docs://ns/portal-guide`:
- Transport/511: HTML-only, no machine-readable feed, no NOT_CONFIGURED stubs
- NS ArcGIS Hub (novagis): no public no-auth FeatureServers confirmed, fully deferred
- Rockweed leases (exhe-htib): geometry-only, discovery-only via ns_query_dataset

## Test Results

- **42 tests** in TestNsPrompts (22) + TestNsResources (20): all pass
- **254 total** nova_scotia module tests: all pass
- **Coverage:** 97.07% (above the 95% requirement)
- **TDD:** Tests written first (RED), then implementation (GREEN)

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

- prompts.py: FOUND
- resources.py: FOUND
- test_prompts_resources.py: FOUND
- Commit 3cf77eb (Task 1 — 6 prompts): FOUND
- Commit f325833 (Task 2 — 7 resources): FOUND
