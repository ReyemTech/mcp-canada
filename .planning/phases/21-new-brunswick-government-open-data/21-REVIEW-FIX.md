---
phase: 21-new-brunswick-government-open-data
fixed_at: 2026-07-30T19:40:29Z
review_path: .planning/phases/21-new-brunswick-government-open-data/21-REVIEW.md
iteration: 1
findings_in_scope: 6
fixed: 6
skipped: 0
status: all_fixed
---

# Phase 21: Code Review Fix Report

**Fixed at:** 2026-07-30T19:40:29Z
**Source review:** .planning/phases/21-new-brunswick-government-open-data/21-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 6 (1 critical, 4 warning, 1 info — `fix_scope: all`)
- Fixed: 6
- Skipped: 0

All fixes were applied TDD-style (failing reproduction test added first, confirmed RED,
then fixed, confirmed GREEN) per `.claude/rules/tests.md`, committed atomically, and
verified against the live GeoNB endpoint where the finding concerned upstream SQL
behavior (CR-01). Full module suite (366 tests), coverage (99.71%, threshold 95%),
`ruff check`, and `pyright` all pass clean after every commit. Full repo suite
(3550 tests) also passes.

## Fixed Issues

### CR-01: FILTER_REQUIRED guard defeated by a single `%` (or whitespace) argument

**Files modified:** `src/mcp_canada/modules/new_brunswick/client.py`,
`src/mcp_canada/modules/new_brunswick/tools.py`,
`src/mcp_canada/modules/new_brunswick/__tests__/test_client.py`,
`src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py`

**Commit:** `84192e3`

**Applied fix:** Both defects confirmed real and independently exploitable before
fixing (see live verification below), then closed:

