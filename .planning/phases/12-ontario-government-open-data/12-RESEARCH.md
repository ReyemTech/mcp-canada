# Phase 12: Ontario Government Open Data - Research

**Researched:** 2026-04-08
**Domain:** CKAN open data portal, provincial government data, CSV/XLSX parsers
**Confidence:** HIGH

## Summary

Ontario's open data portal (`data.ontario.ca`) is a standard CKAN 2.8 instance with 2,946 datasets from 20+ ministry organizations. It exposes the same CKAN Action API v3 that the project already uses for the federal `open.canada.ca` portal — meaning the existing `ckan` module's client patterns, cache strategy, and response shaping are directly reusable with a URL swap.

The portal requires no authentication for read operations. The CKAN Datastore extension is enabled and some CSV resources are queryable via `datastore_search`. However, the majority of high-value datasets (education enrollment, population projections, energy, transportation) are published as XLSX/CSV file downloads with `datastore_active: false`, making them suitable for `fetch_and_parse()` from `shared/parsers.py`.

The primary implementation decision is toolset scope: this phase should deliver (1) a CKAN discovery/search layer mirroring the federal `ckan` module but pointed at `data.ontario.ca`, and (2) a small set of curated high-value data tools that parse specific Ontario datasets. Given 2,946 datasets across domains, tool selection should prioritize datasets that are: actively updated, CSV/XLSX format (parseable), and have no access restrictions.

**Primary recommendation:** Implement `ontario_` prefixed tools using the existing CKAN client pattern for discovery + `fetch_and_parse()` from `shared/parsers.py` for dataset-specific tools. No new dependencies required.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `fastmcp.tools.tool` | 3.2.x | Standalone @tool decorator | Required by FileSystemProvider |
| `httpx` | existing | Async HTTP to CKAN API | Already in stack; CKAN API is plain HTTP |
| `pydantic` | v2 | Schema validation | Already in stack |
| `aiocache` | existing | TTL cache via `cached_fetch()` | Already in stack |

### Supporting (already in `shared/`)
| Utility | Location | Purpose | When to Use |
|---------|----------|---------|-------------|
| `fetch_and_parse()` | `shared/parsers.py` | Fetch + parse XLSX/CSV from URL | Any Ontario dataset download URL |
| `cached_fetch()` | `shared/cache.py` | Cache any coroutine result | All client functions |
| `get_limiter()` | `shared/rate_limiter.py` | Per-source TokenBucket | All HTTP calls |
| `make_response()` | `shared/envelope.py` | Success envelope | All tool returns |
| `make_error()` | `shared/envelope.py` | Error envelope | All error paths |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Reusing ckan module pattern | Custom REST client | The federal ckan module already solves this problem; reuse is correct |
| `fetch_and_parse()` for XLSX | CKAN Datastore API | Datastore is enabled on only a minority of resources; XLSX fetch is universal |
| Module prefix `on_` | `ontario_` | `ontario_` is unambiguous and matches the naming convention of the roadmap; `on_` could be confused with "on/off" |

**Installation:** No new packages needed. All required libraries are in the existing stack.

## Architecture Patterns

### Recommended Project Structure
```
src/mcp_canada/modules/ontario/
├── __init__.py          # MODULE_NAME = "ontario", MODULE_DESCRIPTION
├── constants.py         # BASE_URL, RATE_GROUP, RATE_LIMIT, CACHE_TTLs, DATASET_REGISTRY
├── schemas.py           # Pydantic models for shaped responses (flat)
├── client.py            # Async functions returning (data, was_cached) tuples
├── tools.py             # @tool functions with ontario_ prefix
└── __tests__/
    ├── conftest.py      # Sample API response fixtures
    ├── test_client.py   # Unit tests with mocked HTTP
    └── test_tools.py    # Unit tests with mocked client functions
```

