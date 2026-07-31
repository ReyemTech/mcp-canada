---
phase: 21
fixed_at: 2026-07-31T02:39:12Z
review_path: Second round of Codex automated review of PR #6 (reviewed commit 5660496c88), findings supplied inline by the orchestrator with independent verification against the code and, for G1, against the live upstream — not sourced from a committed REVIEW.md
iteration: 2
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 21: New Brunswick — Codex Review Fix Report (Round 2)

**Fixed at:** 2026-07-31T02:39:12Z
**Source review:** Second round of Codex's automated review of PR #6 (`gsd/phase-21-new-brunswick-government-open-data`, reviewed commit `5660496c88`), four findings supplied directly by the orchestrator with inline evidence. The orchestrator independently verified all four against the implemented code and, for G1, against the live `open.canada.ca` upstream before dispatch — none were re-litigated as false positives.
**Iteration:** 2

**Summary:**
- Findings in scope: 4 (P1: G1, G2 · P2: G3, G4)
- Fixed: 4
- Skipped: 0

Each fix was implemented TDD-first (failing reproduction test written and run red, then the
minimal fix applied and the test run green) and committed atomically as its own commit — including
splitting G1/G2, which both touch `fetch_dataset_details`/`fetch_query_dataset` in `client.py`,
into two independently-reviewable commits rather than one combined diff. Full verification
(`uv run pytest`, coverage, `uv run ruff check`, `uv run pyright`,
`scripts/generate_catalog.py --check`) is green — see **Verification** below. G1 was additionally
verified live, both before and after the fix (see that section).

## Fixed Issues

### G1: `package_show` is unscoped — non-NB datasets escape the advertised NB boundary

**Files modified:** `src/mcp_canada/modules/new_brunswick/constants.py`, `src/mcp_canada/modules/new_brunswick/client.py`, `src/mcp_canada/modules/new_brunswick/tools.py`, `src/mcp_canada/modules/new_brunswick/__tests__/test_client.py`, `src/mcp_canada/modules/new_brunswick/__tests__/test_tools.py`
**Commit:** `b5120aa`
**Applied fix:** `fetch_dataset_details` called `_api_get("package_show", {"id": dataset_id})` with
no `fq` scoping at all — unlike `package_search`, `package_show` takes a bare id/slug, so the
earlier `extra_fq` hardening (`_build_fq`/`_validate_extra_fq`) never touched it. Orchestrator
live-verified before the fix that `dataset_id="6059da1d-e1da-4f2b-a420-b5c2a130eeaa"` returned a
full Environment Canada dataset ("ec" organization) through `nb_get_dataset_details`, whose
docstring states the NB filter "CANNOT be widened" (T-21-04). `nb_query_dataset` inherited the same
hole via its call to `fetch_dataset_details`.

Added `NB_ORG_NAME: Final[str] = "nb"` in `constants.py` as the single source of truth for the
organization name — `NB_ORG_FQ` is now derived from it (`f"organization:{NB_ORG_NAME}"`) instead of
duplicating the literal. `fetch_dataset_details` now reads `raw.get("organization")` after
`package_show` returns and raises `NotFound` (→ `NOT_FOUND`, never `InvalidInput`, per the finding's
explicit instruction) when `organization.name != NB_ORG_NAME`. A missing or `None` `organization`
key fails closed — `organization.get("name") if isinstance(organization, dict) else None` yields
`None`, which never equals `"nb"`, so a malformed record is rejected rather than silently treated as
NB-scoped. Because `fetch_query_dataset` calls `fetch_dataset_details` directly, it inherits the
guard with no code change of its own; `nb_query_dataset` (the tool) does not catch `NotFound`
itself, so the exception propagates to `@upstream_guard`, which is the only path that turns it into
a `NOT_FOUND` envelope.

New tests (`test_client.py`, `TestFetchDatasetDetails`): `test_non_nb_organization_raises_not_found`
(the exact live-reproduced EC case), `test_missing_organization_key_fails_closed_as_not_found`,
`test_none_organization_fails_closed_as_not_found`, and a positive control
`test_nb_organization_still_resolves_successfully` proving the fix does not reject every id.
(`TestFetchQueryDataset`): `test_non_nb_organization_propagates_not_found`, proving the guard covers
`nb_query_dataset` too. (`test_tools.py`, `TestNbQueryDataset`):
`test_non_nb_organization_returns_not_found_envelope`, proving the tool-layer `@upstream_guard`
mapping. Docstrings on `fetch_dataset_details`, `nb_get_dataset_details` and `nb_query_dataset` were
updated to describe the new boundary.

