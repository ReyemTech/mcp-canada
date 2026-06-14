---
status: diagnosed
trigger: "UAT: 5 Manitoba ArcGIS Hub discovery tools return HTTP 400 against live geoportal.gov.mb.ca"
created: 2026-06-14T00:00:00Z
updated: 2026-06-14T00:00:00Z
symptoms_prefilled: true
goal: find_root_cause_only
---

## Current Focus

hypothesis: CONFIRMED — wrong query params (num/start + empty q), NOT a wrong host
test: live curl probes of geoportal.gov.mb.ca with different param names
expecting: confirmed root cause + working request recipe
next_action: diagnosis complete; hand to planner for gap-closure plan

## Symptoms

expected: discovery tools return dataset records (search/list orgs/list categories) from the Manitoba geoportal
actual: HTTP 400 Bad Request -> UPSTREAM_ERROR for all Hub Search code-path tools
errors: 400 from https://geoportal.gov.mb.ca/api/search/v1/collections/all/items?q=parks&num=10&start=0
reproduction: call manitoba_search_datasets / manitoba_list_organizations / manitoba_list_categories live
started: never worked live (unit tests mocked the response so the bug was masked)

## Eliminated

- hypothesis: The HOST geoportal.gov.mb.ca is wrong; discovery must move to hub.arcgis.com or arcgis.com sharing REST
  evidence: geoportal.gov.mb.ca/api/search/v1/collections/all/items?q=parks&limit=10 returns HTTP 200 with 18 matching datasets (Manitoba Parks, etc). The host and the /collections/all/items path are CORRECT. hub.arcgis.com/api/search/v1/collections/all/items with the same params returns 400 (its all collection is not enabled). No host change needed.
  timestamp: 2026-06-14

- hypothesis: The response shape is wrong and _flatten_hub_feature / conftest fixtures need rewriting
  evidence: Live response is a GeoJSON FeatureCollection with top-level numberMatched/numberReturned/features, and each feature has id + properties.{title,snippet,type,owner,url,numViews,modified,categories}. This EXACTLY matches both _flatten_hub_feature() and the HUB_SEARCH_RAW conftest fixture. The flattening/parsing code is correct; only the request params are wrong.
  timestamp: 2026-06-14

## Evidence

- timestamp: 2026-06-14
  checked: curl geoportal.gov.mb.ca/api/search/v1/collections/all/items?q=parks&num=10&start=0 (current code params)
  found: HTTP 400 Bad Request — reproduces the UAT bug exactly
  implication: num/start are the offending params (ArcGIS-REST conventions, not OGC API Records)

- timestamp: 2026-06-14
  checked: same URL with ?q=parks&limit=10
  found: HTTP 200, numberMatched=18, 10 features returned
  implication: the OGC param is `limit` (page size), not `num`

- timestamp: 2026-06-14
  checked: pagination params on same endpoint — offset vs startindex
  found: ?limit=2&offset=2 -> HTTP 400 ; ?limit=2&startindex=2 -> HTTP 200 (different first id, confirms real paging). BUT ?startindex=0 -> empty/malformed body (numberReturned=None) on 3/3 runs; omitting startindex -> 200 with full page.
  implication: the OGC offset param is `startindex` and is 1-BASED. startindex=0 is invalid. Must OMIT startindex when offset==0 (and pass startindex>=1 otherwise), exactly like shared/arcgis_hub.search_hub_datasets omits offset when 0.

- timestamp: 2026-06-14
  checked: empty-query path used by fetch_organizations / fetch_categories (they pass {"q": "", "num": .., "start": 0})
  found: ?q=&limit=100 -> HTTP 400 (empty q value rejected). Omitting q entirely -> HTTP 200. With limit=50 (no q) the response yields owners (Manitoba_Government) and categories (/Categories/Agriculture, /Environment, /Health, /Transportation, ...).
  implication: fetch_organizations and fetch_categories fail for TWO reasons (num/start AND empty q). Fix must omit q when blank, and use limit. The category param the code uses ("categories") is harmless — ?categories=X -> 200 — so no change needed there, though it has no documented effect.

- timestamp: 2026-06-14
  checked: item-detail endpoint built by fetch_dataset_details — HUB_SEARCH_URL + "/" + item_id, i.e. /api/search/v1/collections/all/items/{id}
  found: HTTP 200; returns a single Feature dict with top-level properties + links (no "features" key). Matches the `"properties" in result` branch in fetch_dataset_details.
  implication: fetch_dataset_details' URL and response handling are CORRECT. It is only collaterally affected IF the planner consolidates _hub_get, but as written it does NOT use num/start/empty-q, so its live path likely already works. Verify during fix.

