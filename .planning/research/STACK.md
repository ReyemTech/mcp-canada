# Technology Stack: StatCan + Datastore Milestone

**Project:** mcp-canada v1.1 — Statistics Canada integration
**Researched:** 2026-04-07
**Scope:** Additive stack decisions only. Existing stack (FastMCP 3.2.x, httpx, pydantic, aiocache, tenacity) is fixed.

---

## Constraint Recap (from PROJECT.md)

The dependency policy is explicit: no new dependencies unless the stdlib cannot solve the problem.
The existing stack already handles HTTP, caching, retry, and validation.
Two new concerns require a decision: **async SQLite access** and **SSL certificate repair**.
SDMX XML parsing is a third concern but resolves to stdlib.

---

## Decision 1: SDMX XML Parsing — Use `xml.etree.ElementTree` (stdlib)

**Recommendation:** `xml.etree.ElementTree` from the standard library. No new dependency.

**Rationale:**

StatCan's SDMX endpoint returns two formats via content negotiation:
- `application/vnd.sdmx.data+json` — SDMX-JSON (preferred for data queries)
- `application/vnd.sdmx.genericdata+xml` — SDMX-ML 2.1 (XML, needed for structure/metadata)

For **data queries**, request SDMX-JSON. The response is standard JSON parseable by `httpx`'s `.json()` method — no XML parser needed at all. This eliminates the hardest XML parsing path entirely.

For **structure queries** (codelists, dataflow definitions, concept schemes), the response is SDMX-ML XML. These documents are small metadata payloads (kilobytes, not megabytes). `xml.etree.ElementTree` handles them without performance issues. The Python 3.12 C-accelerated implementation is fast enough for payloads this size.

**Why not lxml:** lxml is faster and has better XPath support, but it requires a compiled C extension and adds a binary dependency. For small SDMX structure documents at metadata-fetch frequency (24hr cache), the performance difference is immaterial. The project's dependency policy prohibits adding it.

**Why not pandasdmx / sdmx1:** These are full SDMX client libraries that bring in lxml, pandas, and a large dependency tree. They solve a general problem; we only need to extract specific fields from known SDMX response shapes. Over-engineered for the task.

**Namespace handling pattern:**

StatCan SDMX-ML uses `message:`, `generic:`, and `structure:` namespace prefixes. ElementTree requires explicit namespace registration. The pattern used throughout StatCan's SDMX responses:

```python
import xml.etree.ElementTree as ET

SDMX_NS = {
    "message": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "generic": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic",
    "structure": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
    "common": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
}

root = ET.fromstring(xml_bytes)
datasets = root.findall("message:DataSet/generic:Series", SDMX_NS)
```

Define `SDMX_NS` once in `constants.py` and import it in `client.py`. Never hardcode namespace URIs inline.

**Confidence:** HIGH — stdlib is always available, StatCan SDMX-JSON path removes XML from data queries entirely, XML is only needed for small metadata responses.

---

## Decision 2: Async SQLite — Add `aiosqlite` (one new dependency, justified)

**Recommendation:** `aiosqlite==0.22.1` (December 2025 release). This is the sole new dependency addition.

**Rationale:**

The datastore module is a FastMCP async server component. All tool functions are `async def`. The stdlib `sqlite3` module is synchronous and blocking — calling it directly in an async context blocks the event loop, freezing all concurrent tool calls. This is not acceptable.

The options are:

| Approach | Assessment |
|----------|-----------|
| `sqlite3` directly in `async def` | Blocks event loop. Breaks concurrent use. NOT acceptable. |
| `asyncio.run_in_executor(None, sqlite3_call)` | Works but verbose. Error-prone for connection/cursor lifecycle. |
| `aiosqlite` | Clean async wrapper over sqlite3's threading model. Mirrors sqlite3 API. |
| SQLAlchemy async | ORM overhead, 7+ transitive dependencies. Explicitly prohibited. |
| Tortoise ORM / SQLModel | Same problem. No ORM. |

`aiosqlite` runs sqlite3 in a dedicated background thread with a request queue, exposing an `async with` interface that mirrors stdlib. Zero transitive dependencies. MIT licensed. Actively maintained (v0.22.1, December 2025). Python >=3.9 (project requires >=3.12, compatible).

**The stdlib `run_in_executor` alternative is rejected** because: managing thread-pool connection lifecycles across multiple concurrent tool calls is error-prone, the code would be verbose and non-idiomatic, and `aiosqlite` is exactly the right abstraction at ~800 lines of pure Python.

**Usage pattern (consistent with existing module client pattern):**

```python
import aiosqlite

async def execute_query(db_path: str, sql: str, params: tuple = ()) -> list[dict]:
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
```

**No connection pool needed.** SQLite is file-local. `aiosqlite` serializes writes via its internal thread queue. Open connection per operation; let context manager close it.