1. Added `_escape_like_value()` — escapes SQL `LIKE` metacharacters (`%`, `_`, and the
   escape character `\` itself) ahead of `_escape_sql_value`'s apostrophe-doubling.
   `_upper_contains_clause` now calls it and appends `ESCAPE '\'` to the generated
   clause.
2. `_require_any_filter` now tests `f.strip() if isinstance(f, str) else f is not None`
   instead of bare `any(filters)` — a whitespace-only string is rejected, and (as a
   related correctness fix in the same truthiness class) an int filter value of `0`
   (e.g. `civic_number=0`) is no longer mistaken for "not provided".
3. The three tool-layer pre-checks (`nb_get_wetlands`, `nb_get_parcels`,
   `nb_get_civic_addresses`) now route through a new `_is_blank()` helper with the same
   `.strip()` semantics, so the fast-path check agrees with the client's second line of
   defence instead of only catching the truthy/falsy case.

**Live verification (2026-07-30) against `geonb.snb.ca/.../GeoNB_SNB_Parcels/MapServer/0/query`:**
- `UPPER(COUNTY) LIKE '%%%'` (pre-fix, unescaped) → `{"count": 604520}` — confirms the
  reported bypass matches literally every row in the layer.
- `UPPER(COUNTY) LIKE '% %'` (pre-fix, whitespace bypass) → `{"count": 37532}` —
  confirms the whitespace bypass matches every multi-word county.
- `UPPER(COUNTY) LIKE '%\%%' ESCAPE '\'` (post-fix escaping) → `{"count": 0}` — a
  literal `%` now correctly matches nothing.
- `UPPER(COUNTY) LIKE '%YORK%' ESCAPE '\'` (post-fix, real value) → `{"count": 64208}`
  — confirms the `ESCAPE` clause is accepted by the live endpoint and does not break
  ordinary matching (addresses the review's explicit "verify against the live endpoint
  rather than assuming" caution).

Added failing-first reproduction tests at both layers (whitespace bypass, `%`-wildcard
bypass, zero-as-a-real-filter) before applying the fix; updated pre-existing tests that
hardcoded the old (unescaped, unclamped) clause strings to the new `ESCAPE '\'` form.

### WR-01: `extra_fq` could escape the "never caller-overridable" NB organization scope

**Files modified:** `src/mcp_canada/modules/new_brunswick/client.py`,
`src/mcp_canada/modules/new_brunswick/__tests__/test_client.py`

**Commit:** `791f30b`

**Applied fix:** `_build_fq` now wraps both the NB clause and the caller's fragment in
explicit parentheses: `f"({NB_ORG_FQ}) AND ({extra_fq})"`. Strengthened
`test_search_hostile_fq_cannot_displace_nb_clause` (and added a new `TestBuildFq` case)
to assert actual boolean *semantics*, not just string shape: each test substitutes the
NB clause and the hostile fragment's leaf terms with Python `True`/`False` and evaluates
the composed expression under standard `and`/`or` precedence, proving the composed `fq`
can never be true when the NB clause is false — regardless of what operators the
caller's fragment contains.

### WR-02: `nb_search_datasets` echoed raw, unclamped `limit`/`offset`

**Files modified:** `src/mcp_canada/modules/new_brunswick/client.py`,
`src/mcp_canada/modules/new_brunswick/tools.py`,
`src/mcp_canada/modules/new_brunswick/__tests__/test_client.py`,
`src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py`

**Commit:** `f9626dd`

**Applied fix:** `fetch_search_datasets` now includes the clamped `limit`/`offset` it
actually sent upstream in its returned payload. `nb_search_datasets` echoes that payload
directly instead of overwriting it with `{**payload, "limit": limit, "offset": offset}`
(the caller's raw values). Verified `limit=500, offset=-5` now reports `limit=100,
offset=0` in the response, matching what was actually sent to CKAN (`rows=100,
start=0`).

### WR-03: `nb_query_dataset`'s `limit` wasn't validated

**Files modified:** `src/mcp_canada/modules/new_brunswick/client.py`,
`src/mcp_canada/modules/new_brunswick/tools.py`,
`src/mcp_canada/modules/new_brunswick/__tests__/test_client.py`,
`src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py`

**Commit:** `2ff6931`

**Applied fix:** `fetch_query_dataset` now rejects `limit <= 0` with `InvalidInput`
before any network call (including before `fetch_dataset_details`), mirroring the
pattern already used by `fetch_gnb_socrata_query`. Additionally split the tool-layer
`except InvalidInput` handler in `nb_query_dataset`: a negative-limit error is no longer
mislabeled as "Invalid resource index" (which would also have triggered an unnecessary
`fetch_dataset_details` call to compute a meaningless `valid_range`) — only an exception
whose message actually references `resource_index` takes that branch now.

### WR-04: Manifest tool-naming test only checked bare `.startswith("nb_")`

**Files modified:** `src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py`

**Commit:** `a32b398`

**Applied fix:** Replaced the bare `startswith` check with a full-match regex
(`nb_[a-z0-9]+(?:_[a-z0-9]+)*`) enforcing lowercase snake_case with no double
underscores, no missing separator after the prefix, and no trailing underscore. Added a
parametrized negative test (`nb__get_x`, `nbget_x`, `nb_Get_X`, `nb_get_x_`, `nb_`,
`on_get_x`) proving the strengthened check is actually falsifiable — every one of those
malformed names would have passed the old bare `.startswith("nb_")` check.

### IN-01: `schemas.py` (277 lines, ~17 Pydantic models) was entirely unused

**Files modified:** `src/mcp_canada/modules/new_brunswick/client.py`

**Commit:** `734f54b`

**Applied fix:** Confirmed the sibling-module convention by inspecting
`saskatchewan/client.py`, `alberta/client.py`, and `manitoba/client.py` — all three
import every schema class into `client.py` via a single
`from .schemas import (...)  # noqa: F401 — re-exported for downstream plans` block,
even though `client.py` builds and returns plain dicts throughout (schemas document the
live field shapes without enforcing them on the hot path). Matched that exact pattern
for New Brunswick rather than deleting `schemas.py` or guessing at a different
resolution — this was the least ambiguous of the two options the finding raised, since
three sibling modules already establish the convention identically.

## Skipped Issues

None — all 6 in-scope findings were fixed.

---

_Fixed: 2026-07-30T19:40:29Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
