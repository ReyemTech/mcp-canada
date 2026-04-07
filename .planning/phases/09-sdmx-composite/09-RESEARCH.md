# Phase 9: SDMX + Composite - Research

**Researched:** 2026-04-07
**Domain:** StatCan SDMX REST API (structure + data + vector endpoints) + composite fetch-and-store tool
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Support both raw SDMX key strings AND named dimension dicts
- Raw key: agent passes `"1.2+3.."` directly (matches SDMX spec)
- Named dict: agent passes `{"geography": ["Ontario"], "age": "all"}` — tool translates to key using codelist from `sc_get_sdmx_structure`
- Raw key is the primary interface; named dict is a convenience layer
- `sc_get_sdmx_structure` response includes a suggested key example (e.g., `"1...."`) showing dimension positions so agents can copy-paste into `sc_get_sdmx_data`
- Mutual exclusion enforced: `lastN` and date range (`start_period`/`end_period`) cannot be used simultaneously — return `INVALID_INPUT` error if both provided
- `sc_fetch_vectors_to_store` requires agent-specified `table_name` parameter (no auto-naming)
- Table name follows module prefix convention from Phase 7: `statcan_cpi_2024`, `statcan_gdp_quarterly`, etc.
- If table already exists: append new rows (consistent with Phase 7 append-only decision)
- Table created on first call if it doesn't exist — uses `ds_create_table` internally
- Schema inferred from fetched data (consistent with Phase 7 type inference decision)
- SDMX REST base URL: `https://www150.statcan.gc.ca/t1/wds/sdmx/statcan/rest/`

### Claude's Discretion

- SDMX XML namespace handling pattern (ElementTree vs JSON content negotiation)
- Whether `sc_get_sdmx_data` and `sc_get_sdmx_vector_data` share a common flattening helper
- How to serialize the named dimension dict -> SDMX key translation
- Error handling for invalid SDMX key syntax

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SC-10 | Agent can fetch the dimension structure (codelists) for a table via SDMX | SDMX structure endpoint URL pattern; XML parsing with ElementTree; namespace constants; codelist extraction approach documented below |
| SC-11 | Agent can retrieve server-side filtered observations using SDMX key syntax with date range and lastN support | SDMX data endpoint URL; SDMX-JSON parsing; key syntax rules; mutual exclusion enforcement; flattening helper pattern documented below |
| SC-12 | Agent can retrieve observations for a single vector via SDMX with date range filtering | SDMX vector endpoint URL pattern; same SDMX-JSON parsing path as SC-11; reuses same flattening helper |
| SC-15 | Agent can fetch multiple vectors for a date range and store results directly to the shared datastore in one tool call | Composite tool calls `get_bulk_vector_data` then `datastore.create_table` + `datastore.insert_rows`; schema inference from `_infer_sqlite_type`; table name validation via `_validate_identifier` |
</phase_requirements>

---

## Summary

Phase 9 adds three SDMX tools plus one composite tool, all implemented as additions to the existing `statcan/client.py` and `statcan/tools.py`. The SDMX tools hit a separate base URL (`/sdmx/statcan/rest/`) rather than the WDS base URL. Structure queries return SDMX 2.1 XML (must parse with `xml.etree.ElementTree`); data and vector queries return SDMX-JSON when the `Accept: application/json` header is sent.

The composite tool (`sc_fetch_vectors_to_store`) bridges `statcan/client.py` and `datastore/client.py`: it calls the already-implemented `get_bulk_vector_data` function, then calls `create_table` (if needed) and `insert_rows` from the datastore client. The datastore client is already production-ready and requires no changes.

