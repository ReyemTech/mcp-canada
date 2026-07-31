---
phase: 21
fixed_at: 2026-07-31T01:20:00Z
review_path: Codex automated review of PR #6 (findings supplied inline, orchestrator-verified against code and live GeoNB layers before dispatch — not sourced from a committed REVIEW.md)
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 21: New Brunswick — Codex Review Fix Report

**Fixed at:** 2026-07-31T01:20:00Z
**Source review:** Codex's automated review of PR #6 (`gsd/phase-21-new-brunswick-government-open-data`), five findings supplied directly by the orchestrator with inline evidence, independently re-verified against the implemented code and (for F4/F5) against the live GeoNB endpoints prior to dispatch.
**Iteration:** 1

**Summary:**
- Findings in scope: 5 (P1: F1, F2 · P2: F3, F4, F5)
- Fixed: 5
- Skipped: 0

Each fix was implemented TDD-first (failing reproduction test written and run red, then the
minimal fix applied and the test run green) and committed atomically. A sixth commit strengthens
the F4/F5 live integration coverage. Full verification (`uv run pytest`, coverage,
`uv run ruff check`, `uv run pyright`, `scripts/generate_catalog.py --check`) is green — see
**Verification** below.

## Fixed Issues

### F1: `extra_fq` delimiter-breaking escapes the NB organization scope

**Files modified:** `src/mcp_canada/modules/new_brunswick/client.py`, `src/mcp_canada/modules/new_brunswick/__tests__/test_client.py`
**Commit:** `264449c`
**Applied fix:** `_build_fq` wrapped a caller-supplied `extra_fq` fragment in parentheses to stop
it widening the CKAN discovery scope past `organization:nb` (T-21-04), but assumed the fragment
was already a well-formed Lucene atom. A fragment carrying its own unbalanced parenthesis (e.g.
`"*:* ) OR (*:*"`) closed `_build_fq`'s own wrapping paren early, composing
`"(organization:nb) AND (*:* ) OR (*:*)"` — whose trailing `OR (*:*)` matches every non-NB dataset
regardless of the NB clause. Added `_validate_extra_fq`, called from `_build_fq` before
composition: nesting-depth tracking (not a plain open/close count — the attack string has equal
counts of `(`/`)` but in the wrong order, so a count comparison alone does not catch it) rejects
any fragment whose depth goes negative or fails to return to zero, and a parity check rejects an
unbalanced double quote. Both raise `InvalidInput` (→ `INVALID_INPUT` via `@upstream_guard`),
before any fq string is composed or any network call is made. Also strengthened
`TestBuildFq.test_hostile_extra_fq_cannot_widen_result_past_nb_scope`'s neighbourhood: the
existing test only ever fed a *balanced* hostile fragment and its truth-table evaluator assumed a
well-formed atom — added `test_delimiter_breaking_extra_fq_is_rejected_before_composition`,
`test_unbalanced_double_quote_extra_fq_is_rejected`, and a positive control
(`test_balanced_extra_fq_with_nested_parens_still_composes`) proving legitimate Lucene grouping
still works.

### F2: caller `limit` is never clamped for curated GeoNB tools

**Files modified:** `src/mcp_canada/modules/new_brunswick/client.py`, `src/mcp_canada/modules/new_brunswick/__tests__/test_client.py`
**Commit:** `3ecf46f`
**Applied fix:** `_geonb_query` passed the caller's `limit` straight into
`arcgis_hub.query_feature_service`'s `max_records`, which *replaces* that function's own
`MAX_RECORDS` default rather than being bounded by it — `MAX_RECORDS` appeared only as each
curated tool's `limit` *default*, never as an enforced cap, so `fetch_crown_land(limit=10_000_000)`
forwarded `max_records=10000000` and `fetch_crown_land(limit=0)` forwarded `max_records=0`
(silently returning an empty success). Added a single guard at the top of `_geonb_query` —
`if not (1 <= limit <= MAX_RECORDS): raise InvalidInput(...)` — before the cache key is built or
any network call is made. Because every curated GeoNB tool's client function delegates to
`_geonb_query` (crown land, flood hazard, historical floods, wetlands, contaminated sites, parcels,
civic addresses, health facilities, public schools), the bound is now inherited in one place rather
than needing to be repeated per tool. This also closes the lower-bound gap in the raw escape hatch
`fetch_geonb_layer_features`, whose own pre-check only rejected `limit > MAX_RECORDS` and left
`limit <= 0` open — that check is now a redundant (harmless) first line of defence. New tests:
`TestGeonbQueryHelper` gained direct coverage of the too-large, zero, negative and at-the-cap
cases (each asserting `mock_query.assert_not_awaited()` for the rejected cases); `TestFetchCrownLand`
gained two tests proving a curated tool inherits the guard through `_geonb_query` rather than
needing its own check.

### F3: Socrata query accepts a non-positive limit

