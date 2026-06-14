---
status: diagnosed
phase: 18-manitoba-government-open-data
source: [18-01-SUMMARY.md, 18-02-SUMMARY.md, 18-03-SUMMARY.md, 18-04-SUMMARY.md, 18-05-SUMMARY.md, 18-06-SUMMARY.md, 18-07-SUMMARY.md, 18-08-SUMMARY.md]
started: 2026-06-14T00:00:00Z
updated: 2026-06-14T00:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Module loads & tools are discoverable
expected: Server boots with the manitoba module auto-registered; discover_tools finds manitoba_* tools by natural-language query. 20 tools total.
result: pass

### 2. Search the Manitoba geoportal
expected: manitoba_search_datasets("parks") returns a flat results list + total from geoportal.gov.mb.ca (ArcGIS Hub). _meta.source.api = "manitoba-geoportal-hub".
result: issue
reported: "Live call returns UPSTREAM_ERROR / HTTP 400 Bad Request from https://geoportal.gov.mb.ca/api/search/v1/collections/all/items?q=parks&num=10&start=0 — also affects manitoba_list_organizations and manitoba_list_categories (same Hub Search API). Unit tests passed only because the Hub response was mocked."
severity: major

### 3. Provincial parks (bilingual)
expected: ~93 parks with bilingual names (NAME_E / NOM_F), optional park_type filter, _meta envelope.
result: pass
note: Live call returned count~93, api=manitoba-provincial-parks.

### 4. Flood alerts — empty is valid (off-season)
expected: overland flood watch/warning polygons; empty features list is a SUCCESS (not error) when no flooding active.
result: pass
note: Live call returned count~0 (empty), api=manitoba-flood-alerts — correct off-season behavior.

### 5. Drought status — Manitoba-scoped
expected: D0–D4 drought polygons filtered to Manitoba (server-side bbox), not the full continental layer.
result: pass
note: Live call returned count~4 Manitoba-scoped polygons, api=manitoba-drought-monitor.

### 6. Surgical wait times
expected: diagnostic/surgical wait averages with procedure + year + average-wait-days fields.
result: pass
note: Live call returned count~72, api=manitoba-surgical-wait-times.

### 7. Manitoba 511 without a key → NOT_CONFIGURED (graceful)
expected: manitoba_get_road_events returns structured make_error("NOT_CONFIGURED", ...) with registration URL — not an exception.
result: pass
note: Live call returned NOT_CONFIGURED with manitoba511.ca signup URL — graceful, no crash.

### 8. Prompts & resources discoverable
expected: 6 bilingual manitoba_ prompts (3 guided + 3 quick lookups) in prompts/list; 7 manitoba resources (data:// departments, health-regions, major-rivers; docs:// flood-data-guide, portal-guide; template:// dataset-report, flood-report) in resources/list with valid content.
result: pass
note: Live — 6 prompts + 7 resources all present; first resource content valid (1463 chars).

### 9. French language pass-through
expected: Calling any manitoba_ tool with lang="fr" returns _meta.lang = "fr" and French structural/error messages; data may remain source-language.
result: pass
note: Live — _meta.lang="fr"; 511 error returned in French ("Clé API Manitoba 511 non configurée...").

## Summary

total: 9
passed: 8
issues: 1
pending: 0
skipped: 0

## Gaps

- truth: "Discovery tools (manitoba_search_datasets, manitoba_get_dataset_details, manitoba_query_dataset, manitoba_list_organizations, manitoba_list_categories) return live results from the Manitoba geoportal ArcGIS Hub"
  status: failed
  reason: "User reported: Live call returns HTTP 400 Bad Request from https://geoportal.gov.mb.ca/api/search/v1/collections/all/items?q=parks&num=10&start=0. Confirmed across manitoba_search_datasets, manitoba_list_organizations, manitoba_list_categories. The 15 curated FeatureServer tools all work live; only the 5 Hub-Search-based discovery tools fail. Unit tests passed because the Hub response was mocked — the real endpoint/params are wrong."
  severity: major
  test: 2
  root_cause: "Discovery tools send ArcGIS-REST query params to an OGC API Records (Hub Search v1) endpoint. The host/path/flattening are correct — pure request-param bug: `num` must be `limit`; `start` must be `startindex` (1-based, omit when 0); empty `q=\"\"` is rejected and must be omitted. Live-confirmed on geoportal.gov.mb.ca 2026-06-14: `?q=parks&num=10&start=0`→400 vs `?q=parks&limit=10`→200. Tests masked it because test_client.py asserts only call_args[0][0] (URL), never the params dict. Affects 3 of 5 discovery tools; get_dataset_details (item endpoint) and query_dataset (FeatureServer path) are NOT affected."
  artifacts:
    - path: "src/mcp_canada/modules/manitoba/client.py"
      issue: "fetch_search_datasets / fetch_organizations / fetch_categories send num/start params and a blank q to the Hub Search OGC endpoint"
    - path: "src/mcp_canada/modules/manitoba/__tests__/test_client.py"
      issue: "TestSharedApiGetContract / discovery tests assert only the URL, never the outgoing params dict — so the wrong params went undetected"
  missing:
    - "In fetch_search_datasets/fetch_organizations/fetch_categories: map outgoing params num→limit, start→startindex (1-based; omit when 0), and omit q when empty. Keep the public num/start tool signature unchanged for API stability."
    - "Add request-param regression assertions (assert on call_args params dict, not just URL) so the contract is enforced — these would fail RED against current code."
    - "Optional: clarifying comment on HUB_SEARCH_URL in constants.py (URL itself is correct)."
  debug_session: ".planning/debug/manitoba-hub-search-400.md"
