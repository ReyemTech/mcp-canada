# Domain Pitfalls: StatCan API + SQLite MCP Integration

**Project:** mcp-canada v1.1 — Statistics Canada + Shared Datastore
**Researched:** 2026-04-07
**Domain:** Government REST/SDMX API integration; SQLite-backed MCP tools

---

## Critical Pitfalls

Mistakes that cause agent failures, security vulnerabilities, or mandatory rewrites.

---

### Pitfall 1: SQL Injection via User-Controlled Table Names

**What goes wrong:** The LLM or agent provides a table name (or column name) as a string. If that string is interpolated directly into `CREATE TABLE`, `INSERT INTO`, or `SELECT FROM` SQL statements — rather than passed as a parameterized value — an attacker or a confused agent can execute arbitrary SQL. Table and column names cannot be parameterized with `?` placeholders in sqlite3; they must be interpolated. This makes them the most dangerous input surface.

Anthropic's own reference SQLite MCP server had this exact vulnerability (CVE reported in GitHub issue #3314, #1348). The repository was archived rather than patched.

**Why it happens:** Developers use `?` placeholders for values but forget that table/column identifiers require a different sanitization path. A statement like `f"SELECT * FROM {table_name}"` is fully injectable if `table_name` comes from tool arguments.

**Consequences:** An agent could be prompted (via stored prompt injection or confused reasoning) to pass a table name like `real_table; DROP TABLE real_table; --`, wiping stored data. In the worst case, an adversary pre-seeds a row with a malicious table name and an agent later reads and replays it.

**Prevention:**
- Allowlist table names against a strict regex: `^[a-zA-Z_][a-zA-Z0-9_]{0,63}$`. Reject anything that does not match before building any SQL string.
- Use Python's `sqlite3` identifier quoting for unavoidable interpolation: wrap identifiers in double-quoted strings and escape embedded double quotes (`identifier.replace('"', '""')`).
- Never accept raw SQL strings from tool arguments (no `execute_sql(query: str)` that runs arbitrary DDL).
- Log and test with adversarial table names in the unit test suite.

**Warning signs:** Tool argument named `table_name`, `column`, or `schema` that flows directly into an f-string SQL construction without a regex check first.

**Phase:** Datastore module implementation (SQLite tools phase). This must be correct from the first commit — retrofitting is error-prone.

---

### Pitfall 2: Blocking the asyncio Event Loop with sqlite3

**What goes wrong:** Python's `sqlite3` module is synchronous and blocking. Calling it directly inside an `async` function stalls the entire asyncio event loop for the duration of the database operation. In an MCP server handling concurrent tool calls, this means all other in-flight requests (including live API calls) block behind a SQLite write.

**Why it happens:** `sqlite3.connect()` returns a synchronous connection. Developers assume they can `await` around it or that it is non-blocking because FastMCP is async. It is not.

**Consequences:** A slow `INSERT` (e.g., bulk-inserting 1,000 StatCan observation rows) can starve other tool calls for hundreds of milliseconds. Under concurrent agent usage the server appears to hang intermittently.