**Files modified:** `src/mcp_canada/modules/new_brunswick/client.py`, `src/mcp_canada/modules/new_brunswick/__tests__/test_client.py`
**Commit:** `193c091`
**Applied fix:** `fetch_gnb_socrata_query` validated only `limit > MAX_RECORDS`, so `limit=0` or a
negative value was sent upstream as Socrata's `$limit` — producing either an upstream error for
caller-invalid input, or a payload whose `truncated = len(rows) >= limit` calculation is
nonsensically `True` with zero rows. Added `if limit <= 0: raise InvalidInput(...)` immediately
before the existing upper-bound check, matching `fetch_query_dataset`'s established lower-bound
pattern (`client.py` ~line 506) — both checks run before any network call. New tests:
`test_zero_limit_raises_before_any_network_call` and
`test_negative_limit_raises_before_any_network_call`, both asserting
`mock_query.assert_not_awaited()`.

### F4: `nb_get_contaminated_sites` returns no way to locate a site

**Files modified:** `src/mcp_canada/modules/new_brunswick/client.py`, `src/mcp_canada/modules/new_brunswick/tools.py`, `src/mcp_canada/modules/new_brunswick/__tests__/test_client.py`, `tests/integration/test_tool_scenarios.py`
**Commit:** `6e81ebe` (+ `5edda91` for the live integration assertion)
**Applied fix:** `fetch_contaminated_sites`'s `out_fields` omitted `Latitude`/`Longitude` even
though the live `GeoNB_ELG_Contaminated_Sites/0` layer carries both (**live-verified** via a direct
`?f=json` query against `geonb.snb.ca` before committing — HTTP 200, both fields present with
non-null values on at least one feature) and `NBContaminatedSite` in `schemas.py` already declared
them — the tool advertised mapped site locations but returned none. Widened `out_fields` to
`"Status_E,Status_F,FileOpenDate,PidType_E,PidType_F,Latitude,Longitude"` and updated the tool
docstring to state that a result carries its coordinates. New unit test
`test_out_fields_include_latitude_and_longitude` asserts the mocked `query_feature_service` call
receives both field names. The live integration scenario
`test_contaminated_sites_bilingual_status` was strengthened to assert `Latitude`/`Longitude`
presence in a real response and passes against the live endpoint.

### F5: `nb_get_civic_addresses` cannot complete its own documented geocoding workflow

**Files modified:** `src/mcp_canada/modules/new_brunswick/client.py`, `src/mcp_canada/modules/new_brunswick/tools.py`, `src/mcp_canada/modules/new_brunswick/schemas.py`, `src/mcp_canada/modules/new_brunswick/__tests__/test_client.py`, `tests/integration/test_tool_scenarios.py`
**Commit:** `4964e77` (+ `5edda91` for the live integration assertion)
**Applied fix:** `fetch_civic_addresses`'s `out_fields` omitted `LATITUDE`, `LONGITUDE` and `PID`
(only `COUNTY` was already present), so the tool's own documented address → point / address →
parcel workflow could not complete: no point was ever returned, and `PID` — the other
`nb_get_parcels` filter alongside `county` — was unreachable from a result. **Live-verified** via a
direct `?f=json` query against `geonb.snb.ca/.../GeoNB_DPS_Civic_Address/MapServer/0` before
committing (HTTP 200; `LATITUDE`, `LONGITUDE`, `COUNTY`, `PID` all present with real values).
Widened `out_fields` to
`"CIVIC_NUM,STREET,ST_TYPE_E,ST_TYPE_F,COMMUNITY,COUNTY,PID,LATITUDE,LONGITUDE"`, added
`PID: str | None`, `LATITUDE: float | None`, `LONGITUDE: float | None` to the `NBCivicAddress`
schema (matching the live field types — `LATITUDE`/`LONGITUDE` are `esriFieldTypeDouble`), and
updated the tool docstring to describe the completed workflow (including chaining into
`nb_get_parcels` by `pid`, not only `county`). New unit test
`test_out_fields_include_location_and_parcel_linking_fields`. The live integration scenario
`test_civic_address_in_fredericton` was strengthened to assert presence of all four new fields and
passes against the live endpoint.

## Skipped Issues

None — all five findings were fixed.

## Verification

Run inside the isolated fixer worktree (`/tmp/sv-21-reviewfix-g1az6q`, branch
`gsd-reviewfix/21-2095574`) after all five fixes and the integration-test strengthening commit:

| Check | Result |
|---|---|
| `uv run pytest` | 3563 passed, 2 skipped, 369 deselected (integration, run separately below) |
| `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` | 97.39% total, threshold met |
| `uv run ruff check src/ tests/` | All checks passed |
| `uv run pyright` | 0 errors (2 pre-existing warnings, unrelated `weather/climate` module) |
| `uv run python scripts/generate_catalog.py --check` | Catalog is up to date |
| `uv run pytest tests/integration/test_tool_scenarios.py -k "test_contaminated_sites_bilingual_status or test_civic_address_in_fredericton" -m integration` | 2 passed — confirms F4/F5's widened `out_fields` return HTTP 200 (not 400) against the live GeoNB endpoints |

No `21-SECURITY.md` edits were made, per instruction — the orchestrator owns correcting T-21-03 and
T-21-04's dispositions given F1/F2's findings.

---

_Fixed: 2026-07-31T01:20:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
