---
phase: 16-quebec-government-open-data
plan: 08
subsystem: api
tags: [quebec, bridge, route-filter, bug-fix, tdd]

requires:
  - phase: 16-quebec-government-open-data/07
    provides: "Bridge int->str coercion and _normalize_route zero-padding"
provides:
  - "Exact num_route match in fetch_bridge_structures — no substring fallback"
affects: [16-quebec-government-open-data]

tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - src/mcp_canada/modules/quebec/client.py
    - src/mcp_canada/modules/quebec/__tests__/test_client.py
    - tests/integration/test_tool_scenarios.py

key-decisions:
  - "Removed nom_route substring fallback entirely — exact num_route match is the only reliable filter path"

patterns-established: []

requirements-completed: [QC-BRIDGE-ROUTE-SUBSTRING-FIX]

duration: 2min
completed: 2026-04-12
---

# Phase 16 Plan 08: Quebec Bridge Route Substring Fix Summary

**Removed nom_route substring fallback in fetch_bridge_structures so route='A-20' returns only Autoroute 20 bridges, not Route 204**

## Performance

- **Duration:** 2 min
- **Started:** 2026-04-12T04:13:18Z
- **Completed:** 2026-04-12T04:15:21Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Fixed substring match bug: `"20" in "route 204"` no longer lets Route 204 rows pass the A-20 filter
- Added TestQuebecBridgeRouteSubstringFix with mixed fixture (A-20 + Route 204 rows) proving exact match only
- Tightened integration test to explicitly reject route_num='00204' in A-20 results

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: failing test for substring bug** - `d30d3a9` (test)
2. **Task 1 GREEN: remove nom_route fallback** - `2768478` (fix)
3. **Task 2: tighten integration test** - `bcea3af` (test)

_Note: TDD task has separate RED and GREEN commits_

## Files Created/Modified
- `src/mcp_canada/modules/quebec/client.py` - Removed nom/raw_digits variables and substring fallback at line 704; filter now uses only `num != norm`
- `src/mcp_canada/modules/quebec/__tests__/test_client.py` - Added TestQuebecBridgeRouteSubstringFix class with test_a20_excludes_route_204 and test_route_204_excludes_a20
- `tests/integration/test_tool_scenarios.py` - Added explicit Route 204 rejection assertions in test_bridges_route_filter_row_types

## Decisions Made
- Removed nom_route substring fallback entirely rather than fixing it (e.g., word-boundary regex) because _normalize_route already handles all user input formats and the num_route exact match is the reliable path

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Coverage at 94.47% (below 95% threshold) is pre-existing and not caused by this change. Verified by running coverage before and after — identical result. The fix removed 3 lines of dead code, which can only help coverage.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Bridge route filter is now correct for all route inputs
- All Quebec unit tests pass (151 passed)
- Ruff clean

---
*Phase: 16-quebec-government-open-data*
*Completed: 2026-04-12*