**Primary recommendation:** Use `Accept: application/json` for all SDMX data/vector queries; use stdlib `xml.etree.ElementTree` for structure XML. No new dependencies needed.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `xml.etree.ElementTree` | stdlib | Parse SDMX 2.1 XML structure responses | Already in stdlib; no new dep; sufficient for codelist extraction from known namespace structure |
| `httpx.AsyncClient` | existing | HTTP requests to SDMX endpoints | Same pattern as WDS client; `_make_statcan_client()` reused |
| `aiosqlite` | existing | SQLite writes in composite tool | Already used by datastore module; no new dep |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `cached_fetch` | shared | Cache SDMX structure responses | Structure rarely changes; cache with `CACHE_TTL_META` (24hr); use `statcan_sdmx:` prefix |
| `get_limiter` | shared | Rate limiting for SDMX requests | Same `RATE_GROUP`/`RATE_LIMIT` as WDS; SDMX shares the per-IP quota |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `xml.etree.ElementTree` | `application/vnd.sdmx.structure+json` Accept header | SDMX structure+json is supported in the SDMX standard but StatCan's implementation is unverified to return JSON for structure queries — the structure endpoint URL pattern (`/structure/Data_Structure_{pid}`) returns XML by default; stick with XML |
| `xml.etree.ElementTree` | `lxml` | lxml is faster and more capable but adds a dependency; ElementTree handles the known SDMX 2.1 namespace tree without issues |

**Installation:** No new packages required.

---

## Architecture Patterns

### Recommended File Changes

```
src/mcp_canada/modules/statcan/
├── constants.py     # Add SDMX_BASE_URL, SDMX_API_NAME, SDMX_XML_NAMESPACES
├── schemas.py       # Add SDMXDimension, SDMXCodelist, SDMXStructure, SDMXObservationRow
├── client.py        # Add get_sdmx_structure(), get_sdmx_data(), get_sdmx_vector_data()
│                    # Add _parse_structure_xml(), _build_sdmx_key(), _flatten_sdmx_json()
└── tools.py         # Add sc_get_sdmx_structure, sc_get_sdmx_data,
                     # sc_get_sdmx_vector_data, sc_fetch_vectors_to_store
```

### Pattern 1: SDMX Structure Query (XML)

**What:** GET request to `/structure/Data_Structure_{productId}` returns SDMX 2.1 XML. Parse with ElementTree to extract dimension codelists.

**When to use:** SC-10 — `sc_get_sdmx_structure` tool

**Example:**
```python
# Source: StatCan SDMX User Guide + mcp-statcan reference
SDMX_BASE_URL = "https://www150.statcan.gc.ca/t1/wds/sdmx/statcan/rest/"

# XML namespaces for SDMX 2.1 structure messages
SDMX_XML_NAMESPACES = {
    "mes": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "str": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
    "com": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
}

async def get_sdmx_structure(product_id: int) -> tuple[SDMXStructure, bool]:
    url = SDMX_BASE_URL + f"structure/Data_Structure_{product_id}"
    # Use plain GET, no special Accept header needed (XML is the default)
    async with _make_statcan_client() as http:
        resp = await http.get(url)
        resp.raise_for_status()
        return _parse_structure_xml(resp.text, product_id)

def _parse_structure_xml(xml_text: str, product_id: int) -> SDMXStructure:
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml_text)
    ns = SDMX_XML_NAMESPACES

    # Build codelist lookup: codelist_id -> list of (code_id, name_en, name_fr)
    codelists: dict[str, list[tuple[str, str, str]]] = {}
    for cl in root.findall(".//str:Codelist", ns):
        cl_id = cl.get("id", "")
        codes = []
        for code in cl.findall("str:Code", ns):
            code_id = code.get("id", "")
            names = {n.get("{http://www.w3.org/XML/1998/namespace}lang", "en"): n.text or ""
                     for n in code.findall("com:Name", ns)}
            codes.append((code_id, names.get("en", ""), names.get("fr", "")))
        codelists[cl_id] = codes

    # Extract dimensions from DataStructure
    dimensions = []
    for ds in root.findall(".//str:DataStructure", ns):
        for dim_list in ds.findall(".//str:DimensionList", ns):
            for dim in dim_list.findall("str:Dimension", ns):
                pos = int(dim.get("position", 0))
                dim_id = dim.get("id", "")
                # Resolve codelist reference
                cl_ref = dim.find(".//str:Enumeration/Ref", ns)
                cl_id = cl_ref.get("id", "") if cl_ref is not None else ""
                codes = codelists.get(cl_id, [])
                dimensions.append(SDMXDimension(
                    position=pos,
                    id=dim_id,
                    codelist_id=cl_id,
                    codes=codes,
                ))
    dimensions.sort(key=lambda d: d.position)
    return SDMXStructure(product_id=product_id, dimensions=dimensions)
```

### Pattern 2: SDMX Data Query (JSON)

**What:** GET request to `/data/DF_{productId}/{key}` with `Accept: application/json`. Returns SDMX-JSON compact format.

