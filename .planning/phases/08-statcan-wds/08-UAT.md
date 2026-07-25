---
status: diagnosed
phase: 08-statcan-wds
source: 08-01-SUMMARY.md, 08-02-SUMMARY.md, 08-03-SUMMARY.md
started: 2026-04-07T06:30:00Z
updated: 2026-07-25T00:00:00Z
---

## Current Test

[testing complete — tests 3-6 resolved 2026-07-25; see Gaps]

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
result: pass
tested: 2026-07-25 (live, through MCP call_tool)
note: |
  Returns a 12-key flattened dict. Dimensions/members are human-readable and
  bilingual ("Geography"/"Géographie", member "Newfoundland and Labrador" with
  parent_member_id + classification_code). Stated expectation met.
  Defect noted separately: `frequency` decodes frequencyCode 6 as "Bi-monthly"
  on a table whose own title is "Consumer Price Index, monthly". See Gap 1.

### 4. Decode code sets
expected: `sc_get_code_sets()` returns decoded labels for frequency codes (e.g., 6 = "Monthly"), scalar factors, UOM, and status codes. Both numeric code and text label are present in each entry.
result: pass
tested: 2026-07-25 (live, through MCP call_tool)
note: |
  6 code-set families returned; each entry carries code + desc_en + desc_fr.
  Frequency set is proxied live from StatCan and is CORRECT: 6 = "Monthly",
  7 = "Bimonthly", 9 = "Quarterly", 12 = "Annual" (17 codes, 1-21).
  This test is what exposes Gap 1 — the live code set disagrees with the
  hardcoded FREQUENCY_CODES map the other sc_ tools decode against.

### 5. Get series info by vector
expected: `sc_get_series_info_by_vector(vector_id=41690973)` returns series metadata including table reference, coordinate, frequency label, and unit of measure label. Numeric codes are decoded alongside labels.
result: fail
tested: 2026-07-25 (live, through MCP call_tool)
note: |
  Two parts of the expectation are unmet:
   1. frequency label is WRONG — frequencyCode 6 returned as "Bi-monthly"
      (CPI 18100004 is monthly). See Gap 1.
   2. NO unit-of-measure label — the response carries `uom_code: 17` with no
      decoded `uom` field. `SeriesInfo` (schemas.py:63-77) has no `uom` member.
      UOM decoding is only reachable via the data://statcan/uom-codes resource,
      which does not satisfy "unit of measure label" in the response. See Gap 2.
  Everything else present and correct: product_id, coordinate, vector_id,
  scalar_factor ("units"), decimals, terminated, title_en/title_fr.

### 6. Get latest observations by vector
expected: `sc_get_data_by_vector(vector_id=41690973, num_observations=5)` returns the 5 most recent data points with reference period dates and numeric values (floats, not strings). Sorted newest-first.
result: pass
tested: 2026-07-25 (live, through MCP call_tool)
note: |
  5 rows, newest-first (2026-06-01, 2026-05-01, 2026-04-01, ...), values are
  floats (169.0, 169.6, 168.0). Stated expectation met.
  Two corrections to the test as written:
   - the parameter is `n`, not `num_observations` (Pydantic rejects the latter
     before the tool body runs) — the expectation text was never executable.
   - each row repeats the Gap 1 defect: consecutive one-month-apart reference
     periods are all labelled `"frequency": "Bi-monthly"`.

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
passed: 12
failed: 1
issues: 3
pending: 0
skipped: 0

## Gaps

### Gap 1 — FREQUENCY_CODES map is shifted and truncated (major, agent-visible wrong data)

`src/mcp_canada/modules/statcan/constants.py:28-41` hardcodes a frequency map that
does not match StatCan's own code set (confirmed live via `sc_get_code_sets`, test 4):

| code | hardcoded (wrong) | StatCan live (correct) |
|------|-------------------|------------------------|
| 2  | Weekly (Sunday) | Weekly |
| 5  | Monthly | *(not a StatCan code)* |
| 6  | **Bi-monthly** | **Monthly** |
| 7  | **Quarterly** | **Bimonthly** |
| 8  | Semi-annual | *(not a StatCan code)* |
| 9  | **Annual** | **Quarterly** |
| 10 | Every 2 years | *(not a StatCan code)* |
| 11 | **Every 3 years** | **Semi-annual** |
| 12 | **Irregular** | **Annual** |
| 13 | Every 2 years | Every 2 years |
| 14-21 | *missing* | Every 3/4/5/10 years, Occasional, Occasional Quarterly/Monthly/Daily |

Impact: every `sc_` tool that decodes frequency reports the wrong cadence. Monthly
CPI reads "Bi-monthly"; a quarterly series would read "Annual". Four call sites:
`client.py:321` (cube metadata), `:395` (series info), `:438`, `:471` (observations).
`resources.py:40-52` (`data://statcan/frequency-codes`) repeats the same wrong table.

Why the unit tests miss it: `__tests__/test_client.py` builds its expected value with
`FREQUENCY_CODES.get(raw["frequencyCode"])` — asserting the map against itself. The
assertions are tautological and pass for any map, correct or not.

Fix: replace the hardcoded map with StatCan's published code set (or derive it from
`getCodeSets` at runtime with a long TTL), update the `data://` resource catalog to
match, and replace the self-referential assertions with literal expected labels.

### Gap 2 — sc_get_series_info_by_vector returns no UOM label (minor)

`SeriesInfo` (`schemas.py:63-77`) exposes `uom_code: int` but no decoded `uom`
string, so the test-5 expectation "unit of measure label" is not met. Either add a
`uom` field decoded from the live UOM code set, or amend the UAT expectation to
accept resource-catalog lookup as the intended design.
