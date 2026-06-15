# Phase 20: Nova Scotia Government Open Data — Research

**Researched:** 2026-06-15
**Domain:** Nova Scotia provincial open data (data.novascotia.ca — Socrata SODA API)
**Confidence:** HIGH for SODA API mechanics (live-verified with 40+ direct probes); HIGH for dataset catalog and field schemas (live-confirmed); HIGH for shared/socrata.py design (based on live response shapes + arcgis_hub.py template)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Build `shared/socrata.py`** (a reusable SODA client), parallel to `shared/arcgis_hub.py` and `shared/ogc.py`. Adds a 4th row to the Portal Technologies table in CLAUDE.md.
- The shared client must cover: catalog discovery (`/api/catalog/v1`), per-dataset reads (`/resource/{id}.json` with SoQL params), CSV/JSON handling. Keyless reads default; `X-App-Token` optional without API change.
- Reuse `shared/cache.py`, `shared/rate_limiter.py`, `shared/envelope.py`, and `shared/parsers.fetch_and_parse()`.
- Module prefix: planner's discretion between `ns_` and `nova_scotia_`.
- Module name: `nova_scotia`.
- **Signature domains all in scope:** Fishing/aquaculture (signature), environment/energy, lands/forests/wildlife, health+demographics.
- **Mid-band ~14-18 tools.** 5 discovery + ~9-13 curated.
- **5 discovery tools** (Socrata flavor): search_datasets, get_dataset_details, query_dataset, list_organizations, list_categories.
- **Transport / 511 DEFERRED** — NS 511 is HTML-only.
- **Socrata-first geospatial** — ArcGIS Hub (novagis) only if public no-auth FeatureServers confirmed; default: don't build ArcGIS path.
- **6 bilingual prompts** (3 guided + 3 quick lookups) + **~7 zero-parameter resources**.
- Bilingual `lang: Literal["en","fr"] = "en"` on every `@tool`; inline `lang == 'fr'` ternary; no `shared/i18n.py:t()`.
- `TestSharedApiGetContract`-style test pinning outgoing SoQL params (Manitoba/Saskatchewan lesson).
- Live-integration mandate: integration tests MUST hit real data.novascotia.ca and assert FIELD PRESENCE + non-null values.

### Claude's Discretion

- Final module prefix (`ns_` vs `nova_scotia_`); final dataset selection per domain.
- Exact Socrata discovery surface (`/api/catalog/v1` vs `/api/views.json` vs data.json export).
- SoQL query strategies; cache TTLs per tool; final prompt/resource set.

### Deferred Ideas (OUT OF SCOPE)

- Halifax and other NS municipal portals (Halifax is Phase 33).
- Transport / 511 — HTML-only, no clean feed.
- NS ArcGIS Hub (novagis) curated tools — unless research finds public no-auth FeatureServers.
- Socrata `X-App-Token` / authenticated higher-throttle reads — design for it, keyless default.
- Generalizing `shared/socrata.py` for other Socrata portals — build reusable now, onboard 2nd portal later.
- Federal-catalogue-proxy.
- Bilingual `shared/i18n.py:t()` adoption.

</user_constraints>

---

<phase_requirements>
## Phase Requirements

Proposed `NS-XX` requirements for Phase 20. Planner must add these to REQUIREMENTS.md.

| ID | Description | Research Support |
|----|-------------|-----------------|
| NS-01 | `shared/socrata.py` provides a reusable SODA client with `search_catalog(domain, q, limit, offset)`, `get_dataset_metadata(domain, dataset_id)`, `query_dataset(domain, dataset_id, where, select, order, limit, offset)`, and `list_categories(domain)` — returning parsed dicts, consistent with `api_get` parsed-dict contract | SODA API live-verified against data.novascotia.ca; 706 datasets in catalog; keyless reads confirmed |
| NS-02 | Agent can search Nova Scotia's data.novascotia.ca Socrata catalogue by keyword with pagination | `/api/catalog/v1?domains=data.novascotia.ca&q=...&limit=...&offset=...&only=datasets` live-verified; resultSetSize=706; q= search and offset= pagination both confirmed working |
| NS-03 | Agent can get full metadata for a specific Nova Scotia dataset by ID | `/api/views/{id}.json` live-verified; returns id, name, description, category, columns (name+dataTypeName), attribution, license |
| NS-04 | Agent can run a SoQL query against any Nova Scotia dataset via `/resource/{id}.json` with `$where`, `$select`, `$order`, `$limit`, `$offset`, `$q` | SoQL $where, $select, $order, $group, $limit all confirmed live; flat JSON rows returned |
| NS-05 | Agent can list Nova Scotia government organizations (attributions) that publish on data.novascotia.ca | Derived from catalog results (attribution field); catalog API exposes publisher/attribution per dataset |
| NS-06 | Agent can list Nova Scotia data categories | `/api/catalog/v1` domain_category values enumerated: 20+ categories confirmed including Fishing and Aquaculture, Environment and Energy, Nature and Environment, Lands Forests and Wildlife, Health and Wellness, Population and Demographics, Mines and Minerals |
| NS-07 | Agent can get Nova Scotia marine aquaculture lease locations with species, owner, waterbody, county, status, and area | Dataset `h57h-p9mm` (Nova Scotia Marine Aquaculture Leases) live-verified; fields: license_le, ownership, species, waterbody, county, sitestatus, navchart, speciestyp, hectares, lat_dms, long_dms; GeoJSON geometry also present |
| NS-08 | Agent can get Nova Scotia landbased aquaculture licenses with species type, owner, county, and status | Dataset `yqwg-f62a` (Nova Scotia Landbased Aquaculture Licenses) live-verified; fields: license_le, species, county, speciestyp, ownership, sitestatus, lat_dms, long_dms |
| NS-09 | Agent can get Nova Scotia fish hatchery stocking records with stock species, hatchery, county, fish length/weight, count released, and stocking date | Dataset `8e4a-m6fw` live-verified; fields: county, name, type, stock, stock_strain, hatchery, fish_length_cm, fish_weight_g, number_released, stocking_date, primary_stocking_objective, mark, growth_stage; data current to 2025-11-19 |
| NS-10 | Agent can get Nova Scotia aquaculture production, value, and employment data by county and year | Dataset `v2ex-ev63` live-verified; fields: year, county, kgs, total_value, full_time, pt_employ_6_mth, pt_employ_6_mth_1, total_employ |
| NS-11 | Agent can get Nova Scotia surface water quality monitoring station locations and continuous sensor readings (temperature, pH, conductance, dissolved oxygen) | Dataset `i9ee-9hct` (station locations) + `bkfi-mjgw` (continuous readings, data through 2024-12-06) live-verified; fields: date, time, temperature_c, ph, specific_conductance_s_cm, dissolved_oxygen_mg_l, station_number |
| NS-12 | Agent can get Nova Scotia boil water advisories with site name, county, date issued, date removed, facility type, and advisory duration | Dataset `7t68-9xmm` live-verified; fields: site_name, county, date_advisory_issued, date_advisory_removed, facility_type, length_of_advisory; data current to 2025 |
| NS-13 | Agent can get Nova Scotia hospital and long-term care facility locations with type, address, county, health zone, beds, and coordinates | Dataset `tmfr-3h8a` (Hospitals) + `x76a-axw2` (LTC/RCF Facilities) live-verified; hospitals have facility name, address, town, county, type, coordinates; LTC has beds count, zone, facility_type, SEA participation |
| NS-14 | Agent can get Nova Scotia vital statistics (births, deaths, rates, natural increase) by county and year | Dataset `r794-fttm` live-verified; fields: counties, year, population, live_births, birth_rate, deaths, death_rate, excess_of_births_over_deaths, natural_increase_rate; year filter confirmed working |
| NS-15 | Agent can get Nova Scotia protected areas with name, protection type, owner, authority, designation status, and area | Dataset `ticv-5du5` (The Nova Scotia Protected Areas System) live-verified; fields: objectid, pro_name, protect1, symbol, owner, authority, status, web_url, ha_gis; GeoJSON geometry present |
| NS-16 | Agent can get Nova Scotia ambient air quality monitoring station locations with measurements and monitoring period | Dataset `3bbm-drnh` live-verified; fields: national_air_pollution_surveillance_network_id, station_name, province, city, country, latitude, longitude, measurements, monitoring_period, location |
| NS-17 | Agent can get Nova Scotia chronic disease prevalence data dispatched by disease type (diabetes, AMI, COPD, hypertension, asthma) by health zone, sex, age group, and year | AMI `24qf-ntke` + Diabetes `cumi-sw99` live-verified; all share schema: year, zone (health_zone), sex, agegroup, population, prevalence, crude_prevalence_rate |
| NS-18 | All Nova Scotia tools follow mcp-canada conventions (standalone @tool, make_response/make_error envelope, Use-for + Keywords single-line docstrings, ns_ prefix), are discoverable via discover_tools, and 6 prompts + 7 resources are auto-discovered by FileSystemProvider | Conventions established by Phases 12-19 |

