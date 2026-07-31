---
phase: 21-new-brunswick-government-open-data
reviewed: 2026-07-30T18:50:00Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - src/mcp_canada/modules/new_brunswick/__init__.py
  - src/mcp_canada/modules/new_brunswick/constants.py
  - src/mcp_canada/modules/new_brunswick/schemas.py
  - src/mcp_canada/modules/new_brunswick/client.py
  - src/mcp_canada/modules/new_brunswick/tools.py
  - src/mcp_canada/modules/new_brunswick/prompts.py
  - src/mcp_canada/modules/new_brunswick/resources.py
  - src/mcp_canada/modules/new_brunswick/__tests__/__init__.py
  - src/mcp_canada/modules/new_brunswick/__tests__/conftest.py
  - src/mcp_canada/modules/new_brunswick/__tests__/test_client.py
  - src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py
  - src/mcp_canada/modules/new_brunswick/__tests__/test_prompts_resources.py
  - src/mcp_canada/shared/arcgis_hub.py
  - src/mcp_canada/shared/__tests__/test_arcgis_hub.py
  - tests/integration/test_tool_scenarios.py
findings:
  critical: 1
  warning: 4
  info: 1
  total: 6
status: issues_found
---

# Phase 21: Code Review Report

**Reviewed:** 2026-07-30T18:50:00Z
**Depth:** standard
**Files Reviewed:** 15 (CLAUDE.md, README.md, TOOLS.md read as reference/context only — no findings against them; TOOLS.md is auto-generated from live docstrings/signatures and matches the code, CLAUDE.md's New Brunswick section is accurate)
**Status:** issues_found

## Summary

The module is well structured and most of the specific risk areas called out for this
phase check out clean on direct inspection: every ArcGIS `where` clause built from a
caller string runs through `_escape_sql_value` (apostrophes are correctly doubled,
verified against `_escape_sql_value("21G'15") == "21G''15"` and equivalent tests for
county/community/street/status), `civic_number` is interpolated unquoted as a real int
(no string-injection surface), the two new `shared/arcgis_hub.py` functions
(`list_arcgis_server_services`, `get_arcgis_server_layers`) are purely additive and
don't touch the `where=None` / empty-`q` code paths the CLAUDE.md pitfalls warn about,
the 511 key is never interpolated into any exception message or log line that reaches
an error envelope, and the 22-tool manifest is proven bidirectionally consistent by
`TestManifestMatchesShippedSurface` (not just an alias-equality check). TOOLS.md and
CLAUDE.md's New Brunswick sections both describe what the code actually does.

The one BLOCKER is a real, provable gap in the three `FILTER_REQUIRED_TOOLS` guards
(`nb_get_parcels`, `nb_get_civic_addresses`, and to a lesser extent `nb_get_wetlands`):
the guard only checks argument *truthiness*, and the `_upper_contains_clause` helper
never neutralizes SQL `LIKE` wildcard metacharacters — so a single-character argument
(`county="%"`) satisfies "a filter was provided" while producing a WHERE clause that
matches the entire 604,520-row layer, exactly the outcome T-21-03 exists to prevent.
The warnings are lower-stakes: an unparenthesized Solr `fq` concatenation that doesn't
verifiably hold the "never caller-overridable" (T-21-04) guarantee the docstring makes,
a response that echoes the caller's raw unclamped `limit`/`offset` instead of what was
actually sent upstream, an unvalidated negative `limit` in `nb_query_dataset`, and
~277 lines of entirely-unused Pydantic schemas.

## Critical Issues

### CR-01: FILTER_REQUIRED guard is defeated by a single `%` (or whitespace) argument

**File:** `src/mcp_canada/modules/new_brunswick/client.py:871-888, 946-964, 1032-1113`
**File:** `src/mcp_canada/modules/new_brunswick/tools.py:665-673, 710-725`

**Issue:** T-21-03 exists specifically so `nb_get_parcels` (604,520 rows) and
`nb_get_civic_addresses` (373,172 rows) never hit the network with an effectively
unfiltered query. Both the tool-layer pre-check (`if ... and not county:` /
`if ... and not community and not street ...:`) and the client-layer
`_require_any_filter` (`if any(filters): return`) only test Python truthiness. Two
independent gaps both defeat the guard:

1. **Whitespace bypass.** `county=" "` is truthy, so the guard is satisfied. It then
   flows into `_upper_contains_clause("COUNTY", " ")` → `UPPER(COUNTY) LIKE '% %'`,
   which matches every county containing a space — e.g. `"Saint John"` (one of NB's 15
   counties, per `data://nb/counties`). A caller believing they've been rejected for
   "no filter" instead silently gets an entire county back.

2. **LIKE-wildcard bypass (the more severe one).** `_escape_sql_value` only doubles a
   literal apostrophe — it never escapes `%` or `_`, the two SQL `LIKE` metacharacters.
   `_upper_contains_clause(field, value)` builds
   `f"UPPER({field}) LIKE '%{_escape_sql_value(value.upper())}%'"`. Passing
   `county="%"` produces `UPPER(COUNTY) LIKE '%%%'` — three consecutive wildcards,
   semantically identical to a bare `'%'`, i.e. **matches every row in the layer**.
   The same one-character payload works for `nb_get_civic_addresses`
   (`community="%"` or `street="%"`). This is not a narrow edge case: `"%"` is a
   completely ordinary, truthy string that any caller (or a confused LLM agent
   echoing a template placeholder) could pass.

`MAX_RECORDS` (5000) and pagination still cap the single response, so this isn't an
unbounded data dump — but it is a full, silent defeat of the "reject before any
network call" guarantee CLAUDE.md documents for these two layers (up to 5 paginated
network round-trips fetching 5000 essentially-random rows), and the resulting response
looks like a normal, successful, filtered query to the caller.

