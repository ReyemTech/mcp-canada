# Phase 21: New Brunswick Government Open Data - Pattern Map

**Mapped:** 2026-07-30
**Files analyzed:** ~14 new module files + 2 new shared functions + 2 test files extended
**Analogs found:** 12 / 14 (module files have direct 1:1 analogs; 2 shared-extension files have partial analogs)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `src/mcp_canada/modules/new_brunswick/__init__.py` | config | — | `modules/nova_scotia/__init__.py` | exact |
| `src/mcp_canada/modules/new_brunswick/constants.py` | config | — | `modules/saskatchewan/constants.py` (multi-base) + `modules/manitoba/constants.py` (511 key env) | role-match |
| `src/mcp_canada/modules/new_brunswick/schemas.py` | model | transform | `modules/nova_scotia/schemas.py` | exact |
| `src/mcp_canada/modules/new_brunswick/client.py` (discovery fns) | service | CRUD (request-response) | `modules/alberta/client.py` (`_api_get`, `fq` composition) | exact |
| `src/mcp_canada/modules/new_brunswick/client.py` (GeoNB fns) | service | request-response | `modules/saskatchewan/client.py` (multi-limiter, `arcgis_hub.query_feature_service` call sites) | exact |
| `src/mcp_canada/modules/new_brunswick/client.py` (511 stub fns) | service | request-response | `modules/manitoba/client.py` (`Five11NotConfigured`, `_511_get`) | exact |
| `src/mcp_canada/modules/new_brunswick/tools.py` | controller | request-response | `modules/nova_scotia/tools.py` + `modules/saskatchewan/tools.py` | exact |
| `src/mcp_canada/modules/new_brunswick/prompts.py` | controller | request-response | `modules/nova_scotia/prompts.py` | exact |
| `src/mcp_canada/modules/new_brunswick/resources.py` | controller | request-response | `modules/nova_scotia/resources.py` | exact |
| `src/mcp_canada/modules/new_brunswick/__tests__/conftest.py` | test | — | `modules/saskatchewan/__tests__/conftest.py` | exact |
| `src/mcp_canada/modules/new_brunswick/__tests__/test_client.py` | test | — | `modules/saskatchewan/__tests__/test_client.py` | exact |
| `src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py` | test | — | `modules/nova_scotia/__tests__/test_tools.py` | exact |
| `src/mcp_canada/modules/new_brunswick/__tests__/test_prompts_resources.py` | test | — | `modules/nova_scotia/__tests__/test_prompts_resources.py` | exact |
| `src/mcp_canada/shared/arcgis_hub.py` (+ 2 new fns) | utility | request-response | Same file, existing `search_hub_datasets`/`get_layer_metadata` | role-match (extension, no true analog for "bare Server directory enumeration") |
| `src/mcp_canada/shared/__tests__/test_arcgis_hub.py` (+ 2 test classes) | test | — | Same file, existing `TestSearchHubDatasets` | role-match |
| `tests/integration/test_tool_scenarios.py` (+ NB scenarios) | test | request-response | `TestManitobaToolScenarios` (line 2100) | exact |
| `CLAUDE.md` (Socrata row correction) | docs | — | n/a — direct text edit | n/a |

## Pattern Assignments

### `src/mcp_canada/modules/new_brunswick/client.py` — discovery functions (controller-adjacent service, CRUD/request-response)

**Analog:** `src/mcp_canada/modules/alberta/client.py`

**`_api_get` + `fq` composition pattern** (`alberta/client.py:173-188, 341-365`):
```python
async def _api_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """CKAN Action API call against open.alberta.ca.

    Returns the parsed CKAN `result` field. Raises `httpx.HTTPStatusError` on
    success=False or when the upstream returns a non-dict envelope.

    Phase 15-05 contract (enforced by TestSharedApiGetContract):
      - api_get returns already-parsed JSON — do NOT call .raise_for_status()
        or .json() on the return value.
    """
    ...

# fq composition for organization/format filters:
params: dict[str, Any] = {
    "q": q,
    "rows": min(max(rows, 1), 100),
    "start": max(start, 0),
}
fq_parts: list[str] = []
if organization:
    fq_parts.append(f"organization:{organization}")
if format:
    fq_parts.append(f"res_format:{format}")
if fq_parts:
    params["fq"] = " ".join(fq_parts)
```

