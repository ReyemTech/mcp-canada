# Phase 8: StatCan WDS - Research

**Researched:** 2026-04-07
**Domain:** Statistics Canada WDS REST API — endpoints, response shapes, caching, BM25 search, coordinate padding
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- BM25/TF-IDF ranking for cube search over cached getAllCubesListLite results
- Search fields: `cubeTitleEn`, `cubeTitleFr`, `subjectCode`, `surveyCode` — not footnotes
- Default result limit: top 10; agent may pass `limit` param
- Cube list loaded lazily on first search, cached 1hr via existing `cached_fetch()`
- Full flatten: strip `{"status", "object"}` envelope, extract data, convert string numbers to floats
- Code IDs: include both code AND decoded label (e.g. `{"frequency_code": 6, "frequency": "Monthly"}`)
- Coordinate auto-padding: agent passes `"1.1"`, client pads to 10 dimensions (`"1.1.0.0.0.0.0.0.0.0"`)
- All tools return `make_response()` / `make_error()` envelopes
- Prefix: `sc_` for all tool names
- Descriptive names: `sc_search_cubes`, `sc_get_cube_metadata`, `sc_get_data_by_vector`, `sc_get_changed_series`, etc.
- All tools standalone `@tool` with `lang: Literal["en", "fr"]`, `Use for:` + `Keywords:` docstrings
- Reuse: `_make_statcan_client()`, `cached_fetch()`, `get_limiter()`, `BASE_URL`, `RATE_GROUP`, `RATE_LIMIT` from Phase 7

### Claude's Discretion
- Exact BM25 implementation approach (stdlib only — `math.log` + `collections.Counter`)
- Whether to split `client.py` into `wds_client.py` (single file fine if manageable)
- Pydantic schema design for flattened responses
- Error code mappings for StatCan's `responseStatusCode` values
- How to handle the WDS maintenance window (00:00–08:30 EST) — 409 responses

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SC-01 | Agent can search Statistics Canada tables by keyword (client-side BM25 on cached cube list) | getAllCubesListLite fields documented; BM25 stdlib implementation specified |
| SC-02 | Agent can retrieve detailed metadata for a specific table by productId | getCubeMetadata POST endpoint, response shape fully documented |
| SC-03 | Agent can decode numeric codes (frequency, units, scalar factor, status) | getCodeSets GET endpoint documented; all code tables in Constants section |
| SC-04 | Agent can look up series metadata by vectorId | getSeriesInfoFromVector POST documented |
| SC-05 | Agent can look up series metadata by productId + coordinate | getSeriesInfoFromCubePidCoord POST documented; coordinate padding required |
| SC-06 | Agent can retrieve latest N observations for a given vectorId | getDataFromVectorsAndLatestNPeriods POST documented |
| SC-07 | Agent can retrieve latest N observations by productId + coordinate | getDataFromCubePidCoordAndLatestNPeriods POST documented |
| SC-08 | Agent can retrieve data for a vector within a reference period date range | getDataFromVectorByReferencePeriodRange GET documented |
| SC-09 | Agent can retrieve data for multiple vectors within a release date range | getBulkVectorDataByRange POST documented |
| SC-13 | Agent can list series that changed today | getChangedSeriesList GET documented |
| SC-14 | Agent can list cubes that changed on a specific date | getChangedCubeList/{date} GET documented |
| INF-02 | StatCan API calls rate-limited to 20 req/s via shared TokenBucket | `get_limiter("statcan", rate=20.0)` — RATE_GROUP/RATE_LIMIT already in constants.py |
| INF-03 | Tiered TTLs: cube list 1hr, metadata 24hr, code sets 7d, observations 1hr | TTL constants to add to constants.py; `cached_fetch()` already works |
| INF-04 | All StatCan tools support bilingual responses (lang: en/fr) | `lang` param pattern established in all existing modules |
| INF-05 | All tools follow mcp-canada conventions | 5-file module pattern, @tool, make_response/make_error, Keywords/Use-for |
</phase_requirements>

---

## Summary

Phase 8 builds the full Statistics Canada WDS module on top of the stub created in Phase 7. The module needs 11 client functions and 11 tools — all following the existing 5-file module pattern. The Phase 7 stub provides `_make_statcan_client()`, `BASE_URL`, `RATE_GROUP`, `RATE_LIMIT`, and `STATCAN_VERIFY=True`; Phase 8 consumes all of these.

