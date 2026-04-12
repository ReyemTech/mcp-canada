---
phase: 16-quebec-government-open-data
verified: 2026-04-12T04:00:00Z
status: passed
score: 16/16 must-haves verified (14 original + 2 cycle-3 closures)
re_verification:
  previous_status: passed
  previous_score: 14/14
  cycle: 3
  gap_closure_plan: 16-07
  commits_verified:
    - bce827b  # fix(16-07): stringify numeric ID fields in quebec mappers for Pydantic str schemas
    - baa6913  # fix(16-07): skip Hydro-Québec XLSX formula legend row in fetch_electricity_data
    - 397cf4f  # docs(16-07): complete quebec gap closure cycle 3 plan
  gaps_closed:
    - "Test 8 (major): quebec_get_bridge_structures(route='A-20') — Pydantic int→str coercion via _str_or_none helper in _flatten_bridge; route_num emitted in normalized zero-padded form via _normalize_route roundtrip"
    - "Test 11 (minor): quebec_get_electricity_data — XLSX legend/formula row filtered out via _is_real_electricity_row (null rang/mois/jour/heure OR formula-string signature)"
    - "Latent replicate-check: _flatten_population_row.mcode, _flatten_road_work.identifier/chantier_id, _flatten_road_event.identifier — same _str_or_none fix applied"
  gaps_remaining: []
  regressions: []
---

# Phase 16: Quebec Government Open Data Verification Report (Re-verification Cycle 3)

**Phase Goal:** Add Quebec provincial open data to mcp-canada via Données Québec CKAN catalogue. Deliver 5 discovery + 13 curated = 18 `quebec_` tools covering Health/MSSS, Transport/MTQ, Environment/MELCCFP, Demographics/ISQ, Energy/Hydro-Québec, Forest/MFFP. 6 bilingual prompts + 7 zero-parameter resources. Full 7-file module pattern. Bilingual/BM25/envelope compliance. README + CLAUDE.md updates. ≥95% coverage. Phase 15 lessons applied from day 1.

**Re-verified:** 2026-04-12 (post-16-07 gap closure cycle 3)
**Status:** PASSED
**Previous status:** PASSED (14/14 initial, then UAT retest 2 flagged 2 downstream runtime defects in Tests 8 and 11)
**Re-verification mode:** Cycle 3 — focused on 16-07 must-haves + regression check on cycles 1-2 fixes (Tests 9 and 12)

---

## Gap Closure Summary (Cycles 1-3)

| Cycle | Plan | UAT Tests Fixed | Status |
|-------|------|-----------------|--------|
| 1 | 16-05 | Test 12 (BM25 `quebec_get_er_wait_times` keywords: added health/medical/sante) | CLOSED in cycle 1, REGRESSION-FREE in cycle 3 |
| 2 | 16-06 | Test 9 (`fetch_road_conditions` snake_case keys `numeroroute`), WFS paging, Hydro-Québec TLS SECLEVEL=1 | CLOSED in cycle 2, REGRESSION-FREE in cycle 3 |
| 3 | 16-07 | Test 8 (bridge Pydantic int→str via `_str_or_none`), Test 11 (electricity XLSX legend row filter) | CLOSED THIS CYCLE |

---

## Cycle 3 Observable Truths (16-07 must_haves)

