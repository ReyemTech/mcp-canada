---
created: 2026-07-25T00:00:00Z
title: Fix StatCan FREQUENCY_CODES map — shifted and truncated, ships wrong cadence labels
area: bug
severity: major
found_by: 2026-07-25 state reconciliation (08-UAT tests 3-6, previously left [pending])
files:
  - src/mcp_canada/modules/statcan/constants.py:28
  - src/mcp_canada/modules/statcan/client.py:321
  - src/mcp_canada/modules/statcan/client.py:395
  - src/mcp_canada/modules/statcan/client.py:438
  - src/mcp_canada/modules/statcan/client.py:471
  - src/mcp_canada/modules/statcan/resources.py:40
  - src/mcp_canada/modules/statcan/schemas.py:63
  - src/mcp_canada/modules/statcan/__tests__/test_client.py:19
---

## Problem

`FREQUENCY_CODES` in `statcan/constants.py:28-41` does not match StatCan's published
frequency code set. Confirmed live: `sc_get_code_sets()` (which proxies StatCan's own
`getCodeSets`) returns codes 1-21 with 6 = "Monthly", while the hardcoded map says
6 = "Bi-monthly". The map is shifted from code 6 onward and stops at 13.

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

## Impact

Agent-visible wrong data on every StatCan tool that decodes frequency. Live reproduction
against CPI table 18100004 (a table whose own title reads "Consumer Price Index, monthly"):

```
sc_get_data_by_vector(vector_id=41690973, n=5)
  -> ref_per 2026-06-01, 2026-05-01, 2026-04-01, ...   # one month apart
     "frequency": "Bi-monthly"                          # every row
```

`sc_get_cube_metadata` and `sc_get_series_info_by_vector` report the same wrong label.
A quarterly series would be reported as "Annual". Note `sc_get_code_sets` itself is
correct — it proxies live data — so the server contradicts itself between tools.

## Why tests did not catch it

`__tests__/test_client.py` constructs its expected value with
`FREQUENCY_CODES.get(raw["frequencyCode"], "Unknown")` — asserting the map against
itself (lines 19, 32, 66, 98, 157, 165, 183, 194, 206, 217). Tautological: passes for
any map, correct or not. The UAT test designed to catch this (08-UAT test 4,
"e.g., 6 = Monthly") was left `result: [pending]` and never run until 2026-07-25.

## Fix

1. RED: replace the self-referential assertions with literal expected labels
   (`assert result.frequency == "Monthly"` for frequencyCode 6). Confirm they fail.
2. GREEN: correct `FREQUENCY_CODES` to StatCan's 17-entry set (1, 2, 4, 6, 7, 9,
   11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21) — or derive it from `getCodeSets`
   at runtime behind a long-TTL `cached_fetch`, which cannot drift again.
3. Update `data://statcan/frequency-codes` (`resources.py:40-52`) — it repeats the
   same wrong table, including the French labels.
4. Add an integration test asserting the hardcoded map agrees with live
   `sc_get_code_sets` output, so future drift fails CI rather than shipping.

## Related (smaller, same UAT pass)

`SeriesInfo` (`schemas.py:63-77`) exposes `uom_code: int` but no decoded `uom` label,
so `sc_get_series_info_by_vector` does not meet the 08-UAT test-5 expectation
("unit of measure label"). Either add the decoded field or amend the expectation.
See `.planning/phases/08-statcan-wds/08-UAT.md` Gap 2.
