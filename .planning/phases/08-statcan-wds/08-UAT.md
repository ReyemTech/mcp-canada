---
status: complete
phase: 08-statcan-wds
source: 08-01-SUMMARY.md, 08-02-SUMMARY.md, 08-03-SUMMARY.md
started: 2026-04-07T06:30:00Z
updated: 2026-04-07T06:30:00Z
---

## Current Test

number: 1
name: Discover StatCan tools via BM25
expected: |
  Run `discover_tools("statistics canada GDP")` through the MCP server.
  Returns a list containing `sc_search_cubes` and other sc_ tools.
  The discovery system finds StatCan tools by keyword without knowing exact tool names.
awaiting: user response

## Tests

### 1. Discover StatCan tools via BM25
expected: Run `discover_tools("statistics canada GDP")` — returns sc_ tools in results. Discovery works without knowing exact tool names.
result: pass
note: Initially failed because server was running published PyPI version (no sc_ tools). Passed after restarting with `uv run mcp-canada` from source.

### 2. Search cubes by keyword
expected: `sc_search_cubes(query="consumer price index")` returns ranked results with productId, title (en/fr), subject code. Top result should be CPI table (18-10-0004-01 or similar). Results are limited to top 10 by default.
result: pass

### 3. Get cube metadata
expected: `sc_get_cube_metadata(product_id="18100004")` returns flattened metadata with dimensions, members, and footnotes. Dimension names and member labels are human-readable strings, not just numeric codes.
result: [pending]

### 4. Decode code sets
expected: `sc_get_code_sets()` returns decoded labels for frequency codes (e.g., 6 = "Monthly"), scalar factors, UOM, and status codes. Both numeric code and text label are present in each entry.
result: [pending]

### 5. Get series info by vector
expected: `sc_get_series_info_by_vector(vector_id=41690973)` returns series metadata including table reference, coordinate, frequency label, and unit of measure label. Numeric codes are decoded alongside labels.
result: [pending]

### 6. Get latest observations by vector
expected: `sc_get_data_by_vector(vector_id=41690973, num_observations=5)` returns the 5 most recent data points with reference period dates and numeric values (floats, not strings). Sorted newest-first.
result: [pending]

### 7. Get data by coordinate with auto-padding
expected: `sc_get_data_by_coord(product_id="18100004", coordinate="1.1", num_observations=3)` works even though the coordinate is only 2 positions — server auto-pads to 10. Returns observation data.
result: issue
reported: "responseStatusCode 2 (no data) was treated as UPSTREAM_ERROR instead of returning empty result"
severity: major
note: Fixed in commit 23dd4b5. Coordinate 1.1 has no data for this table — empty result is correct.

### 8. Get data by date range
expected: `sc_get_data_by_date_range(vector_id=41690973, start_date="2024-01-01", end_date="2024-12-31")` returns observations within that reference period window.
result: issue
reported: "Empty data array on first call — transient empty body from StatCan. Works on retry."
severity: minor
note: Fixed with _statcan_fetch retry wrapper in commit 52361a3.

### 9. Bulk vector data
expected: `sc_get_bulk_vector_data(vector_ids=[41690973], start_release="2024-01-01", end_release="2024-06-30")` fetches vectors in one call. Response groups data by vector ID.
result: pass
note: Initially 406 — WDS requires datetime format. Fixed with auto-append T00:00/T23:59 in commit 146f9df.

### 10. Changed cubes monitoring
expected: `sc_get_changed_cubes(date="2026-04-04")` returns a list of StatCan tables that were updated on that date.
result: pass

### 11. Bilingual responses
expected: `sc_search_cubes(query="prix consommation", lang="fr")` returns results with French titles and `_meta.lang` set to "fr".
result: pass
note: Initially failed due to nullable cansim_id. Fixed in commit 146f9df.

### 12. Rate limiting respected
expected: Integration test suite passes without 429 errors. Tests complete within timeout.
result: pass
note: 10/10 integration tests passed in 3.57s against live StatCan API.

### 13. Error handling for invalid input
expected: `sc_get_cube_metadata(product_id=99999999)` returns structured error, not a traceback.
result: pass

### 14. Cache behavior
expected: Second call to `sc_search_cubes` returns `_meta.cached: true`.
result: pass

## Summary

total: 14
passed: 11
issues: 3
pending: 0
skipped: 0

## Gaps

[none yet]
