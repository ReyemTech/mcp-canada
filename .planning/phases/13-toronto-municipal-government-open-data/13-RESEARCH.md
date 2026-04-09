# Phase 13: Toronto Municipal Government Open Data - Research

**Researched:** 2026-04-09
**Domain:** Toronto CKAN Open Data API + GTFS ZIP parsing + Neighbourhood Profiles + Datastore SQL
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **CKAN base URL:** `ckan0.cf.opendata.inter.prod-toronto.ca`
- **Tool prefix:** `toronto_` (consistent with `ontario_` pattern; convention locked for all future municipal modules)
- **Curated datasets:**
  - TTC transit: parse GTFS CSV files (stops.txt, routes.txt, trips.txt) from ZIP — not just download links
  - Neighbourhood profiles: two tools — single-neighbourhood deep dive (all indicators) + cross-neighbourhood comparison (single indicator across all 140/158 neighbourhoods)
  - 311 Service Requests: use CKAN Datastore SQL (`datastore_search_sql`) for server-side filtering by date range, category, ward — dataset is too large to fetch entirely
  - Property/housing: building permits + short-term rentals (Airbnb/VRBO registrations) + apartment buildings (RentSafeTO scores)
  - Budget/finance: Financial Information Return — revenue, expenses, capital spending by department
- **Data format handling:** Parse CSV, XLSX, JSON, GeoJSON; GeoJSON properties-only by default with `include_geometry=true` opt-in
- **New parsers:** `_parse_geojson()` and `_parse_json()` go into `shared/parsers.py` — reusable for all future modules

### Claude's Discretion

- Exact CKAN Datastore SQL query patterns for 311 data
- Which specific GTFS files to parse (stops.txt is essential; shapes.txt may be too large)
- RentSafeTO vs apartment buildings dataset selection based on data quality
- How to handle neighbourhood profile indicator names (snake_case or preserve original)

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.

</user_constraints>

---

## Summary

Phase 13 adds the City of Toronto's open data catalogue to mcp-canada. Toronto runs a standard CKAN 2.9 instance at `ckan0.cf.opendata.inter.prod-toronto.ca` with three custom plugins (`updateschema`, `extendedapi`, `extendedurl`) that add Toronto-specific fields but do not break CKAN API compatibility. The module structure mirrors the Phase 12 Ontario module exactly — same 5-file pattern, same `_api_get` helper with caching/rate-limiting, same `_shape_dataset` bilingual fallback chain.

The critical implementation discoveries are: (1) The 311 Service Requests dataset has **zero datastore_active resources** — all 18 annual resources are ZIP files; the `datastore_search_sql` strategy must be re-evaluated or redirected to a dataset that is actually datastore-active. (2) GTFS data arrives as a single 35.9 MB ZIP — requires `zipfile` + `BytesIO` stdlib parsing (no new dependencies). (3) The 2021 Neighbourhood Profiles dataset is XLSX-only (no datastore-active CSV); the 2016 and earlier are datastore-active CSVs but use the 140-neighbourhood model. (4) RentSafeTO apartment evaluation datasets ARE datastore-active with rich fields. (5) Budget data is annual XLSX with no datastore access.