**When to use:** SC-11 — `sc_get_sdmx_data` tool

**Example:**
```python
# Source: StatCan SDMX User Guide + sdmx-json field guide
SDMX_JSON_ACCEPT = "application/json"

async def get_sdmx_data(
    product_id: int,
    key: str,
    start_period: str | None = None,
    end_period: str | None = None,
    last_n: int | None = None,
) -> tuple[list[SDMXObservationRow], bool]:
    # Mutual exclusion enforced here (not just in tool layer)
    if last_n is not None and (start_period or end_period):
        raise ValueError("lastN and date range cannot be used simultaneously")

    params: dict = {}
    if start_period:
        params["startPeriod"] = start_period
    if end_period:
        params["endPeriod"] = end_period
    if last_n is not None:
        params["lastNObservations"] = last_n

    url = SDMX_BASE_URL + f"data/DF_{product_id}/{key}"
    async with _make_statcan_client() as http:
        resp = await http.get(url, params=params, headers={"Accept": SDMX_JSON_ACCEPT})
        resp.raise_for_status()
        return _flatten_sdmx_json(resp.json()), False
```

### Pattern 3: SDMX-JSON Compact Format Navigation

**What:** SDMX-JSON uses positional indices throughout to minimize payload size. Series are keyed by dot-joined dimension indices; observations are keyed by time-period index.

**Example:**
```python
# Source: sdmx-json field guide (sdmx-twg/sdmx-json)
def _flatten_sdmx_json(payload: dict) -> list[SDMXObservationRow]:
    rows = []
    structure = payload.get("data", {}).get("structures", [{}])[0]

    # Build dimension value lookups: dim_pos -> [value_name, ...]
    dim_lookups: list[list[str]] = []
    series_dims = [d for d in structure.get("dimensions", {}).get("series", [])
                   if "keyPosition" in d]
    series_dims.sort(key=lambda d: d["keyPosition"])
    for dim in series_dims:
        dim_lookups.append([v.get("name", v.get("id", "")) for v in dim.get("values", [])])

    # Build time period list from observation-level TIME_PERIOD dimension
    obs_dims = structure.get("dimensions", {}).get("observation", [])
    time_periods: list[str] = []
    for od in obs_dims:
        if od.get("id") == "TIME_PERIOD":
            time_periods = [v.get("id", "") for v in od.get("values", [])]
            break

    for dataset in payload.get("data", {}).get("dataSets", []):
        for series_key_str, series_data in dataset.get("series", {}).items():
            indices = [int(i) for i in series_key_str.split(":")]
            dim_values = [
                dim_lookups[pos][idx] if pos < len(dim_lookups) and idx < len(dim_lookups[pos]) else str(idx)
                for pos, idx in enumerate(indices)
            ]
            for obs_key_str, obs_vals in series_data.get("observations", {}).items():
                t_idx = int(obs_key_str)
                period = time_periods[t_idx] if t_idx < len(time_periods) else obs_key_str
                value = obs_vals[0] if obs_vals else None
                rows.append(SDMXObservationRow(
                    period=period,
                    value=float(value) if value is not None else None,
                    dimensions=dict(zip([d.get("id","") for d in series_dims], dim_values)),
                ))
    return rows
```

### Pattern 4: Named Dimension Dict -> Key Translation

**What:** Agent passes `{"Geography": "1", "Products and product groups": "1+2"}` — tool resolves to `"1.1+2"` by ordering by dimension position.

**When to use:** Convenience path in `sc_get_sdmx_data` tool layer

**Example:**
```python
def _build_sdmx_key(dim_dict: dict[str, str | list[str]], structure: SDMXStructure) -> str:
    """Build dot-separated SDMX key from named dimension dict.

    Dimension names are matched case-insensitively.
    "all" or empty list maps to wildcard (empty position).
    List values are joined with "+".
    """
    key_parts: list[str] = [""] * len(structure.dimensions)
    name_to_pos: dict[str, int] = {
        d.id.lower(): d.position - 1 for d in structure.dimensions
    }
    for dim_name, value in dim_dict.items():
        pos = name_to_pos.get(dim_name.lower())
        if pos is None:
            continue  # unknown dim name — skip silently, wildcard
        if value == "all" or value == [] or value == "":
            key_parts[pos] = ""  # wildcard
        elif isinstance(value, list):
            key_parts[pos] = "+".join(str(v) for v in value)
        else:
            key_parts[pos] = str(value)
    return ".".join(key_parts)
```

