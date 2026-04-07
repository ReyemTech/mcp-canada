# mcp-canada v1.1: Statistics Canada Integration

## What This Is

An expansion of the mcp-canada MCP server to include Statistics Canada data (80,000+ data tables covering demographics, economy, health, environment, and more) alongside the existing 7 federal APIs. Adds a shared SQLite datastore module enabling cross-module data analysis — agents can fetch data from any API, store it locally, and run SQL queries across sources.

## Core Value

An agent can combine data from any Canadian government source (BoC rates, StatCan GDP, weather, recalls) in a single SQL query — turning 7 isolated APIs into one queryable data platform.

## Requirements

### Validated

- ✓ Bank of Canada module (8 tools) — v1.0
- ✓ Open Parliament module (10 tools) — v1.0
- ✓ Recalls & Safety Alerts module (6 tools) — v1.0
- ✓ Drug Product Database module (8 tools) — v1.0
- ✓ CKAN Open Data module (7 tools) — v1.0
- ✓ Canadian Nutrient File module (8 tools) — v1.0
- ✓ Weather/Climate module (34 tools) — v1.0
- ✓ BM25 discovery + meta tools (5 tools) — v1.0
- ✓ Install subcommand (14 platforms) — v1.0.post
- ✓ Bilingual support (en/fr) — v1.0

### Active

- [ ] Statistics Canada WDS REST tools (cube search, metadata, series info, vector data, code sets)
- [ ] Statistics Canada SDMX tools (structure queries, server-side filtered data, vector data)
- [ ] Composite fetch tools (bulk vector fetch with local storage)
- [ ] Shared SQLite datastore module (create table, insert, query, schema, list, drop)
- [ ] Cross-module store tools (any module can write fetched data to the shared datastore)
- [ ] StatCan SSL certificate handling (fix verify=False with proper cert bundling)
- [ ] Proper caching for StatCan APIs (cube list 1hr, metadata 24hr, observations 1hr)
- [ ] Rate limiting for StatCan endpoints
- [ ] Bilingual support for StatCan tools (en/fr)
- [ ] Unit tests for all new tools (95%+ coverage)
- [ ] Integration tests for live StatCan API calls
- [ ] README update with StatCan module and datastore documentation
- [ ] EXAMPLES.md update with cross-module SQL query examples

### Out of Scope

- SQLite full-text search — unnecessary complexity, BM25 discovery handles tool finding
- StatCan bulk CSV/SDMX file downloads — too large for MCP context, agents should use filtered queries
- Real-time StatCan notifications — no push API exists
- StatCan data visualization — agents handle presentation
- Migration of existing modules to use the datastore — future enhancement, not required for v1.1
- HTTP transport for the datastore — SQLite is local-only by design

## Context

mcp-statcan (https://github.com/Aryan-Jhaveri/mcp-statcan) by Aryan Jhaveri is an existing MCP server for Statistics Canada data. It uses the raw MCP SDK (not FastMCP), has 18 tools (10 API + 2 composite + 6 database), zero tests, and disables SSL globally. We are porting its API logic into mcp-canada's architecture — not using it as a dependency.

Statistics Canada exposes two public APIs:
- **WDS REST API** (`https://www150.statcan.gc.ca/t1/wds/rest`) — JSON, no auth, list-wrapped responses with status/object pattern
- **SDMX REST API** (`https://www150.statcan.gc.ca/t1/wds/sdmx/statcan/rest/`) — XML structures + JSON data, no auth, server-side filtering

StatCan's SSL certificate chain has known issues requiring `verify=False` in httpx. We will attempt to fix this with proper cert bundling (certifi or pinned cert) rather than disabling verification.

The shared datastore is a new architectural concept for mcp-canada. It adds a `datastore` module with generic SQLite tools that any module can use. This enables the core value: cross-module SQL queries.

## Constraints

- **No new dependencies beyond stdlib**: SQLite is in stdlib (`sqlite3`). StatCan API calls use existing `httpx`. No ORM.
- **5-file module pattern**: Both `statcan` and `datastore` modules must follow the existing pattern (constants, schemas, client, tools, __init__)
- **95%+ test coverage**: All new code must be tested. Integration tests for live StatCan APIs.
- **Backward compatible**: Existing modules unchanged. `uvx mcp-canada` still works. `--modules statcan` loads only StatCan.
- **SSL**: Attempt cert fix; fall back to scoped `verify=False` for statcan module only if cert bundling fails.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Fork & absorb (not dependency) | mcp-statcan uses raw MCP SDK, incompatible with FastMCP/BM25 | — Pending |
| Shared datastore (not statcan-only) | Cross-module SQL is the core value proposition | — Pending |
| Both WDS + SDMX APIs | SDMX enables server-side filtering for large datasets | — Pending |
| Include SQLite/composite tools | Enables multi-step analysis workflows | — Pending |
| "Inspired by" attribution | Credit Aryan Jhaveri without implying fork/derivation | — Pending |
| Try to fix SSL (not disable) | Security-first; fall back to scoped disable if needed | — Pending |

---
*Last updated: 2026-04-07 after initialization*
