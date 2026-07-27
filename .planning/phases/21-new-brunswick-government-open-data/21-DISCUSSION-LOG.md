# Phase 21 Discussion Log

**Date:** 2026-07-27
**Mode:** discuss (default, interactive)

## Areas presented
Discovery strategy · MapServer client · Domain coverage · Transport/511
— user selected **all four**.

## Decisions

| Area | Chosen | Note |
|---|---|---|
| Discovery | Federal CKAN (`organization:nb`) + GeoNB | recommended option |
| ArcGIS | Extend `shared/arcgis_hub.py` | recommended option |
| Domains | All four (54 of 62 services) | broadest of the options |
| Transport | `NOT_CONFIGURED` stubs | **diverges from recommendation** (defer) — user chose the Manitoba pattern so the capability is discoverable |
| Module size | Mid-band ~18-22 tools | asked as a follow-up once all four domains were selected |

## Live verification performed during discussion

Grounding the options rather than inheriting assumptions:

- `data.gnb.ca`, `opendata.gnb.ca`, `nbopendata.ca` — **all DNS failures**.
  CLAUDE.md's "future Socrata portals PEI/NB" note is **wrong for NB**.
- `geonb.snb.ca/arcgis/rest/services` — 200, ArcGIS Server 10.91, **62 services,
  all MapServer, zero FeatureServer**
- `GeoNB_DNR_Crown_Land/MapServer` — `capabilities: Map,Query,Data`; layer **3**
  (not 0) returns attributes
- `shared/arcgis_hub.py:query_feature_service` against that MapServer —
  **works unchanged**, 3 features returned
- GeoNB ArcGIS Hub — **401** `private org id ... not accessible`
- `open.canada.ca` `organization:nb` — **221 first-party GNB datasets**,
  CSV-heavy, with genuine FR/EN title pairs
- `511.gnb.ca/api/v2/get/event` — `Invalid Key`, so key-gated not absent

## Scope creep redirected
None raised. Four ideas captured under Deferred: CKAN datastore querying for NB
tabular data, NB municipal portals, GeoNB basemap/imagery services, and
verifying the PEI Socrata assumption independently in Phase 23.
