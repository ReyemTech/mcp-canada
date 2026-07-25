---
created: 2026-04-12T01:35:51.887Z
title: Research cross-Canada ER wait times datasets
area: research
files:
  - src/mcp_canada/modules/quebec/tools.py:283
  - src/mcp_canada/modules/quebec/client.py
  - src/mcp_canada/modules/british_columbia/tools.py:947
---

## Problem

Quebec's `quebec_get_er_wait_times` (Phase 16) exposes a rich, hourly, machine-readable ER occupancy dataset via the MSSS CKAN datastore. Per-hospital rows include:

- `establishment` — health authority (e.g. "CISSS du Bas-Saint-Laurent")
- `installation` — hospital name (e.g. "Centre hospitalier régional du Grand-Portage")
- `functional_stretchers` — total ER capacity
- `occupied_stretchers` — current occupancy
- `patients_over_24h` — patients waiting >24 hours
- `patients_over_48h` — patients waiting >48 hours
- `extraction_time` — snapshot time of day
- `last_updated` — ISO timestamp of last refresh

This is genuinely exceptional open data. Cross-Canada ER wait time comparison would be extremely valuable for:

- Health policy analysts
- Patient routing / triage decision support
- News/media reporting on health system strain
- Cross-provincial benchmarking
- Agent-driven public health queries

**Current state:** Only Quebec has this. Checked across all provincial modules via grep:

| Province | Current tool | What it returns |
|---|---|---|
| **Quebec** | `quebec_get_er_wait_times` | ✓ hourly MSSS feed with full occupancy stats |
| **BC** | `bc_get_emergency_rooms` | ✗ geographic locations + wheelchair accessibility only (BCGW WFS layer) |
| Ontario | — | None (Health Quality Ontario has web dashboards, not CKAN) |
| Alberta | — | None (AHS ahs.ca/waittimes is a web dashboard, not open data) |
| Manitoba, Saskatchewan, Maritimes, territories | — | None known |

**Updated 2026-07-25** — phases 17-20 shipped after this todo was filed and settled
several of the rows above:

| Province | Finding from the shipped phase |
|---|---|
| **Alberta** (Phase 17) | AHS has FeatureServers for hospitals/zones/EMS-PCN clinics, but **no** wait-time or occupancy layer. AB-16 explicitly records ER wait times as subsumed/deferred (Pitfall 9). |
| **Saskatchewan** (Phase 19) | Health **deferred** — SHA publishes no public ArcGIS FeatureServer at all. |
| **Nova Scotia** (Phase 20) | Socrata portal shipped with `ns_get_health_facilities`; no wait-time dataset surfaced during that phase. |

BC Phase 15 explicitly surfaced locations but not wait times — the BCGW layer `WHSE_IMAGERY_AND_BASE_MAPS.GSR_EMERGENCY_ROOMS_SV` doesn't include occupancy.

## Solution

**Phase 1: Research (low effort, high value)**

Research whether each of these provinces exposes an ER wait time / hospital occupancy feed on a machine-readable open data portal:

- Ontario — check data.ontario.ca CKAN for MOH/HQO/Ontario Health datasets; check Ontario Health Atlas API
- British Columbia — check catalogue.data.gov.bc.ca for Ministry of Health CKAN datasets beyond the WFS geographic layer
- Alberta — Phase 17 already swept open.alberta.ca and the AHSGIS FeatureServers
  without finding occupancy data; the remaining lead is a backing API behind
  ahs.ca/waittimes
- Manitoba — **NOT** data.manitoba.ca (unreachable, confirmed Phase 18). Use the
  geoportal.gov.mb.ca ArcGIS Hub (org `mMUesHYPkXjaFGfS`) instead
- Saskatchewan — **NOT** data.saskatchewan.ca (does not exist, confirmed Phase 19).
  Try geohub.saskatchewan.ca, though Phase 19 already found SHA has no public
  FeatureServer — likely a dead end
- Nova Scotia — data.novascotia.ca is **Socrata**, not CKAN (confirmed Phase 20);
  query via `/api/catalog/v1`, and note the `categories=` parameter is broken
- New Brunswick — check nbopendata.ca for Horizon/Vitalité
- Newfoundland and Labrador — check opendata.gov.nl.ca
- Prince Edward Island — check peiopendata.ca
- NWT/Yukon/Nunavut — likely no open feed

Return findings as a per-province table with: dataset name, URL, format (CSV/JSON/API), update frequency, row shape.

**Phase 2: Design (if ≥3 provinces have data)**

If research finds usable feeds for 3+ provinces, design a unified convention:

- Each province that has data gets a `{prefix}_get_er_wait_times` tool with a common return shape (establishment / installation / capacity / occupancy / overflow counts / timestamp)
- Add a meta-tool `compare_er_wait_times_canada` that fans out to all available provincial tools in parallel and returns a unified cross-provincial comparison
- Alternatively: surface as a prompt that guides agents through the cross-province workflow if a meta-tool is too heavy

**Phase 3: Implementation**

- Added as tasks in each province's existing module when their phase is implemented, OR
- Added as a decimal gap-closure phase to existing completed provincial modules (e.g. 15.1 BC ER wait times, 16.1 Quebec already has it)
- The `compare_er_wait_times_canada` meta-tool would live in `src/mcp_canada/meta/` or as a new `cross_canada/` module

**Phase 4: Prompts & Resources**

- `compare_er_wait_times_now` prompt — quick lookup
- `explore_canadian_er_strain` prompt — guided workflow comparing provinces
- `data://canada/er-wait-time-coverage` resource — catalog of which provinces have live data

**Not Phase 16 scope.** Phase 16 is "bring Quebec online". This is a cross-module enhancement for a future phase, either as its own dedicated phase or absorbed into each province's future phase scope.

## Context

Surfaced during Phase 16 UAT on 2026-04-11. User tested `quebec_get_er_wait_times()` and observed the richness of the data, then asked whether equivalent datasets exist across Canada. This todo captures the research trigger so it isn't lost when UAT closes.