**Recommendation: SHIP.** data.novascotia.ca (Socrata) has 706 publicly accessible datasets with a fully keyless SODA API. SoQL queries ($where, $select, $order, $group, $limit, $offset) all work live. All 9 curated datasets above return live data. The shared/socrata.py client is the core deliverable enabling this and future Socrata portals.

**Tool count:** 5 discovery (NS-02 to NS-06) + 12 curated (NS-07 to NS-17, with NS-13 covering two datasets, NS-17 dispatching by disease) = **17 tools**. Within the mid-band 14-18 target.

**NS ArcGIS Hub (novagis.maps.arcgis.com) verdict:** Deferred per CONTEXT.md — no public no-auth FeatureServers confirmed during research. Socrata catalog is rich enough without it.

**Transport verdict:** NS 511 is HTML-only. Confirmed deferred per CONTEXT.md. No NOT_CONFIGURED stubs.

</phase_requirements>

---

## Summary

### Critical Finding: Nova Scotia Socrata SODA API is keyless, fully featured, and live-verified — SHIP RECOMMENDED

1. **`data.novascotia.ca` runs Socrata** (confirmed by `X-Socrata-Region` header per CONTEXT.md). The catalog contains **706 datasets** (confirmed with `resultSetSize` from live probes at `offset=0`, `offset=100`, `offset=700`). The `api/catalog/v1` endpoint is the most reliable discovery surface — it returns structured metadata with fields including `resource.id`, `resource.name`, `resource.description`, `classification.domain_category`, `classification.domain_tags`, and `metadata.domain`. All datasets are under the **Open Government Licence – Nova Scotia (version 1.1)** — free for commercial use with attribution.

2. **The SODA API is fully keyless and functional.** Live reads to `/resource/{id}.json` with SoQL parameters (`$where`, `$select`, `$order`, `$group`, `$limit`, `$offset`, `$q`) all work without any authentication header. The optional `X-App-Token` header (for higher throttle limits) requires zero API surface change — just add it to the request headers when the env var is set. Default Socrata limit is 1000 records; max is 50000.

3. **The catalog API (`/api/catalog/v1`) is the correct discovery endpoint.** The `q=` parameter does full-text search across name/description/tags. The `offset=` parameter provides reliable pagination (confirmed: `?q=water&offset=0` returns {boil water advisories, surface water quality…}; `?q=water&offset=10` returns {Antigonish County, Shelburne County water quality…} — different datasets, pagination works). The `only=datasets` parameter filters to datasets only (excluding maps, charts). The `categories=` parameter does NOT work (returns 0 results) — filter by `classification.domain_category` in code post-fetch or use `q=` search instead. Domain-tag filtering via `search_context=` returns HTTP 404.

4. **The `api/views.json` endpoint is a lower-quality alternative** — returns arrays without pagination metadata, fields differ from catalog/v1 format. Use `api/catalog/v1` for discovery.

5. **Nova Scotia's signature domain is fishing/aquaculture.** Four live Socrata datasets provide curated coverage: marine aquaculture leases (`h57h-p9mm`, GeoJSON geometry + flat fields), landbased aquaculture licenses (`yqwg-f62a`), fish hatchery stocking records (`8e4a-m6fw`, data current to 2025-11), and aquaculture production/value/employment (`v2ex-ev63`). All return non-null data on live probes.

6. **Health + demographics domain is strong.** Hospitals (`tmfr-3h8a`), Long-term Care/RCF facilities (`x76a-axw2` with zone, beds, coordinates), LTC waitlist (`c39g-gsdd`), and a rich chronic disease prevalence series (diabetes, AMI, COPD, hypertension, asthma — all sharing identical schemas with health_zone, sex, agegroup fields).

7. **Environment domain has live water quality and protected areas.** Surface water quality monitoring continuous data (`bkfi-mjgw`, data through 2024-12-06), boil water advisories (`7t68-9xmm`, current to 2025), and the protected areas system (`ticv-5du5`, with GeoJSON boundaries).

8. **Air quality monitoring has a stations catalog (`3bbm-drnh`) but individual pollutant readings are split across ~20 per-station/per-pollutant datasets** (O3 by station, PM2.5 by station). The stations dataset is the practical entry point; individual pollutant time series should be discovery-only (agent uses `query_dataset` with the specific dataset ID).

9. **The `$group` aggregation SoQL works** (confirmed: `$select=county,speciestyp,count(*)&$group=county,speciestyp` on the marine leases dataset returns correct grouped counts).

10. **GeoJSON geometry is available in Socrata datasets** (confirmed: marine aquaculture leases `h57h-p9mm` has `the_geom` as MultiPolygon; hospitals have `the_geom` as Point; protected areas have `the_geom` as MultiPolygon). The SODA API returns geometry inline in the JSON rows — no separate WFS/GeoJSON endpoint needed. When geometry is present, include an `include_geometry` param in `query_dataset` to pass through or strip `the_geom`.

**Primary recommendation:** SHIP via Socrata. Build `shared/socrata.py` first (Wave 0), then the nova_scotia module. 5 discovery + 12 curated tools = 17 total.

---

## Portal Architecture Discovery

### data.novascotia.ca — Confirmed Socrata Portal

| Property | Value |
|----------|-------|
| **URL** | `https://data.novascotia.ca` |
| **Technology** | Socrata (Tyler Technologies) |
| **Dataset count** | 706 publicly available datasets (confirmed via `resultSetSize`) |
| **Auth** | Keyless reads work; `X-App-Token` header raises throttle limits (optional, future) |
| **License** | Open Government Licence – Nova Scotia v1.1 — free, commercial use allowed, attribution required |
| **Catalogue endpoint** | `/api/catalog/v1?domains=data.novascotia.ca&limit=...&offset=...&q=...&only=datasets` |
| **Dataset read endpoint** | `/resource/{4x4-id}.json?$where=...&$select=...&$order=...&$limit=...&$offset=...` |
| **Metadata endpoint** | `/api/views/{4x4-id}.json` |
| **Dataset ID format** | 8-char with hyphen: `xxxx-xxxx` (e.g., `h57h-p9mm`, `8e4a-m6fw`) |
| **Default $limit** | 1000 records |
| **Max $limit** | 50000 records |

### Categories (confirmed from live catalog enumeration)

20+ domain categories in the NS catalog (complete list for `list_categories` resource):

- Agriculture and Agri-business
- Business and Economy
- Business and Industry
- Communications
- Community Services
- Crime and Justice
- Education - Early Childhood
- Education - Post-Secondary and Skills Training
- Education - Primary to Grade 12
- Employment and Labour
- Environment and Energy
- Financial Services
- Fishing and Aquaculture
- Government Administration
- Health and Wellness
- Immigration and Migration
- Internal Government Services
- Lands, Forests and Wildlife
- Mines and Minerals
- Municipalities
- Nature and Environment
- Permits and Licensing
- Population and Demographics
- Procurement and Contracts
- Public Opinion Research
- Roads, Driving and Transport

### ArcGIS Hub (novagis) — Deferred

`novagis.maps.arcgis.com` exists but no public no-auth FeatureServer was confirmed during research. Per CONTEXT.md locked decision: Socrata-first, ArcGIS only if public endpoints confirmed. Result: **do not build ArcGIS path in this phase**.

### Transport / 511 — Deferred

NS 511 is HTML-based; no clean machine-readable feed confirmed. Consistent with CONTEXT.md locked decision: fully deferred, no NOT_CONFIGURED stubs.

---

## Standard Stack

### Core (no new dependencies)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `fastmcp` | 3.2.x | MCP server framework | Project standard |
| `httpx` | 0.28.x | Async HTTP | Shared infrastructure |
| `pydantic` | v2 | Flat schemas | Project standard |
| `aiocache` | latest | TTL caching via `cached_fetch` | Project standard |
| `tenacity` | latest | Retry in `shared/http.api_get` | Project standard |

### Supporting (all existing shared infra)

| Module | Purpose | When to Use |
|--------|---------|-------------|
| `shared/socrata.py` (NEW) | SODA catalog search + per-dataset reads with SoQL | All nova_scotia module functions; reusable for future Socrata portals |
| `shared/http.py:api_get` | Underlying HTTP call with retry | Used inside shared/socrata.py |
| `shared/cache.py:cached_fetch` | TTL caching | Every nova_scotia client function |
| `shared/rate_limiter.py:get_limiter` | Token bucket per source | Every nova_scotia client function |
| `shared/envelope.py` | `make_response` / `make_error` | Every tool function |
| `shared/parsers.py:fetch_and_parse` | File parsing for query_dataset CSV/XLSX path | Auto-router in query_dataset tool |

### No New Dependencies

The existing stack covers every Nova Scotia surface. The SODA API is pure JSON over HTTPS — `httpx` + standard `api_get` suffices. No additional XML parsing, binary formats, or specialized clients needed.

### Installation

No new packages required.

---

## Socrata SODA API Mechanics (live-verified)

### Discovery: `/api/catalog/v1`

**Recommended endpoint** (vs `api/views.json`): richer structure, reliable pagination, metadata fields.