### Pattern 5: Composite Fetch-and-Store

**What:** Calls `get_bulk_vector_data` (already implemented), infers schema from first observation row, calls `create_table` if needed, calls `insert_rows`.

**When to use:** SC-15 — `sc_fetch_vectors_to_store` tool

**Example:**
```python
# Source: datastore/client.py (already implemented)
from mcp_canada.modules.datastore import client as ds_client

async def fetch_vectors_to_store(
    vector_ids: list[int],
    start_release: str,
    end_release: str,
    table_name: str,
) -> tuple[dict, bool]:
    # 1. Validate table name (reuse datastore's validator)
    ds_client._validate_identifier(table_name)

    # 2. Fetch bulk vector data (already implemented in WDS client)
    bulk_data, was_cached = await get_bulk_vector_data(vector_ids, start_release, end_release)

    # 3. Flatten all observations into dicts, adding vector_id column
    rows = []
    for vid, obs_list in bulk_data.items():
        for obs in obs_list:
            row = obs.model_dump()
            row["vector_id"] = vid
            rows.append(row)

    if not rows:
        return {"stored": 0, "table": table_name, "vectors": list(bulk_data.keys())}, was_cached

    # 4. Infer schema from first row using datastore's type inferrer
    columns = [(col, ds_client._infer_sqlite_type(val)) for col, val in rows[0].items()]

    # 5. Create table (IF NOT EXISTS — append semantics)
    await ds_client.create_table(table_name, columns)

    # 6. Insert rows
    inserted, _ = await ds_client.insert_rows(table_name, rows)

    return {"stored": inserted, "table": table_name, "vectors": list(bulk_data.keys())}, False
```

### Anti-Patterns to Avoid

- **Passing `lastN` + date range simultaneously:** StatCan returns HTTP 406. Enforce mutual exclusion in both client and tool layers.
- **Using `+` on geography dimension in SDMX OR-key:** StatCan has a known bug returning wrong geography labels for multi-value dimension keys. Document in docstring; advise using individual requests or wildcard.
- **Skipping `statcan_sdmx:` cache key prefix:** Will collide with `statcan_wds:` keys for the same productId.
- **Importing `datastore.client._validate_identifier` directly:** The function is private (`_` prefix); call `ds_client._validate_identifier` but note it's an internal helper. Alternatively, re-validate table_name in the composite tool layer before calling `create_table` (which validates internally anyway).
- **Returning raw SDMX dimension indices instead of resolved names:** Always resolve indices against the structure's `values` arrays before returning rows to agents.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Async SQLite writes | Custom sqlite3 + run_in_executor | `datastore.client.insert_rows()` | Already implements WAL mode, identifier validation, executemany, and commit |
| Table creation with type inference | Custom DDL builder | `datastore.client.create_table()` + `datastore.client._infer_sqlite_type()` | Already handles type mapping, identifier validation, IF NOT EXISTS semantics |
| Rate limiting for SDMX | New rate limiter | `get_limiter(RATE_GROUP, RATE_LIMIT)` | SDMX shares the same per-IP StatCan quota as WDS |
| HTTP retry on transient errors | Custom retry loop | `_statcan_retry` decorator | Already configured for TimeoutException, ConnectError, ValueError |
| SSL handling | Custom cert bundle | `_make_statcan_client()` | `STATCAN_VERIFY=True` already validated in Phase 7; certifi works for statcan.gc.ca |
| SDMX-JSON parsing library | `sdmx1` / `pandaSDMX` | Hand-rolled `_flatten_sdmx_json()` | Dependency policy; the SDMX-JSON structure is documented and simple enough for ~50 lines |

**Key insight:** The WDS client infrastructure (`_make_statcan_client`, `_statcan_retry`, `_limiter_acquire`, `_statcan_fetch`, `cached_fetch`) is fully reusable for SDMX. No new HTTP infrastructure is needed.

---

## Common Pitfalls

### Pitfall 1: lastNObservations + Date Range = HTTP 406

**What goes wrong:** StatCan rejects requests combining `lastNObservations` with `startPeriod`/`endPeriod`. Returns 406 Not Acceptable.

