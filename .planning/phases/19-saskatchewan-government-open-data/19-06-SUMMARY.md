---
phase: 19-saskatchewan-government-open-data
plan: "06"
subsystem: prompts-resources
tags: [prompts, resources, bilingual, arcgis-hub, multi-org, deferred-domains]
dependency_graph:
  requires: [19-05]
  provides: [SK-15]
  affects: []
tech_stack:
  added: []
  patterns:
    - standalone @prompt from fastmcp.prompts with lang Annotated[Literal["en","fr"]]
    - standalone @resource from fastmcp.resources with ZERO parameters (bilingual inline)
    - guided list[Message] prompts (user + assistant roles) for multi-step tool chains
    - quick lookup str prompts for single-tool instructions
    - data:// returns json.dumps (bilingual content inline, no lang param)
    - docs:// returns raw markdown (both EN+FR in same document)
    - template:// returns markdown with {placeholder} syntax
key_files:
  created:
    - src/mcp_canada/modules/saskatchewan/prompts.py
    - src/mcp_canada/modules/saskatchewan/resources.py
  modified:
    - src/mcp_canada/modules/saskatchewan/__tests__/test_prompts_resources.py
decisions:
  - "Message.content is TextContent (not str) — access via m.content.text in tests (matches Manitoba pattern)"
  - "Resources are ZERO-parameter — lang param would promote to ResourceTemplate and drop from resources/list"
  - "WSA_Reservoirs layer-26 documented in portal-guide and agriculture-data-guide for agent awareness"
  - "Deferred domains (transport key-gated, health no public FeatureServer) surfaced in portal-guide and health-regions data resource"
metrics:
  duration: "8min"
  completed_date: "2026-06-15"
  tasks_completed: 2
  files_created: 2
  files_modified: 1
  test_cases: 28
  coverage: "97.27%"
---

# Phase 19 Plan 06: Saskatchewan Prompts and Resources Summary

Saskatchewan prompts and resources (Phase 40 pattern) — 6 bilingual @prompt functions (3 guided list[Message] + 3 quick lookup str) and 7 zero-parameter @resource functions covering crop regions, river basins, SHA health authority, multi-org portal architecture, agriculture data guide, and report templates.

## What Was Built

### 6 Bilingual Prompts (`src/mcp_canada/modules/saskatchewan/prompts.py`)

#### Guided Workflow Prompts (list[Message], user + assistant roles)

| Prompt | Tools Chained | Description |
|--------|---------------|-------------|
| `saskatchewan_explore_agriculture` | `_get_crop_yields` → `_get_grain_elevators` → `_get_mineral_mines` | Agriculture + mining economy; crop region dispatch; potash/uranium context |
| `saskatchewan_explore_environment` | `_get_fire_bans` → `_get_historic_wildfires` → `_get_air_quality` | Fire ban dispatch (SPSA layer routing); historic wildfires; live air quality |
| `saskatchewan_explore_water` | `_get_wsa_stations` → `_get_wsa_reservoirs` | WSA org architecture; HyperLink_Graph for live hydrographs; layer-26 quirk |

#### Quick Lookup Prompts (str)

| Prompt | Tool Guided | Key Notes |
|--------|-------------|-----------|
| `saskatchewan_quick_dataset_search` | `_search_datasets` | No CKAN; data.sk.ca doesn't exist; WSA+SPSA not Hub-discoverable |
| `saskatchewan_fire_ban_status_now` | `_get_fire_bans` | ban_scope dispatch (urban/rural/provincial/parks); empty=no-bans note |
| `saskatchewan_crop_yield_lookup` | `_get_crop_yields` | provincial vs 5 regions; PDF reports not machine-readable |

### 7 Zero-Parameter Resources (`src/mcp_canada/modules/saskatchewan/resources.py`)

#### data:// Resources (JSON, bilingual inline)

| URI | Content | Key Data |
|-----|---------|----------|
| `data://saskatchewan/crop-regions` | 5 crop reporting regions | SE/SW/Central/NE/NW with location, signature crops, en/fr labels |
| `data://saskatchewan/major-basins` | 6 major river basins | Qu'Appelle, North/South Sask, Assiniboine, Churchill, Athabasca + WSA monitoring flags |
| `data://saskatchewan/health-regions` | Single SHA (2017 merger) | Province-wide authority; health domain deferred (no public FeatureServer); major facilities |

#### docs:// Resources (Markdown, both languages inline)

| URI | Content |
|-----|---------|
| `docs://saskatchewan/portal-guide` | 3-server architecture (GeoHub zcv98lgAl8xQ04cW + WSA 7MBdlVpjqbfBhQer + SPSA egis); data.sk.ca doesn't exist; deferred transport (511 key-gated) + health; Petroleum HTTP 400 routing; WSA layer-26 quirk; GOS Standard Unrestricted Use Data Licence v2.0 |
| `docs://saskatchewan/agriculture-data-guide` | Crop yields (bu/acre) vs PDF weekly reports; Crop_Production_2025 boundary-only caveat; grain elevator PR='SK' filter; mineral mines dispatch table |

#### template:// Resources (Markdown with {placeholder})

| URI | Content |
|-----|---------|
| `template://saskatchewan/dataset-report` | Dataset exploration report with search, dataset spotlight, sample data, notes, next steps |
| `template://saskatchewan/wildfire-report` | Fire ban status by scope, historic wildfire summary, air quality readings by community |

## Tests

- **28 test cases** across TestSaskPrompts (13) and TestSaskResources (15)
- `test_resources_have_zero_parameters`: verifies all 7 resources have 0 function parameters via `inspect.signature`
- `test_portal_guide_documents_multi_org`: asserts both org IDs (zcv98lgAl8xQ04cW and 7MBdlVpjqbfBhQer) + SPSA present
- `test_portal_guide_deferred_domains`: asserts 511/transport and health deferred sections present
- Coverage: **97.27%** (Saskatchewan module; above 95% threshold)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Message.content is TextContent, not str**
- **Found during:** Task 1 test execution (GREEN phase)
- **Issue:** Tests used `m.content` directly in string join — `Message.content` is `mcp.types.TextContent` with a `.text` attribute, not a raw `str`
- **Fix:** Changed `m.content` to `m.content.text` with `hasattr(m.content, "text")` guard (matches Manitoba test pattern)
- **Files modified:** `__tests__/test_prompts_resources.py`
- No separate commit — fixed inline during Task 1 GREEN phase before committing

## Self-Check

- [x] `src/mcp_canada/modules/saskatchewan/prompts.py` exists (6 prompts)
- [x] `src/mcp_canada/modules/saskatchewan/resources.py` exists (7 resources)
- [x] 28 tests pass, coverage 97.27%
- [x] All resources have ZERO parameters (verified by test_resources_have_zero_parameters)
- [x] portal-guide documents both deferred domains (transport + health)
- [x] portal-guide documents both org IDs and SPSA server

## Self-Check: PASSED