**Primary recommendation:** Mirror Ontario module for CKAN discovery tools; add seven curated tools covering TTC, neighbourhoods (2 tools), 311 (parse ZIP CSVs with client-side filter since SQL is unavailable), housing/property (building permits + short-term rentals + RentSafeTO), and budget (XLSX parse). Add GeoJSON + JSON parsers to `shared/parsers.py`.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `httpx` | existing | Async HTTP for CKAN API + file downloads | Already in stack; handles timeout/retry |
| `zipfile` | stdlib | Unpack GTFS ZIP in-memory via BytesIO | No new dep; Python stdlib |
| `csv` / `io` | stdlib | Parse GTFS `.txt` files from ZIP | Already used in `_parse_csv` |
| `json` | stdlib | Parse JSON resources from CKAN | Already used everywhere |
| `aiocache` | existing | Cache all parsed data | Already in stack via `cached_fetch` |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pandas` / `openpyxl` | existing optional | Parse Neighbourhood Profile XLSX (2021) and Budget XLSX | Existing fallback chain in `_parse_xlsx` |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| stdlib `zipfile` | `gtfs-kit`, `pygtfs` | External deps violate dependency policy; stdlib handles GTFS ZIP fine |
| Client-side 311 filter | `datastore_search_sql` | SQL path is unavailable — no datastore-active 311 resources exist |

**Installation:**
```bash
# No new dependencies — all stdlib or already in stack
```

---

## Architecture Patterns

### Recommended Project Structure

```
src/mcp_canada/modules/toronto/
├── __init__.py          # MODULE_NAME = "toronto", MODULE_DESCRIPTION
├── constants.py         # BASE_URL, RATE_GROUP, RATE_LIMIT, cache TTLs, curated IDs
├── schemas.py           # GTFSStop, GTFSRoute, NeighbourhoodProfile Pydantic models (flat)
├── client.py            # All async fetch functions returning (data, was_cached)
├── tools.py             # @tool functions with toronto_ prefix
└── __tests__/
    ├── __init__.py
    ├── conftest.py      # Sample CKAN responses, GTFS bytes, RentSafeTO rows
    ├── test_client.py   # Unit tests mocking httpx
    └── test_tools.py    # Unit tests mocking client functions
```

**shared/parsers.py additions:**
- `_parse_geojson(content: bytes, include_geometry: bool = False) -> list[dict]`
- `_parse_json(content: bytes) -> list[dict] | dict`
- Route both in `fetch_and_parse()` by URL suffix: `.geojson` → GeoJSON, `.json` → JSON

### Pattern 1: Toronto CKAN Client (mirrors Ontario exactly)

**What:** Copy Ontario's `_api_get` helper, swap `BASE_URL` and `RATE_GROUP`. Same `_shape_dataset` with bilingual fallback chain.
**When to use:** All 5 discovery tools (search_datasets, get_dataset_details, get_resource, list_organizations, get_dataset_stats).

```python
# Source: src/mcp_canada/modules/ontario/client.py (established pattern)
BASE_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/"
RATE_GROUP = "toronto"
RATE_LIMIT = 5.0  # conservative — no published Toronto CKAN rate limit

async def _api_get(path: str, params: dict, cache_ttl: int) -> tuple[Any, bool]:
    url = BASE_URL + path
    cache_key = f"toronto:{path}?{_sorted_params(params)}"
    limiter = get_limiter(RATE_GROUP, rate=RATE_LIMIT)

    async def fetcher() -> Any:
        await limiter.acquire()
        async with httpx.AsyncClient(timeout=30.0) as http:
            response = await http.get(url, params=params)
            response.raise_for_status()
            return response.json()["result"]

    return await cached_fetch(cache_key, cache_ttl, fetcher)
```

### Pattern 2: GTFS ZIP Parsing (NEW — no dep)

**What:** Download GTFS ZIP, unpack in-memory with stdlib `zipfile`, parse selected `.txt` files as CSVs using existing `_parse_csv` logic.
**When to use:** `toronto_get_ttc_routes`, `toronto_get_ttc_stops`.

```python
# Source: Python stdlib zipfile + existing _parse_csv pattern
import zipfile
from io import BytesIO

async def fetch_gtfs_file(zip_url: str, filename: str, ttl: int = 21600) -> tuple[list[dict], bool]:
    """Fetch GTFS ZIP and extract a single .txt file as list[dict]."""
    cache_key = f"toronto:gtfs:{filename}"

    async def fetcher() -> list[dict]:
        async with httpx.AsyncClient(timeout=120.0) as http:  # large ZIP
            response = await http.get(zip_url)
            response.raise_for_status()
            with zipfile.ZipFile(BytesIO(response.content)) as zf:
                with zf.open(filename) as f:
                    return _parse_csv(f.read(), skip_rows=0)

    return await cached_fetch(cache_key, ttl, fetcher)
