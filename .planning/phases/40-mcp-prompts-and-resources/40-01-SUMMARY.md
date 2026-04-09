---
phase: 40-mcp-prompts-and-resources
plan: "01"
subsystem: mcp-prompts-resources
tags: [prompts, resources, bank-of-canada, fastmcp, bilingual, example-module]
dependency_graph:
  requires: []
  provides:
    - boc-prompts-reference-implementation
    - boc-resources-reference-implementation
    - example-module-prompt-resource-templates
  affects:
    - src/mcp_canada/modules/bank_of_canada/prompts.py
    - src/mcp_canada/modules/bank_of_canada/resources.py
    - src/mcp_canada/modules/bank_of_canada/__tests__/test_prompts_resources.py
    - src/mcp_canada/modules/_example/prompts.py
    - src/mcp_canada/modules/_example/resources.py
tech_stack:
  added: []
  patterns:
    - "@prompt standalone decorator (fastmcp.prompts) for guided workflows and quick lookups"
    - "@resource standalone decorator (fastmcp.resources) with data://, docs://, template:// URI schemes"
    - "Annotated[Literal['en','fr'], 'Language: ...'] pattern for prompt lang params"
    - "Zero-parameter resource functions (no lang) to stay FunctionResource not ResourceTemplate"
    - "Bilingual content embedded inline in JSON catalogs and markdown guides"
    - "FunctionPrompt.from_function() + FunctionResource.from_function() for unit testing"
key_files:
  created:
    - src/mcp_canada/modules/bank_of_canada/prompts.py
    - src/mcp_canada/modules/bank_of_canada/resources.py
    - src/mcp_canada/modules/bank_of_canada/__tests__/test_prompts_resources.py
    - src/mcp_canada/modules/_example/prompts.py
    - src/mcp_canada/modules/_example/resources.py
  modified: []
decisions:
  - "Guided workflow prompts (list[Message]) for multi-step tool chaining; quick lookups (str) for single-tool instructions"
  - "Resources are zero-parameter functions — lang param would promote to ResourceTemplate and remove from resources/list"
  - "Bilingual content embedded inline in resources (both languages in one JSON/Markdown)"
  - "test using FunctionPrompt.from_function() + FunctionResource.from_function() avoids needing a live MCP server"
metrics:
  duration: "10min 42s"
  completed_date: "2026-04-09"
  tasks_completed: 2
  files_created: 5
  tests_added: 36
  coverage: "95.74%"
---

# Phase 40 Plan 01: BoC Prompts and Resources Reference Implementation Summary

**One-liner:** 5 bilingual @prompt functions and 7 zero-parameter @resource functions for the Bank of Canada module, establishing the 7-file pattern all subsequent modules will follow.

## What Was Built

### Bank of Canada prompts.py — 5 prompts

| Name | Type | Returns | Purpose |
|------|------|---------|---------|
| `boc_analyze_rates` | guided workflow | `list[Message]` | Chains boc_search_series → boc_get_exchange_rates for rate analysis |
| `boc_get_policy_rate` | quick lookup | `str` | Single instruction: boc_get_interest_rates with rate_type='policy' |
| `boc_compare_currencies` | guided workflow | `list[Message]` | Compares two currencies over a date range |
| `boc_explore_commodities` | guided workflow | `list[Message]` | Chains boc_list_groups → boc_get_commodity_prices for BCPI exploration |
| `boc_check_inflation` | quick lookup | `str` | Single instruction: boc_get_inflation_data for CPI data |

### Bank of Canada resources.py — 7 resources

| URI | Type | Content |
|-----|------|---------|
| `data://boc/currency-codes` | JSON catalog | 17 FX currencies with en/fr bilingual labels |
| `data://boc/interest-rate-types` | JSON catalog | 5 rate types mapped to series codes + bilingual descriptions |
| `data://boc/commodity-types` | JSON catalog | 6 BCPI commodity categories with bilingual descriptions |
| `data://boc/inflation-indicators` | JSON catalog | 4 CPI measures with bilingual descriptions and series codes |
| `docs://boc/series-naming` | Markdown guide | FX/rate/CPI/BCPI naming conventions + discovery tools |
| `docs://boc/api-quirks` | Markdown guide | Date formats, null values, cache TTLs, common 404 causes |
| `template://boc/rate-report` | Markdown template | Exchange rate report with {currency}, {start_date}, {latest_value} placeholders |

### _example module — 2 annotated template files

- `prompts.py`: 2 examples (guided workflow + quick lookup) with extensive inline comments
- `resources.py`: 3 examples (data:// catalog + docs:// guide + template://) with zero-param rule explanation

## Tests

36 unit tests in `test_prompts_resources.py`:
- TestBocPrompts: 19 tests covering en/fr for all 5 prompts, role correctness, tool name presence
- TestBocResources: 17 tests covering JSON validity, bilingual keys, markdown format, placeholder syntax, zero-param enforcement

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check

### Files Exist

- src/mcp_canada/modules/bank_of_canada/prompts.py: FOUND
- src/mcp_canada/modules/bank_of_canada/resources.py: FOUND
- src/mcp_canada/modules/bank_of_canada/__tests__/test_prompts_resources.py: FOUND
- src/mcp_canada/modules/_example/prompts.py: FOUND
- src/mcp_canada/modules/_example/resources.py: FOUND

### Commits

- 928d3be: test(40-01): add failing tests for BoC prompts and resources
- 1c0e1e7: feat(40-01): add BoC prompts.py and resources.py reference implementation
- e27fb31: feat(40-01): add annotated prompt/resource templates to _example module

### Verification Results

- All 36 prompt/resource unit tests: PASSED
- Full suite 1216 tests: PASSED
- Coverage: 95.74% (above 95% threshold)

## Self-Check: PASSED
