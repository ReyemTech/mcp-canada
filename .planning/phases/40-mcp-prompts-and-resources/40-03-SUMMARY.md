---
phase: 40-mcp-prompts-and-resources
plan: "03"
subsystem: mcp-prompts-resources
tags: [prompts, resources, open-parliament, recalls, drug-database, nutrient-file, fastmcp, bilingual]
dependency_graph:
  requires:
    - boc-prompts-reference-implementation (40-01)
  provides:
    - parl-prompts-resources
    - recalls-prompts-resources
    - drug-prompts-resources
    - nutrient-prompts-resources
  affects:
    - src/mcp_canada/modules/open_parliament/prompts.py
    - src/mcp_canada/modules/open_parliament/resources.py
    - src/mcp_canada/modules/recalls/prompts.py
    - src/mcp_canada/modules/recalls/resources.py
    - src/mcp_canada/modules/drug_database/prompts.py
    - src/mcp_canada/modules/drug_database/resources.py
    - src/mcp_canada/modules/nutrient_file/prompts.py
    - src/mcp_canada/modules/nutrient_file/resources.py
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
    - src/mcp_canada/modules/open_parliament/prompts.py
    - src/mcp_canada/modules/open_parliament/resources.py
    - src/mcp_canada/modules/open_parliament/__tests__/test_prompts_resources.py
    - src/mcp_canada/modules/recalls/prompts.py
    - src/mcp_canada/modules/recalls/resources.py
    - src/mcp_canada/modules/recalls/__tests__/test_prompts_resources.py
    - src/mcp_canada/modules/drug_database/prompts.py
    - src/mcp_canada/modules/drug_database/resources.py
    - src/mcp_canada/modules/drug_database/__tests__/test_prompts_resources.py
    - src/mcp_canada/modules/nutrient_file/prompts.py
    - src/mcp_canada/modules/nutrient_file/resources.py
    - src/mcp_canada/modules/nutrient_file/__tests__/test_prompts_resources.py
  modified: []
decisions:
  - "Guided workflow prompts (list[Message]) for multi-step tool chaining; quick lookups (str) for single-tool instructions (same pattern as BoC reference)"
  - "Resources are zero-parameter functions — lang param would promote to ResourceTemplate and remove from resources/list"
  - "Bilingual content embedded inline in resources (both languages in one JSON/Markdown)"
  - "Parliament session format as JSON with current + historical sessions for agent reference"
  - "Drug schedule codes follow Health Canada classification (Prescription/OTC/Schedule I-III/Unscheduled)"
  - "Nutrient food groups use canonical CNF group IDs (1-25) matching the API's actual group_id values"
  - "Common nutrients indexed by CNF nutrient_id (e.g., 208=Energy, 203=Protein) for direct API cross-reference"
metrics:
  duration: "12min"
  completed_date: "2026-04-09"
  tasks_completed: 2
  files_created: 12
  tests_added: 131
  coverage: "96.41%"
---

# Phase 40 Plan 03: Federal API Modules Prompts and Resources Summary

**One-liner:** 19 bilingual @prompt functions and 27 zero-parameter @resource functions across Open Parliament, Recalls, Drug Database, and Nutrient File modules, enabling guided multi-tool workflows and instant reference data access.

## What Was Built

### Open Parliament — 5 prompts + 7 resources

| Name | Type | Returns | Purpose |
|------|------|---------|---------|
| `parl_research_bill` | guided workflow | `list[Message]` | Chains parl_search_bills → parl_get_bill_details → parl_get_votes |
| `parl_find_mp` | quick lookup | `str` | Single instruction for parl_get_politicians or parl_search_by_riding |
| `parl_track_voting` | guided workflow | `list[Message]` | Chains parl_get_votes → parl_get_voting_record → parl_get_ballots |
| `parl_search_debates` | quick lookup | `str` | Single instruction for parl_search_hansard |
| `parl_party_breakdown` | guided workflow | `list[Message]` | parl_get_party_members for party comparison |

| URI | Type | Content |
|-----|------|---------|
| `data://parliament/party-codes` | JSON catalog | 6 party codes (CPC, LPC, NDP, BQ, GPC, IND) with bilingual names |
| `data://parliament/session-format` | JSON catalog | "44-1" format explained, current + 3 recent sessions |
| `data://parliament/bill-types` | JSON catalog | C-/S-/C-2xx/S-2xx prefixes with origin and examples |
| `docs://parliament/voting-guide` | Markdown guide | Divisions, ballot types, interpreting results |
| `docs://parliament/hansard-guide` | Markdown guide | What Hansard is, search strategies, debate structure |
| `docs://parliament/api-quirks` | Markdown guide | Rate limits, pagination, politician slugs, bill numbers |
| `template://parliament/mp-profile` | Markdown template | MP profile with voting record, debate contributions |

### Recalls — 4 prompts + 6 resources

| Name | Type | Returns | Purpose |
|------|------|---------|---------|
| `recalls_investigate_alert` | guided workflow | `list[Message]` | Chains recalls_search → recalls_get_details |
| `recalls_quick_search` | quick lookup | `str` | Single instruction for recalls_search |
| `recalls_check_food_safety` | quick lookup | `str` | Single instruction for recalls_get_food |
| `recalls_vehicle_safety` | guided workflow | `list[Message]` | Chains recalls_get_vehicles → recalls_get_details |

