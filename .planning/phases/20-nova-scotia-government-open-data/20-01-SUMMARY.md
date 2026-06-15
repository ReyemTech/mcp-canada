---
phase: 20-nova-scotia-government-open-data
plan: "01"
subsystem: shared-socrata-client + nova-scotia-module-scaffold
tags:
  - socrata
  - soda-api
  - shared-client
  - nova-scotia
  - wave-0
  - scaffold
dependency_graph:
  requires: []
  provides:
    - shared/socrata.py (4th portal client — reusable across all Socrata portals)
    - nova_scotia module skeleton (7-file pattern; Plans 02-06 fill bodies)
    - 20-SPIKE.md (3 shape verdicts + 2 confirmations)
  affects:
    - Phase 20 Plans 02-06 (all depend on shared/socrata.py + locked client signatures)
    - Future Socrata portals (PEI, NB, Fredericton — reuse shared/socrata.py)
tech_stack:
  added:
    - shared/socrata.py (new 4th portal client; httpx only, no new deps)
  patterns:
    - Socrata SODA API: /api/catalog/v1 discovery + /resource/{id}.json SoQL reads
    - httpx_client injection (same as arcgis_hub.py/ogc.py)
    - offset/$offset omitted at 0 (Pitfall 8)
    - X-App-Token header conditional on app_token (None by default)
    - _soql helper centralises acquire()+query_dataset() in module client
    - _normalize_zone_field handles AMI health_zone→zone + diabetes/COPD agegroup→age_group
key_files:
  created:
    - src/mcp_canada/shared/socrata.py
    - src/mcp_canada/shared/__tests__/test_socrata.py
    - src/mcp_canada/modules/nova_scotia/__init__.py
    - src/mcp_canada/modules/nova_scotia/constants.py
    - src/mcp_canada/modules/nova_scotia/schemas.py
    - src/mcp_canada/modules/nova_scotia/client.py
    - src/mcp_canada/modules/nova_scotia/tools.py
    - src/mcp_canada/modules/nova_scotia/prompts.py
    - src/mcp_canada/modules/nova_scotia/resources.py
    - src/mcp_canada/modules/nova_scotia/__tests__/__init__.py
    - src/mcp_canada/modules/nova_scotia/__tests__/conftest.py
    - src/mcp_canada/modules/nova_scotia/__tests__/test_client.py
    - src/mcp_canada/modules/nova_scotia/__tests__/test_tools.py
    - src/mcp_canada/modules/nova_scotia/__tests__/test_prompts_resources.py
    - .planning/phases/20-nova-scotia-government-open-data/20-SPIKE.md
  modified: []
decisions:
  - "shared/socrata.py is the 4th portal client (CKAN / ArcGIS Hub / OGC WFS / Socrata SODA); modeled structurally on arcgis_hub.py (httpx injection, parsed dicts returned, no cached_fetch/get_limiter inside)"
  - "offset and $offset omitted when 0 (Socrata Pitfall 8 from 20-RESEARCH.md) — confirmed in TestSharedSocrataContract"
  - "ACTIVE_ADVISORY_FILTER = 'date_advisory_removed IS NULL' (spike-confirmed: 82 active, empty-string = type-mismatch error on date column)"
  - "AMI chronic disease dataset (24qf-ntke) uses 'health_zone' field and has no 'sex' field — normalized in _normalize_zone_field"
  - "Hypertension dataset (sztc-sewr) uses 'hypertension_count' + 'prevalence_rate' (not standard 'prevalence'/'crude_prevalence_rate'); NovaScotiaChronicDiseaseRow uses nullable fields for schema differences"
  - "Rockweed leases (exhe-htib) has 3 tabular fields (ownership/lease_le/hectares) but no county/species/location — no curated tool; DS_ROCKWEED_LEASES in constants for discovery-only"
  - "RATE_LIMIT = 2.0 (conservative; keyless Socrata ~1 req/sec per IP without token)"
metrics:
  duration: "11 minutes"
  completed_date: "2026-06-15"
  tasks_completed: 3
  files_created: 15
