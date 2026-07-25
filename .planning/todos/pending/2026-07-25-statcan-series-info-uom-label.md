---
created: 2026-07-25T00:00:00Z
title: sc_get_series_info_by_vector returns uom_code with no decoded UOM label
area: bug
severity: minor
found_by: 2026-07-25 state reconciliation (08-UAT test 5)
files:
  - src/mcp_canada/modules/statcan/schemas.py:63
  - src/mcp_canada/modules/statcan/client.py:395
  - src/mcp_canada/modules/statcan/resources.py:123
---

## Problem

`SeriesInfo` (`schemas.py:63-77`) exposes `uom_code: int` but no decoded `uom`
string. Live response for vector 41690973 ends at `"uom_code": 17` with no label,
so 08-UAT test 5's expectation ("returns series metadata including ... unit of
measure label") is not met. `frequency` and `scalar_factor` are both decoded in
the same response, so the omission is inconsistent rather than deliberate.

UOM decoding is currently only reachable through the `data://statcan/uom-codes`
resource, which requires the agent to make a second lookup.

## Fix (choose one)

1. Add a `uom: str` field to `SeriesInfo`, decoded the same way `frequency` and
   `scalar_factor` already are. Needs a UOM code map — derive it from
   `getCodeSets` (`object.uom`) rather than hand-writing it, per the lesson from
   the FREQUENCY_CODES defect fixed 2026-07-25.
2. Or amend the 08-UAT test-5 expectation to accept resource-catalog lookup as
   the intended design, and document it in the tool docstring.

## Context

This is Gap 2 of `.planning/phases/08-statcan-wds/08-UAT.md`. Gap 1 (the shifted
FREQUENCY_CODES / SCALAR_FACTOR_CODES maps) was fixed 2026-07-25 — see that
commit for the pattern: transcribe from the published code set, assert literal
labels, and add a live-drift integration guard.