Neither `test_tools.py` nor `test_client.py` has a test with a whitespace or
wildcard-only filter value — both `_require_any_filter` and the `_upper_contains_clause`
call sites are only exercised with real content ("Bog", "York", "Fredericton", ...).

**Fix:** Escape `%` and `_` in `_escape_sql_value` (or a new LIKE-specific escaper used
by `_upper_contains_clause`) with an explicit `ESCAPE` clause, and strip+require
non-empty content in the guards:

```python
def _escape_sql_value(value: str) -> str:
    return value.replace("'", "''")

def _escape_like_value(value: str) -> str:
    # Escape SQL LIKE metacharacters before the apostrophe doubling, then the
    # containment clause must declare ESCAPE '\' so ArcGIS honours it.
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return _escape_sql_value(escaped)

def _upper_contains_clause(field: str, value: str) -> str:
    return f"UPPER({field}) LIKE '%{_escape_like_value(value.upper())}%' ESCAPE '\\'"
```

```python
def _require_any_filter(tool_name, *filters, layer_record_count):
    if tool_name not in FILTER_REQUIRED_TOOLS:
        return
    if any(f.strip() if isinstance(f, str) else f for f in filters):
        return
    raise InvalidInput(...)
```

And the tool-layer pre-checks (`nb_get_parcels`, `nb_get_civic_addresses`,
`nb_get_wetlands`) need the same `.strip()` treatment on `not county` / `not community`
/ `not street` so the fast-path check agrees with the client's second line of defence.

## Warnings

### WR-01: `extra_fq` can potentially override the "never caller-overridable" NB organization scope (T-21-04)

**File:** `src/mcp_canada/modules/new_brunswick/client.py:184-199`