**NB-specific deviation (per D-01/D-03 and Pattern 1 of RESEARCH.md):** NB's `_api_get` targets
`open.canada.ca` (federal CKAN), not a provincial CKAN, and `fq` must **always** start with
`organization:nb` — non-optional, never caller-overridable — then AND additional filters:
```python
fq = "organization:nb"
if extra_fq:
    fq = f"{fq} AND {extra_fq}"
params = {"q": query, "fq": fq, "rows": rows, "start": start}
```
Do NOT expose an open `organization` parameter to callers the way Alberta/BC do (Anti-Pattern in
RESEARCH.md) — NB has no other organization to filter to.

**Bilingual title/notes fallback** (`modules/ckan/client.py:84-113`, verified reusable as-is per D-12/Pattern 2):
```python
def _shape_dataset(raw: dict[str, Any], lang: str = "en") -> dict[str, Any]:
    title_translated: dict[str, str] | None = raw.get("title_translated")
    if title_translated:
        title = title_translated.get(lang) or title_translated.get("en") or raw.get("title")
    else:
        title = raw.get("title")

    notes_translated: dict[str, str] | None = raw.get("notes_translated")
    if notes_translated:
        description = notes_translated.get(lang) or notes_translated.get("en") or raw.get("notes")
    else:
        description = raw.get("notes")
```
Copy this function verbatim into `new_brunswick/client.py`'s own `_shape_dataset` — do not import
from `modules/ckan`.

---

### `src/mcp_canada/modules/new_brunswick/client.py` — GeoNB curated functions (service, request-response)

**Analog:** `src/mcp_canada/modules/saskatchewan/client.py` (multi-base ArcGIS)

**Module-level limiters pattern** (`saskatchewan/client.py:119-121`):
```python
_hub_limiter = get_limiter(RATE_GROUP_HUB, RATE_LIMIT_HUB)
_wsa_limiter = get_limiter(RATE_GROUP_WSA, RATE_LIMIT_WSA)
_spsa_limiter = get_limiter(RATE_GROUP_SPSA, RATE_LIMIT_SPSA)
```
NB likely needs only ONE limiter (single GeoNB base `https://geonb.snb.ca/arcgis/rest/services`,
unlike Saskatchewan's 3 distinct hosts) plus a separate limiter for the federal CKAN discovery
calls and one for the 511 stub — i.e. 2-3 limiters total, not 3+ per-ArcGIS-base like Saskatchewan.

**Curated fetch call site** — each fetcher acquires its limiter then delegates entirely to
`shared/arcgis_hub.py:query_feature_service`, passing the pre-resolved, hardcoded layer id (never
guessed — see Pitfall 1 in RESEARCH.md):
```python
await _hub_limiter.acquire()
features, truncated = await arcgis_hub.query_feature_service(
    service_url=f"{GEONB_BASE_URL}/GeoNB_DNR_Crown_Land/MapServer",
    layer_id=3,  # NOT 0 — verified via {service}/MapServer?f=json
    where=where or "1=1",
    out_fields="OBJECTID,HOLDER,Shape_Length,Shape_Area",
    include_geometry=include_geometry,
)
```

**Unbounded-query guard (V5/DoS mitigation per RESEARCH.md Security Domain):** for the largest
layers (Parcels 604,520 records, Civic_Address 373,172, Wetlands 163,206), require at least one
filter parameter before allowing an unfiltered query — raise `InvalidInput` before any network
call, mirroring BC's `bc_get_water_wells` guard precedent (not in this repo's NB files yet; apply
the same shape as `InvalidInput` usage below).

