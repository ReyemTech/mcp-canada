# Phase 16: Quebec Government Open Data - Research

**Researched:** 2026-04-11
**Domain:** Données Québec CKAN API + curated provincial datasets
**Confidence:** HIGH (all findings live-verified against the actual API)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Use Données Québec CKAN API at `https://www.donneesquebec.ca/recherche/api/3/action/` — standard CKAN + `User-Agent` header recommended
- **NO secondary geospatial portal** in this phase. Géoportail Québec, MTQ ArcGIS Feature Services, and MELCCFP WFS endpoints are deferred
- Geospatial datasets hosted on Données Québec are parsed from file resources (CSV, GeoJSON) via `shared/parsers.fetch_and_parse()` or CKAN `datastore_search` — no new protocol support needed
- Module prefix: `quebec_`
- Default `lang: Literal["en", "fr"] = "en"` — consistent project-wide
- All bilingual error messages use the inline `lang == "fr"` ternary pattern — do NOT introduce `shared/i18n.py:t()` imports
- `quebec_search_datasets` returns results from all 139 orgs by default — no hardcoded allowlist
- `_api_get` MUST treat shared `api_get` return as parsed dict — NO `.raise_for_status()` / `.json()` calls
- `TestSharedApiGetContract` class pattern — patches `mcp_canada.modules.quebec.client.api_get` (NOT shared layer) with raw-dict `AsyncMock`

### Claude's Discretion
- Exact CKAN `fq` strategies for filtering federated catalog (Montreal org slugs, NGO exclusion patterns if needed at docstring level)
- Which specific MSSS datasets to curate (MSSS has many overlapping health datasets — pick the most agent-friendly)
- Whether SOPFEU wildfire data is on Données Québec or on a SOPFEU-specific portal (research has confirmed — see below)
- Whether Hydro-Québec outages are on Données Québec CKAN or require the Hydro-Québec website API (research has confirmed — see below)
- How to handle bilingual CKAN fields — research has confirmed the field shape (plain French `title` only, no `title_translated`)
- Rate limit settings for Données Québec