### Pattern 1: CKAN Discovery Layer (reuse federal CKAN pattern)
**What:** Identical to the `ckan` module client, pointing to `https://data.ontario.ca/api/3/`
**When to use:** For all portal-level tools (search, dataset details, resource info)
**Example:**
```python
# constants.py
BASE_URL = "https://data.ontario.ca/api/3/"
RATE_GROUP = "ontario"
RATE_LIMIT = 10.0  # Conservative; no published limit

# client.py — same _api_get() pattern as ckan module
async def _api_get(path: str, params: dict, cache_ttl: int) -> tuple[Any, bool]:
    url = BASE_URL + path
    cache_key = f"ontario:{path}?{sorted_params}"
    limiter = get_limiter(RATE_GROUP, rate=RATE_LIMIT)
    async def fetcher():
        await limiter.acquire()
        async with httpx.AsyncClient(timeout=30.0) as http:
            r = await http.get(url, params=params)
            r.raise_for_status()
            return r.json()["result"]
    return await cached_fetch(cache_key, cache_ttl, fetcher)
```

### Pattern 2: Dataset-Specific CSV/XLSX Tool
**What:** Curated tools that fetch a known Ontario dataset URL and parse it via `fetch_and_parse()`
**When to use:** For high-value datasets where the download URL is stable and the data schema is known
**Example:**
```python
# client.py
POPULATION_PROJECTIONS_URL = (
    "https://data.ontario.ca/dataset/f52a6457-fb37-4267-acde-11a1e57c4dc8"
    "/resource/31376797-1e4c-4426-ba75-0d93f4bb9f45/download/"
    "ontario_mof_population_projections_for_2024-2051.xlsx"
)

async def fetch_population_projections(lang: str = "en") -> tuple[list[dict], bool]:
    url = POPULATION_PROJECTIONS_URL if lang == "en" else POPULATION_PROJECTIONS_URL_FR
    return await fetch_and_parse(url, sheet=0, skip_rows=0, ttl=CACHE_TTL_DATA)
```

### Pattern 3: CKAN Datastore Query (for datastore_active resources)
**What:** Direct structured query to `datastore_search` action for resources with `datastore_active: true`
**When to use:** Only when a resource explicitly has `datastore_active: true` — verified at implementation time
**Example:**
```python
async def fetch_datastore_resource(resource_id: str, q: str | None = None, limit: int = 100) -> tuple[list[dict], bool]:
    params = {"resource_id": resource_id, "limit": limit}
    if q:
        params["q"] = q
    result, cached = await _api_get("action/datastore_search", params, CACHE_TTL_SEARCH)
    return result.get("records", []), cached
```

### Ontario CKAN Response Differences from Federal CKAN

The Ontario portal uses the same CKAN envelope (`{"success": true, "result": ...}`) but has these differences:

| Feature | Federal (open.canada.ca) | Ontario (data.ontario.ca) |
|---------|--------------------------|--------------------------|
| Bilingual field suffix | `_translated` | `_translated` (same) |
| Datastore | Not commonly used in existing module | Some CSV resources have `datastore_active: true` |
| Organizations | `owner_org` | `owner_org` (same) |
| Extra fields | `access_level`, `exemption` | `access_level`, `exemption` (similar pattern) |
| Groups | Thematic | Only "covid-19" group (sparse grouping) |
| Resource URL pattern | Stable direct links | Stable direct download links |
| Language support | EN/FR | EN/FR |

The `_shape_dataset()` function from the federal CKAN module can be reused as-is or adapted for Ontario.

### Anti-Patterns to Avoid
- **Do not hardcode dataset resource IDs without a corresponding dataset ID:** Resource IDs can be recreated on portal reindexing; always keep the parent dataset ID for recovery.
- **Do not use `datastore_search` without checking `datastore_active` first:** Most Ontario resources are not in the Datastore; fetching via the datastore endpoint returns a 404.
- **Do not fetch multi-sheet XLSX without specifying the sheet:** Ontario education XLSX files have multiple sheets; always specify `sheet=0` or the correct sheet name.
- **Do not attempt to parse ZIP resources:** Vehicle population and energy data are distributed as ZIP archives — these exceed reasonable MCP context budget and should be documented as out of scope for tool consumption.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| XLSX parsing | Custom openpyxl loop | `shared/parsers.fetch_and_parse()` | Already handles BOM, pandas fallback, snake_case keys, privacy masking |
| CSV parsing | `csv.DictReader` in tools.py | `shared/parsers.fetch_and_parse()` | Same parser handles both |
| HTTP caching | `functools.lru_cache` | `shared/cache.cached_fetch()` | Async-safe TTL cache already in stack |
| Rate limiting | `asyncio.sleep()` | `shared/rate_limiter.get_limiter()` | TokenBucket already in stack |
| Response envelope | Custom dict | `shared/envelope.make_response()` | Required by BM25 discovery layer |
| CKAN API client | Separate httpx calls per tool | `_api_get()` helper in `ontario/client.py` | Same pattern as federal ckan module |

