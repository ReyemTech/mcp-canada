# Feature Landscape: Statistics Canada MCP Integration

**Domain:** Statistics Canada WDS REST + SDMX API wrapping for MCP agent use
**Researched:** 2026-04-07
**Overall confidence:** HIGH (WDS endpoints verified against official docs; SDMX verified against official user guide; feature categorisation cross-checked against mcp-statcan reference implementation)

---

## Table Stakes

Features agents expect. Missing = module feels broken or useless.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Cube search by keyword | Agents must be able to discover tables without knowing productId upfront. 80,000+ tables — discovery is the front door. | Low | WDS `getAllCubesListLite` returns full inventory; search must be client-side (no server-side search endpoint exists in WDS). Cache 1hr. |
| Cube metadata retrieval | Once a productId is found, agents need dimension names and member lists to construct valid series coordinates. | Low | WDS `getCubeMetadata` POST. Response includes title (en+fr), dimensions, members, footnotes. |
| Code set decoding | WDS responses use numeric codes for frequency, units of measure, scalar factor, and observation status. Without decoding, agent sees "6" instead of "Monthly". | Low | WDS `getCodeSets` GET. Cache indefinitely (code sets rarely change). |
| Latest-N data by vector | Most common retrieval pattern: "give me the last 12 months of series V123456". Vectors are the primary way StatCan identifies a data point. | Low | WDS `getDataFromVectorsAndLatestNPeriods` POST. |
| Latest-N data by productId + coordinate | Second retrieval path: agent knows the table and dimension combination but not the vectorId. | Low | WDS `getDataFromCubePidCoordAndLatestNPeriods` POST. |
| Series info by vector | Resolve a vectorId to its metadata (table, coordinate, frequency, units). Required before agents can interpret values. | Low | WDS `getSeriesInfoFromVector` POST. |
| Series info by productId + coordinate | Reverse lookup: resolve a coordinate to its vectorId and metadata. Required when agent knows the table structure but needs the vector. | Low | WDS `getSeriesInfoFromCubePidCoord` POST. |
| Bilingual support (en/fr) | mcp-canada enforces `lang: Literal["en","fr"]` on every tool. StatCan natively supports both languages. Not optional. | Low | Pass `lang` through to API calls where the endpoint accepts it (e.g., `getFullTableDownloadCSV/{productId}/{language}`). |
| Envelope + error contract | All mcp-canada tools must return `make_response()` or `make_error()`. BM25 discovery depends on docstring Keywords. | Low | Architectural requirement — not StatCan-specific, but must not be omitted. |

---

## Differentiators

