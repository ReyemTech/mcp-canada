# Project Research Summary

**Project:** mcp-canada v1.1 — Statistics Canada + Shared Datastore Milestone
**Domain:** Government REST/SDMX API wrapping for MCP agent use; SQLite cross-module persistence
**Researched:** 2026-04-07
**Confidence:** HIGH

## Executive Summary

mcp-canada v1.1 adds two new modules to an already-working FastMCP server: a `statcan` module wrapping the Statistics Canada WDS REST and SDMX REST APIs, and a `datastore` module providing shared SQLite persistence across all modules. The correct build order is datastore first (no external dependencies, fastest to green), then statcan WDS tools, then SDMX tools, then the composite fetch-and-store tool that bridges both modules. Both modules follow the mandatory 5-file module pattern (`constants.py`, `schemas.py`, `client.py`, `tools.py`, `__tests__/`) and require no changes to `server.py` or `shared/`.

The recommended stack is almost entirely the existing one. The single justified new dependency is `aiosqlite==0.22.1` for async-safe SQLite access — the only alternative (`asyncio.to_thread` wrapping raw `sqlite3`) is error-prone at the connection-lifecycle level and would produce non-idiomatic code. Note: ARCHITECTURE.md recommends `asyncio.to_thread` as sufficient, while STACK.md recommends `aiosqlite` — STACK.md's reasoning is stronger. For StatCan SSL, attempt `truststore` first; fall back to a scoped `verify=False` limited strictly to the statcan module's `httpx.AsyncClient`. SDMX data queries prefer JSON via the `Accept` header, reserving `xml.etree.ElementTree` (stdlib) for structure-only responses.

The dominant risks are SQL injection via agent-supplied table names (critical, must be mitigated from first commit with an allowlist regex), blocking the asyncio event loop with synchronous sqlite3 calls (critical, wrap all SQLite I/O in `asyncio.to_thread`), and the StatCan maintenance window (00:00–08:30 EST) producing HTTP 409 responses that must be surfaced as `UPSTREAM_UNAVAILABLE` rather than retried aggressively. The WDS API also has several subtle parsing requirements — coordinate zero-padding, application-level FAILED status inside HTTP 200 responses, and SDMX parameter mutual exclusion — all of which must be enforced in `client.py`, not left to callers.

---

## Key Findings

### Recommended Stack

The existing stack (FastMCP 3.2.x, httpx, pydantic, aiocache, tenacity) handles HTTP, caching, retry, rate limiting, and validation. Only two areas require decisions:

- **Async SQLite:** `aiosqlite==0.22.1` — the established async wrapper over stdlib sqlite3; zero transitive dependencies, mirrors the sqlite3 API, and eliminates event-loop blocking without error-prone manual thread management.
- **SDMX XML parsing:** `xml.etree.ElementTree` (stdlib) — used only for SDMX structure/metadata queries (small payloads). Data queries use SDMX-JSON via `Accept` header, avoiding XML entirely for the hot path.
- **SSL:** `truststore==0.10.4` (conditional) — attempt system trust store resolution first; fall back to scoped `verify=False` on the statcan client only. Never touch the shared lifespan client.

**Core technologies:**
- `aiosqlite==0.22.1`: async SQLite access — only justified new dependency; pure Python, no transitive deps
- `xml.etree.ElementTree` (stdlib): SDMX structure XML parsing — already available, no new dep
- `truststore==0.10.4` (conditional): OS trust store for StatCan SSL — add only after empirical confirmation that certifi fails
- Existing `cached_fetch()` + `get_limiter()` + `make_response()`/`make_error()`: all reused unchanged

### Expected Features

