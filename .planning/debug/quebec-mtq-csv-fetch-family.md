---
status: diagnosed
trigger: "Quebec Tests 8/9/11 — MTQ WFS CSV + Hydro-Québec two-step fetches return empty or UPSTREAM_ERROR 'File is not a zip file'"
created: 2026-04-12T02:00:00Z
updated: 2026-04-12T02:10:00Z
---

## Current Focus

hypothesis: `shared/parsers.fetch_and_parse` routes MTQ WFS CSV URLs to `_parse_xlsx` because it strips the query string before checking the `.csv` suffix; Hydro-Québec package has zero CSV resources so `fetch_electricity_data` returns empty before fetch_and_parse is even called.
test: Live curl + live Python reproduction against all 4 MTQ endpoints and the Hydro-Québec package_show.
expecting: Both confirmed as root causes.
next_action: Document, recommend fix, update UAT gap entries.

## Symptoms

expected:
  - Test 8: `quebec_get_bridge_structures(route="A-20")` returns bridge features from MTQ WFS CSV.
  - Test 9: `quebec_get_road_conditions()` returns current road condition rows from MTQ WFS CSV.
  - Test 11: `quebec_get_electricity_data()` returns Hydro-Québec historical production/consumption rows.
actual:
  - Test 8: `UPSTREAM_ERROR: MTQ WFS error: File is not a zip file`
  - Test 9: envelope well-formed but `data=[]` (silent graceful path)
  - Test 11: envelope well-formed but `data=[]` with `_meta.source.url` pointing at `package_show`
errors: "File is not a zip file" (openpyxl `zipfile.BadZipFile` raised from `_parse_xlsx`)
reproduction:
  - Test 8: `await quebec_get_bridge_structures(route="A-20")`
  - Test 9: `await quebec_get_road_conditions()`
  - Test 11: `await quebec_get_electricity_data()`
  - Direct reproduction: `await fetch_and_parse(MTQ_BRIDGES_URL)` → raises `BadZipFile`
started: introduced when Phase 16 Plan 03 (MTQ WFS CSV tools) and Plan 04 (electricity data two-step) landed; unit tests mocked the transport, so the routing bug was never exercised against a real URL with `outputformat=csv` query param.

## Eliminated

- hypothesis: "MTQ WFS endpoint is returning non-CSV content (ZIP, HTML, XML error)"
  evidence: Live curl shows HTTP 200, Content-Disposition `attachment; filename=resultat_TQ.csv`, and body bytes start with BOM `\ufeff` + comma-separated headers (`ide_strct,num_dossr,...` for bridges; `NumeroSegment,NumeroRoute,...` for road conditions; `identifiant,identifiantChantier,...` for road works). All three MTQ endpoints return genuine CSV (sizes 4.3MB / 103KB / 162KB). The error is NOT on the server side.
  timestamp: 2026-04-12T02:05:00Z

- hypothesis: "Tool layer is re-raising a downstream error with a wrapped 'is not a zip file' message"
  evidence: `grep -rn "is not a zip file"` returns zero matches in src/. The literal string comes from Python stdlib `zipfile.BadZipFile`, raised inside `openpyxl.load_workbook(BytesIO(content))` when the bytes are not a valid ZIP. Our code does not produce this string; it's raised by openpyxl and stringified by `tools.py:454` (`f"MTQ WFS error: {exc}"`).
  timestamp: 2026-04-12T02:05:30Z

- hypothesis: "Hydro-Québec package_show is returning empty resources (API broken)"
  evidence: Live Python call returns `success: True` with 4 resources. ALL 4 are format=`XLSX` (not CSV). So `fetch_electricity_data` falls into the `csv_url is None → return []` branch after correctly fetching the package. The envelope URL stays at package_show because the tool hardcodes `api_url=BASE_URL + "package_show"` at `tools.py:614`, independent of whether CSV parsing happened.
  timestamp: 2026-04-12T02:06:00Z