```

**Avoid `shapes.txt`** — it can exceed 5 MB per mode and is not useful for agent queries.

### Pattern 3: CKAN Datastore Search (for RentSafeTO, active datastore resources)

**What:** Use `datastore_search` action (not SQL) for resources confirmed as `datastore_active=true`. Returns paginated rows with field metadata.
**When to use:** RentSafeTO apartment evaluations (`244f7a02-da5c-425b-b55f-fbdd133dd732`), Building Permits - Pool Enclosures (`7114cd7e-103a-438b-9258-d80e7b0e10d2`).

```python
# Source: CKAN API docs — standard action
async def fetch_datastore_records(
    resource_id: str,
    filters: dict | None = None,
    limit: int = 100,
    offset: int = 0,
    fields: list[str] | None = None,
    cache_ttl: int = 3600,
) -> tuple[list[dict], bool]:
    params: dict = {"resource_id": resource_id, "limit": limit, "offset": offset}
    if filters:
        params["filters"] = json.dumps(filters)
    if fields:
        params["fields"] = ",".join(fields)
    result, cached = await _api_get("action/datastore_search", params, cache_ttl)
    return result.get("records", []), cached
```

### Pattern 4: GeoJSON Parser (NEW — to shared/parsers.py)

**What:** Parse GeoJSON `FeatureCollection` into flat list[dict]. By default extract only `properties`; with `include_geometry=True` add `geometry` key.
**When to use:** Toronto Neighbourhoods boundary dataset, any GeoJSON resource.

```python
# New function in shared/parsers.py
def _parse_geojson(content: bytes, include_geometry: bool = False) -> list[dict[str, Any]]:
    """Parse GeoJSON FeatureCollection bytes into a flat list of property dicts.

    Args:
        content: Raw GeoJSON bytes.
        include_geometry: If True, adds 'geometry' key to each record.

    Returns:
        list of dicts — one per Feature, keys from Feature.properties.
    """
    data = json.loads(content.decode("utf-8"))
    features = data.get("features", [])
    result = []
    for feature in features:
        props = dict(feature.get("properties") or {})
        if include_geometry:
            props["geometry"] = feature.get("geometry")
        result.append(props)
    return result
```

Route in `fetch_and_parse()`:
```python
elif lower_url.endswith(".geojson"):
    return _parse_geojson(raw, include_geometry=False)
elif lower_url.endswith(".json"):
    return _parse_json(raw)
