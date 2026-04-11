---
status: resolved
trigger: "Gap 4 (Test 13): bc_get_water_wells(lang='fr') with no filter returns an error envelope whose lang field is 'fr' but whose message text is still English"
created: 2026-04-11T00:00:00Z
updated: 2026-04-11T05:00:00Z
resolved: 2026-04-11T05:00:00Z
resolved_by: "15-05 plan execution — inline lang == 'en' ternary added to tools.py:700-708"
---

## Current Focus

hypothesis: The guard message in `bc_get_water_wells` is a hardcoded English string literal passed directly to `make_error`, with no lang-conditional branch or `i18n.t()` lookup. `make_error` only stamps `lang` into the envelope — it does not translate the message.
test: Read tools.py:700-706 to confirm the literal; read shared/envelope.py:make_error to confirm it is a pure pass-through; grep the codebase for any prior use of `t(` or `lang == "fr"` in tool error paths.
expecting: confirmation that (a) the message is hardcoded, (b) make_error cannot translate, (c) no module currently uses i18n.t() in production tool code.
next_action: write minimum-diff fix recommendation.

## Symptoms

expected: `bc_get_water_wells(lang="fr")` called with no filter returns an error envelope with the guard message in French. Envelope already has `_meta.lang: "fr"` (actually `error.lang: "fr"` — envelope is an `error` dict, not wrapped in `_meta`).
actual: `error.lang == "fr"` but `error.message` is the English literal `"bc_get_water_wells requires at least one of city, well_class, or aquifer_id (dataset has 130K+ records — Pitfall 5)."`
errors: none — no exception; this is a silent content bug.
reproduction: `await bc_get_water_wells(lang="fr")` with no `city`/`well_class`/`aquifer_id`.
started: always broken — the guard was introduced this way in phase 15 (Pitfall 5 mitigation).

## Eliminated

- hypothesis: `make_error` is supposed to translate the message when `lang="fr"` and the caller forgot to wire something up.
  evidence: `src/mcp_canada/shared/envelope.py:48-67` — `make_error` is a dumb builder. It writes `message` straight through into `error.message` and stamps `lang` into `error.lang`. No translation layer, no hook, no catalog lookup. This is by design — the contract is "caller passes the already-translated message".
  timestamp: 2026-04-11T00:00:00Z

- hypothesis: Other BC tools do this correctly, so the water wells guard is a one-off oversight.
  evidence: Every `make_error` call in `src/mcp_canada/modules/british_columbia/tools.py` (lines 143, 165, 198, 213, 248, 264, 270, 283, 307, 317, 351, 387, 455, 491, 510, 563, 613, 663, 725, 771, 821, 859, 880, 924, 971, 1015, 1065, 1111, 1161) uses a hardcoded English string. None branches on `lang`. None calls `t()`. The water wells guard is representative, not exceptional.
  timestamp: 2026-04-11T00:00:00Z

- hypothesis: This is a British Columbia-specific defect — other modules honour `lang`.
  evidence: `bank_of_canada/tools.py` make_error calls (lines 95, 133, 182, 233, 279, 318, 367) all use hardcoded English f-strings. `ontario/tools.py` (lines 65, 98, 132, 166, 198, 317) — same pattern. Grep for `lang == "fr"` across `src/mcp_canada/modules/**/tools.py` returns **zero matches**. Grep for `from mcp_canada.shared.i18n import` across all `src/` modules returns **zero matches**. The `t()` helper in `shared/i18n.py` exists but is never imported by any production tool — only by `tests/test_i18n.py`. This is a project-wide latent bug: every tool ignores `lang` for error text while dutifully passing it into `make_error`.
  timestamp: 2026-04-11T00:00:00Z

## Evidence

- timestamp: 2026-04-11T00:00:00Z
  checked: `src/mcp_canada/modules/british_columbia/tools.py:700-706`
  found: |
    if city is None and well_class is None and aquifer_id is None:
        return make_error(
            "INVALID_INPUT",
            "bc_get_water_wells requires at least one of city, well_class, or aquifer_id "
            "(dataset has 130K+ records — Pitfall 5).",
            lang=lang,
        )
  implication: Exact location of the offending literal. `lang` is passed to `make_error` but the message itself is a fixed English string with zero lang awareness.

- timestamp: 2026-04-11T00:00:00Z
  checked: `src/mcp_canada/shared/envelope.py:48-67` (make_error signature and body)
  found: |
    def make_error(code: str, message: str, lang: str = "en", **extra: Any) -> dict[str, Any]:
        return {
            "error": {
                "code": code,
                "message": message,
                "lang": lang,
                **extra,
            }
        }
  implication: `make_error` is a pure builder. It does NOT translate. The caller is responsible for producing the localised `message`. This is the documented contract. No change needed here.

