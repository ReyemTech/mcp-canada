---
status: complete
phase: 16-quebec-government-open-data
source:
  - 16-01-SUMMARY.md
  - 16-02-SUMMARY.md
  - 16-03-SUMMARY.md
  - 16-04-SUMMARY.md
  - 16-05-SUMMARY.md
  - 16-06-SUMMARY.md
started: 2026-04-11T00:00:00Z
updated: 2026-04-11T00:00:00Z
gaps_resolved: 2026-04-11T00:00:00Z
retest_started: 2026-04-11T00:00:00Z
retest_completed: 2026-04-11T00:00:00Z
retest_scope: "Tests 8, 9, 11, 12 — post-16-05 gap closure re-verification"
retest2_started: 2026-04-11T00:00:00Z
retest2_completed: 2026-04-11T00:00:00Z
retest2_scope: "Tests 8, 9, 11 — post-16-06 gap closure re-verification (cycle 2)"
---

## Current Test

[retest 2 complete]

## Tests

### 1. Quebec module auto-registers (behind BM25)
expected: Server starts; `list_modules` shows `quebec`; no registration errors. (Direct tool listing correctly hides the 18 quebec_ tools behind BM25.)
result: pass

### 2. CKAN search returns Quebec datasets
expected: Call `quebec_search_datasets(q="santé")` — returns a list of Données Québec datasets (not empty). Each result has id/title/name/resources_count. `_meta.source.api` is `donnees-quebec` (or similar). The federated catalog (139 orgs) means results can include provincial ministries, Hydro-Québec, Montreal ARTM, and NGOs.
result: pass

### 3. Dataset details surface correct fields
expected: Call `quebec_get_dataset_details(package_id="feux-de-foret")` — returns the MFFP forest fires archive dataset with title, notes (primarily French), organization, tags, and resources list. Title is a plain French string (no `title_fr`/`title_en` or `title_translated` field exists on DQ).
result: pass

### 4. list_categories uses group_list (thematic groups, not tags)
expected: Call `quebec_list_categories()` — returns Données Québec's thematic groups with bilingual French titles and `package_count`, NOT 4,200 noisy tags. Uses `group_list` (DQ supports it; BC returns 403).
result: pass
notes: Live count is 12 groups (not 10 as RESEARCH.md claimed). Groups verified — Agriculture et alimentation, Économie et entreprises, Éducation et recherche, Environnement/ressources naturelles et énergie, Gouvernement et finances, Infrastructures, Loi/justice et sécurité publique, Politiques sociales, Santé, Société et culture, Tourisme/sports et loisirs, Transport. Research-doc drift flagged for fix.

### 5. Health installations via CKAN datastore
expected: Call `quebec_get_health_installations(instal_type="CLSC")` — returns CLSC installations from the MSSS datastore. The parameter name is `instal_type` (not `type_` or `type`). Each row has name, address, region, type flags.
result: pass
notes: Initial test script used wrong param name `type_` — tool signature is actually `instal_type: str | None = None`. Corrected call passed.

### 6. ER wait times (hourly datastore)
expected: Call `quebec_get_er_wait_times()` — returns current ER hourly situation for ~116 Quebec hospitals from MSSS datastore. Each row has hospital name, wait time, occupancy rate. `_meta.cached` uses short TTL (~1 hour) since data updates hourly.
result: pass
notes: _meta.cached surfaces cached:bool only (not TTL value) — TTL lives server-side in cached_fetch. Expected envelope shape; my test script was imprecise about what "shows short TTL" meant.

### 7. Bridge structures required-filter guard
expected: Call `quebec_get_bridge_structures()` with NO filters — returns an error envelope with `error.code == "INVALID_INPUT"` explaining that at least one of `route`, `municipality`, or `region` is required. Follows the BC water wells 130K-record guard pattern.
result: pass

### 8. Bridge structures with filter returns features
expected: Call `quebec_get_bridge_structures(route="A-20")` — returns bridge structures filtered to Autoroute 20 from the MTQ WFS CSV. Each has structure ID, name, municipality, coordinates. Not the guard error.
result: issue
retest: 2026-04-11
retest_result: issue
retest_reported: "Envelope well-formed with _meta.source.url=https://ws.mapserver.transports.gouv.qc.ca/swtq but data=[] — BadZipFile error is gone (parser fix worked) but route='A-20' filter returns zero rows. Either the CSV column holding route number has a different name than the client matcher expects, or the CSV payload for swtq is a layer-list doc (not the feature CSV), or the WFS request is missing a typename and returning the capabilities doc."
severity: major
notes: "Parser fix from 16-05 task 1 is confirmed working (no more BadZipFile exception propagation). Remaining issue is a DIFFERENT root cause: either the CSV column name mismatch in fetch_bridge_structures filter logic, or fetch_and_parse is parsing the wrong response (WFS capabilities doc instead of feature CSV because the URL is missing ?service=WFS&typename=...). Needs live curl of MTQ_BRIDGES_URL to inspect payload shape."