---

# Phase 20 Plan 01: Nova Scotia Wave 0 Scaffold Summary

Socrata SODA client (4th portal technology) + nova_scotia module foundation + spike verdicts locked.

## What Was Built

### Task 1: shared/socrata.py (RED→GREEN)

Built the 4th portal client modeled on `shared/arcgis_hub.py`. Public surface:

| Function | Endpoint | Returns |
|----------|---------|---------|
| `search_catalog(domain, q, limit, offset, only, *, app_token, httpx_client)` | `/api/catalog/v1` | `dict` (raw catalog JSON) |
| `get_dataset_metadata(domain, dataset_id, *, app_token, httpx_client)` | `/api/views/{id}.json` | `dict` (flat metadata) |
| `query_dataset(domain, dataset_id, where, select, order, limit, offset, q, group, *, app_token, httpx_client)` | `/resource/{id}.json` | `list[dict]` (flat rows) |
| `shape_catalog_result(result)` | — | `dict` (flat catalog entry) |

**Param-omission rules (pinned by TestSharedSocrataContract):**
- `offset` omitted from catalog params when `offset == 0` (Socrata default; cleaner requests)
- `$offset` omitted from SoQL params when `offset == 0` (same rule for resource endpoint)
- `$where`, `$select`, `$order`, `$q`, `$group` omitted when not provided (never send `None` values)
- `X-App-Token` header added only when `app_token` is set (keyless default)

**23 tests, all green.** TestSharedSocrataContract has 8 tests pinning the outgoing params dict (the Manitoba/Saskatchewan lesson). 127 shared suite tests, 0 regressions.

**Constants:** `DEFAULT_TIMEOUT=30.0`, `MAX_DESCRIPTION_CHARS=500`, `CATALOG_PATH`, `RESOURCE_PATH`, `VIEWS_PATH`.

**No new dependencies.** httpx only (already in project).

### Task 2: Wave 0 Spike (20-SPIKE.md)

Live probes against data.novascotia.ca (keyless, 2026-06-15). All 5 items resolved:

**1. Rockweed leases `exhe-htib`**
- Verdict: **has 3 tabular fields** (ownership, lease_le, hectares). Not geometry-only.
- Decision: No curated tool (thin schema); `DS_ROCKWEED_LEASES` in constants for discovery-only via `ns_search_datasets`/`ns_query_dataset`.

**2. Boil-water active filter**
- `ACTIVE_ADVISORY_FILTER = "date_advisory_removed IS NULL"` — confirmed by live count: 82 active advisories.
- Empty-string comparison (`= ''`) causes `query.soql.type-mismatch` on the date column — not a valid filter.

**3. Chronic disease zone field map**

| Disease | zone field | age field | sex? | prevalence field | rate field |
|---------|-----------|-----------|------|----------------|-----------|
| AMI (24qf-ntke) | `health_zone` → normalize to `zone` | `age_group` | **ABSENT** | `prevalence` | `crude_prevalence_rate` |
| Diabetes (cumi-sw99) | `zone` | `agegroup` → normalize | sex present | `prevalence` | `crude_prevalence_rate` |
| COPD (ua9e-4pss) | `zone` | `agegroup` → normalize | sex present | `prevalence` | `crude_prevalence_rate` |
| Hypertension (sztc-sewr) | `zone` | `age_group` | sex present | `hypertension_count` | `prevalence_rate` |
| Asthma (2bih-5dgk) | `zone` | `age_group` | sex present | `prevalence` | `crude_prevalence_rate` |

**4. `categories=` param is broken** — returns `resultSetSize: 0`. Use `q=` + client-side `domain_category` filter. Confirmed.

**5. `$select` strips `the_geom`** — geometry absent when field not in `$select` list. Confirmed. All curated tools for geometry-enabled datasets must use explicit `$select`.

### Task 3: nova_scotia Module Scaffold (12 files)

7-file module pattern + test scaffolds. Module auto-registered by FileSystemProvider via `MODULE_NAME = "nova_scotia"`.