---

### `src/mcp_canada/shared/arcgis_hub.py` — new `list_arcgis_server_services` / `get_arcgis_server_layers`

**Analog:** Same file's existing `search_hub_datasets` (lines 42-88) and `get_layer_metadata`
(lines 174-215) — style/shape to copy, NOT logic (Hub Search API vs. bare ArcGIS Server directory
are functionally different; this is the one genuinely new piece of code in the phase per
RESEARCH.md "Key insight").

**Imports already present in the file to reuse** (`shared/arcgis_hub.py:15-24`):
```python
from __future__ import annotations
from typing import Any
import httpx
from mcp_canada.shared.http import decode_json, decode_json_bytes
from mcp_canada.shared.parsers import _parse_geojson
from mcp_canada.shared.errors import NotFound
```

**Style to copy — dual-path httpx_client injection + `decode_json` discipline** (`search_hub_datasets`, lines 42-88):
```python
async def search_hub_datasets(
    portal_base_url: str | None,
    query: str = "",
    limit: int = 10,
    offset: int = 0,
    *,
    httpx_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    if portal_base_url is None:
        raise NotFound("portal has no public ArcGIS Hub open data portal")

    url = portal_base_url.rstrip("/") + HUB_SEARCH_PATH
    params: dict[str, Any] = {"limit": limit}
    if query and query.strip():
        params["q"] = query   # empty q rejected w/ HTTP 400 by every Hub portal — omit it
    if offset > 0:
        params["startindex"] = offset

    if httpx_client is not None:
        response = await httpx_client.get(url, params=params)
        response.raise_for_status()
        return decode_json(response, url)

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return decode_json(response, url)
```

**New functions to write, matching this exact shape** (per RESEARCH.md Pattern 3 — verbatim
skeleton, fill in the body following the dual-path structure above):
```python
async def list_arcgis_server_services(
    base_url: str,
    *,
    httpx_client: httpx.AsyncClient | None = None,
) -> list[dict[str, Any]]:
    """GET {base_url}?f=json -> filter to the `services` list (excludes folders)."""
    url = base_url.rstrip("/")
    params = {"f": "json"}
    # ... same dual-path (httpx_client injected vs. new AsyncClient) as search_hub_datasets
    data = decode_json(response, url)
    return data.get("services", [])


async def get_arcgis_server_layers(
    service_url: str,
    *,
    httpx_client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """GET {service_url}/MapServer?f=json -> {"layers": [...], "tables": [...]}."""
    url = f"{service_url.rstrip('/')}/MapServer"
    # ... same dual-path
    data = decode_json(response, url)
    return {
        "layers": [{"id": l.get("id"), "name": l.get("name")} for l in data.get("layers", [])],
        "tables": [{"id": t.get("id"), "name": t.get("name")} for t in data.get("tables", [])],
    }
```

**`where or "1=1"` coalescing (already correct, do not re-derive)** — `query_feature_service` and
`get_count` both already guard against a `None`/dropped `where` (lines 134, 242):
```python
params: dict[str, Any] = {
    # httpx drops None-valued params; ArcGIS /query rejects a request
    # with no `where`, which surfaces as a bogus UPSTREAM_ERROR.
    "where": where or "1=1",
    ...
}
```
No changes needed to `query_feature_service` itself — GeoNB MapServer works unchanged (D-05).

---

### `src/mcp_canada/modules/new_brunswick/client.py` — 511 transport stubs (service, request-response)

**Analog:** `src/mcp_canada/modules/manitoba/client.py` — copy verbatim, renaming identifiers.