- timestamp: 2026-06-14
  checked: how unit tests masked the bug — src/mcp_canada/modules/manitoba/__tests__/test_client.py + conftest.py
  found: tests patch client.api_get with AsyncMock(return_value=HUB_SEARCH_RAW) and only assert call_args[0][0] == HUB_SEARCH_URL (the URL). They NEVER assert on call_args[0][1] (the params dict). The mock returns a valid response regardless of params, so num/start/empty-q were never exercised against contract.
  implication: add request-param assertions (regression tests) so the corrected params are pinned and the bug cannot silently return.

## Resolution

root_cause: |
  The 5 discovery tools send ArcGIS-REST query conventions to an OGC API Records
  (Hub Search v1) endpoint. fetch_search_datasets builds params {"q", "num", "start"};
  fetch_organizations/fetch_categories build {"q": "", "num", "start"}. The live
  endpoint https://geoportal.gov.mb.ca/api/search/v1/collections/all/items rejects:
    - `num`   (must be `limit`)              -> 400
    - `start` (must be `startindex`, 1-based)-> 400
    - empty `q=""`                            -> 400 (must omit q when blank)
  The HOST, the /collections/all/items path, the item-detail URL, the response
  flattening (_flatten_hub_feature), and the conftest fixtures are all CORRECT.
  This is a pure request-parameter bug. Tests masked it by mocking api_get and never
  asserting on the params dict.

fix: |
  ONE-LINE ESSENCE: replace num->limit, start->startindex (1-based, omit when 0),
  and omit q when empty, in the Manitoba Hub Search requests.

  constants.py: no change required (HUB_SEARCH_URL is correct). Optionally add a
  comment noting OGC params are limit/startindex.

  client.py — 3 functions (helper _hub_get and fetch_dataset_details are already fine):

    1) fetch_search_datasets(query, category, num, start, ...):
       Build params as:
         params = {"limit": min(max(num, 1), 100)}
         if query: params["q"] = query        # omit q when blank
         if start and start > 0: params["startindex"] = start  # 1-based; omit when 0
         if category: params["categories"] = category   # harmless; keep
       (Keep public signature num/start for API stability; only the outgoing param
        NAMES change. total still read from raw.get("numberMatched"); features from
        raw.get("features") — both confirmed present.)

    2) fetch_organizations(num, ...):
       Replace _hub_get({"q": "", "num": min(num,100), "start": 0})
       with     _hub_get({"limit": min(num, 100)})    # omit q, no startindex when 0

    3) fetch_categories(...):
       Replace _hub_get({"q": "", "num": 100, "start": 0})
       with     _hub_get({"limit": 100})              # omit q, no startindex when 0

  __tests__/conftest.py: fixtures (HUB_SEARCH_RAW / HUB_SEARCH_EMPTY) already match
  the REAL response shape — NO fixture change needed. The mocks were never wrong; the
  request params were.

  __tests__/test_client.py: add regression assertions that pin the corrected params,
  e.g. assert mock_api_get.call_args[0][1] == {"limit": 10, "q": "parks"} for a basic
  search; assert "num" not in params and "start" not in params and ("q" not in params
  or params["q"]) for fetch_organizations/fetch_categories; assert startindex omitted
  when start=0 and equals start when start>0. These would have caught the bug (RED).

verification: |
  Live probes (2026-06-14, geoportal.gov.mb.ca, UA mcp-canada/1.0):
    - ?q=parks&num=10&start=0          -> 400  (current/broken)
    - ?q=parks&limit=10                -> 200, numberMatched=18, 10 features (fixed search)
    - ?q=parks&limit=10&startindex=10  -> 200  (fixed pagination)
    - ?limit=50  (no q)                -> 200, owners + categories present (fixed orgs/categories)
    - ?q=&limit=100                    -> 400  (proves empty-q must be omitted)
    - ?limit=2&offset=2                -> 400 ; ?limit=2&startindex=2 -> 200 (proves startindex)
    - /collections/all/items/{id}      -> 200, single Feature dict (fetch_dataset_details OK)

files_changed:
  - src/mcp_canada/modules/manitoba/client.py  (fetch_search_datasets, fetch_organizations, fetch_categories — param names only)
  - src/mcp_canada/modules/manitoba/__tests__/test_client.py  (add request-param regression assertions)
  - src/mcp_canada/modules/manitoba/constants.py  (optional: clarifying comment only)