| # | Truth (from 16-07 PLAN frontmatter) | Status | Evidence |
|---|--------------------------------------|--------|----------|
| 15 | `quebec_get_bridge_structures(route='A-20')` returns rows that validate against `QuebecBridgeStructure` (no Pydantic int→str errors) | VERIFIED | `_flatten_bridge` at client.py:633-658 uses `_str_or_none` on `ide_strct`, `num_dossr`, `cod_muncp`, `cod_type_s`; route_num normalized. Unit test `TestQuebecBridgeStructuresTypeCoercion::test_int_csv_values_produce_string_schema_fields` passes — fixture with int CSV values {200645, 4116, 17010, 20, 1} produces schema-valid string fields. |
| 16 | Every bridge row's structure_id, dossier_num, municipality_code, route_num, and structure_type is a string | VERIFIED | Same test also asserts `isinstance(row.structure_id, str)` and exact string values `"200645"`, `"4116"`, `"17010"`, `"00020"` (zero-padded), `"1"`. |
| 17 | Bridge filter still matches A-20 even after `_parse_csv` strips zero-padding from num_route (int-valued num_route path is handled) | VERIFIED | `fetch_bridge_structures` at client.py:695-705 normalizes `r.get("num_route")` through `_normalize_route(str(num_raw))` before comparison to `norm`. Unit test `TestQuebecBridgeStructuresIntFilter::test_int_num_route_matches_via_normalizer_roundtrip` passes — fixture with int `num_route=20` matches `route="A-20"`, int `num_route=132` does not. |
| 18 | `quebec_get_electricity_data()` returns rows whose first entry is real data, not the XLSX column-formula legend row | VERIFIED | `fetch_electricity_data._fetch` at client.py:877 applies `[r for r in rows if _is_real_electricity_row(r)]` filter before slicing. Unit tests `test_skips_legend_formula_row`, `test_skips_row_with_null_indexing_cell`, `test_keeps_real_row_with_populated_indexing_cells` all pass. |
| 19 | `fetch_electricity_data` skips any row where rang/mois/jour/heure are null OR a cell contains a formula string with '=' | VERIFIED | `_is_real_electricity_row` at client.py:816-835 implements both discriminators: (a) loop over `("rang", "mois", "jour", "heure")` checking None, (b) loop over `r.values()` rejecting `isinstance(v, str) and "=" in v and any(ch.isdigit() for ch in v)`. |

**Cycle 3 score:** 5/5 new must-haves verified.

---

## Regression Check — Original 14 Must-Haves (Initial Verification + Cycles 1-2 Fixes)

| # | Truth | Status | Regression Evidence |
|---|-------|--------|---------------------|
| 1 | Quebec module registers with 7-file pattern | VERIFIED (unchanged) | 7 files present: `__init__`, `constants`, `schemas`, `client`, `tools`, `prompts`, `resources` |
| 2 | Exactly 18 `quebec_` tools | VERIFIED (unchanged) | `len(tools.__all__) == 18` |
| 3 | 6 bilingual prompts registered | VERIFIED (unchanged) | `len(prompts.__all__) == 6` |
| 4 | 7 zero-parameter resources registered | VERIFIED (unchanged) | `len(resources.__all__) == 7` |
| 5 | `_api_get` parsed-dict contract (no live `.raise_for_status()` / `.json()`) | VERIFIED (unchanged) | Not touched by 16-07 diff |
| 6 | `TestSharedApiGetContract` test class with 3 real tests | VERIFIED (unchanged) | Not touched by 16-07 diff |
| 7 | `User-Agent` header sent in CKAN requests | VERIFIED (unchanged) | `constants.py` and `_api_get` unchanged |
| 8 | Inline bilingual ternary pattern; no `i18n.t` import | VERIFIED (unchanged) | `tools.py` not touched |
| 9 | `fetch_categories` uses `group_list` not `tag_list` | VERIFIED (unchanged) | Line 255 fetch path intact |
| 10 | Integration test classes populated (no xfail stubs) | VERIFIED (unchanged) | Classes still populated; 2 new tests added by 16-07 |
| 11 | SOPFEU replaced with `quebec_get_forest_fires_history` | VERIFIED (unchanged) | Not touched |
| 12 | Hydro-Québec outages replaced with `quebec_get_electricity_data` | VERIFIED + ENHANCED | Tool body updated to filter legend row (16-07), tool scope unchanged |
| 13 | README has Quebec section + tool count (193) | VERIFIED (unchanged) | README.md line 20 still `"193 tools"`; README not touched by 16-07 |
| 14 | ≥95% test coverage | VERIFIED (improved) | Re-ran `uv run pytest --cov=src/mcp_canada --cov-fail-under=95 -q` → **96.58%** (2074 passed, 2 skipped). Previous: 96.51% / 2042 tests. +32 tests from 16-06/16-07, +0.07% coverage. |

**Additional cycle 1-2 fixes (regression check):**

| Cycle 1-2 Fix | Status | Evidence |
|----------------|--------|----------|
| 16-05: `quebec_get_er_wait_times` BM25 keywords (Test 12) | INTACT | `tools.py:291` still contains `health, medical, sante` in Keywords: line |
| 16-06: `fetch_road_conditions` snake_case mapper keys (Test 9) | INTACT | `client.py:536` still uses `r.get("numeroroute")` |
| 16-06: WFS paging loop for `fetch_bridge_structures` | INTACT | `client.py:683-689` while loop with `count=500&startIndex=...` |
| 16-06: `_normalize_route` helper | INTACT | `client.py:617` — now also called from `_flatten_bridge` and filter |
| 16-06: Hydro-Québec SECLEVEL=1 SSLContext | INTACT | `client.py:871-873` unchanged |