### 9. Road conditions (MTQ WFS CSV, active TTL)
expected: Call `quebec_get_road_conditions()` — returns current Quebec road condition data from the MTQ WFS CSV endpoint. Bilingual columns — EN vs FR descriptions selected by `lang` param. `_meta.cached` uses short TTL (active data). Graceful empty list if the WFS endpoint fails (research flagged low-confidence endpoint).
result: issue
retest: 2026-04-11
retest_result: issue
retest_reported: "CSV now parses and rows ARE returned (no more silent empty), but every field in every row is null: {segment_id: null, route_num: null, route_name: null, region: null, pavement_status: null, visibility: null, has_snow_presence: null, timestamp: null}. Column mapping in fetch_road_conditions doesn't match the real CSV column names."
severity: major
notes: "Parser fix + error propagation fix from 16-05 task 1 both confirmed working — rows flow through. Remaining issue is DIFFERENT root cause: the schema mapping layer (fetch_road_conditions transform) uses column names that don't exist in the live MTQ CSV. Fix: curl MTQ_ROAD_CONDITIONS_URL, inspect actual headers, align mapper. Same class of bug likely exists for bridges (Test 8 retest) and road_works/road_events."
retest2: 2026-04-11
retest2_result: pass
retest2_notes: "CONFIRMED FIXED — 16-06 commit 6979468. Live response: [{segment_id:3201, route_num:117, route_name:'route 117', region:'Abitibi-Témiscamingue', pavement_status:'Bare and Dry', visibility:'Good', has_snow_presence:'N', timestamp:'2026/04/11 05:02:04'}, ...]. All 8 fields populated. Bilingual lang=en param working (English description strings). QuebecRoadCondition Pydantic schema apparently uses int for segment_id/route_num — no int→str validation issue unlike QuebecBridgeStructure."
notes: Likely same root cause family as Test 8 (MTQ WFS CSV endpoints not being fetched/parsed correctly). Research flagged fetch_road_conditions as low-confidence — the graceful-empty path in _fetch masks the real failure. Test 8 surfaced the underlying "File is not a zip file" error when route filter path was hit; road_conditions swallows the exception and returns empty.

### 10. Air quality stations (RSQAQ datastore)
expected: Call `quebec_get_air_quality_stations(active_only=True)` — returns 245 Réseau de surveillance de la qualité de l'air du Québec (RSQAQ) monitoring stations, filtered to those with no `DATE_FERMETURE` (still active). Each has station name, municipality, coordinates.
result: pass

### 11. Electricity data (two-step CKAN → CSV)
expected: Call `quebec_get_electricity_data()` — two-step: first fetches Hydro-Québec dataset details, picks first CSV resource, then parses it via `fetch_and_parse`. Returns historical production/consumption rows. Note: this is NOT real-time outages (SOPFEU/outages data is not on Données Québec per research — replaced with historical data).
result: issue
retest: 2026-04-11
retest_result: issue
retest_reported: "{'error':{'code':'UPSTREAM_ERROR','message':'Error fetching electricity data: [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] ssl/tls alert handshake failure (_ssl.c:1081)','lang':'en'}}"
severity: major
notes: "XLSX matcher fix (16-05 task 2) + envelope source_url plumbing both confirmed working — the tool now reaches the actual XLSX fetch step instead of returning silent empty. Remaining issue is NEW (not covered by 16-05): the Hydro-Québec server (hydroquebec.com) rejects the TLS handshake with SSLV3_ALERT_HANDSHAKE_FAILURE. This is a server-side cipher/protocol mismatch. Options: (a) use the donneesquebec.ca-hosted mirror URL instead of the direct hydroquebec.com URL if the package has one, (b) pass a custom httpx SSLContext with broader cipher suites, (c) document this as a known upstream limitation. Needs investigation of alternate resource URLs in package_show response."
retest2: 2026-04-11
retest2_result: pass
retest2_notes: "CONFIRMED FIXED — 16-06 commit 23b7a33. TLS handshake succeeds against hydroquebec.com, XLSX parsed, rows contain real hourly production/consumption values (e.g. rang=1 mois=1 jour=1 heure=1 production_brute=21065.13 MWh). Scoped SECLEVEL=1 SSLContext works end-to-end. Minor data-quality observation (new minor issue, logged below): first row is the XLSX legend/formula row with rang=null and formula strings like '5=1-2+3+4' in cells — the parser should skip the first row. Not a blocker for the SSL fix verification but worth a follow-up cleanup."
notes: _meta.source.url points at package_show (step 1) rather than the CSV URL (step 2), suggesting either (a) the selected Hydro-Québec dataset has no CSV resource, (b) the CSV parse step failed silently, or (c) the code returns package_show source URL even after successful CSV parse. Needs diagnosis.