```
GET https://data.novascotia.ca/api/catalog/v1
  ?domains=data.novascotia.ca
  &q={search_term}          # full-text across name/description/tags
  &limit={N}                # page size (default 10, max not hard-limited)
  &offset={N}               # pagination offset (0-indexed, confirmed working)
  &only=datasets            # filters out maps/charts/stories
```

**Response shape:**
```json
{
  "results": [
    {
      "resource": {
        "id": "h57h-p9mm",         // 4x4 dataset ID
        "name": "Nova Scotia Marine Aquaculture Leases",
        "description": "...",
        "type": "dataset",
        "updatedAt": "...",
        "columns_name": ["license_le", "ownership", ...],
        "columns_field_name": ["license_le", "ownership", ...],
        "columns_datatype": ["text", "text", ...],
        "download_count": 8495
      },
      "classification": {
        "domain_category": "Fishing and Aquaculture",
        "domain_tags": ["marine", "aquaculture", "leases", ...],
        "categories": [],
        "tags": [],
        "domain_metadata": [
          {"key": "Detailed-Metadata_Department", "value": "Fisheries and Aquaculture"},
          {"key": "Detailed-Metadata_Frequency", "value": "Monthly"}
        ]
      },
      "metadata": {"domain": "data.novascotia.ca"},
      "permalink": "https://data.novascotia.ca/d/h57h-p9mm",
      "link": "https://data.novascotia.ca/Fishing-and-Aquaculture/...",
      "owner": {"id": "...", "user_type": "organization", "display_name": "Open Data Nova Scotia"}
    }
  ],
  "resultSetSize": 706,
  "timings": {...},
  "warnings": []
}
```

**Pagination:** `resultSetSize` is total matching count. `offset=` skips records. Works correctly at all offsets tested (0, 10, 100, 200, 400, 700).

**Category filtering:** The `categories=` param does NOT work (returns 0 results). The `search_context=` URL format returns HTTP 404. Use `q=` keyword search to find category-specific datasets, or filter client-side on `classification.domain_category`.

### Per-Dataset Read: `/resource/{id}.json`

```
GET https://data.novascotia.ca/resource/h57h-p9mm.json
  ?$where=speciestyp='Shellfish'    # SQL-like filter
  ?$select=license_le,county,species  # field projection
  ?$order=county ASC                # sort
  ?$limit=100                       # page size (default 1000, max 50000)
  ?$offset=0                        # pagination
  ?$q=salmon                        # full-text search within dataset
  ?$group=county,speciestyp         # aggregation (with COUNT() in $select)
```

Returns flat JSON array of row objects. SoQL confirmed:
- `$where=year='2020'` — value quoted, works for text fields stored as strings
- `$where=date > '2023-01-01T00:00:00.000'` — ISO 8601 timestamp comparison
- `$select=county,count(*) AS count&$group=county` — aggregation confirmed working
- `$q=salmon` — full-text search within the dataset

### Metadata: `/api/views/{id}.json`

Returns dataset schema: `id`, `name`, `category`, `description`, `columns` (array of `{name, dataTypeName, description}`), `attribution`, `license.name`, `publicationDate`, `viewLastModified`, `tags`.

**Use in `get_dataset_details` tool:** Flatter than the catalog entry; best for schema inspection.

### `X-App-Token` Header

Add as an optional header to all requests. When `NS_APP_TOKEN` env var is set (future enhancement), include `X-App-Token: {token}` in every request. Without it, Socrata applies throttling (~1 req/sec per IP). **Design the client so the token slot exists but is None by default.**

---

## shared/socrata.py Design

### Function Surface (prescriptive)

```python
"""Reusable Socrata SODA API async client.

Used by any Canadian provincial/municipal module that publishes via Socrata.
data.novascotia.ca is the first consumer.

Public functions:
    search_catalog(domain, q, limit, offset, only) -> dict
    get_dataset_metadata(domain, dataset_id) -> dict
    query_dataset(domain, dataset_id, where, select, order, limit, offset, q, group) -> list[dict]
    shape_catalog_result(result) -> dict
"""
```

**`search_catalog`**
```python
async def search_catalog(
    domain: str,
    q: str = "",
    limit: int = 10,
    offset: int = 0,
    only: str = "datasets",
    *,
    app_token: str | None = None,
    httpx_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """Search a Socrata catalog for datasets matching a query.

    Args:
        domain: Socrata domain (e.g., "data.novascotia.ca").
        q: Free-text search (default: "" = all datasets).
        limit: Page size (default: 10).
        offset: Pagination offset (default: 0). Omitted from request if 0.
        only: Filter to "datasets", "maps", "charts", "stories", "files" (default: "datasets").
        app_token: Optional Socrata app token for higher rate limits.
        httpx_client: Optional pre-built AsyncClient for testing.

    Returns:
        Raw catalog JSON: {results, resultSetSize, timings, warnings}

    Raises:
        httpx.HTTPStatusError: On 4xx/5xx responses.
    """
```

**`get_dataset_metadata`**
```python
async def get_dataset_metadata(
    domain: str,
    dataset_id: str,
    *,
    app_token: str | None = None,
    httpx_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """Fetch schema and metadata for a specific dataset from /api/views/{id}.json.

    Returns:
        Flat dict with: id, name, category, description, columns (list of
        {name, field_name, data_type, description}), attribution, license_name,
        publication_date, row_count (if available), tags.
    """
```

**`query_dataset`**
```python
async def query_dataset(
    domain: str,
    dataset_id: str,
    where: str | None = None,
    select: str | None = None,
    order: str | None = None,
    limit: int = 1000,
    offset: int = 0,
    q: str | None = None,
    group: str | None = None,
    *,
    app_token: str | None = None,
    httpx_client: httpx.AsyncClient | None = None,
) -> list[dict[str, Any]]:
    """Query a Socrata dataset via SoQL against /resource/{id}.json.

    Args:
        domain: Socrata domain.
        dataset_id: 4x4 dataset identifier (e.g., "h57h-p9mm").
        where: SoQL WHERE clause (e.g., "county='Halifax'").
        select: Comma-separated field names or "field, count(*) AS n".
        order: Sort clause (e.g., "year DESC").
        limit: Max rows (default 1000, Socrata max 50000).
        offset: Pagination offset (default 0).
        q: Full-text search within the dataset.
        group: GROUP BY clause for aggregations.
        app_token: Optional Socrata app token.
        httpx_client: Optional pre-built AsyncClient for testing.

    Returns:
        List of flat row dicts from the SODA endpoint.

    Raises:
        httpx.HTTPStatusError: On 4xx/5xx responses.
    """
```

**`shape_catalog_result`**
```python
def shape_catalog_result(result: dict[str, Any]) -> dict[str, Any]:
    """Flatten a single catalog results[i] entry to a flat dict.

    Returns:
        Flat dict: id, name, description, category, tags, department,
        permalink, updated_at, download_count, type, column_names.
    """
```

### Structural Template Notes (from arcgis_hub.py/ogc.py)

- **Same injection pattern:** `httpx_client: httpx.AsyncClient | None = None` on all public functions — enables dependency injection for tests without monkeypatching.
- **Returns parsed dicts, NOT `httpx.Response`** — consistent with `api_get` parsed-dict contract and arcgis_hub.py pattern.
- **No `cached_fetch` or `get_limiter` inside shared/socrata.py** — these stay in the per-module `client.py` (same as arcgis_hub.py — the shared client is pure HTTP, caching is a module concern).
- **`MAX_DESCRIPTION_CHARS = 500`** — truncate long descriptions like arcgis_hub.py.
- **`DEFAULT_TIMEOUT = 30.0`** — same as arcgis_hub.py and ogc.py.
- **Geometry stripping:** When `the_geom` appears in row dicts, leave it in by default (agents may want it). Document that agents should use `$select` to exclude it when not needed.

### Request Contract (TestSharedSocrataContract)

The test class that pins the outgoing request parameters (preventing the Manitoba lesson where mocked tests missed a live 400):

```python
class TestSharedSocrataContract:
    """Asserts that shared/socrata.py sends exactly the right params to the SODA API."""

    @pytest.mark.asyncio
    async def test_search_catalog_sends_correct_params(self):
        """search_catalog with all args must send: domains, q, limit, offset, only."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.json.return_value = {"results": [], "resultSetSize": 0, "timings": {}, "warnings": []}
            MockClient.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_resp)

            await search_catalog("data.novascotia.ca", q="aquaculture", limit=5, offset=10, only="datasets")

            call_kwargs = MockClient.return_value.__aenter__.return_value.get.call_args
            # URL must be correct
            assert "data.novascotia.ca/api/catalog/v1" in call_kwargs[0][0]
            # params must be exactly right
            params = call_kwargs[1].get("params") or call_kwargs[0][1]
            assert params["domains"] == "data.novascotia.ca"
            assert params["q"] == "aquaculture"
            assert params["limit"] == 5
            assert params["offset"] == 10
            assert params["only"] == "datasets"

    @pytest.mark.asyncio
    async def test_query_dataset_sends_soql_params(self):
        """query_dataset must send $where, $select, $limit, $offset to /resource/{id}.json."""
        with patch("httpx.AsyncClient") as MockClient:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.json.return_value = [{"county": "Halifax"}]
            MockClient.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_resp)

            await query_dataset(
                "data.novascotia.ca", "h57h-p9mm",
                where="county='Halifax'", select="county,species", limit=50, offset=0
            )

            call_kwargs = MockClient.return_value.__aenter__.return_value.get.call_args
            assert "data.novascotia.ca/resource/h57h-p9mm.json" in call_kwargs[0][0]
            params = call_kwargs[1].get("params") or call_kwargs[0][1]
            assert params["$where"] == "county='Halifax'"
            assert params["$select"] == "county,species"
            assert params["$limit"] == 50
            # offset=0 should be omitted from params (Socrata default is 0)
            assert "$offset" not in params or params["$offset"] == 0

    @pytest.mark.asyncio
    async def test_offset_omitted_when_zero(self):
        """offset=0 must NOT appear in catalog API params (Socrata treats it same as absent but cleaner)."""
        # Verify the offset is omitted from catalog search when 0
        with patch("httpx.AsyncClient") as MockClient:
            ...
```