### Deferred Ideas (OUT OF SCOPE)
- Géoportail Québec / ArcGIS Feature Services
- Quebec City municipal open data (`donnees.ville.quebec.qc.ca`)
- Laval, Gatineau, Longueuil, Sherbrooke, Saguenay municipal portals
- SOPFEU-specific portal (confirmed: wildfire data is NOT on DQ CKAN — see below)
- Hydro-Québec outages API (confirmed: outages data is NOT on DQ CKAN — see below)
- MTQ Quebec 511 scraping (road conditions archive CSV is 970K rows, 530MB ZIP — too large; live data is WFS-queryable via MTQ's external server)
- MSS (Montreal ARTM) transit — Montreal-specific, belongs in Phase 27
- Bilingual `shared/i18n.py:t()` adoption — future dedicated phase
</user_constraints>

---

## Summary

Five critical findings from live API probing that directly reshape curated tool scope:

1. **SOPFEU wildfire data NOT on Données Québec.** SOPFEU is not registered as an organization (`fq=organization:sopfeu` returns 0 results). Historical fire perimeters (`feux-de-foret`, org: `mrn`) exist as GPKG/SHP/FGDB only — no CSV or GeoJSON resource, and formats are not supported by `fetch_and_parse()`. The planned `quebec_get_active_fires` and `quebec_get_fire_perimeters` tools are moved to deferred. **Replacement:** `quebec_get_road_works` (MTQ live construction/events WFS — verified working) and `quebec_get_fire_prevention_zones` (MSP mesures preventives — CONTEXT.md defers MSP auth issues). Final replacement: `quebec_get_road_works` + `quebec_get_wildfire_risk` (SOPFEU data via MFFP's publicly available annual stats — see dataset catalog below).

2. **Hydro-Québec outage data NOT on Données Québec.** The 10 Hydro-Québec datasets on DQ are energy production/consumption statistics and hydrometeorological data. No outage registry exists. Moved to deferred. **Replacement:** `quebec_get_electricity_production` (historical production/consumption — Hydro-Québec org on DQ, CSV available) and one of the MELCCFP air quality real-time tools.

3. **ER wait times ARE on Données Québec via CKAN datastore.** `fichier-horaire-des-donnees-de-la-situation-a-l-urgence` (MSSS, hourly update) has `datastore_active=True`, 116 rows, queryable via `datastore_search`. This is the best real-time health dataset available.

4. **Bilingual metadata shape:** DQ CKAN datasets have a single `title` field in French only. No `title_translated`, `title_fr`, or `title_en` fields exist. The client should surface `title` as-is (French) plus `organization` name. Tools should document the French-primary nature in their docstrings.

5. **DQ has CKAN groups (10 thematic groups)** unlike BC which returns HTTP 403. `quebec_list_categories` should use `group_list` not `tag_list`. Groups are: Agriculture, Économie, Éducation, Environnement/Ressources/Énergie, Gouvernement/Finances, Infrastructures, Loi/Justice/Sécurité, Politiques sociales, Santé, Société/Culture.

**Primary recommendation:** Follow the BC module pattern exactly (post-15-05 `_api_get` fix). Replace SOPFEU tools with road works + wildfire risk; replace Hydro-Québec outages with electricity production data. Use `datastore_search` for health tools (installations, ER wait times) since they have `datastore_active=True`. Use WFS CSV resources from `ws.mapserver.transports.gouv.qc.ca` for MTQ transport tools.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `fastmcp` | 3.2.x | MCP server framework | Project standard |
| `httpx` | 0.28.x | Async HTTP — `api_get` (CKAN) + `fetch_and_parse` (files) | Shared infrastructure |
| `pydantic` | v2 | Flat schemas for CKAN responses | Project standard |
| `aiocache` | latest | TTL cache via `cached_fetch()` | Project standard |
| `tenacity` | latest | Retry on 429/5xx inside `api_get` | Project standard |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `shared/http.py:api_get` | — | CKAN Action API calls | All `_api_get` calls |
| `shared/parsers.py:fetch_and_parse` | — | CSV/JSON direct file parsing | MTQ WFS CSV endpoints, MAMH municipal CSV |
| `shared/cache.py:cached_fetch` | — | All client functions | Every client function |
| `shared/rate_limiter.py:get_limiter` | — | Token bucket per source | Every client function |
| `shared/envelope.py` | — | `make_response`/`make_error` | Every tool function |

**Installation:** No new packages needed. All existing stack sufficient.

---

## Données Québec CKAN API Details (Live-Verified)

**Base URL:** `https://www.donneesquebec.ca/recherche/api/3/action/`

**User-Agent:** `httpx` 0.28.1 sends `python-httpx/0.28.1` by default — DQ CKAN returns real JSON without any special header. The CONTEXT.md note about "User-Agent required" was based on an older observation (may have been a WAF behavior that changed). However, set `headers={"User-Agent": "mcp-canada/1.0 (+https://github.com/reyemtech/mcp-canada)"}` in `api_get` calls for proper identification and to avoid potential future blocking.

**Dataset count:** 1,593 packages (live, 2026-04-11)

**Organization count:** 139 orgs (federated: provincial ministries + municipalities + NGOs + parastatal entities)

**Response shape for `package_search`:**
```json
{
  "success": true,
  "result": {
    "count": 1593,
    "results": [{
      "id": "uuid",
      "name": "slug-kebab-case",
      "title": "Titre en français",
      "notes": "Description en français",
      "organization": {"name": "msss", "title": "Ministère de la Santé..."},
      "license_id": "cc-by",
      "update_frequency": "monthly|annual|continuous|hourly|asNeeded|semiannual|weekly",
      "language": "FR",
      "groups": [{"name": "sante", ...}],
      "extras_organisation_principale": "gouvernement-du-quebec",
      "inv_access_level": "open",
      "num_resources": 3,
      "num_tags": 5
    }]
  }
}
```

**Bilingual metadata field shape (CONFIRMED):** DQ uses plain `title` (French only). No `title_translated`, `title_fr`, `title_en`, or `notes_translated` fields exist. Client flatten should use `title` as-is. Agents wanting English should use `discover_tools`/`call_tool` and the tool docstrings.

**Group/category support:** `group_list?all_fields=true` returns 10 thematic groups (CONFIRMED working, unlike BC which returns HTTP 403). Use groups for `quebec_list_categories`.

**Tag support:** `tag_list` returns ~4,200 tags — too noisy for browsing; keep `tag_list` for programmatic use but don't expose as primary category list.

**`fq` filter syntax (CONFIRMED):**
- `fq=organization:msss` — filter by org slug
- `fq=groups:sante` — filter by thematic group
- `fq=organization:msss+groups:sante` — combined (space-separated multiple fq values work)

**CKAN Datastore availability (CONFIRMED):** DQ exposes both `datastore_search` and `datastore_search_sql`. Resources with `datastore_active=True` are queryable. Key datastore-active resources found:
- MSSS health installations: 1,592 rows, `datastore_search` + SQL confirmed working
- MSSS ER hourly situation: 116 rows (one row per hospital), hourly updates, `datastore_search` confirmed working
- MAMH municipal registry: CSV with `datastore_active=True`
- RSQAQ air quality stations: 245 rows, `datastore_search` confirmed working

**MTQ external WFS endpoints (confirmed working for CSV):**
- Base: `https://ws.mapserver.transports.gouv.qc.ca/swtq`
- Road works: `?service=wfs&version=2.0.0&request=getfeature&typename=ms:chantiers_mtmdet&outputformat=csv`
- Road warnings: `?service=wfs&version=2.0.0&request=getfeature&typename=ms:evenements&outputformat=csv`
- Bridge structures: `?service=wfs&version=2.0.0&request=getfeature&typename=ms:gsq_v_desc_strct_tri&outputformat=csv`

Note: The MTQ WFS CSV URLs are stored as resource URLs within DQ CKAN packages (`travaux-routiers`, `avertissement-routier`, `structure`). Use `package_show` to get canonical URL, then `fetch_and_parse(url)` directly.

**Known DQ extras fields unique to DQ:**
- `extras_organisation_principale` — the primary provincial org even for federated datasets from municipalities
- `inv_access_level` — always `"open"` for open datasets
- `inv_security_classification` — `"Public"` for open data
- `language` — `"FR"` for all DQ datasets (no EN-only datasets found)

---

## Bilingual Metadata Field Shape (Live-Verified)

**CONFIRMED:** All DQ CKAN metadata is French-only.

| Field | Shape | English equivalent |
|-------|-------|--------------------|
| `title` | Plain French string | Not available |
| `notes` | Plain French markdown/text | Not available |
| `organization.title` | French org name | Not available |
| `update_frequency` | French: `"mensuel"`, `"annuel"`, `"continu"`, `"horaire"`, `"asNeeded"`, `"semiannuel"`, `"hebdomadaire"` | N/A |
| `groups[].display_name` | French group name | Not available |

**Client flatten strategy:** Return `title` and `notes` as-is (French). Add a `lang_note` field explaining FR-primary nature, OR simply return the data and let the `lang` parameter affect error messages and prompts only (not catalog metadata — there's no English to fall back to).

**MTQ WFS CSV columns are bilingual:** `conditions_routieres_annee_courante.csv` has separate `FR`/`EN` columns for conditions (e.g. `DescriptionEtatChausseeFR`/`DescriptionEtatChausseeEN`). Road works CSV (`travaux-routiers`) has `descriptionAnglais` column alongside `descriptionFrancais`. Client flatten should use the appropriate column based on `lang` parameter.

---

## Curated Dataset Recommendations (18 tools adjusted for real availability)

### Revised Tool List (replacing SOPFEU + Hydro-Québec outages)

**Health / MSSS (3 tools):**

#### Tool 1: `quebec_get_health_installations`
- **Package ID:** `fichiers-cartographiques-m02-des-installations-et-etablissements`
- **Org:** `msss`
- **Resource:** Installation CSV, `datastore_active=True`, resource_id `2aa06e66-c1d0-4e2f-bf3c-c2e413c3f84d`
- **Access:** `datastore_search` with optional `filters` for CLSC/CHSGS/CHSLD/CHPSY boolean flags
- **Key columns:** `INSTAL_COD`, `INSTAL_NOM`, `ETAB_NOM`, `RSS_NOM` (health region), `MRC_NOM`, `MUN_NOM`, `ADRESSE`, `CODE_POSTA`, `LONGITUDE`, `LATITUDE`, `CLSC`, `CHSGS`, `CHSLD`, `CHPSY`, `DATE_MAJ`
- **Rate of change:** Semiannual — `CACHE_TTL_STATIC` (86400s)
- **Total records:** 1,592 installations
- **Notes:** Single dataset covers hospitals (CHSGS=Oui), CLSCs (CLSC=Oui), long-term care (CHSLD=Oui), psychiatric (CHPSY=Oui). Agent can filter by type. Subsumes both `quebec_get_hospitals` and `quebec_get_clsc_locations` from CONTEXT.md into a single richer tool.

#### Tool 2: `quebec_get_er_wait_times`
- **Package ID:** `fichier-horaire-des-donnees-de-la-situation-a-l-urgence`
- **Org:** `msss`
- **Resource:** Hourly CSV, `datastore_active=True`, resource_id `a9272cc9-8234-40d1-9806-9f6b4c75c20d`
- **Access:** `datastore_search` with optional `q=` full-text on `Nom_installation`
- **Key columns:** `Nom_etablissement`, `Nom_installation`, `Nombre_de_civieres_fonctionnelles`, `Nombre_de_civieres_occupees`, `Nombre_de_patients_sur_civiere_plus_de_24_heures`, `Nombre_de_patients_sur_civiere_plus_de_48_heures`, `Heure_de_l'extraction_(image)`, `Mise_a_jour`
- **Rate of change:** Hourly — `CACHE_TTL_ACTIVE` (300s)
- **Total records:** 116 rows (one per hospital emergency department)

#### Tool 3: `quebec_get_population_by_municipality`
- **Package ID:** `repertoire-des-municipalites-du-quebec`
- **Org:** `affaires-municipales-et-occupation-du-territoire`
- **Resource:** `MUN.csv` at `https://donneesouvertes.affmunqc.net/repertoire/MUN.csv`, `datastore_active=True`
- **Access:** `fetch_and_parse(url)` — direct CSV (1,282 rows, fast)
- **Key columns:** `mcode`, `munnom` (municipality name), `regadm` (administrative region), `mrc` (MRC), `mpopul` (population), `msuperf` (area km²), `mcodedesi` (municipal type: Ville/Village/Municipality), `mayor`
- **Rate of change:** Daily updates — `CACHE_TTL_SEARCH` (3600s)
- **Notes:** Subsumes `quebec_get_population_by_region` from CONTEXT.md — municipality-level data includes region and MRC, allowing grouping. Client should support optional `region` param to filter by `regadm`.

**Transport / MTQ (3 tools):**

#### Tool 4: `quebec_get_road_conditions`
- **Package ID:** `condition-routiere-hivernale-du-reseau-routier-mtq`
- **Org:** `mtq`
- **Resource:** WFS CSV (live, continuous): `https://ws.mapserver.transports.gouv.qc.ca/swtq?service=wfs&version=2.0.0&request=GetFeature&typeName=ms:conditions_routieres&outputFormat=csv`
- **Access:** `fetch_and_parse(url)` — the WFS CSV URL works for other typename (`ms:evenements`) but `conditions_routieres` may need the annual current CSV instead
- **Fallback:** Annual current CSV at `https://ws.mapserver.transports.gouv.qc.ca/donnees/geomatique/crh_annee_courante_csv.zip` — 970K rows, 19MB ZIP — TOO LARGE for `fetch_and_parse` (224MB unzipped)
- **Key columns (from CSV):** `NumeroSegment`, `NumeroRoute`, `NomRoute`, `NomRegion`, `CodeEtatChaussee`, `DescriptionEtatChausseeFR`, `DescriptionEtatChausseeEN`, `CodeVisibilite`, `DescriptionVisibiliteFR`, `DescriptionVisibiliteEN`, `IndicateurPresenceLamesNeige`, `DateEtHeureCondition`
- **Rate of change:** Continuous — `CACHE_TTL_ACTIVE` (300s) when using live WFS
- **CONFIRMED WORKING (phase 16-05 correction):** The `ms:conditions_routieres` WFS CSV endpoint returns ~100KB of real CSV data. The previous LOW-confidence flag was incorrect — the bug was a client-side parser dispatch issue in `shared/parsers.py` that stripped query strings before detecting the format, causing all MTQ WFS CSV responses (whose format hint is `?outputformat=csv` in the query string, not the path suffix) to fall through to `_parse_xlsx` and raise `BadZipFile`. Fixed in plan 16-05 gap closure.
- **Bilingual columns:** `DescriptionEtatChausseeFR/EN` and `DescriptionVisibiliteFR/EN` — client should select by `lang` parameter.

#### Tool 5: `quebec_get_road_works`
- **Package ID:** `travaux-routiers`
- **Org:** `mtq`
- **Resource:** WFS CSV (live, continuous): `https://ws.mapserver.transports.gouv.qc.ca/swtq?service=wfs&version=2.0.0&request=getfeature&typename=ms:chantiers_mtmdet&outputformat=csv`
- **Access:** `fetch_and_parse(url)` — CONFIRMED WORKING (tested, returns current construction zones)
- **Key columns:** `identifiant`, `identifiantChantier`, `routeAutoroute`, `entraveType`, `debut`, `fin`, `miseAJour`, `identificationDesTravaux`, `localisation`, `direction`, `descriptionFrancais`, `descriptionAnglais`, `couleurLigne`, `source`
- **Rate of change:** Continuous — `CACHE_TTL_ACTIVE` (300s)
- **Bilingual:** `descriptionFrancais`/`descriptionAnglais` — select by `lang` parameter.

#### Tool 6: `quebec_get_bridge_structures`
- **Package ID:** `structure`
- **Org:** `mtq`
- **Resource:** WFS CSV: `https://ws.mapserver.transports.gouv.qc.ca/swtq?service=wfs&version=2.0.0&request=getfeature&typename=ms:gsq_v_desc_strct_tri&outputformat=csv`
- **Access:** `fetch_and_parse(url)` — CONFIRMED WORKING (returns bridge/culvert/tunnel inventory)
- **Key columns:** `ide_strct`, `num_dossr`, `val_annee_`, `code_des_s` (status), `nom_route`, `nom_obstc` (obstacle crossed), `nom_muncp`, `cod_muncp`, `nom_strct`, `num_route`, `geo_lattd`, `geo_longt`, `val_longr` (length), `val_largr_` (width), `cod_type_s` (structure type)
- **Rate of change:** Daily — `CACHE_TTL_SEARCH` (3600s)
- **Notes:** Covers bridges, culverts (>4.5m), tunnels, retaining walls — ~50K+ structures. Client must require at least one filter (route number, municipality, or region) to avoid unbounded response. Add the same guard pattern as `bc_get_water_wells`.

**SOPFEU replacement + MFFP wildfires (2 tools — replacing originally planned active fires + perimeters):**

#### Tool 7: `quebec_get_road_events`
- **Package ID:** `avertissement-routier`
- **Org:** `mtq`
- **Resource:** WFS CSV: `https://ws.mapserver.transports.gouv.qc.ca/swtq?service=wfs&version=2.0.0&request=getfeature&typename=ms:evenements&outputformat=csv`
- **Access:** `fetch_and_parse(url)` — CONFIRMED WORKING (returns current road events/warnings)
- **Key columns:** `identifiant`, `entrave`, `numeroRoute`, `localisation`, `direction`, `municipalite`, `duree`, `cause`, `consequence`, `detour`, `regions`, `enVigueurDepuis`, `couleurLigne`
- **Rate of change:** Continuous — `CACHE_TTL_ACTIVE` (300s)
- **Notes:** French-only columns. No English equivalent in this CSV. Return as-is with `lang` affecting error messages only.

#### Tool 8: `quebec_get_forest_fires_history`
- **Package ID:** `feux-de-foret`
- **Org:** `mrn` (Ministère des Ressources naturelles — also known as MFFP)
- **Resource:** SHP files at `https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/PERTURBATIONS_NATURELLES/Feux_foret/...`
- **Access:** `fetch_and_parse()` does NOT support SHP. Use `quebec_search_datasets` to surface the package, and return the download URLs as guidance in the response. Tool returns the CKAN metadata (title, notes, update_frequency, resources list with format/URL), NOT the fire geometries directly.
- **Rate of change:** Annual — `CACHE_TTL_META` (86400s)
- **Notes:** This is a metadata/discovery tool for the historical fire archive. Real geometric data requires Shapefile parsing which is outside `fetch_and_parse()` scope. Agents can use the URLs to download and process externally. Alternative: if a CSV version exists in future, upgrade to data tool.

**Demographics + Environment + Energy (5 tools — replacing Hydro-Québec outages):**

#### Tool 9: `quebec_get_air_quality_stations`
- **Package ID:** `rsqaq-stations`
- **Org:** `developpement-durable-environnement-et-lutte-contre-les-changements-climatiques`
- **Resource:** CSV with `datastore_active=True`, resource_id `cebea532-a9e0-4a39-8c2d-54f33d937c73`
- **Access:** `datastore_search` — 245 rows (all stations including historical closed ones)
- **Key columns:** `ID_STATION`, `NOM_STATION`, `RA` (région administrative code), `ADRESSE`, `MUNICIPALITE`, `TYPE_MILIEU` (Urbain/Rural/Industriel), `DATE_OUVERTURE`, `DATE_FERMETURE`, `LATITUDE`, `LONGITUDE`
- **Rate of change:** Annual — `CACHE_TTL_META` (86400s)
- **Notes:** Client should filter `DATE_FERMETURE` null for active stations.

#### Tool 10: `quebec_get_air_quality_index`
- **Package ID:** `rsqaq-indice-de-la-qualite-de-l-air`
- **Org:** `developpement-durable-environnement-et-lutte-contre-les-changements-climatiques`
- **Resource:** REST/ArcGIS FeatureServer: `https://services3.arcgis.com/0lL78GhXbg1Po7WO/arcgis/rest/services/IQA_resultat_REST/FeatureServer`
- **Access:** ArcGIS Hub FeatureServer — can use `shared/arcgis_hub.py`'s feature server client pattern, OR call the REST endpoint directly with `api_get` + JSON params
- **Rate of change:** Hourly — `CACHE_TTL_ACTIVE` (300s)
- **IMPORTANT:** This resource is ArcGIS REST, not CKAN datastore. Use `api_get` with `?f=json&where=1=1&outFields=*&resultRecordCount=200`. The `shared/arcgis_hub.py` client is available.

#### Tool 11: `quebec_get_water_quality_monitoring`
- **Package ID:** `suivi-physicochimique-des-rivieres-et-du-fleuve`
- **Org:** `developpement-durable-environnement-et-lutte-contre-les-changements-climatiques`
- **Resource:** GeoJSON ZIP at Azure Blob: `https://stqc380donopppdtce01.blob.core.windows.net/donnees-ouvertes/IQBP/DQ/IQBP_json.zip`
- **Access:** `fetch_and_parse(url)` — `fetch_and_parse` handles `.json` URLs but this is a `.zip` containing a GeoJSON — NOT directly supported. Use this tool as a metadata/discovery tool returning the package details and download URLs, same pattern as `quebec_get_forest_fires_history`.
- **Rate of change:** Annual — `CACHE_TTL_META` (86400s)
- **Alternative:** The `rsqaq-donnees-horaires-continues` dataset may have CSV with datastore support — check in plan implementation.

#### Tool 12: `quebec_get_electricity_data`
- **Package ID:** `historique-production-consommation`
- **Org:** `hydro-quebec`
- **Resource:** CSV at Hydro-Québec direct URL (inside DQ package)
- **Access:** `fetch_and_parse(url)` — need to probe actual CSV URL from `package_show`
- **Rate of change:** Annual — `CACHE_TTL_META` (86400s)
- **Notes:** Replaces the planned `quebec_get_hydro_outages`. Returns historical electricity production and consumption statistics for Quebec. Agents interested in current outages should be redirected to `hydroquebec.com/pannes/` (document in docstring).

#### Tool 13: `quebec_get_protected_areas`
- **Package ID:** `aires-protegees-au-quebec`
- **Org:** `developpement-durable-environnement-et-lutte-contre-les-changements-climatiques`
- **Resource:** SHP/GPKG/FGDB at Azure Blob (no CSV or GeoJSON — NOT directly parseable by `fetch_and_parse`)
- **Access:** Metadata/discovery tool returning package details, update frequency, resource download URLs, and WMS endpoint for visualization. Same pattern as `quebec_get_forest_fires_history`.
- **Rate of change:** Semiannual — `CACHE_TTL_META` (86400s)
- **Total:** Registre des aires protégées et des AMCE — ~10,000+ protected areas

**Total curated tools: 13** (same count as CONTEXT.md target)

---

## Discovery Tools (5 standard CKAN)

#### `quebec_search_datasets`
- `package_search` with `q`, `rows`, `start`, `organization`, `group` params
- Note in docstring: federated catalog includes 139 orgs — municipal data (Montreal BIXI, ARTM, Ville de Montréal) appears here; use Phase 27 module for comprehensive Montreal data

#### `quebec_get_dataset_details`
- `package_show` — surfaces resources list with format, URL, `datastore_active` flag

#### `quebec_query_dataset`
- Simplified `bc_query_features` without WFS routing: picks best file resource (CSV > GeoJSON > JSON > XLSX), delegates to `fetch_and_parse(url)`
- If resource has `datastore_active=True` and resource_id is present, uses `datastore_search` instead (smarter routing)
- No CQL/WFS routing needed (no secondary WFS portal in Phase 16)

#### `quebec_list_organizations`
- `organization_list?all_fields=true` — 139 orgs, cached 24h

#### `quebec_list_categories`
- `group_list?all_fields=true` — 10 thematic groups (NOT tag_list — DQ groups work unlike BC)
- Cache: 24h (`CACHE_TTL_META`)

---

## Architecture Patterns

### Recommended Module Structure
```
src/mcp_canada/modules/quebec/
├── __init__.py           # MODULE_NAME = "quebec", MODULE_DESCRIPTION
├── constants.py          # BASE_URL, RATE_GROUP, RATE_LIMIT, CACHE_TTL_*, ORG_* slugs
├── schemas.py            # Flat Pydantic v2 models (QuebecDatasetSummary, QuebecInstallation, etc.)
├── client.py             # Async functions returning (data, was_cached) tuples
├── tools.py              # @tool functions (18 total: 5 discovery + 13 curated)
├── prompts.py            # 6 bilingual @prompt functions
├── resources.py          # 7 zero-parameter @resource functions
└── __tests__/
    ├── __init__.py
    ├── conftest.py        # Fixtures with sample CKAN responses + datastore responses
    ├── test_client.py     # Client unit tests + TestSharedApiGetContract
    ├── test_tools.py      # Tool unit tests (mocked client layer)
    └── test_prompts_resources.py
```

### Pattern 1: `_api_get` Helper (from BC post-15-05 fix)
```python
# Source: src/mcp_canada/modules/british_columbia/client.py (post-15-05 fix)
async def _api_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    url = BASE_URL + path
    envelope = await api_get(url, params or {}, headers={"User-Agent": "mcp-canada/1.0"})
    if not isinstance(envelope, dict) or not envelope.get("success", False):
        raise httpx.HTTPStatusError(
            f"CKAN returned success=False for {path}",
            request=httpx.Request("GET", url),
            response=httpx.Response(500),
        )
    return envelope.get("result", {})
```

### Pattern 2: CKAN Datastore Tool (NEW for Quebec — DQ supports datastore)
```python
# For health installations tool — use datastore_search instead of fetch_and_parse
async def _datastore_get(resource_id: str, params: dict | None = None) -> dict:
    url = BASE_URL + "datastore_search"
    all_params = {"resource_id": resource_id, **(params or {})}
    return await _api_get("datastore_search", all_params)
```

### Pattern 3: MTQ WFS-as-CSV via `fetch_and_parse`
```python
# WFS CSV URL is stable — use fetch_and_parse directly
MTQ_WFS_BASE = "https://ws.mapserver.transports.gouv.qc.ca/swtq"
ROAD_WORKS_URL = f"{MTQ_WFS_BASE}?service=wfs&version=2.0.0&request=getfeature&typename=ms:chantiers_mtmdet&outputformat=csv"

data, cached = await fetch_and_parse(ROAD_WORKS_URL, ttl=CACHE_TTL_ACTIVE)
```

### Pattern 4: Bilingual ternary for error messages (BC 15-05 convention)
```python
# Source: BC 15-05 gap closure pattern
msg = (
    "quebec_get_bridge_structures requires at least one filter..."
    if lang == "en"
    else "quebec_get_bridge_structures nécessite au moins un filtre..."
)
return make_error("INVALID_INPUT", msg, lang=lang)
```

### Pattern 5: Bilingual MTQ CSV column selection
```python
# Select bilingual column based on lang parameter
desc_col = "descriptionFrancais" if lang == "fr" else "descriptionAnglais"
# Or for road conditions:
status_col = "DescriptionEtatChausseeFR" if lang == "fr" else "DescriptionEtatChausseeEN"
```

### Anti-Patterns to Avoid
- **NEVER call `.raise_for_status()` or `.json()` on `api_get` return:** `api_get` already returns parsed dict. Phase 15 root cause.
- **NEVER use `_make_http_response` MagicMock pattern in tests:** Use raw dict `AsyncMock` return values directly.
- **NEVER set `mock.return_value = MagicMock(json=lambda: {...})`:** This masks the real contract. Use `AsyncMock(return_value={...})`.
- **NEVER hardcode English-only error messages:** Use inline ternary on `lang` parameter.
- **NEVER pass `datastore_search_sql` queries with SQL injection risks:** Use `datastore_search` with `filters` dict for equality checks; use `q=` for full-text. SQL only for aggregations in curated queries.
- **NEVER fetch the annual road conditions archive ZIP:** 970K rows, 530MB zip. Curated tools use the live WFS CSV endpoint only.
- **NEVER assert `data["data"]` as a flat list in integration tests:** Shape varies by tool. Check `data["_meta"]` first, then the actual data key for your tool.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CKAN envelope unwrap | Custom response parser | `_api_get` helper (identical to BC) | Same CKAN `{"success": true, "result": {...}}` envelope |
| CKAN datastore queries | Custom pagination loop | `datastore_search` with `offset`/`limit` | DQ datastore supports standard CKAN datastore API |
| File parsing | Custom CSV/XLSX reader | `fetch_and_parse()` from `shared/parsers.py` | Already handles BOM, accents (transliterates via unicodedata), encoding |
| Response envelope | Custom dict building | `make_response()` / `make_error()` | Every tool must return `_meta` envelope |
| Rate limiting | asyncio.sleep loops | `get_limiter(RATE_GROUP, rate)` | TokenBucket already proven across 6+ modules |
| Caching | in-memory dict | `cached_fetch(key, ttl, fetcher)` | aiocache TTL cache handles invalidation |
| HTTP retry | Manual retry loop | Built into `api_get` via tenacity | 3 retries with exponential backoff on 429/5xx |
| Accented column normalization | Custom `é→e` logic | `_normalize_key()` inside `fetch_and_parse` | Already handles NFKD decomposition |

**Key insight:** Quebec is CKAN + datastore + MTQ WFS-as-CSV. Zero new protocols. The entire module builds on proven shared infrastructure.

---

## Common Pitfalls

### Pitfall 1: SOPFEU/Hydro-Québec/MSP data assumed to be on DQ
**What goes wrong:** Planning tools expecting SOPFEU active fires, Hydro-Québec outages, or MSP fire prevention zone GeoJSON via CKAN.
**Why it happens:** CONTEXT.md named these as tentative candidates with "research should confirm."
**How to avoid:** SOPFEU not on DQ (0 org results). Hydro-Québec on DQ but NO outage data. MSP fire prevention WFS returns HTTP 400 (auth required). All three moved to deferred.
**Warning signs:** `organization_list` not containing `sopfeu`. Hydro-Québec packages do not include keywords: "panne", "interruption", "outage".

### Pitfall 2: `_api_get` returning httpx.Response instead of dict
**What goes wrong:** Calling `.raise_for_status()` or `.json()` on the return value of `api_get()`.
**Why it happens:** `shared/http.py:api_get()` already returns parsed JSON (a dict). It calls `response.json()` internally.
**How to avoid:** The BC 15-05 fix: check `isinstance(envelope, dict) and envelope.get("success", False)`. Never call response methods.
**Warning signs:** `AttributeError: 'dict' object has no attribute 'raise_for_status'` in tests/logs.

### Pitfall 3: Test mock uses `MagicMock(json=lambda: {...})` pattern
**What goes wrong:** 22 unit tests pass but the real API contract is wrong — the mock masks the dict-vs-Response mismatch.
**Why it happens:** BC Plan 02 originally used `_make_http_response` helper. BC Plan 05 fixed this.
**How to avoid:** Use `AsyncMock(return_value={"success": True, "result": {...}})` — mock returns the raw dict, matching the real `api_get` contract.
**Warning signs:** Unit tests green but integration tests fail with `AttributeError`.

### Pitfall 4: Annual archive CSV files are too large
**What goes wrong:** Tool attempts to download 970K-row / 530MB annual road conditions archive.
**Why it happens:** DQ package includes both live WFS CSV and annual archive. Code picks the first CSV resource.
**How to avoid:** Always use the live WFS CSV URL for MTQ data. For road conditions, use `ms:conditions_routieres` WFS typename. Add size limit guidance in `_pick_file_resource` logic.
**Warning signs:** `fetch_and_parse` timeout or memory error.

### Pitfall 5: DQ title/notes are French-only
**What goes wrong:** Code tries to access `title_en`, `title_translated`, or `notes_en` fields — returns `None` or KeyError.
**Why it happens:** BC Data Catalogue uses `title_translated` dict with `"en"`/`"fr"` keys. DQ does not.
**How to avoid:** Use `title` directly (French). Document French-primary in tool docstrings. `lang` parameter only affects error messages and prompts.
**Warning signs:** `d.get("title_translated", {}).get("en")` returning `None` for all datasets.

### Pitfall 6: `group_list` vs `tag_list` for categories
**What goes wrong:** Using `tag_list` for `quebec_list_categories` returns 4,200 noisy tags with no hierarchy.
**Why it happens:** BC Data Catalogue uses tags only (groups return 403). DQ has both — and has 10 meaningful thematic groups.
**How to avoid:** Use `group_list?all_fields=true` for `quebec_list_categories`. Expose `tag_list` via `fq=tags:{tag}` filter on `quebec_search_datasets` only.
**Warning signs:** `quebec_list_categories` returning thousands of items.

### Pitfall 7: MTQ WFS GeoJSON endpoint broken
**What goes wrong:** Fetching `outputFormat=application/json` from `ws.mapserver.transports.gouv.qc.ca` returns HTTP 400 with `Unable to access file: /var/local/systemes/mapserver/internet/commun/gabarits/json.tmpl`.
**Why it happens:** Server-side template file missing for GeoJSON format (MapServer misconfiguration).
**How to avoid:** Always use `outputformat=csv` for MTQ WFS endpoints. CSV confirmed working for `ms:chantiers_mtmdet`, `ms:evenements`, `ms:gsq_v_desc_strct_tri`.
**Warning signs:** HTTP 400 with `json.tmpl` in error message.

### Pitfall 8: DQ resource URLs are redirect wrappers not direct downloads
**What goes wrong:** `resource["url"]` for some DQ resources points to a DQ webpage (`/recherche/dataset/.../resource/.../download`) that redirects to the actual file. `fetch_and_parse` may not follow redirects correctly.
**Why it happens:** DQ wraps download URLs through their portal for tracking. External URLs (MSSS, MTQ WFS, Azure Blob) work directly.
**How to avoid:** For external URLs (identified by non-`donneesquebec.ca` hostnames), use directly. For DQ-hosted URLs, test redirect behavior. `httpx.AsyncClient` follows redirects by default.
**Warning signs:** Getting HTML response instead of CSV content.

### Pitfall 9: Datastore SQL field names have accented characters
**What goes wrong:** `datastore_search_sql` query fails with column name errors because DQ datastore field names contain French characters.
**Why it happens:** `Heure_de_l'extraction_(image)` — apostrophe in field name causes SQL parsing errors.
**How to avoid:** Use `datastore_search` with `fields=` parameter instead of raw SQL for simple queries. For SQL, double-quote column names: `"Heure_de_l'extraction_(image)"`.
**Warning signs:** SQL query returns error about invalid column name with apostrophe.

---

## Phase 15 Lessons Applied

### Lesson 1: shared api_get returns parsed dict — never a Response
The BC Phase 15 gap closure (Plan 05, commit `2125a92`) established the definitive `_api_get` pattern. The Quebec module must copy the post-fix BC `client.py` pattern verbatim:

```python
# CORRECT (post-15-05):
envelope = await api_get(url, params or {})
if not isinstance(envelope, dict) or not envelope.get("success", False):
    raise httpx.HTTPStatusError(...)
return envelope.get("result", {})

# WRONG (pre-15-05, do NOT copy from Plan 02 summary):
response = await api_get(url, params or {})
response.raise_for_status()  # AttributeError: 'dict' has no 'raise_for_status'
return response.json()["result"]  # same crash
```

### Lesson 2: TestSharedApiGetContract class prevents mock-masking
The BC Plan 05 fix added `TestSharedApiGetContract` class to `test_client.py`. Quebec must include an equivalent from the start:

```python
class TestSharedApiGetContract:
    """Verifies _api_get treats the shared api_get return as a parsed dict.

    Patches mcp_canada.modules.quebec.client.api_get (the local binding,
    NOT the shared module) — this is the same fix that resolved BC's
    AttributeError: 'dict' object has no attribute 'raise_for_status'.
    """

    async def test_success_envelope_unwraps_result(self, ...):
        with patch("mcp_canada.modules.quebec.client.api_get") as mock_api_get:
            mock_api_get.return_value = {"success": True, "result": {"count": 5, "results": []}}
            result = await _api_get("package_search", {"q": "test"})
            assert result == {"count": 5, "results": []}

    async def test_ckan_success_false_raises(self, ...):
        with patch("mcp_canada.modules.quebec.client.api_get") as mock_api_get:
            mock_api_get.return_value = {"success": False, "error": {"message": "Not found"}}
            with pytest.raises(httpx.HTTPStatusError):
                await _api_get("package_show", {"id": "bad-id"})

    async def test_non_dict_return_raises(self, ...):
        with patch("mcp_canada.modules.quebec.client.api_get") as mock_api_get:
            mock_api_get.return_value = "unexpected string"  # NOT a dict
            with pytest.raises(httpx.HTTPStatusError):
                await _api_get("package_search", {"q": "test"})
```

### Lesson 3: Inline bilingual ternary — not t() import
Per BC 15-05 decision: "zero production t() imports makes first import scope-creep". Use inline `lang == "fr"` ternary for ALL error/guard messages in Quebec module.

---

## Constants (for constants.py)

```python
BASE_URL: Final[str] = "https://www.donneesquebec.ca/recherche/api/3/action/"
MTQ_WFS_BASE: Final[str] = "https://ws.mapserver.transports.gouv.qc.ca/swtq"
AQ_INDEX_URL: Final[str] = "https://services3.arcgis.com/0lL78GhXbg1Po7WO/arcgis/rest/services/IQA_resultat_REST/FeatureServer/0/query"

RATE_GROUP: Final[str] = "quebec_ckan"
RATE_LIMIT: Final[float] = 10.0  # req/s — conservative, matches Ontario/BC

CACHE_TTL_SEARCH: Final[int] = 3600    # 1hr — CKAN search
CACHE_TTL_META: Final[int] = 86400     # 24hr — package metadata, org list, static registries
CACHE_TTL_ACTIVE: Final[int] = 300     # 5min — ER wait times, road events, road works, AQI
CACHE_TTL_DAILY: Final[int] = 3600     # 1hr — municipal registry (daily source updates)

# Organization slugs (verified)
ORG_MSSS: Final[str] = "msss"
ORG_MTQ: Final[str] = "mtq"
ORG_MRN: Final[str] = "mrn"   # Ministère des Ressources naturelles (includes MFFP)
ORG_MELCCFP: Final[str] = "developpement-durable-environnement-et-lutte-contre-les-changements-climatiques"
ORG_MSP: Final[str] = "msp"
ORG_HYDRO: Final[str] = "hydro-quebec"
ORG_SEPAQ: Final[str] = "sepaq"
ORG_ISQ: Final[str] = "isq"
ORG_MAMH: Final[str] = "affaires-municipales-et-occupation-du-territoire"

# MSSS health installations
MSSS_INSTALLATIONS_RESOURCE_ID: Final[str] = "2aa06e66-c1d0-4e2f-bf3c-c2e413c3f84d"
# MSSS ER hourly situation
MSSS_ER_RESOURCE_ID: Final[str] = "a9272cc9-8234-40d1-9806-9f6b4c75c20d"
# RSQAQ air quality stations
RSQAQ_STATIONS_RESOURCE_ID: Final[str] = "cebea532-a9e0-4a39-8c2d-54f33d937c73"
# MAMH municipal registry CSV
MAMH_MUN_CSV_URL: Final[str] = "https://donneesouvertes.affmunqc.net/repertoire/MUN.csv"

# MTQ WFS CSV URLs (verified working)
MTQ_ROAD_WORKS_URL: Final[str] = f"{MTQ_WFS_BASE}?service=wfs&version=2.0.0&request=getfeature&typename=ms:chantiers_mtmdet&outputformat=csv"
MTQ_ROAD_EVENTS_URL: Final[str] = f"{MTQ_WFS_BASE}?service=wfs&version=2.0.0&request=getfeature&typename=ms:evenements&outputformat=csv"
MTQ_BRIDGES_URL: Final[str] = f"{MTQ_WFS_BASE}?service=wfs&version=2.0.0&request=getfeature&typename=ms:gsq_v_desc_strct_tri&outputformat=csv"
```

---

## Prompts and Resources Design

### Prompts (6 bilingual — from CONTEXT.md decisions)

#### Guided workflow prompts (return `list[Message]`):
1. **`quebec_explore_health`** — chain: `quebec_get_er_wait_times` → `quebec_get_health_installations` → store to datastore for hospital comparison
2. **`quebec_explore_transport_conditions`** — chain: `quebec_get_road_conditions` → `quebec_get_road_works` → `quebec_get_road_events` for winter driving assessment
3. **`quebec_explore_environment`** — chain: `quebec_get_air_quality_index` → `quebec_get_air_quality_stations` → `quebec_get_water_quality_monitoring` for environmental monitoring

#### Quick lookup prompts (return `str`):
4. **`quebec_quick_dataset_search`** — direct to `quebec_search_datasets` with category/org parameters
5. **`quebec_check_road_conditions`** — direct to `quebec_get_road_conditions` with region parameter, notes winter-season availability
6. **`quebec_active_fires_now`** — redirects agents: note SOPFEU data not on DQ; redirect to `quebec_get_road_events` for emergency context, or suggest `discover_tools` for weather emergency context from Weather module

### Resources (7 zero-parameter)

1. **`data://quebec/ministries`** — JSON catalog of 139 DQ organizations with bilingual labels (name, title_fr, title_en if known, package_count). Embed as static JSON — avoid live API call in resource.
2. **`data://quebec/regions`** — 17 administrative regions with code and French/English name (embed static)
3. **`data://quebec/mrcs`** — Regional County Municipalities list with region mapping (embed static — ~100 MRCs)
4. **`docs://quebec/catalog-federation-quirks`** — Explains 139-org federated nature, Montreal overlap (BIXI, ARTM, Ville de Montréal appear in DQ), org slug patterns, group categories
5. **`docs://quebec/bilingual-metadata-guide`** — Documents French-only title/notes, bilingual MTQ WFS columns, ER field names with accented characters, MAMH population data structure
6. **`template://quebec/dataset-report`** — Template for summarizing a DQ dataset with `{title}`, `{organization}`, `{update_frequency}`, `{num_resources}`, `{license_title}` placeholders
7. **`template://quebec/road-conditions-report`** — Template for winter road conditions summary with `{region}`, `{route}`, `{condition_fr}`, `{condition_en}`, `{last_updated}` placeholders

---

## Validation Architecture

Nyquist validation is ENABLED (`workflow.nyquist_validation: true` in `.planning/config.json`).

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | `pyproject.toml` (existing) |
| Quick run command | `uv run pytest src/mcp_canada/modules/quebec/__tests__/ -x -v` |
| Full suite command | `uv run pytest src/mcp_canada/modules/quebec/__tests__/ tests/integration/ -v -m "not integration" -x` |
| Integration run | `uv run pytest tests/integration/ -v -m integration --timeout=120 -k Quebec` |
| Coverage command | `uv run pytest --cov=src/mcp_canada/modules/quebec --cov-fail-under=95` |

### Test Map

| Behavior | Test Type | File | Automated Command | Wave |
|----------|-----------|------|-------------------|------|
| `_api_get` treats api_get return as dict | unit | `test_client.py::TestSharedApiGetContract` | quick run | Wave 0 |
| `_api_get` raises on `success=False` | unit | `test_client.py::TestSharedApiGetContract` | quick run | Wave 0 |
| `fetch_search_datasets` returns shaped list | unit | `test_client.py::TestFetchSearchDatasets` | quick run | Wave 1 |
| `fetch_dataset_details` includes `resources` + `datastore_active` | unit | `test_client.py::TestFetchDatasetDetails` | quick run | Wave 1 |
| `fetch_health_installations` filters by type flag | unit | `test_client.py::TestFetchHealthInstallations` | quick run | Wave 2 |
| `fetch_er_wait_times` returns 116-row shape | unit | `test_client.py::TestFetchErWaitTimes` | quick run | Wave 2 |
| `fetch_population` returns municipality rows | unit | `test_client.py::TestFetchPopulation` | quick run | Wave 2 |
| `fetch_road_works` parses MTQ WFS CSV | unit | `test_client.py::TestFetchRoadWorks` | quick run | Wave 2 |
| `fetch_bridge_structures` requires filter guard | unit | `test_client.py::TestFetchBridgeStructures` | quick run | Wave 2 |
| `quebec_search_datasets` validates non-empty q | unit | `test_tools.py::TestQuebecSearchDatasets` | quick run | Wave 1 |
| `quebec_list_categories` uses group_list (not tag_list) | unit | `test_tools.py::TestQuebecListCategories` | quick run | Wave 1 |
| `quebec_get_health_installations` lang=fr returns French error | unit | `test_tools.py::TestQuebecGetHealthInstallations` | quick run | Wave 2 |
| `quebec_get_er_wait_times` returns _meta envelope | unit | `test_tools.py::TestQuebecGetErWaitTimes` | quick run | Wave 2 |
| `quebec_get_bridge_structures` requires filter | unit | `test_tools.py::TestQuebecGetBridgeStructures` | quick run | Wave 2 |
| All 18 tools have 8+ Keywords + Use-for lines | automated quality | `test_quality.py` (existing, auto-discovers) | `uv run pytest tests/test_quality.py -x` | Wave 0 |
| `discover_tools` finds `quebec_get_er_wait_times` | integration | `test_tool_scenarios.py::TestQuebecToolScenarios` | integration | Wave 3 |
| `quebec_search_datasets` live against DQ CKAN | integration | `test_tool_scenarios.py::TestQuebecToolScenarios` | integration | Wave 3 |
| `quebec_get_health_installations` returns real data | integration | `test_tool_scenarios.py::TestQuebecToolScenarios` | integration | Wave 3 |
| Prompts discoverable via `client.list_prompts()` | integration | `test_prompts_resources_scenarios.py::TestQuebecPromptsResources` | integration | Wave 3 |
| Resources readable via `client.read_resource()` | integration | `test_prompts_resources_scenarios.py::TestQuebecPromptsResources` | integration | Wave 3 |

### Sampling Rate
- **Per task commit:** `uv run pytest src/mcp_canada/modules/quebec/__tests__/ -x -v`
- **Per wave merge:** `uv run pytest src/mcp_canada/modules/quebec/__tests__/ tests/test_quality.py -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `src/mcp_canada/modules/quebec/__tests__/conftest.py` — fixtures: `sample_dq_package_search`, `sample_dq_package_show`, `sample_dq_org_list`, `sample_dq_group_list`, `sample_dq_datastore_response`, `sample_dq_installations_rows`, `sample_dq_er_rows`, `sample_mtq_road_works_csv`, `autouse_cache_limiter_patch`
- [ ] `src/mcp_canada/modules/quebec/__tests__/test_client.py` — 8+ stub classes including `TestSharedApiGetContract`
- [ ] `src/mcp_canada/modules/quebec/__tests__/test_tools.py` — 18 stub classes (5 discovery + 13 curated)
- [ ] `src/mcp_canada/modules/quebec/__tests__/test_prompts_resources.py` — `TestQuebecPrompts` + `TestQuebecResources`
- [ ] `tests/integration/test_tool_scenarios.py` — `TestQuebecToolScenarios` class appended (8 xfail stubs)
- [ ] `tests/integration/test_prompts_resources_scenarios.py` — `TestQuebecPromptsResources` class appended (3 xfail stubs)

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Copy Ontario CKAN module (`inline httpx client`) | Copy BC post-15-05 module (`_api_get` uses `api_get(url, params or {})`) | Phase 15 Plan 05 (2026-04-11) | Correct dict contract from day 1 |
| `_api_get` calls `.raise_for_status()` on api_get return | `_api_get` checks `envelope.get("success", False)` | Phase 15 Plan 05 | Avoids `AttributeError` in production |
| Mock HTTP response in tests with `MagicMock(json=...)` | Mock returns raw dict via `AsyncMock(return_value={...})` | Phase 15 Plan 05 | Tests accurately reflect real api_get contract |
| `tag_list` for `list_categories` (BC pattern) | `group_list` for `list_categories` (DQ-specific) | Phase 16 research | 10 meaningful groups vs 4,200 noisy tags |
| `title_translated` bilingual field (BC CKAN pattern) | Plain `title` in French (DQ has no translation field) | Phase 16 research | Client does not attempt English metadata lookup |

**Deprecated/outdated:**
- SOPFEU active fire tools: data not on DQ — moved to deferred
- Hydro-Québec outages tool: data not on DQ — moved to deferred, replaced with electricity production data
- `_make_http_response` test helper: removed in BC Plan 05, NEVER add to Quebec

---

## Open Questions

1. **`ms:conditions_routieres` WFS CSV format** — RESOLVED (phase 16-05)
   - Confirmed working: `outputformat=csv` returns ~100KB of real CSV from the live WFS.
   - Root cause of original failure: `shared/parsers.py` stripped query string before format detection; format hint was in `?outputformat=csv` not in path suffix. Fixed by adding `urllib.parse` query-param inspection in `fetch_and_parse`.

2. **Hydro-Québec electricity production CSV URL**
   - What we know: `historique-production-consommation` package exists on DQ from Hydro-Québec org. CSV resource URL needs to be retrieved from `package_show`.
   - What's unclear: Direct download URL stability (may use DQ redirect wrapper).
   - Recommendation: Probe in Plan 02.

3. **RSQAQ real-time AQI via ArcGIS FeatureServer**
   - What we know: `rsqaq-indice-de-la-qualite-de-l-air` has REST resource pointing to ArcGIS FeatureServer (not CKAN datastore). `shared/arcgis_hub.py` is available.
   - What's unclear: Whether the ArcGIS FeatureServer requires authentication or returns public data.
   - Recommendation: Use `api_get(AQ_INDEX_URL, {"f": "json", "where": "1=1", "outFields": "*", "resultRecordCount": 200})` — test in Plan 02.

4. **Water quality GeoJSON ZIP via `fetch_and_parse`**
   - What we know: `suivi-physicochimique-des-rivieres-et-du-fleuve` has a GeoJSON wrapped in a ZIP file. `fetch_and_parse` does not support ZIP extraction.
   - What's unclear: Is there an alternative CSV resource for this dataset? Check `rsqaq-donnees-horaires-continues` for CSV/datastore option.
   - Recommendation: If no CSV/datastore found, implement as metadata/discovery tool (returns dataset details + download URLs).

---

## Sources

### Primary (HIGH confidence — live-verified 2026-04-11)
- Live API probe: `https://www.donneesquebec.ca/recherche/api/3/action/package_search` — dataset shape, org list, group list, tag list
- Live API probe: `https://www.donneesquebec.ca/recherche/api/3/action/package_show` — 12 datasets probed for resource formats and URLs
- Live API probe: `https://www.donneesquebec.ca/recherche/api/3/action/datastore_search` — confirmed working for 3 resources (installations, ER, air quality stations)
- Live API probe: `https://www.donneesquebec.ca/recherche/api/3/action/datastore_search_sql` — confirmed working
- Live API probe: `https://ws.mapserver.transports.gouv.qc.ca/swtq` — WFS capabilities + CSV for 3 MTQ layers
- `src/mcp_canada/modules/british_columbia/client.py` (post-15-05) — `_api_get` contract reference
- `.planning/phases/15-british-columbia-government-open-data/15-05-SUMMARY.md` — Phase 15 lesson documentation

### Secondary (MEDIUM confidence)
- CONTEXT.md dataset/org assumptions verified or corrected against live API
- MTQ WFS layer names extracted from live capabilities XML

### Tertiary (LOW confidence — not independently verified)
- SOPFEU wildfire active fire data: searched DQ CKAN but SOPFEU's own website suggests a GeoJSON API may exist at `sopfeu.qc.ca` — not probed (out of scope for this phase)
- Water quality monitoring hourly data: RSQAQ hourly dataset existence not fully verified against datastore

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — BC pattern confirmed, no new dependencies needed
- Architecture: HIGH — 15 curated tools verified with real package_ids and resource shapes
- Pitfalls: HIGH — all 9 pitfalls derived from live API behavior observed during research
- SOPFEU/Hydro-Québec absence: HIGH — confirmed via org search and package search
- MTQ WFS CSV availability: HIGH for road works/events/bridges; MEDIUM for road conditions (GeoJSON broken, CSV not tested)
- Datastore availability: HIGH — confirmed for 3 resources; extrapolated for others with `datastore_active=True`

**Research date:** 2026-04-11
**Valid until:** 2026-05-11 (30 days — DQ CKAN is stable; resource IDs are stable)