The StatCan WDS REST API uses HTTP POST for most write-style queries (even reads) and HTTP GET for catalog/monitoring endpoints. All responses share an `{"status": "SUCCESS|FAILED", "object": ...}` envelope that must be unwrapped before consuming data. The most important implementation risk is the `FAILED` status arriving with HTTP 200 — every client function must check `status == "SUCCESS"` before accessing `object`.

BM25 cube search can be implemented with only `math.log` and `collections.Counter` from stdlib — no new dependencies. The reference implementation (mcp-statcan) uses AND-logic substring matching without ranking; our implementation supersedes this with proper BM25 scoring over title (en+fr), subjectCode, and surveyCode fields.

**Primary recommendation:** Implement 11 client functions in `statcan/client.py` expanded from the factory stub, plus matching tools in `statcan/tools.py`, with `statcan/schemas.py` (new) for flat Pydantic models. Add cache TTL constants and code-set mappings to `statcan/constants.py`.

---

## Standard Stack

### Core (already in project — no new installs)

| Library | Version | Purpose | Notes |
|---------|---------|---------|-------|
| `httpx` | transitive | Async HTTP to WDS REST | Use `_make_statcan_client()` factory |
| `pydantic` | v2 | Flat response schemas | `BaseModel`, `model_dump()` |
| `aiocache` | — | TTL cache via `cached_fetch()` | Already in `shared/cache.py` |
| `math` (stdlib) | — | BM25 `log()` for IDF | No new dep needed |
| `collections` (stdlib) | — | `Counter` for term frequency | No new dep needed |
| `difflib` (stdlib) | — | `get_close_matches()` for suggestions | Already used in BoC module |

### No New Dependencies
The dependency policy prohibits additions. The full BM25 implementation fits in ~40 lines using `math.log` and `collections.Counter`.

**Installation:** Nothing to install — all dependencies are already in the project.

---

## Architecture Patterns

### Recommended File Changes

```
src/mcp_canada/modules/statcan/
├── __init__.py           # Update MODULE_DESCRIPTION
├── constants.py          # ADD: cache TTLs, code-set dicts, endpoint path constants
├── schemas.py            # CREATE NEW: flat Pydantic models for all WDS responses
├── client.py             # EXPAND: 11 async client functions + BM25 search helper
├── tools.py              # CREATE NEW: 11 sc_ @tool functions
└── __tests__/
    ├── conftest.py       # CREATE NEW: shared WDS response fixtures
    ├── test_client.py    # CREATE NEW: unit tests for all client functions
    └── test_tools.py     # CREATE NEW: unit tests for all tool functions
```

### Pattern 1: Client Function with Cached POST

Every WDS POST client function follows this shape:

```python
# Source: existing BoC module pattern adapted for StatCan
async def get_cube_metadata(product_id: int) -> tuple[CubeMetadata, bool]:
    cache_key = f"statcan_wds:getCubeMetadata:{product_id}"
    limiter = get_limiter(RATE_GROUP, rate=RATE_LIMIT)

    async def fetcher() -> Any:
        await limiter.acquire()
        async with _make_statcan_client() as http:
            resp = await http.post(
                BASE_URL + "getCubeMetadata",
                json=[{"productId": product_id}],
            )
            resp.raise_for_status()
            raw = resp.json()
        # WDS wraps single-item POSTs in a list
        item = raw[0] if isinstance(raw, list) else raw
        if item.get("status") != "SUCCESS":
            raise ValueError(f"WDS FAILED: {item.get('object')}")
        return item["object"]

    data, was_cached = await cached_fetch(cache_key, CACHE_TTL_META, fetcher)
    return _flatten_cube_metadata(data), was_cached
```

### Pattern 2: Coordinate Auto-Padding

```python
# Source: adapted from mcp-statcan src/util/coordinate.py
_COORD_DIMS = 10

def pad_coordinate(coord: str) -> str:
    """Pad a WDS coordinate string to exactly 10 dot-separated dimensions.

    Examples:
        "1.3.1"       -> "1.3.1.0.0.0.0.0.0.0"
        "1.3.1.2.0"   -> "1.3.1.2.0.0.0.0.0.0"
        "1.3.1.2.0.0.0.0.0.0" -> unchanged
    """
    parts = coord.split(".")
    while len(parts) < _COORD_DIMS:
        parts.append("0")
    return ".".join(parts[:_COORD_DIMS])
```

