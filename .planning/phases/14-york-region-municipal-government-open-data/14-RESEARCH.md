# Phase 14: York Region Municipal Government Open Data - Research

**Researched:** 2026-04-10
**Domain:** ArcGIS Hub REST API / ArcGIS Feature Services / York Region Open Data
**Confidence:** MEDIUM-HIGH (API patterns verified live; some local portal URLs unverified)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Use ArcGIS REST Feature Service API directly via httpx — NO new dependency
- Explicitly rejected: `arcgis` Python SDK (~800MB dependency footprint — violates no-new-deps policy)
- Use `&f=geojson` query parameter to get native GeoJSON responses (reuses `_parse_geojson` from shared/parsers.py)
- Server-side filtering via simplified named parameters (ward=, category=, min_year=) that the client translates to ArcGIS WHERE clauses internally
- Auto-paginate with a cap (max 5000 records per tool call), return `truncated: true` flag when cap hit
- Single `src/mcp_canada/modules/york_region/` module covering 10 portals total
- Tool prefixes per portal: `york_region_`, `markham_`, `vaughan_`, `richmond_hill_`, `aurora_`, `newmarket_`, `king_`, `east_gwillimbury_`, `whitchurch_stouffville_`, `georgina_`
- All 10 portals get the same 5 discovery tools: search_datasets, get_dataset_details, query_features, list_organizations, list_categories
- Portal base URLs stored in constants.py per-portal mapping
- York Region regional portal gets 5 curated areas: transit (YRT/Viva stops + routes via Feature Service), road network, census/demographics, public health statistics, waste management
- Markham, Vaughan, Richmond Hill (3 largest cities) each get 1-2 curated tools (addresses, roads)
- Remaining 6 local municipalities get discovery-only (no curated tools)
- YRT/Viva transit: use ArcGIS Feature Services only — skip the licensed GTFS feed
- Create `shared/arcgis_hub.py` as reusable ArcGIS REST Feature Service client
- Catalog search via the undocumented `/api/v2/datasets` Hub API with fallback to portal services directory listing if the Hub API errors
- Include prompts.py and resources.py from the start (7-file pattern, not retrofit)
- 4-6 bilingual prompts total covering discovery workflows + regional curated data (transit, health, roads)
- 6-10 resources: portal catalog, municipality list with population/area, dataset naming conventions docs, response templates

### Claude's Discretion
- Exact dataset IDs and Feature Service URLs per portal (discovered during research — see below)
- Whether to wrap the ArcGIS REST client as a context manager or bare async functions
- How to handle Feature Services with non-standard field names (ESRI systems often use ALL_CAPS or `OBJECTID`)
- Exact shape of WHERE clause translation (LIKE vs =, case sensitivity)
- Whether to expose MapServer endpoints in addition to FeatureServer endpoints

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

---

## Summary

York Region uses ArcGIS Hub (Esri) as its open data platform, which is architecturally distinct from CKAN (used by Ontario and Toronto). The regional portal at `insights-york.opendata.arcgis.com` contains 442 items searchable via the Hub Search API (`/api/search/v1/collections/all/items`). The actual spatial data is served from ArcGIS REST Feature Services hosted at `ww8.yorkmaps.ca/arcgis/rest/services/OpenData/` — a dedicated ArcGIS Server with 34 services organized by thematic category. The `&f=geojson` parameter works correctly on all tested FeatureServer endpoints, returning RFC 7946-compliant GeoJSON. The existing `_parse_geojson` in shared/parsers.py handles these responses without modification.

The critical finding for the 10-portal federation: **only 3 of the 9 local municipalities have confirmed standalone ArcGIS Hub portals** (Markham: 436 items, Aurora: 21 items, Newmarket: 61 items). Richmond Hill, Vaughan, King Township, East Gwillimbury, Whitchurch-Stouffville, and Georgina do NOT appear to have dedicated public ArcGIS Hub portals as of early 2026. Whitchurch-Stouffville has only a census-specific hub (2021 data). The CONTEXT.md decision to give all 10 portals the same 5 discovery tools still stands — for portals without standalone hubs, the discovery tools return "no datasets found" gracefully, and curated tools for the 3 largest cities still work (Vaughan and Richmond Hill data may be accessed via York Region regional portal or their ArcGIS REST services directly). This requires a design decision from the planner on fallback behavior.

**Primary recommendation:** Build `shared/arcgis_hub.py` around the Hub Search API (`/api/search/v1/`) plus direct FeatureServer queries. Use York Region's confirmed Feature Service base URL (`ww8.yorkmaps.ca/arcgis/rest/services/OpenData/`) for curated regional tools. For local portals without ArcGIS Hub, the discovery tools gracefully return empty results — do not block implementation.

---

## Standard Stack