- timestamp: 2026-04-11T00:00:00Z
  checked: `src/mcp_canada/shared/i18n.py` (full file)
  found: |
    - LABELS catalog with 5 keys: error.rate_limited, error.api_unavailable,
      error.invalid_input, error.upstream_error, error.not_found
    - t(key, lang, **kwargs) helper that looks up a template and format()s it
    - Fallback chain: requested lang -> en -> key name
  implication: Infrastructure for bilingual error messages exists but is completely unused by production code. `error.invalid_input` already has a French template: `"Entrée invalide : {detail}"`. This is the idiomatic target for the fix.

- timestamp: 2026-04-11T00:00:00Z
  checked: `grep "from mcp_canada.shared.i18n import" src/`
  found: Zero matches inside `src/`. Only `tests/test_i18n.py` imports it.
  implication: `t()` has never been used in a production tool. Using it in `bc_get_water_wells` establishes a new precedent for the project — but it is the precedent the phase 02 RESEARCH doc and `.claude/rules` imply was always intended.

- timestamp: 2026-04-11T00:00:00Z
  checked: `grep 'lang == "fr"' src/mcp_canada/modules/**/tools.py`
  found: Zero matches.
  implication: No module currently uses a `lang == "fr"` ternary in `tools.py`. The only `lang == "fr"` branches are in `prompts.py` files (statcan, weather, bank_of_canada, drug_database, york_region, ircc, …) — that is a separate, established pattern for prompt content.

- timestamp: 2026-04-11T00:00:00Z
  checked: `src/mcp_canada/modules/bank_of_canada/tools.py:95-372` and `src/mcp_canada/modules/ontario/tools.py:65-321`
  found: Every `make_error` call uses hardcoded English. None branches on `lang`. None calls `t()`.
  implication: The BC water wells guard is not an outlier — it is representative of the project-wide convention. Fixing it in isolation diverges from convention by being more correct. Not fixing it leaves Test 13 failing. The minimum-diff fix is to localise JUST the water wells guard because that is the only message the UAT asserts on.

## Resolution

root_cause: |
  `bc_get_water_wells` at `src/mcp_canada/modules/british_columbia/tools.py:700-706` passes a hardcoded English literal to `make_error`. `make_error` does not translate — it only stamps `lang` into the envelope. So `error.lang == "fr"` while `error.message` stays English. This is actually the project-wide convention: **no production tool** (bank_of_canada, ontario, BC, or any other module) ever branches error text on `lang` or uses `shared/i18n.py:t()`. The bilingual-error infrastructure in `shared/i18n.py` exists but has zero production imports. Test 13 is the first UAT that actually asserts on localised error text, so it exposes a latent systemic gap by hitting the most visible (and most docstring-documented) guard.

fix: |
  Applied in plan 15-05 (commit 1f42468). Replaced tools.py:700-706 with:

  ```python
  if city is None and well_class is None and aquifer_id is None:
      message = (
          "bc_get_water_wells requires at least one of city, well_class, or aquifer_id "
          "(dataset has 130K+ records — Pitfall 5)."
          if lang == "en"
          else "bc_get_water_wells exige au moins un des paramètres city, well_class ou "
               "aquifer_id (l'ensemble de données contient plus de 130 000 enregistrements — Pitfall 5)."
      )
      return make_error("INVALID_INPUT", message, lang=lang)
  ```

  Rationale for the inline ternary over `t()`:
  1. Zero production code currently imports `shared/i18n.py:t()`. Introducing the first
     import for one guard message would be scope-creep.
  2. The inline `lang == "fr"` branch mirrors the established pattern in prompts.py files
     across 7 modules.
  3. Minimum diff: 6 lines changed in one function. No new imports.

  Two regression tests added to test_tools.py:
  - test_guard_returns_french_message_when_lang_fr
  - test_guard_returns_english_message_when_lang_en

verification: |
  Confirmed:
  - `uv run pytest src/mcp_canada/modules/british_columbia/__tests__/test_tools.py -k water_wells -x -v`
    → Both new tests pass, all existing water wells tests green.
  - `uv run pytest src/mcp_canada/modules/british_columbia/ -x -q`
    → 148 passed.

files_changed:
  - src/mcp_canada/modules/british_columbia/tools.py
  - src/mcp_canada/modules/british_columbia/__tests__/test_tools.py

## Scope Assessment

**Isolated to one message in one tool**, in the sense that only `bc_get_water_wells` is asserted on by Test 13 and only its guard message needs a French variant for Gap 4 to close.

**Systemic across the whole project**, in the sense that every `@tool` in every module hardcodes English error text while passing `lang` through to `make_error`. The project has a bilingual error message *contract* (`make_error` accepts `lang`, `shared/i18n.py` has a `t()` helper and a labels catalog) but no production code honours it. Any future UAT that asserts on French error text will fail the same way.

**Recommended treatment for future work:** audit all tool error paths for bilingual coverage — the hardcoded-English pattern is systemic across all modules. This belongs in a dedicated bilingual-errors phase, not in individual gap fixes.
