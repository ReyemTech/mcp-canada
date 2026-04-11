---
status: diagnosed
trigger: "BC UAT Tests 2/3/9/14 blocker: 'dict' object has no attribute 'raise_for_status' when calling bc_search_datasets, bc_get_dataset_details, bc_query_features live."
created: 2026-04-10T00:00:00Z
updated: 2026-04-10T00:00:00Z
---

## Current Focus

hypothesis: british_columbia/client.py:_api_get misuses the shared shared/http.py:api_get contract — it treats the return value as an httpx.Response (calls .raise_for_status() and .json() on it), but shared api_get returns already-parsed JSON (dict/list).
test: Read shared/http.py:api_get return type + BC _api_get call site; cross-check with Ontario/Toronto/open_parliament/weather reference modules.
expecting: Confirmation that the shared contract returns parsed JSON and BC is the only caller treating it as a Response.
next_action: Root cause confirmed — write up minimum-diff fix and update UAT gap entries.

## Symptoms

expected: Calling bc_search_datasets(q="wildfire") returns a list of BC datasets with _meta.source.api == "bc-data-catalogue"; bc_get_dataset_details returns queryable_via_wfs + object_name; bc_query_features routes WFS datasets to the WFS path.
actual: All three tools raise "'dict' object has no attribute 'raise_for_status'" when exercised against the live CKAN endpoint. Integration suite reports 7 failures cascading from the same exception.
errors: "Error calling tool 'bc_search_datasets': 'dict' object has no attribute 'raise_for_status'" (Test 2); same message for bc_get_dataset_details (Test 3) and bc_query_features (Test 9); Test 14 reports 7 integration failures.
reproduction: uv run mcp-canada, then call bc_search_datasets(q="wildfire") via the MCP client (or run tests/integration/ -m integration -k Bc). Fails on the first real HTTP call to https://catalogue.data.gov.bc.ca/api/3/action/package_search.
started: Never worked live. Unit tests all green because they mocked with a MagicMock Response wrapper; no one exercised the real shared api_get path before UAT.

## Eliminated

- hypothesis: CKAN endpoint returning malformed envelope
  evidence: tag_list / organization_list / package_search all fail with the same AttributeError regardless of payload — the failure is in BC client code, not in CKAN responses.
  timestamp: 2026-04-10T00:00:00Z

- hypothesis: httpx version drift changing Response API
  evidence: raise_for_status exists on httpx.Response in all supported versions; the error message "'dict' object has no attribute 'raise_for_status'" explicitly says the value is a dict, not a Response.
  timestamp: 2026-04-10T00:00:00Z

- hypothesis: BC-specific rate limiter or cache wrapping the response
  evidence: neither cached_fetch nor get_limiter alters the fetcher return value — they just await it and pass it through. The dict comes directly from api_get.
  timestamp: 2026-04-10T00:00:00Z

## Evidence

- timestamp: 2026-04-10T00:00:00Z
  checked: src/mcp_canada/shared/http.py:34-58 — api_get signature and body
  found: api_get returns `response.json()` (already parsed dict/list), NOT the httpx.Response object. The docstring at line 48-49 says "Returns: Parsed JSON response." The inner `_fetch()` explicitly calls `response.raise_for_status()` and returns `response.json()` before api_get's return.
  implication: Any caller that treats api_get's return value as a Response is wrong.

- timestamp: 2026-04-10T00:00:00Z
  checked: src/mcp_canada/modules/british_columbia/client.py:55-78 — _api_get helper
  found: Lines 69-71 do this:
    ```
    response = await api_get(url, params or {})   # line 69 — receives a DICT
    response.raise_for_status()                   # line 70 — AttributeError: dict has no .raise_for_status
    envelope = response.json()                    # line 71 — never reached
    ```
  implication: BC _api_get treats api_get's parsed-JSON return as a Response. The very first CKAN call explodes on line 70.