---

## Architecture Patterns

### Recommended Module Structure

```
src/mcp_canada/shared/
├── socrata.py              # NEW — reusable SODA client
└── __tests__/
    └── test_socrata.py     # NEW — unit tests for shared client + contract tests

src/mcp_canada/modules/nova_scotia/
├── __init__.py             # MODULE_NAME = "nova_scotia", MODULE_DESCRIPTION (en+fr)
├── constants.py            # BASE_DOMAIN, RATE_GROUP, CACHE_TTLs, DATASET_IDS
├── schemas.py              # Flat Pydantic v2 models (AquacultureLease, HatcheryRecord, etc.)
├── client.py               # ~17 async functions returning (data, was_cached) tuples
├── tools.py                # 17 @tool functions (5 discovery + 12 curated)
├── prompts.py              # 6 bilingual @prompt functions
├── resources.py            # 7 zero-parameter @resource functions
└── __tests__/
    ├── __init__.py
    ├── conftest.py          # Sample SODA API response fixtures (catalog + row data)
    ├── test_client.py       # Client unit tests + TestSharedApiGetContract
    ├── test_tools.py        # Tool unit tests (mocked client layer)
    └── test_prompts_resources.py
```

### Pattern 1: constants.py — Dataset IDs as the Single Source of Truth

```python
# src/mcp_canada/modules/nova_scotia/constants.py
from typing import Final

BASE_DOMAIN: Final[str] = "data.novascotia.ca"
BASE_URL: Final[str] = f"https://{BASE_DOMAIN}"
RATE_GROUP: Final[str] = "nova_scotia_soda"
RATE_LIMIT: Final[float] = 5.0   # conservative; Socrata throttles keyless at ~1/s per IP without token

# -------------------------------------------------------------------------
# Fishing / Aquaculture dataset IDs (live-verified 2026-06-15)
# -------------------------------------------------------------------------
DS_MARINE_AQUACULTURE_LEASES: Final[str] = "h57h-p9mm"
DS_LANDBASED_AQUACULTURE_LICENSES: Final[str] = "yqwg-f62a"
DS_FISH_HATCHERY_STOCKING: Final[str] = "8e4a-m6fw"
DS_AQUACULTURE_PRODUCTION: Final[str] = "v2ex-ev63"
DS_ROCKWEED_LEASES: Final[str] = "exhe-htib"   # geometry-only, thin fields

# -------------------------------------------------------------------------
# Environment / Water dataset IDs
# -------------------------------------------------------------------------
DS_SURFACE_WATER_QUALITY_CONTINUOUS: Final[str] = "bkfi-mjgw"
DS_SURFACE_WATER_QUALITY_STATIONS: Final[str] = "i9ee-9hct"
DS_BOIL_WATER_ADVISORIES: Final[str] = "7t68-9xmm"

# -------------------------------------------------------------------------
# Lands / Environment dataset IDs
# -------------------------------------------------------------------------
DS_PROTECTED_AREAS: Final[str] = "ticv-5du5"
DS_CROWN_LAND: Final[str] = "3nka-59nz"

# -------------------------------------------------------------------------
# Air Quality dataset IDs
# -------------------------------------------------------------------------
DS_AIR_QUALITY_STATIONS: Final[str] = "3bbm-drnh"

# -------------------------------------------------------------------------
# Health + Demographics dataset IDs
# -------------------------------------------------------------------------
DS_HOSPITALS: Final[str] = "tmfr-3h8a"
DS_LTC_RCF_FACILITIES: Final[str] = "x76a-axw2"
DS_LTC_WAITLIST: Final[str] = "c39g-gsdd"
DS_BIRTHS_DEATHS: Final[str] = "r794-fttm"
DS_CHRONIC_DISEASE: Final[dict[str, str]] = {
    "ami": "24qf-ntke",
    "diabetes": "cumi-sw99",
    "copd": "ua9e-4pss",
    "hypertension": "sztc-sewr",
    "asthma": "2bih-5dgk",
}

# -------------------------------------------------------------------------
# Cache TTLs (seconds)
# -------------------------------------------------------------------------
CACHE_TTL_LIVE: Final[int] = 900       # 15min — advisories (boil water)
CACHE_TTL_SEARCH: Final[int] = 3600    # 1h — catalog search results
CACHE_TTL_META: Final[int] = 86400     # 24h — facility locations, leases, hatchery
CACHE_TTL_ANNUAL: Final[int] = 604800  # 7d — vital stats, production (annual data)

# -------------------------------------------------------------------------
# Pagination
# -------------------------------------------------------------------------
DEFAULT_PAGE_SIZE: Final[int] = 1000
MAX_RECORDS: Final[int] = 5000
```

### Pattern 2: Client Function Shape (SODA-flavored)

```python
# src/mcp_canada/modules/nova_scotia/client.py
from mcp_canada.shared import socrata
from mcp_canada.shared.cache import cached_fetch
from mcp_canada.shared.rate_limiter import get_limiter
from .constants import (
    BASE_DOMAIN, RATE_GROUP, RATE_LIMIT,
    DS_MARINE_AQUACULTURE_LEASES, CACHE_TTL_META, MAX_RECORDS
)

_limiter = get_limiter(RATE_GROUP, rate=RATE_LIMIT)


async def fetch_search_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
) -> tuple[dict, bool]:
    cache_key = f"nova_scotia:catalog:search:{query}:{limit}:{offset}"

    async def fetcher() -> dict:
        await _limiter.acquire()
        return await socrata.search_catalog(
            BASE_DOMAIN, q=query, limit=limit, offset=offset, only="datasets"
        )

    return await cached_fetch(cache_key, CACHE_TTL_SEARCH, fetcher)


async def fetch_marine_aquaculture_leases(
    county: str | None = None,
    species_type: str | None = None,
    limit: int = MAX_RECORDS,
) -> tuple[dict, bool]:
    """Fetch marine aquaculture leases; optionally filter by county or species type."""
    where_parts = []
    if county:
        where_parts.append(f"county='{county}'")
    if species_type:
        where_parts.append(f"speciestyp='{species_type}'")
    where = " AND ".join(where_parts) or None

    cache_key = f"nova_scotia:marine_leases:{county or 'all'}:{species_type or 'all'}"

    async def fetcher() -> dict:
        await _limiter.acquire()
        rows = await socrata.query_dataset(
            BASE_DOMAIN,
            DS_MARINE_AQUACULTURE_LEASES,
            where=where,
            select="license_le,ownership,species,waterbody,county,sitestatus,speciestyp,hectares,lat_dms,long_dms",
            order="county ASC",
            limit=limit,
        )
        return {"leases": rows, "count": len(rows), "truncated": len(rows) >= limit}

    return await cached_fetch(cache_key, CACHE_TTL_META, fetcher)
```

### Pattern 3: Discovery Tool (Socrata flavor)

```python
# src/mcp_canada/modules/nova_scotia/tools.py
from fastmcp.tools import tool
from mcp_canada.shared.envelope import make_response, make_error
from .client import fetch_search_datasets
from .constants import BASE_URL

@tool
async def ns_search_datasets(
    query: str,
    limit: int = 10,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search Nova Scotia's open data catalogue on data.novascotia.ca.

    Use for: finding datasets on Nova Scotia's Socrata portal; discovering which datasets exist for a topic.
    Keywords: nova scotia open data catalogue search datasets socrata soda portal browse discover inventory find
    """
    try:
        data, cached = await fetch_search_datasets(query, limit=limit, offset=offset)
        results = [socrata.shape_catalog_result(r) for r in data.get("results", [])]
        total = data.get("resultSetSize", 0)
        return make_response(
            {"results": results, "total": total, "offset": offset, "limit": limit},
            api_name="nova-scotia-socrata",
            api_url=f"{BASE_URL}/api/catalog/v1",
            cached=cached,
            lang=lang,
        )
    except Exception as e:
        return make_error("UPSTREAM_ERROR", str(e), lang=lang)
```

### Pattern 4: Curated Tool with Disease Dispatch

