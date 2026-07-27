# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Unit tests (fast, mocked — default)
uv run pytest

# Single test file
uv run pytest src/mcp_canada/modules/bank_of_canada/__tests__/test_tools.py -x -v

# Single test
uv run pytest src/mcp_canada/modules/bank_of_canada/__tests__/test_tools.py::TestBocGetExchangeRates::test_returns_exchange_rates -x

# Integration tests (live APIs, ~2min)
uv run pytest tests/integration/ -v -m integration --timeout=120

# Coverage (must be ≥95%)
uv run pytest --cov=src/mcp_canada --cov-fail-under=95

# Start server
uv run mcp-canada                                    # stdio
uv run mcp-canada --transport sse --port 8000         # SSE
uv run mcp-canada --transport http --port 8000        # Streamable HTTP
uv run mcp-canada --modules bank_of_canada,recalls    # selective

# Type check & lint
uv run pyright
uv run ruff check src/ tests/
```

## Architecture

**FastMCP 3.2.x** with FileSystemProvider auto-discovery. Drop a module folder into `src/mcp_canada/modules/` — it registers automatically.

**BM25SearchTransform** hides all tools behind `discover_tools` + `call_tool`. Agents see 3 always-visible tools; the ~50 underlying tools are found via BM25 search.

**Lifespan** creates a shared `httpx.AsyncClient`. Supports stdio, SSE, and Streamable HTTP.

### Module Pattern (7 files + tests)

Every module in `src/mcp_canada/modules/{name}/`:

| File | Purpose |
|------|---------|
| `__init__.py` | `MODULE_NAME` and `MODULE_DESCRIPTION` |
| `constants.py` | `BASE_URL`, `RATE_GROUP`, `RATE_LIMIT`, `CACHE_TTL`, mappings |
| `schemas.py` | Pydantic v2 models — always flat |
| `client.py` | Async functions returning `(data, was_cached)` tuples |
| `tools.py` | `@tool` functions (standalone, NOT `@mcp.tool`) |
| `prompts.py` | `@prompt` functions — guided workflows + quick lookups |
| `resources.py` | `@resource` functions — catalogs, docs, templates |
| `__tests__/` | `conftest.py`, `test_client.py`, `test_tools.py`, `test_prompts_resources.py` |

### Shared Utilities (`src/mcp_canada/shared/`)

- `cache.py` — `cached_fetch(key, ttl, fetcher)` → `(data, was_cached)`
- `envelope.py` — `make_response()` / `make_error()` for _meta envelope
- `rate_limiter.py` — `get_limiter(source, rate)` per-source TokenBucket
- `http.py` — `api_get(url, params, headers)` with retry on 429/5xx
- `i18n.py` — `t(key, lang)` bilingual error messages
- `arcgis_hub.py` — ArcGIS Hub FeatureServer client (Phase 14: York Region and other ArcGIS Hub portals)
- `ogc.py` — OGC WFS 2.0 client (Phase 15: BC Geographic Warehouse; reuse for Quebec and other provinces with WFS portals)
- `socrata.py` — Socrata SODA client (Phase 20: Nova Scotia data.novascotia.ca; reuse for future Socrata portals PEI/NB)

### Portal Technologies (4)

| Technology | Client | First used | Pattern |
|-----------|--------|------------|---------|
| **CKAN** | `shared/http.py` + per-module `_api_get` | Federal CKAN, Ontario, Toronto, BC CKAN, Quebec (Données Québec), Alberta (open.alberta.ca) | `BASE_URL + /api/3/action/` |
| **ArcGIS Hub** | `shared/arcgis_hub.py` | Phase 14: York Region; Phase 17: Alberta (WMBappServices wildfire, AHSGIS health, GeoDiscover environment/parks); Phase 18: Manitoba (geoportal.gov.mb.ca, org mMUesHYPkXjaFGfS); Phase 19: Saskatchewan (geohub.saskatchewan.ca, primary org zcv98lgAl8xQ04cW + WSA org 7MBdlVpjqbfBhQer + SPSA gis.saskatchewan.ca/egis) | FeatureServer `query` endpoint |
| **OGC WFS 2.0** | `shared/ogc.py` | Phase 15: British Columbia | `GetFeature` with CQL_FILTER; two-step CKAN→WFS workflow |
| **Socrata** | `shared/socrata.py` | Phase 20: Nova Scotia (data.novascotia.ca) | SODA API: `/api/catalog/v1` discovery + `/resource/{id}.json` SoQL (`$where/$select/$order/$limit`); keyless, optional `X-App-Token` |

**ArcGIS Hub empty-`q` pitfall:** every Hub portal returns **HTTP 400 for `q=`** and 200 when `q` is omitted (verified 2026-07-25 across aurora, newmarket, york_region, markham, manitoba). `shared/arcgis_hub.py:search_hub_datasets` omits the parameter when the query is empty or whitespace — mirroring the `startindex=0` handling. Before that fix, every "list everything" call (e.g. `aurora_list_categories`) returned `UPSTREAM_ERROR`, which read as an outage. Affects York Region, Alberta, Manitoba and Saskatchewan.

**ArcGIS `where` must never be None:** httpx drops params whose value is `None`, so a `where=None` reaches ArcGIS as *no `where` at all* — and `/query` answers that with HTTP 200 carrying an error 400 "Unable to perform query operation", which surfaces to agents as a bogus `UPSTREAM_ERROR`. `shared/arcgis_hub.py` now coalesces `where or "1=1"` inside both `query_feature_service` and `get_count`, so call sites can pass `str | None` freely. Four Alberta call sites had shipped this bug (verified live against Saskatchewan `Public_Fire_Ban`, 2026-07-26). Same masking class as the empty-`q` pitfall above.

**Toronto TTC GTFS — never pin the download URL:** Toronto republishes the feed under fresh dataset AND resource uuids. A pinned `GTFS_ZIP_URL` constant 404'd and left both TTC tools dead behind an `UPSTREAM_ERROR`. The ZIP is resolved at call time from CKAN `package_show` keyed by the dataset **slug** (`ttc-routes-and-schedules`), which survives republishes. See `toronto/client.py:_resolve_gtfs_zip_url`.

**Alberta static reports (AER ST1/ST3/ST39):** Alberta Energy Regulator publishes well/production/pipeline statistics as static XLSX/TXT files at `static.aer.ca/prd/`. These are **not** a portal technology — they're downloaded and parsed via `shared/parsers.py` (`fetch_and_parse`) and routed through per-tool URL templates. See `docs://alberta/aer-data-guide` for the product slug casing and rotation rules. **511 Alberta v2 JSON API** is an undocumented-but-stable raw-JSON feed (not CKAN envelope) used for road events / winter conditions / cameras.