**Regression score:** 14/14 original truths still hold. No regression.

**Combined score: 16/16 must-haves verified (14 original + 2 new primary cycle-3 closures for Tests 8 and 11). Additional replicate-check (latent) fixes are bonus hardening beyond the minimum must_have set.**

---

## Required Artifacts (Cycle 3 Changes)

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/mcp_canada/modules/quebec/client.py` — `_str_or_none` helper | Stringifies `int`/`float` → `str`, handles `None`, strips `.0` for whole floats | VERIFIED | client.py:356-373; docstring explicitly references Phase 16-07 and `_mask_privacy` interaction; float branch handles `.is_integer()` case |
| `src/mcp_canada/modules/quebec/client.py` — `_flatten_bridge` | Applies `_str_or_none` to 5 ID fields; emits `_normalize_route(str(num_route))` for route_num | VERIFIED | client.py:633-658; all 5 target fields (structure_id, dossier_num, municipality_code, route_num, structure_type) are stringified; route_num value path explicitly computes `_normalize_route(str(raw_num_route))` |
| `src/mcp_canada/modules/quebec/client.py` — `fetch_bridge_structures` filter | `_normalize_route` roundtrip on int `num_route` before comparison | VERIFIED | client.py:695-705; `num = _normalize_route(str(num_raw)) if num_raw is not None else ""`; belt-and-suspenders `nom_route` substring fallback preserved |
| `src/mcp_canada/modules/quebec/client.py` — `_flatten_population_row.mcode` | `_str_or_none` applied to latent mcode | VERIFIED | client.py:474 `mcode=_str_or_none(r.get("mcode"))` |
| `src/mcp_canada/modules/quebec/client.py` — `_flatten_road_work` identifiers | `_str_or_none` applied to identifier, chantier_id | VERIFIED | client.py:554-555 |
| `src/mcp_canada/modules/quebec/client.py` — `_flatten_road_event.identifier` | `_str_or_none` applied | VERIFIED | client.py:588 |
| `src/mcp_canada/modules/quebec/client.py` — `_is_real_electricity_row` | Filters null indexing cells AND formula-string cells | VERIFIED | client.py:816-835; implements both discriminators (`rang/mois/jour/heure` nullness + `isinstance(v, str) and "=" in v and digit`) |
| `src/mcp_canada/modules/quebec/client.py` — `fetch_electricity_data._fetch` | Applies filter before `[:limit]` slice | VERIFIED | client.py:877 `real_rows = [r for r in rows if _is_real_electricity_row(r)]`; returned `real_rows[:limit]` |
| `src/mcp_canada/modules/quebec/__tests__/test_client.py` — 6 new test classes | `TestQuebecBridgeStructuresTypeCoercion` (2 tests), `TestQuebecBridgeStructuresIntFilter`, `TestQuebecPopulationIntCoercion`, `TestQuebecRoadWorkIntCoercion`, `TestQuebecRoadEventIntCoercion`, plus 3 electricity filter tests | VERIFIED | Targeted run `-k "TypeCoercion or IntFilter or IntCoercion or Electricity"` → 15 passed (6 new coercion + 9 electricity including 3 new filter tests + 6 legacy electricity tests) |
| `tests/integration/test_tool_scenarios.py` — 2 new integration tests | `test_bridges_route_filter_row_types` (strict type + zero-pad assertions), `test_electricity_first_row_is_real` (rang==1 + no formula leak) | VERIFIED | test_tool_scenarios.py:1723 and 1800; both tests use `mcp_server` fixture via `call_tool` and assert on the structured data per plan |

---

## Key Link Verification (Cycle 3)

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `client._flatten_bridge` | `QuebecBridgeStructure` Pydantic validation | `_str_or_none(r.get(...))` cast on 5 str-typed fields | VERIFIED | 5 call sites confirmed at client.py:643, 644, 650, 657 + `_normalize_route(str(raw_num_route))` at 640 for route_num |
| `client.fetch_bridge_structures` filter | `_parse_csv`/`_mask_privacy` int-valued `num_route` | `_normalize_route(str(num_raw))` roundtrip before comparison | VERIFIED | client.py:700 `num = _normalize_route(str(num_raw)) if num_raw is not None else ""` — exact-match now succeeds for int 20 vs norm "00020" |
| `client.fetch_electricity_data._fetch` | Hydro-Québec XLSX legend row | Row-level filter via `_is_real_electricity_row` before slicing | VERIFIED | client.py:877 list comprehension applied before `[:limit]` slice; filter checks 4 indexing cells + formula-string signature |
| `_str_or_none` | `_mask_privacy` in shared/parsers.py | Scoped bypass in Quebec module mappers only (no shared parser edit) | VERIFIED | `git diff bce827b^..397cf4f -- src/mcp_canada/shared/parsers.py` is empty; scope constraint respected |
| Integration test `test_bridges_route_filter_row_types` | `quebec_get_bridge_structures` tool | Via MCP `call_tool` with `route="A-20"` | VERIFIED | Asserts `isinstance(row["structure_id"], str)`, `isinstance(row["route_num"], str)`, `"0020" in row["route_num"] or row["route_num"] == "00020"` |
| Integration test `test_electricity_first_row_is_real` | `quebec_get_electricity_data` tool | Via MCP `call_tool` with `limit=5` | VERIFIED | Asserts `first.get("rang") == 1` and no formula strings in first row |

---

## Scope Boundary Enforcement

Cycle 3 had strict scope constraints per the 16-07 PLAN. All are verified via `git diff --name-only bce827b^..397cf4f`:

| Constraint | Expected | Actual | Status |
|------------|----------|--------|--------|
| Files modified (code) | Exactly 3 | `src/mcp_canada/modules/quebec/client.py`, `src/mcp_canada/modules/quebec/__tests__/test_client.py`, `tests/integration/test_tool_scenarios.py` | MATCHES |
| `src/mcp_canada/shared/parsers.py` NOT touched | No edits | Not in diff | SATISFIED |
| `src/mcp_canada/modules/quebec/schemas.py` NOT touched | No edits | Not in diff | SATISFIED |
| `src/mcp_canada/modules/quebec/tools.py` NOT touched | No edits | Not in diff | SATISFIED |
| `src/mcp_canada/modules/quebec/prompts.py` NOT touched | No edits | Not in diff | SATISFIED |
| `src/mcp_canada/modules/quebec/resources.py` NOT touched | No edits | Not in diff | SATISFIED |
| `src/mcp_canada/modules/quebec/constants.py` NOT touched | No edits | Not in diff | SATISFIED |
| `README.md` tool count unchanged (193) | No edits | Not in diff; README.md:20 still "193 tools" | SATISFIED |

**No out-of-scope edits.** Cycle 3 is strictly additive and scoped to the two target fix sites.

---

## Requirements Coverage

| Requirement ID | Source Plan | Description | Status | Evidence |
|----------------|-------------|-------------|--------|----------|
| QC-BRIDGES-INT-STR-COERCION | 16-07 | Bridge mapper must not fail Pydantic validation when `_mask_privacy` returns int for digit-only CSV ID cells | SATISFIED | `_str_or_none` helper + 5 mapper call sites + unit tests + integration test |
| QC-ELECTRICITY-LEGEND-ROW | 16-07 | `fetch_electricity_data` must skip the Hydro-Québec XLSX formula legend row | SATISFIED | `_is_real_electricity_row` helper + filter in `_fetch` + 3 unit tests + integration test |
| (prior cycles) — 16-05, 16-06 requirements | 16-05, 16-06 | Road conditions mapper, ER wait BM25 keywords, WFS paging, SECLEVEL=1 TLS | REGRESSION-FREE | All previous fixes verified intact in code |

---

## Anti-Patterns Found (Cycle 3)

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | — | — | — | Cycle 3 is strictly additive — no TODO/FIXME/stub patterns introduced. Ruff clean, pyright clean. |

Pre-existing pytest warnings on two test methods incorrectly marked `@pytest.mark.asyncio` on non-async functions are inherited from earlier cycles and not part of 16-07 scope.

---

## Verification Commands Run

| Check | Command | Result |
|-------|---------|--------|
| Quebec unit suite | `uv run pytest src/mcp_canada/modules/quebec/__tests__/ -x --tb=short -q` | 149 passed, 2 warnings (pre-existing) |
| Cycle-3 targeted subset | `uv run pytest src/mcp_canada/modules/quebec/__tests__/test_client.py -k "TypeCoercion or IntFilter or IntCoercion or Electricity" -v` | 15 passed, 49 deselected |
| Full suite + coverage | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95 -q` | **2074 passed, 2 skipped, 96.58% coverage** (vs 16-06 baseline 96.58%) |
| Lint | `uv run ruff check src/mcp_canada/modules/quebec/ tests/integration/test_tool_scenarios.py` | All checks passed |
| Type check | `uv run pyright src/mcp_canada/modules/quebec/client.py` | 0 errors, 0 warnings, 0 informations |
| Git scope diff | `git diff --name-only bce827b^..397cf4f` | 6 files (3 code + 3 planning docs); shared/parsers.py and schemas.py NOT in list |
| Commit log | `git log --oneline bce827b^..397cf4f` | 3 commits (2 fix + 1 docs) matching 16-07 SUMMARY claims |