**Live verification (both directions, per the finding's explicit requirement):**
```
Before fix — EC dataset returned in full:
  nb_get_dataset_details(dataset_id="6059da1d-e1da-4f2b-a420-b5c2a130eeaa")
    -> SUCCESS, organization = "ec", title = "Weather Radar - DPQPE"

After fix — same id:
  nb_get_dataset_details(dataset_id="6059da1d-e1da-4f2b-a420-b5c2a130eeaa")
    -> error.code == "NOT_FOUND"

After fix — a real NB dataset id (from a live nb_search_datasets call):
  nb_get_dataset_details(dataset_id="af456a56-b162-032d-69ee-719d3aac9ac7")
    -> SUCCESS, organization.name == "nb"
```

### G2: `fetch_query_dataset` has no upper bound on `limit`

**Files modified:** `src/mcp_canada/modules/new_brunswick/client.py`, `src/mcp_canada/modules/new_brunswick/tools.py`, `src/mcp_canada/modules/new_brunswick/__tests__/test_client.py`
**Commit:** `820855a`
**Applied fix:** `fetch_query_dataset` checked only `limit <= 0` (added in round 1, WR-03) — nothing
capped the upper bound before `rows[:limit]` sliced a parsed CSV/XLSX/JSON resource. Orchestrator
live-verified before the fix that `limit=10_000_000` and `limit=5001` were both accepted. Added
`if limit > MAX_RECORDS: raise InvalidInput(...)` immediately after the existing lower-bound check,
before any network call — mirroring the identical pattern already enforced by
`fetch_gnb_socrata_query` (round 1, F3) and `_geonb_query` (round 1, F2). `MAX_RECORDS` was already
imported in `client.py`, so no new import was needed.

New tests: `test_limit_above_max_records_raises_invalid_input_before_any_parsing` (asserts neither
`api_get` nor `fetch_and_parse` is awaited when the cap is exceeded — the check must short-circuit
before `fetch_dataset_details` runs) and `test_limit_at_max_records_is_accepted` (the boundary value
itself, `MAX_RECORDS`, must not be rejected). Docstrings on `fetch_query_dataset` and
`nb_query_dataset` were updated to name the cap.

**Live verification:**
```
nb_query_dataset(dataset_id="af456a56-b162-032d-69ee-719d3aac9ac7", resource_index=0, limit=10_000_000)
  -> error.code == "INVALID_INPUT"
  -> error.message == "Invalid input: nb_query_dataset limit must be at most 5000, got 10000000"
```

### G3: `MODULE_DESCRIPTION` is stale in two separate ways

**Files modified:** `src/mcp_canada/modules/new_brunswick/__init__.py`, `src/mcp_canada/modules/new_brunswick/__tests__/test_prompts_resources.py`, `TOOLS.md`
**Commit:** `af307ec`
**Applied fix:** `MODULE_DESCRIPTION`/`MODULE_DESCRIPTION_FR` still said "three upstream surfaces"
and never mentioned `gnb.socrata.com`, even though the Wave 0 checkpoint (option-a) added
`nb_search_gnb_socrata_datasets`/`nb_query_gnb_socrata_dataset` as a fourth discovery surface (the
finding Codex flagged). Separately — not flagged by Codex, caught during the fix — the same text
still advertised "minerals, parks" as curated GeoNB coverage, even though that same checkpoint
dropped `nb_get_mineral_occurrences`/`nb_get_provincial_parks` to the long tail (reachable only via
`nb_query_geonb_layer`, no dedicated tool). Since `meta/list_modules.py` returns
`MODULE_DESCRIPTION` verbatim and the generated `TOOLS.md` catalogue repeats it, both errors were
agent-visible.

Rewrote `MODULE_DESCRIPTION` and `MODULE_DESCRIPTION_FR` (kept semantically equivalent across
languages) to name all four surfaces — federal CKAN, `gnb.socrata.com`, GeoNB, NB 511 — and to
describe minerals/provincial parks as reachable only through the long-tail `nb_query_geonb_layer`
tool rather than listing them as curated coverage. Also updated the module-level docstring at the
top of `__init__.py` (the "Three upstream surfaces" header comment) for consistency, since it had
the identical staleness. Ran `python scripts/generate_catalog.py` to regenerate `TOOLS.md`;
`README.md` needed no change — its NB row already said "GeoNB bare ArcGIS Server +
gnb.socrata.com Socrata", i.e. it already reflected four surfaces.

New tests (`test_prompts_resources.py`, `TestModuleDescription`):
`test_describes_four_upstream_surfaces_including_gnb_socrata`,
`test_fr_description_also_names_gnb_socrata`, and
`test_minerals_and_parks_not_advertised_as_curated_coverage`.

### G4: the flood-risk prompt instructs an unexecutable workflow

**Files modified:** `src/mcp_canada/modules/new_brunswick/prompts.py`, `src/mcp_canada/modules/new_brunswick/__tests__/test_prompts_resources.py`
**Commit:** `9c24fae`
**Applied fix:** `nb_flood_risk_assessment` told the agent to pass a location such as
"Fredericton" through a four-step workflow, but no flood tool accepts a place name —
`nb_get_flood_hazard_areas` is filtered by `sheet=`, `nb_get_historical_floods` by `event=`,
`nb_get_wetlands` by `wetland_class=`/`status=`, and none of the three carries geometry, so there
was no spatial path either. Civic-address resolution (the only tool in this module that actually
returns `LATITUDE`/`LONGITUDE`, per commit `4964e77`) was listed last, as Step 4 — after the three
flood-layer calls the location was supposedly needed for.

Reordered both language variants so `nb_get_civic_addresses` (with `community=`/`street=` derived
from the caller's location) is now Step 1, explicitly resolving to a point (`LATITUDE`/`LONGITUDE`)
plus `COUNTY`/`PID` before any flood-layer call. Added an explicit statement — "No flood-layer tool
accepts a place name as an argument" (EN) / "Aucun outil de couche d'inondation n'accepte un nom de
lieu comme argument" (FR) — describing the three flood tools' real filters (sheet/event/class)
generically in that sentence (not by literal tool name) so the location-resolution tool name still
appears textually before the flood-tool names later in the message. Flood hazard index, historical
floods and wetlands became Steps 2–4, unchanged in content and required-filter behaviour. Did not
invent a location parameter on any flood tool — the fix is entirely narrative, no client/tool
signature changed. Updated the module-level docstring and `nb_flood_risk_assessment`'s own
docstring to describe the new chain order.

New tests: `test_flood_risk_assessment_does_not_invent_a_location_parameter` (EN — asserts "accepts
a place name" appears and that `nb_get_civic_addresses` is named before `nb_get_flood_hazard_areas`
in the assistant message) and `test_flood_risk_assessment_fr_does_not_invent_a_location_parameter`
(same ordering assertion, FR). All five pre-existing `TestNbPrompts` assertions for this prompt
(message count, roles, the four tool names, `Technical_`/`Sheet_Numb` citation, EN≠FR) still pass
unmodified.

## Skipped Issues

None — all four findings were fixed.

## Verification

```
uv run pytest                                          # 3577 passed, 2 skipped, 369 deselected
uv run pytest --cov=src/mcp_canada --cov-fail-under=95  # 97.40% total coverage
uv run ruff check src/ tests/                           # All checks passed!
uv run pyright                                          # 0 errors, 2 pre-existing warnings
                                                          #   (weather/climate, untouched by this fix)
python scripts/generate_catalog.py --check              # Catalog is up to date.
```

NB-module-only subset: `uv run pytest src/mcp_canada/modules/new_brunswick/__tests__/ -q` — 393
passed (up from 380 before this round: +13 new tests across the four fixes, plus the pre-existing
suite untouched).

Each of the four commits above was verified independently before the next was started — the full
NB suite, ruff and pyright were re-run after every single fix, not just at the end.

---

_Fixed: 2026-07-31T02:39:12Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 2_