```

### Pattern 5: Neighbourhood Profile Parsing

**What:** The 2016 dataset (datastore-active) uses **indicator-per-row** layout with 140+ neighbourhood columns. Query via `datastore_search` filtering by `Characteristic`. The 2021 dataset is XLSX-only with same indicator-per-row layout.
**When to use:** `toronto_get_neighbourhood_profile` (single neighbourhood), `toronto_compare_neighbourhoods` (single indicator).

```python
# Query 2016 datastore-active resource by Characteristic
# resource_id: "7f8eee5e-85fb-415c-aef3-c3bd4998445f" (2016 140-model)
# Each row: {Category, Topic, Characteristic, "Agincourt North": val, "Alderwood": val, ...}
# For single-neighbourhood: filter rows by neighbourhood column name, pivot to flat dict
# For cross-neighbourhood: filter rows by Characteristic, return one value per neighbourhood
```

### Anti-Patterns to Avoid

- **Using `datastore_search_sql` for 311 data:** None of the 311 Customer-Initiated resources have `datastore_active=true`. All 18 resources are annual ZIPs. Use client-side filtering on parsed CSV rows instead, or direct the tool to fetch a specific year's ZIP.
- **Fetching full GTFS ZIP on every request:** 35.9 MB ZIP — must cache aggressively (TTL >= 6 hours).
- **Fetching shapes.txt from GTFS:** May exceed MCP context budget; skip unless explicitly needed.
- **Using `@mcp.tool` instead of standalone `@tool`:** Silently won't register via FileSystemProvider.
- **Cache key collision with Ontario module:** Prefix all keys with `"toronto:"` not `"ontario:"`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| ZIP decompression | Custom HTTP streaming unpacker | `zipfile.ZipFile(BytesIO(...))` | Stdlib handles ZIP natively |
| CSV parsing from ZIP entry | Custom text parser | `_parse_csv(f.read())` from existing shared/parsers | Already handles BOM, normalization |
| CKAN envelope unwrapping | Per-tool response shaping | `_api_get` helper (Ontario pattern) | `{"success": True, "result": ...}` is identical |
| GeoJSON parsing | External `geojson` library | `json.loads` + property extraction | No complex validation needed; stdlib JSON is enough |
| Rate limiting | Custom sleep/delay | `get_limiter(RATE_GROUP, rate=RATE_LIMIT)` | Existing TokenBucket in shared/ |
| Caching | Manual dict | `cached_fetch(key, ttl, fetcher)` | Existing aiocache integration |

**Key insight:** The Toronto CKAN is standard CKAN — the Ontario module is a direct template. New work is only (a) GeoJSON/JSON parsers in shared/, (b) GTFS ZIP parsing, and (c) curated dataset-specific client functions.

---

## Common Pitfalls

### Pitfall 1: 311 Datastore SQL Assumption

**What goes wrong:** Attempting `datastore_search_sql` on 311 Service Requests dataset — all 18 resources return `datastore_active: false`. The API call returns a 404 or CKAN error.
**Why it happens:** The 311 dataset is delivered as annual ZIP archives, not loaded into CKAN's PostgreSQL datastore.
**How to avoid:** For 311 tool, either (a) fetch a specific year's CSV from inside the ZIP and filter client-side, or (b) limit scope to the Animal Services service requests which IS datastore-active. Recommending option (a): download requested year's ZIP, parse CSV from inside, apply ward/category/date filters in Python.
**Warning signs:** Tool returns `{"success": false, "error": {"message": "Resource ... was not found in the datastore"}}`.

### Pitfall 2: GTFS ZIP Size / Timeout

**What goes wrong:** GTFS ZIP is 35.9 MB. Default `httpx.AsyncClient(timeout=30.0)` will time out on slow connections.
**Why it happens:** Large file download over public internet.
**How to avoid:** Use `timeout=120.0` for GTFS downloads. Cache result with TTL of 6+ hours (updates every 6 weeks). Only download on cache miss.
**Warning signs:** `httpx.ReadTimeout` exception in tests or production.

### Pitfall 3: Neighbourhood Profile Column Layout

**What goes wrong:** Treating the neighbourhood profile as row-per-neighbourhood. It is actually indicator-per-row with neighbourhoods as columns. Naively iterating rows gives 2,383 indicator rows, not 140 neighbourhood rows.
**Why it happens:** Statistics Canada census profile format — designed for indicator comparison, not neighbourhood listing.
**How to avoid:** When building the single-neighbourhood tool, filter by neighbourhood column (select all rows, extract that column's value). When building cross-neighbourhood tool, filter by `Characteristic` row and return the full row values as a neighbourhood→value dict.
**Warning signs:** Tool returns 2,383 records when user asks for one neighbourhood's data.

### Pitfall 4: Toronto CKAN Custom Field Names

**What goes wrong:** Toronto CKAN resources have additional metadata fields (`datastore_cache`, `dataset_category`, `civic_issues`, `refresh_rate`) that Ontario CKAN doesn't have. `_shape_resource` may need to expose `datastore_active` flag to help agents decide whether SQL queries are possible.
**Why it happens:** Toronto's `updateschema` plugin extends the standard CKAN resource schema.
**How to avoid:** Extend `_shape_resource` (Toronto-specific version) to include `datastore_active: bool` in the shaped output. Agents can then know which resources support `datastore_search`.

### Pitfall 5: 2021 Neighbourhood Data Is XLSX Only

**What goes wrong:** Assuming datastore-active CSV exists for the most recent (2021) neighbourhood data. Only 2016 and earlier have datastore-active CSVs.
**Why it happens:** 2021 dataset was added in XLSX format using the 158-neighbourhood model; not yet loaded to datastore.
**How to avoid:** Use the 2016 datastore-active resource (`7f8eee5e-85fb-415c-aef3-c3bd4998445f`) for the neighbourhood profile tools. Document in tool docstring that data is from 2016 census.

### Pitfall 6: Cache Key Collision With Ontario Module

**What goes wrong:** Both Ontario and Toronto modules use `cached_fetch`. If Toronto uses the same key pattern without prefix, queries collide.
**Why it happens:** Ontario already set the precedent: `f"ontario:{path}?{sorted_params}"`.
**How to avoid:** All Toronto cache keys use `f"toronto:{path}?{sorted_params}"` prefix — established in Phase 12 STATE.md decision.

---

## Code Examples

### Full GTFS stops.txt Parse (with cache)

```python
# In toronto/client.py
GTFS_ZIP_URL = "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/7795b45e-e65a-4465-81fc-c36b9dfff169/resource/cfb6b2b8-6191-41e3-bda1-b175c51148cb/download/opendata_ttc_schedules.zip"
CACHE_TTL_GTFS = 21600  # 6 hours — GTFS updates every ~6 weeks