### 12. Discovery finds Quebec tools via BM25
expected: Call `discover_tools(query="Quebec hospitals health")` — returns Quebec tools in the top results (e.g. `quebec_get_health_installations`, `quebec_get_er_wait_times`, `quebec_explore_health` prompt). The 18 quebec_ tools are reachable through the BM25 discovery layer.
result: issue
retest: 2026-04-11
retest_result: pass
notes: "quebec_get_er_wait_times BM25 keywords are 'quebec, emergency, er, wait times, urgence, hospital, civieres, msss, real-time, stretchers, occupancy, temps attente' — missing the literal word 'health'. BM25 matches only 2/3 query tokens (quebec+hospital) versus 3/3 for quebec_get_health_installations. Fix: add 'health', 'medical', 'sante' to the keywords line. Trivial one-line fix in tools.py docstring. CONFIRMED FIXED 2026-04-11 post 16-05 commit 5c371cb — quebec_get_er_wait_times now in top-5 results."

### 13. quebec_explore_health prompt returns guided workflow
expected: Invoke the `quebec_explore_health` prompt — returns a multi-message conversation (user + assistant roles) walking through a Quebec health analysis workflow: installations → ER wait times → population by region. `lang="fr"` returns French content.
result: pass

### 14. docs://quebec/catalog-federation-quirks resource is readable
expected: Read the resource at URI `docs://quebec/catalog-federation-quirks` — returns a markdown document explaining the federated 139-org nature of Données Québec (mix of provincial ministries, Hydro-Québec, Montreal ARTM, NGOs) and the Montreal overlap caveat. Bilingual content. Zero-parameter resource — no input required.
result: pass

### 15. Bilingual error messages
expected: Call `quebec_get_bridge_structures(lang="fr")` with no filters — error envelope has `_meta.lang: "fr"` AND the error message is in French (e.g. contains "au moins un" or "requiert"). Uses the inline `lang == "fr"` ternary pattern from Phase 15 post-gap-closure (not `shared/i18n.py:t()`).
result: pass

### 16. Integration test suite passes
expected: Run `uv run pytest tests/integration/ -v -m integration --timeout=120 -k "Quebec or quebec"` — all `TestQuebecToolScenarios` (~9 scenarios) and `TestQuebecPromptsResources` (~3 scenarios) pass against the live Données Québec + MTQ WFS APIs.
result: pass
notes: Integration suite green. Tests 8/9/11 issues may not be exercised by the integration suite — integration tests for bridge structures, road conditions, and electricity data likely use tolerant assertions (e.g. structural checks, accepting empty lists) that mask the MTQ CSV fetch failures.

## Summary

total: 16
passed: 12
issues: 4
pending: 0
skipped: 0

retest_2026-04-11:
  scope: "Tests 8, 9, 11, 12 — post-16-05 gap closure"
  total: 4
  passed: 1    # Test 12 (BM25 keywords)
  issues: 3    # Tests 8, 9, 11 (new downstream root causes revealed by parser fix)
  status: "16-05 confirmed landed (parser/error-propagation/xlsx-matcher/BM25 all verified). Three NEW downstream issues remain, requiring a second gap-closure cycle (16-06)."

retest2_2026-04-11:
  scope: "Tests 8, 9, 11 — post-16-06 gap closure"
  total: 3
  passed: 2    # Tests 9 (snake_case mapper) and 11 (SSLContext)
  issues: 1    # Test 8 — Pydantic int→str coercion (NEW downstream issue exposed by WFS paging reaching rows)
  minor_issues: 1  # Test 11 — XLSX legend/formula row leak (new minor, data-quality, not blocking)
  status: "16-06 confirmed landed (WFS paging + route normalizer + snake_case mapper + SECLEVEL=1 SSLContext all working end-to-end). One major + one minor downstream issue remain, requiring a third gap-closure cycle (16-07)."

## Gaps