**Key insight:** The entire Ontario module is an adaptation of existing patterns. No new abstractions should be introduced. New code is only: a `constants.py` with Ontario-specific URLs and TTLs, and `tools.py` with Ontario-specific tool signatures and dataset selection.

## Common Pitfalls

### Pitfall 1: Datastore False Positive
**What goes wrong:** Calling `datastore_search` on a resource that has `datastore_active: false` returns HTTP 404 or an error JSON.
**Why it happens:** CKAN Datastore must be explicitly enabled per resource; most Ontario resources are file downloads only.
**How to avoid:** Check `datastore_active` in the resource metadata before implementing a datastore tool. All curated dataset tools in this phase should verify their resource's `datastore_active` status during implementation.
**Warning signs:** 404 from `datastore_search` action; `"success": false` in response.

### Pitfall 2: XLSX Multi-Sheet without Sheet Specification
**What goes wrong:** `fetch_and_parse()` defaults to `sheet=0` which may not be the data sheet for multi-sheet Ontario XLSX files.
**Why it happens:** Ontario education and population XLSX files often have a "Notes" or "Metadata" tab as the first sheet.
**How to avoid:** Always inspect the actual XLSX file before hardcoding sheet index. Use the sheet name (string) rather than index when possible.
**Warning signs:** Parsed data has only metadata rows; columns look like "note", "source", "date modified".

### Pitfall 3: Restricted Dataset Resource Count
**What goes wrong:** A dataset appears in search results with `num_resources > 0` but no actual downloadable files.
**Why it happens:** Ontario marks some datasets as `access_level: restricted` due to privacy; the portal entry exists but resources are withheld.
**How to avoid:** During curated tool selection, fetch the `package_show` response and verify `resources[0].url` is a real downloadable URL. The wait times datasets (hospital, Cancer Care Ontario) are restricted.
**Warning signs:** `resources` array empty; `access_level: restricted` in dataset metadata.

### Pitfall 4: Bilingual URL Selection
**What goes wrong:** French XLSX download URL is used for the `lang="en"` path (or vice versa).
**Why it happens:** Ontario datasets often have parallel EN/FR resources with similar filenames differing only by language prefix.
**How to avoid:** Build a DATASET_REGISTRY-style dict (as in the IRCC module) mapping `lang -> url` for each curated dataset. Never use string manipulation to toggle language in URLs.
**Warning signs:** French column headers in English response; `_normalize_key()` output differs from expected column names.

### Pitfall 5: ZIPped Resources
**What goes wrong:** Fetching vehicle population or energy datasets returns a ZIP file, not CSV/XLSX.
**Why it happens:** Large annual datasets are compressed for download efficiency.
**How to avoid:** Identify ZIP resources during dataset selection and exclude them from curated tool scope. Note in the tool docstring that raw downloads are available at the portal URL.
**Warning signs:** `content-type: application/zip`; `fetch_and_parse()` raises parse error since URL ends in `.zip`.

### Pitfall 6: Rate Limiting Without Published Limits
**What goes wrong:** Sending many requests quickly could trigger IP-based throttling from Ontario's government hosting.
**Why it happens:** No published rate limit means the server's limit is unknown.
**How to avoid:** Set `RATE_LIMIT = 10.0` (req/s) — same as the federal CKAN module — as a safe conservative default. Never burst above 10 req/s.

## Code Examples