**Issue:** `_build_fq` concatenates the mandatory `organization:nb` clause and the
caller-supplied `extra_fq` fragment with a bare `AND`, no parentheses:
`f"{NB_ORG_FQ} AND {extra_fq}"`. CKAN's Action API forwards `fq` straight to Solr's
classic Lucene query parser, where mixing `AND`/`OR` without explicit grouping is a
well-documented source of unintended operator precedence (`A AND B OR C` does not
reliably parse as `A AND (B OR C)`). A caller passing something like
`extra_fq="*:* OR organization:xyz"` could plausibly produce a query that is no longer
scoped to `organization:nb` for every result — the exact outcome the docstring
("results ... CANNOT be widened ... no organization parameter to override the New
Brunswick filter (T-21-04)") and the code comment ("Non-overridable — never expose an
`organization` parameter to callers") both promise won't happen.
`test_search_hostile_fq_cannot_displace_nb_clause` only asserts the resulting *string*
starts with the NB clause and contains the hostile fragment — it never asserts on
actual Solr query semantics, so this security property is unverified, not proven.

**Fix:** Group both clauses explicitly so precedence can't be reinterpreted, regardless
of how the caller's fragment is written:

```python
def _build_fq(extra_fq: str | None) -> str:
    if extra_fq:
        return f"({NB_ORG_FQ}) AND ({extra_fq})"
    return NB_ORG_FQ
```

### WR-02: `nb_search_datasets` echoes the caller's raw, unclamped `limit`/`offset` instead of what was actually sent upstream

**File:** `src/mcp_canada/modules/new_brunswick/tools.py:153-162`
**File:** `src/mcp_canada/modules/new_brunswick/client.py:377-398`

**Issue:** `fetch_search_datasets` clamps the outgoing CKAN request to
`clamped_limit = max(1, min(limit, 100))` and `clamped_offset = max(offset, 0)`, but
never returns those clamped values. `nb_search_datasets` then builds its response as
`{**payload, "limit": limit, "offset": offset}` — the tool's own, un-clamped
parameters. Calling with `limit=500, offset=-5` sends `rows=100, start=0` to CKAN but
reports `"limit": 500, "offset": -5` in `_meta`/`data`, which will mislead an agent
computing the next page's offset or reasoning about how many rows were actually
requested.

**Fix:** Have `fetch_search_datasets` return the clamped values in its payload (e.g.
`{"results": [...], "total": N, "limit": clamped_limit, "offset": clamped_offset}`) and
have the tool echo those instead of its own raw parameters.

### WR-03: `nb_query_dataset`'s `limit` isn't validated — a negative value silently truncates from the end instead of erroring

**File:** `src/mcp_canada/modules/new_brunswick/client.py:445-493`

**Issue:** `fetch_query_dataset(dataset_id, resource_index=0, limit=1000, ...)` never
clamps or validates `limit` (unlike `fetch_search_datasets` and
`fetch_gnb_socrata_query`, both of which do). `rows[:limit]` with a negative `limit`
(e.g. `-1`) silently drops the trailing `abs(limit)` rows instead of failing loudly or
returning the intended set, and `"truncated": len(rows) > limit` is always `True` for
any negative `limit` (since `len(rows) >= 0 > limit`), producing a nonsensical
truncation flag rather than a validation error.

**Fix:** Reject `limit <= 0` (or clamp it) the same way `fetch_gnb_socrata_query`
already rejects `limit > MAX_RECORDS`, before any parsing work happens.

### WR-04: Manifest-membership tests only check `.startswith("nb_")`, not the full canonical prefix casing/format used elsewhere in the docstrings

**File:** `src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py:178-181`

**Issue:** `test_every_tool_name_uses_nb_prefix` is the only automated guard tying tool
naming to the module convention, and it only asserts `name.startswith("nb_")`. That's
consistent with the rest of the suite and not itself wrong, but it means a tool named
e.g. `nb__get_x` (double underscore) or `nbget_x`-adjacent typos would still pass, and
nothing in the test suite asserts the module-prefix convention documented in
`.claude/rules/modules.md` beyond the bare prefix check. Low-stakes given
`TestManifestMatchesShippedSurface` already proves bidirectional registration
consistency, but worth tightening if this pattern is copied to a future province module.

## Info

### IN-01: `schemas.py` (277 lines, ~17 Pydantic models) is entirely unused

**File:** `src/mcp_canada/modules/new_brunswick/schemas.py`

**Issue:** No file in the module (`client.py`, `tools.py`, `prompts.py`,
`resources.py`) or its test suite imports anything from `schemas.py` — confirmed by
grepping every model name across the module. `client.py` builds and returns plain
dicts throughout; the Pydantic models never validate or shape a single response. This
differs from the sibling `saskatchewan`/`alberta`/`manitoba` modules, which at least
import their schemas with a `# noqa: F401 — re-exported for downstream plans` marker
in `client.py` to signal the models are intentionally reserved for future use.

**Fix:** Either wire the schemas into `client.py` (even just as a `noqa`-marked import,
matching the sibling-module convention) or remove the file if it isn't planned for use
— as written, it's dead code that will silently drift from the live GeoNB field names
it documents (nothing enforces that `NBFloodHazardArea`, for example, still matches
`out_fields="Sheet_Numb,Technical_,Flood_Haza,Technical1"` in `client.py`).

---

_Reviewed: 2026-07-30T18:50:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