- truth: "quebec_get_bridge_structures returns bridge features when filtered by route"
  status: resolved
  reason: "User reported: UPSTREAM_ERROR 'MTQ WFS error: File is not a zip file' — fetch_and_parse is trying to unzip a non-zip response from the MTQ bridge structures endpoint"
  severity: major
  test: 8
  root_cause: "shared/parsers.py:fetch_and_parse detects file format from URL path suffix only (line 513: url.lower().split('?')[0]). MTQ WFS URLs put the format in the query string (?outputformat=csv); after stripping the query the path /swtq has no suffix and falls through to _parse_xlsx. openpyxl then raises zipfile.BadZipFile: File is not a zip file. Affects ALL 4 MTQ WFS tools (road_works and road_events are also silently broken — integration tests use tolerant or/or assertions)."
  artifacts:
    - path: "src/mcp_canada/shared/parsers.py:513"
      issue: "URL path-suffix-only format detection ignores ?outputformat=csv query hint; falls through to _parse_xlsx which raises BadZipFile on CSV bytes"
    - path: "src/mcp_canada/modules/quebec/client.py:624"
      issue: "fetch_bridge_structures calls fetch_and_parse(MTQ_BRIDGES_URL) — propagates the BadZipFile exception to tools.py:454 which wraps it as UPSTREAM_ERROR"
    - path: "src/mcp_canada/modules/quebec/client.py:552"
      issue: "fetch_road_works has the same bug (silently covered by tolerant integration test)"
    - path: "src/mcp_canada/modules/quebec/client.py:583"
      issue: "fetch_road_events has the same bug (silently covered by tolerant integration test)"
    - path: "src/mcp_canada/shared/__tests__/test_parsers.py"
      issue: "Parser routing tests only exercise URLs with path suffixes (example.com/data.csv, .xlsx). No test covers WFS-style query-param format hints."
    - path: "tests/integration/test_tool_scenarios.py:1662,1685"
      issue: "test_get_road_works_wfs_csv and test_get_bridge_structures_requires_filter use tolerant assertion '_meta in data OR error in data' — error envelopes count as pass, masking the regression."
  missing:
    - "Enhance fetch_and_parse (shared/parsers.py) to detect format from query string (outputformat/format/f) in addition to URL path suffix"
    - "Add shared/__tests__/test_parsers.py test case for WFS-style URL with ?outputformat=csv and no .csv path suffix"
    - "Replace tolerant '_meta in data or error in data' integration assertions for MTQ tools with strict '_meta in data'"
  debug_session: ".planning/debug/quebec-mtq-csv-fetch-family.md"

- truth: "quebec_get_road_conditions returns current MTQ road condition rows"
  status: resolved
  reason: "User reported: envelope well-formed but data=[]. Graceful-empty path in _fetch masked the real failure — tool provides no value. Same root cause as Test 8: MTQ WFS CSV URL routed to _parse_xlsx which raises BadZipFile, then swallowed by try/except in fetch_road_conditions."
  severity: major
  test: 9
  root_cause: "Same primary root cause as Test 8 — shared/parsers.py:fetch_and_parse routing bug. The MTQ conditions_routieres WFS CSV endpoint is live and returns real CSV (confirmed via curl: 103KB, columns include DescriptionEtatChausseeFR/EN). The research doc was wrong to flag this endpoint as LOW confidence — it works. The silent-empty result is because fetch_road_conditions catches Exception at client.py:502-505 and returns [] on any parser failure, hiding the BadZipFile."
  artifacts:
    - path: "src/mcp_canada/modules/quebec/client.py:502-505"
      issue: "try/except Exception: return [] masks the real BadZipFile error raised by fetch_and_parse, making the tool appear healthy with data=[]"
    - path: "src/mcp_canada/shared/parsers.py:513"
      issue: "Same parser routing bug as Test 8 — strips ?outputFormat=csv before suffix check"
    - path: ".planning/phases/16-quebec-government-open-data/16-RESEARCH.md:216"
      issue: "Research assumption 'LOW confidence on WFS CSV' for ms:conditions_routieres is incorrect — the CSV endpoint works; the bug is client-side parser dispatch. Remove the low-confidence flag after fix."
  missing:
    - "Fix shared/parsers.py routing (same single-root-cause fix as Test 8)"
    - "After fix, either remove the try/except graceful-empty path in fetch_road_conditions OR keep it as true seasonal fallback (winter-only data) but add logging so parser errors are surfaced"
    - "Add integration test test_get_road_conditions_live asserting either non-empty data OR a documented off-season empty state (not a silent exception)"
    - "Update 16-RESEARCH.md Pitfall 7 / conditions_routieres notes to reflect that CSV works"
  debug_session: ".planning/debug/quebec-mtq-csv-fetch-family.md"