Apply `pad_coordinate()` to every `coordinate` parameter before including it in a WDS request body.

### Pattern 3: Response Envelope Unwrapping

```python
def _unwrap(raw: Any) -> Any:
    """Unwrap a single WDS status/object envelope."""
    if isinstance(raw, list):
        raw = raw[0]
    if raw.get("status") != "SUCCESS":
        raise ValueError(f"WDS FAILED: {raw.get('object')}")
    return raw["object"]
```

For list-returning POSTs (e.g. `getDataFromVectorsAndLatestNPeriods` with multiple vectors), iterate and collect per-item status. Partial failures go in a `_meta.warnings` list — do not silently drop them.

### Pattern 4: BM25 Cube Search (stdlib only)

```python
# Source: BM25 formula from https://en.wikipedia.org/wiki/Okapi_BM25
# Implementation: math.log + collections.Counter, no external deps
from collections import Counter
from math import log

_K1 = 1.2
_B = 0.75

def _bm25_score(query_terms: list[str], doc_tokens: list[str],
                avg_dl: float, N: int, df: dict[str, int]) -> float:
    tf = Counter(doc_tokens)
    dl = len(doc_tokens)
    score = 0.0
    for term in query_terms:
        f = tf.get(term, 0)
        if f == 0:
            continue
        n = df.get(term, 0)
        idf = log((N - n + 0.5) / (n + 0.5) + 1)
        norm = 1 - _B + _B * (dl / avg_dl)
        score += idf * ((f * (_K1 + 1)) / (f + _K1 * norm))
    return score

def _build_doc_tokens(cube: dict) -> list[str]:
    """Tokenize a cube entry for BM25 scoring."""
    text = " ".join([
        cube.get("cubeTitleEn", ""),
        cube.get("cubeTitleFr", ""),
        " ".join(cube.get("subjectCode", [])),
        " ".join(cube.get("surveyCode", [])),
    ]).lower()
    return text.split()
```

Pre-compute `avg_dl` and per-term `df` over the full cube list once after loading, store alongside the cube list in the cache value.

### Pattern 5: Code Set Decoding (inline dict, no live fetch on hot path)

Code sets are loaded once via `getCodeSets` on first use, cached with a 7-day TTL (`CACHE_TTL_CODESETS = 604800`). Frequency and scalar factor codes are also hardcoded in `constants.py` as a fallback since they rarely change.

```python
# constants.py additions
FREQUENCY_CODES: dict[int, str] = {
    1: "Daily", 2: "Weekly", 4: "Biweekly", 6: "Monthly",
    7: "Bimonthly", 9: "Quarterly", 11: "Semi-annual", 12: "Annual",
    13: "Every 2 years",
}

SCALAR_FACTOR_CODES: dict[int, str] = {
    0: "units", 1: "tens", 2: "hundreds", 3: "thousands",
    4: "ten thousands", 5: "hundred thousands", 6: "millions",
    7: "ten millions", 8: "hundred millions", 9: "billions",
    888: "null",
}
```

### Anti-Patterns to Avoid

- **Check HTTP 200 = success:** WDS returns HTTP 200 for application-level failures. Always check `status == "SUCCESS"` before accessing `object`.
- **Skip coordinate padding:** Never pass a raw user coordinate to WDS. Always call `pad_coordinate()` first.
- **Direct getAllCubesList fetch:** Use `getAllCubesListLite` for search/catalog. `getAllCubesList` returns dimension details that overflow context.
- **Module-level client instance:** Do not create a single `httpx.AsyncClient` at module level. Use `_make_statcan_client()` as a context manager per request (or use `async with` in fetcher closures).
- **Cache key without full context:** Never cache only `productId` — include endpoint name and all parameters: `statcan_wds:getDataFromVectorsAndLatestNPeriods:74804:10`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| TTL caching | Custom dict + timestamps | `cached_fetch(key, ttl, fetcher)` | Already exists in `shared/cache.py`; handles race conditions |
| Rate limiting | `asyncio.sleep()` calls | `get_limiter(RATE_GROUP, rate=RATE_LIMIT)` | TokenBucket already in `shared/rate_limiter.py` |
| Response envelope | Custom dict wrapper | `make_response()` / `make_error()` | Enforced by `test_quality.py`; agents depend on `_meta` |
| SSL scoping | New httpx client config | `_make_statcan_client()` | Phase 7 already resolved certifi; don't touch shared clients |
| Fuzzy suggestions | Edit distance logic | `difflib.get_close_matches()` | stdlib; pattern established in BoC module |