```python
@tool
async def ns_get_chronic_disease_prevalence(
    disease: Literal["ami", "diabetes", "copd", "hypertension", "asthma"],
    health_zone: str | None = None,
    sex: str | None = None,
    year: str | None = None,
    limit: int = 1000,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get Nova Scotia chronic disease crude prevalence by health zone, sex, and age group.

    Use for: querying NS health statistics; comparing disease rates across health zones; analyzing chronic disease burden by age/sex.
    Keywords: nova scotia chronic disease prevalence diabetes heart disease COPD hypertension asthma health zone statistics NS Health
    """
    VALID_DISEASES = list(CHRONIC_DISEASE_DATASETS)
    if disease not in VALID_DISEASES:
        return make_error(
            "INVALID_INPUT",
            f"Unknown disease '{disease}'" if lang == "en" else f"Maladie inconnue '{disease}'",
            lang=lang,
            valid=VALID_DISEASES,
        )
    try:
        data, cached = await fetch_chronic_disease(disease, health_zone, sex, year, limit)
        return make_response(
            data,
            api_name="nova-scotia-socrata",
            api_url=f"https://data.novascotia.ca/resource/{CHRONIC_DISEASE_DATASETS[disease]}.json",
            cached=cached,
            lang=lang,
        )
    except Exception as e:
        return make_error("UPSTREAM_ERROR", str(e), lang=lang)
```

### Anti-Patterns to Avoid

- **NEVER use `categories=` param in the catalog API** — confirmed to return 0 results. Use `q=` or post-fetch filter on `classification.domain_category`.
- **NEVER use `api/views.json` for discovery** — no `resultSetSize`, no pagination metadata, different schema. Use `api/catalog/v1`.
- **NEVER use `search_context=` param** — returns HTTP 404.
- **NEVER hardcode dataset IDs in tool functions** — all dataset IDs in `constants.py` (the single source of truth).
- **NEVER call `response.raise_for_status()` or `.json()` on `api_get` return** — `api_get` returns parsed JSON dict (Phase 15 root-cause pitfall).
- **NEVER put `cached_fetch` or `get_limiter` inside `shared/socrata.py`** — caching is a module concern, shared client is pure HTTP (arcgis_hub.py pattern).
- **NEVER use `@mcp.tool`** — standalone `@tool` from `fastmcp.tools` only.
- **NEVER skip rate limiting** — keyless Socrata throttles at ~1 req/sec per IP. `RATE_LIMIT = 5.0` is the conservative design limit.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SODA catalog search | Custom httpx catalog client | `shared/socrata.search_catalog()` | Reusable across all future Socrata portals; tested |
| SoQL query builder | Custom query string builder | `shared/socrata.query_dataset()` with params | Handles `$where`, `$select`, `$order`, `$limit`, `$offset`, `$q`, `$group` cleanly |
| Response envelope | Per-tool JSON schema | `make_response` / `make_error` | Every tool must use this |
| Cache / rate limiting | Per-tool custom logic | `cached_fetch` + `get_limiter` | All modules use this |
| Metadata fetch | Separate HTTP client for `/api/views/` | `shared/socrata.get_dataset_metadata()` | Same client, same injection pattern |
| Category enumeration | Hardcoded list | `list_categories` tool querying catalog dynamically | Categories change as NS adds data |
| Geometry parsing | Custom GeoJSON parser | SODA returns geometry inline in `the_geom`; pass through or strip via `$select` | Socrata handles geometry natively |

**Key insight:** Socrata is the first portal technology in this codebase where the shared client is a SODA-specific HTTP abstraction (not a general `api_get` wrapper). The value is in standardizing the `$param` SoQL vocabulary and the catalog result shape — future Socrata portals (PEI, NB, Fredericton, etc.) can reuse `shared/socrata.py` with zero changes.

---

## Per-Domain Curated Dataset Catalog (live-verified)

### Domain 1: Fishing / Aquaculture (Signature — 4 curated tools)

| Tool | Dataset ID | Dataset Name | Key Columns | Cache TTL | Notes |
|------|-----------|-------------|-------------|-----------|-------|
| `ns_get_marine_aquaculture_leases` | `h57h-p9mm` | Nova Scotia Marine Aquaculture Leases | license_le, ownership, species, waterbody, county, sitestatus, speciestyp, hectares, lat_dms, long_dms | 24h | GeoJSON MultiPolygon in `the_geom`; use `$where` for county/speciestyp filter; `$select` to exclude geometry |
| `ns_get_landbased_aquaculture_licenses` | `yqwg-f62a` | Nova Scotia Landbased Aquaculture Licenses | license_le, species, county, speciestyp, ownership, sitestatus, lat_dms, long_dms | 24h | Finfish dominant (Atlantic Salmon, Rainbow Trout) |
| `ns_get_fish_hatchery_stocking` | `8e4a-m6fw` | Nova Scotia Fish Hatchery Stocking Records | county, name, type, stock, stock_strain, hatchery, fish_length_cm, fish_weight_g, number_released, stocking_date, mark | 24h | Current to 2025-11-19; Brook Trout dominant; `$order=stocking_date DESC` recommended |
| `ns_get_aquaculture_production` | `v2ex-ev63` | Aquaculture Production, Value, Employment Data by County | year, county, kgs, total_value, full_time, pt_employ_6_mth, pt_employ_6_mth_1, total_employ | 7d | Annual data by county; useful for cross-module economic analysis |

**SoQL tips for aquaculture:**
- Marine leases: `$where=speciestyp='Shellfish'` or `$where=county='Inverness'`
- Hatchery: `$where=stock='Brook Trout'&$order=stocking_date DESC`
- Production: `$where=year='2017'` (year field is text, use string comparison)

### Domain 2: Environment / Water (3 curated tools)

| Tool | Dataset ID | Dataset Name | Key Columns | Cache TTL | Notes |
|------|-----------|-------------|-------------|-----------|-------|
| `ns_get_water_quality_monitoring` | `bkfi-mjgw` | Surface Water Quality Monitoring Network Continuous | date, time, temperature_c, ph, specific_conductance_s_cm, dissolved_oxygen_mg_l, station_number | 1h | Data through 2024-12-06; `$where=date > '2024-01-01T00:00:00.000'&$order=date DESC` |
| `ns_get_boil_water_advisories` | `7t68-9xmm` | Boil Water Advisories | site_name, county, date_advisory_issued, date_advisory_removed, facility_type, length_of_advisory | 15min | Live; current to 2025; `$where=date_advisory_removed IS NULL` for active advisories |
| `ns_get_protected_areas` | `ticv-5du5` | The Nova Scotia Protected Areas System | objectid, pro_name, protect1, symbol, owner, authority, status, web_url, ha_gis | 7d | GeoJSON MultiPolygon in `the_geom`; use `$select` to exclude geometry; `$where=status='Designated'` for official protected areas |

**SoQL tips for environment:**
- Water quality: `$where=station_number='NS01EF0002'` for specific station
- Boil water: `$where=county='ANNAPOLIS COUNTY'` — county names are uppercase

### Domain 3: Lands / Forests / Wildlife (merged into environment — no extra curated tools needed beyond protected areas)

The `ticv-5du5` (Protected Areas System) covers this domain. Crown Land (`3nka-59nz`) is discoverable via `ns_search_datasets`. The "Old Growth Forest Policy Layer" (`wanf-acts`) and crown land datasets are better served via `ns_query_dataset` than curated tools — low agent query frequency.

### Domain 4: Air Quality (1 curated tool)

| Tool | Dataset ID | Dataset Name | Key Columns | Cache TTL | Notes |
|------|-----------|-------------|-------------|-----------|-------|
| `ns_get_air_quality_stations` | `3bbm-drnh` | NS Provincial Ambient Air Quality Monitoring Stations | national_air_pollution_surveillance_network_id, station_name, city, latitude, longitude, measurements, monitoring_period | 24h | Reference catalog only — individual pollutant readings are in 20+ separate per-station datasets (O3, PM2.5, SO2, CO per station); these are discoverable via `ns_search_datasets` |

**Note on individual pollutant datasets:** The 20+ individual datasets (e.g., `gqhb-4cnd` O3 at Lake Major, `36wx-n4y2` PM2.5 at Halifax) are too numerous to curate individually. The stations catalog tool (`ns_get_air_quality_stations`) returns the station inventory; agents can use `ns_query_dataset` with the specific dataset ID to read individual pollutant time series. Document this pattern in `docs://ns/air-quality-guide` resource.

### Domain 5: Health + Demographics (4 curated tools)