- truth: "quebec_get_electricity_data returns Hydro-Québec historical production/consumption rows"
  status: resolved
  reason: "User reported: envelope well-formed but data=[] and _meta.source.url points at package_show. DIFFERENT root cause from Tests 8/9 — Hydro-Québec package has zero CSV resources; all 4 resources are XLSX format. fetch_electricity_data matches only format=='CSV' so csv_url stays None and the function returns [] before fetch_and_parse is called. Envelope URL is hardcoded at package_show in the tool layer regardless of CSV parsing outcome."
  severity: major
  test: 11
  root_cause: "Two bugs in fetch_electricity_data + quebec_get_electricity_data: (1) client.py:754-757 hardcodes format matcher to 'CSV' only, but the Hydro-Québec 'historique-production-consommation' package publishes 4 XLSX files (years 2018-2021) — NO CSV resources exist. Verified live: package_show returns success=True with 4 resources, all format='XLSX'. (2) tools.py:614 hardcodes api_url=BASE_URL + 'package_show' in the envelope, so even a successful file fetch would report the wrong URL. Research doc assumed 'CSV available' without live verification."
  artifacts:
    - path: "src/mcp_canada/modules/quebec/client.py:754-757"
      issue: "Format matcher `(r.format or '').upper() == 'CSV'` returns no match because all 4 resources are XLSX. Function returns [] after successfully fetching package metadata."
    - path: "src/mcp_canada/modules/quebec/tools.py:614"
      issue: "api_url=BASE_URL + 'package_show' hardcoded in make_response — envelope URL stays at discovery endpoint regardless of whether any file was fetched"
    - path: ".planning/phases/16-quebec-government-open-data/16-RESEARCH.md:286"
      issue: "Research claimed 'CSV at Hydro-Québec direct URL (inside DQ package)' — WRONG. The package publishes XLSX files only. Verification step was skipped."
    - path: "src/mcp_canada/modules/quebec/__tests__/test_client.py::TestFetchElectricityData"
      issue: "Unit test mocks package_show response with a synthetic CSV resource, masking the real-world XLSX-only shape"
  missing:
    - "Rename csv_url→file_url and expand matcher to ('CSV', 'XLSX', 'XLS') in fetch_electricity_data"
    - "Skip empty-url resources (the 2020 entry has url='')"
    - "Have the client return the actual file URL so the tool envelope can reflect it (or document that package_show is the canonical discovery URL)"
    - "Add live integration test that calls quebec_get_electricity_data and asserts len(data['data']) > 0 OR a bilingual 'no parseable resource' error — not silent empty"
    - "Update 16-RESEARCH.md Hydro-Québec section to correct the 'CSV available' claim"
  debug_session: ".planning/debug/quebec-mtq-csv-fetch-family.md"

- truth: "quebec_get_er_wait_times is discoverable via BM25 search for Quebec health queries"
  status: resolved
  reason: "User reported: search for 'Quebec hospitals health' returned quebec_get_health_installations rank 1 but quebec_get_er_wait_times is not in the top 5. Keywords list missing the literal word 'health'."
  severity: minor
  test: 12
  root_cause: "tools.py:291 keywords line for quebec_get_er_wait_times lacks 'health'/'medical'/'sante'; BM25 is token-matching so queries with 'health' drop this tool out of top results."
  artifacts:
    - path: "src/mcp_canada/modules/quebec/tools.py:291"
      issue: "Keywords line missing health/medical/sante tokens"
  missing:
    - "Add 'health', 'medical', 'sante' to the Keywords line of quebec_get_er_wait_times"
  debug_session: ""
  resolved_by: "16-05 commit 5c371cb; confirmed by 2026-04-11 retest"

# ═══════════════════════════════════════════════════════════════════
# NEW GAPS from 2026-04-11 retest — post-16-05 downstream root causes
# ═══════════════════════════════════════════════════════════════════