**Why it happens:** SDMX standard permits the combination; StatCan does not implement it.

**How to avoid:** Enforce mutual exclusion at client level (raise `ValueError` before HTTP call); also check in tool layer (return `INVALID_INPUT` error with explanation). The `CONTEXT.md` decision locks this.

**Warning signs:** Any SDMX client function accepting all four time parameters without constraint.

### Pitfall 2: SDMX Cache Key Collisions with WDS

**What goes wrong:** `cached_fetch("statcan_wds:18100004", ...)` and `cached_fetch("statcan_sdmx:18100004", ...)` are different responses for the same productId.

**How to avoid:** All SDMX cache keys must be prefixed `statcan_sdmx:` — never reuse WDS key patterns.

### Pitfall 3: Structure XML Namespace Mismatch

**What goes wrong:** ElementTree `findall("str:Codelist")` returns nothing if namespaces are not registered correctly.

**Why it happens:** SDMX 2.1 uses Clark notation `{uri}localname` internally; the `ns` dict must be passed to every `findall`/`find` call.

**How to avoid:** Pass `ns` dict as second argument to every ElementTree find/findall call: `root.findall(".//str:Codelist", ns)`. Define `SDMX_XML_NAMESPACES` constant once in `constants.py`.

**Warning signs:** Structure parsing returning empty dimension lists in tests.

### Pitfall 4: OR-Key Geography Label Bug

**What goes wrong:** Requesting `1+2.1.1` (OR-key on geography) returns correct data but wrong geography labels.

**How to avoid:** Document in `sc_get_sdmx_data` tool docstring: "Note: OR-key syntax (`+`) on geography dimension may return incorrect labels for multi-value queries — use wildcard or separate calls for reliable geography labeling."

### Pitfall 5: Composite Tool Table Name Injection

**What goes wrong:** Agent-provided `table_name` flows into SQL DDL. The datastore `create_table()` validates internally, but the error surfaces as a generic exception rather than a structured `INVALID_INPUT` response.

**How to avoid:** In the composite tool, validate `table_name` against `IDENTIFIER_RE` before calling any datastore functions; return `INVALID_INPUT` with explanation if invalid.

### Pitfall 6: Empty Bulk Data Result in Composite Tool

**What goes wrong:** `get_bulk_vector_data` returns `{}` (all vectors failed) — calling `create_table` with empty columns list crashes.

**How to avoid:** Check `if not rows: return early` before schema inference and table creation. Return a `NOT_FOUND` error or a response indicating zero rows stored.

---

## Code Examples

Verified patterns from official sources and existing codebase:

### SDMX Endpoint URLs

```python
# Source: StatCan SDMX User Guide + confirmed by mcp-statcan reference
SDMX_BASE_URL = "https://www150.statcan.gc.ca/t1/wds/sdmx/statcan/rest/"

# Structure query: GET (no Accept header required; returns XML by default)
# https://www150.statcan.gc.ca/t1/wds/sdmx/statcan/rest/structure/Data_Structure_18100004

# Data query: GET with Accept: application/json
# https://www150.statcan.gc.ca/t1/wds/sdmx/statcan/rest/data/DF_18100004/1.1?lastNObservations=12

# Vector query: GET with Accept: application/json
# https://www150.statcan.gc.ca/t1/wds/sdmx/statcan/rest/vector/v41690973?startPeriod=2020-01&endPeriod=2024-01
```

### Key Syntax Examples

```python
# Source: StatCan SDMX User Guide
# All dimensions wildcard (all series):          "..."
# First dimension fixed, rest wildcard:          "1.."
# OR on second dimension:                        ".1+2."
# Fully specified 3-dimension key:               "1.2.1"
# 2-dimension table, all wildcard:               "."

# Suggested key example to include in structure response:
# If table has 3 dimensions, suggest: "1...." (first member of each dim)
def _make_suggested_key(structure: SDMXStructure) -> str:
    """Build a suggested key using first code of each dimension."""
    parts = []
    for dim in sorted(structure.dimensions, key=lambda d: d.position):
        first_code = dim.codes[0][0] if dim.codes else ""
        parts.append(first_code)
    return ".".join(parts)
```

### SDMX-JSON Compact Response Shape

