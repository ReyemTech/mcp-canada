---
status: complete
phase: 16-quebec-government-open-data
source:
  - 16-01-SUMMARY.md
  - 16-02-SUMMARY.md
  - 16-03-SUMMARY.md
  - 16-04-SUMMARY.md
  - 16-05-SUMMARY.md
started: 2026-04-11T00:00:00Z
updated: 2026-04-11T00:00:00Z
gaps_resolved: 2026-04-11T00:00:00Z
retest_started: 2026-04-11T00:00:00Z
retest_completed: 2026-04-11T00:00:00Z
retest_scope: "Tests 8, 9, 11, 12 — post-16-05 gap closure re-verification"
---

## Current Test

[retest complete]

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
  status: failed
  reason: "User reported: envelope well-formed with _meta.source.url=https://ws.mapserver.transports.gouv.qc.ca/swtq but data=[] — route filter returns zero rows"
  severity: major
  test: 8
  retest_of: 8
  discovered: 2026-04-11
  root_cause: "UNDIAGNOSED — hypothesis: either (a) the CSV column holding route number has a different name than the filter matcher expects in fetch_bridge_structures, or (b) the MTQ_BRIDGES_URL is missing WFS query params (service=WFS&typename=...) and swtq is returning a capabilities/layer-list doc rather than the feature CSV, so fetch_and_parse successfully parses a CSV that has no route rows at all. Needs live curl of the URL to inspect payload shape."
  artifacts: []
  missing:
    - "curl MTQ_BRIDGES_URL and inspect response (is it feature data or layer list?)"
    - "If feature data: compare CSV column names to the filter matcher in fetch_bridge_structures"
    - "If layer list: add missing WFS query params (service=WFS, version=2.0.0, request=GetFeature, typename=<bridges_layer>)"
  debug_session: ""

- truth: "quebec_get_road_conditions returns rows with populated fields (route/region/pavement/visibility/snow/timestamp)"
  status: failed
  reason: "User reported: rows ARE returned (error propagation fix confirmed) but every field is null — {segment_id: null, route_num: null, route_name: null, region: null, pavement_status: null, visibility: null, has_snow_presence: null, timestamp: null}"
  severity: major
  test: 9
  retest_of: 9
  discovered: 2026-04-11
  root_cause: "UNDIAGNOSED — the schema-mapping layer in fetch_road_conditions uses column names that don't match the real MTQ conditions_routieres CSV headers. The transform dict/mapper references columns like 'SegmentId', 'RouteNum', 'Region' but the live CSV likely uses different casing or French names (e.g., 'id_segment', 'numero_route', 'NomRegion'). Needs live curl to enumerate actual headers."
  artifacts:
    - path: "src/mcp_canada/modules/quebec/client.py:fetch_road_conditions"
      issue: "Row-to-schema mapper references column names that don't exist in the live CSV; every field null-coalesces"
  missing:
    - "curl MTQ_ROAD_CONDITIONS_URL, inspect header row"
    - "Align fetch_road_conditions column-mapper keys with actual CSV headers"
    - "Apply same alignment audit to fetch_bridge_structures, fetch_road_works, fetch_road_events (same family)"
    - "Add a unit test with a fixture CSV that matches the live header shape, not the synthetic one"
  debug_session: ""

- truth: "quebec_get_electricity_data returns non-empty Hydro-Québec historical rows"
  status: failed
  reason: "User reported: {'error':{'code':'UPSTREAM_ERROR','message':'Error fetching electricity data: [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] ssl/tls alert handshake failure (_ssl.c:1081)','lang':'en'}}"
  severity: major
  test: 11
  retest_of: 11
  discovered: 2026-04-11
  root_cause: "UNDIAGNOSED — the Hydro-Québec origin server (hydroquebec.com) rejects httpx's default TLS handshake. Likely OpenSSL 3.x default SECLEVEL=2 excluding weak ciphers/protocols the server still uses. Either (a) the server supports only legacy cipher suites, or (b) needs SNI-specific config, or (c) cert chain issue. Now that the XLSX matcher fix landed, the tool actually reaches the fetch step and surfaces the real upstream error instead of returning empty."
  artifacts:
    - path: "src/mcp_canada/shared/http.py"
      issue: "Default httpx.AsyncClient lacks SSL context override for legacy hydroquebec.com TLS config"
    - path: "src/mcp_canada/modules/quebec/client.py:fetch_electricity_data"
      issue: "Selects the first XLSX resource URL (hydroquebec.com) without checking for alternate mirror URLs in the package_show response"
  missing:
    - "Try `curl -v` on the XLSX URL to confirm the handshake failure and identify the server's preferred ciphers"
    - "Option A: Build a custom ssl.SSLContext (set_ciphers('DEFAULT:@SECLEVEL=1')) scoped only to hydroquebec.com fetches"
    - "Option B: Check package_show for a donneesquebec.ca-hosted mirror of the same XLSX and prefer it"
    - "Option C: Document as known upstream limitation and return a bilingual 'external service unavailable' error"
    - "Add an integration test that asserts either non-empty data OR this specific SSL error (not a silent empty)"
  debug_session: ""