**No ORM, no migrations framework.** Tools create tables explicitly with `CREATE TABLE IF NOT EXISTS`. Schema is agent-controlled. This is deliberate: the datastore is a scratch space for agents, not a versioned application database.

**Confidence:** HIGH — aiosqlite is the established stdlib wrapper for this exact use case. Version verified against PyPI.

---

## Decision 3: SSL Certificate Handling — Tiered Strategy

**Recommendation:** Attempt fix with `truststore` first; fall back to scoped `verify=False` on the StatCan client only if truststore does not resolve it.

**Background:**

StatCan's endpoint `https://www150.statcan.gc.ca/t1/wds/` uses a certificate chain that fails verification in Python's certifi bundle in some environments. The root cause is typically a missing intermediate CA certificate that Canadian government infrastructure uses. The existing mcp-statcan reference implementation globally disables SSL (`VERIFY_SSL = False`) — a practice we must avoid for a published package.

**Tier 1 — Try `truststore` first (preferred, no new dependency if available):**

`truststore` 0.10.4 (August 2025) exposes the OS native trust store via an `ssl.SSLContext`. macOS, Windows, and Linux all include Canada's federal PKI intermediate CAs in their system trust stores when properly updated. If the system store resolves StatCan's chain, no cert bundle addition is needed.

```python
import ssl
import truststore
import httpx

ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
async with httpx.AsyncClient(verify=ctx) as client:
    ...
```

`truststore` requires Python 3.10+ (project requires 3.12 — compatible). It has no transitive dependencies. Version 0.10.4 is current.

**However:** `truststore` is a new dependency. The project policy says "no new dependencies." Add it only after confirming in Phase implementation that certifi alone fails and truststore resolves it. Do NOT add it speculatively.

**Tier 2 — Scoped `verify=False` on StatCan client only (fallback, not preferred):**

If truststore does not resolve the chain issue, scope `verify=False` to the StatCan httpx client instance only — not globally. This is the fallback, not the default.

```python
# In statcan/client.py only — never in shared/http.py
_STATCAN_SSL = False  # See: constants.STATCAN_VERIFY_SSL

async def _statcan_get(path: str, ...) -> tuple[Any, bool]:
    async with httpx.AsyncClient(verify=_STATCAN_SSL, timeout=30.0) as http:
        ...
```

The constant `STATCAN_VERIFY_SSL` must be defined in `constants.py` and documented with the reason. This makes the disable explicit, traceable, and auditable — not buried in ad-hoc code.

**What NOT to do:**

- Never set `verify=False` in the shared `http.py` utility (would disable SSL for all modules)
- Never use `truststore.inject_into_ssl()` in library code (documented as application-only API; using it in a library causes import-time side effects for consumers)
- Never add a pinned StatCan certificate to the bundle — cert pinning breaks silently when they rotate certs, which is worse than the current failure mode

**Decision protocol during implementation:**

```
1. Test with default httpx (certifi) — does it work? → done, no change needed
2. Test with truststore.SSLContext — does it work? → add truststore dependency
3. Neither works? → use scoped verify=False with STATCAN_VERIFY_SSL constant
```

**Confidence:** MEDIUM — truststore approach is well-documented for httpx; whether it resolves StatCan's specific chain issue requires empirical verification during implementation. The fallback is safe and well-scoped.

---

## Decision 4: SDMX-JSON vs SDMX-XML for Data Queries — Prefer JSON

**Recommendation:** Request `application/vnd.sdmx.data+json` for all data (observation) queries. Reserve XML parsing for structure/metadata queries only.

**Rationale:**

StatCan's SDMX REST API supports content negotiation. The data endpoint returns SDMX-JSON when the `Accept` header is set to `application/vnd.sdmx.data+json`. This is:
- Directly parseable by `httpx.Response.json()`
- Structurally simpler than SDMX-ML for observation data
- Consistent with the existing module pattern (all other modules parse JSON)

SDMX-ML structure responses (codelists, dataflow definitions) are XML-only — no JSON alternative. That is the only path where ElementTree is required.

**Header to set in StatCan client constants:**

```python
SDMX_DATA_HEADERS = {"Accept": "application/vnd.sdmx.data+json;version=1.0.0"}
SDMX_STRUCT_HEADERS = {"Accept": "application/vnd.sdmx.structure+json;version=1.0.0"}
```

Check whether StatCan supports `structure+json` during implementation. If yes, XML parsing becomes optional entirely. If no, ElementTree handles it.

**Confidence:** MEDIUM — StatCan SDMX user guide confirms JSON data format exists; whether structure queries support JSON requires implementation-time verification.

---

## Decision 5: StatCan WDS Rate Limiting — 25 req/s per IP

**Recommendation:** Use existing `get_limiter()` from `shared/rate_limiter.py` with `RATE_LIMIT = 20` (conservative, below the 25 req/s documented limit).