| URI | Type | Content |
|-----|------|---------|
| `data://recalls/categories` | JSON catalog | FOOD/VEHICLE/HEALTH/CPS with bilingual labels and tool names |
| `data://recalls/severity-levels` | JSON catalog | Class I/II/III/Warning with urgency levels |
| `docs://recalls/search-tips` | Markdown guide | Category filtering, date filtering, getting full details |
| `docs://recalls/food-safety-guide` | Markdown guide | Nine priority allergens, reading recall notices, consumer advice |
| `template://recalls/safety-alert` | Markdown template | Safety alert summary with recall_id, date, risk_level |
| `template://recalls/recall-report` | Markdown template | Multi-recall investigation report with findings table |

### Drug Database — 5 prompts + 7 resources

| Name | Type | Returns | Purpose |
|------|------|---------|---------|
| `drug_research_medication` | guided workflow | `list[Message]` | Chains drug_search → drug_get_details → drug_get_ingredients → drug_get_routes |
| `drug_quick_search` | quick lookup | `str` | Single instruction for drug_search |
| `drug_check_company` | quick lookup | `str` | Single instruction for drug_search_companies |
| `drug_compare_generics` | guided workflow | `list[Message]` | drug_search + drug_get_details + drug_get_therapeutic_class |
| `drug_check_status` | quick lookup | `str` | Single instruction for drug_get_status with DIN |

| URI | Type | Content |
|-----|------|---------|
| `data://drug/schedule-codes` | JSON catalog | Prescription/OTC/Schedule I-III/Unscheduled with bilingual descriptions |
| `data://drug/route-codes` | JSON catalog | 10 administration routes (oral, topical, IV, IM, etc.) with bilingual labels |
| `data://drug/status-codes` | JSON catalog | APPROVED/MARKETED/CANCELLED/DORMANT/UNDER REVIEW with active flag |
| `data://drug/therapeutic-classes` | JSON catalog | 14 ATC level-1 codes (A-V) with bilingual class descriptions |
| `docs://drug/din-guide` | Markdown guide | What DINs are, format, finding them, DIN vs NPN vs DIN-HM |
| `docs://drug/search-tips` | Markdown guide | Brand vs generic, company search, exact DIN lookup, status interpretation |
| `template://drug/medication-report` | Markdown template | Full drug profile with DIN, ingredients, routes, ATC class |

### Nutrient File — 5 prompts + 7 resources

| Name | Type | Returns | Purpose |
|------|------|---------|---------|
| `nutrient_analyze_food` | guided workflow | `list[Message]` | Chains nutrient_search_foods → nutrient_get_food_details → nutrient_get_nutrient_amounts → nutrient_get_serving_sizes |
| `nutrient_quick_search` | quick lookup | `str` | Single instruction for nutrient_search_foods |
| `nutrient_compare_foods` | guided workflow | `list[Message]` | nutrient_search_foods (x2) → nutrient_compare_foods |
| `nutrient_browse_food_groups` | quick lookup | `str` | nutrient_list_food_groups → nutrient_search_by_food_group |
| `nutrient_check_daily_values` | guided workflow | `list[Message]` | nutrient_get_nutrient_amounts → interpret vs Canadian DV |

| URI | Type | Content |
|-----|------|---------|
| `data://nutrient/food-groups` | JSON catalog | All 24 CNF food group IDs with bilingual names (Dairy, Meat, Produce, etc.) |
| `data://nutrient/common-nutrients` | JSON catalog | 15 key nutrient IDs (208=Energy, 203=Protein, etc.) with units and category |
| `data://nutrient/serving-size-measures` | JSON catalog | 10 common measures (100g, cup, tbsp, slice, etc.) with gram equivalents |
| `docs://nutrient/cnf-guide` | Markdown guide | CNF scope, 5800+ foods, data sources, update frequency, limitations |
| `docs://nutrient/interpretation-guide` | Markdown guide | Per-100g conversion, Canadian Daily Values table, %DV calculation, cooking adjustment |
| `template://nutrient/food-profile` | Markdown template | Single food profile with macro/micro table and serving sizes |
| `template://nutrient/comparison-report` | Markdown template | Side-by-side food comparison with difference column and winner flags |

## Tests

131 unit tests total across 4 new test files:
- TestParlPrompts: 20 tests / TestParlResources: 17 tests
- TestRecallsPrompts: 17 tests / TestRecallsResources: 15 tests
- TestDrugPrompts: 19 tests / TestDrugResources: 15 tests
- TestNutrientPrompts: 20 tests / TestNutrientResources: 18 tests

All 1599 tests passing at 96.41% coverage (above 95% threshold).

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check

### Files Exist

- src/mcp_canada/modules/open_parliament/prompts.py: FOUND
- src/mcp_canada/modules/open_parliament/resources.py: FOUND
- src/mcp_canada/modules/open_parliament/__tests__/test_prompts_resources.py: FOUND
- src/mcp_canada/modules/recalls/prompts.py: FOUND
- src/mcp_canada/modules/recalls/resources.py: FOUND
- src/mcp_canada/modules/recalls/__tests__/test_prompts_resources.py: FOUND
- src/mcp_canada/modules/drug_database/prompts.py: FOUND
- src/mcp_canada/modules/drug_database/resources.py: FOUND
- src/mcp_canada/modules/drug_database/__tests__/test_prompts_resources.py: FOUND
- src/mcp_canada/modules/nutrient_file/prompts.py: FOUND
- src/mcp_canada/modules/nutrient_file/resources.py: FOUND
- src/mcp_canada/modules/nutrient_file/__tests__/test_prompts_resources.py: FOUND

### Commits

- 99a3fe8: feat(40-03): add Open Parliament + Recalls prompts/resources + tests
- 7dc2991: feat(40-03): add Drug Database + Nutrient File prompts/resources + tests

### Verification Results

- All 131 prompt/resource unit tests: PASSED
- Full suite 1599 tests: PASSED
- Coverage: 96.41% (above 95% threshold)

## Self-Check: PASSED