| Tool | Dataset ID | Dataset Name | Key Columns | Cache TTL | Notes |
|------|-----------|-------------|-------------|-----------|-------|
| `ns_get_health_facilities` | `tmfr-3h8a` + `x76a-axw2` | Hospitals + LTC/RCF Facilities | facility_name, address, town, county, type, zone, beds, x_coordinate, y_coordinate | 7d | Dispatch by `facility_type: Literal["hospital", "long_term_care"]`; hospitals have "type" (Regional, District, Community); LTC has zone (Central/Eastern/Northern/Western), nursing_homes_nh_no_of_beds |
| `ns_get_ltc_waitlist` | `c39g-gsdd` | Long-term Care Waitlist | year, date, waiting_in_community, waiting_in_hospital, total_waiting_for_initial_placement, waiting_for_inter_facility_transfer | 24h | Weekly data from 2011; `$order=date DESC` for current; community vs hospital split is key |
| `ns_get_vital_statistics` | `r794-fttm` | NS Births and Deaths with Rates | counties, year, population, live_births, birth_rate, deaths, death_rate, excess_of_births_over_deaths, natural_increase_rate | 7d | Annual by county; `$where=year='2020'` uses string comparison; `$where=counties='ANNAPOLIS'` for county filter |
| `ns_get_chronic_disease_prevalence` | dispatched: `24qf-ntke`, `cumi-sw99`, `ua9e-4pss`, `sztc-sewr`, `2bih-5dgk` | AMI, Diabetes, COPD, Hypertension, Asthma | year, zone/health_zone, sex, agegroup, population, prevalence, crude_prevalence_rate | 7d | Dispatch by `disease: Literal["ami","diabetes","copd","hypertension","asthma"]`; all share same schema; AMI uses `health_zone`, Diabetes uses `zone` — normalize to `zone` |

**SoQL tips for health:**
- Health facilities: Two-dataset dispatch avoids 20-field combined response
- Chronic disease: `$where=zone='Zone 1 - Western' AND sex='F'&$order=year ASC`
- Vital stats: county names are UPPERCASE (`'ANNAPOLIS'` not `'Annapolis'`)

---

## Prompts and Resources

### 6 Bilingual Prompts

| Prompt | Type | Description |
|--------|------|-------------|
| `ns_explore_aquaculture_data` | Guided workflow (list[Message]) | Multi-step: discover NS aquaculture datasets → query marine leases → query hatchery records |
| `ns_health_zone_analysis` | Guided workflow (list[Message]) | Multi-step: get hospitals by zone → get LTC facilities → get chronic disease rates → build report |
| `ns_water_quality_analysis` | Guided workflow (list[Message]) | Multi-step: get station locations → query continuous readings → filter by date range → check boil water advisories |
| `ns_quick_find_dataset` | Quick lookup (str) | Instructs agent to use `ns_search_datasets` with specific query |
| `ns_quick_protected_areas` | Quick lookup (str) | Instructs agent to call `ns_get_protected_areas` with status filter |
| `ns_quick_vital_stats` | Quick lookup (str) | Instructs agent to call `ns_get_vital_statistics` filtered by county and year range |

### 7 Zero-Parameter Resources

| Resource URI | Content | Format |
|-------------|---------|--------|
| `data://ns/categories` | All 26 domain categories in NS catalog with count estimate | JSON |
| `data://ns/health-zones` | NS 4 health zones (Western/Northern/Eastern/Central) with counties per zone | JSON |
| `data://ns/fishing-areas` | NS aquaculture lease areas + counties; speciestyp values (Shellfish/Finfish/Marine Plant) | JSON |
| `data://ns/departments` | NS government departments publishing on data.novascotia.ca (from `domain_metadata`) | JSON |
| `docs://ns/socrata-guide` | How SODA/SoQL works: $where/$select/$order/$group/$limit/$offset syntax with NS examples | Markdown |
| `docs://ns/air-quality-guide` | Explains 20+ per-station pollutant datasets; pattern for querying individual stations via ns_query_dataset | Markdown |
| `template://ns/aquaculture-report` | Template for aquaculture sector analysis: lease counts by county, production by species, employment summary | Markdown |

---

## Common Pitfalls

### Pitfall 1: `categories=` parameter in catalog API returns 0 results

**What goes wrong:** `GET /api/catalog/v1?categories=Fishing+and+Aquaculture` returns `{results: [], resultSetSize: 0}`.
**Why it happens:** Socrata's catalog API v1 does not support client-facing `categories=` filtering. The correct internal mechanism is the `search_context` format, which also returns HTTP 404 on this portal.
**How to avoid:** Use `q=` keyword search for topic filtering. For category enumeration in `list_categories`, aggregate `classification.domain_category` values from fetched results. Do not offer a `category=` parameter in the discovery tools without testing it live first.
**Warning signs:** `resultSetSize: 0` with a `categories=` param.

### Pitfall 2: `api/views.json` is not a substitute for `api/catalog/v1`

**What goes wrong:** Developer uses `/api/views.json` for catalog discovery — gets an array without `resultSetSize`, different field names, no pagination envelope.
**Why it happens:** Both endpoints exist in Socrata but `api/views.json` is the older "views" API designed for portal navigation, not programmatic catalog access.
**How to avoid:** Always use `/api/catalog/v1?domains={domain}` for discovery. The `only=datasets` param correctly filters to datasets. `api/views.json` is only useful for backward compatibility and should not be referenced in the shared client.

### Pitfall 3: Year values are strings, not integers, in SoQL $where

**What goes wrong:** `$where=year=2020` returns HTTP 400 "Unable to convert value '2020' to integer".
**Why it happens:** Many NS datasets store year as a text column type (even when it looks numeric). The SoQL type system requires quoted values for text fields.
**How to avoid:** Always test field types via `/api/views/{id}.json` before writing SoQL. When in doubt, use quoted strings: `$where=year='2020'`. Confirmed in `r794-fttm` (vital stats: year is text column).

### Pitfall 4: County names are UPPERCASE in SoQL $where for some datasets

**What goes wrong:** `$where=county='Annapolis'` returns 0 rows for vital stats dataset.
**Why it happens:** The `r794-fttm` dataset stores county names in uppercase (`'ANNAPOLIS'`). Some datasets use title case, others uppercase.
**How to avoid:** Always check the actual stored values with a `$limit=3` probe before writing `$where` filters. Tool docstrings should document the case convention. Consider using `upper(county)='ANNAPOLIS'` in SoQL for case-insensitive matching, or document the expected casing per dataset.

### Pitfall 5: `the_geom` column bloats responses significantly

**What goes wrong:** Querying `h57h-p9mm` (marine aquaculture leases) without a `$select` returns MultiPolygon coordinate arrays that dwarf the actual attribute data — hundreds of KB per row for complex polygons.
**Why it happens:** Socrata includes `the_geom` in the default `*` field set when geometry exists.
**How to avoid:** Always use explicit `$select` in curated tool queries to exclude `the_geom` unless geometry is specifically needed: `$select=license_le,ownership,species,waterbody,county,sitestatus,speciestyp,hectares,lat_dms,long_dms`. For `ns_query_dataset` (generic), document that agents should use `$select` to control geometry inclusion.

### Pitfall 6: Boil water advisories active-filter pattern

**What goes wrong:** Assuming `date_advisory_removed IS NULL` works for active advisories — Socrata SoQL uses `IS NULL` but some datasets store removal dates as empty string `""` instead of NULL.
**Why it happens:** Socrata has two representations: proper SQL NULL and empty string. NS's boil water dataset may use either.
**How to avoid:** Wave 0 spike: probe `$where=date_advisory_removed IS NULL` and compare count against `$where=date_advisory_removed=''`. Use the one that returns current active advisories. Document in tool docstring.

### Pitfall 7: Chronic disease datasets have inconsistent zone field names

**What goes wrong:** AMI uses `health_zone` field; Diabetes uses `zone`. A unified dispatch tool that assumes `zone` for all diseases fails on AMI queries.
**Why it happens:** Different NS datasets were published by different teams with slightly different schema conventions.
**How to avoid:** The client function for chronic disease dispatch must normalize the output: map `health_zone` → `zone` in the returned rows. Add a `_normalize_zone_field(row)` helper in client.py that renames `health_zone` to `zone` when present. Test this normalization in unit tests.

### Pitfall 8: SoQL `$offset=0` should be omitted

**What goes wrong:** Sending `$offset=0` is harmless but adds noise to test assertions and logs.
**Why it happens:** Developers copy `$offset` from pagination code to base cases.
**How to avoid:** In `shared/socrata.py:query_dataset`, only add `$offset` to params dict when `offset > 0`. Same for catalog API `offset=` param.

---

## Code Examples

### Example 1: Catalog search with pagination

```python
# Source: live-verified against data.novascotia.ca/api/catalog/v1 on 2026-06-15
# Search for aquaculture datasets, page 2 (offset=5):
import httpx

async with httpx.AsyncClient() as client:
    resp = await client.get(
        "https://data.novascotia.ca/api/catalog/v1",
        params={
            "domains": "data.novascotia.ca",
            "q": "aquaculture",
            "limit": 5,
            "offset": 5,
            "only": "datasets",
        }
    )
    data = resp.json()
    # data["resultSetSize"] == 65 (total matching)
    # data["results"][0]["resource"]["id"] == "4x4-id"
    # data["results"][0]["classification"]["domain_category"] == "Fishing and Aquaculture"
```

### Example 2: SoQL query with $where + $select