### Core (Verified)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| httpx | existing | ArcGIS REST + Hub API calls | Already in project; no new dep |
| fastmcp.tools | existing | @tool decorator | Project standard |
| shared/parsers.py `_parse_geojson` | Phase 13 | Parse `&f=geojson` responses | Reuses existing — no new code |
| shared/cache.py `cached_fetch` | existing | TTL caching | Project standard |
| shared/rate_limiter.py `get_limiter` | existing | Per-portal rate limiting | Project standard |
| shared/envelope.py | existing | make_response / make_error | Project standard |

### New Shared Infrastructure
| File | Purpose |
|------|---------|
| `shared/arcgis_hub.py` | ArcGIS Hub Search API client + FeatureServer query client |

### Installation
```bash
# No new packages — uses existing httpx, fastmcp, aiocache
```

---

## Portal URLs (Verified and Unverified)

### Confirmed ArcGIS Hub Portals
| Municipality | Portal URL | Item Count | Status |
|-------------|-----------|-----------|--------|
| York Region (regional) | `https://insights-york.opendata.arcgis.com` | 442 | VERIFIED |
| City of Markham | `https://data-markham.opendata.arcgis.com` | 436 | VERIFIED |
| Town of Aurora | `https://town-of-aurora-data-hub-aurora.hub.arcgis.com` | 21 | VERIFIED |
| Town of Newmarket | `https://navigate-newmarket.hub.arcgis.com` | 61 | VERIFIED |

### NOT Confirmed — No Standalone ArcGIS Hub Found
| Municipality | Status | Best Alternative |
|-------------|--------|-----------------|
| City of Vaughan | No public ArcGIS Hub found | Maps at `maps.vaughan.ca/arcgis/rest/services` (internal, not Open Data) |
| City of Richmond Hill | No public ArcGIS Hub found | GIS viewer at `richmondhill.ca`; no open data portal |
| Township of King | No public ArcGIS Hub found | Only document links on king.ca/i-want/look-or-explore/open-data-information |
| Town of East Gwillimbury | No public ArcGIS Hub found | None identified |
| Town of Whitchurch-Stouffville | Census-only hub | `https://whitchurch-stouffville-census-hub-2021-townofws.hub.arcgis.com/` (census data only, not general open data) |
| Town of Georgina | No public ArcGIS Hub found | None identified |