## Evidence

- timestamp: 2026-04-12T02:03:00Z
  checked: `curl -D - https://ws.mapserver.transports.gouv.qc.ca/swtq?...&typename=ms:gsq_v_desc_strct_tri&outputformat=csv`
  found: HTTP 200; Content-Disposition: `attachment; filename=resultat_TQ.csv`; NO Content-Type header; body is 4,342,345 bytes of UTF-8-BOM CSV starting with `ide_strct,num_dossr,val_annee_,code_des_s,nom_route,...`.
  implication: Server is healthy and returns real CSV. Problem is in our parser dispatch.

- timestamp: 2026-04-12T02:03:03Z
  checked: `curl -D - https://ws.mapserver.transports.gouv.qc.ca/swtq?...&typeName=ms:conditions_routieres&outputFormat=csv`
  found: HTTP 200; Content-Disposition: `attachment; filename=resultat_TQ.csv`; body is 103,021 bytes of UTF-8-BOM CSV (`NumeroSegment,NumeroRoute,NomRoute,NomRegion,...,DescriptionEtatChausseeFR,DescriptionEtatChausseeEN,...`). `ms:conditions_routieres` IS live and returns real data — the research-flagged "low confidence" was wrong.
  implication: `fetch_road_conditions` would work if the parser didn't raise.

- timestamp: 2026-04-12T02:03:04Z
  checked: `curl -D - https://ws.mapserver.transports.gouv.qc.ca/swtq?...&typename=ms:chantiers_mtmdet&outputformat=csv`
  found: HTTP 200; Content-Disposition: `attachment; filename=resultat_TQ.csv`; body is 162,407 bytes of UTF-8-BOM CSV starting with `identifiant,identifiantChantier,routeAutoroute,...`.
  implication: Road works endpoint is healthy; same parser dispatch bug is hitting it silently (integration test tolerates errors so it passed green).

- timestamp: 2026-04-12T02:04:00Z
  checked: `uv run python3 -c "... url.lower().split('?')[0]" on MTQ bridges URL`
  found: `lower_url = 'https://ws.mapserver.transports.gouv.qc.ca/swtq'`. `endswith('.csv')=False`, `endswith('.xls')=False`, `endswith('.geojson')=False`, `endswith('.json')=False`. Routes to the `else` branch → `_parse_xlsx`.
  implication: This is the root cause for the MTQ family. `parsers.py:513` strips `?outputformat=csv` before the suffix check; since the path is `/swtq` (no extension), everything falls through to XLSX.

- timestamp: 2026-04-12T02:04:30Z
  checked: `await fetch_and_parse(MTQ_BRIDGES_URL, ttl=60)`
  found: `EXCEPTION: BadZipFile: File is not a zip file`
  implication: Confirms the routing bug end-to-end. openpyxl calls `zipfile.ZipFile(BytesIO(raw))` on CSV bytes; Python's zipfile module raises `BadZipFile: File is not a zip file`.

- timestamp: 2026-04-12T02:05:00Z
  checked: `await fetch_road_works()`, `await fetch_road_events()`, `await fetch_road_conditions()`, `await fetch_bridge_structures(route='A-20')`
  found:
    - road_works: `EXCEPTION BadZipFile: File is not a zip file`
    - road_events: `EXCEPTION BadZipFile: File is not a zip file`
    - road_conditions: `OK rows=0 cached=False` (silent — try/except Exception returns [])
    - bridges: `EXCEPTION BadZipFile: File is not a zip file`
  implication: ALL FOUR MTQ client functions are broken, not just the two in the UAT gap list. `quebec_get_road_works` and `quebec_get_road_events` are also currently non-functional — integration test 16 passed because `test_get_road_works_wfs_csv` accepts `"_meta" in data or "error" in data` (either is "pass"). Test 9 was the only user test that hit `fetch_road_conditions` which swallows the exception.