**Exception + gated fetch pattern** (`manitoba/client.py:139-141, 171-191`):
```python
class Five11NotConfigured(Exception):
    """Raised when MANITOBA_511_KEY env var is not set."""


async def _511_get(endpoint: str, params: dict[str, Any] | None = None) -> list[dict]:
    """Manitoba 511 REST API v3 call. Returns raw JSON list.

    GATED: requires MANITOBA_511_KEY environment variable.
    If key is absent, raises Five11NotConfigured.
    Tool layer catches Five11NotConfigured and returns make_error("NOT_CONFIGURED").
    """
    key = os.environ.get(FIVE11_KEY_ENV, "")
    if not key:
        raise Five11NotConfigured(
            "MANITOBA_511_KEY not set. Register at https://www.manitoba511.ca/my511/register "
            "then request a developer API key."
        )
    rows = await api_get(
        f"{FIVE11_BASE_URL}/{endpoint}",
        {**(params or {}), "key": key, "format": "json"},
        headers={"User-Agent": USER_AGENT},
    )
    return rows if isinstance(rows, list) else []
```

**NB deviation (per D-09/RESEARCH.md Open Question 1):** no known public free-registration URL for
NB 511 — the message should point to `https://511.gnb.ca` generally rather than inventing a
specific registration path:
```python
class Five11NotConfigured(Exception):
    """Raised when NEW_BRUNSWICK_511_KEY env var is not set."""


async def _511_get(endpoint: str, params: dict[str, Any] | None = None) -> list[dict]:
    key = os.environ.get(FIVE11_KEY_ENV, "")
    if not key:
        raise Five11NotConfigured(
            "NEW_BRUNSWICK_511_KEY not set. A developer key must be obtained "
            "from the NB Department of Transportation and Infrastructure via https://511.gnb.ca."
        )
    rows = await api_get(f"{FIVE11_BASE_URL}/{endpoint}", {**(params or {}), "key": key})
    return rows if isinstance(rows, list) else []
```

**Tool-layer catch pattern** (`manitoba/tools.py:734-760`):
```python
_NOT_CONFIGURED_MSG_EN = (
    "New Brunswick 511 requires a developer key. Visit https://511.gnb.ca "
    "then request an API key, and set the NEW_BRUNSWICK_511_KEY environment variable."
)
_NOT_CONFIGURED_MSG_FR = (
    "Le 511 du Nouveau-Brunswick nécessite une clé de développeur. Visitez https://511.gnb.ca "
    "puis demandez une clé API et définissez la variable d'environnement NEW_BRUNSWICK_511_KEY."
)

@tool
async def nb_get_road_events(lang: Literal["en", "fr"] = "en") -> dict:
    """..."""
    try:
        ...
    except Five11NotConfigured:
        msg = _NOT_CONFIGURED_MSG_FR if lang == "fr" else _NOT_CONFIGURED_MSG_EN
        return make_error("NOT_CONFIGURED", msg, lang=lang)
```
This satisfies D-10 — `NOT_CONFIGURED` is a normal envelope return, not an exception path, and the
integration test must assert the exact shape (never wrap in `tolerates_upstream_error`) per
RESEARCH.md's Phase Requirements → Test Map.

---

### `src/mcp_canada/modules/new_brunswick/tools.py` (controller, request-response)

**Analog:** `src/mcp_canada/modules/nova_scotia/tools.py` (module header/imports) +
`src/mcp_canada/modules/saskatchewan/tools.py` (curated-tool ArcGIS shape)

**File header / imports pattern** (`nova_scotia/tools.py:1-38`):
```python
"""New Brunswick module tools — @tool functions for the MCP server.

All tools use standalone @tool from fastmcp.tools (NEVER @mcp.tool).
All tools include lang: Literal["en", "fr"] = "en" parameter.
All tools return make_response() on success, make_error() on failure.
All tools use the "nb_" prefix.
"""

from __future__ import annotations

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_error, make_response

from . import client as _client
from .constants import (...)
from mcp_canada.shared.errors import InvalidInput
```