**Key insight:** Every shared utility already exists. Phase 8 adds only StatCan-specific logic (endpoint calls, flattening, BM25) — all infrastructure reuses Phase 7 + shared layer.

---

## Common Pitfalls

### Pitfall 1: WDS Returns HTTP 200 for FAILED Responses
**What goes wrong:** Every WDS endpoint wraps responses in `{"status": "SUCCESS|FAILED", "object": ...}`. HTTP 200 is returned for both. Code that checks only `resp.raise_for_status()` will silently pass failed responses to the flattening layer, producing corrupt output.
**Why it happens:** Developers follow the HTTP idiom (200 = ok). StatCan violates this.
**How to avoid:** After `resp.raise_for_status()`, always check `item["status"] == "SUCCESS"` before accessing `item["object"]`. For list responses, iterate all items.
**Warning signs:** Client functions that access `raw[0]["object"]` directly without a status check.

### Pitfall 2: Missing Coordinate Padding
**What goes wrong:** WDS coordinate-based endpoints require exactly 10 dimension values (e.g. `"1.3.1.0.0.0.0.0.0.0"`). A coordinate like `"1.3"` returns an error or empty result.
**Why it happens:** The API docs show short examples; the 10-position requirement is buried in the spec.
**How to avoid:** Call `pad_coordinate(coord)` before constructing any WDS request body that includes a `coordinate` field.
**Warning signs:** Any raw user-provided coordinate string appearing in a request body.

### Pitfall 3: Cache Key Collisions Between Endpoints
**What goes wrong:** The shared `cached_fetch()` uses a single in-memory cache. If two endpoints are called with the same productId and the cache key doesn't include the endpoint name, a `getCubeMetadata` response could be returned for a `getSeriesInfoFromCubePidCoord` call.
**How to avoid:** Always prefix with `statcan_wds:{endpointName}:{params}`. Example: `statcan_wds:getCubeMetadata:35100003`.

### Pitfall 4: Scalar Factor Not Included in Observation Rows
**What goes wrong:** WDS observation values already have the decimal applied, but `scalarFactorCode` is a separate field. If the flattened `ObservationRow` omits the scalar label, an agent sees a value of `1.5` with no indication it means `1.5 millions`.
**How to avoid:** Include both `scalar_factor_code: int` and `scalar_factor: str` (decoded label) in every `ObservationRow`. Use the `SCALAR_FACTOR_CODES` dict from constants.

### Pitfall 5: Maintenance Window 409 Surfaced as Generic Error
**What goes wrong:** WDS returns HTTP 409 from midnight to 08:30 EST. If this is treated as a generic `UPSTREAM_ERROR`, agents get confusing messages.
**How to avoid:** Catch `httpx.HTTPStatusError` with status 409 and return `make_error("UPSTREAM_UNAVAILABLE", "StatCan WDS is in its maintenance window (00:00–08:30 EST). Try again after 08:30 EST.", ...)`.

### Pitfall 6: BM25 Pre-computation Missing
**What goes wrong:** Recalculating `avg_dl` and per-term document frequency on every search call over 80K+ cubes adds ~200ms per query.
**How to avoid:** Store `(cubes_list, avg_dl, df_table)` as a single cached object. Compute `avg_dl` and `df` once when the cube list is first loaded and cache them alongside the list.

---

## Code Examples

Verified patterns from official StatCan WDS documentation and established project patterns:

### getAllCubesListLite — Cube Discovery (SC-01)
```python
# Source: https://www.statcan.gc.ca/en/developers/wds/user-guide
# GET https://www150.statcan.gc.ca/t1/wds/rest/getAllCubesListLite
# Response: list of objects, each with fields below

# Key fields per cube object:
# productId: int          — numeric table ID (e.g. 18100004)
# cansimId: str           — legacy CANSIM number (e.g. "326-0020")
# cubeTitleEn: str        — English table title
# cubeTitleFr: str        — French table title
# cubeStartDate: str      — earliest data date
# cubeEndDate: str        — latest data date
# releaseTime: str        — last release timestamp
# archived: bool
# subjectCode: list[str]  — subject area codes
# surveyCode: list[str]   — survey codes
# frequencyCode: int      — see FREQUENCY_CODES dict
```