- timestamp: 2026-04-12T02:06:00Z
  checked: `api_get(https://www.donneesquebec.ca/recherche/api/3/action/package_show, id=historique-production-consommation)` via Python client
  found: `success: True`, 4 resources, ALL with `format=XLSX`:
    1. XLSX `2021 : Historique...` → `https://www.hydroquebec.com/data/documents-donnees/xls/suivi-2021-de-l-entente-globale-cadre.xlsx`
    2. XLSX `2020 : ...` → `` (EMPTY url)
    3. XLSX `2019 : ...` → `.../suivi-2019-entente-globale-cadre-mai2020.xlsx`
    4. XLSX `2018 : ...` → `.../suivi-2018-entente-globale-cadre-1mai2019.xlsx`
  implication: Test 11 root cause is DIFFERENT from Test 8/9. `fetch_electricity_data` at `client.py:751-760` loops looking for `(r.format or "").upper() == "CSV"` — no resource matches, `csv_url` stays None, function returns `[]`. The `_meta.source.url` stays at `package_show` because the tool hardcodes that URL in the envelope regardless of whether CSV parsing happens (`tools.py:614`). The research doc assumed "CSV available" without verifying — the actual resources are XLSX-only.

- timestamp: 2026-04-12T02:06:30Z
  checked: `grep -rn "is not a zip file" src/`
  found: 0 matches. String originates from Python stdlib `zipfile` module, not from mcp_canada.
  implication: Confirms the error is raised by openpyxl → zipfile.BadZipFile, not by our code.

- timestamp: 2026-04-12T02:07:00Z
  checked: `fetch_and_parse` callers (`grep -rn "fetch_and_parse(" src/`)
  found: 7 production callers
    - `ontario/client.py:306` — `POPULATION_PROJECTIONS_RESOURCE_URL` (static .xlsx URL, works)
    - `ircc/client.py:44` — static .xlsx URLs (works)
    - `british_columbia/tools.py:315` — dynamic `resource["url"]` (depends on URL)
    - `quebec/client.py:314` — `picked.url` from _pick_best_resource (can be anything)
    - `quebec/client.py:472` — `MAMH_MUN_CSV_URL` ends in `.csv` (works)
    - `quebec/client.py:503,552,583,624` — MTQ WFS URLs (BROKEN — no .csv suffix in path)
    - `quebec/client.py:760` — `csv_url` from two-step (would work if URL was real CSV)
  implication: Min-diff fix is to enhance format detection in `fetch_and_parse` so it recognises `outputformat=csv`/`outputFormat=csv`/`format=csv` query parameters. This unblocks MTQ without changing any caller signature.

## Resolution

root_cause:
  primary: "`shared/parsers.py:fetch_and_parse` detects file format by URL path suffix only (line 513: `url.lower().split('?')[0]`). MTQ WFS URLs have the format hint in the query string (`?...&outputformat=csv`), so after stripping the query the path `/swtq` matches no suffix and falls through to `_parse_xlsx`. openpyxl then tries to open CSV bytes as a ZIP and raises `zipfile.BadZipFile: File is not a zip file`. Affects all 4 MTQ WFS CSV tools: `fetch_bridge_structures` (Test 8), `fetch_road_conditions` (Test 9, silently via graceful except), `fetch_road_works`, `fetch_road_events`."

  secondary: "`fetch_electricity_data` (Test 11) is a completely different bug: the Hydro-Québec `historique-production-consommation` package has ZERO CSV resources — all 4 resources are XLSX. The function hardcodes `(r.format or '').upper() == 'CSV'` and returns `[]` when no match is found. Separately, `quebec_get_electricity_data` tool hardcodes `api_url=BASE_URL + 'package_show'` in the envelope (`tools.py:614`) so users see the package_show URL even though no CSV was fetched."