**Discovery tool shape** (`nova_scotia/tools.py:46-68`):
```python
@tool
async def nb_search_datasets(
    query: str = "",
    limit: int = 10,
    offset: int = 0,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Search Government of New Brunswick open datasets via the federal CKAN catalogue
    (open.canada.ca, filtered to organization:nb).

    Use for: searching New Brunswick's open data; discovering NB datasets by keyword;
    browsing the 221 first-party GNB datasets on the federal portal.
    Keywords: new brunswick open data catalogue search datasets ckan federal portal
    browse discover inventory find provincial government data gnb bilingual
    """
    try:
        data, cached = await _client.fetch_search_datasets(query=query, limit=limit, offset=offset, lang=lang)
        return make_response(
            {"results": data.get("results", []), "total": data.get("total", 0), "offset": offset, "limit": limit},
            api_name="new-brunswick-federal-ckan",
            api_url="https://open.canada.ca/data/api/3/action/package_search",
            cached=cached,
            lang=lang,
        )
    except Exception as exc:
        return make_error("UPSTREAM_ERROR", str(exc), lang=lang)
```
Note: prefer `@upstream_guard(_API_NAME)` beneath `@tool` over the bare `except Exception` shown
above where feasible — Saskatchewan's tools.py uses `@upstream_guard`; RESEARCH.md's ERR-01
guidance for this phase explicitly recommends it (Nova Scotia predates the guard's introduction
and is not the strictest analog for error handling — use Saskatchewan for that axis).

**Saskatchewan curated-tool imports/header for the ArcGIS-backed side** (`saskatchewan/tools.py:1-40`):
```python
"""Saskatchewan module tools.
...
Every @tool:
  - Uses standalone `@tool` from fastmcp.tools (NEVER @mcp.tool)
  - Accepts lang: Literal["en", "fr"] = "en"
  - Returns make_response() on success / make_error() on failure
  - Has Use for: + single-line Keywords: (8+ terms) in docstring
  - Uses saskatchewan_ prefix
"""
from typing import Any, Literal
import httpx
from fastmcp.tools import tool
from mcp_canada.shared.envelope import make_error, make_response
from . import client as _client
from .constants import (...)
from mcp_canada.shared.errors import InvalidInput, NotFound

_API_NAME_HUB = "saskatchewan-geohub"
```
Adapt directly for NB: `_API_NAME_GEONB = "new-brunswick-geonb"`, `_API_NAME_CKAN =
"new-brunswick-federal-ckan"`, `_API_NAME_511 = "new-brunswick-511"`.

---

### `src/mcp_canada/modules/new_brunswick/__tests__/` (test files)

**Analog:** `src/mcp_canada/shared/__tests__/test_arcgis_hub.py` structure for the two new shared
functions — assert **outgoing params**, not just the URL (the Manitoba/Saskatchewan lesson,
explicitly called out in the phase context):

**Existing class structure to mirror for the two new shared functions** (`test_arcgis_hub.py`):
```
class TestSearchHubDatasets:
    async def test_happy_path_returns_raw_dict(self): ...
    async def test_raises_value_error_when_portal_none(self): ...
    async def test_empty_query_works(self): ...
    async def test_offset_zero_omitted_from_params(self): ...
    async def test_offset_positive_sends_startindex_not_offset(self): ...
```
New classes to add: `TestListArcgisServerServices` (happy path returns 62-service-shaped list,
excludes folders, asserts `params={"f": "json"}` sent), `TestGetArcgisServerLayers` (happy path
returns `{layers, tables}` shape, asserts URL is `{service_url}/MapServer` not `/MapServer/query`).

**`tests/integration/test_tool_scenarios.py`** — mirror `TestManitobaToolScenarios` (line 2100)
class structure for a new `TestNewBrunswickToolScenarios` class: happy path via `Client(mcp)` +
`call_tool`, discovery via `discover_tools`, error handling for bad input, and the
`NOT_CONFIGURED` 511 assertion (exact-shape, not tolerated).

## Shared Patterns