- timestamp: 2026-04-10T00:00:00Z
  checked: src/mcp_canada/modules/ontario/client.py:151-181 (_api_get reference), src/mcp_canada/modules/toronto/client.py:112-133 (_api_get reference), src/mcp_canada/modules/ckan/client.py:148 (shared CKAN helper), src/mcp_canada/modules/open_parliament/client.py:66-74, src/mcp_canada/modules/weather/collections/client.py:32
  found: NONE of the other modules call shared api_get the way BC does. The reference pattern is one of two things:
    1. CKAN modules (ontario, toronto, ckan) bypass shared api_get entirely and create their own `httpx.AsyncClient()` inside the fetcher — see ontario line 175: `async with httpx.AsyncClient(timeout=30.0) as http: response = await http.get(...); response.raise_for_status(); envelope = response.json(); return envelope["result"]`.
    2. open_parliament and weather DO call shared api_get and correctly treat the result as parsed JSON: `return await api_get(url, params=..., headers=...)` (open_parliament line 72) and `return await api_get(url, params={"f": "json"})` (weather/collections line 32).
  implication: BC is the only module mixing the two patterns — it imports shared api_get (parsed-JSON contract) AND then calls .raise_for_status()/.json() as if it were the httpx pattern. This is a copy-paste hybrid that couldn't have been exercised live.

- timestamp: 2026-04-10T00:00:00Z
  checked: src/mcp_canada/modules/british_columbia/__tests__/test_client.py — all 22 unit tests
  found: The test helper `_make_http_response()` at lines 25-31 builds a MagicMock that:
    - has `.json.return_value = json_data`
    - has `.raise_for_status = MagicMock()` (no-op)
    Then every test patches `mcp_canada.modules.british_columbia.client.api_get` to return that mock (e.g. lines 46, 64, 77, 101, 126, 144, 155, 165, 175, 185, 199, 220, 239, 260, 277, 299). So the mocked api_get returns a FAKE Response, which makes BC's `response.raise_for_status()` + `response.json()` silently "work." The contract mismatch between BC's _api_get and the real shared api_get was masked by test mocks.
  implication: The 22 unit tests passed because they mirrored BC's broken mental model instead of mirroring the real shared contract. Zero tests exercised the real api_get return type.

- timestamp: 2026-04-10T00:00:00Z
  checked: 4 BC call sites calling the broken _api_get — lines 187, 217, 264, 280
  found: Every one of these is wrapped inside a `fetcher()` closure passed to `cached_fetch`. So on a cache miss (first live call) the exception fires; on a cache hit the fetcher is never invoked (which explains why `bc_get_active_fires` and other WFS tools — which bypass _api_get and go through _wfs_fetch — worked: they never touch the broken helper).
  implication: The blocker is confined to the 4 CKAN-dependent code paths: fetch_search_datasets (Test 2), fetch_dataset_details (Test 3), fetch_organizations, fetch_tags. bc_query_features (Test 9) cascades because it calls fetch_dataset_details internally to decide WFS-vs-file routing. bc_get_active_fires, bc_get_fire_perimeters, bc_get_protected_areas, bc_get_water_wells all passed because they go through _wfs_fetch, not _api_get.

## Resolution

root_cause: |
  src/mcp_canada/modules/british_columbia/client.py:69-71 calls
  `response = await api_get(...); response.raise_for_status(); envelope = response.json()`
  but src/mcp_canada/shared/http.py:api_get already returns parsed JSON (not a
  Response). The first real CKAN call raises AttributeError on line 70 because
  dicts don't have `.raise_for_status`. Unit tests masked this by patching
  api_get with a MagicMock Response wrapper that happens to have both methods.
  The bug exists because BC is the only module that BOTH imports shared
  api_get AND uses the direct-httpx CKAN envelope-unwrapping pattern copied
  from ontario/toronto — the two patterns are mutually exclusive.