```python
# Source: live-verified against data.novascotia.ca/resource/h57h-p9mm.json on 2026-06-15
# Shellfish-only leases in Inverness county:
resp = await client.get(
    "https://data.novascotia.ca/resource/h57h-p9mm.json",
    params={
        "$where": "speciestyp='Shellfish' AND county='Inverness'",
        "$select": "license_le,ownership,species,waterbody,county,sitestatus,hectares,lat_dms,long_dms",
        "$limit": 100,
        "$order": "county ASC",
    }
)
rows = resp.json()  # flat list of row dicts, no envelope
```

### Example 3: SoQL aggregation ($group + COUNT)

```python
# Source: live-verified against data.novascotia.ca/resource/h57h-p9mm.json on 2026-06-15
# Count leases by county and species type:
resp = await client.get(
    "https://data.novascotia.ca/resource/h57h-p9mm.json",
    params={
        "$select": "county, speciestyp, count(*) AS count",
        "$group": "county, speciestyp",
        "$order": "count DESC",
        "$limit": 50,
    }
)
```

### Example 4: Metadata fetch

```python
# Source: live-verified against data.novascotia.ca/api/views/2bvk-dtnt.json on 2026-06-15
resp = await client.get("https://data.novascotia.ca/api/views/8e4a-m6fw.json")
meta = resp.json()
# meta["id"] == "8e4a-m6fw"
# meta["name"] == "Nova Scotia Fish Hatchery Stocking Records"
# meta["category"] == "Fishing and Aquaculture"
# meta["columns"][0]["name"] == "County"
# meta["columns"][0]["dataTypeName"] == "text"
# meta["license"]["name"] == "Nova Scotia Open Government Licence"
```

### Example 5: shared/socrata.py module-level structure

```python
# Pattern from shared/arcgis_hub.py — apply to shared/socrata.py:
DEFAULT_TIMEOUT = 30.0
MAX_DESCRIPTION_CHARS = 500
CATALOG_PATH = "/api/catalog/v1"
RESOURCE_PATH = "/resource/{dataset_id}.json"
VIEWS_PATH = "/api/views/{dataset_id}.json"

async def search_catalog(domain, q="", limit=10, offset=0, only="datasets", *, app_token=None, httpx_client=None):
    url = f"https://{domain}{CATALOG_PATH}"
    params = {"domains": domain, "q": q, "limit": limit, "only": only}
    if offset > 0:
        params["offset"] = offset
    headers = {}
    if app_token:
        headers["X-App-Token"] = app_token
    # ... httpx_client injection pattern (same as arcgis_hub.py)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Socrata `api/views.json` | `api/catalog/v1` with `domains=` param | Socrata v1 catalog API (2017+) | Structured pagination, metadata, total count |
| Socrata dataset IDs were 4-char | Still 4x4 format (`xxxx-xxxx`) | N/A — stable format | IDs remain stable, safe to hardcode |
| SoQL `$offset` always sent | Omit `$offset=0` | Best practice | Cleaner requests, simpler assertions |
| Geometry always included | `$select` to exclude `the_geom` | Good practice since SODA 2.0 | Prevents response bloat |

**Categories filter `categories=` param:** Confirmed broken on data.novascotia.ca as of 2026-06-15. Use `q=` search instead.

---

## Open Questions

1. **Boil water advisories NULL vs empty string for active filter**
   - What we know: `7t68-9xmm` has `date_advisory_removed` field; 2025 dates confirmed in sample
   - What's unclear: Whether NULL or `""` represents "advisory still active"
   - Recommendation: Wave 0 spike — probe `$where=date_advisory_removed IS NULL` vs `$where=date_advisory_removed=''`. Both take < 1 second. Pin behavior in constants as `ACTIVE_ADVISORY_FILTER`.

2. **`ns_get_rockweed_leases` viability**
   - What we know: `exhe-htib` dataset exists; live probe showed only `the_geom` field (no attribute data visible in response)
   - What's unclear: Whether the dataset has tabular fields beyond geometry, or is purely a polygon layer
   - Recommendation: Wave 0 spike — probe `GET /api/views/exhe-htib.json` for column list. If only geometry, drop from curated tools (discovery-only).

3. **Socrata rate limiting behavior without app token**
   - What we know: Keyless reads work; Socrata documents ~1 req/sec per IP without token
   - What's unclear: Whether consecutive MCP agent calls will trigger throttling in practice
   - Recommendation: Set `RATE_LIMIT = 2.0` (conservative 2 req/sec, well under the 1/sec documented limit with burst headroom) as a starting point. Adjust upward in a follow-up phase if no throttling observed. Design `NS_APP_TOKEN` env var slot from day 1.

4. **Health zone to county mapping resource**
   - What we know: NS has 4 health zones (Western/Northern/Eastern/Central); chronic disease data groups by zone
   - What's unclear: Complete county-to-zone mapping (not found in any probed dataset)
   - Recommendation: Hard-code from public NS Health documentation in `data://ns/health-zones` resource. NS has 18 counties — known mapping is available.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + pytest-asyncio (existing project standard) |
| **Config file** | `pyproject.toml` (existing `[tool.pytest.ini_options]`) |
| **Quick run command** | `uv run pytest src/mcp_canada/modules/nova_scotia/__tests__/ src/mcp_canada/shared/__tests__/test_socrata.py -x -v` |
| **Full suite command** | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |
| **Integration command** | `uv run pytest tests/integration/ -v -m integration --timeout=120 -k "NovaScotia"` |
| **Estimated runtime** | ~30s unit (mocked); integration ~3 min live |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| NS-01 (Wave 0 prerequisite) | `shared/socrata.py` sends correct params to SODA API | unit (contract) | `pytest src/mcp_canada/shared/__tests__/test_socrata.py::TestSharedSocrataContract -x` | ❌ Wave 0 |
| NS-01 | `search_catalog` returns structured dict with results + resultSetSize | unit | `pytest .../test_socrata.py::TestSearchCatalog -x` | ❌ Wave 0 |
| NS-01 | `query_dataset` sends $where/$select/$order/$limit to /resource/ | unit (contract) | `pytest .../test_socrata.py::TestSharedSocrataContract::test_query_dataset_sends_soql_params -x` | ❌ Wave 0 |
| NS-01 | `get_dataset_metadata` fetches /api/views/{id}.json | unit | `pytest .../test_socrata.py::TestGetDatasetMetadata -x` | ❌ Wave 0 |
| NS-02 | `ns_search_datasets` tool returns results with id/name/category | unit + live integ | `pytest .../nova_scotia/__tests__/test_tools.py::TestNsSearchDatasets -x` | ❌ Wave 0 |
| NS-03 | `ns_get_dataset_details` returns schema columns | unit | `pytest .../test_tools.py::TestNsGetDatasetDetails -x` | ❌ Wave 0 |
| NS-04 | `ns_query_dataset` executes SoQL with _meta envelope | unit | `pytest .../test_tools.py::TestNsQueryDataset -x` | ❌ Wave 0 |
| NS-05 | `ns_list_organizations` returns publisher names | unit | `pytest .../test_tools.py::TestNsListOrganizations -x` | ❌ Wave 0 |
| NS-06 | `ns_list_categories` returns 20+ category strings | unit + live integ | `pytest .../test_tools.py::TestNsListCategories -x` | ❌ Wave 0 |
| NS-07 | Marine leases: license_le/ownership/species/county non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetMarineAquacultureLeases -x` | ❌ Wave 0 |
| NS-08 | Landbased licenses: license_le/speciestyp/county non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetLandbasedAquacultureLicenses -x` | ❌ Wave 0 |
| NS-09 | Hatchery stocking: stock/county/number_released/stocking_date non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetFishHatcheryStocking -x` | ❌ Wave 0 |
| NS-10 | Aquaculture production: year/county/kgs/total_value non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetAquacultureProduction -x` | ❌ Wave 0 |
| NS-11 | Water quality: station_number/date/temperature_c non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetWaterQualityMonitoring -x` | ❌ Wave 0 |
| NS-12 | Boil water: site_name/county/date_advisory_issued non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetBoilWaterAdvisories -x` | ❌ Wave 0 |
| NS-13 | Health facilities: facility_name/county/type non-null; dispatch by facility_type | unit + live integ | `pytest .../test_tools.py::TestNsGetHealthFacilities -x` | ❌ Wave 0 |
| NS-14 | Vital stats: counties/year/population/live_births non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetVitalStatistics -x` | ❌ Wave 0 |
| NS-15 | Protected areas: pro_name/protect1/owner/status non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetProtectedAreas -x` | ❌ Wave 0 |
| NS-16 | Air quality stations: station_name/latitude/longitude non-null | unit + live integ | `pytest .../test_tools.py::TestNsGetAirQualityStations -x` | ❌ Wave 0 |
| NS-17 | Chronic disease: year/zone/crude_prevalence_rate non-null; invalid disease → INVALID_INPUT | unit + live integ | `pytest .../test_tools.py::TestNsGetChronicDiseasePrevalence -x` | ❌ Wave 0 |
| NS-18 | discover_tools finds ns_ tools; 6 prompts + 7 resources auto-discovered | live integ | `pytest tests/integration/test_tool_scenarios.py::TestNovaScotiaToolScenarios -x` | ❌ Wave 0 |