Verified patterns from official sources:

### CKAN Package Search (Ontario)
```python
# Source: data.ontario.ca/api/3/action/package_search — verified live
# Standard CKAN envelope response
GET https://data.ontario.ca/api/3/action/package_search?q=population&rows=5

# Response:
{
  "success": true,
  "result": {
    "count": 96,
    "results": [
      {
        "id": "f52a6457-fb37-4267-acde-11a1e57c4dc8",
        "name": "population-projections",
        "title": "Population projections",
        "access_level": "open",
        "organization": {"name": "finance", "title": "Finance"},
        "num_resources": 12,
        "resources": [...],
        "metadata_modified": "2025-08-01T..."
      }
    ]
  }
}
```

### CKAN Datastore Search (for datastore_active resources only)
```python
# Source: data.ontario.ca/api/3/action/datastore_search — verified live
GET https://data.ontario.ca/api/3/action/datastore_search?resource_id=68afb214-...&limit=2

# Response (for WAH training providers CSV — datastore_active: true):
{
  "success": true,
  "result": {
    "total": 23,
    "fields": [
      {"id": "Provider", "type": "text"},
      {"id": "Website", "type": "text"},
      {"id": "Date approved", "type": "date"},
      {"id": "Program name", "type": "text"}
    ],
    "records": [
      {"Provider": "2840950 ONTARIO LIMITED", "Date approved": "2025-08-18", ...}
    ]
  }
}
```

### Fetch and Parse XLSX (Ontario population data)
```python
# Source: shared/parsers.py fetch_and_parse() — existing pattern
from mcp_canada.shared.parsers import fetch_and_parse

rows, was_cached = await fetch_and_parse(
    url="https://data.ontario.ca/dataset/f52a6457-.../download/ontario_mof_population_projections_for_2024-2051.xlsx",
    sheet=0,
    skip_rows=0,
    ttl=86400,  # 24 hours
)
# Returns: ([{"geography": "Ontario", "year": 2024, "population": ...}, ...], bool)
```

### Tool Function Skeleton (Ontario pattern)
```python
# Source: project conventions in CLAUDE.md + existing ckan/tools.py pattern
from fastmcp.tools import tool
from typing import Literal
from mcp_canada.shared.envelope import make_response, make_error

@tool
async def ontario_search_datasets(
    query: str,
    rows: int = 10,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search Ontario's Open Data Catalogue for provincial government datasets.

    Use for: finding Ontario provincial government datasets on health, education,
    population, transportation, environment, and other provincial topics.
    Keywords: ontario, provincial, open data, search, dataset, catalogue,
    government, ministry, health, education, population, housing, transit.
    """
    try:
        datasets, cached = await fetch_ontario_datasets(query=query, rows=rows, lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error("UPSTREAM_ERROR", f"Ontario data portal returned HTTP {exc.response.status_code}.", lang=lang)
    return make_response(datasets, api_name="Ontario Data Catalogue", api_url="https://data.ontario.ca", cached=cached, lang=lang)
```

## High-Value Curated Dataset Candidates

Based on live API research, these Ontario datasets are: open access, actively updated, and parseable via XLSX/CSV:

| Dataset | Organization | Format | Update Frequency | Resource ID (EN) |
|---------|-------------|--------|-----------------|-----------------|
| Population Projections (2024-2051) | Finance | XLSX | Annual (Aug 2025) | 31376797-1e4c-4426-ba75-0d93f4bb9f45 |
| School Enrolment by Grade | Education | XLSX/TXT | Annual | (see notes) |
| Licensed Child Care Facilities | Education | XLSX | Monthly | (see notes) |
| School Board Contact Info | Education | CSV | Monthly | (datastore_active: true) |
| Government-approved driving schools | Transportation | CSV | As required | (see notes) |
| Approved Working at Heights Providers | Labour | CSV | Monthly | 6ebd3e44-cfcf-467b-9437-6bfd10dcad2e |

**Note:** Resource IDs for education datasets should be re-fetched at implementation time via `package_show` as they rotate with each annual upload.