**Prevention:**
- Wrap all SQLite calls in `asyncio.get_event_loop().run_in_executor(None, ...)` to offload to the default `ThreadPoolExecutor`.
- Create one SQLite connection per executor thread, not a single global connection (sqlite3's default threading mode is `check_same_thread=True` for a reason — connections are not thread-safe by default).
- Enable WAL mode (`PRAGMA journal_mode=WAL`) on first connection to allow concurrent reads during writes.
- Set a `timeout` on `sqlite3.connect()` (e.g., 30 seconds) so a locked database produces a clear error rather than an infinite hang.

**Warning signs:** Any `sqlite3.connect(...)` call appearing directly inside an `async def` function body without wrapping in `run_in_executor`.

**Phase:** Datastore module implementation (SQLite client layer). Must be enforced before any tools are written on top.

---

### Pitfall 3: SSL verify=False Applied Globally

**What goes wrong:** StatCan's SSL certificate chain fails verification in some Python environments because intermediate certificates are not sent by the server. The quick fix — `verify=False` on the httpx client — disables TLS verification for all connections made through that client, not just StatCan endpoints.

The existing mcp-statcan sets `VERIFY_SSL = False` globally in a constants file, which applies to every outbound request the module makes.

**Why it happens:** `httpx.AsyncClient(verify=False)` is a one-line fix. The implications (MITM vulnerability for all requests through that client) are easy to miss.

**Consequences:** If the global `httpx.AsyncClient` shared across modules is configured with `verify=False`, every API call in the entire mcp-canada server — Bank of Canada, Weather, Drug Database — loses TLS verification. An on-path attacker can intercept and alter any response.

**Prevention:**
- Create a separate `httpx.AsyncClient` instance specifically for StatCan requests, scoped to the statcan module's client.py. Never modify the shared lifespan client.
- Attempt fix via certifi first: `httpx.AsyncClient(verify=certifi.where())`. certifi is already a transitive dependency of httpx.
- If certifi does not resolve the chain issue, pin StatCan's specific CA certificate (downloaded from StatCan or extracted from the chain) and pass it as the `verify` path.
- If cert bundling fails after genuine effort, apply `verify=False` only to the statcan-scoped client and annotate it prominently with the reason and a TODO to revisit.
- Unit tests must mock the httpx client at the statcan module level, not the global level, to catch accidental bleed-through.

**Warning signs:** Any `verify=False` appearing outside `mcp_canada/modules/statcan/client.py`. Any change to the shared lifespan client in `server.py` to accommodate StatCan.

**Phase:** StatCan client implementation (first phase of statcan module). Must be resolved before integration tests run.

---

### Pitfall 4: Using getAllCubesList Instead of getAllCubesListLite for Discovery

**What goes wrong:** StatCan's `getAllCubesList` endpoint returns comprehensive metadata including all dimensions and footnotes for all 80,000+ tables. `getAllCubesListLite` returns the same inventory without dimension/footnote details.

If `getAllCubesList` is used for cube search/discovery (e.g., to populate a searchable catalog), the response payload is orders of magnitude larger. In an MCP context window it is unusable — it will overflow the agent's context and may cause hallucination.

**Why it happens:** `getAllCubesList` sounds like the natural endpoint for "get all cubes." The word "Lite" implies incomplete data. But for discovery purposes, the Lite endpoint provides everything needed (productId, title, date range, frequency, subject codes).

**Consequences:** Agents receive a truncated or errored response. If the response is not truncated, the agent's context window fills with cube metadata, leaving no room for the actual question or the tool result. mcp-statcan documents "Context overflow may cause data fabrication" as a known consequence.

**Prevention:**
- Always use `getAllCubesListLite` for catalog/search purposes.
- Cache the Lite catalog for 1 hour (TTL matches StatCan's release cadence — new tables appear at 08:30 EST).
- When a tool needs dimension details for a specific cube, fetch `getCubeMetadata/{pid}` on demand for that single cube, not the full catalog.
- Set an explicit truncation limit on search results returned to agents (e.g., top 20 matches).

**Warning signs:** Any tool that fetches the full cube list and returns it directly to the agent without filtering. Response payloads exceeding ~50KB being passed through a tool result.

**Phase:** StatCan WDS tools implementation (catalog/search tools).

---

## Moderate Pitfalls

Mistakes that cause incorrect data, wasted API quota, or poor agent UX without causing a complete failure.

---

### Pitfall 5: WDS List-Wrapped Response Format Not Checked for FAILED Status

**What goes wrong:** The WDS REST API returns most responses as JSON with two fields: `"status": "SUCCESS"` or `"status": "FAILED"`, and `"object"` containing the actual data. Some endpoints — particularly `getDataFromCubePidCoordAndLatestNPeriods` — return a **list** of these status-object pairs, one per requested coordinate.

If code only checks the HTTP status code (200 OK is returned even for application-level failures) and assumes the response body is always the data, it silently returns corrupt or empty results to the agent.

A specific edge case: Census tables use zero as a filler for suppressed cells, but the API returns `responseStatusCode: 2` (rounded to zero) rather than a failure — meaning a zero value is valid data, not an error.

**Why it happens:** Developers are accustomed to HTTP status codes signaling errors. The WDS API uses HTTP 200 for both success and application-level failures.

**Prevention:**
- Always check `response["status"] == "SUCCESS"` before accessing `response["object"]`.
- For list responses, iterate all items and collect both successes and failures; surface failures as partial errors in the `_meta` envelope rather than silently dropping them.
- Treat `responseStatusCode: 2` (zero-filled Census data) as valid data — do not filter it out as an error.
- Include unit tests for the FAILED status case using a fixture that returns `{"status": "FAILED", "object": "Not available"}`.

**Warning signs:** Client functions that access `raw["object"]` without first branching on `raw.get("status")`. Integration tests that only verify happy-path responses.

**Phase:** StatCan WDS client implementation (all client functions).

---

### Pitfall 6: SDMX lastNObservations + Date Range = HTTP 406

**What goes wrong:** The StatCan SDMX API does not support combining `lastNObservations` with `startPeriod` or `endPeriod` in the same request. Doing so returns an HTTP 406 (Not Acceptable). This is a StatCan-specific constraint — standard SDMX implementations allow this combination.

mcp-statcan documents this explicitly as a known limitation.

**Why it happens:** The SDMX standard permits both parameter types simultaneously. Developers assume StatCan follows the standard. The error (406) is not self-explanatory.

**Prevention:**
- In the SDMX client, enforce mutual exclusion: if `startPeriod` or `endPeriod` is provided, clear `lastNObservations`. If `lastNObservations` is provided, clear date range parameters. Document this constraint in the tool docstring where agents will see it.
- Return a structured error (`INVALID_INPUT`) if a caller provides both, with an explanatory message.
- Add a unit test that verifies the mutual exclusion logic at the client level.

**Warning signs:** Any SDMX client function that accepts all four parameters without enforcing constraints. Integration test failures with HTTP 406 responses.

**Phase:** StatCan SDMX client implementation.

---

### Pitfall 7: WDS Coordinate Padding Not Applied

**What goes wrong:** WDS endpoints that accept coordinates (e.g., `getDataFromCubePidCoordAndLatestNPeriods`) require coordinates padded to exactly 10 dimension positions separated by dots: `1.3.1.0.0.0.0.0.0.0`. A coordinate like `1.3.1` without padding returns an error or empty result.

**Why it happens:** The dimension count varies by table (some have 3 dimensions, others have 9). Developers pass the "natural" coordinate without padding because the API docs show short examples that appear to work in browser demos but fail programmatically.

**Prevention:**
- Implement a `pad_coordinate(coord: str, length: int = 10) -> str` utility that splits on `.`, pads with zeros to 10 elements, and rejoins. Apply it to every coordinate before constructing a WDS URL.
- Unit-test the padding function with coordinates of 1, 3, 7, and 10 dimensions.

**Warning signs:** Raw user-provided coordinate strings appearing in WDS URLs without a padding step.

**Phase:** StatCan WDS client implementation (coordinate-based endpoints).

---

### Pitfall 8: WDS Data Unavailability Window Not Handled

**What goes wrong:** The WDS API locks tables and returns HTTP 409 for many endpoints between midnight and 08:30 EST while updating data. An MCP server that treats 409 as a generic server error will surface a confusing error to agents during this window.

At 25 requests/second per IP, the rate limit is also higher than it looks — burst requests from `asyncio.gather()` over multiple vectors can hit it in under a second.

**Why it happens:** 409 is an unusual status code (Conflict in REST conventions). Developers add it to retry logic, but retrying during a 30-minute maintenance window burns rate limit quota and delays responses without helping.

**Prevention:**
- Add 409 to the `is_retryable` check in `shared/http.py` for StatCan-specific clients only — but cap retries to 1 and wait at least 60 seconds before retrying (not the default exponential backoff starting at 1 second).
- Alternatively, surface a clear `UPSTREAM_UNAVAILABLE` error code with a message explaining the maintenance window, so agents can inform users.
- Cap concurrent StatCan requests via the existing `TokenBucket` rate limiter. 25 req/s is the per-IP limit; configure the statcan limiter at 20 req/s to stay safely below it.
- Add `429` to the retryable set for StatCan; the API can throttle under load even within the rate limit.

**Warning signs:** `asyncio.gather()` over a large list of vector fetches without rate limiting. 409 responses being surfaced as generic `UPSTREAM_ERROR`.

**Phase:** StatCan WDS client implementation (constants and error handling).

---

### Pitfall 9: Cache Key Collisions Between WDS and SDMX

**What goes wrong:** The shared `cached_fetch()` in `shared/cache.py` uses a single `SimpleMemoryCache` instance. If StatCan WDS and SDMX tool responses are cached with keys that do not include the API type prefix, a WDS response for product `14100287` could be returned when an SDMX query for the same product ID is made.

**Why it happens:** Developers copy the Bank of Canada cache key pattern (`boc:{path}?{params}`) but forget to make the prefix unique per API type.

**Prevention:**
- Prefix all statcan cache keys with the API type: `statcan_wds:{...}` and `statcan_sdmx:{...}`.
- Use the full URL path (not just the product ID) in cache keys for StatCan endpoints, since the same product ID can be requested with different coordinate or time-range parameters.

**Warning signs:** Cache keys constructed from only a product ID or vector ID without including query parameters.

**Phase:** StatCan client implementation (both WDS and SDMX clients).

---

### Pitfall 10: SDMX OR-Key Geography Labels Are Wrong

**What goes wrong:** When using the `+` operator in SDMX dimension keys to request multiple geographies (e.g., `...01+02+03...`), the API returns data but labels the geography dimension incorrectly. This is a documented bug in StatCan's SDMX implementation (acknowledged in mcp-statcan).

**Why it happens:** The OR-key syntax is part of the SDMX standard but StatCan's label resolution for multi-value dimension keys is broken server-side.

**Consequences:** Agents receive data with geography codes (`01`, `02`) instead of human-readable labels (`Nova Scotia`, `Prince Edward Island`), making the output harder to interpret and potentially misleading.

**Prevention:**
- Avoid OR-key multi-geography queries in the SDMX client implementation. Use wildcard (omit the dimension value) to get all geographies and filter client-side, or make individual requests per geography.
- If OR-key must be supported, document the broken-label behavior in the tool docstring so agents know to cross-reference codes.
- Fetch and resolve geography codes from the WDS codeset endpoint (`getCodeSets/{pid}`) when building SDMX responses.

**Warning signs:** SDMX query construction that joins dimension values with `+` for the geography dimension.

**Phase:** StatCan SDMX client implementation.

---

## Minor Pitfalls

Issues that degrade developer experience or test reliability without affecting production behavior.

---

### Pitfall 11: SQLite Database Path Not Configurable

**What goes wrong:** If the datastore module hardcodes the SQLite file path (e.g., `/tmp/mcp_canada.db` or `./data.db`), tests create real files in the working directory, tests cannot run in parallel with isolated databases, and users cannot control where data is stored.

**Prevention:**
- Accept the database path as a parameter to the datastore client (defaulting to a platform-appropriate location, e.g., `~/.mcp-canada/datastore.db`).
- In tests, use `tmp_path` (pytest's temporary directory fixture) to create an isolated database per test.
- Never hardcode a path in `constants.py` — use an environment variable or a constructor argument.

**Phase:** Datastore module implementation.

---

### Pitfall 12: Integration Tests Hit Real StatCan APIs Without Timeout Safeguards

**What goes wrong:** StatCan APIs can be slow (3-10 seconds per request is common for metadata endpoints). Integration tests without explicit timeouts hang indefinitely when StatCan is in its maintenance window or under load, blocking CI pipelines.

**Prevention:**
- Mark all StatCan integration tests with `@pytest.mark.integration` (already excluded from default CI runs).
- Set `--timeout=120` in pytest config for integration runs.
- Add per-test timeouts via `pytest-timeout` markers for StatCan-specific tests (e.g., `@pytest.mark.timeout(60)`).
- Document in `tests/integration/README.md` that StatCan tests will fail between midnight and 08:30 EST.

**Phase:** Test implementation for statcan module.

---

### Pitfall 13: Flattening WDS Scalar Factor Incorrectly

**What goes wrong:** WDS data points include a `scalar` field (multiplier code: 0=units, 3=thousands, 6=millions, 9=billions). The actual value in the `value` field is pre-scaled — it already has the decimal applied — but the scalar is a separate code that must be looked up via `getCodeSets`. If a tool displays the raw `value` without noting the scalar, the agent may interpret GDP in millions as a unit-less count.

**Prevention:**
- Always fetch and include the scalar factor label (not just the code) in the flattened response.
- Cache the code sets for 24 hours (they change infrequently).
- Include the scalar label in the flattened `ObservationRow` schema for StatCan responses.

**Phase:** StatCan WDS client implementation (observation flattening).

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| SQLite datastore tools | SQL injection via table/column names | Regex allowlist before any SQL string construction |
| SQLite client layer | Blocking event loop | All sqlite3 calls via `run_in_executor` |
| StatCan SSL handling | Global verify=False bleed | Scoped per-module httpx client; certifi first |
| WDS cube catalog tools | getAllCubesList payload overflow | Use Lite endpoint + cache + truncated results |
| WDS observation tools | FAILED status silently ignored | Check `status == "SUCCESS"` before `object` access |
| WDS coordinate tools | Missing coordinate padding | `pad_coordinate()` utility applied before every WDS URL |
| SDMX client | lastNObs + date range = 406 | Enforce mutual exclusion in client; document in docstring |
| SDMX multi-geography | OR-key labels broken | Avoid `+` on geography dimension; filter client-side |
| Cache keys | WDS/SDMX key collisions | `statcan_wds:` and `statcan_sdmx:` prefixes |
| StatCan integration tests | Tests hang in maintenance window | `@pytest.mark.timeout`, document 00:00-08:30 EST window |
| Observation flattening | Scalar factor misinterpretation | Include scalar label in flattened row; cache code sets |
| SQLite path | Hardcoded paths break parallel tests | Configurable path via constructor; `tmp_path` in tests |

---

## Sources

- Statistics Canada WDS User Guide: https://www.statcan.gc.ca/en/developers/wds/user-guide (rate limits, 409 window, coordinate format, response status pattern, scalar factors)
- Statistics Canada SDMX User Guide: https://www.statcan.gc.ca/en/developers/sdmx/user-guide (lastNObservations + date range constraint, OR-key behavior, response formats)
- mcp-statcan known issues (Aryan Jhaveri): https://github.com/Aryan-Jhaveri/mcp-statcan (SSL verify=False, OR-key label bug, context overflow hallucination risk, 406 on combined SDMX params)
- SQL injection in MCP SQLite server (GitHub issue #3314): https://github.com/modelcontextprotocol/servers/issues/3314
- Datadog Security Labs — MCP SQL injection case study: https://securitylabs.datadoghq.com/articles/mcp-vulnerability-case-study-SQL-injection-in-the-postgresql-mcp-server/
- Trend Micro — SQLite MCP vulnerability analysis: https://www.trendmicro.com/en_us/research/25/f/why-a-classic-mcp-server-vulnerability-can-undermine-your-entire-ai-agent.html
- Python sqlite3 thread safety: https://ricardoanderegg.com/posts/python-sqlite-thread-safety/
- SQLite WAL concurrency: https://iifx.dev/en/articles/17373144
- httpx SSL documentation: https://www.python-httpx.org/advanced/ssl/