### getCubeMetadata — Table Metadata (SC-02)
```python
# Source: https://www.statcan.gc.ca/en/developers/wds/user-guide
# POST https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata
# Request: [{"productId": 18100004}]
# Response: [{"status": "SUCCESS", "object": {...}}]

# object fields:
# productId, cansimId, cubeTitleEn, cubeTitleFr
# cubeStartDate, cubeEndDate, frequencyCode
# nbSeriesCube, nbDatapointsCube, releaseTime
# archiveStatusCode, subjectCode, surveyCode, issueDate
# dimensions: list of {dimensionNameEn, dimensionNameFr,
#                       hasUom, members: [{memberId, parentMemberId,
#                       memberNameEn, memberNameFr, classificationCode,
#                       classificationTypeCode, geoFlag}]}
# footnotes: list of {footnoteId, footnoteTitleEn, footnoteTitleFr,
#                     memberFootnote/seriesFootnote}
```

### getSeriesInfoFromVector / getSeriesInfoFromCubePidCoord (SC-04, SC-05)
```python
# Source: https://www.statcan.gc.ca/en/developers/wds/user-guide
# POST https://www150.statcan.gc.ca/t1/wds/rest/getSeriesInfoFromVector
# Request: [{"vectorId": 32164132}]
# Response: [{"status": "SUCCESS", "object": {
#   "responseStatusCode": int,
#   "productId": int,
#   "coordinate": "1.12.0.0.0.0.0.0.0.0",
#   "vectorId": int,
#   "frequencyCode": int,
#   "scalarFactorCode": int,
#   "decimals": int,
#   "terminated": int,
#   "SeriesTitleEn": str,
#   "SeriesTitleFr": str,
#   "memberUomCode": int
# }}]

# getSeriesInfoFromCubePidCoord:
# Request: [{"productId": 35100003, "coordinate": "1.12.0.0.0.0.0.0.0.0"}]
# Same response shape
```

### getDataFromVectorsAndLatestNPeriods — Latest N (SC-06)
```python
# Source: https://www.statcan.gc.ca/en/developers/wds/user-guide
# POST https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods
# Request: [{"vectorId": 32164132, "latestN": 12}]
# Response: [{"status": "SUCCESS", "object": {
#   "productId": int,
#   "coordinate": str,
#   "vectorId": int,
#   "vectorDataPoint": [
#     {
#       "refPer": "2023-01-01",        # normalized reference period
#       "refPer2": "",                  # secondary period (for ranges)
#       "refPerRaw": "January 2023",
#       "refPerRaw2": "",
#       "value": 159.8,                # decimal already applied
#       "decimals": 1,
#       "scalarFactorCode": 0,         # 0=units
#       "symbolCode": 0,
#       "statusCode": 0,               # 0=normal
#       "securityLevelCode": 0,
#       "releaseTime": "2023-02-21T08:30",
#       "frequencyCode": 6             # 6=Monthly
#     }
#   ]
# }}]
# latestN must be > 0
```

### getBulkVectorDataByRange — Multi-Vector (SC-09)
```python
# Source: https://www.statcan.gc.ca/en/developers/wds/user-guide
# POST https://www150.statcan.gc.ca/t1/wds/rest/getBulkVectorDataByRange
# Request:
# {
#   "vectorIds": ["74804", "32164132"],
#   "startDataPointReleaseDate": "2023-01-01T08:30",
#   "endDataPointReleaseDate": "2024-01-01T08:30"
# }
# Note: vectorIds are strings in this endpoint (not ints like other endpoints)
# Response: list of {status, object} per vector — same vectorDataPoint shape
```

### getDataFromVectorByReferencePeriodRange (SC-08)
```python
# Source: https://www.statcan.gc.ca/en/developers/wds/user-guide
# GET https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorByReferencePeriodRange
# Query params: vectorIds="1","2"&startRefPeriod=2020-01-01&endReferencePeriod=2023-01-01
# Note: vectorIds repeated as comma-quoted strings, not a JSON array
# Response: same vectorDataPoint structure
```

