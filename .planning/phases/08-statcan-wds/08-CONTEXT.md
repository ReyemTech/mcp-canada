# Phase 8: StatCan WDS - Context

**Gathered:** 2026-04-07
**Status:** Ready for planning

<domain>
## Phase Boundary

All Statistics Canada WDS REST API tools: cube discovery/search, metadata retrieval, code set decoding, series info (by vector and by coordinate), data retrieval (latest-N, date-range, bulk multi-vector), and change monitoring. Plus infrastructure: rate limiting, tiered caching, bilingual support, and mcp-canada tool conventions. No SDMX tools or composite/datastore tools in this phase.

</domain>

<decisions>
## Implementation Decisions

### Cube search behavior
- BM25/TF-IDF ranking algorithm for keyword search across 80K+ cubes
- Search fields: title (en/fr), subject codes, survey name — not notes/footnotes
- Default result limit: top 10 (agent can pass `limit` param for more)
- Cube list loaded lazily on first search call, cached for 1hr per existing constants
- Cache uses existing `cached_fetch()` from `shared/cache.py`

### Response flattening
- Full flatten: strip StatCan's `[{status, object}]` envelope, extract data, convert string numbers to floats
- Code IDs: include both code and decoded label — e.g., `{"frequency_code": 6, "frequency": "Monthly"}`
- Coordinate auto-padding: agent passes `"1.1"` and client pads to 10 dimensions (`"1.1.0.0.0.0.0.0.0.0"`)
- All tools return `make_response()` / `make_error()` envelopes per mcp-canada convention

### Tool naming & grouping
- Prefix: `sc_` (short, token-efficient, covers both WDS and future SDMX)
- Descriptive names: `sc_search_cubes`, `sc_get_cube_metadata`, `sc_get_data_by_vector`, `sc_get_changed_series`, etc.
- All tools follow standalone `@tool` pattern with `lang: Literal["en", "fr"]`, `Use for:` + `Keywords:` docstrings

### Claude's Discretion
- Exact BM25 implementation approach (stdlib difflib SequenceMatcher, or custom scoring)
- Whether to split client.py into wds_client.py for this phase (single file is fine if manageable)
- Pydantic schema design for flattened responses
- Error code mappings for StatCan's `responseStatusCode` values
- How to handle the WDS maintenance window (00:00-08:30 EST) — 409 responses

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `shared/cache.py`: `cached_fetch(key, ttl, fetcher)` — use for cube list, metadata, code sets
- `shared/rate_limiter.py`: `get_limiter("statcan", rate=20.0)` — constants already defined in Phase 7
- `shared/envelope.py`: `make_response()` / `make_error()` — standard envelope
- `shared/http.py`: NOT used for StatCan — `_make_statcan_client()` in `statcan/client.py` handles SSL scoping
- `modules/statcan/constants.py`: `BASE_URL`, `RATE_GROUP`, `RATE_LIMIT`, `STATCAN_VERIFY` already set
- `modules/statcan/client.py`: `_make_statcan_client()` factory ready

### Established Patterns
- 5-file module pattern (constants, schemas, client, tools, __init__)
- Client functions return `(data, was_cached)` tuples
- Tool docstrings require `Use for:` and `Keywords:` lines for BM25 discovery
- All tools accept `lang: Literal["en", "fr"]`
- Flat Pydantic schemas (no nested models mirroring API structure)
- `difflib.get_close_matches()` for suggestions on invalid input

### Integration Points
- `statcan/constants.py` — add cache TTLs, WDS endpoint paths, code set mappings
- `statcan/client.py` — expand from factory to full WDS client functions
- `statcan/schemas.py` — create (new file) for flattened response models
- `statcan/tools.py` — create (new file) for all `sc_` tool functions
- `statcan/__init__.py` — update MODULE_NAME and MODULE_DESCRIPTION

</code_context>

<specifics>
## Specific Ideas

- Inspired by mcp-statcan by Aryan Jhaveri (https://github.com/Aryan-Jhaveri/mcp-statcan) — porting API logic with mcp-canada quality standards
- mcp-statcan's coordinate padding utility (`pad_coordinate`) is a useful reference for the auto-pad implementation
- mcp-statcan's code set cache (module-level globals with 1hr TTL) can inform the caching approach, but use `cached_fetch()` instead

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 08-statcan-wds*
*Context gathered: 2026-04-07*