- truth: "quebec_get_bridge_structures(route='A-20') returns non-empty bridge features"
  status: resolved
  resolved_by: "16-06 commit 970a93a — WFS paging loop + _normalize_route helper (paging + normalization confirmed working 2026-04-11 retest 2; reveals schema type-coercion gap tracked as new entry below)"
  reason: "User reported: envelope well-formed with _meta.source.url=https://ws.mapserver.transports.gouv.qc.ca/swtq but data=[] — route filter returns zero rows"
  severity: major
  test: 8
  retest_of: 8
  discovered: 2026-04-11
  root_cause: |
    CONFIRMED 2026-04-11 (live curl investigation):
    TWO distinct issues:
    (1) WFS server default page cap: MTQ bridge WFS endpoint returns only 30 rows by default (maxFeatures
        server-side limit). Total dataset is 11,696 structures. Without count+startIndex paging, fetch_and_parse
        downloads only the first 30 records — Autoroute 20 structures don't appear until row 30+. Server
        IGNORES CQL_FILTER parameter entirely (tested: CQL_FILTER=num_route='00020' returns all 11,696 rows
        unfiltered). WFS 2.0 count+startIndex pagination works (verified: startIndex=30 returns next page
        including Autoroute 20 entries).
    (2) Route format mismatch: Live CSV stores num_route as zero-padded 5-digit codes: '00020' for Autoroute 20,
        '00132' for Route 132, etc. User-facing filter route='A-20' never matches '00020'. Fix needs a route
        normalizer: 'A-20' -> '00020', 'Route 132' -> '00132', or match on nom_route column (contains
        'Autoroute 20 Ouest'/'Autoroute 20 Est') rather than exact num_route match.
    Column names: CORRECT — fetch_bridge_structures uses r.get('num_route'), r.get('nom_muncp') etc. which
    all survive _normalize_key unchanged (already snake_case with underscores). The mapper is not the bug.
  artifacts:
    - path: "src/mcp_canada/modules/quebec/client.py:fetch_bridge_structures"
      issue: "Calls fetch_and_parse(MTQ_BRIDGES_URL) without count/startIndex — downloads only 30/11696 rows. Server CQL_FILTER unsupported. Post-parse filter on num_route uses user format 'A-20' which never matches WFS zero-padded code '00020'."
    - path: "src/mcp_canada/modules/quebec/constants.py:MTQ_BRIDGES_URL"
      issue: "URL has no count/startIndex — needs WFS paging params injected per-request, not hardcoded in constant"
  missing:
    - "Implement WFS paging in fetch_bridge_structures: loop with count=500+startIndex until no more rows, collecting all records before post-parse filtering"
    - "Add route normalizer: map user-friendly strings ('A-20', 'Route 132', '20') to WFS zero-padded num_route codes ('00020', '00132') OR switch to nom_route ILIKE match"
    - "Unit test: fixture CSV with BOM-stripped headers (nom_route, num_route, nom_muncp), verify A-20 filter returns only Autoroute 20 rows"
    - "Integration test test_bridges_route_filter_returns_rows: call quebec_get_bridge_structures(route='A-20') and assert len(data['data']) > 0"
  debug_session: ""

- truth: "quebec_get_road_conditions returns rows with populated fields (route/region/pavement/visibility/snow/timestamp)"
  status: resolved
  resolved_by: "16-06 commit 6979468 — mapper keys aligned to _normalize_key snake_case output"
  reason: "User reported: rows ARE returned (error propagation fix confirmed) but every field is null — {segment_id: null, route_num: null, route_name: null, region: null, pavement_status: null, visibility: null, has_snow_presence: null, timestamp: null}"
  severity: major
  test: 9
  retest_of: 9
  discovered: 2026-04-11
  root_cause: |
    CONFIRMED 2026-04-11 (live curl + _normalize_key analysis):
    The MTQ conditions_routieres CSV uses PascalCase column names (NumeroSegment, NumeroRoute, NomRoute,
    NomRegion, DescriptionEtatChausseeFR, DescriptionEtatChausseeEN, DescriptionVisibiliteFR,
    DescriptionVisibiliteEN, IndicateurPresenceLamesNeige, EnVigueurDepuis).
    fetch_and_parse routes to _parse_csv which applies _normalize_key to ALL column headers.
    _normalize_key lowercases and strips all non-alnum chars: 'NumeroSegment' -> 'numerosegment',
    'DescriptionEtatChausseeFR' -> 'descriptionetatchausseefr', 'EnVigueurDepuis' -> 'envigueurdepuis'.
    But fetch_road_conditions mapper uses the ORIGINAL PascalCase names:
      r.get('NumeroSegment') -> None  (key is 'numerosegment')
      r.get('NumeroRoute') -> None    (key is 'numeroroute')
      r.get('NomRoute') -> None       (key is 'nomroute')
      r.get('NomRegion') -> None      (key is 'nomregion')
      r.get('DescriptionEtatChausseeFR') -> None  (key is 'descriptionetatchausseefr')
      r.get('DateEtHeureCondition') -> None  (no such column; actual is 'EnVigueurDepuis' -> 'envigueurdepuis')
    Bridge columns (num_route, nom_muncp etc.) are already snake_case so _normalize_key preserves them —
    that's why bridge mapper works fine and road conditions mapper does not.
    The unit test fixture uses synthetic headers matching the ORIGINAL names, masking the mismatch.
  artifacts:
    - path: "src/mcp_canada/modules/quebec/client.py:fetch_road_conditions (lines ~502-516)"
      issue: "Mapper keys are PascalCase originals; after _parse_csv normalizes all headers to snake_case the lookups all return None. Also 'DateEtHeureCondition' key does not exist in live CSV (actual field is 'EnVigueurDepuis' -> normalized 'envigueurdepuis')."
    - path: "src/mcp_canada/modules/quebec/__tests__/test_client.py"
      issue: "Road conditions fixture CSV uses synthetic PascalCase headers that match the (wrong) mapper — test passes on fake data and masks the live failure."
  missing:
    - "Replace mapper keys with normalized snake_case equivalents: 'NumeroSegment'->'numerosegment', 'NumeroRoute'->'numeroroute', 'NomRoute'->'nomroute', 'NomRegion'->'nomregion', 'DescriptionEtatChausseeFR'->'descriptionetatchausseefr', 'DescriptionEtatChausseeEN'->'descriptionetatchausseeen', 'DescriptionVisibiliteFR'->'descriptionvisibilitefr', 'DescriptionVisibiliteEN'->'descriptionvisibiliteen', 'IndicateurPresenceLamesNeige'->'indicateurpresencelamesneige', 'EnVigueurDepuis' (timestamp, not 'DateEtHeureCondition') -> 'envigueurdepuis'"
    - "Update unit test fixture CSV to use the real live CSV header names so the test exercises the actual normalizer path"
    - "Integration test asserting non-null route/region/pavement_status on at least one row"
  debug_session: ""