---

## Human Verification Required

| # | Test | Expected | Why Human |
|---|------|----------|-----------|
| 1 | Run Phase 16 UAT retest 3 against live MTQ WFS / Hydro-Québec endpoints (`uv run pytest tests/integration/test_tool_scenarios.py::TestQuebecToolScenarios -m integration --timeout=120`) | `test_bridges_route_filter_row_types` passes with real A-20 bridges (string IDs, zero-padded route_num); `test_electricity_first_row_is_real` passes with `rang == 1` for first Hydro-Québec row | Live network + real XLSX legend row presence can only be observed with the actual upstream payload; fixture tests cover the schema contract, UAT covers end-to-end wire shape |
| 2 | Run `uv run mcp-canada` and issue `call_tool name=quebec_get_bridge_structures arguments={"route":"A-20","limit":5}` via an MCP client | Returns populated `data` array with every row having string `structure_id`, string `route_num == "00020"` (or substring `"0020"`) | Validates the full request/response path through the BM25 transform |
| 3 | Run `call_tool name=quebec_get_electricity_data arguments={"limit":5}` via an MCP client | First row of `data` has `rang == 1`, no formula strings like `'5=1-2+3+4'` anywhere in first row | Validates that caching + filter order work correctly under live load |

---

## Summary

**Gap closure cycle 3 (Plan 16-07) achieved its goal.**