**`constants.py`:** All dataset IDs, `ACTIVE_ADVISORY_FILTER`, `CHRONIC_DISEASE_DATASETS` dispatch dict, `CHRONIC_DISEASE_ZONE_FIELD`/`CHRONIC_DISEASE_AGE_FIELD`/`CHRONIC_DISEASE_HAS_SEX` per-disease maps, `RATE_LIMIT=2.0`, `CACHE_KEY_PREFIX="nova_scotia:"`, `NS_APP_TOKEN_ENV="NS_APP_TOKEN"`, `MAX_RECORDS=5000`.

**`schemas.py`:** 15 flat Pydantic v2 models. `NovaScotiaChronicDiseaseRow` uses nullable fields to handle hypertension/AMI schema differences (not a discriminated union — simpler and downstream plans fill normalization).

**`client.py`:** `_soql` helper fully implemented (acquires rate limit token then calls `socrata.query_dataset`). `_normalize_zone_field` fully implemented (handles health_zone→zone, agegroup→age_group). 17 `NotImplementedError` stubs with locked signatures (Plans 02-05 fill bodies only).

**`tools.py`, `prompts.py`, `resources.py`:** Import skeletons with zero definitions (Plans 02-06 fill).

**`conftest.py`:** Complete fixture set:
- `SAMPLE_CATALOG_RESPONSE` (2 entries, resultSetSize=706)
- `SAMPLE_VIEWS_METADATA`
- Per-dataset row fixtures for all 4 aquaculture + 4 environment + 5 health datasets
- `SAMPLE_MARINE_LEASES_ROWS_WITH_GEOM` / `SAMPLE_PROTECTED_AREAS_ROWS_WITH_GEOM` (for geometry strip tests)
- `SAMPLE_BOIL_WATER_ROWS_EMPTY` (critical: empty list = valid, not error)
- `SAMPLE_CHRONIC_DISEASE_ROWS_AMI` (uses `health_zone`, no `sex`)
- `SAMPLE_CHRONIC_DISEASE_ROWS_DIABETES` (uses `zone`, `agegroup`)
- `SAMPLE_CHRONIC_DISEASE_ROWS_HYPERTENSION` (uses `hypertension_count`, `prevalence_rate`)
- Autouse `_clear_cache_and_limiter` fixture

**Test scaffolds:** `test_client.py` has 18 placeholder classes; `test_tools.py` has 18 placeholder classes; `test_prompts_resources.py` has 2 placeholder classes.

## Deviations from Plan

None — plan executed exactly as written.

One spike finding that EXPANDS the plan's documented understanding: hypertension dataset (`sztc-sewr`) has non-standard field names (`hypertension_count`, `prevalence_rate`) that differ from the other 4 disease datasets. The research doc mentioned `crude_prevalence_rate` for all 5 but the live probe revealed this difference. `NovaScotiaChronicDiseaseRow` in schemas.py now has nullable `hypertension_count` and `prevalence_rate` fields to accommodate this. `CHRONIC_DISEASE_HAS_SEX` dict added to constants (not in original plan spec but needed by Plan 05's sex-filter logic for AMI).

## Self-Check

- `src/mcp_canada/shared/socrata.py` — exists, imports cleanly
- `src/mcp_canada/shared/__tests__/test_socrata.py` — 23 tests, all pass
- `src/mcp_canada/modules/nova_scotia/__init__.py` — MODULE_NAME == 'nova_scotia'
- `src/mcp_canada/modules/nova_scotia/constants.py` — DS_MARINE_AQUACULTURE_LEASES == 'h57h-p9mm', CHRONIC_DISEASE_DATASETS['ami'] == '24qf-ntke', MAX_RECORDS == 5000
- `.planning/phases/20-nova-scotia-government-open-data/20-SPIKE.md` — contains exhe-htib, ACTIVE_ADVISORY_FILTER, health_zone, categories verdicts
- Shared test suite: 127 passed, 0 failed, 0 regressions
- pytest collection: no ImportError or syntax errors in nova_scotia __tests__/