fix:
  primary_recommended: |
    **Single-root-cause fix for MTQ family (Tests 8, 9, and the silent-green 16-road-works/16-road-events):**

    In `src/mcp_canada/shared/parsers.py:fetch_and_parse()`, extend the format-detection logic to also inspect query-string format hints. Replace lines 513-525 with:

    ```python
    # Detect format by URL path suffix first, then by query-string format hints.
    # MTQ WFS endpoints put format in query (?outputformat=csv) not the path.
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(url)
    path_lower = parsed.path.lower()
    query_params = {k.lower(): [v.lower() for v in vs] for k, vs in parse_qs(parsed.query).items()}
    # Collect all format hints from known WFS-style query keys
    query_formats: set[str] = set()
    for key in ("outputformat", "format", "f"):
        query_formats.update(query_params.get(key, []))

    def _matches(ext: str, fmt: str) -> bool:
        return path_lower.endswith(ext) or fmt in query_formats

    if _matches(".csv", "csv"):
        return _parse_csv(raw, skip_rows)
    elif _matches(".xls", "xls"):
        return _parse_xls(raw, sheet, skip_rows)
    elif _matches(".geojson", "geojson") or _matches(".geojson", "application/json+geo"):
        return _parse_geojson(raw)
    elif _matches(".json", "json"):
        return _parse_json(raw)
    elif ircc_parse_config is not None:
        return _parse_ircc_xlsx(raw, sheet=sheet, **ircc_parse_config)
    else:
        return _parse_xlsx(raw, sheet, skip_rows)
    ```

    This fixes all 4 MTQ tools with zero caller changes. Keeps the existing path-suffix fast-path. Caches are keyed on URL so existing cached failures do not apply (exceptions are not cached per `shared/cache.py`).

  secondary_required: |
    **Test 11 (electricity) requires its own fix because the root cause is different:**

    1. In `client.py:fetch_electricity_data`, expand the resource matcher to also accept XLSX (the only format actually published):
       ```python
       for r in details.resources:
           fmt = (r.format or "").upper()
           if fmt in ("CSV", "XLSX", "XLS") and r.url:
               file_url = r.url
               break
       ```
       Rename `csv_url` → `file_url`. `fetch_and_parse` already routes .xlsx URLs to `_parse_xlsx`.

    2. In `tools.py:quebec_get_electricity_data`, do NOT hardcode `api_url=BASE_URL + "package_show"`. Either (a) pass the actual file URL back from the client and use it in the envelope, or (b) accept that package_show is the discovery URL but rename the tool docstring note to clarify this is the Hydro-Québec metadata API rather than a CSV endpoint.

    3. Skip the resource with empty `url=""` (2020 entry has no URL — likely Hydro-Québec pulled that file).

    4. Consider caching: `CACHE_TTL_META` (24h) on metadata package results, and a separate cache entry for the parsed XLSX rows.

    5. Verify from logs or integration test that `https://www.hydroquebec.com/...xlsx` is reachable from the target deployment (my local environment returned `SSL: SSLV3_ALERT_HANDSHAKE_FAILURE` — this could be a local TLS config issue; verify via pytest integration with `@pytest.mark.integration`).

verification:
  - "Unit: add a test in `src/mcp_canada/shared/__tests__/test_parsers.py` that calls `fetch_and_parse` with a URL like `https://example.com/wfs?service=wfs&outputformat=csv` (no .csv path suffix) and mocks a 200 response with CSV bytes — asserts it routes to `_parse_csv`."
  - "Integration: add live-URL assertions (not tolerant or/or) for `quebec_get_bridge_structures(route='A-20')` expecting `len(data['data']) > 0` and `quebec_get_road_conditions()` expecting either non-empty OR explicit season-empty note (winter-only). Replace the `\"_meta\" in data or \"error\" in data` pattern with `assert \"_meta\" in data` so future regressions fail loudly."
  - "Live reproduction after fix: `await fetch_and_parse('https://ws.mapserver.transports.gouv.qc.ca/swtq?service=wfs&version=2.0.0&request=getfeature&typename=ms:gsq_v_desc_strct_tri&outputformat=csv')` should return ~50K rows (bridges), and `await fetch_electricity_data()` should return the 2021 XLSX rows (or the first available year)."
  - "After fix, rerun Tests 8/9/11 manually via the MCP tool layer and expect all three to return data (or a well-formed bilingual INVALID_INPUT for test 7 unchanged)."