### getChangedSeriesList / getChangedCubeList (SC-13, SC-14)
```python
# Source: https://www.statcan.gc.ca/en/developers/wds/user-guide
# GET https://www150.statcan.gc.ca/t1/wds/rest/getChangedSeriesList
# No params — returns series changed today
# Response: {"status": "SUCCESS", "object": [
#   {"vectorId": int, "productId": int, "coordinate": str,
#    "releaseTime": str, "responseStatusCode": int}
# ]}

# GET https://www150.statcan.gc.ca/t1/wds/rest/getChangedCubeList/2024-01-15
# Returns: [{"productId": int, "releaseTime": str, "responseStatusCode": int}]
```

### getCodeSets (SC-03)
```python
# Source: https://www.statcan.gc.ca/en/developers/wds/user-guide
# GET https://www150.statcan.gc.ca/t1/wds/rest/getCodeSets
# Response: {"status": "SUCCESS", "object": {
#   "scalar": [{"scalarFactorCode": 0, "scalarFactorDescEn": "units", "scalarFactorDescFr": "unités"},...],
#   "frequency": [{"frequencyCode": 6, "frequencyDescEn": "Monthly", "frequencyDescFr": "Mensuel"},...],
#   "statusCode": [...],
#   "symbolCode": [...],
#   "securityLevelCode": [...],
#   "memberUomCode": [...]
# }}
# Cache for 7 days (codes rarely change)
```

---

## State of the Art

| Old Approach (mcp-statcan) | Current Approach (mcp-canada) | Impact |
|---------------------------|-------------------------------|--------|
| AND-logic substring match, no ranking | BM25 scoring over title+subject+survey | More relevant results for ambiguous queries |
| Module-level `verify=False` client | `_make_statcan_client()` with `certifi` (Phase 7) | No SSL security regression |
| No caching | Tiered TTL cache via `cached_fetch()` | Reduces API load; faster repeated queries |
| No rate limiting | TokenBucket at 20 req/s | Prevents IP ban from burst requests |
| Flat response passthrough | Flat Pydantic models + code decoding | Agent sees `"frequency": "Monthly"` not `6` |
| No error distinction | `UPSTREAM_UNAVAILABLE` for 409 maintenance window | Agents get actionable error messages |

**Deprecated/outdated:**
- `getAllCubesList` (full): use `getAllCubesListLite` for discovery; fetch `getCubeMetadata` on demand
- Raw coordinate strings in requests: always `pad_coordinate()` first

---

## Open Questions

1. **`getDataFromVectorByReferencePeriodRange` query string format**
   - What we know: Parameters are `vectorIds="1","2"&startRefPeriod=...&endReferencePeriod=...`
   - What's unclear: Whether httpx `.get(url, params={"vectorIds": [...]})` serializes this correctly or requires manual string construction
   - Recommendation: Test with a single real vector in a unit integration test early; may need manual param construction like `"vectorIds=%221%22,%222%22"`

2. **responseStatusCode values beyond 0 and 2**
   - What we know: 0 = normal data; 2 = Census zero-filler (valid zero, not error)
   - What's unclear: Full list of `responseStatusCode` values and whether any others represent data quality flags vs errors
   - Recommendation: Return all data regardless of `responseStatusCode`; include the code in the flattened row as `status_code: int`; agents can filter