**BC two-step CKAN→WFS workflow:** Discover datasets via `bc_search_datasets` (CKAN) → get `object_name` + `queryable_via_wfs` via `bc_get_dataset_details` → query geospatial features via `bc_query_features` (WFS). See `docs://bc/wfs-query-guide` resource for full CQL syntax and examples.

**Socrata categories= workaround:** The `/api/catalog/v1?categories=X` parameter is **broken** (returns `resultSetSize=0` for any category on data.novascotia.ca). Use `q=` keyword search + client-side aggregation of `classification.domain_category` instead. Geometry columns (`the_geom`) must be excluded via explicit `$select`; belt-and-suspenders row-level strip handles any API anomaly. NS transport/511 (HTML-only) and NS ArcGIS Hub (novagis, no public no-auth FeatureServers) are deferred.

**Manitoba ArcGIS Hub (geoportal.gov.mb.ca, org mMUesHYPkXjaFGfS):** Hub Search API at `/api/search/v1/collections/all/items` (NOT `/api/v2/datasets` which 404s). `data.manitoba.ca` is unreachable; `mli.gov.mb.ca` (Manitoba Land Initiative) was retired 2022-02-09 — never reference either. **Manitoba 511 v3 key GATED:** account signup + explicit key request at https://www.manitoba511.ca/my511/register; tools return `NOT_CONFIGURED` via `Five11NotConfigured` exception when `MANITOBA_511_KEY` env var absent. River Conditions are live CSV (no FeatureServer backing the web app). See `docs://manitoba/portal-guide` for the full pitfall list.

**Saskatchewan multi-org ArcGIS (geohub.saskatchewan.ca):** THREE separate ArcGIS bases — primary Hub org `zcv98lgAl8xQ04cW` (agriculture/mining/environment), WSA org `7MBdlVpjqbfBhQer` (water infrastructure), and SPSA `gis.saskatchewan.ca/egis` (fire bans). `data.saskatchewan.ca` does NOT exist. WSA_Reservoirs FeatureServer uses **layer 26** (not layer 0 — layer 0 returns empty; spike-confirmed 2026-06-15). FIRE_BAN_LAYERS dispatch: `{"urban":0,"rural":2,"provincial":3,"parks":8}`. Three module-level limiters (_hub_limiter/_wsa_limiter/_spsa_limiter). **Transport deferred:** Saskatchewan Highway Hotline 511 key-gated. **Health deferred:** SHA has no public ArcGIS FeatureServer. **startindex pagination fix** landed in Phase 19 (`shared/arcgis_hub.py:search_hub_datasets`), benefiting York Region, Alberta, Manitoba, and Saskatchewan Hub modules. See `docs://saskatchewan/portal-guide` for the full multi-org architecture.

## Core Rules

**TDD: Red → Green → Refactor.** Write failing tests first. Bug fixes require a reproduction test.