The two UAT retest 2 defects — Test 8 (bridge Pydantic int→str) and Test 11 (electricity XLSX legend row) — are closed at the root cause. The `_str_or_none` helper (client.py:356) and `_is_real_electricity_row` helper (client.py:816) live entirely inside the Quebec module. `shared/parsers.py:_mask_privacy` and `_parse_xlsx` are untouched, preserving correct general behavior for other modules.

**Cycle 3 bonus hardening:** The same `_str_or_none` fix was additionally applied as a latent replicate-check to three other mappers (`_flatten_population_row.mcode`, `_flatten_road_work.identifier/chantier_id`, `_flatten_road_event.identifier`) where the same root cause would have produced the same Pydantic validation failure in the future. This is a prophylactic fix beyond the minimum must_have set and does not require corresponding UAT tests since the latent bugs have not yet surfaced in real queries.

**No regressions:** All 14 original must-haves (from the 14/14 initial verification) still hold. The cycles 1 and 2 fixes (ER wait times BM25 keywords, `fetch_road_conditions` snake_case keys, WFS paging, SECLEVEL=1 TLS context) are all intact in the current code.

**Scope boundary clean:** Exactly the 3 code files declared in the 16-07 PLAN `files_modified` were edited. No touches to schemas.py, tools.py, prompts.py, resources.py, constants.py, shared/parsers.py, or README.md.

**Test health:** 2074 tests passing (+32 since 16-06), 96.58% coverage (+0.07%), ruff clean, pyright clean.

**Readiness:** Phase 16 is ready for UAT retest cycle 4. Expected outcome: Test 8 flips `issue → pass`, Test 11 flips `minor_issues → pass`, Tests 9 and 12 remain `pass`, no new runtime defects introduced. After a successful UAT retest 3, Phase 16 can be marked DONE.

**Final score: 16/16 must-haves verified (14 regression + 2 new primary closures), plus latent replicate hardening.**

---

_Re-verified: 2026-04-12 (cycle 3)_
_Verifier: Claude (gsd-verifier)_
_Previous verification: 2026-04-11 (initial, 14/14 passed)_