files_changed: []

## Why Unit Tests Missed It

1. **`shared/__tests__/test_parsers.py` only tested URLs with path suffixes** (`example.com/data.csv`, `example.com/data.xlsx`). No test exercised a URL with a format hint in the query string. The parser's dispatch logic was never tested against the actual URL shape used by MTQ WFS.
2. **Quebec module unit tests mock `fetch_and_parse` directly.** The conftest fixture `sample_mtq_road_works_csv` provides mocked rows so the client functions are tested against the post-parse shape, never against real MTQ URLs.
3. **Integration test `test_get_road_works_wfs_csv` uses tolerant assertions**: `assert "_meta" in data or "error" in data`. An error envelope counts as a pass. Same for `test_get_bridge_structures_requires_filter` which accepts either `_meta` or `error` on the with-filter call.
4. **`fetch_road_conditions` catches `Exception` at `client.py:502-505` and returns `[]`** — no error surfaces to any test even when the parser raises.
5. **No live integration test exists for `quebec_get_electricity_data`, `quebec_get_road_conditions`, or `quebec_get_road_events`.**

### Test Improvement Suggestions

- Add `test_fetch_and_parse_routes_wfs_csv_query_param` in `shared/__tests__/test_parsers.py`:
  ```python
  async def test_routes_wfs_csv_via_query_param(self):
      url = "https://ws.mapserver.transports.gouv.qc.ca/swtq?service=wfs&outputformat=csv"
      mock_resp = MagicMock(); mock_resp.content = b"a,b\n1,2\n"; mock_resp.raise_for_status = MagicMock()
      with patch("httpx.AsyncClient") as mc:
          mc.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_resp)
          rows, _ = await fetch_and_parse(url, ttl=60)
      assert rows == [{"a": 1, "b": 2}]  # routed to _parse_csv
  ```
- Replace tolerant `"_meta" or "error"` assertions in `tests/integration/test_tool_scenarios.py::TestQuebecToolScenarios` with strict `assert "_meta" in data` for every MTQ tool.
- Add a live integration test `test_get_electricity_data_returns_rows_or_metadata_note` that asserts either `len(data["data"]) > 0` or a documented explicit empty-state code (not a silent empty).
- Add a `fetch_and_parse` corpus test that exercises one real URL from each portal type (CKAN, MTQ WFS CSV, MAMH CSV, IRCC XLSX) with `@pytest.mark.integration` to catch dispatch regressions.

## Minimum-Diff Fix Summary

- **1 file** for the MTQ family root cause: `src/mcp_canada/shared/parsers.py` — enhance `fetch_and_parse` query-string format detection (~15 lines changed/added).
- **1 file** for the electricity data secondary fix: `src/mcp_canada/modules/quebec/client.py` — `fetch_electricity_data` expand format matcher from CSV-only to CSV/XLSX/XLS (~4 lines).
- **1 file** for envelope honesty: `src/mcp_canada/modules/quebec/tools.py` — `quebec_get_electricity_data` return the actual file URL in envelope (~3 lines) OR explicitly document package_show is the metadata URL.
- **1 file** for regression protection: `src/mcp_canada/shared/__tests__/test_parsers.py` — add WFS query-param routing test (+1 test).
- **1 file** to tighten integration tests: `tests/integration/test_tool_scenarios.py` — drop tolerant `or "error"` assertions on MTQ tools (3 edits).