**Critical note for planner:** The CONTEXT.md decision states all 10 portals get the same 5 discovery tools. For portals without ArcGIS Hub, discovery tools should return an informative response (0 results + note that this municipality doesn't maintain a standalone open data portal). The 3 largest city curated tools (Vaughan, Richmond Hill) need separate verification — their data may live on the York Region portal or internal REST services.

**Confidence:** HIGH for confirmed portals; HIGH for "not found" conclusions (Winter 2023 University of Toronto GTA audit confirmed only 18/29 GTA municipalities had dedicated portals).

---

## Architecture Patterns

### York Region ArcGIS REST Server (Primary Data Source)
The regional ArcGIS Server at `ww8.yorkmaps.ca` is the authoritative source for York Region curated data:
```
ww8.yorkmaps.ca/arcgis/rest/services/OpenData/
├── Biodiversity/          FeatureServer + MapServer
├── Boundary/              FeatureServer (Municipal Boundary, EDI Neighbourhoods)
├── Clean_Water_Act/       FeatureServer
├── Contours1m2016/        FeatureServer
├── DevelopmentApplicationStatusAndTeams/  FeatureServer
├── DrinkingWater/         FeatureServer (10 tables, maxRecordCount=2000)
├── Elevation/             FeatureServer
├── Environmental/         FeatureServer (Solid Waste Site, Regional Forest)
├── Health_And_Safety/     FeatureServer (Beach Water Testing, Hospital — maxRecordCount=2000)
├── Location/              FeatureServer (Address Point, Community)
├── Planning/              FeatureServer (Parcel, Employment Land, Population Estimates)
├── Society/               FeatureServer (Bike Path — maxRecordCount=2000)
├── Structures/            FeatureServer (Building Footprint, Municipal Office, etc.)
├── Traffic/               FeatureServer
├── Transportation/        FeatureServer (Regional Roads, Roads, Bus Stops, Bus Routes)
└── Utilities/             MapServer only (no FeatureServer)
```

### Hub Search API Pattern (Dataset Discovery)
The Hub Search API (`/api/search/v1/collections/all/items`) is the correct endpoint — NOT `/api/v2/datasets` (returns 404) and NOT `/api/v3/datasets` (searches the global ArcGIS Online catalog, not portal-scoped).

```
# Correct Hub Search API for portal-scoped discovery
GET https://{hub_domain}/api/search/v1/collections/all/items
  ?q={keyword}
  &limit={n}

# Response structure:
{
  "type": "FeatureCollection",
  "numberMatched": 442,   # total results
  "numberReturned": 5,    # this page
  "features": [
    {
      "properties": {
        "title": "...",
        "type": "Feature Service",   # type field
        "url": "https://...",        # REST endpoint
        "owner": "...",
        "tags": [...],
        "description": "...",
        "categories": [...]
      }
    }
  ],
  "links": [
    {"rel": "next", "href": "...?offset=5&limit=5"}
  ]
}
```

### FeatureServer Query Pattern (Spatial Data Retrieval)
```
GET {feature_server_url}/{layer_id}/query
  ?where=1=1                    # required (all records) or WHERE clause
  &outFields=*                  # all fields, or comma-separated list
  &f=geojson                    # native GeoJSON response
  &resultRecordCount=1000       # page size (capped by maxRecordCount)
  &resultOffset=0               # pagination offset
  &returnCountOnly=true         # count query (omit outFields/geometry)
```

**GeoJSON response from FeatureServer (RFC 7946 compliant):**
- Contains `"exceededTransferLimit": true` at top level when more records exist (non-standard vendor extension — ignored by `_parse_geojson`)
- Feature properties use ESRI naming: `OBJECTID` (OID), `GLOBALID` (UUID), field names in ALL_CAPS
- Geometry types: Point, Polyline (MultiLineString in GeoJSON), Polygon
- Coordinates in [longitude, latitude] WGS84 (EPSG:4326) for `&f=geojson`

### Pagination Strategy for FeatureServer
```python
# Auto-pagination with 5000 record cap
MAX_RECORDS = 5000
PAGE_SIZE = 1000  # safe default; actual maxRecordCount varies (1000-2000)

offset = 0
all_features = []
while offset < MAX_RECORDS:
    batch = await query_features(url, layer, offset=offset, count=PAGE_SIZE)
    all_features.extend(batch["features"])
    if not batch.get("exceededTransferLimit"):
        break
    offset += len(batch["features"])
    if offset >= MAX_RECORDS:
        truncated = True
        break
```

### WHERE Clause Translation
ESRI supports SQL-92 subset. Key patterns:
- String equality: `FIELD_NAME = 'value'` (case-sensitive by default)
- String contains: `FIELD_NAME LIKE '%value%'`
- Numeric: `FIELD_NAME > 100`
- Multiple conditions: `FIELD_NAME = 'a' AND OTHER = 'b'`
- All records: `1=1`

### Recommended Project Structure
```
src/mcp_canada/
├── shared/
│   └── arcgis_hub.py       # NEW: ArcGIS Hub Search API + FeatureServer client
└── modules/
    └── york_region/
        ├── __init__.py      # MODULE_NAME, MODULE_DESCRIPTION
        ├── constants.py     # PORTAL_URLS dict, SERVICE_URLS, RATE_*, CACHE_*
        ├── schemas.py       # Pydantic models (flat): HubDataset, FeatureRecord
        ├── client.py        # Portal-specific wrappers of shared/arcgis_hub.py
        ├── tools.py         # 50+ @tool functions with 10 portal prefixes
        ├── prompts.py       # 4-6 bilingual @prompt functions
        └── resources.py     # 6-10 @resource functions (data://, docs://, template://)
```

### Anti-Patterns to Avoid
- **Using `/api/v2/datasets`:** Returns 404 on all tested portals — dead endpoint
- **Using `/api/v3/datasets` unscoped:** Searches the global ArcGIS Online catalog (130K+ items), not the portal
- **MapServer for data:** MapServer endpoints lack Query/Extract capabilities on some services; always prefer FeatureServer where available
- **Assuming maxRecordCount is uniform:** Varies by layer (1000 for Transportation FeatureServer/2, 2000 for most others)
- **Caching `exceededTransferLimit`:** This is an ephemeral response flag, not a property to cache in Pydantic models

---

## Curated Dataset Inventory (Verified Feature Service URLs)

### York Region Regional Portal — 5 Curated Areas

#### 1. Transit (YRT/Viva)
| Dataset | Feature Service URL | Layer | Record Count |
|---------|--------------------|----|-------|
| Bus Stops from GTFS | `https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer` | 2 | 4,810 |
| Bus Routes from GTFS | `https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer` | 3 | ~300+ |
| Regional Road Network | `https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer` | 0 | 762 |
| Roads (all) | `https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer` | 1 | varies |

Fields for Bus Stops: `OBJECTID, STOP_ID, CODE, STOP_NAME, WHEELCHAIR_BOARDING, SCHEDULE_START, SCHEDULE_END`
Fields for Bus Routes: `OBJECTID, ROUTE_ID, ROUTE_SHORT_NAME, ROUTE_LONG_NAME, SCHEDULE_START, SCHEDULE_END`

#### 2. Census/Demographics (2021 Census, hosted on ArcGIS Online)
| Dataset | Feature Service URL | Notes |
|---------|--------------------|----|
| Age and Sex by Dissemination Area | `https://services1.arcgis.com/GzvOwaQBbX7KLiuG/arcgis/rest/services/myProfile_of_Age_and_Sex_by_Dissemination_Area__2021_Census/FeatureServer` | 364 fields, maxRecordCount=2000 |
| Total Income by DA | `https://services1.arcgis.com/GzvOwaQBbX7KLiuG/arcgis/rest/services/myProfile_of_Total_Income_by_Census_Dissemination_Area__2021_Census/FeatureServer` | |
| Ethnocultural Diversity by DA | `https://services1.arcgis.com/GzvOwaQBbX7KLiuG/arcgis/rest/services/myProfile_of_Ethnocultural_and_Religious_Diversity_by_Dissemination_Area__2021_Census/FeatureServer` | |

Key census fields: `DAUID, CSDUID, CSDNAME, TOT_POP, M_TOTAL, F_TOTAL, TOT_AVG_AGE_POP, TOT_MED_AGE_POP` + age group breakdowns (TOT_0_TO_4_YRS, TOT_65_YRS_OVER, etc.)

#### 3. Public Health / Safety
| Dataset | Feature Service URL | Layer | Notes |
|---------|--------------------|----|-------|
| Beach Water Testing | `https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Health_And_Safety/FeatureServer` | 0 | Point |
| Hospital Locations | `https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Health_And_Safety/FeatureServer` | 1 | Point |
| Drinking Water (Adverse Incidents) | `https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/DrinkingWater/FeatureServer` | Table 0 | 10 tables total |

#### 4. Waste Management
| Dataset | Feature Service URL | Notes |
|---------|--------------------|----|
| Waste Diversion Statistics | `https://services1.arcgis.com/GzvOwaQBbX7KLiuG/arcgis/rest/services/Waste_Diversion_Statistics_(Annual_Waste_Tonnages_-_Collected)/FeatureServer` | 2010-2021 tonnage data |
| Solid Waste Sites | `https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Environmental/FeatureServer` | Layer 0: Point locations |

#### 5. Road Network (regional)
- Regional Roads (Layer 0): 762 records, fields include road name, type, classification
- Roads (Layer 1): all roads including local

### Markham — 2 Curated Tools (Verified)
| Dataset | Feature Service URL | Notes |
|---------|--------------------|----|
| Civic Addresses | `https://utility.arcgis.com/usrsvcs/servers/7791a0d2e3d3422b8eab3c800be5c4e7/rest/services/OpenData/OD_ADDRESSES/FeatureServer` | Fields: FULL_ADDRESS, STREET, TYPE, MUNICIPALITY, WM_AREA |
| Road Network (SLRN) | `https://utility.arcgis.com/usrsvcs/servers/264f35f118324ee0a40ffa53714b23fe/rest/services/OpenData/OD_SLRN/FeatureServer` | maxRecordCount=2000; Fields: NAME, TYPE, FULLNAME, OWNER |

Additional confirmed Markham Feature Services (discovery targets): Parks, Bicycle Routes, Trails, Heritage Conservation Districts, Fire Stations, City Owned Facilities, Site Plan Control — Special Areas

### Vaughan — Curated Tools (RESEARCH GAP)
No confirmed public ArcGIS Hub or Feature Service URL for Vaughan. Vaughan's internal ArcGIS portal at `maps.vaughan.ca` is not an Open Data endpoint. The planner must decide: **skip Vaughan curated tools for now**, or use York Region portal as a fallback for Vaughan data. Confidence: LOW.

### Richmond Hill — Curated Tools (RESEARCH GAP)
Same situation as Vaughan: no confirmed public open data portal. Confidence: LOW.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| GeoJSON parsing | Custom parser | `shared/parsers._parse_geojson(content, include_geometry)` | Already exists with correct include_geometry pattern |
| HTTP fetching | Direct httpx calls | `shared/http.api_get()` or httpx directly with retry | Existing shared utility has retry on 429/5xx |
| Cache | Custom dict | `shared/cache.cached_fetch(key, ttl, fetcher)` | Existing aiocache wrapper |
| Rate limiting | asyncio.sleep | `shared/rate_limiter.get_limiter(source, rate)` | Existing TokenBucket per-source |
| Pagination loop | Ad-hoc loop | ArcGIS resultOffset/resultRecordCount pattern (see above) | Standard ESRI pagination; detect via `exceededTransferLimit` |
| WHERE clause builder | SQL string concatenation | Simple f-string with LIKE/= (ESRI only supports SQL-92 subset) | Avoid ORMs — overkill for 3-4 field types |
| Response envelope | Custom dict | `shared/envelope.make_response()` / `make_error()` | Project-wide standard |

**Key insight:** The ArcGIS ecosystem has significant field naming quirks (ALL_CAPS, OBJECTID, Shape__Length). Don't try to normalize these in the shared client — let the tool layer do selective field picking for agent-friendly output.

---

## Common Pitfalls

### Pitfall 1: Using `/api/v2/datasets` Hub endpoint
**What goes wrong:** Returns HTTP 404 on all tested York Region portals.
**Why it happens:** CONTEXT.md referenced this as the expected endpoint, but it appears to be an older/deprecated Hub API version that isn't enabled on these portals.
**How to avoid:** Use `/api/search/v1/collections/all/items` which was verified working on York Region (442 items), Markham (436 items), Newmarket (61 items), Aurora (21 items).
**Warning signs:** 404 response, no JSON body.

### Pitfall 2: `exceededTransferLimit` is a vendor extension, not standard GeoJSON
**What goes wrong:** If code strictly validates GeoJSON before passing to `_parse_geojson`, the vendor extension field causes failure.
**Why it happens:** ESRI adds `"exceededTransferLimit": true` as a top-level FeatureCollection property — not in the RFC 7946 spec.
**How to avoid:** `_parse_geojson` already handles this (ignores unknown top-level keys). Check `exceededTransferLimit` BEFORE calling `_parse_geojson` to decide whether to continue paginating.
**Code pattern:**
```python
raw = response.json()
truncated = raw.get("exceededTransferLimit", False)
features = _parse_geojson(response.content, include_geometry=include_geometry)
```

### Pitfall 3: maxRecordCount varies significantly by layer
**What goes wrong:** Hardcoding 1000 as page size causes missed records on 2000-count services; requesting 5000 on 1000-count services is silently capped.
**Why it happens:** Each FeatureServer layer has its own `maxRecordCount` configured at the Esri server level.
**How to avoid:** Fetch layer metadata first (`/FeatureServer/{layer_id}?f=json`), read `maxRecordCount`, use `min(requested, maxRecordCount)` as page size. Cache this metadata (it changes rarely).
**Observed values:** Transportation Layer 2 (Bus Stops): 1000; Health_And_Safety: 2000; DrinkingWater: 2000; Planning: 2000.

### Pitfall 4: ArcGIS Online-hosted services vs. York Region-hosted services
**What goes wrong:** Census datasets are hosted at `services1.arcgis.com/GzvOwaQBbX7KLiuG/...` (ArcGIS Online), not at `ww8.yorkmaps.ca`. Both require the same query pattern but have different reliability/SLA.
**Why it happens:** Some datasets were published directly to ArcGIS Online rather than York Region's on-premise server.
**How to avoid:** Store each curated dataset URL in constants.py (not derived from base URL). Test each URL independently during implementation.

### Pitfall 5: Markham uses `utility.arcgis.com/usrsvcs/servers/...` proxied URLs
**What goes wrong:** These URLs contain an internal server ID that could rotate. Bookmarking Feature Service URLs directly may break.
**Why it happens:** Markham hosts data via the ArcGIS Online utility.arcgis.com proxy (secure service proxy), which wraps internal endpoints.
**How to avoid:** Store specific curated URLs in constants.py and plan for them to change. The Hub Search API always returns current URLs — implement as fallback discovery if curated URL returns 404.

### Pitfall 6: Portals without ArcGIS Hub (6 of 9 local municipalities)
**What goes wrong:** Implementing `{municipality}_search_datasets` tool assumes a Hub API exists at a known URL, but 6 municipalities have no confirmed ArcGIS Hub.
**Why it happens:** Research confirms only 18/29 GTA municipalities have dedicated open data portals (U of T 2023 audit).
**How to avoid:** For municipalities without confirmed Hub URLs, the discovery tools must handle "no portal found" gracefully — return a structured error with explanation rather than HTTP error. The tool prefix still exists (per CONTEXT.md decision), but returns a NOT_FOUND error with message explaining the municipality does not maintain a standalone open data portal.

### Pitfall 7: ALL_CAPS field names require careful docstring documentation
**What goes wrong:** Agents receiving `STOP_NAME`, `ROUTE_SHORT_NAME`, `OBJECTID` may be confused by ESRI naming conventions.
**Why it happens:** ESRI uses all-caps field names as database column names, exposed verbatim in API responses.
**How to avoid:** Document field names in tool docstrings. Add a `docs://york_region/field-naming-conventions` resource explaining ESRI naming patterns. Do NOT rename fields (adds complexity for no agent benefit — agents can reference field names in context).

---

## Code Examples

### Hub Search API Call (Verified)
```python
# Source: verified against insights-york.opendata.arcgis.com/api/search/v1/collections/all/items
import httpx

async def search_hub_datasets(
    portal_base_url: str,
    query: str,
    limit: int = 10,
    offset: int = 0,
) -> dict:
    url = f"{portal_base_url}/api/search/v1/collections/all/items"
    params = {"q": query, "limit": limit}
    if offset > 0:
        params["offset"] = offset
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params, timeout=30.0)
        r.raise_for_status()
    return r.json()
    # Response: {"type": "FeatureCollection", "numberMatched": N, "numberReturned": n, "features": [...]}
```

### FeatureServer Query with Pagination (Verified)
```python
# Source: verified against ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer/2
import httpx
from mcp_canada.shared.parsers import _parse_geojson

MAX_RECORDS = 5000

async def query_feature_service(
    service_url: str,
    layer_id: int,
    where: str = "1=1",
    out_fields: str = "*",
    include_geometry: bool = False,
) -> tuple[list[dict], bool]:
    """Returns (features, truncated)."""
    features = []
    offset = 0
    truncated = False

    async with httpx.AsyncClient() as client:
        while offset < MAX_RECORDS:
            params = {
                "where": where,
                "outFields": out_fields,
                "f": "geojson",
                "resultOffset": offset,
                "resultRecordCount": min(1000, MAX_RECORDS - offset),
            }
            r = await client.get(
                f"{service_url}/{layer_id}/query",
                params=params,
                timeout=30.0,
            )
            r.raise_for_status()
            data = r.json()
            batch = _parse_geojson(r.content, include_geometry=include_geometry)
            features.extend(batch)

            if not data.get("exceededTransferLimit", False):
                break
            offset += len(batch)
            if offset >= MAX_RECORDS:
                truncated = True
                break

    return features, truncated
```

### Layer Metadata Fetch (for maxRecordCount)
```python
# Source: verified against FeatureServer endpoints
async def get_layer_metadata(service_url: str, layer_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{service_url}/{layer_id}?f=json", timeout=10.0)
        r.raise_for_status()
    data = r.json()
    return {
        "max_record_count": data.get("maxRecordCount", 1000),
        "fields": [{"name": f["name"], "type": f["type"]} for f in data.get("fields", [])],
        "geometry_type": data.get("geometryType"),
        "name": data.get("name"),
    }
```

### Portal Constants Pattern
```python
# Source: project pattern from toronto/constants.py
# In york_region/constants.py

PORTAL_URLS: dict[str, str | None] = {
    "york_region": "https://insights-york.opendata.arcgis.com",
    "markham": "https://data-markham.opendata.arcgis.com",
    "vaughan": None,  # No confirmed ArcGIS Hub as of 2026-04
    "richmond_hill": None,  # No confirmed ArcGIS Hub as of 2026-04
    "aurora": "https://town-of-aurora-data-hub-aurora.hub.arcgis.com",
    "newmarket": "https://navigate-newmarket.hub.arcgis.com",
    "king": None,  # No confirmed ArcGIS Hub as of 2026-04
    "east_gwillimbury": None,  # No confirmed ArcGIS Hub as of 2026-04
    "whitchurch_stouffville": None,  # Census hub only; no general open data
    "georgina": None,  # No confirmed ArcGIS Hub as of 2026-04
}

# York Region Feature Service base (on-premise ArcGIS Server)
YR_FEATURE_SERVER_BASE = "https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData"

# Curated Feature Service URLs
YR_TRANSIT_FS = f"{YR_FEATURE_SERVER_BASE}/Transportation/FeatureServer"
YR_BUS_STOPS_LAYER = 2          # 4,810 records
YR_BUS_ROUTES_LAYER = 3
YR_REGIONAL_ROADS_LAYER = 0     # 762 records
YR_ALL_ROADS_LAYER = 1

YR_HEALTH_FS = f"{YR_FEATURE_SERVER_BASE}/Health_And_Safety/FeatureServer"
YR_BEACH_TESTING_LAYER = 0
YR_HOSPITAL_LAYER = 1

YR_ENVIRONMENTAL_FS = f"{YR_FEATURE_SERVER_BASE}/Environmental/FeatureServer"
YR_SOLID_WASTE_SITES_LAYER = 0

YR_DRINKING_WATER_FS = f"{YR_FEATURE_SERVER_BASE}/DrinkingWater/FeatureServer"
# Tables: 0=Adverse Incident, 1=Annual Chemical Result, 8=Water System

# Census on ArcGIS Online (York Region org: GzvOwaQBbX7KLiuG)
YR_CENSUS_ORG = "GzvOwaQBbX7KLiuG"
YR_AGE_SEX_FS = (
    "https://services1.arcgis.com/GzvOwaQBbX7KLiuG/arcgis/rest/services/"
    "myProfile_of_Age_and_Sex_by_Dissemination_Area__2021_Census/FeatureServer"
)
YR_INCOME_FS = (
    "https://services1.arcgis.com/GzvOwaQBbX7KLiuG/arcgis/rest/services/"
    "myProfile_of_Total_Income_by_Census_Dissemination_Area__2021_Census/FeatureServer"
)
YR_WASTE_DIVERSION_FS = (
    "https://services1.arcgis.com/GzvOwaQBbX7KLiuG/arcgis/rest/services/"
    "Waste_Diversion_Statistics_(Annual_Waste_Tonnages_-_Collected)/FeatureServer"
)

# Markham curated Feature Services
MARKHAM_ADDRESSES_FS = (
    "https://utility.arcgis.com/usrsvcs/servers/"
    "7791a0d2e3d3422b8eab3c800be5c4e7/rest/services/OpenData/OD_ADDRESSES/FeatureServer"
)
MARKHAM_ROADS_FS = (
    "https://utility.arcgis.com/usrsvcs/servers/"
    "264f35f118324ee0a40ffa53714b23fe/rest/services/OpenData/OD_SLRN/FeatureServer"
)

RATE_GROUP = "arcgis_hub"
RATE_LIMIT = 5.0  # requests per second (no published limit; conservative)
CACHE_TTL_SEARCH = 3600    # 1 hour for search results
CACHE_TTL_META = 86400     # 24 hours for layer metadata
CACHE_TTL_DATA = 3600      # 1 hour for feature data
```

---

## Authentication

**Finding:** ALL tested endpoints are publicly accessible without API keys or OAuth tokens.

Verified public access:
- York Region Hub Search API (`/api/search/v1/collections/all/items`) — no token required
- York Region FeatureServer queries (`ww8.yorkmaps.ca`) — no token required
- ArcGIS Online FeatureServer queries (`services1.arcgis.com/GzvOwaQBbX7KLiuG`) — no token required
- Markham Hub Search API and FeatureServer queries — no token required

**Confidence:** HIGH — verified by successful unauthenticated requests returning data.

---

## Rate Limits

**Finding:** No published rate limits for these portals.

What is known:
- ArcGIS Online has a global 10,000 API calls/minute cap per org (for authenticated subscribers)
- For public/unauthenticated access, no documented limit found in Esri developer docs
- York Region's on-premise server (`ww8.yorkmaps.ca`) has no published rate limit

**Recommendation:** Use `RATE_LIMIT = 5.0` requests/second (same as Toronto). This is conservative and respectful for a municipal server. One rate limiter group `"arcgis_hub"` shared across all 10 portals prevents concurrent bursts.

**Confidence:** MEDIUM — rate limits are inferred from being conservative, not from published documentation.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `/api/v2/datasets` Hub endpoint | `/api/search/v1/collections/all/items` | ~2022 when ArcGIS Hub v2 released | v2 returns 404 on these portals |
| `/api/v3/datasets` (global) | `/api/search/v1/` (portal-scoped) | Ongoing | v3 searches global catalog; v1 searches portal catalog |
| `arcgis` Python SDK (pre-2022) | Direct httpx + REST API | Design decision | 800MB dependency eliminated |

**Deprecated/outdated:**
- `/api/v2/datasets`: Not enabled on York Region, Markham, Aurora, Newmarket portals (404)
- MapServer-only services: `ActiveConstruction`, `OpenDataRepository`, `Utilities`, `Collisions` have no FeatureServer; use Hub Search API discovery to expose these as downloadable dataset links only

---

## Open Questions

1. **Vaughan and Richmond Hill curated tools**
   - What we know: Neither municipality has a confirmed public ArcGIS Hub or open data FeatureServer
   - What's unclear: Whether to implement discovery tools returning "no portal" error, or skip these prefixes from the tool count
   - Recommendation: Keep tool prefixes per CONTEXT.md decision; discovery tools return structured `NOT_FOUND` error with explanation. Planner should decide whether to create stub curated tools or omit them.

2. **Whitchurch-Stouffville census hub scope**
   - What we know: `whitchurch-stouffville-census-hub-2021-townofws.hub.arcgis.com` exists but is census-only (21 datasets)
   - What's unclear: Should `whitchurch_stouffville_search_datasets` use this census-specific hub or return NOT_FOUND
   - Recommendation: Use the census hub URL for the discovery tools — 21 datasets is still useful data, note the census-only scope in the tool docstring.

3. **Vaughan and Richmond Hill curated Feature Service discovery**
   - What we know: Both cities use ArcGIS internally (`maps.vaughan.ca`, `richmondhill.ca`) but don't expose open data
   - What's unclear: Whether any internal ArcGIS REST services at these cities are publicly accessible
   - Recommendation: Planner should set expectation that Vaughan and Richmond Hill get discovery-only (same as King, East Gwillimbury, Georgina) — promote them from "3 largest cities with curated tools" to "discovery-only with stub tools."

4. **Census field selection for census demographics tool**
   - What we know: 364 fields in Age and Sex layer — far too many to return by default
   - What's unclear: Which subset of fields agents actually want
   - Recommendation: Return focused set by default: `CSDNAME, DAUID, TOT_POP, M_TOTAL, F_TOTAL, TOT_AVG_AGE_POP, TOT_MED_AGE_POP, TOT_0_TO_14_YRS, TOT_15_TO_64_YRS, TOT_65_YRS_OVER` — use `outFields` parameter to limit response.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio |
| Config file | `pyproject.toml` (existing) |
| Quick run command | `uv run pytest src/mcp_canada/modules/york_region/__tests__/ -x -v` |
| Full suite command | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |

### Phase Requirements → Test Map
| Behavior | Test Type | Automated Command | File Exists? |
|----------|-----------|-------------------|-------------|
| Hub Search API returns datasets | unit | `pytest .../york_region/__tests__/test_client.py::test_search_hub_returns_datasets -x` | Wave 0 |
| FeatureServer query returns GeoJSON features | unit | `pytest .../york_region/__tests__/test_client.py::test_query_features_returns_list -x` | Wave 0 |
| Pagination with `exceededTransferLimit` | unit | `pytest .../york_region/__tests__/test_client.py::test_pagination_continues_on_exceeded_limit -x` | Wave 0 |
| york_region_search_datasets tool (happy path) | unit | `pytest .../york_region/__tests__/test_tools.py::test_york_region_search_datasets_returns_response -x` | Wave 0 |
| markham_get_addresses tool | unit | `pytest .../york_region/__tests__/test_tools.py::test_markham_get_addresses -x` | Wave 0 |
| Discovery tool for portal without Hub (Vaughan) | unit | `pytest .../york_region/__tests__/test_tools.py::test_vaughan_discovery_returns_not_found -x` | Wave 0 |
| york_region_get_transit_stops tool | unit | `pytest .../york_region/__tests__/test_tools.py::test_york_region_get_transit_stops -x` | Wave 0 |
| york_region_get_census_demographics tool | unit | `pytest .../york_region/__tests__/test_tools.py::test_york_region_get_census_demographics -x` | Wave 0 |
| york_region_ tools discoverable via BM25 | integration | `pytest tests/integration/test_tool_scenarios.py::TestYorkRegionToolScenarios -m integration -x` | Wave 0 |
| Prompts discoverable | integration | `pytest tests/integration/test_prompts_resources_scenarios.py::TestYorkRegionPromptScenarios -m integration -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest src/mcp_canada/modules/york_region/__tests__/ -x -v`
- **Per wave merge:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `src/mcp_canada/shared/arcgis_hub.py` — new shared client (not a test file, but prerequisite)
- [ ] `src/mcp_canada/modules/york_region/__tests__/conftest.py` — sample API response fixtures
- [ ] `src/mcp_canada/modules/york_region/__tests__/test_client.py` — client unit tests with mocked httpx
- [ ] `src/mcp_canada/modules/york_region/__tests__/test_tools.py` — tool unit tests
- [ ] `tests/integration/test_tool_scenarios.py` append `TestYorkRegionToolScenarios` class

---

## Sources

### Primary (HIGH confidence)
- `https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData` — verified; lists 34 services, server version 10.81
- `https://insights-york.opendata.arcgis.com/api/search/v1/collections/all/items` — verified; 442 items, working pagination
- `https://data-markham.opendata.arcgis.com/api/search/v1/collections/all/items` — verified; 436 items
- `https://navigate-newmarket.hub.arcgis.com/api/search/v1/collections/all/items` — verified; 61 items
- `https://town-of-aurora-data-hub-aurora.hub.arcgis.com/api/search/v1/collections/all/items` — verified; 21 items
- `https://ww8.yorkmaps.ca/arcgis/rest/services/OpenData/Transportation/FeatureServer/2/query?...&f=geojson` — verified; returns RFC 7946 GeoJSON, 4,810 bus stops
- University of Toronto GTA open data audit (Winter 2023) — confirmed 18/29 GTA municipalities have portals
- `gist.github.com/jgravois/1b7ec5080e992a59f65cf7a2190e4365` — Hub v3 Search API structure
- `developers.arcgis.com/rest/services-reference/enterprise/query-feature-service-layer/` — FeatureServer query parameters

### Secondary (MEDIUM confidence)
- York Region bus stop count verified (4,810) via `returnCountOnly=true` query
- York Region regional road count verified (762)
- maxRecordCount values verified per FeatureServer service metadata
- All curated Feature Service URLs verified via live API calls

### Tertiary (LOW confidence)
- Vaughan, Richmond Hill "no open data portal" conclusion — based on failed web search and U of T audit; not definitively confirmed by checking all possible URL patterns

---

## Metadata

**Confidence breakdown:**
- Hub Search API patterns: HIGH — verified against 4 live portals
- ArcGIS FeatureServer query patterns: HIGH — verified with multiple live queries returning real data
- Curated York Region dataset URLs: HIGH — directly tested
- Curated Markham dataset URLs: MEDIUM — tested layer metadata but not full data queries
- Local municipality portal availability: HIGH (confirmed present) / HIGH (confirmed absent via exhaustive search)
- Rate limits: LOW — no published limits; recommendation is conservative assumption
- Vaughan/Richmond Hill curated tools: LOW — no confirmed Feature Service URLs

**Research date:** 2026-04-10
**Valid until:** 2026-07-10 (portal URLs are stable; Feature Service URLs via `utility.arcgis.com` may rotate)