**Every `@tool` must:** use standalone `@tool` from `fastmcp.tools`, include `lang: Literal["en", "fr"]`, return `make_response()`/`make_error()`, have `Use for:` + `Keywords:` in docstring, use module prefix (`boc_`, `parl_`, etc.).

**Every `@tool` must have catch-all error coverage** — enforced by `tests/test_tool_error_handling.py` in the default unit suite. Satisfy it with `@upstream_guard(<api_name>)` beneath `@tool` (preferred — it is additive, so any handlers inside the function still run first), a broad `except Exception`/`httpx.HTTPError`, or delegation to a module helper that has one. **Catching only `httpx.HTTPStatusError` is not enough:** it covers a 500 but not a timeout, a connect error or a malformed body, each of which escapes as a raw `ToolError`. Phase 20.2 found 108 of 271 tools in that state.

**Never decode JSON outside `decode_json()` / `decode_json_bytes()`** (both in `shared/http.py`) — enforced by `tests/test_upstream_error_classification.py`. `json.JSONDecodeError` subclasses `ValueError`, so a raw `response.json()` on an upstream HTML error page gets reported as `INVALID_INPUT` — blaming the caller for someone else's outage, and failing live tests with a misleading code (`assert_live_or_transient` tolerates only `UPSTREAM_ERROR`/`RATE_LIMITED`/`UPSTREAM_UNAVAILABLE`). The helpers raise `httpx.DecodingError`, which is an `HTTPError` but not a `ValueError`, so it reaches the catch-all instead. Phase 20.2 guarded `api_get` alone and left ArcGIS Hub, OGC WFS and Socrata exposed; Phase 20.3 routed all 14 decode sites through the helpers. Use `decode_json(response, url)` for a `Response`, `decode_json_bytes(content, url)` when you hold raw bytes.

**Every client function must:** return `(data, was_cached)`, use `cached_fetch()` + `get_limiter()`, flatten responses aggressively.

**Don't:** add dependencies, modify `server.py` for new modules, put module tests in top-level `tests/`, skip rate limiting, mix refactoring with feature work.

**Integration tests must be able to fail.** Every path through a test in `tests/integration/` must reach an assertion — no one-armed `if "_meta" in data:` guards, no bare `return`, no data-dependent `pytest.skip`. To tolerate a genuine outage, assert the error code instead:

```python
live = assert_live_or_transient(data, "tool_name", "api-name")
if live:
    assert_rows(data, "tool_name")          # refuses empty unless you say why
```

`tests/test_integration_test_quality.py` enforces this in the DEFAULT unit suite. A test that genuinely cannot comply declares `@pytest.mark.tolerates_upstream_error(reason=...)` with a mandatory reason.

**After implementing any tool:** add integration tests in `tests/integration/test_tool_scenarios.py` that call the tool through the MCP Client layer (not client functions directly). Think in sample prompts — what would an agent ask? See `.claude/rules/tests.md` for the pattern.

**Docstring quality is enforced by `test_quality.py` — it will fail your tests if Keywords/Use-for lines are missing.**

## Prompt and Resource Rules

### Every `@prompt` must:
- Use standalone `@prompt` from `fastmcp.prompts` — never `@mcp.prompt`
- Include `lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en"` parameter
- Use module prefix naming: `boc_`, `parl_`, `wx_`, `rcll_`, `drug_`, `ckan_`, etc.
- Have a docstring describing when agents should use this prompt

**Guided workflow prompts** chain multiple tools for complex analysis:
- Return `list[Message]` with user + assistant roles (at least 2 messages)
- First message (user role): asks what the agent wants to analyze
- Second message (assistant role): gives step-by-step instructions with specific tool calls

**Quick lookup prompts** guide a single-tool call:
- Return `str` with tool name and parameter instructions
- Result is treated as a single user message by FastMCP

### Every `@resource` must:
- Use standalone `@resource` from `fastmcp.resources` — never `@mcp.resource`
- Have ZERO function parameters — any parameter (including `lang`) promotes the function to ResourceTemplate and removes it from `resources/list`
- Use type-prefixed URI scheme: `data://`, `docs://`, or `template://`
- Use module-prefixed URI path: e.g., `data://boc/currency-codes`

**URI scheme conventions:**
- `data://` — JSON catalogs: return `json.dumps(...)`. Bilingual content embedded inline (both `en`/`fr` in same JSON).
- `docs://` — Markdown guides: return raw markdown string. Both languages can be in the same document.
- `template://` — Markdown templates: return markdown with `{placeholder}` syntax for agents to fill in.

**Resource content rules:**
- `data://` resources must be valid JSON — never return Python dict directly
- Bilingual content belongs inline, not behind a `lang` parameter
- Static reference data (e.g., neighbourhood lists) should be embedded, not fetched via HTTP

### Weather module exception:
- `prompts.py` lives at the top-level `weather/` (not in sub-modules). FileSystemProvider scans recursively — one file covers all 8 sub-modules and avoids duplicates.
