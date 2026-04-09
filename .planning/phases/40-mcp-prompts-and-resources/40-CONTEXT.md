# Phase 40: MCP Prompts and Resources - Context

**Gathered:** 2026-04-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Add MCP prompts (guided workflow templates) and resources (static reference data) to all existing modules. Prompts give agents pre-built conversation flows that chain tools together. Resources give agents instant access to reference catalogs, documentation guides, and response templates without extra tool calls. This is a cross-cutting phase that touches all 12 modules plus shared infrastructure.

</domain>

<decisions>
## Implementation Decisions

### Prompt types
- Both guided workflows (multi-step, multi-turn) AND quick lookup templates per module
- Guided workflows return `list[Message]` with user + assistant messages to prime the conversation
- Quick lookups return single instruction strings for common queries
- 4-6 prompts per module (~60 prompts total across 12 modules)

### Resource types
- Three categories: reference catalogs (JSON), documentation guides (markdown), and response templates (markdown with placeholders)
- 6-10 resources per module (~80-100 resources total)
- Catalogs: valid value lists agents need repeatedly (currency codes, series names, province codes, CKAN org lists, drug schedule codes)
- Docs: data quirks, API limitations, interpretation guides (e.g., "How to read StatCan metadata")
- Templates: example response formats for common queries

### Bilingual support
- Both prompts and resources support bilingual content (en/fr)
- Prompts accept a `lang` parameter, return instructions in chosen language
- Resources include both English and French labels/descriptions in a single resource

### Naming convention
- Prompts follow module prefix convention: `boc_analyze_rates`, `toronto_explore_neighbourhood`, `statcan_find_data`
- Resource URIs are type-prefixed: `data://boc/currency-codes`, `docs://boc/series-naming`, `template://boc/rate-comparison`

### Discovery and visibility
- Native MCP protocol visibility — no extra listing tools needed
- Prompts appear as slash-commands in Claude Desktop via `prompts/list`
- Resources appear as browsable references via `resources/list`
- Listings are lightweight (name + description only, content loads on demand)

### Resource format
- JSON for catalogs (machine-parseable)
- Markdown for documentation guides (human-readable)
- Markdown with placeholders for templates

### Claude's Discretion
- Exact prompt conversation flow per module (which tools to chain and in what order)
- Which specific data points become catalog resources vs stay in tool responses
- How to structure documentation guides (sections, depth, examples)
- Whether FileSystemProvider auto-discovers prompts/resources or needs manual registration

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `FastMCP.prompt()` decorator and `FastMCP.add_prompt()` — available in FastMCP 3.2.x (`server.py` L1777-1808)
- `FastMCP.resource()` decorator and `FastMCP.add_resource()` — available in FastMCP 3.2.x (`server.py` L1622-1765)
- `shared/i18n.py` — `t(key, lang)` bilingual message system, extend for prompt/resource text
- `_example/` module — template for new modules, will be updated with prompt/resource examples

### Established Patterns
- FileSystemProvider auto-discovers `@tool` functions from module directories
- BM25SearchTransform only wraps tools — prompts and resources are separate MCP primitives
- Module `__init__.py` exports `MODULE_NAME` and `MODULE_DESCRIPTION`
- All tools use standalone `@tool` from `fastmcp.tools` — prompts/resources likely need standalone decorators too

### Integration Points
- `server.py` — may need modification if FileSystemProvider doesn't auto-discover prompts/resources
- Each module's `__init__.py` — may need to export prompt/resource metadata
- `CLAUDE.md` — rules section needs updating for prompt/resource conventions
- `README.md` — needs prompt and resource catalog sections
- `_example/` module — needs prompts.py and resources.py templates

</code_context>

<specifics>
## Specific Ideas

- mcp-brasil pattern: 63 prompts + 88 resources across ~20 features, auto-discovered via FeatureRegistry
- Module file structure extends from 5-file to 7-file: add `prompts.py` + `resources.py`
- _example module gets updated with annotated prompt/resource templates for future module authors
- Prefer auto-discovery if FileSystemProvider supports it — keep server.py untouched per module

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 40-mcp-prompts-and-resources*
*Context gathered: 2026-04-09*
