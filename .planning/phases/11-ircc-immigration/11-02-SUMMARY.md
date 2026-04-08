---
phase: 11-ircc-immigration
plan: 02
subsystem: api
tags: [ircc, immigration, xlsx, dataset-registry, client-functions]

requires:
  - phase: 11-ircc-immigration
    provides: "shared/parsers.py fetch_and_parse() (Plan 01)"

provides:
  - "IRCC module skeleton: __init__.py, constants.py, schemas.py, client.py"
  - "DATASET_REGISTRY with 11 dataset categories and all breakdown+lang URL mappings"
  - "11 async client functions returning (list[dict], was_cached) tuples"
  - "ValueError with valid key list for unknown breakdown or unsupported language"

affects: [ircc-tools, plan-03, integration-tests]

tech-stack:
  added: []
  patterns:
    - "Dataset registry triple-nested dict: DATASET_REGISTRY[dataset_key][breakdown_key][lang] = url"
    - "_fetch_dataset private helper: reduces 11 public functions to one-liners"
    - "ValueError for invalid breakdown includes sorted valid key list for agent UX"

key-files:
  created:
    - src/mcp_canada/modules/ircc/__init__.py
    - src/mcp_canada/modules/ircc/constants.py
    - src/mcp_canada/modules/ircc/schemas.py
    - src/mcp_canada/modules/ircc/client.py
    - src/mcp_canada/modules/ircc/__tests__/__init__.py
    - src/mcp_canada/modules/ircc/__tests__/conftest.py
    - src/mcp_canada/modules/ircc/__tests__/test_client.py
  modified: []

key-decisions:
  - "DATASET_REGISTRY triple-nested dict (dataset, breakdown, lang) -> URL: single source of truth"
  - "adhoc_pr English-only enforced at client level via ValueError on lang='fr'"
  - "Operational Processing space-containing filenames stored as-is (httpx handles encoding)"
  - "_fetch_dataset private helper: all 11 public functions are one-liners delegating to it"
  - "conftest uses unittest.mock.patch (AsyncMock) not pytest-mock mocker fixture (not installed)"

patterns-established:
  - "Client pattern: _fetch_dataset(dataset_key, breakdown, lang) -> fetch_and_parse(url)"
  - "Error pattern: ValueError with sorted(registry.keys()) for agent-readable suggestions"

requirements-completed: [IRCC-04, IRCC-05, IRCC-06]

duration: 4min
completed: 2026-04-08
---

# Phase 11 Plan 02: IRCC Module Skeleton Summary

**IRCC dataset registry (11 categories, all breakdown+lang URL mappings) and 11 async client functions backed by shared/parsers.py fetch_and_parse()**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-08T18:54:50Z
- **Completed:** 2026-04-08T18:59:18Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- IRCC module skeleton with MODULE_NAME, MODULE_DESCRIPTION
- DATASET_REGISTRY with all 11 dataset categories: pr, study, work_imp, work_tfwp, ee_admissions, ee_invited, tr_to_pr, asylum, ops, afghan, adhoc_pr
- All breakdown+lang combinations mapped to exact IRCC download URLs (48+ URL entries)
- 11 async client functions, each delegating to _fetch_dataset helper
- ValueError raised with sorted valid key list for unknown breakdown or unsupported language
- 33 unit tests covering URL lookup, ValueError, and French URL variants

## Task Commits

Each task was committed atomically:

1. **Task 1: Create IRCC module skeleton and dataset registry** - `f767d21` (feat)
2. **Task 2 RED: Failing tests for IRCC client functions** - `b0cf9c2` (test)
3. **Task 2 GREEN: Implement IRCC client functions** - `b6a0f1d` (feat)

## Files Created/Modified

- `src/mcp_canada/modules/ircc/__init__.py` - MODULE_NAME and MODULE_DESCRIPTION
- `src/mcp_canada/modules/ircc/constants.py` - DATASET_REGISTRY, CKAN_IDS, all constants (11 datasets)
- `src/mcp_canada/modules/ircc/schemas.py` - Documents dynamic column schema approach
- `src/mcp_canada/modules/ircc/client.py` - 11 async client functions + _fetch_dataset helper
- `src/mcp_canada/modules/ircc/__tests__/__init__.py` - Empty init
- `src/mcp_canada/modules/ircc/__tests__/conftest.py` - mock_fetch_and_parse fixture
- `src/mcp_canada/modules/ircc/__tests__/test_client.py` - 33 unit tests

## Decisions Made

- DATASET_REGISTRY triple-nested dict (dataset, breakdown, lang) -> URL is the single source of truth. Simple, flat, and zero overhead at lookup time.
- adhoc_pr English-only constraint enforced at the client layer — lang='fr' raises ValueError since adhoc_pr breakdown entries have no "fr" key in the registry.
- Operational Processing space-containing filenames stored as-is (httpx handles percent-encoding correctly on its own; pre-encoding would double-encode).
- _fetch_dataset private helper reduces 11 public functions to one-liners, eliminating duplication while keeping the public API clean.
- unittest.mock.patch with AsyncMock used in conftest (pytest-mock not installed in this project).

## Deviations from Plan

None - plan executed exactly as written. parsers.py was already present from Plan 01 execution (git log confirmed it existed).

## Issues Encountered

- conftest.py initially used `mocker` fixture (pytest-mock), but this project uses stdlib unittest.mock. Fixed before RED commit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All 11 client functions are ready for Plan 03 tool layer
- DATASET_REGISTRY is complete and tested
- Plan 03 (tools.py) can import client functions and call them with breakdown + lang params
- No blockers