### Error classification (`InvalidInput`/`NotFound`/`UpstreamData`)
**Source:** `src/mcp_canada/shared/errors.py:33-61`
**Apply to:** Every NB client function that needs to raise — never `raise ValueError` directly.
```python
class InvalidInput(ValueError):
    """raise InvalidInput(f"mineral must be one of {sorted(MINES)}, got {mineral!r}")"""

class NotFound(ValueError):
    """raise NotFound(f"Dataset not found: {dataset_id}")"""

class UpstreamData(ValueError):
    """raise UpstreamData("StatCan returned empty response body")"""
```

### Catch-all coverage (`@upstream_guard`)
**Source:** `src/mcp_canada/shared/envelope.py:78-176`
**Apply to:** Every NB `@tool` function — beneath `@tool`:
```python
@tool
@upstream_guard(_API_NAME_GEONB)
async def nb_get_crown_land(...) -> dict:
    ...
```
Handles `httpx.HTTPStatusError`, `httpx.TimeoutException`/`ConnectError`/`HTTPError`,
`InvalidInput`, `NotFound`, `UpstreamData`, `JSONDecodeError`/`UnicodeDecodeError`,
`pydantic.ValidationError`, bare `ValueError` (defaults `UPSTREAM_ERROR`), and a final
`except Exception` catch-all — covers ERR-01 through ERR-07 in one decorator.

### JSON decoding discipline
**Source:** `src/mcp_canada/shared/http.py:16-54`
**Apply to:** Both new `shared/arcgis_hub.py` functions and NB's own `_api_get`/`_511_get` — never
call `response.json()` or `json.loads()` directly; always route through `decode_json(response,
url)` or `decode_json_bytes(content, url)`.

### Response envelope
**Source:** `src/mcp_canada/shared/envelope.py:22-75`
**Apply to:** Every NB tool's return value:
```python
return make_response(data, api_name="new-brunswick-geonb", api_url=service_url, cached=cached, lang=lang)
# or
return make_error("INVALID_INPUT", str(exc), lang=lang)
```

### Bilingual title/notes fallback
**Source:** `src/mcp_canada/modules/ckan/client.py:84-113` (see Pattern Assignments above for full excerpt)
**Apply to:** NB's own `_shape_dataset` in `new_brunswick/client.py` — copy the fallback chain
verbatim; do not special-case NB's duplicate FR/EN CKAN record pairs (Pitfall 5 — the existing
fallback already handles it correctly).

### Multi-limiter setup for multi-surface modules
**Source:** `src/mcp_canada/modules/saskatchewan/client.py:119-121`
**Apply to:** `new_brunswick/client.py` module-level setup — one limiter per distinct upstream
surface (federal CKAN, GeoNB ArcGIS Server, 511), not per-service within GeoNB (GeoNB is a single
host unlike Saskatchewan's 3 distinct ArcGIS bases).

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `shared/arcgis_hub.py:list_arcgis_server_services` / `get_arcgis_server_layers` | utility | request-response | No prior module has queried a *bare* ArcGIS Server REST directory (`/arcgis/rest/services?f=json`) without a Hub Search API in front — every prior province (York Region, Alberta, Manitoba, Saskatchewan) used `search_hub_datasets` against a Hub portal. Style is copied from `search_hub_datasets`/`get_layer_metadata` in the same file; the underlying endpoint shape is genuinely new to this codebase (confirmed in RESEARCH.md "Key insight" and "State of the Art" table). |

## Metadata

**Analog search scope:** `src/mcp_canada/modules/{nova_scotia,manitoba,saskatchewan,alberta,ckan}/`,
`src/mcp_canada/shared/{arcgis_hub.py,errors.py,envelope.py,http.py}`,
`src/mcp_canada/shared/__tests__/test_arcgis_hub.py`, `tests/integration/test_tool_scenarios.py`
**Files scanned:** ~20 (read in full or targeted grep/read passes)
**Pattern extraction date:** 2026-07-30