3. **asyncio.gather burst behavior with TokenBucket**
   - What we know: `getBulkVectorDataByRange` takes a list of vectorIds in one request (no burst). But `sc_get_data_by_vector` called in parallel by multiple agents could burst.
   - What's unclear: Whether the current `TokenBucket.acquire()` queues concurrent `asyncio.gather` calls properly under high concurrency
   - Recommendation: Monitor during integration testing; TokenBucket uses `asyncio.Lock` so queuing should be correct — low risk

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (no version pin in pyproject) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `uv run pytest src/mcp_canada/modules/statcan/ -x -v` |
| Full suite command | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SC-01 | BM25 cube search returns ranked results | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py::TestBm25Search -x` | Wave 0 |
| SC-01 | `sc_search_cubes` tool returns make_response envelope | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_tools.py::TestScSearchCubes -x` | Wave 0 |
| SC-02 | getCubeMetadata returns flattened dimensions | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py::TestGetCubeMetadata -x` | Wave 0 |
| SC-03 | getCodeSets returns decoded labels | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py::TestGetCodeSets -x` | Wave 0 |
| SC-04 | getSeriesInfoFromVector returns SeriesInfo | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py::TestGetSeriesInfoFromVector -x` | Wave 0 |
| SC-05 | getSeriesInfoFromCubePidCoord pads coordinate | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py::TestCoordinatePadding -x` | Wave 0 |
| SC-06 | Latest-N by vector returns ObservationRow list | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py::TestLatestNByVector -x` | Wave 0 |
| SC-07 | Latest-N by coord pads coordinate before request | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py::TestLatestNByCoord -x` | Wave 0 |
| SC-08 | Reference period range returns vectorDataPoints | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py::TestRefPeriodRange -x` | Wave 0 |
| SC-09 | Bulk vector range accepts list of vectorIds | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py::TestBulkVectorRange -x` | Wave 0 |
| SC-13 | getChangedSeriesList returns today's changes | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py::TestChangedSeries -x` | Wave 0 |
| SC-14 | getChangedCubeList by date returns cube list | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py::TestChangedCubes -x` | Wave 0 |
| INF-02 | Rate limiter `acquire()` called before each request | unit | Verify in test_client.py mock assertions | Wave 0 |
| INF-03 | Tiered cache TTLs used correctly per endpoint | unit | Mock `cached_fetch` and check `ttl` arg | Wave 0 |
| INF-04 | `lang` parameter passes through to envelope | unit | `test_tools.py` — check `_meta.lang` | Wave 0 |
| INF-05 | All tools have Keywords + Use for in docstring | auto | `uv run pytest src/mcp_canada/modules/statcan/__tests__/ -k quality` (via test_quality.py) | Existing |
| All | Live StatCan API happy paths | integration | `uv run pytest tests/integration/ -v -m integration --timeout=120` | Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest src/mcp_canada/modules/statcan/ -x -v`
- **Per wave merge:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Phase gate:** Full suite green (including coverage) before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `src/mcp_canada/modules/statcan/__tests__/conftest.py` — WDS response fixtures (cube list, metadata, series info, observation data, code sets, changed series)
- [ ] `src/mcp_canada/modules/statcan/__tests__/test_client.py` — all client function tests
- [ ] `src/mcp_canada/modules/statcan/__tests__/test_tools.py` — all tool function tests
- [ ] `src/mcp_canada/modules/statcan/schemas.py` — new file
- [ ] `src/mcp_canada/modules/statcan/tools.py` — new file
- [ ] Integration test class `TestStatcanWdsScenarios` in `tests/integration/test_tool_scenarios.py`

---

## Sources

### Primary (HIGH confidence)
- Statistics Canada WDS User Guide — https://www.statcan.gc.ca/en/developers/wds/user-guide — all endpoint URLs, HTTP methods, request/response shapes, coordinate format, maintenance window, rate limits, responseStatusCode, scalar factor behavior
- Project CLAUDE.md, `.claude/rules/modules.md`, `.claude/rules/tests.md` — all mcp-canada conventions

### Secondary (MEDIUM confidence)
- mcp-statcan `src/util/coordinate.py` — `pad_coordinate()` implementation (verified against WDS spec)
- mcp-statcan `src/api/cube_tools.py` — AND-logic search (our BM25 approach supersedes this)
- Okapi BM25 — https://en.wikipedia.org/wiki/Okapi_BM25 — formula, k1/b parameters, stdlib Python pseudocode

### Tertiary (LOW confidence)
- mcp-statcan `src/api/metadata_tools.py` — code set pattern visible only partially; implementation cross-checked against official docs

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies; all reuses verified existing project code
- API endpoints: HIGH — directly verified against official StatCan WDS User Guide
- Architecture: HIGH — follows established 5-file module pattern with verified existing patterns
- BM25 implementation: HIGH — formula from Wikipedia + verified stdlib feasibility
- Pitfalls: HIGH — cross-verified against PITFALLS.md (prior research) and official docs

**Research date:** 2026-04-07
**Valid until:** 2026-07-07 (90 days — WDS API is stable; endpoint shapes rarely change)