Features that make this integration more powerful than the reference mcp-statcan implementation.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| SDMX filtered data retrieval | Server-side dimension filtering via SDMX key syntax (e.g., `1.2+3..` to select specific members). Avoids returning entire table when agent only needs one province or one age group. Critical for large tables. | Medium | SDMX `data` endpoint at `https://www150.statcan.gc.ca/t1/wds/sdmx/statcan/rest/`. Key syntax: dot-separated dimensions, `+` for OR, empty position for wildcard. Supports `startPeriod`, `endPeriod`, `lastNObservations` query params. |
| SDMX structure query | Returns dimension codelists for a table — the valid values per dimension. Required to construct valid SDMX filter keys without guessing. Agents must call this before calling SDMX data. | Medium | SDMX `structure` endpoint. Returns XML (parse to extract codelist values). |
| SDMX vector data | Retrieve filtered observations by vectorId via SDMX. Alternative to WDS for single-series retrieval with date range control. | Low | SDMX vector endpoint. Supports `startPeriod`/`endPeriod`. |
| Date-range data by reference period | Retrieve data for a vector within a specific reference period window (not just latest-N). Enables precise historical analysis. | Low | WDS `getDataFromVectorByReferencePeriodRange` GET. Useful for economic time-series spanning specific policy periods. |
| Bulk vector fetch by date range | Retrieve data for multiple vectors simultaneously within a release date range. Enables multi-series comparison without multiple round trips. | Medium | WDS `getBulkVectorDataByRange` POST. Accepts list of vectorIds + start/end release datetimes. |
| Shared SQLite datastore | Any module can persist fetched data to a local SQLite database and run SQL queries across sources. Cross-module SQL (e.g., JOIN BoC interest rates with StatCan CPI) is the core value proposition of v1.1. | High | Shared `datastore` module: `create_table`, `insert_data`, `query_database`, `list_tables`, `get_table_schema`, `drop_table`. No ORM — raw `sqlite3`. |
| Composite fetch-and-store | Single tool call: fetch multiple vectors for a date range AND store results to SQLite. Reduces round trips for common analysis workflows. | Medium | Combines WDS `getBulkVectorDataByRange` + datastore insert. Reference: mcp-statcan `fetch_vectors_to_database`. |
| SSL certificate fix | mcp-statcan disables SSL globally (`verify=False` on the module-level client). We attempt proper cert bundling (certifi). Scoped fallback if cert bundling fails. Security improvement over the reference implementation. | Medium | Constraint from PROJECT.md. Attempt certifi bundle; if StatCan cert chain still fails, scope `verify=False` to the StatCan httpx client only — do not touch global SSL state. |
| Proper TTL caching | mcp-statcan has no caching. mcp-canada adds tiered TTL: cube list 1hr, cube metadata 24hr, observations 1hr, code sets indefinitely. Prevents hammering the StatCan API (rate limit: 25 req/s per IP). | Low | Use existing `cached_fetch()` from `shared/cache.py`. TTL constants in `statcan/constants.py`. |
| Rate limiting | mcp-statcan has no rate limiting. mcp-canada adds per-source TokenBucket. StatCan limit: 50 req/s global, 25 req/s per IP. | Low | Use existing `get_limiter()` from `shared/rate_limiter.py`. |
| Changed series/cubes detection | Agents can ask "what StatCan data changed today?" — useful for daily monitoring workflows. | Low | WDS `getChangedSeriesList` (today's changes) and `getChangedCubeList/{date}` (changes on a specific date). |

---

## Anti-Features

Features to deliberately NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Full table CSV download | `getFullTableDownloadCSV` returns a URL pointing to a large ZIP file. Tables routinely exceed 100MB. Unacceptable for MCP context windows. Agents can't process raw CSV blobs. | Use SDMX filtered queries or latest-N vector fetches to retrieve only the needed slice. |
| Full table SDMX download | Same problem as CSV: `getFullTableDownloadSDMX` returns a URL to a massive XML archive. | Use SDMX filtered data endpoint with explicit key filtering instead. |
| getAllCubesList (full) | The full `getAllCubesList` includes dimension-level detail for every table — very large response, slow, rarely needed. | Use `getAllCubesListLite` for discovery (no dimension detail), then `getCubeMetadata` for the specific table the agent selects. |
| Delta File ingestion | The Delta File service is for high-volume bulk sync (all changed data each business day). MCP agents don't need full corpus sync. | Use `getChangedSeriesList` or `getChangedCubeList` for monitoring; fetch specific vectors when changes are relevant. |
| Data visualization | Rendering charts is out of scope for an MCP tool server. mcp-statcan demo GIFs show agents generating visualizations — that's the agent's job, not the server's. | Return structured data. Let the agent (Claude, GPT, etc.) handle presentation. |
| StatCan notifications / push | No push API exists. StatCan does not support webhooks or subscriptions. | Use `getChangedSeriesList` for poll-based change detection. |
| Store cube metadata to SQLite | mcp-statcan's `store_cube_metadata` creates complex relational tables (dimensions + members). High complexity, low agent utility — agents rarely need to SQL-query dimension structure. | Expose metadata via `statcan_get_cube_metadata` tool. Store observation data (not metadata) to SQLite if persistence is needed. |
| HTTP transport for datastore | SQLite is a local file. Exposing it over HTTP would require auth, serialization, and a network layer. | Keep SQLite local-only. MCP stdio/SSE transport already handles the client-server boundary. |
| SQLite full-text search on cube titles | BM25 tool discovery already handles tool finding. A separate FTS5 index on cube titles adds complexity without clear benefit — the cube list is cached in memory already. | Use the in-process cube search (title substring/keyword matching in the cached list). |

---

## Feature Dependencies

```
statcan_search_cubes
  (no dependencies — standalone discovery)

statcan_get_cube_metadata
  → requires: productId (typically found via statcan_search_cubes)

statcan_get_series_info_from_cube
  → requires: productId + coordinate
  → requires: statcan_get_cube_metadata to know valid dimension members

statcan_get_series_info_from_vector
  → requires: vectorId (known from statcan_get_cube_metadata or prior query)

statcan_get_data_latest_n_by_vector
  → requires: vectorId
  → depends on: statcan_get_series_info_from_vector OR statcan_get_cube_metadata (to find vectorId)

statcan_get_data_latest_n_by_coord
  → requires: productId + coordinate
  → depends on: statcan_get_cube_metadata (to know valid coordinate)

statcan_get_data_by_reference_period
  → requires: vectorId + date range
  → depends on: statcan_get_series_info_from_vector

statcan_get_bulk_vector_data
  → requires: list of vectorIds + release date range
  → depends on: statcan_get_series_info_from_vector (to build vectorId list)

statcan_get_sdmx_structure
  → requires: productId (from statcan_search_cubes)
  → produces: dimension codelists needed to build SDMX filter keys

statcan_get_sdmx_data
  → requires: productId + SDMX filter key
  → HARD DEPENDENCY: statcan_get_sdmx_structure (must call first to know valid key values)

statcan_get_sdmx_vector_data
  → requires: vectorId
  → optional: startPeriod/endPeriod

statcan_get_code_sets
  → no dependencies — decoding reference, call anytime

statcan_get_changed_series
  → no dependencies — returns today's changed series

statcan_get_changed_cubes
  → requires: ISO date string

datastore_create_table
  → no dependencies

datastore_insert_data
  → requires: table must exist (datastore_create_table or prior insert)

datastore_query
  → requires: at least one table with data

datastore_list_tables
  → no dependencies

datastore_get_schema
  → requires: named table must exist

datastore_drop_table
  → requires: named table must exist

statcan_fetch_vectors_to_store (composite)
  → requires: vectorIds + date range
  → HARD DEPENDENCY: datastore (SQLite available)
  → calls: statcan_get_bulk_vector_data + datastore_insert_data internally
```

---

## MVP Recommendation

Prioritize for v1.1 milestone in this order:

**Phase 1 — Discovery and Metadata (unblock all other tools)**
1. `statcan_search_cubes` — cube title keyword search
2. `statcan_get_cube_metadata` — dimension/member detail
3. `statcan_get_code_sets` — code decoding reference
4. `statcan_get_series_info_from_vector` — vector resolution
5. `statcan_get_series_info_from_cube` — coordinate resolution

**Phase 2 — Data Retrieval (core value)**
6. `statcan_get_data_latest_n_by_vector` — most common fetch pattern
7. `statcan_get_data_latest_n_by_coord` — alternate fetch path
8. `statcan_get_data_by_reference_period` — date-range fetch
9. `statcan_get_bulk_vector_data` — multi-series fetch

**Phase 3 — SDMX (differentiating capability)**
10. `statcan_get_sdmx_structure` — dimension codelists
11. `statcan_get_sdmx_data` — filtered data retrieval
12. `statcan_get_sdmx_vector_data` — SDMX single-vector fetch

**Phase 4 — Change Detection**
13. `statcan_get_changed_series` — today's changed series
14. `statcan_get_changed_cubes` — changed tables by date

**Phase 5 — Shared Datastore (enables cross-module SQL)**
15. `datastore_create_table`
16. `datastore_insert_data`
17. `datastore_query`
18. `datastore_list_tables`
19. `datastore_get_schema`
20. `datastore_drop_table`

**Phase 6 — Composite (requires Phase 2 + Phase 5)**
21. `statcan_fetch_vectors_to_store`

**Defer:**
- Full table CSV/SDMX download tools — anti-feature (too large for MCP context)
- `store_cube_metadata` composite — anti-feature (high complexity, low agent utility)

---

## Commonly Needed Data Tables (Reference for Integration Tests)

These are the most frequently accessed StatCan tables. Useful for writing realistic integration test scenarios.

| Domain | Table ID | Description |
|--------|----------|-------------|
| Labour | 14-10-0287-03 | Labour force characteristics by province, monthly, seasonally adjusted |
| Prices | 18-10-0004-01 | Consumer Price Index, monthly, not seasonally adjusted |
| GDP | 36-10-0434-01 | GDP at basic prices, by industry, monthly |
| GDP | 36-10-0222-01 | Gross domestic product, expenditure-based, provincial and territorial, annual |
| Housing | 36-10-0688-01 | Estimates of housing stock in units |
| Trade | 12-10-0011-01 | International trade in services |
| Environment | 38-10-0097-01 | Greenhouse gas emissions by province and territory |

Note: Table IDs use the format `NN-10-NNNN-NN`. Strip hyphens and trailing zeros to get the numeric productId for WDS API calls (e.g., `18-10-0004-01` → productId `18100004`).

---

## Sources

- Statistics Canada WDS User Guide: https://www.statcan.gc.ca/en/developers/wds/user-guide (HIGH confidence — official documentation)
- Statistics Canada SDMX User Guide: https://www.statcan.gc.ca/en/developers/sdmx/user-guide (HIGH confidence — official documentation)
- Statistics Canada Developer Tips: https://www.statcan.gc.ca/en/developers/tips (HIGH confidence — official)
- mcp-statcan reference implementation: https://github.com/Aryan-Jhaveri/mcp-statcan (MEDIUM confidence — implementation reference, not documentation)
- mcp-statcan on MCP Market: https://mcpmarket.com/server/statcan-api (LOW confidence — marketing copy, use cases only)
- PROJECT.md constraints and key decisions (HIGH confidence — project-specific, already validated)
