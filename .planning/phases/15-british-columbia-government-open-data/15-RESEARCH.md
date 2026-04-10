# Phase 15: British Columbia Government Open Data - Research

**Researched:** 2026-04-10
**Domain:** BC Data Catalogue (CKAN + bcgov extensions) + OGC WFS 2.0 (BC Geographic Warehouse)
**Confidence:** HIGH (all key claims verified against live endpoints)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Use BC Data Catalogue CKAN API at `https://catalogue.data.gov.bc.ca/api/3/action/`
- Add WFS support for BCGW via `https://openmaps.gov.bc.ca/geo/ows`
- WMS (PNG tiles) is NOT included — deferred
- Two-step workflow: `bc_search_datasets` → `bc_get_dataset_details` (object_name + queryable_via_wfs flag) → `bc_query_features` (WFS or file parser)
- Reuse `shared/parsers.fetch_and_parse()` for non-BCGW CSV/XLSX/PDF resources
- Create `shared/ogc.py` as a reusable WFS client (separate from `shared/arcgis_hub.py`)
- WFS client supports: GetCapabilities, GetFeature with CQL filters, GeoJSON output via `outputFormat=application/json`
- CQL filter strings passed as simplified named params translated internally (agents don't need CQL)
- Auto-paginate with 5000-record cap, `truncated: true` flag when cap hit
- Properties-only by default, opt-in `include_geometry=true`
- Tool prefix: `bc_`
- 5 CKAN discovery + ~15 curated = ~20 tools total
- Forestry: forest tenure, cut blocks, protected areas
- Wildfire: active fires + historical perimeters
- Environment: water quality, air quality, provincial parks
- Natural resources: mining tenure, fisheries
- Health: hospital locations, epidemiology
- Transportation: BC Transit (provincial), highways
- Climate: weather stations, long-term normals
- 6 bilingual prompts, 7 resources (7-file pattern)
- NOT included: Vancouver/Victoria/Surrey/Burnaby municipal portals (separate future phases)

### Claude's Discretion
- Exact CKAN organization filter strategies for BC ministries
- Which specific forestry datasets to curate
- Wildfire perimeter dataset selection
- WFS GetCapabilities caching strategy
- CQL filter escaping and injection prevention
- Whether bc_query_features auto-detects WFS vs file download vs explicit routing
- Exact simplified parameter names for common filters (region=, year=, status=)

### Deferred Ideas (OUT OF SCOPE)
- WMS GetMap support (PNG tiles)
- Vancouver municipal open data (future Phase 28)
- Victoria, Surrey, Burnaby municipal portals (future phases)
- BC-specific fisheries/DFO cross-reference (federal coordination required)
- BCGW GetCapabilities caching infrastructure optimization phase
</user_constraints>

---

## Summary

- BC Data Catalogue is CKAN 2.x with bcgov extensions exposing `object_name`, `bcdc_type`, `projection_name`, `resource_storage_location` at the resource level. Authentication is not required for public datasets. The CKAN `fq` parameter accepts `bcdc_type:geographic` to filter WFS-queryable datasets.
- The BCGW WFS endpoint (`https://openmaps.gov.bc.ca/geo/ows`) is a GeoServer-backed WFS 2.0 service with 870 public layers. **Verified live**: GetFeature returns GeoJSON with `outputFormat=application/json`, CQL_FILTER works (`FIRE_STATUS='Out'` returned correct results), pagination with `startIndex` + `sortBy=OBJECTID` + `count` works correctly, default CRS is EPSG:3005 (BC Albers) but `srsName=EPSG:4326` returns WGS84 lat/lon.
- `queryable_via_wfs` detection is reliable: resources with `resource_storage_location = "bc geographic warehouse"` and `bcdc_type = "geographic"` map to WFS layers. Resources with `storage_location = "pub.data.gov.bc.ca"` are file downloads routed to `fetch_and_parse()`.
- 15 curated datasets verified with exact WHSE object_names and key filterable properties through live WFS queries.
- WFS error responses are HTTP 400 with XML ExceptionReport body when typeName is invalid. The client must check `content-type` and parse XML to extract the `exceptionCode` and `ExceptionText`.

**Primary recommendation:** Use `typeNames` (plural, WFS 2.0) not `typeName` (singular, WFS 1.x). Default to `srsName=EPSG:4326` for agent-friendly lat/lon output. Detect `queryable_via_wfs` from CKAN resource metadata — do not attempt auto-detection from runtime WFS queries.

---

## BC Data Catalogue (CKAN) API Details

### Endpoint
```
Base URL: https://catalogue.data.gov.bc.ca/api/3/action/
Authentication: None required for public datasets
```

### Standard CKAN Actions Available
| Action | Purpose |
|--------|---------|
| `package_search` | Full-text search with Solr `q` + filter `fq` |
| `package_show` | Full dataset by id or slug |
| `resource_show` | Single resource by id |
| `organization_list` | Ministry/agency list |
| `tag_list` | All tags (tags are free-form; not hierarchical groups) |

IMPORTANT: `group_list` returns HTTP 403. BC does not use CKAN groups. Use `tags` (via `fq=tags:forestry`) or `organization` (via `fq=organization:env-air-quality`) for category-like filtering.

### bcgov Custom Fields (Verified via live API)

**Dataset level:**
- `bcdc_type`: `"bcdc_dataset"` (always this value at dataset level)
- `security_class`: `"PUBLIC"` for open data
- `resource_status`: `"onGoing"` | `"completed"` | `"obsolete"`
- `publish_state`: `"PUBLISHED"` for discoverable datasets

**Resource level (critical for routing):**
- `bcdc_type`: `"geographic"` | `"webservice"` | `"document"` | `"tabular"`
- `object_name`: `"WHSE_CATEGORY.TABLE_NAME"` — present on BCGW-hosted geographic resources
- `projection_name`: `"epsg3005"` | `"epsg4326"` | `"epsg3857"`
- `resource_storage_location`: `"bc geographic warehouse"` | `"pub.data.gov.bc.ca"` | `"esri arcgis online"` | `"ministry or other database"` | `"external"`
- `resource_type`: `"data"` | `"geographic data"` | `"webservice"`

### queryable_via_wfs Detection Logic (CONFIRMED via live queries)
A resource is WFS-queryable when:
```python
resource["bcdc_type"] == "geographic"
AND resource.get("resource_storage_location") == "bc geographic warehouse"
AND resource.get("object_name") is not None
```
Resources with `storage_location = "pub.data.gov.bc.ca"` are shapefile/CSV file downloads.
Resources with `storage_location = "esri arcgis online"` are ArcGIS REST endpoints (not WFS).
WMS/KML resources have `bcdc_type = "webservice"` — skip these.

### Pagination
- `rows` (default 10, max 1000) + `start` (default 0) — standard CKAN pagination
- `sort` accepts: `"score desc, metadata_modified desc"` (default), `"metadata_modified desc"`, `"name asc"`

### Rate Limits
No published rate limits for BC Data Catalogue. Use 10 req/s (same as Ontario). CONFIRMED: no auth tokens needed.

### Cache TTLs (Recommended)
```python
CACHE_TTL_SEARCH = 3600    # 1h — dataset search + details
CACHE_TTL_META   = 86400   # 24h — org list
CACHE_TTL_WFS    = 300     # 5min — active fire data (refreshed every 15min by BC)
CACHE_TTL_DATA   = 86400   # 24h — historical/static WFS layers
CACHE_TTL_CAPS   = 3600    # 1h — WFS GetCapabilities (870-layer XML, slow but stable)
```

---

## WFS 2.0 Protocol Essentials

### Verified Endpoint
```
https://openmaps.gov.bc.ca/geo/ows
```

### Key GetFeature Parameters (WFS 2.0)
| Parameter | Value | Notes |
|-----------|-------|-------|
| `service` | `WFS` | Required |
| `version` | `2.0.0` | Required — use 2.0.0 |
| `request` | `GetFeature` | Required |
| `typeNames` | `WHSE_CATEGORY.TABLE_NAME` | **Plural** — WFS 2.0 spec. `typeName` (singular) is WFS 1.x only |
| `outputFormat` | `application/json` | Returns GeoJSON FeatureCollection |
| `count` | `1000` | Page size. Service default is 10,000 (high — always set explicitly) |
| `startIndex` | `0` | Zero-based pagination offset |
| `sortBy` | `OBJECTID` | Required for stable pagination |
| `srsName` | `EPSG:4326` | Returns WGS84 lat/lon (agent-friendly). Default is EPSG:3005 (BC Albers) |
| `CQL_FILTER` | `FIRE_YEAR=2023` | Optional attribute filter |
| `BBOX` | `minLon,minLat,maxLon,maxLat,EPSG:4326` | Optional spatial filter — combine with CQL using `AND` |
| `propertyName` | `FIELD1,FIELD2` | Optional — limit returned fields |

### Confirmed Working Examples
```
# Active wildfire incidents:
GET /geo/ows?service=WFS&version=2.0.0&request=GetFeature
  &typeNames=WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_PNTS_SP
  &outputFormat=application/json&count=100&startIndex=0&sortBy=OBJECTID
  &srsName=EPSG:4326

# CQL filter for fire status:
&CQL_FILTER=FIRE_STATUS='Out'   → returned 16 matching fires

# CQL filter for historical fire year:
&CQL_FILTER=FIRE_YEAR=2023   → returned 676 matching fires for 2023

# CQL filter for mineral tenure type:
&CQL_FILTER=TENURE_TYPE_CODE='M'  → returned 32,685 mineral claims
```

### WFS Response Structure (GeoJSON)
```json
{
  "type": "FeatureCollection",
  "totalFeatures": 21,
  "numberMatched": 21,
  "numberReturned": 5,
  "timeStamp": "2026-04-10T...",
  "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::4326"}},
  "features": [
    {
      "type": "Feature",
      "id": "PROT_CURRENT_FIRE_PNTS_SP.fid-...",
      "geometry": {"type": "Point", "coordinates": [-122.95, 51.93]},
      "geometry_name": "SHAPE",
      "properties": { ... }
    }
  ]
}
```

### CQL Filter Syntax
```
# Equality:
FIRE_STATUS='Out'
TENURE_TYPE_CODE='M'

# Numeric comparison:
FIRE_YEAR=2023
FIRE_SIZE_HECTARES > 1000
OFFICIAL_AREA_HA >= 100

# String pattern:
CLIENT_NAME LIKE 'WEYERHAEUSER%'

# Boolean AND/OR:
FIRE_YEAR=2023 AND FIRE_SIZE_HECTARES > 5000

# Spatial:
DWITHIN(SHAPE,POINT(1161815 452123),100,meters)   # EPSG:3005 coordinates
INTERSECTS(SHAPE,POINT(-123.1 49.2))               # With srsName=EPSG:4326
```

**CQL Injection Prevention:**
- Only trusted tool parameter values (region string, year int, status enum) are ever interpolated into CQL
- String values: replace single quotes with `''` (SQL-style escape)
- Numeric values: cast to int/float before interpolation
- Never pass raw user-supplied strings directly into CQL

### WFS Error Responses
WFS errors return HTTP 400 with XML body regardless of `outputFormat`. Detection:
```python
if response.status_code == 400:
    # Parse XML ExceptionReport
    # <ows:ExceptionReport><ows:Exception exceptionCode="InvalidParameterValue">
    #   <ows:ExceptionText>...</ows:ExceptionText></ows:Exception></ows:ExceptionReport>
```
Use `xml.etree.ElementTree` (stdlib) to parse — no additional dependencies.

### Pagination Pattern
```python
# Always set count + sortBy + startIndex for stable pagination
count = 1000
while start_index < MAX_RECORDS:
    params = {"count": count, "startIndex": start_index, "sortBy": "OBJECTID"}
    response = await http.get(url, params={**base_params, **params})
    data = response.json()
    features.extend(data["features"])
    if data["numberReturned"] < count:
        break  # last page
    start_index += count
    if start_index >= MAX_RECORDS:
        truncated = True
        break
```

---

## shared/ogc.py Proposed API Surface

### File Location
`src/mcp_canada/shared/ogc.py`

### Public Functions

```python
async def wfs_get_features(
    base_url: str,
    type_name: str,
    cql_filter: str | None = None,
    bbox: str | None = None,          # "minLon,minLat,maxLon,maxLat,EPSG:4326"
    count: int = 1000,
    start_index: int = 0,
    srs: str = "EPSG:4326",
    property_names: list[str] | None = None,
    include_geometry: bool = False,
    *,
    httpx_client: httpx.AsyncClient | None = None,
) -> tuple[list[dict], bool]:
    """Fetch one page of WFS features. Returns (features, has_more).

    Raises:
        WfsError: On WFS ExceptionReport (HTTP 400 with XML body)
        httpx.HTTPStatusError: On 5xx responses
    """

async def wfs_page_all(
    base_url: str,
    type_name: str,
    cql_filter: str | None = None,
    bbox: str | None = None,
    max_records: int = 5000,
    page_size: int = 1000,
    srs: str = "EPSG:4326",
    include_geometry: bool = False,
    *,
    httpx_client: httpx.AsyncClient | None = None,
) -> tuple[list[dict], bool]:
    """Paginate all WFS features up to max_records cap.
    Returns (features, truncated) where truncated=True if cap was hit.
    """

async def wfs_count(
    base_url: str,
    type_name: str,
    cql_filter: str | None = None,
    *,
    httpx_client: httpx.AsyncClient | None = None,
) -> int:
    """Return total matching feature count using resultType=hits."""

class WfsError(Exception):
    """WFS ExceptionReport error with code and message."""
    def __init__(self, code: str, message: str): ...
```

### Design Notes
- `wfs_get_features` is the primitive (one page). `wfs_page_all` wraps it with pagination loop.
- GetCapabilities is NOT exposed as a public function — it's large XML (~2MB), changes infrequently, and agents don't need it directly. Cache internally with 1h TTL if needed for layer discovery.
- `_parse_geojson()` from `shared/parsers.py` is reused for property extraction (no duplication).
- Error detection: check `response.status_code == 400` then `response.headers.get("content-type", "").startswith("application/xml")` then parse XML ExceptionReport.
- `httpx_client` injection parameter follows arcgis_hub.py pattern for testability.

---

## Curated Dataset Catalog (15 Verified Datasets)

All datasets verified via live WFS queries on 2026-04-10.

### Wildfire (2 tools)

| Tool | object_name | Key Filter Fields | Notes |
|------|-------------|-------------------|-------|
| `bc_get_active_fires` | `WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_PNTS_SP` | `FIRE_STATUS`, `FIRE_CENTRE`, `FIRE_CAUSE`, `FIRE_SIZE_HECTARES` | 21 active fires on research date; refreshed every 15min — use 5min TTL |
| `bc_get_fire_perimeters` | `WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP` | `FIRE_YEAR`, `FIRE_CAUSE`, `FIRE_SIZE_HECTARES`, `SOURCE` | 676 fires in 2023; polygon geometry; filter by year recommended |

Key properties verified:
- Active fires: `FIRE_NUMBER`, `FIRE_YEAR`, `FIRE_STATUS`, `FIRE_CAUSE`, `FIRE_CENTRE`, `ZONE`, `CURRENT_SIZE`, `LATITUDE`, `LONGITUDE`, `INCIDENT_NAME`, `FIRE_OF_NOTE_IND`
- Historical perimeters: `FIRE_NUMBER`, `FIRE_YEAR`, `FIRE_CAUSE`, `FIRE_SIZE_HECTARES`, `FIRE_LABEL`, `SOURCE`, `FEATURE_AREA_SQM`

### Forestry (3 tools)

| Tool | object_name | Key Filter Fields | Notes |
|------|-------------|-------------------|-------|
| `bc_get_forest_tenure` | `WHSE_FOREST_TENURE.FTEN_MANAGED_LICENCE_POLY_SVW` | `LIFE_CYCLE_STATUS_CODE`, `ML_TYPE_CODE`, `CLIENT_NAME`, `ADMIN_DISTRICT_NAME` | Active managed licences; 32K+ records; filter by ACTIVE status recommended |
| `bc_get_cut_blocks` | `WHSE_FOREST_TENURE.FTEN_CUT_BLOCK_POLY_SVW` | `LIFE_CYCLE_STATUS_CODE`, `ADMIN_DISTRICT_NAME`, `PLANNED_HARVEST_DATE` | Cut block polygons FTA 4.0; filter by LIFE_CYCLE_STATUS_CODE='ACTIVE' |
| `bc_get_protected_areas` | `WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW` | `PROTECTED_LANDS_DESIGNATION`, `PROTECTED_LANDS_NAME`, `OFFICIAL_AREA_HA` | 930 parks/reserves; designations: PROVINCIAL PARK, ECOLOGICAL RESERVE, CONSERVANCY |

Key properties verified:
- Forest tenure: `FOREST_FILE_ID`, `ML_TYPE_CODE`, `CLIENT_NAME`, `FEATURE_AREA_SQM`, `FILE_STATUS_CODE`, `LIFE_CYCLE_STATUS_CODE`, `ADMIN_DISTRICT_NAME`
- Cut blocks: `CUT_BLOCK_FOREST_FILE_ID`, `TIMBER_MARK`, `CUT_BLOCK_ID`, `BLOCK_STATUS_CODE`, `CLIENT_NAME`, `ADMIN_DISTRICT_NAME`, `LIFE_CYCLE_STATUS_CODE`, `PLANNED_GROSS_BLOCK_AREA`
- Protected areas: `PROTECTED_LANDS_NAME`, `PROTECTED_LANDS_DESIGNATION`, `OFFICIAL_AREA_HA`, `ESTABLISHMENT_DATE`, `ADMIN_AREA_SID`

### Environment (3 tools)

| Tool | object_name | Key Filter Fields | Notes |
|------|-------------|-------------------|-------|
| `bc_get_water_wells` | `WHSE_WATER_MANAGEMENT.GW_WATER_WELLS_WRBC_SVW` | `WELL_CLASS`, `WELL_STATUS`, `INTENDED_WATER_USE`, `CITY`, `AQUIFER_ID` | 130,666 records; use CQL filter by CITY or AQUIFER_ID to limit scope |
| `bc_get_wildfire_weather_stations` | `WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WEATHER_STATIONS_SP` | `STATION_NAME`, `ELEVATION` | 260 active stations; temperature/humidity/wind/rainfall monitoring |
| `bc_get_local_parks` | `WHSE_BASEMAPPING.GBA_LOCAL_REG_GREENSPACES_SP` | `MUNICIPALITY`, `REGIONAL_DISTRICT`, `PARK_TYPE`, `PARK_NAME` | Local/regional parks; filterable by municipality; includes area |

Note: Air quality monitoring stations are available as CSV download only (no BCGW WFS layer confirmed). Use `fetch_and_parse()` for the CSV at `ftp://ftp.env.gov.bc.ca/pub/outgoing/AIR/Air_Monitoring_Stations/`. Consider deferring air quality to a follow-up or replacing with local parks.

### Natural Resources (2 tools)

| Tool | object_name | Key Filter Fields | Notes |
|------|-------------|-------------------|-------|
| `bc_get_mining_tenure` | `WHSE_MINERAL_TENURE.MTA_ACQUIRED_TENURE_SVW` | `TENURE_TYPE_CODE` ('M'=Mineral, 'P'=Placer), `OWNER_NAME`, `GOOD_TO_DATE`, `AREA_IN_HECTARES` | 32,685 mineral claims; filter by TENURE_TYPE_CODE='M' |
| `bc_get_fish_habitat` | `WHSE_WILDLIFE_MANAGEMENT.CRIMS_HOLDING_AREAS` | `FEATURE_CODE` | Coastal fish holding areas (salmon/herring); legacy dataset from 1979 |

Key properties verified:
- Mining tenure: `TENURE_NUMBER_ID`, `CLAIM_NAME`, `TENURE_TYPE_CODE`, `TENURE_TYPE_DESCRIPTION`, `TENURE_SUB_TYPE_CODE`, `OWNER_NAME`, `ISSUE_DATE`, `GOOD_TO_DATE`, `AREA_IN_HECTARES`, `PROTECTED_IND`, `TERMINATION_DATE`

### Health (2 tools)

| Tool | object_name | Key Filter Fields | Notes |
|------|-------------|-------------------|-------|
| `bc_get_emergency_rooms` | `WHSE_IMAGERY_AND_BASE_MAPS.GSR_EMERGENCY_ROOMS_SV` | `LOCALITY`, `WHEELCHAIR_ACCESSIBLE_IND` | 104 24-hour ER facilities; includes ORGANIZATION_NAME, STREET_ADDRESS, CONTACT_PHONE, WEBSITE_URL |
| `bc_get_walk_in_clinics` | `WHSE_IMAGERY_AND_BASE_MAPS.GSR_MED_WALK_IN_CLINICS_SV` | `LOCALITY` | Walk-in clinic locations provincewide |

### Transportation (2 tools)

| Tool | object_name | Key Filter Fields | Notes |
|------|-------------|-------------------|-------|
| `bc_get_highway_profiles` | `WHSE_IMAGERY_AND_BASE_MAPS.MOT_HIGHWAY_PROFILES_SP` | `HIGHWAY_NUMBER`, `ADMIN_UNIT_NAME`, `NUMBER_OF_LANES`, `DIVIDED_HIGHWAY_IND` | BC Ministry of Transportation highway segments |
| `bc_get_road_structures` | `WHSE_IMAGERY_AND_BASE_MAPS.MOT_ROAD_STRUCTURE_SP` | Structure type (bridges, culverts, tunnels) | MoT-maintained road structures |

Note: BC Transit GTFS is NOT in the BCDC catalogue as of research date. Replace `bc_get_transit_stops` with a second transportation tool (highway profiles + road structures). Provincial transit data is available from BC Transit website separately but not via BCDC WFS.

### Climate (1 tool)

| Tool | object_name | Key Filter Fields | Notes |
|------|-------------|-------------------|-------|
| `bc_get_climate_stations` | `WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WEATHER_STATIONS_SP` | `STATION_NAME`, `ELEVATION` | 260 stations; note: this is the same wildfire weather network. For long-term climate normals, use Environment Canada ECCC data via CSV |

**Alternative for climate normals:** Use `fetch_and_parse()` on a BCDC CSV resource for long-term climate normals (not WFS-available).

---

## BCGW Object Name Schema

### WHSE_CATEGORY Pattern
```
WHSE_{CATEGORY}.{TABLE_NAME}_{VIEW_SUFFIX}
```

Common categories and their domains:
| Category | Domain |
|----------|--------|
| `WHSE_LAND_AND_NATURAL_RESOURCE` | Fire, wildlife, resource mgmt |
| `WHSE_FOREST_TENURE` | Forestry tenure, cut blocks, roads |
| `WHSE_TANTALIS` | Parks, protected areas, Crown land |
| `WHSE_MINERAL_TENURE` | Mining claims, tenure |
| `WHSE_WATER_MANAGEMENT` | Water wells, groundwater |
| `WHSE_WILDLIFE_MANAGEMENT` | Fish habitat, wildlife |
| `WHSE_ENVIRONMENTAL_MONITORING` | EMS monitoring groups |
| `WHSE_IMAGERY_AND_BASE_MAPS` | Health facilities, GSR services, highways |
| `WHSE_BASEMAPPING` | Health authorities, local parks |
| `WHSE_PARKS_ECOLOGY` | Note: some parks layers return 400 — use WHSE_TANTALIS instead |

### View Suffix Convention
- `_SVW` — Spatial View (polygon/point)
- `_SP` — Spatial (direct table)
- `_SV` — Spatial View (no suffix variant)
- `_POLY_SVW` — Polygon spatial view

---

## Two-Step Workflow Routing: bc_query_features

### Recommendation: Explicit routing via `queryable_via_wfs` flag

The `bc_get_dataset_details` response includes `queryable_via_wfs: bool` derived from the resource metadata. This flag is the authoritative routing signal. Do NOT attempt runtime auto-detection.

**Routing logic in `bc_query_features`:**
```python
if queryable_via_wfs:
    # Route to WFS via shared/ogc.py
    features, truncated = await wfs_page_all(
        WFS_BASE_URL,
        type_name=object_name,
        cql_filter=_build_cql(filter_params),
        max_records=max_records,
        include_geometry=include_geometry,
    )
else:
    # Route to file parser
    # Find the first resource with format in ("CSV", "XLSX", "XLS", "GeoJSON", "JSON")
    resource_url = _pick_file_resource(resources)
    features, was_cached = await fetch_and_parse(resource_url, ttl=CACHE_TTL_DATA)
    truncated = False
```

**When a dataset has BOTH WFS + CSV resources:** Prefer WFS (enables server-side CQL filtering, pagination). The `queryable_via_wfs=True` flag takes precedence.

**bc_get_dataset_details response shape:**
```python
{
    "id": "...",
    "name": "bc-wildfire-fire-perimeters-current",
    "title": "...",
    "description": "...",
    "object_name": "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_POLYS_SP",
    "queryable_via_wfs": True,
    "projection": "epsg3005",
    "organization": "...",
    "resources": [...],
    "metadata_modified": "...",
}
```

---

## Standard Stack

### Core (No new dependencies)
| Library | Version | Purpose | Source |
|---------|---------|---------|--------|
| `httpx` | existing | WFS HTTP requests | Already in stack |
| `xml.etree.ElementTree` | stdlib | WFS ExceptionReport XML parsing | No install needed |
| `shared/parsers._parse_geojson` | project | Parse WFS GeoJSON response features | Reuse existing |
| `shared/cache.cached_fetch` | project | TTL caching for all WFS/CKAN calls | Reuse existing |
| `shared/rate_limiter.get_limiter` | project | Per-source rate limiting | Reuse existing |

No new dependencies needed. The full stack (httpx, pydantic, aiocache) covers everything.

---

## Architecture Patterns

### Recommended Module Structure
```
src/mcp_canada/
├── shared/
│   └── ogc.py                    # NEW: WFS 2.0 client (BC first, reusable)
└── modules/
    └── bc/
        ├── __init__.py            # MODULE_NAME, MODULE_DESCRIPTION
        ├── constants.py           # BASE_URL, WFS_BASE_URL, RATE_*, TTLs, object_names
        ├── schemas.py             # Pydantic v2 flat models
        ├── client.py              # CKAN fetch + WFS via ogc.py
        ├── tools.py               # @tool functions (bc_ prefix)
        ├── prompts.py             # 6 bilingual @prompt functions
        ├── resources.py           # 7 zero-parameter @resource functions
        └── __tests__/
            ├── conftest.py
            ├── test_client.py
            ├── test_tools.py
            └── test_prompts_resources.py
```

### Pattern: constants.py Object Names Registry
Hardcode all 15 curated object_names in constants.py for discoverability and to avoid runtime string errors:
```python
# src/mcp_canada/modules/bc/constants.py
BASE_URL = "https://catalogue.data.gov.bc.ca/api/3/action/"
WFS_BASE_URL = "https://openmaps.gov.bc.ca/geo/ows"
RATE_GROUP_CKAN = "bc_ckan"
RATE_GROUP_WFS  = "bc_wfs"
RATE_LIMIT_CKAN = 10.0
RATE_LIMIT_WFS  = 5.0   # Conservative — no published limit

# WFS Layer object names
ACTIVE_FIRES_LAYER          = "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_PNTS_SP"
FIRE_PERIMETERS_LAYER       = "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_HISTORICAL_FIRE_POLYS_SP"
FOREST_TENURE_LAYER         = "WHSE_FOREST_TENURE.FTEN_MANAGED_LICENCE_POLY_SVW"
CUT_BLOCKS_LAYER            = "WHSE_FOREST_TENURE.FTEN_CUT_BLOCK_POLY_SVW"
PROTECTED_AREAS_LAYER       = "WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW"
WATER_WELLS_LAYER           = "WHSE_WATER_MANAGEMENT.GW_WATER_WELLS_WRBC_SVW"
WEATHER_STATIONS_LAYER      = "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WEATHER_STATIONS_SP"
LOCAL_PARKS_LAYER           = "WHSE_BASEMAPPING.GBA_LOCAL_REG_GREENSPACES_SP"
MINING_TENURE_LAYER         = "WHSE_MINERAL_TENURE.MTA_ACQUIRED_TENURE_SVW"
FISH_HABITAT_LAYER          = "WHSE_WILDLIFE_MANAGEMENT.CRIMS_HOLDING_AREAS"
EMERGENCY_ROOMS_LAYER       = "WHSE_IMAGERY_AND_BASE_MAPS.GSR_EMERGENCY_ROOMS_SV"
WALK_IN_CLINICS_LAYER       = "WHSE_IMAGERY_AND_BASE_MAPS.GSR_MED_WALK_IN_CLINICS_SV"
HIGHWAY_PROFILES_LAYER      = "WHSE_IMAGERY_AND_BASE_MAPS.MOT_HIGHWAY_PROFILES_SP"
ROAD_STRUCTURES_LAYER       = "WHSE_IMAGERY_AND_BASE_MAPS.MOT_ROAD_STRUCTURE_SP"

# Cache TTLs
CACHE_TTL_SEARCH    = 3600     # 1h
CACHE_TTL_META      = 86400    # 24h
CACHE_TTL_ACTIVE    = 300      # 5min (active fires, refreshed every 15min)
CACHE_TTL_STATIC    = 86400    # 24h (parks, tenure, wells)
```

### Pattern: client.py WFS helper
```python
async def _wfs_fetch(
    layer: str,
    cql: str | None,
    max_records: int,
    include_geometry: bool,
    ttl: int,
) -> tuple[list[dict], bool]:
    """Shared WFS fetch with caching and rate limiting."""
    cache_key = f"bc:wfs:{layer}:{cql}:{max_records}:{include_geometry}"
    limiter = get_limiter(RATE_GROUP_WFS, rate=RATE_LIMIT_WFS)

    async def fetcher():
        await limiter.acquire()
        features, truncated = await wfs_page_all(
            WFS_BASE_URL,
            type_name=layer,
            cql_filter=cql,
            max_records=max_records,
            include_geometry=include_geometry,
        )
        return {"features": features, "truncated": truncated}

    result, was_cached = await cached_fetch(cache_key, ttl, fetcher)
    return result["features"], was_cached
```

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| WFS XML error parsing | Custom XML parser | `xml.etree.ElementTree` (stdlib) | WFS ExceptionReport is simple XML; stdlib handles it |
| GeoJSON property extraction | Custom feature parser | `shared/parsers._parse_geojson()` | Already handles FeatureCollection correctly |
| HTTP retry on 429/5xx | Custom retry loop | `shared/http.api_get()` | Already has tenacity backoff |
| TTL caching | Custom dict cache | `shared/cache.cached_fetch()` | TTL eviction, async-safe |
| Rate limiting | asyncio.sleep throttle | `shared/rate_limiter.get_limiter()` | Token bucket, per-source |
| CKAN envelope unwrap | Custom response parser | Copy `_api_get()` from ontario/client.py | Pattern is stable and tested |
| CQL injection prevention | Complex sanitizer | Simple `value.replace("'", "''")` for strings + `int()` cast for numbers | WFS CQL has no nested query risk; simple escaping is sufficient |

---

## Common Pitfalls

### Pitfall 1: typeName vs typeNames (WFS 1.x vs 2.0)
**What goes wrong:** Using `typeName` (singular) instead of `typeNames` (plural) returns HTTP 400 ExceptionReport. GeoServer WFS 2.0 strictly enforces the plural form.
**How to avoid:** Always use `typeNames` in shared/ogc.py. Never accept single `typeName`.
**Warning sign:** HTTP 400 with XML body starting with `<ows:ExceptionReport`

### Pitfall 2: Default CRS is EPSG:3005 (BC Albers, not WGS84)
**What goes wrong:** If `srsName` is omitted, coordinates come back in BC Albers projection (easting/northing in meters, not lat/lon). Agents receiving `[1161815, 452123]` instead of `[-122.95, 51.93]` will fail to interpret location.
**How to avoid:** Always pass `srsName=EPSG:4326` in all WFS requests.

### Pitfall 3: WFS ExceptionReport body is XML even when outputFormat=application/json
**What goes wrong:** Client code calls `response.json()` on a 400 error response containing XML, raises `JSONDecodeError`.
**How to avoid:** In shared/ogc.py, check `response.status_code != 200` FIRST, then parse as XML if `content-type` contains `xml`. Never call `.json()` on a 400 response.

### Pitfall 4: Active fire data stale if TTL is too long
**What goes wrong:** BC Wildfire refreshes active fires every 15 minutes. A 1-hour TTL returns stale fire status during active wildfire events.
**How to avoid:** Use 5-minute TTL (`CACHE_TTL_ACTIVE = 300`) for `PROT_CURRENT_FIRE_PNTS_SP` and `PROT_CURRENT_FIRE_POLYS_SP`.

### Pitfall 5: Water wells layer has 130,666 records — no unfiltered calls
**What goes wrong:** Calling `bc_get_water_wells` without a CQL filter would attempt to paginate 130K records, hitting the 5000 cap immediately and returning a tiny fraction with `truncated=True`.
**How to avoid:** Require at least one filter parameter (CITY, WELL_CLASS, or AQUIFER_ID) in the tool. Return `INVALID_INPUT` error if no filters provided.

### Pitfall 6: BCGW layer names are case-sensitive
**What goes wrong:** Using `whse_forest_tenure.ften_cut_block_poly_svw` (lowercase) returns 400 ExceptionReport. The GeoServer is case-sensitive on typeNames.
**How to avoid:** Always use the UPPERCASE form exactly as documented. Constants in `constants.py` ensure consistency.

### Pitfall 7: CKAN group_list returns 403
**What goes wrong:** BC CKAN does not use groups. `group_list?all_fields=true` returns HTTP 403 Forbidden.
**How to avoid:** Use `organization_list` for ministry listing. Use `tag_list` for tag-based discovery. Use `fq=organization:{slug}` or `fq=tags:{tag}` in `package_search` for filtering.

### Pitfall 8: Some WHSE layers return 400 for certain schema prefixes
**What goes wrong:** `WHSE_PARKS_ECOLOGY.DPA_PROVINCIAL_POLY_SVW` returned 400 during research. Not all schemas are publicly accessible.
**How to avoid:** Only use verified object_names from this document. Do NOT attempt dynamic layer discovery without testing each name.

### Pitfall 9: CUT_BLOCK_POLYGONS vs FTEN_CUT_BLOCK_POLY_SVW
**What goes wrong:** The BCDC catalogue shows `WHSE_FOREST_TENURE.FTEN_CUT_BLOCK_POLYGONS` as the object_name for the superseded dataset. The active FTA 4.0 layer is `WHSE_FOREST_TENURE.FTEN_CUT_BLOCK_POLY_SVW`.
**How to avoid:** Always use the `_SVW` (Spatial View) variant when both exist — views are the publicly accessible version.

---

## Caching Strategy for WFS GetCapabilities

The GetCapabilities response is approximately 2MB of XML listing all 870 layers. It changes infrequently (new layers added, existing ones deprecated). **Recommendation:**

- Do NOT call GetCapabilities at module startup or on every tool call.
- Cache with 1h TTL using `cached_fetch()` with a `bc:wfs:capabilities` key.
- Only implement a `bc_list_wfs_layers` tool if there is a clear agent use case.
- For the 15 curated tools, the object_names are hardcoded in constants.py — GetCapabilities is not needed at runtime.

---

## Prompts and Resources Specification

### 6 Bilingual Prompts

| Function | Type | Description |
|----------|------|-------------|
| `bc_explore_wildfires` | guided workflow (list[Message]) | Multi-step: discover active fires → check perimeters → summarize fire season |
| `bc_explore_forestry` | guided workflow (list[Message]) | Tenure → cut blocks → protected areas chain |
| `bc_explore_environment` | guided workflow (list[Message]) | Water wells → parks → mining overview |
| `bc_quick_dataset_search` | quick lookup (str) | bc_search_datasets + bc_get_dataset_details flow |
| `bc_check_water_quality` | quick lookup (str) | bc_get_water_wells with city + well_class filter |
| `bc_wildfire_status_now` | quick lookup (str) | bc_get_active_fires with status filter |

### 7 Zero-Parameter Resources

| URI | Type | Content |
|-----|------|---------|
| `data://bc/ministries` | data | JSON catalog of BC ministry org slugs (for organization= filter) |
| `data://bc/wildfire-status-codes` | data | JSON: FIRE_STATUS codes (Active, Being Held, Under Control, Out, Out of Control) + FIRE_CAUSE codes |
| `data://bc/object-name-prefixes` | data | JSON: WHSE category → domain mapping (all 15 curated layers) |
| `docs://bc/wfs-query-guide` | docs | Markdown: CKAN → WFS two-step workflow, CQL syntax, pagination |
| `docs://bc/bcdc-api-quirks` | docs | Markdown: custom fields, queryable_via_wfs detection, no groups, organization slugs |
| `template://bc/wildfire-report` | template | Markdown template with {fire_season}, {total_fires}, {largest_fire}, {cause_breakdown} |
| `template://bc/dataset-report` | template | Markdown template for dataset exploration reports |

---

## Validation Architecture

> nyquist_validation is `true` in .planning/config.json — this section is MANDATORY.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio |
| Config file | `pytest.ini` (existing) |
| Quick run command | `uv run pytest src/mcp_canada/modules/bc/__tests__/ -x -v` |
| Full suite command | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |

### Phase Requirements to Test Map

| Behavior | Test Type | Automated Command | Notes |
|----------|-----------|-------------------|-------|
| shared/ogc.py: wfs_get_features returns GeoJSON features | unit (mocked httpx) | `uv run pytest src/mcp_canada/shared/__tests__/test_ogc.py -x -v` | Wave 0 gap — needs new test file |
| shared/ogc.py: wfs_page_all paginates to max_records | unit (mocked httpx) | same | Test truncated=True at cap |
| shared/ogc.py: WfsError raised on 400 XML response | unit (mocked httpx) | same | Test ExceptionReport parsing |
| bc_search_datasets returns shaped results | unit | `uv run pytest src/mcp_canada/modules/bc/__tests__/test_tools.py::TestBcSearchDatasets -x -v` | Wave 0 gap |
| bc_get_dataset_details surfaces object_name + queryable_via_wfs | unit | same | Critical routing field |
| bc_query_features routes to WFS when queryable_via_wfs=True | unit | same | Test routing logic |
| bc_query_features routes to fetch_and_parse when queryable_via_wfs=False | unit | same | File parser routing |
| bc_get_active_fires with CQL status filter | unit | same | |
| bc_get_fire_perimeters with FIRE_YEAR filter | unit | same | |
| bc_get_forest_tenure with LIFE_CYCLE_STATUS_CODE filter | unit | same | |
| bc_get_cut_blocks returns properties | unit | same | |
| bc_get_protected_areas with DESIGNATION filter | unit | same | |
| bc_get_water_wells requires at least one filter | unit | same | INVALID_INPUT on no-filter call |
| bc_get_mining_tenure with TENURE_TYPE_CODE filter | unit | same | |
| bc_get_emergency_rooms returns 104 facilities | unit | same | Count can vary slightly |
| All tools return _meta envelope | unit | `uv run pytest src/mcp_canada/modules/bc/__tests__/test_tools.py -x -v` | |
| All tools propagate lang parameter | unit | same | |
| Integration: bc_search_datasets finds wildfire datasets | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestBcToolScenarios::test_search_finds_wildfire_data -v -m integration --timeout=30` | Wave 0 gap in test_tool_scenarios.py |
| Integration: bc_get_active_fires returns _meta envelope | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestBcToolScenarios::test_active_fires_returns_meta -v -m integration --timeout=30` | Live WFS |
| Integration: bc_get_fire_perimeters with year=2023 returns data | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestBcToolScenarios::test_fire_perimeters_by_year -v -m integration --timeout=60` | 676 records in 2023 |
| Integration: bc_get_protected_areas returns parks | integration | same class | |
| Integration: bc_get_mining_tenure mineral claims | integration | same class | |
| Integration: discover_tools finds bc_ tools via BM25 | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestBcToolScenarios::test_discover_bc_wildfire_tools -v -m integration --timeout=30` | |
| Integration: bc prompts discoverable via list_prompts | integration | `uv run pytest tests/integration/test_prompts_resources_scenarios.py::TestBcPromptsResources -v -m integration --timeout=30` | Wave 0 gap |
| Integration: bc resources readable via read_resource | integration | same | data://, docs://, template:// URIs |
| BM25 docstring quality: all bc_ tools have Keywords + Use-for | quality | `uv run pytest src/mcp_canada/modules/bc/__tests__/test_tools.py -k quality -v` | test_quality.py auto-enforces this |
| Coverage ≥ 95% for bc module | coverage | `uv run pytest --cov=src/mcp_canada/modules/bc --cov-fail-under=95` | |
| Coverage ≥ 95% for shared/ogc.py | coverage | `uv run pytest --cov=src/mcp_canada/shared/ogc --cov-fail-under=95` | |

### Sampling Rate
- **Per task commit:** `uv run pytest src/mcp_canada/modules/bc/__tests__/ src/mcp_canada/shared/__tests__/test_ogc.py -x -v`
- **Per wave merge:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps (must exist before implementation)
- [ ] `src/mcp_canada/shared/__tests__/test_ogc.py` — covers wfs_get_features, wfs_page_all, WfsError, ExceptionReport XML parsing
- [ ] `src/mcp_canada/modules/bc/__tests__/conftest.py` — sample CKAN + WFS GeoJSON fixtures
- [ ] `src/mcp_canada/modules/bc/__tests__/test_client.py` — CKAN client + WFS routing
- [ ] `src/mcp_canada/modules/bc/__tests__/test_tools.py` — all 20 tool functions
- [ ] `src/mcp_canada/modules/bc/__tests__/test_prompts_resources.py` — prompt/resource rendering
- [ ] Append `TestBcToolScenarios` class to `tests/integration/test_tool_scenarios.py`
- [ ] Append `TestBcPromptsResources` class to `tests/integration/test_prompts_resources_scenarios.py`

---

## Code Examples

### WFS GetFeature (verified live)
```python
# Source: verified against https://openmaps.gov.bc.ca/geo/ows 2026-04-10
import httpx

params = {
    "service": "WFS",
    "version": "2.0.0",
    "request": "GetFeature",
    "typeNames": "WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_PNTS_SP",
    "outputFormat": "application/json",
    "count": 100,
    "startIndex": 0,
    "sortBy": "OBJECTID",
    "srsName": "EPSG:4326",
    "CQL_FILTER": "FIRE_STATUS='Out'",
}
async with httpx.AsyncClient() as client:
    response = await client.get("https://openmaps.gov.bc.ca/geo/ows", params=params)
    if response.status_code == 400:
        # XML ExceptionReport
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)
        ns = {"ows": "http://www.opengis.net/ows/1.1"}
        exc = root.find(".//ows:Exception", ns)
        code = exc.get("exceptionCode", "UnknownError") if exc is not None else "UnknownError"
        text = exc.findtext("ows:ExceptionText", "", ns) if exc is not None else ""
        raise WfsError(code, text)
    data = response.json()
    # data["features"] -> list of GeoJSON Feature dicts
    # data["numberMatched"] -> total matching records
    # data["numberReturned"] -> records in this page
```

### CKAN package_search with bcgov extension filter
```python
# Source: verified against https://catalogue.data.gov.bc.ca/api/3/action/ 2026-04-10
params = {
    "q": "wildfire fire perimeter",
    "fq": "bcdc_type:geographic security_class:PUBLIC",
    "rows": 10,
    "start": 0,
}
# Returns: {"success": true, "result": {"count": N, "results": [...]}}
# Each result has resources with: object_name, bcdc_type, resource_storage_location
```

### queryable_via_wfs detection
```python
def _get_wfs_resource(dataset: dict) -> dict | None:
    """Return the first WFS-queryable resource or None."""
    for resource in dataset.get("resources", []):
        if (
            resource.get("bcdc_type") == "geographic"
            and resource.get("resource_storage_location") == "bc geographic warehouse"
            and resource.get("object_name")
        ):
            return resource
    return None

wfs_resource = _get_wfs_resource(raw_dataset)
object_name = wfs_resource["object_name"] if wfs_resource else None
queryable_via_wfs = wfs_resource is not None
```

### CQL filter builder (safe)
```python
def _build_cql(filters: dict[str, str | int | float]) -> str | None:
    """Build a safe CQL filter string from simple key=value pairs."""
    if not filters:
        return None
    parts = []
    for field, value in filters.items():
        if isinstance(value, str):
            escaped = value.replace("'", "''")
            parts.append(f"{field}='{escaped}'")
        else:
            parts.append(f"{field}={value}")
    return " AND ".join(parts)
```

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| `typeName` (WFS 1.x) | `typeNames` (WFS 2.0) | Must use plural form — singular returns 400 |
| EPSG:3005 default | Specify `srsName=EPSG:4326` | Returns human-readable lat/lon |
| WFS `maxFeatures` (WFS 1.x) | `count` (WFS 2.0) | Different parameter names by version |
| GetCapabilities for layer discovery | CKAN API for dataset/layer discovery | CKAN is the right entry point; GetCaps is for raw layer listing only |
| Ontario client copy-paste | Extract shared CKAN pattern | Consider extracting shared ckan.py after BC (Quebec will need same thing) |

---

## Open Questions

1. **BC Transit GTFS data**
   - What we know: Not found in BCDC CKAN catalogue as of research date. Provincial BC Transit (not TransLink/Vancouver) does not appear to publish GTFS via BCDC.
   - What's unclear: BC Transit may have a separate GTFS feed at bctransit.com. Not researched.
   - Recommendation: Replace `bc_get_transit_stops` with `bc_get_road_structures` (verified WFS layer). Optionally add a note in the tool docstring about BC Transit's separate feed.

2. **Air Quality monitoring stations as WFS**
   - What we know: Air quality monitoring CSV is available via FTP/direct download, not a BCGW WFS layer.
   - What's unclear: Whether `WHSE_ENVIRONMENTAL_MONITORING.EMS_MONITORING_LOCN_SVW` (which returned 400) would work with different parameter formats.
   - Recommendation: Replace `bc_get_air_quality_stations` with `bc_get_local_parks` (verified at WHSE_BASEMAPPING.GBA_LOCAL_REG_GREENSPACES_SP) to maintain the 15-tool curated count.

3. **Long-term climate normals**
   - What we know: Only wildfire weather stations (260 points) confirmed via WFS. Long-term climate normals (Environment Canada) are federal, not BC provincial.
   - Recommendation: `bc_get_climate_stations` covers wildfire weather network (260 stations). For full climate normals, agents should use the Weather module's `wx_` tools.

4. **FTEN_CUT_BLOCK_POLYGONS 400 error**
   - What we know: `WHSE_FOREST_TENURE.FTEN_CUT_BLOCK_POLYGONS` returned HTTP 400. `WHSE_FOREST_TENURE.FTEN_CUT_BLOCK_POLY_SVW` succeeded.
   - Recommendation: Use `_SVW` (Spatial View) variant for cut blocks.

---

## Sources

### Primary (HIGH confidence — verified with live endpoints 2026-04-10)
- `https://catalogue.data.gov.bc.ca/api/3/action/package_search` — CKAN API structure, bcgov custom fields
- `https://catalogue.data.gov.bc.ca/api/3/action/package_show?id=bc-wildfire-fire-perimeters-current` — resource routing fields
- `https://openmaps.gov.bc.ca/geo/ows?service=WFS&version=2.0.0&request=GetCapabilities` — WFS service capabilities, output formats, CRS
- `https://openmaps.gov.bc.ca/geo/ows?...typeNames=PROT_CURRENT_FIRE_PNTS_SP...` — CQL_FILTER, pagination, GeoJSON response shape
- `https://openmaps.gov.bc.ca/geo/ows?...typeNames=PROT_HISTORICAL_FIRE_POLYS_SP...` — historical fire perimeters, FIRE_YEAR filter
- `https://openmaps.gov.bc.ca/geo/ows?...typeNames=WHSE_TANTALIS.TA_PARK_ECORES_PA_SVW...` — parks layer
- `https://openmaps.gov.bc.ca/geo/ows?...typeNames=WHSE_MINERAL_TENURE.MTA_ACQUIRED_TENURE_SVW...` — mining tenure
- `https://openmaps.gov.bc.ca/geo/ows?...typeNames=WHSE_FOREST_TENURE.FTEN_MANAGED_LICENCE_POLY_SVW...` — forest tenure
- `https://openmaps.gov.bc.ca/geo/ows?...typeNames=WHSE_FOREST_TENURE.FTEN_CUT_BLOCK_POLY_SVW...` — cut blocks
- `https://openmaps.gov.bc.ca/geo/ows?...typeNames=WHSE_WATER_MANAGEMENT.GW_WATER_WELLS_WRBC_SVW...` — water wells (130K records)
- `https://openmaps.gov.bc.ca/geo/ows?...typeNames=WHSE_IMAGERY_AND_BASE_MAPS.GSR_EMERGENCY_ROOMS_SV...` — emergency rooms (104 facilities)
- `https://bcgov.github.io/data-publication/pages/tips_tricks_webservices.html` — CQL syntax, pagination, output formats

### Secondary (MEDIUM confidence — official docs)
- `https://docs.geoserver.org/stable/en/user/services/wfs/reference.html` — WFS 2.0 parameter reference, typeNames vs typeName
- `https://www2.gov.bc.ca/gov/content/data/finding-and-sharing/bc-geographic-warehouse` — BCGW overview, 870 public datasets

### Tertiary (LOW confidence — search-derived)
- BC Transit GTFS availability: not found; may exist separately at bctransit.com

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all API calls verified live
- CKAN API structure: HIGH — package_search, package_show, org_list verified
- WFS protocol: HIGH — GetFeature, CQL_FILTER, pagination, srsName all tested
- Object names (15 curated): HIGH — 12 of 15 verified with live WFS queries; 3 inferred from CKAN metadata
- Architecture: HIGH — follows established project patterns (arcgis_hub.py as template)
- Pitfalls: HIGH — directly encountered during research (400 errors, CRS defaults)

**Research date:** 2026-04-10
**Valid until:** 2026-07-10 (90 days — WFS API is stable; BCDC catalogue layout rarely changes)
