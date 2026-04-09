# Phase 13: Toronto Municipal Government Open Data - Context

**Gathered:** 2026-04-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Add Toronto's municipal open data catalogue (open.toronto.ca) to mcp-canada. Toronto uses CKAN API at `ckan0.cf.opendata.inter.prod-toronto.ca`. Provides CKAN discovery tools + curated high-value dataset tools for transit, neighbourhoods, 311 requests, housing, and budget data. Also extends shared parsers with GeoJSON and JSON support.

</domain>

<decisions>
## Implementation Decisions

### Curated datasets
- TTC transit: parse GTFS CSV files (stops.txt, routes.txt, trips.txt) into searchable structured data — not just download links
- Neighbourhood profiles: two tools — one for single-neighbourhood deep dive (all indicators), one for cross-neighbourhood comparison (single indicator across all 140 neighbourhoods)
- 311 Service Requests: use CKAN Datastore SQL (`datastore_search_sql`) for server-side filtering by date range, category, ward — dataset is too large to fetch entirely
- Property/housing: full coverage — building permits, short-term rentals (Airbnb/VRBO registrations), and apartment buildings (RentSafeTO scores)
- Budget/finance: include Financial Information Return — revenue, expenses, capital spending by department

### Tool naming
- Prefix: `toronto_` (consistent with `ontario_` pattern)
- Convention locked for all future municipal modules: full city name always (montreal_, vancouver_, calgary_, edmonton_, etc.)

### Data format handling
- Parse all parseable formats: CSV, XLSX, JSON, GeoJSON
- GeoJSON: properties only by default, `include_geometry=true` parameter to include coordinates
- New parsers (`_parse_geojson()`, `_parse_json()`) go into shared/parsers.py — reusable for all future modules

### Claude's Discretion
- Exact CKAN Datastore SQL query patterns for 311 data
- Which specific GTFS files to parse (stops.txt is essential; shapes.txt may be too large)
- RentSafeTO vs apartment buildings dataset selection based on data quality
- How to handle neighbourhood profile indicator names (snake_case or preserve original)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/mcp_canada/modules/ontario/` — identical CKAN API pattern, can copy structure and swap URLs
- `shared/parsers.py` — `fetch_and_parse()` handles CSV/XLSX/XLS, needs GeoJSON + JSON additions
- `shared/reshape.py` — `reshape_observations()` and `reshape_temporal_columns()` for nested output if needed
- `shared/cache.py` — `cached_fetch()` for all client functions
- `shared/rate_limiter.py` — `get_limiter()` per-source TokenBucket
- `shared/envelope.py` — `make_response()`/`make_error()` for all tool returns

### Established Patterns
- CKAN client: `fetch_search_datasets()`, `fetch_dataset_details()`, etc. with `_shape_dataset()` helper
- Module structure: 5-file pattern (__init__, constants, schemas, client, tools)
- Bilingual: `title_translated`/`notes_translated` fallback chain in CKAN responses
- BM25 docstrings: `Use for:` + `Keywords:` on single lines

### Integration Points
- `shared/parsers.py` — add `_parse_geojson()` and `_parse_json()` to routing in `fetch_and_parse()`
- `tests/integration/test_tool_scenarios.py` — append `TestTorontoToolScenarios` class
- `README.md` — add Toronto section, update tool count

</code_context>

<specifics>
## Specific Ideas

- CKAN base URL: `ckan0.cf.opendata.inter.prod-toronto.ca`
- Toronto CKAN has Datastore enabled on many CSV resources — use `datastore_search_sql` for 311 queries
- GTFS data: parse CSV files inside the GTFS ZIP or use individual resource downloads if available
- Neighbourhood profiles: ~2,400 indicators per neighbourhood, 140 neighbourhoods

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 13-toronto-municipal-government-open-data*
*Context gathered: 2026-04-09*