**Dataset design recommendation:** For Phase 12, implement curated tools for population projections (XLSX download) plus CKAN discovery tools. Education and child care tools may be added if time permits. Hospital wait times, vehicle population (ZIP), and energy (ZIP) are out of scope.

## Module Naming and Discovery

### Module Prefix
Use `ontario_` prefix for all tool names: `ontario_search_datasets`, `ontario_get_dataset`, `ontario_get_population_projections`, etc.

**Rationale:** Phases 13-17 will add `toronto_`, `york_`, `bc_`, `qc_`, `ab_` modules. The provincial prefix ensures BM25 disambiguation when an agent asks "find Ontario health data" vs "find BC health data."

### MODULE_DESCRIPTION Strategy
```python
MODULE_DESCRIPTION = (
    "Ontario provincial government open data tools: search 2,946 datasets from "
    "Ontario ministries (Health, Education, Finance, Agriculture, Transportation, "
    "Environment), retrieve dataset details and resources, and fetch curated datasets "
    "including population projections, school enrollment, and child care facility lists. "
    "All data under Open Government Licence – Ontario."
)
```

### How Ontario Differs from Federal CKAN Module
| Aspect | Federal (ckan_) | Ontario (ontario_) |
|--------|-----------------|-------------------|
| Base URL | `https://open.canada.ca/data/en/api/3/` | `https://data.ontario.ca/api/3/` |
| Dataset count | 80,000+ | 2,946 |
| Thematic groups | Extensive | Only "covid-19" |
| Organizations | Federal departments | Ontario ministries |
| Datastore use | Rarely checked | Some CSV resources active |
| Curated tools | None in ckan module | Population, enrollment, child care |
| Bilingual | EN/FR via `_translated` | EN/FR via `_translated` (same) |
| License | Open Government Licence Canada | Open Government Licence – Ontario |

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Separate HTTP clients per endpoint | `_api_get()` shared helper | Phase 2 (ckan module) | Use same pattern |
| Module-specific parsers | `shared/parsers.fetch_and_parse()` | Phase 11 (IRCC) | Reuse directly |
| IRCC-specific XLSX parsing config | `ircc_parse_config` parameter (optional) | Phase 11 | Standard XLSX without merged headers uses default `fetch_and_parse()` |

**Not deprecated:** All patterns from the `ckan` module remain valid and should be replicated for Ontario.

## Open Questions

1. **Population XLSX internal sheet structure**
   - What we know: Resource URL is a 244KB XLSX with `sheet=0`, published by Ministry of Finance
   - What's unclear: Whether sheet 0 is the data sheet or a "Notes" sheet; exact column names
   - Recommendation: Fetch the file during Wave 0 (setup) and inspect columns before writing the tool; document the sheet index in constants.py

2. **Datastore rate limiting**
   - What we know: No published rate limit for Ontario's CKAN Datastore API
   - What's unclear: Whether aggressive datastore queries could trigger WAF throttling
   - Recommendation: Apply same 10 req/s TokenBucket as CKAN search; monitor during integration testing

3. **Education enrollment XLSX multi-sheet layout**
   - What we know: Education XLSX files have parallel EN/FR resources; `datastore_active: false`; resource IDs rotate annually
   - What's unclear: Whether the XLSX uses merged headers (requiring `ircc_parse_config`) or flat single-row headers
   - Recommendation: Inspect the actual XLSX during Wave 0; use standard `fetch_and_parse()` if headers are flat, or `ircc_parse_config` if merged

4. **Tool count budget for Phase 12**
   - What we know: The phase description says "first provincial-level data source" with curated dataset scope TBD
   - What's unclear: Whether Phase 12 should be CKAN discovery only (5-7 tools mirroring federal ckan) or include curated dataset tools (adds 2-4 more)
   - Recommendation: Implement 5-6 CKAN discovery tools + 1-2 curated dataset tools (population projections); keep it focused. Additional curated tools can be Wave 2 if time permits.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (uv run pytest) |
| Config file | pyproject.toml |
| Quick run command | `uv run pytest src/mcp_canada/modules/ontario/__tests__/ -x -v` |
| Full suite command | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |

### Phase Requirements → Test Map

No formal requirement IDs assigned yet (TBD in REQUIREMENTS.md). Based on phase description, anticipated requirements:

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ONT-01 | CKAN search returns shaped datasets | unit | `uv run pytest src/mcp_canada/modules/ontario/__tests__/test_tools.py::TestOntarioSearchDatasets -x` | Wave 0 |
| ONT-02 | CKAN package_show returns dataset details | unit | `uv run pytest src/mcp_canada/modules/ontario/__tests__/test_tools.py::TestOntarioGetDataset -x` | Wave 0 |
| ONT-03 | CKAN resource_show returns resource details | unit | `uv run pytest src/mcp_canada/modules/ontario/__tests__/test_tools.py::TestOntarioGetResource -x` | Wave 0 |
| ONT-04 | Population projections XLSX parsed and returned | unit | `uv run pytest src/mcp_canada/modules/ontario/__tests__/test_tools.py::TestOntarioGetPopulation -x` | Wave 0 |
| ONT-05 | All tools return _meta envelope on success | unit | `uv run pytest src/mcp_canada/modules/ontario/__tests__/test_tools.py -k "meta" -x` | Wave 0 |
| ONT-06 | All tools return error envelope on HTTP error | unit | `uv run pytest src/mcp_canada/modules/ontario/__tests__/test_tools.py -k "error" -x` | Wave 0 |
| ONT-07 | discover_tools finds ontario tools by keyword | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestOntarioDiscovery -x -m integration` | Wave 0 |
| ONT-08 | Live CKAN search returns real data | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestOntarioLive -x -m integration` | Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest src/mcp_canada/modules/ontario/__tests__/ -x`
- **Per wave merge:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `src/mcp_canada/modules/ontario/__tests__/conftest.py` — sample CKAN API response fixtures
- [ ] `src/mcp_canada/modules/ontario/__tests__/test_client.py` — client unit tests
- [ ] `src/mcp_canada/modules/ontario/__tests__/test_tools.py` — tool unit tests
- [ ] `tests/integration/test_tool_scenarios.py` — integration scenarios for Ontario tools (may already exist; add new class)
- [ ] Inspect population projections XLSX file to confirm sheet 0 is the data sheet and document columns in constants.py

## Sources

### Primary (HIGH confidence)
- Live API: `https://data.ontario.ca/api/3/action/package_search` — verified 2,946 datasets, response structure, bilingual fields
- Live API: `https://data.ontario.ca/api/3/action/organization_list` — verified 20 organizations and dataset counts
- Live API: `https://data.ontario.ca/api/3/action/datastore_search` — verified Datastore is enabled for some CSV resources (WAH providers: 23 records confirmed)
- Live API: `https://data.ontario.ca/api/3/action/package_show` — verified full resource metadata including `datastore_active` flags
- `data.ontario.ca/about` — confirmed CKAN 2.8, Datastore API requirements (server-side only), no authentication for reads
- `ontario.ca/page/open-government-licence-ontario` — Open Government Licence – Ontario v1.0, free reuse with attribution

### Secondary (MEDIUM confidence)
- Project codebase (`src/mcp_canada/modules/ckan/`) — existing federal CKAN module confirms the client pattern is directly reusable
- Project codebase (`src/mcp_canada/shared/parsers.py`) — `fetch_and_parse()` confirmed to handle XLSX and CSV without new code

### Tertiary (LOW confidence)
- WebSearch results on Ontario open data value datasets — dataset names and descriptions verified via live API; rankings are subjective

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — entire stack reused from existing modules; verified by codebase inspection
- Architecture: HIGH — identical to ckan module pattern, verified against live Ontario CKAN API
- Pitfalls: HIGH — datastore_active confirmed via live API calls; ZIP format confirmed; restricted datasets confirmed
- Curated dataset selection: MEDIUM — resource IDs verified at research time; may rotate on next annual publish

**Research date:** 2026-04-08
**Valid until:** 2026-05-08 (30 days; CKAN APIs are stable; resource IDs for education may rotate on next school year release)