fix: |
  Minimum-diff fix — change the 4 lines in british_columbia/client.py:55-78
  to treat api_get's return as parsed JSON:

    async def _api_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = BASE_URL + path
        envelope = await api_get(url, params or {})   # already parsed JSON
        if not isinstance(envelope, dict) or not envelope.get("success", False):
            # CKAN success envelope is {"success": bool, "result": ...}
            raise httpx.HTTPStatusError(
                f"CKAN returned success=False for {path}",
                request=httpx.Request("GET", url),
                response=httpx.Response(500),
            )
        return envelope.get("result", {})

  Do NOT call `.raise_for_status()` or `.json()` — shared api_get already did
  both. HTTP-level errors (4xx/5xx) are already raised by shared api_get's
  internal `_fetch()` at shared/http.py:55. BC only needs to check CKAN's
  application-level `success: false` envelope.

  Scope: BC-only. Do NOT retrofit shared api_get to return a Response —
  5 other modules (open_parliament, weather/collections, weather/climate, etc.)
  already rely on the parsed-JSON contract and would break.

  Also add fr i18n key for the bc_get_water_wells guard message to fix
  Gap 4 (Test 13) — unrelated to _api_get but noted while investigating.

verification: |
  Confirmed via file reads + grep — not yet applied or tested. Next step for
  the fix agent:
    1. Apply the 4-line _api_get patch above.
    2. Add a unit test that patches `shared.http.api_get` (not
       `british_columbia.client.api_get`) and returns a raw dict envelope to
       exercise the real contract. This would have caught the bug.
    3. Run tests/integration/test_tool_scenarios.py::TestBcToolScenarios
       against the live CKAN endpoint with `-m integration --timeout=120`.
    4. Re-run the 4 UAT prompts for Tests 2, 3, 9, 14.
    5. Fix Gap 4 (Test 13) separately — route the bc_get_water_wells guard
       message through shared/i18n.py t() with an fr translation key.

files_changed: []

## Why Unit Tests Missed It

The test helper `_make_http_response()` in __tests__/test_client.py:25-31 built a MagicMock with both `.raise_for_status()` and `.json()` attributes, then every test patched `mcp_canada.modules.british_columbia.client.api_get` to return that fake Response. This mirrored BC's buggy mental model: "api_get returns a Response, I call .raise_for_status()/.json() on it." The real shared api_get returns a dict. No test ever exercised the real contract.

### Test improvement suggestion
Add one "contract" test per module that patches shared/http.py:api_get (not the module-local import) with an AsyncMock returning a raw dict, and verifies the module handles it correctly. Example:

```python
@pytest.mark.asyncio
async def test_api_get_handles_real_shared_contract(sample_ckan_package_search_response):
    """_api_get must handle shared api_get's parsed-JSON return correctly."""
    from mcp_canada.modules.british_columbia import client as bc_client
    with patch(
        "mcp_canada.shared.http.api_get",
        new=AsyncMock(return_value=sample_ckan_package_search_response),
    ):
        results, _ = await bc_client.fetch_search_datasets(q="fire")
    assert isinstance(results, list)
```

Patching `mcp_canada.shared.http.api_get` instead of `mcp_canada.modules.british_columbia.client.api_get` forces the module under test to go through the real import chain and exposes contract mismatches.

## Gap Scope

Single root cause covers:
- Gap 1 (Test 2) — bc_search_datasets — direct _api_get call at line 187.
- Gap 2 (Test 3) — bc_get_dataset_details — direct _api_get call at line 217.
- Gap 3 (Test 9) — bc_query_features — cascades because it calls fetch_dataset_details internally for WFS routing.
- Gap 5 (Test 14) — integration suite 7 failures — all CKAN-dependent scenarios go through the same broken _api_get; WFS-only scenarios pass.

Gap 4 (Test 13) is a SEPARATE bug (hardcoded English guard message, unrelated to _api_get) and is not addressed by this fix.