- truth: "quebec_get_electricity_data returns non-empty Hydro-Québec historical rows"
  status: resolved
  resolved_by: "16-06 commit 23b7a33 — scoped SECLEVEL=1 SSLContext for hydroquebec.com"
  reason: "User reported: {'error':{'code':'UPSTREAM_ERROR','message':'Error fetching electricity data: [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] ssl/tls alert handshake failure (_ssl.c:1081)','lang':'en'}}"
  severity: major
  test: 11
  retest_of: 11
  discovered: 2026-04-11
  root_cause: |
    CONFIRMED 2026-04-11 (live curl + uv run python SSL test):
    The Hydro-Québec XLSX URLs (e.g. https://www.hydroquebec.com/data/documents-donnees/xls/suivi-2021-de-l-entente-globale-cadre.xlsx)
    use TLSv1.2 with cipher AES128-GCM-SHA256, which curl handles fine but Python's ssl module with
    OpenSSL 3.x SECLEVEL=2 (the default) rejects as insufficiently secure.
    Confirmed fix: ssl.create_default_context() + ctx.set_ciphers('DEFAULT:@SECLEVEL=1') passed as
    verify=ctx to httpx.AsyncClient resolves the handshake and returns HTTP 200 with 3.05MB XLSX content.
    No donneesquebec.ca mirror exists for these files — all 4 resources point to hydroquebec.com directly
    (2020 resource has an empty URL and must be skipped).
    The fix MUST be scoped to fetch_and_parse callers for hydroquebec.com only — not a global ssl change in shared/http.py.
    Implementation path: add optional ssl_context parameter to fetch_and_parse, pass it through to httpx.AsyncClient.
    The fetch_electricity_data client function builds the SSLContext for hydroquebec.com URLs and passes it to fetch_and_parse.
  artifacts:
    - path: "src/mcp_canada/shared/parsers.py:fetch_and_parse"
      issue: "httpx.AsyncClient uses default SSL verify=True — no way to pass custom SSLContext. Needs optional ssl_context parameter."
    - path: "src/mcp_canada/modules/quebec/client.py:fetch_electricity_data"
      issue: "Does not build custom SSLContext for hydroquebec.com; relies on default httpx SSL config which fails with SECLEVEL=2."
  missing:
    - "Add ssl_context: ssl.SSLContext | None = None parameter to fetch_and_parse — passed as verify=ssl_context to httpx.AsyncClient when not None"
    - "In fetch_electricity_data: detect when file_url is from hydroquebec.com and build ssl.create_default_context() with set_ciphers('DEFAULT:@SECLEVEL=1') before calling fetch_and_parse"
    - "Unit test: mock fetch_and_parse to assert ssl_context is passed when url is hydroquebec.com"
    - "Integration test asserting either len(data['data']) > 0 OR a structured UPSTREAM_ERROR (not a silent empty)"
    - "Update shared/__tests__/test_parsers.py to cover ssl_context passthrough (mock httpx.AsyncClient and assert verify=ctx)"
  debug_session: ""

# ═══════════════════════════════════════════════════════════════════
# NEW GAPS from 2026-04-11 retest 2 — post-16-06 downstream root causes
# ═══════════════════════════════════════════════════════════════════

- truth: "quebec_get_bridge_structures(route='A-20') rows validate against QuebecBridgeStructure schema"
  status: failed
  reason: |
    User reported: "MTQ WFS error: 5 validation errors for QuebecBridgeStructure
    structure_id   Input should be a valid string [input_value=200645, input_type=int]
    dossier_num    Input should be a valid string [input_value=4116, input_type=int]
    municipality_code  Input should be a valid string [input_value=17010, input_type=int]
    route_num      Input should be a valid string [input_value=204, input_type=int]
    structure_type Input should be a valid string [input_value=1, input_type=int]"
  severity: major
  test: 8
  retest_of: 8
  discovered: 2026-04-11
  cycle: 3
  root_cause: |
    UNDIAGNOSED — hypothesis:
    WFS paging + route normalizer fixes from 16-06 are confirmed working (rows ARE now reaching
    the feature parser instead of 30-row empty page / missing features). The new failure is at the
    Pydantic validation layer: shared/parsers.py:_parse_csv auto-detects numeric-looking columns
    as int (probably via pandas inference or a cast step in the normalizer), but the
    QuebecBridgeStructure schema in quebec/schemas.py declares these fields as `str`. Pydantic v2
    does not coerce int→str by default and strict validation fails on every row.
    Five affected fields: structure_id, dossier_num, municipality_code, route_num, structure_type —
    all stored in the CSV as digit-only values like 200645, 4116, 17010, 204, 1.
    Note: route_num failure is interesting — it's the field we JUST added a zero-pad normalizer for.
    Either (a) the normalizer only runs for user-facing filter comparison and not for the outgoing
    schema value (so the row still carries 204 instead of '00204'), or (b) _parse_csv normalizes
    AFTER _normalize_route runs.
    Needs inspection of _parse_csv type-inference behavior and the QuebecBridgeStructure field types.
  artifacts:
    - path: "src/mcp_canada/modules/quebec/schemas.py:QuebecBridgeStructure"
      issue: "Fields structure_id, dossier_num, municipality_code, route_num, structure_type declared as str but _parse_csv returns them as int"
    - path: "src/mcp_canada/shared/parsers.py:_parse_csv"
      issue: "Numeric columns auto-inferred as int; no opt-in to keep everything as str"
  missing:
    - "Inspect _parse_csv to find where/how type inference happens"
    - "Decide fix: (a) change schema fields to `int | str` or `int`, (b) add field_validator with str coercion, or (c) stringify all values in _parse_csv or in fetch_bridge_structures mapper"
    - "Preferred: stringify numeric IDs in fetch_bridge_structures mapper with str(r.get(...)) — least invasive and honors the schema contract that these are ID codes (not numbers)"
    - "Replicate check for other Quebec schemas that declare `str` for numeric-looking ID fields — same bug may be latent elsewhere"
    - "Integration test: test_bridges_route_filter_returns_rows should now pass (rows + correct types)"
  debug_session: ""

- truth: "quebec_get_electricity_data skips the XLSX legend/formula row (first row)"
  status: failed
  reason: "Rows include a leading legend row with rang=null, mois=null, jour=null, heure=null and cells containing Excel formula strings like '5=1-2+3+4', '7=5-6', '9=7-8', '13=11x12'. These are the XLSX column formula definitions that document how derived columns are computed, not real data."
  severity: minor
  test: 11
  retest_of: 11
  discovered: 2026-04-11
  cycle: 3
  root_cause: |
    UNDIAGNOSED — hypothesis:
    The Hydro-Québec 'historique-production-consommation' XLSX files use the FIRST data row
    (after the header row) to document formulas for computed/derived columns. Real data starts
    at row 2. Either (a) pandas.read_excel picks up this legend row as regular data, or (b)
    _parse_xlsx doesn't skip it. A defensive filter: skip rows where all of rang/mois/jour/heure
    are null (the first 4 columns are indexing and should always be populated on real rows).
    Alternative: use `header=[0,1]` in pandas.read_excel to consume both the column name row
    AND the formula legend row as a multi-index header, then flatten.
  artifacts:
    - path: "src/mcp_canada/modules/quebec/client.py:fetch_electricity_data"
      issue: "After XLSX parse, returned rows include an XLSX legend/formula row that should be skipped (contains formula strings in numeric cells)"
    - path: "src/mcp_canada/shared/parsers.py:_parse_xlsx"
      issue: "Generic XLSX parser can't know about domain-specific legend rows; fix should be in the caller, not the shared parser"
  missing:
    - "Add a row filter in fetch_electricity_data: skip any row where rang is null OR the value of a known numeric column is a string containing '='"
    - "Document this XLSX quirk in a comment referencing the Hydro-Québec file shape"
    - "Integration test assertion: first row has rang == 1 (not null)"
  debug_session: ""