**Must have (table stakes):**
- `statcan_search_cubes` — keyword search across 80,000+ cube titles (agent's discovery front door)
- `statcan_get_cube_metadata` — dimensions and member lists for a productId (required before any data fetch)
- `statcan_get_code_sets` — decode numeric frequency/unit/status codes (without this, values are uninterpretable)
- `statcan_get_series_info_from_vector` / `statcan_get_series_info_from_cube` — resolve between vectors and coordinates
- `statcan_get_data_latest_n_by_vector` / `statcan_get_data_latest_n_by_coord` — core data retrieval patterns
- Bilingual support (`lang: Literal["en","fr"]`) — enforced by project architecture on all tools
- `ds_create_table`, `ds_insert_rows`, `ds_query`, `ds_list_tables`, `ds_schema`, `ds_drop_table` — complete datastore CRUD

**Should have (differentiators over mcp-statcan reference):**
- `statcan_get_sdmx_structure` + `statcan_get_sdmx_data` — server-side dimension filtering, critical for large tables
- `statcan_get_bulk_vector_data` — multi-series fetch in one call
- `statcan_get_data_by_reference_period` — date-range historical analysis
- `statcan_fetch_vectors_to_store` (composite) — single-call fetch-and-store, enabling cross-module SQL
- `statcan_get_changed_series` / `statcan_get_changed_cubes` — change detection for monitoring workflows
- Proper TTL caching (mcp-statcan has none) and rate limiting (mcp-statcan has none)
- Scoped SSL fix (mcp-statcan disables SSL globally)

**Defer (anti-features — do not build):**
- Full table CSV/SDMX download tools — tables exceed 100MB, unacceptable for MCP context windows
- `getAllCubesList` (full) tool — use `getAllCubesListLite` for discovery instead
- Delta File ingestion — bulk sync for high-volume pipelines, not agent use cases
- `store_cube_metadata` composite — high complexity, low agent utility
- SQLite FTS5 on cube titles — BM25 tool discovery already handles tool finding

### Architecture Approach

Two new modules integrate via the existing FileSystemProvider auto-discovery system with zero changes to `server.py` or `shared/`. The `datastore` module is intentionally domain-agnostic — it owns SQLite connection lifecycle and SQL execution, knows nothing about any upstream API, and can be used by any current or future module. The `statcan` module wraps both WDS REST and SDMX REST APIs and is the only module that imports from `datastore` (for the composite tool). Dependency direction is strictly one-way: `statcan` → `datastore`; never the reverse.

**Major components:**
1. `datastore` module — generic SQLite CRUD; 6 tools (`ds_*`); async via `asyncio.to_thread`; configurable DB path via `MCP_CANADA_DB_PATH`
2. `statcan` module — WDS + SDMX clients; 13+ tools (`statcan_*`); scoped SSL handling; 20 req/s rate limit; tiered TTL cache
3. Composite tools in `statcan/tools.py` — `statcan_fetch_vectors_to_store` bridges both modules; statcan imports datastore client directly

### Critical Pitfalls

1. **SQL injection via agent-supplied table/column names** — use allowlist regex `^[a-zA-Z_][a-zA-Z0-9_]{0,63}$` before any SQL string construction; this must be correct from the first commit (Anthropic's own SQLite MCP server had this CVE)
2. **Blocking the asyncio event loop with sqlite3** — wrap every `sqlite3` call in `asyncio.to_thread()`; open and close connections per call; enable WAL mode; never share a connection across threads
3. **SSL `verify=False` applied globally** — create a separate `httpx.AsyncClient` scoped to `statcan/client.py` only; never modify `shared/http.py` or the server lifespan client; annotate prominently if scoped fallback is used
4. **WDS `getAllCubesList` payload overflow** — always use `getAllCubesListLite`; cache 1hr; truncate search results to top 20 before returning to agent
5. **WDS application-level FAILED status inside HTTP 200** — always check `response["status"] == "SUCCESS"` before accessing `response["object"]`; surface partial failures in `_meta` envelope

---

## Implications for Roadmap

Research strongly suggests a 6-phase build order driven by the dependency chain: datastore must exist before composite tools can be tested; WDS tools must exist before SDMX tools (SSL investigation can proceed in parallel); integration tests come last when all tool surfaces are stable.

### Phase 1: Datastore Module

**Rationale:** No external API dependency — reaches green tests using only stdlib and filesystem. Fastest feedback loop. Composite statcan tools cannot be end-to-end tested until this exists. SSL investigation for StatCan can proceed in parallel without blocking.
**Delivers:** Complete SQLite persistence layer (`ds_create_table`, `ds_insert_rows`, `ds_query`, `ds_list_tables`, `ds_schema`, `ds_drop_table`); configurable DB path; WAL mode enabled
**Addresses:** FEATURES.md Phase 5 (shared datastore)
**Avoids:** Pitfall 1 (SQL injection — allowlist regex from first commit), Pitfall 2 (event loop blocking — `asyncio.to_thread` pattern established before any tools written), Pitfall 11 (hardcoded DB path — `MCP_CANADA_DB_PATH` env var)

### Phase 2: StatCan SSL + Constants (Parallel with Phase 1)

**Rationale:** SSL resolution is empirical — it must be tested against the live StatCan endpoint. Running this in parallel with Phase 1 means the SSL approach is decided before any statcan client code is written, avoiding a rewrite.
**Delivers:** `statcan/constants.py` with all base URLs, TTL constants, rate limit config; confirmed SSL strategy (truststore or scoped `verify=False`); `pyproject.toml` updated with `aiosqlite` (and conditionally `truststore`)
**Avoids:** Pitfall 3 (global SSL disable — decision made at module boundary before client code exists)

### Phase 3: StatCan WDS Discovery + Data Tools

**Rationale:** WDS tools are the highest-value surface and the dependency prerequisite for SDMX tools (agents need productId and coordinate resolution before SDMX queries make sense). All table-stakes features live here.
**Delivers:** `statcan_search_cubes`, `statcan_get_cube_metadata`, `statcan_get_code_sets`, `statcan_get_series_info_from_vector`, `statcan_get_series_info_from_cube`, `statcan_get_data_latest_n_by_vector`, `statcan_get_data_latest_n_by_coord`, `statcan_get_data_by_reference_period`, `statcan_get_bulk_vector_data`, `statcan_get_changed_series`, `statcan_get_changed_cubes`
**Addresses:** FEATURES.md Phase 1 (discovery/metadata) + Phase 2 (data retrieval) + Phase 4 (change detection)
**Avoids:** Pitfall 4 (AllCubesList overflow — use Lite endpoint), Pitfall 5 (FAILED status ignored — check status before object access), Pitfall 7 (coordinate zero-padding — `pad_coordinate()` utility), Pitfall 8 (409 maintenance window — surface as `UPSTREAM_UNAVAILABLE`), Pitfall 9 (cache key collisions — `statcan_wds:` prefix), Pitfall 13 (scalar factor misinterpretation — include label in flattened row)

### Phase 4: StatCan SDMX Tools

**Rationale:** SDMX is a differentiating capability (server-side dimension filtering) but depends on WDS discovery to get valid productIds and coordinate structures. Building it after Phase 3 means it can be tested with real cube knowledge.
**Delivers:** `statcan_get_sdmx_structure`, `statcan_get_sdmx_data`, `statcan_get_sdmx_vector_data`
**Addresses:** FEATURES.md Phase 3 (SDMX)
**Avoids:** Pitfall 6 (SDMX `lastNObservations` + date range = 406 — enforce mutual exclusion), Pitfall 9 (cache key collisions — `statcan_sdmx:` prefix), Pitfall 10 (OR-key geography label bug — avoid `+` on geography dimension)

### Phase 5: Composite Tool

**Rationale:** `statcan_fetch_vectors_to_store` requires both Phase 1 (datastore) and Phase 3 (WDS bulk vector data) to be complete. It is a thin orchestration layer — one function call to fetch + one to insert — but it realizes the core v1.1 value proposition (cross-module data persistence).
**Delivers:** `statcan_fetch_vectors_to_store` — single-call fetch-and-store for multi-series workflows; enables cross-module SQL queries
**Addresses:** FEATURES.md Phase 6 (composite)
**Avoids:** Architecture anti-pattern 1 (composite in datastore module — it lives in `statcan/tools.py`), Architecture anti-pattern 4 (storing nested blobs — flatten VectorRow to dict before insert)

### Phase 6: Integration Tests + README

**Rationale:** Integration tests call tools through the MCP Client layer — the same way an agent would. They require all prior phases to be complete. README must be updated to reflect all new tools (required by module rules).
**Delivers:** Integration test scenarios for all tools; updated README with tool catalog; `tests/integration/README.md` documenting the 00:00–08:30 EST maintenance window
**Avoids:** Pitfall 12 (integration tests hanging — `@pytest.mark.timeout`, `@pytest.mark.integration`)

### Phase Ordering Rationale

- Phases 1 and 2 run in parallel — neither depends on the other, and parallelism accelerates the overall timeline
- Phase 3 blocks on both Phase 1 (for composite testing) and Phase 2 (for SSL decision)
- Phase 4 blocks on Phase 3 (needs real productIds and cube structures to test SDMX filtering)
- Phase 5 blocks on both Phase 1 and Phase 3
- Phase 6 is the integration sweep once all tool surfaces exist
- This ordering means no phase requires retroactive rework — critical decisions (SQL injection prevention, SSL strategy, coordinate padding) are made at module initialization, not bolted on later

### Research Flags

Phases needing empirical verification during execution:
- **Phase 2 (SSL):** truststore resolution of StatCan's certificate chain cannot be confirmed without hitting the live endpoint — decision protocol defined in STACK.md, but the outcome is unknown
- **Phase 4 (SDMX JSON structure):** STACK.md notes that `structure+json` Accept header support needs implementation-time verification; if StatCan supports it, XML parsing becomes optional entirely

Phases with standard/well-documented patterns:
- **Phase 1 (datastore):** sqlite3 + asyncio.to_thread is stdlib and well-understood; SQL injection prevention is documented with a clear regex pattern
- **Phase 3 (WDS tools):** WDS endpoints are fully documented in the official user guide with response shapes; the mcp-statcan reference validates the endpoint map
- **Phase 5 (composite):** thin orchestration over already-working tools; no new API surface
- **Phase 6 (integration tests):** follows established pattern from existing modules in `tests/integration/test_tool_scenarios.py`

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Core decisions backed by official docs and PyPI verification; only SSL resolution requires empirical testing |
| Features | HIGH | WDS and SDMX endpoints verified against official StatCan user guides; feature set cross-checked against mcp-statcan reference implementation |
| Architecture | HIGH | Based on direct source inspection of existing modules; 5-file pattern and shared utility usage are mechanical — no guesswork |
| Pitfalls | HIGH | SQL injection backed by CVE reports; SSL and SDMX constraints from official docs and mcp-statcan known issues; WDS response format from official guide |

**Overall confidence:** HIGH

### Gaps to Address

- **SSL resolution outcome:** Truststore may or may not resolve StatCan's certificate chain in CI environments. If truststore fails and scoped `verify=False` is used, document it prominently in `statcan/constants.py` and flag for future revisit (StatCan may update their certificate chain).
- **SDMX structure JSON support:** Whether StatCan's SDMX endpoint supports `application/vnd.sdmx.structure+json` is unverified. If it does, skip ElementTree for structure queries. If not, proceed with stdlib XML parsing for structure only.
- **Rate limit under asyncio.gather:** The WDS 25 req/s per-IP limit combined with `asyncio.gather()` over many vectors could cause rate-limit errors even with the TokenBucket set to 20 req/s (burst handling). Monitor during integration testing.
- **ARCHITECTURE.md vs STACK.md conflict on SQLite approach:** ARCHITECTURE.md recommends `asyncio.to_thread` with stdlib sqlite3; STACK.md recommends `aiosqlite`. Both are correct approaches — STACK.md's `aiosqlite` produces cleaner code and is the recommended choice, but either can be used. This should be decided once before Phase 1 begins.

---

## Sources

### Primary (HIGH confidence)
- Statistics Canada WDS User Guide: https://www.statcan.gc.ca/en/developers/wds/user-guide — rate limits, endpoint list, response structure, maintenance window, coordinate format, scalar factors
- Statistics Canada SDMX User Guide: https://www.statcan.gc.ca/en/developers/sdmx/user-guide — format negotiation, endpoint structure, `lastNObservations` + date range constraint
- Statistics Canada Developer Tips: https://www.statcan.gc.ca/en/developers/tips — general API usage guidance
- aiosqlite PyPI: https://pypi.org/project/aiosqlite/ — version 0.22.1, December 2025
- truststore PyPI: https://pypi.org/project/truststore/ — version 0.10.4, August 2025
- Python stdlib docs (xml.etree.ElementTree, asyncio.to_thread, sqlite3) — namespace parsing, thread offloading patterns
- httpx SSL docs: https://www.python-httpx.org/advanced/ssl/ — verify parameter, custom SSLContext usage
- Existing mcp-canada module source (bank_of_canada, shared/) — direct inspection for pattern conformance

### Secondary (MEDIUM confidence)
- mcp-statcan reference implementation (Aryan Jhaveri): https://github.com/Aryan-Jhaveri/mcp-statcan — confirms SSL is globally disabled, SDMX-JSON utility exists, OR-key label bug, 406 on combined SDMX params, context overflow risk
- SQL injection in MCP SQLite server (GitHub issue #3314): https://github.com/modelcontextprotocol/servers/issues/3314 — CVE pattern confirmation

### Tertiary (LOW confidence)
- mcp-statcan on MCP Market: https://mcpmarket.com/server/statcan-api — use cases only, marketing copy
- Datadog Security Labs MCP SQL injection case study — pattern validation, not StatCan-specific
- Trend Micro SQLite MCP vulnerability analysis — confirms injection vector applies to table names

---
*Research completed: 2026-04-07*
*Ready for roadmap: yes*