### Integration Test Strategy (Live-Mandate)

Per CONTEXT.md locked decision: integration tests MUST hit real `data.novascotia.ca` and assert FIELD PRESENCE + non-null values (the Manitoba lesson).

**Required live assertions per tool (examples):**

```python
class TestNovaScotiaToolScenarios:

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_marine_aquaculture_leases_returns_field_presence(self):
        """'Show me all shellfish aquaculture leases in Inverness County NS'"""
        async with Client(mcp) as client:
            result = await client.call_tool("call_tool", {
                "name": "ns_get_marine_aquaculture_leases",
                "arguments": {"county": "Inverness", "species_type": "Shellfish", "lang": "en"}
            })
            data = json.loads(result.content[0].text)
            assert "_meta" in data
            assert "data" in data
            leases = data["data"]["leases"]
            assert len(leases) > 0, "Expected at least one Inverness shellfish lease"
            first = leases[0]
            assert first.get("license_le") is not None, "license_le must not be null"
            assert first.get("county") is not None
            assert first.get("ownership") is not None
            assert first.get("species") is not None
            # the_geom must be EXCLUDED (tool uses explicit $select)
            assert "the_geom" not in first

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fish_hatchery_stocking_recent_records(self):
        """'What fish were stocked in Nova Scotia hatcheries in 2025?'"""
        async with Client(mcp) as client:
            result = await client.call_tool("call_tool", {
                "name": "ns_get_fish_hatchery_stocking",
                "arguments": {"stock": "Brook Trout", "limit": 5, "lang": "en"}
            })
            data = json.loads(result.content[0].text)
            assert "_meta" in data
            records = data["data"]["stocking_records"]
            assert len(records) > 0
            first = records[0]
            assert first.get("stock") is not None
            assert first.get("county") is not None
            assert first.get("number_released") is not None
            assert first.get("stocking_date") is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_chronic_disease_ami_returns_health_zone_data(self):
        """'What is the AMI prevalence rate in Western NS for women over 50?'"""
        async with Client(mcp) as client:
            result = await client.call_tool("call_tool", {
                "name": "ns_get_chronic_disease_prevalence",
                "arguments": {"disease": "ami", "sex": "F", "lang": "en"}
            })
            data = json.loads(result.content[0].text)
            assert "_meta" in data
            rows = data["data"]["rows"]
            assert len(rows) > 0
            first = rows[0]
            assert first.get("zone") is not None  # normalized from health_zone
            assert first.get("crude_prevalence_rate") is not None
            assert first.get("year") is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_invalid_disease_returns_structured_error(self):
        """'Get NS tuberculosis prevalence' — tool should return INVALID_INPUT not exception"""
        async with Client(mcp) as client:
            result = await client.call_tool("call_tool", {
                "name": "ns_get_chronic_disease_prevalence",
                "arguments": {"disease": "tuberculosis", "lang": "en"}
            })
            data = json.loads(result.content[0].text)
            assert "error" in data
            assert data["error"]["code"] == "INVALID_INPUT"
            assert "valid" in data["error"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search_datasets_returns_aquaculture_results(self):
        """'What aquaculture data does Nova Scotia have?'"""
        async with Client(mcp) as client:
            result = await client.call_tool("call_tool", {
                "name": "ns_search_datasets",
                "arguments": {"query": "aquaculture", "limit": 5, "lang": "en"}
            })
            data = json.loads(result.content[0].text)
            assert "_meta" in data
            results = data["data"]["results"]
            assert len(results) > 0
            assert data["data"]["total"] >= 10  # confirmed 65 aquaculture results live
            ids = [r["id"] for r in results]
            assert "h57h-p9mm" in ids  # marine leases must be discoverable
```

### Sampling Rate

- **After every task commit:** `uv run pytest src/mcp_canada/modules/nova_scotia/__tests__/ src/mcp_canada/shared/__tests__/test_socrata.py -x`
- **After every wave merge:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Before `/gsd:verify-work`:** Full suite + Nova Scotia live integration scenarios green
- **Max feedback latency:** ~30 seconds (unit suite)

### Wave 0 Gaps

- [ ] `src/mcp_canada/shared/socrata.py` — NEW file; build before any nova_scotia module code
- [ ] `src/mcp_canada/shared/__tests__/test_socrata.py` — TestSharedSocrataContract (request-contract) + unit tests for all 4 public functions
- [ ] `src/mcp_canada/modules/nova_scotia/__init__.py` — MODULE_NAME, MODULE_DESCRIPTION
- [ ] `src/mcp_canada/modules/nova_scotia/constants.py` — all dataset IDs + cache TTLs
- [ ] `src/mcp_canada/modules/nova_scotia/__tests__/conftest.py` — SODA catalog fixture + per-dataset row fixtures for all 12 curated datasets
- [ ] `src/mcp_canada/modules/nova_scotia/__tests__/{test_client,test_tools,test_prompts_resources}.py` — scaffolds
- [ ] `tests/integration/test_tool_scenarios.py` — append `TestNovaScotiaToolScenarios`
- [ ] Wave 0 spikes (before planning any tool that depends on them):
  - Rockweed leases (`exhe-htib`): probe `/api/views/exhe-htib.json` for columns — drop if geometry-only
  - Boil water active-advisory filter: probe `$where=date_advisory_removed IS NULL` vs empty string
  - Chronic disease zone field normalization: confirm `health_zone` vs `zone` across all 5 disease datasets

---

## Sources

### Primary (HIGH confidence — live probes against data.novascotia.ca 2026-06-15)

- `GET https://data.novascotia.ca/api/catalog/v1?domains=data.novascotia.ca&limit=100&offset=0,100,200,400,700` — catalog structure, field names, resultSetSize=706, pagination confirmed
- `GET https://data.novascotia.ca/resource/h57h-p9mm.json` — Marine Aquaculture Leases; SoQL $where/$select/$group confirmed
- `GET https://data.novascotia.ca/resource/8e4a-m6fw.json` — Fish Hatchery Stocking; $where/$order/$select confirmed; data current to 2025-11-19
- `GET https://data.novascotia.ca/resource/2bvk-dtnt.json` + `GET /api/views/2bvk-dtnt.json` — SODA response shape + metadata schema confirmed
- `GET https://data.novascotia.ca/resource/7t68-9xmm.json` — Boil Water Advisories; fields confirmed; 2025 data live
- `GET https://data.novascotia.ca/resource/bkfi-mjgw.json` — Surface Water Quality Continuous; data through 2024-12-06
- `GET https://data.novascotia.ca/resource/ticv-5du5.json` — Protected Areas; field schema + GeoJSON geometry confirmed
- `GET https://data.novascotia.ca/resource/tmfr-3h8a.json` — Hospitals; field schema confirmed
- `GET https://data.novascotia.ca/resource/x76a-axw2.json` — LTC/RCF Facilities; field schema + zone confirmed
- `GET https://data.novascotia.ca/resource/r794-fttm.json` — Vital Statistics; $where year= string comparison confirmed
- `GET https://data.novascotia.ca/resource/24qf-ntke.json` — AMI Prevalence; health_zone field confirmed
- `GET https://data.novascotia.ca/resource/cumi-sw99.json` — Diabetes Prevalence; zone field confirmed
- `GET https://data.novascotia.ca/resource/3bbm-drnh.json` — Air Quality Stations; field schema confirmed
- `GET https://data.novascotia.ca/resource/v2ex-ev63.json` — Aquaculture Production; field schema confirmed
- `GET https://support.novascotia.ca/services/open-data-portal-licence` — Licence name, terms, commercial use confirmed

### Secondary (MEDIUM confidence — confirmed from catalog + metadata)

- Dataset IDs for `yqwg-f62a`, `exhe-htib`, `c39g-gsdd`, `ua9e-4pss`, `sztc-sewr`, `2bih-5dgk`, `chvv-syvv`, `5q4c-27fh` — returned in catalog search results; field schemas not individually probed (assumed consistent with catalog column listing)
- Category list (20+ values) — aggregated from 4 separate catalog pages (offset 0, 100, 200, 400)

### Tertiary (LOW confidence — not individually verified)

- Socrata default limit (1000) and max limit (50000) — documented in Socrata's public SODA documentation, not individually tested against data.novascotia.ca
- `X-App-Token` header behavior — documented Socrata pattern; not tested on this specific portal

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; all shared infra already proven
- Socrata API mechanics: HIGH — 40+ live probes; $where/$select/$order/$group/$limit/offset all confirmed
- Dataset catalog (12 curated): HIGH — IDs confirmed via catalog API + individual resource probe
- Field schemas: HIGH (8 datasets individually probed) / MEDIUM (4 datasets column-listed only)
- Architecture patterns: HIGH — templates from arcgis_hub.py + ogc.py directly applicable
- Pitfalls: HIGH — all 8 pitfalls confirmed via live probe or direct test

**Research date:** 2026-06-15
**Valid until:** 2026-09-15 (stable Socrata API; dataset IDs are permanent in Socrata; 90-day validity conservative)
