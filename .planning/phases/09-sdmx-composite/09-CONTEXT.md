# Phase 9: SDMX + Composite - Context

**Gathered:** 2026-04-07
**Status:** Ready for planning

<domain>
## Phase Boundary

SDMX REST API tools for server-side filtered queries (structure + data + vector) and the composite fetch-and-store tool that bridges StatCan WDS with the shared datastore. No new WDS tools, no datastore changes.

</domain>

<decisions>
## Implementation Decisions

### SDMX key syntax UX
- Support both raw SDMX key strings AND named dimension dicts
- Raw key: agent passes `"1.2+3.."` directly (matches SDMX spec)
- Named dict: agent passes `{"geography": ["Ontario"], "age": "all"}` — tool translates to key using codelist from `sc_get_sdmx_structure`
- Raw key is the primary interface; named dict is a convenience layer
- `sc_get_sdmx_structure` response includes a suggested key example (e.g., `"1...."`) showing dimension positions so agents can copy-paste into `sc_get_sdmx_data`
- Mutual exclusion enforced: `lastN` and date range (`start_period`/`end_period`) cannot be used simultaneously — return `INVALID_INPUT` error if both provided

### Composite store behavior
- `sc_fetch_vectors_to_store` requires agent-specified `table_name` parameter (no auto-naming)
- Table name follows module prefix convention from Phase 7: `statcan_cpi_2024`, `statcan_gdp_quarterly`, etc.
- If table already exists: append new rows (consistent with Phase 7 append-only decision)
- Table created on first call if it doesn't exist — uses `ds_create_table` internally
- Schema inferred from fetched data (consistent with Phase 7 type inference decision)

### Claude's Discretion
- SDMX XML namespace handling pattern (ElementTree vs JSON content negotiation)
- Whether `sc_get_sdmx_data` and `sc_get_sdmx_vector_data` share a common flattening helper
- How to serialize the named dimension dict → SDMX key translation
- Error handling for invalid SDMX key syntax

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `statcan/client.py`: `_make_statcan_client()`, `_limiter_acquire()`, `_statcan_fetch()`, `_statcan_retry`, `_unwrap()`, `pad_coordinate()`, `_flatten_observation()` — all reusable for SDMX
- `statcan/constants.py`: `BASE_URL`, `CACHE_TTL_*`, `RATE_GROUP`, `RATE_LIMIT`, `TIMEOUT_LARGE`
- `statcan/schemas.py`: `ObservationRow` can be reused for SDMX observations (same fields)
- `datastore/client.py`: `create_table()`, `insert_rows()` — called by composite tool
- `shared/envelope.py`: `make_response()` / `make_error()`

### Established Patterns
- `sc_` prefix for all StatCan tools (Phase 8 decision)
- Full flatten with both code + label fields
- Tools catch `HTTPStatusError` (409 → `UPSTREAM_UNAVAILABLE`), `ValueError`, `Exception`
- Client functions return `(data, was_cached)` tuples

### Integration Points
- `statcan/client.py` — add SDMX client functions (new SDMX base URL in constants)
- `statcan/tools.py` — add 3 SDMX tools + 1 composite tool
- `statcan/schemas.py` — add SDMX-specific schemas if needed (SDMXDimension, SDMXCodelist)
- Composite tool imports from both `statcan/client.py` and `datastore/client.py`

</code_context>

<specifics>
## Specific Ideas

- SDMX REST base URL is different from WDS: `https://www150.statcan.gc.ca/t1/wds/sdmx/statcan/rest/`
- Structure endpoint returns XML (SDMX 2.1); data endpoint can return JSON via `Accept: application/vnd.sdmx.data+json`
- The composite tool is the capstone — it enables the core value proposition ("cross-module SQL queries")

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 09-sdmx-composite*
*Context gathered: 2026-04-07*