```python
# Source: sdmx-json field guide (sdmx-twg/sdmx-json on GitHub)
# Top-level: {"meta": {...}, "data": {"structures": [...], "dataSets": [...]}}
# structures[0].dimensions.series = [{id, keyPosition, values: [{id, name}]}]
# structures[0].dimensions.observation = [{id: "TIME_PERIOD", values: [{id: "2024-01"}]}]
# dataSets[0].series = {"0:0:1": {"observations": {"0": [163.4], "1": [162.9]}}}
#                        ^series key by dim index  ^time_period_index: [value, attr...]
```

### Composite Tool Calling Both Clients

```python
# Source: datastore/client.py (Phase 7 implementation)
from mcp_canada.modules.datastore import client as ds_client
from mcp_canada.modules.statcan import client as sc_client

# The datastore functions needed:
# ds_client.create_table(table: str, columns: list[tuple[str, str]]) -> (None, False)
# ds_client.insert_rows(table: str, rows: list[dict]) -> (int, False)
# ds_client._infer_sqlite_type(value: object) -> str  (private but used internally)
# ds_client._validate_identifier(name: str) -> None   (private, raises ValueError)
```

### Existing `_flatten_observation` Reuse for Composite

```python
# Source: statcan/client.py (Phase 8 implementation)
# _flatten_observation(raw_point: dict) -> ObservationRow
# ObservationRow.model_dump() produces the flat dict for insert_rows()
# Adding "vector_id" column before insert:
row = obs.model_dump()
row["vector_id"] = vid  # add vector_id as first or last column
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| WDS-only data retrieval (Phase 8) | SDMX for server-side filtered queries | Phase 9 | Large tables (80K+ series) become usable without returning full payloads |
| Separate fetch + manual store loop | Single `sc_fetch_vectors_to_store` call | Phase 9 | Composite pattern reduces agent round trips for common analysis workflows |

**Deprecated/outdated:**
- `verify=False` on SDMX client: Not needed — `STATCAN_VERIFY=True` was confirmed in Phase 7 to work for statcan.gc.ca (certifi validates the cert chain).

---

## Open Questions

1. **Does `application/vnd.sdmx.structure+json` work for StatCan structure queries?**
   - What we know: The SDMX standard defines this Accept header for JSON structure responses. StatCan's documentation does not confirm support. The structure endpoint URL returns XML by default.
   - What's unclear: Whether StatCan implemented the JSON structure format at all.
   - Recommendation: Use XML (ElementTree) for structure queries — confirmed working by mcp-statcan reference implementation. Attempt JSON structure only if XML approach proves problematic.

2. **Exact SDMX-JSON series key delimiter**
   - What we know: mcp-statcan sdmx_json.py splits series keys on `.` — `"0.0.1".split(".")`. The sdmx-json spec shows keys like `"0:0:1"` separated by colons.
   - What's unclear: Whether StatCan uses `.` or `:` as delimiter in series keys within the JSON payload. Both have been observed in different implementations.
   - Recommendation: In `_flatten_sdmx_json`, try `:` split first (per SDMX-JSON spec), with fallback to `.` split. Validate against a real API response in integration tests.

3. **SDMX vector endpoint URL format**
   - What we know: StatCan user guide shows `/vector/v{vectorId}` (e.g., `/vector/v466670`). The `v` prefix is StatCan-specific (not SDMX standard).
   - What's unclear: Whether `startPeriod`/`endPeriod` are supported on the vector endpoint in the same way as the data endpoint.
   - Recommendation: Implement as documented; integration tests will surface any discrepancy.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest with pytest-asyncio |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| Quick run command | `uv run pytest src/mcp_canada/modules/statcan/__tests__/ -x -v` |
| Full suite command | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SC-10 | `get_sdmx_structure` returns SDMXStructure with dimensions + codelists | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py -k sdmx_structure -x` | Wave 0 |
| SC-10 | `sc_get_sdmx_structure` tool returns `_meta` envelope with dimension list | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_tools.py -k sdmx_structure -x` | Wave 0 |
| SC-11 | `get_sdmx_data` enforces mutual exclusion (lastN + date range -> ValueError) | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py -k sdmx_data_mutual -x` | Wave 0 |
| SC-11 | `get_sdmx_data` flattens SDMX-JSON observations to rows | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py -k sdmx_data_flatten -x` | Wave 0 |
| SC-11 | `sc_get_sdmx_data` tool returns INVALID_INPUT when both lastN and date range provided | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_tools.py -k sdmx_data_invalid -x` | Wave 0 |
| SC-12 | `get_sdmx_vector_data` fetches by vectorId with date range | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_client.py -k sdmx_vector -x` | Wave 0 |
| SC-15 | `sc_fetch_vectors_to_store` creates table + inserts rows when table doesn't exist | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_tools.py -k fetch_to_store -x` | Wave 0 |
| SC-15 | `sc_fetch_vectors_to_store` appends rows when table already exists | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_tools.py -k fetch_to_store_append -x` | Wave 0 |
| SC-15 | `sc_fetch_vectors_to_store` returns INVALID_INPUT on invalid table_name | unit | `uv run pytest src/mcp_canada/modules/statcan/__tests__/test_tools.py -k fetch_to_store_invalid_name -x` | Wave 0 |
| SC-10,11,12,15 | Integration: real SDMX API calls through MCP Client layer | integration | `uv run pytest tests/integration/ -v -m integration --timeout=120 -k sdmx` | Wave 0 |

### Sampling Rate

- **Per task commit:** `uv run pytest src/mcp_canada/modules/statcan/__tests__/ -x`
- **Per wave merge:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `src/mcp_canada/modules/statcan/__tests__/conftest.py` — add SDMX XML fixture (`SDMX_STRUCTURE_XML`), SDMX-JSON fixture (`SDMX_DATA_JSON`), SDMX vector JSON fixture (`SDMX_VECTOR_JSON`)
- [ ] `src/mcp_canada/modules/statcan/__tests__/test_client.py` — add SDMX client test class
- [ ] `src/mcp_canada/modules/statcan/__tests__/test_tools.py` — add SDMX tool test class + composite tool tests
- [ ] `tests/integration/test_tool_scenarios.py` — add SDMX integration scenarios (CPI table 18100004 is a reliable test target)

---

## Sources

### Primary (HIGH confidence)

- StatCan SDMX User Guide: https://www.statcan.gc.ca/en/developers/sdmx/user-guide — endpoint URL patterns, key syntax, query parameters, response formats
- SDMX-JSON Field Guide: https://github.com/sdmx-twg/sdmx-json/blob/master/data-message/docs/1-sdmx-json-field-guide.md — compact JSON structure (dataSets, series keys, observation arrays)
- Existing `statcan/client.py` — `_make_statcan_client`, `_statcan_retry`, `_limiter_acquire`, `_flatten_observation`, `get_bulk_vector_data` patterns (all reusable)
- Existing `datastore/client.py` — `create_table`, `insert_rows`, `_infer_sqlite_type`, `_validate_identifier` (all callable from composite tool)

### Secondary (MEDIUM confidence)

- mcp-statcan reference implementation `sdmx_tools.py` (via WebFetch) — confirms endpoint URL patterns, structure XML parsing approach, JSON Accept header for data queries, mutual exclusion enforcement
- mcp-statcan reference implementation `sdmx_json.py` (via WebFetch) — confirms SDMX-JSON positional index parsing approach
- StatCan SDMX live endpoint `Data_Structure_18100004` (fetched via WebFetch) — confirmed XML namespace declarations, `str:Codelist`/`str:Code` element structure, `com:Name` child elements

### Tertiary (LOW confidence)

- SDMX series key delimiter (`.` vs `:`): mcp-statcan uses `.` split but SDMX-JSON spec shows `:`. Validate in integration tests.
- `application/vnd.sdmx.structure+json` support for StatCan structure endpoint: unverified; XML is the safe fallback.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — stdlib XML, existing httpx/cache/rate-limit patterns confirmed
- Architecture: HIGH — endpoint URLs verified against official docs and live endpoint; JSON response shape verified against SDMX-JSON spec
- Pitfalls: HIGH — mutual exclusion constraint documented in official pitfalls research; OR-key label bug confirmed in mcp-statcan; composite empty-result edge case identified from code inspection
- SDMX-JSON parsing: MEDIUM — spec is clear but series key delimiter (`.` vs `:`) needs empirical validation

**Research date:** 2026-04-07
**Valid until:** 2026-05-07 (StatCan SDMX endpoint is stable; XML structure format is SDMX 2.1 standard)
