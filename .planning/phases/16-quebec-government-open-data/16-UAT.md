---
status: complete
phase: 16-quebec-government-open-data
source:
  - 16-01-SUMMARY.md
  - 16-02-SUMMARY.md
  - 16-03-SUMMARY.md
  - 16-04-SUMMARY.md
started: 2026-04-11T00:00:00Z
updated: 2026-04-12T00:00:00Z
---

## Current Test

[testing complete]

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
reported: "{'error': {'code': 'UPSTREAM_ERROR', 'message': 'MTQ WFS error: File is not a zip file', 'lang': 'en'}}"
severity: major

### 9. Road conditions (MTQ WFS CSV, active TTL)
expected: Call `quebec_get_road_conditions()` — returns current Quebec road condition data from the MTQ WFS CSV endpoint. Bilingual columns — EN vs FR descriptions selected by `lang` param. `_meta.cached` uses short TTL (active data). Graceful empty list if the WFS endpoint fails (research flagged low-confidence endpoint).
result: issue
reported: "Envelope well-formed with _meta.source.url=https://ws.mapserver.transports.gouv.qc.ca/swtq but data=[] — graceful empty path hit, meaning the MTQ WFS CSV fetch failed silently"
severity: major
notes: Likely same root cause family as Test 8 (MTQ WFS CSV endpoints not being fetched/parsed correctly). Research flagged fetch_road_conditions as low-confidence — the graceful-empty path in _fetch masks the real failure. Test 8 surfaced the underlying "File is not a zip file" error when route filter path was hit; road_conditions swallows the exception and returns empty.

### 10. Air quality stations (RSQAQ datastore)
expected: Call `quebec_get_air_quality_stations(active_only=True)` — returns 245 Réseau de surveillance de la qualité de l'air du Québec (RSQAQ) monitoring stations, filtered to those with no `DATE_FERMETURE` (still active). Each has station name, municipality, coordinates.
result: pass

### 11. Electricity data (two-step CKAN → CSV)
expected: Call `quebec_get_electricity_data()` — two-step: first fetches Hydro-Québec dataset details, picks first CSV resource, then parses it via `fetch_and_parse`. Returns historical production/consumption rows. Note: this is NOT real-time outages (SOPFEU/outages data is not on Données Québec per research — replaced with historical data).
result: issue
reported: "Envelope well-formed with _meta.source.url=https://www.donneesquebec.ca/recherche/api/3/action/package_show but data=[] — tool returns no rows. Two-step flow (package_show → pick CSV → fetch_and_parse) produced empty result."
severity: major
notes: _meta.source.url points at package_show (step 1) rather than the CSV URL (step 2), suggesting either (a) the selected Hydro-Québec dataset has no CSV resource, (b) the CSV parse step failed silently, or (c) the code returns package_show source URL even after successful CSV parse. Needs diagnosis.

### 12. Discovery finds Quebec tools via BM25
expected: Call `discover_tools(query="Quebec hospitals health")` — returns Quebec tools in the top results (e.g. `quebec_get_health_installations`, `quebec_get_er_wait_times`, `quebec_explore_health` prompt). The 18 quebec_ tools are reachable through the BM25 discovery layer.
result: issue
reported: "Top 5 results: quebec_get_health_installations, york_region_get_public_health, quebec_search_datasets, quebec_get_dataset_details, quebec_list_organizations. quebec_get_er_wait_times is NOT in the top results."
severity: minor
notes: "quebec_get_er_wait_times BM25 keywords are 'quebec, emergency, er, wait times, urgence, hospital, civieres, msss, real-time, stretchers, occupancy, temps attente' — missing the literal word 'health'. BM25 matches only 2/3 query tokens (quebec+hospital) versus 3/3 for quebec_get_health_installations. Fix: add 'health', 'medical', 'sante' to the keywords line. Trivial one-line fix in tools.py docstring."

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

## Gaps

- truth: "quebec_get_bridge_structures returns bridge features when filtered by route"
  status: failed
  reason: "User reported: UPSTREAM_ERROR 'MTQ WFS error: File is not a zip file' — fetch_and_parse is trying to unzip a non-zip response from the MTQ bridge structures endpoint"
  severity: major
  test: 8
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""

- truth: "quebec_get_road_conditions returns current MTQ road condition rows"
  status: failed
  reason: "User reported: envelope well-formed but data=[]. Graceful-empty path in _fetch masked the real failure — tool provides no value. Same root cause family as Test 8 MTQ WFS CSV endpoints."
  severity: major
  test: 9
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""

- truth: "quebec_get_electricity_data returns Hydro-Québec historical production/consumption rows"
  status: failed
  reason: "User reported: envelope well-formed but data=[] and _meta.source.url points at package_show (step 1 of two-step), not the CSV URL. Two-step flow produced empty result."
  severity: major
  test: 11
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""

- truth: "quebec_get_er_wait_times is discoverable via BM25 search for Quebec health queries"
  status: failed
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