**Background:**

StatCan WDS documentation specifies: server limit of 50 req/s total, individual IP limit of 25 req/s. Set the module rate to 20 req/s to stay safely under the IP limit with headroom for burst.

```python
# statcan/constants.py
RATE_GROUP = "statcan"
RATE_LIMIT = 20  # req/s; StatCan IP limit is 25, leave headroom
```

The SDMX endpoint has no documented rate limit. Apply the same `RATE_GROUP = "statcan"` to share the token bucket across both WDS and SDMX calls — they hit the same server infrastructure.

**Confidence:** HIGH — rate documented in WDS User Guide. Using existing rate_limiter infrastructure requires no changes.

---

## Decision 6: StatCan Cache TTLs

**Recommendation (from PROJECT.md, confirmed against WDS docs):**

```python
# statcan/constants.py
CACHE_TTL_CUBE_LIST = 3600        # 1hr — getAllCubesList changes infrequently
CACHE_TTL_METADATA  = 86400       # 24hr — getCubeMetadata is stable
CACHE_TTL_OBS       = 3600        # 1hr — observations update daily at 08:30 EST
```

WDS docs confirm data updates occur daily at 08:30 EST and endpoints may return HTTP 409 during the 00:00–08:30 maintenance window. The client should handle 409 as a transient error (retry with backoff via tenacity) rather than propagating it as a tool error.

**Confidence:** HIGH — directly from WDS User Guide.

---

## What NOT to Add

| Temptation | Verdict | Reason |
|------------|---------|--------|
| `lxml` | No | Compiled binary dep; stdlib ET sufficient for small SDMX metadata payloads |
| `pandasdmx` / `sdmx1` | No | Full SDMX client with pandas/lxml dep tree; over-engineered |
| `pandas` | No | Not needed; output is flat dicts/lists for pydantic models |
| SQLAlchemy / SQLModel / Tortoise | No | ORM; explicitly prohibited by project constraints |
| `aiohttp` | No | httpx already present; two async HTTP clients is incoherent |
| `requests` | No | Sync; wrong execution model for FastMCP async tools |
| `truststore.inject_into_ssl()` | No | Library-unsafe; causes import-time global side effects |
| New HTTP retry library | No | `tenacity` already handles retries |
| `pytest-httpx` | Yes (dev only) | Already used in existing test suite for mocking httpx |

---

## Summary Table

| Component | Approach | New Dep? | Confidence |
|-----------|----------|----------|------------|
| SDMX data queries | SDMX-JSON via `Accept` header + `httpx.Response.json()` | No | MEDIUM |
| SDMX structure/metadata | `xml.etree.ElementTree` (stdlib) | No | HIGH |
| Async SQLite | `aiosqlite==0.22.1` | **Yes — one justified exception** | HIGH |
| SSL — primary fix | `truststore==0.10.4` via `truststore.SSLContext` | Yes (conditional) | MEDIUM |
| SSL — fallback | Scoped `verify=False` in statcan client only | No | HIGH |
| Rate limiting | Existing `get_limiter()`, `RATE_LIMIT=20` | No | HIGH |
| Caching | Existing `cached_fetch()`, new TTL constants | No | HIGH |
| Response envelope | Existing `make_response()` / `make_error()` | No | HIGH |
| HTTP retries | Existing `tenacity` in `shared/http.py` | No | HIGH |

---

## Installation Delta

```bash
# Only if aiosqlite is approved and truststore resolves SSL:
uv add aiosqlite truststore

# Minimum guaranteed addition:
uv add aiosqlite
```

Add `aiosqlite>=0.22.0` to `[project.dependencies]` in `pyproject.toml`.
Add `truststore>=0.10.0` only after empirical confirmation it resolves StatCan SSL.

---

## Sources

- [StatCan WDS User Guide](https://www.statcan.gc.ca/en/developers/wds/user-guide) — rate limits, endpoint list, response structure, maintenance window
- [StatCan SDMX User Guide](https://www.statcan.gc.ca/en/developers/sdmx/user-guide) — format negotiation, endpoint structure
- [aiosqlite PyPI](https://pypi.org/project/aiosqlite/) — version 0.22.1, December 2025
- [aiosqlite GitHub](https://github.com/omnilib/aiosqlite) — threading model, API reference
- [truststore PyPI](https://pypi.org/project/truststore/) — version 0.10.4, August 2025
- [httpx SSL docs](https://www.python-httpx.org/advanced/ssl/) — verify parameter options, custom ssl.SSLContext usage
- [Python xml.etree.ElementTree docs](https://docs.python.org/3/library/xml.etree.elementtree.html) — namespace parsing, C-accelerated implementation
- [mcp-statcan reference](https://github.com/Aryan-Jhaveri/mcp-statcan) — confirms SSL is globally disabled, SDMX-JSON utility module exists