async def fetch_gtfs_stops(query: str | None = None) -> tuple[list[dict], bool]:
    """Fetch and parse TTC stops from GTFS ZIP. Filters by name substring if query given."""
    cache_key = "toronto:gtfs:stops.txt"

    async def fetcher() -> list[dict]:
        async with httpx.AsyncClient(timeout=120.0) as http:
            r = await http.get(GTFS_ZIP_URL)
            r.raise_for_status()
        with zipfile.ZipFile(BytesIO(r.content)) as zf:
            with zf.open("stops.txt") as f:
                return _parse_csv(f.read(), skip_rows=0)

    rows, cached = await cached_fetch(cache_key, CACHE_TTL_GTFS, fetcher)
    if query:
        q = query.lower()
        rows = [r for r in rows if q in str(r.get("stop_name", "")).lower()]
    return rows, cached
```

### RentSafeTO Evaluation via datastore_search

```python
# resource_id for "Apartment Building Evaluations 2023-current"
RENTSAFE_EVAL_RESOURCE_ID = "244f7a02-da5c-425b-b55f-fbdd133dd732"

async def fetch_rentsafe_evaluations(
    ward: str | None = None,
    min_score: int | None = None,
    limit: int = 50,
) -> tuple[list[dict], bool]:
    params: dict = {
        "resource_id": RENTSAFE_EVAL_RESOURCE_ID,
        "limit": limit,
    }
    if ward:
        params["filters"] = json.dumps({"WARD": ward})
    result, cached = await _api_get("action/datastore_search", params, CACHE_TTL_SEARCH)
    records = result.get("records", [])
    if min_score is not None:
        records = [
            r for r in records
            if r.get("CURRENT_BUILDING_EVAL_SCORE") is not None
            and r["CURRENT_BUILDING_EVAL_SCORE"] >= min_score
        ]
    return records, cached
```

### GeoJSON Parser (shared/parsers.py addition)

```python
import json

def _parse_geojson(content: bytes, include_geometry: bool = False) -> list[dict[str, Any]]:
    """Parse GeoJSON FeatureCollection into flat property dicts.

    Args:
        content: Raw GeoJSON bytes.
        include_geometry: If True, includes 'geometry' key in each record.

    Returns:
        list of dicts with Feature properties (+ optional geometry).
    """
    data = json.loads(content.decode("utf-8"))
    features = data.get("features", [])
    result = []
    for feature in features:
        props = dict(feature.get("properties") or {})
        if include_geometry:
            props["geometry"] = feature.get("geometry")
        result.append(props)
    return result


def _parse_json(content: bytes) -> list[dict[str, Any]]:
    """Parse JSON bytes into list[dict]. Handles both array and FeatureCollection.

    If root is a list, return it directly.
    If root is a dict with a 'features' key, delegate to _parse_geojson.
    Otherwise, wrap root in a list.
    """
    data = json.loads(content.decode("utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "features" in data:
        return _parse_geojson(content)
    return [data]
```

### 311 Service Request Tool (ZIP + client-side filter)

```python
# 311 data: no datastore_active — fetch annual ZIP, parse CSV, filter
# Resource pattern: each year is a separate ZIP
# Latest 2026: use package_show to discover current-year resource URL dynamically

async def fetch_311_requests(
    year: int,
    ward: str | None = None,
    service_type: str | None = None,
    status: str | None = None,
    limit: int = 200,
) -> tuple[list[dict], bool]:
    """Fetch 311 service requests for a given year from annual ZIP."""
    # Discover resource URL for the year dynamically via package_show
    dataset, _ = await fetch_dataset_details("311-service-requests-customer-initiated")
    resources = dataset.get("resources", [])
    zip_resource = next(
        (r for r in resources if str(year) in (r.get("name") or "") and r.get("format") == "ZIP"),
        None,
    )
    if not zip_resource:
        raise ValueError(f"No 311 ZIP resource found for year {year}")

    cache_key = f"toronto:311:{year}"
    url = zip_resource["url"]

    async def fetcher() -> list[dict]:
        async with httpx.AsyncClient(timeout=120.0) as http:
            r = await http.get(url)
            r.raise_for_status()
        with zipfile.ZipFile(BytesIO(r.content)) as zf:
            csv_name = next(n for n in zf.namelist() if n.endswith(".csv"))
            with zf.open(csv_name) as f:
                return _parse_csv(f.read(), skip_rows=0)

    rows, cached = await cached_fetch(cache_key, CACHE_TTL_DATA, fetcher)

    # Client-side filters
    if ward:
        rows = [r for r in rows if ward.lower() in str(r.get("ward", "")).lower()]
    if service_type:
        rows = [r for r in rows if service_type.lower() in str(r.get("service_request_type", "")).lower()]
    if status:
        rows = [r for r in rows if status.lower() in str(r.get("status", "")).lower()]

    return rows[:limit], cached
```

---

## Confirmed Dataset IDs and Resource IDs

| Dataset | CKAN Dataset ID | Key Resource ID | Format | datastore_active |
|---------|----------------|-----------------|--------|-----------------|
| TTC Routes and Schedules | `7795b45e-e65a-4465-81fc-c36b9dfff169` | `cfb6b2b8-6191-41e3-bda1-b175c51148cb` | ZIP (GTFS) | No |
| Neighbourhood Profiles 2016 (140-model) | `6e19a90f-971c-46b3-852c-0c48c436d1fc` | `7f8eee5e-85fb-415c-aef3-c3bd4998445f` | CSV | Yes |
| Neighbourhood Profiles 2021 (158-model) | `6e19a90f-971c-46b3-852c-0c48c436d1fc` | `19d4a806-7385-4889-acf2-256f1e079060` | XLSX | No |
| 311 Service Requests (Customer Initiated) | `311-service-requests-customer-initiated` | Annual ZIPs 2010-2026 | ZIP→CSV | No |
| Short Term Rentals Registration | `short-term-rentals-registration` | `f4659cc1-8985-4e4a-a702-ae24352271e0` | CSV | Yes |
| Apartment Building Evaluations (2023+) | `apartment-building-evaluation` | `244f7a02-da5c-425b-b55f-fbdd133dd732` | CSV | Yes |
| Apartment Building Registration | `apartment-building-registration` | `3ad76a8c-0518-4df2-b94e-8c747d62f8c1` | CSV | Yes |
| Capital Budget & Plan By Ward | `capital-budget-and-plan-ward-level-data-10-year-approved` | `745d4ae3-2d64-4bac-8d3f-161f1e68b087` | XLSX | No |
| Operating Budget Summary | `operating-budget-program-summary-by-expenditure-category` | `f9def3c1-a97f-4d31-bc58-c0494d750b80` | XLSX | No |
| Neighbourhoods Boundary | `fc443770-ef0a-4025-9c2c-2cb558bfab00` | GeoJSON available | GeoJSON | No |

---

## Proposed Tool Set (12 tools total)

### Discovery Tools (mirrors Ontario — 5 tools)

| Tool | Description |
|------|-------------|
| `toronto_search_datasets` | Search Toronto open data catalogue by keyword |
| `toronto_get_dataset_details` | Get full metadata + resources for a dataset |
| `toronto_get_resource` | Get details for a specific resource by ID |
| `toronto_list_organizations` | List Toronto divisions/departments publishing data |
| `toronto_get_dataset_stats` | Total dataset count for open.toronto.ca |

### Curated Tools (7 tools)

| Tool | Dataset | Strategy |
|------|---------|----------|
| `toronto_get_ttc_stops` | TTC GTFS | Parse stops.txt from ZIP; filter by query string |
| `toronto_get_ttc_routes` | TTC GTFS | Parse routes.txt from ZIP; filter by route_type |
| `toronto_get_neighbourhood_profile` | Neighbourhood Profiles 2016 | datastore_search on CSV; filter by neighbourhood name |
| `toronto_compare_neighbourhoods` | Neighbourhood Profiles 2016 | datastore_search; filter by Characteristic, return all neighbourhoods |
| `toronto_get_311_requests` | 311 Customer Initiated | Fetch annual ZIP→CSV; client-side filter by year/ward/type |
| `toronto_get_rentsafe_evaluations` | Apartment Building Evaluations | datastore_search; filter by ward, min_score |
| `toronto_get_short_term_rentals` | Short Term Rentals Registration | datastore_search; filter by ward/status |

**Note on budget/building permits:** The Capital Budget and Operating Budget are large XLSX files updated annually — include as discoverable datasets via `toronto_search_datasets` rather than curated tools, unless the planner has capacity. Building permits are best accessed via `toronto_get_dataset_details` then resource download. Scope conservatively to avoid overextension.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Downloading full 311 CSV (million+ rows) | Fetch annual ZIP + client-side filter | Context decision | Manageable memory footprint |
| Using `datastore_search_sql` for all CKAN | Only for `datastore_active=true` resources | Verified Apr 2026 | Avoids 404 errors on non-indexed resources |
| Treating neighbourhood profile as row-per-neighbourhood | Indicator-per-row pivot | Verified Apr 2026 | Correct query pattern |

---

## Open Questions

1. **Building permits scope**
   - What we know: Active permits (232K records), cleared permits (391K records) — both are large. Pool enclosures (3K records) is datastore-active.
   - What's unclear: Whether the planner should include building permits as curated tool or leave for discovery only.
   - Recommendation: Implement `toronto_get_rentsafe_evaluations` + `toronto_get_short_term_rentals` for housing. Building permits via `toronto_search_datasets` discovery — too large for client-side filter.

2. **Neighbourhood profile — 2016 vs 2021**
   - What we know: 2021 XLSX uses 158-neighbourhood model; 2016 CSV uses 140-neighbourhood model and is datastore-active.
   - What's unclear: Whether the 2021 XLSX will be loaded to datastore in future.
   - Recommendation: Implement against 2016 datastore-active resource. Document the 2021 XLSX as a separate resource agents can discover. Note in tool docstring.

3. **311 ZIP disk/memory footprint**
   - What we know: Annual ZIPs — size unknown but likely 5-50 MB each.
   - What's unclear: Cache strategy — cache the parsed rows (potentially 100K+ records) or the raw ZIP bytes.
   - Recommendation: Cache parsed rows with `limit` applied before caching — but this means the cache key must include filter parameters, increasing cache fragmentation. Alternative: cache all rows, apply filters post-cache. Recommend caching all parsed rows per year (full CSV), apply filters in Python.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing) |
| Config file | `pyproject.toml` (existing) |
| Quick run command | `uv run pytest src/mcp_canada/modules/toronto/ -x -v` |
| Full suite command | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TOR-01 | `toronto_search_datasets` returns shaped results | unit | `uv run pytest src/mcp_canada/modules/toronto/__tests__/test_tools.py::TestTorontoDiscovery -x` | Wave 0 |
| TOR-02 | `toronto_get_dataset_details` returns dataset with resources | unit | `uv run pytest src/mcp_canada/modules/toronto/__tests__/test_tools.py::TestTorontoDatasetDetails -x` | Wave 0 |
| TOR-03 | `toronto_get_ttc_stops` parses GTFS ZIP stops.txt | unit | `uv run pytest src/mcp_canada/modules/toronto/__tests__/test_client.py::TestGTFSClient -x` | Wave 0 |
| TOR-04 | `toronto_get_neighbourhood_profile` returns indicator rows for one neighbourhood | unit | `uv run pytest src/mcp_canada/modules/toronto/__tests__/test_tools.py::TestNeighbourhood -x` | Wave 0 |
| TOR-05 | `toronto_compare_neighbourhoods` returns one indicator across all neighbourhoods | unit | `uv run pytest src/mcp_canada/modules/toronto/__tests__/test_tools.py::TestNeighbourhood -x` | Wave 0 |
| TOR-06 | `toronto_get_311_requests` fetches ZIP and filters client-side | unit | `uv run pytest src/mcp_canada/modules/toronto/__tests__/test_client.py::Test311Client -x` | Wave 0 |
| TOR-07 | `toronto_get_rentsafe_evaluations` queries datastore_search | unit | `uv run pytest src/mcp_canada/modules/toronto/__tests__/test_tools.py::TestRentSafe -x` | Wave 0 |
| TOR-08 | `_parse_geojson` extracts properties from FeatureCollection | unit | `uv run pytest src/mcp_canada/shared/__tests__/test_parsers.py::TestGeoJSON -x` | Wave 0 |
| TOR-09 | `_parse_json` handles array and GeoJSON roots | unit | `uv run pytest src/mcp_canada/shared/__tests__/test_parsers.py::TestParseJSON -x` | Wave 0 |
| TOR-10 | All toronto_ tools discoverable via `discover_tools` | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestTorontoToolScenarios::test_toronto_discovery -v -m integration` | Wave 0 |
| TOR-11 | All toronto_ tools have valid Keywords/Use-for docstrings | quality | `uv run pytest src/mcp_canada/shared/__tests__/test_quality.py -x` | Existing |
| TOR-12 | Coverage ≥95% | coverage | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` | Existing |

### Sampling Rate

- **Per task commit:** `uv run pytest src/mcp_canada/modules/toronto/ src/mcp_canada/shared/__tests__/test_parsers.py -x`
- **Per wave merge:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `src/mcp_canada/modules/toronto/__tests__/__init__.py`
- [ ] `src/mcp_canada/modules/toronto/__tests__/conftest.py` — CKAN fixtures, GTFS bytes, datastore records
- [ ] `src/mcp_canada/modules/toronto/__tests__/test_client.py`
- [ ] `src/mcp_canada/modules/toronto/__tests__/test_tools.py`
- [ ] `tests/integration/test_tool_scenarios.py` — append `TestTorontoToolScenarios` class

---

## Sources

### Primary (HIGH confidence)

- Live CKAN API `ckan0.cf.opendata.inter.prod-toronto.ca` — verified dataset IDs, resource IDs, `datastore_active` flags, column names
- `src/mcp_canada/modules/ontario/client.py` — established CKAN client pattern to mirror
- `src/mcp_canada/shared/parsers.py` — existing parser for CSV/XLSX; extension points for GeoJSON/JSON
- Python stdlib `zipfile` docs — GTFS ZIP parsing pattern

### Secondary (MEDIUM confidence)

- [GitHub: open-data-toronto/ckan-customization-open-data-toronto](https://github.com/open-data-toronto/ckan-customization-open-data-toronto) — Toronto custom plugins (`extendedapi`, `updateschema`, `datastore_cache` semantics)
- CKAN 2.9 API docs — `datastore_search`, `datastore_search_sql`, `package_search` action signatures

### Tertiary (LOW confidence)

- WebSearch results on Toronto GTFS parsing — confirms stdlib `zipfile` + `csv` is standard approach; no third-party dep needed

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libs already in project; no new deps
- Architecture: HIGH — Ontario module is direct template; verified live
- Dataset IDs and resource IDs: HIGH — verified via live API calls
- Pitfalls (311 SQL, GTFS size, neighbourhood layout): HIGH — verified via live API inspection
- Budget dataset structure: MEDIUM — XLSX structure not inspected, only metadata confirmed

**Research date:** 2026-04-09
**Valid until:** 2026-05-09 (stable CKAN; dataset IDs confirmed stable; GTFS updates ~6 weeks)
