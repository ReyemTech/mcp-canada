# Phase 40: MCP Prompts and Resources - Research

**Researched:** 2026-04-09
**Domain:** FastMCP 3.2.0 prompts and resources — standalone decorators, FileSystemProvider auto-discovery, MCP protocol visibility
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Both guided workflows (multi-step, multi-turn) AND quick lookup templates per module
- Guided workflows return `list[Message]` with user + assistant messages to prime the conversation
- Quick lookups return single instruction strings for common queries
- 4-6 prompts per module (~60 prompts total across 12 modules)
- Three resource categories: reference catalogs (JSON), documentation guides (markdown), and response templates (markdown with placeholders)
- 6-10 resources per module (~80-100 resources total)
- Catalogs: valid value lists agents need repeatedly (currency codes, series names, province codes, CKAN org lists, drug schedule codes)
- Docs: data quirks, API limitations, interpretation guides
- Templates: example response formats for common queries
- Both prompts and resources support bilingual content (en/fr)
- Prompts accept a `lang` parameter, return instructions in chosen language
- Resources include both English and French labels/descriptions in a single resource
- Prompts follow module prefix convention: `boc_analyze_rates`, `toronto_explore_neighbourhood`, `statcan_find_data`
- Resource URIs are type-prefixed: `data://boc/currency-codes`, `docs://boc/series-naming`, `template://boc/rate-comparison`
- Native MCP protocol visibility — no extra listing tools needed
- Prompts appear as slash-commands in Claude Desktop via `prompts/list`
- Resources appear as browsable references via `resources/list`
- Listings are lightweight (name + description only, content loads on demand)
- JSON for catalogs (machine-parseable)
- Markdown for documentation guides (human-readable)
- Markdown with placeholders for templates

### Claude's Discretion
- Exact prompt conversation flow per module (which tools to chain and in what order)
- Which specific data points become catalog resources vs stay in tool responses
- How to structure documentation guides (sections, depth, examples)
- Whether FileSystemProvider auto-discovers prompts/resources or needs manual registration

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

---

## Summary

FastMCP 3.2.0's `FileSystemProvider` **auto-discovers `@prompt` and `@resource` decorated functions** from any `.py` file under the module directory — the same mechanism used for `@tool`. The `extract_components()` function in `filesystem_discovery.py` explicitly handles `Tool`, `Resource`, `ResourceTemplate`, and `Prompt` objects, confirming zero server.py changes are needed per module. This was verified empirically: adding `prompts.py` and `resources.py` to a test directory produced auto-discovered `FunctionPrompt` and `FunctionResource` components.

Custom URI schemes (`data://`, `docs://`, `template://`) work out of the box — FastMCP stores URIs as `AnyUrl` strings and does not restrict URI scheme. The `@resource` decorator requires its URI as the first positional argument. The `@prompt` decorator works bare (no arguments). `BM25SearchTransform` is tool-only and has zero interaction with prompts or resources; they are separate MCP primitives exposed through `prompts/list` and `resources/list` natively.

**Primary recommendation:** Add `prompts.py` + `resources.py` to each of the 12 non-example modules. FileSystemProvider picks them up automatically. No server.py changes required. The 5-file module pattern extends to 7-file cleanly.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `fastmcp.prompts.prompt` | 3.2.0 | Standalone `@prompt` decorator | Attaches `PromptMeta` to function; FileSystemProvider extracts it |
| `fastmcp.prompts.Message` | 3.2.0 | Prompt message wrapper | Accepts str, dict, list, BaseModel; auto-serializes to TextContent |
| `fastmcp.resources.resource` | 3.2.0 | Standalone `@resource(uri)` decorator | Attaches `ResourceMeta`; FileSystemProvider extracts it |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `fastmcp.prompts.PromptResult` | 3.2.0 | Explicit prompt result type | Not needed — return `list[Message]` or `str` directly |
| `typing.Literal` | stdlib | `lang: Literal["en", "fr"]` | All prompts need bilingual lang param |
| `json` | stdlib | Serialize catalog resources | For `data://` catalog resources returning JSON strings |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `@resource` (function) | `TextResource` / `FileResource` | Function resources allow dynamic/bilingual content; file resources are static — use function form |
| `list[Message]` return | `PromptResult` directly | `list[Message]` is simpler; FastMCP's `convert_result()` handles the conversion |

**Installation:**
No new packages needed. All imports are already in the project's FastMCP dependency.

```bash
# No additional install needed — fastmcp 3.2.0 already installed
```

---

## Architecture Patterns

### Recommended Module Structure (7-file pattern)
```
src/mcp_canada/modules/{name}/
├── __init__.py         # MODULE_NAME, MODULE_DESCRIPTION (unchanged)
├── constants.py        # BASE_URL, RATE_GROUP, mappings (unchanged)
├── schemas.py          # Pydantic v2 models (unchanged)
├── client.py           # Async fetch functions returning (data, was_cached) (unchanged)
├── tools.py            # @tool functions (unchanged)
├── prompts.py          # @prompt functions — NEW in Phase 40
├── resources.py        # @resource functions — NEW in Phase 40
└── __tests__/
    ├── conftest.py
    ├── test_client.py
    ├── test_tools.py
    └── test_prompts_resources.py   # NEW in Phase 40
```

### Pattern 1: Guided Workflow Prompt (multi-turn)
**What:** Returns `list[Message]` priming a multi-turn agent conversation — user question + assistant setup reply
**When to use:** When agents need guided step-by-step tool chaining (e.g., search → fetch → analyze)

```python
# Source: Verified with FastMCP 3.2.0 prompts/function_prompt.py
from fastmcp.prompts import prompt, Message
from typing import Literal

@prompt
async def boc_analyze_rates(lang: Literal["en", "fr"] = "en") -> list[Message]:
    """Guide an agent through a Bank of Canada exchange rate analysis workflow.

    Chains boc_search_series → boc_get_exchange_rates → boc_get_series_metadata
    to answer questions about CAD exchange rates.
    """
    if lang == "fr":
        return [
            Message(
                "Quelles devises souhaitez-vous analyser? "
                "Exemples: USD, EUR, GBP, JPY. "
                "Je peux récupérer les taux actuels et historiques.",
                role="user",
            ),
            Message(
                "Je vais utiliser boc_get_exchange_rates pour récupérer les données "
                "de l'API Valet de la Banque du Canada. Commençons.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which currencies would you like to analyze? "
            "Examples: USD, EUR, GBP, JPY. "
            "I can fetch current and historical CAD exchange rates.",
            role="user",
        ),
        Message(
            "I will use boc_get_exchange_rates to retrieve data from the "
            "Bank of Canada Valet API. Let's get started.",
            role="assistant",
        ),
    ]
```

### Pattern 2: Quick Lookup Prompt (single string)
**What:** Returns a `str` instruction for a common single-step query
**When to use:** Simple lookups where an agent needs guidance on which tool and parameters to use

```python
# Source: Verified with FastMCP 3.2.0 — str return becomes a single user Message
@prompt
async def boc_get_policy_rate(lang: Literal["en", "fr"] = "en") -> str:
    """Get the current Bank of Canada overnight policy rate."""
    if lang == "fr":
        return (
            "Utilisez boc_get_interest_rates avec rate_type='policy' et recent=1 "
            "pour obtenir le taux directeur actuel de la Banque du Canada."
        )
    return (
        "Use boc_get_interest_rates with rate_type='policy' and recent=1 "
        "to get the current Bank of Canada overnight policy rate."
    )
```

### Pattern 3: Reference Catalog Resource (JSON)
**What:** Static JSON catalog of valid values agents need frequently
**When to use:** Lists of valid codes, series names, province codes, organization IDs

```python
# Source: Verified with FastMCP 3.2.0 resources/function_resource.py
from fastmcp.resources import resource
import json

@resource(
    "data://boc/currency-codes",
    mime_type="application/json",
    name="boc_currency_codes",
    title="Bank of Canada Currency Codes",
)
def boc_currency_codes() -> str:
    """Valid currency codes for the Bank of Canada Valet FX series.

    Use this catalog to find the currency parameter for boc_get_exchange_rates.
    Format: {"CODE": {"en": "English name", "fr": "Nom en français"}}
    """
    return json.dumps({
        "USD": {"en": "US Dollar", "fr": "Dollar américain"},
        "EUR": {"en": "Euro", "fr": "Euro"},
        "GBP": {"en": "British Pound", "fr": "Livre sterling"},
        # ... additional currencies
    }, ensure_ascii=False, indent=2)
```

### Pattern 4: Documentation Guide Resource (Markdown)
**What:** Markdown documentation explaining API quirks, naming conventions, interpretation guides
**When to use:** When agents need conceptual context before querying (e.g., "what does scalar factor 6 mean?")

```python
@resource(
    "docs://boc/series-naming",
    mime_type="text/markdown",
    name="boc_series_naming_guide",
    title="Bank of Canada Series Naming Convention",
)
def boc_series_naming_guide() -> str:
    """Guide to Bank of Canada Valet API series naming conventions.

    Explains the FX{CURRENCY}CAD pattern and available group names.
    """
    return """# Bank of Canada Series Naming

## Exchange Rate Series
Series follow the pattern `FX{CURRENCY}CAD`.
- `FXUSDCAD` — US Dollar to Canadian Dollar
- `FXEURCAD` — Euro to Canadian Dollar

## Groups
Use groups for bulk retrieval:
- `FX_RATES_DAILY` — All daily FX rates
- `BCPI_MONTHLY` — Commodity price index

## Finding Series
Use `boc_search_series` with a keyword, or `boc_list_groups` to browse.
"""
```

### Pattern 5: Response Template Resource (Markdown with placeholders)
**What:** Markdown template showing example formatted response for common queries
**When to use:** When agents need a response format example to model output after

```python
@resource(
    "template://boc/rate-analysis-report",
    mime_type="text/markdown",
    name="boc_rate_analysis_template",
    title="BoC Rate Analysis Report Template",
)
def boc_rate_analysis_template() -> str:
    """Template for formatting a Bank of Canada rate analysis report."""
    return """# Exchange Rate Analysis: {currencies}

**Period:** {start_date} to {end_date}
**Source:** Bank of Canada Valet API

## Summary
{summary_text}

## Data Table
| Date | {column_headers} |
|------|{separator}|
{data_rows}

## Key Observations
- {observation_1}
- {observation_2}
"""
```

### Anti-Patterns to Avoid
- **Returning non-serializable objects from @resource:** Resources must return `str`, `bytes`, or a `ResourceResult`. Return `json.dumps(...)` not a raw dict.
- **Using `@mcp.prompt` or `@mcp.resource`:** FileSystemProvider only auto-discovers standalone decorators. Use `from fastmcp.prompts import prompt` and `from fastmcp.resources import resource`.
- **URI without scheme separator:** `data://boc/currency-codes` is valid; `data:boc/currency-codes` is not (AnyUrl requires `://`).
- **Parametric URIs without URI template syntax:** If a resource takes function parameters, use `{param}` in the URI to make it a `ResourceTemplate` (not `FunctionResource`). For Phase 40, avoid parametric resources — keep all resources static (no function parameters).
- **Mutable bilingual dicts in resource:** Construct bilingual content inline within the function; do not share mutable module-level state.
- **Prompt with *args or **kwargs:** FastMCP rejects these at `Prompt.from_function()` time with `ValueError`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Prompt registration | Custom registry / server.py modification | `@prompt` decorator + FileSystemProvider | auto-discovery is built-in; confirmed working |
| Resource registration | Custom registry / server.py modification | `@resource(uri)` decorator + FileSystemProvider | same auto-discovery pipeline as tools |
| Message serialization | Manual MCP message dict construction | `Message(content, role=...)` | handles str/dict/list/BaseModel → TextContent automatically |
| Bilingual prompt text | Separate prompt functions per language | Single `@prompt` with `lang` param returning `if lang == "fr":` branches | single name in `prompts/list`, cleaner |
| URI scheme validation | Custom validator | Use `data://`, `docs://`, `template://` as-is | AnyUrl accepts any scheme; MCP clients enumerate by URI prefix |

**Key insight:** FileSystemProvider's `extract_components()` already handles all four component types (`Tool`, `Resource`, `ResourceTemplate`, `Prompt`). The discovery is identical — no special registration code is needed.

---

## Common Pitfalls

### Pitfall 1: Forgetting the Resource URI must have `://` separator
**What goes wrong:** `@resource("data:boc/catalog")` raises `pydantic.ValidationError` when FastMCP creates `AnyUrl(uri)`.
**Why it happens:** AnyUrl requires a valid URL scheme with `://`.
**How to avoid:** Always use `data://module/resource-name` format.
**Warning signs:** `pydantic_core.core_schema.UrlSchema` validation errors at server startup.

### Pitfall 2: Resource function with parameters becomes ResourceTemplate, not Resource
**What goes wrong:** A resource with function parameters (even `lang`) becomes a `ResourceTemplate` which has a different URI pattern and is not listed in `resources/list` the same way.
**Why it happens:** `filesystem_discovery.py` checks `has_uri_params or has_func_params` — any function parameter triggers template mode.
**How to avoid:** For Phase 40 static resources, use zero-parameter functions. Handle bilingual content inline (both languages in one JSON/Markdown response), not via a `lang` parameter.
**Warning signs:** Resource not appearing in `resources/list` but appearing in `resources/templates/list`.

### Pitfall 3: Prompt lang parameter appears in agent UI with complex JSON schema description
**What goes wrong:** `lang: Literal["en", "fr"]` shows a verbose JSON schema note in the prompt argument description ("Provide as a JSON string matching...").
**Why it happens:** FastMCP appends schema notes for non-str parameters in prompt arguments.
**How to avoid:** Add an explicit `description` annotation: `lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en"`. This replaces the auto-generated schema note.
**Warning signs:** Verbose argument descriptions when calling `client.list_prompts()`.

### Pitfall 4: Test files in `__tests__/` are discovered by FileSystemProvider but have no components
**What goes wrong:** `discover_and_import` scans `__tests__/conftest.py`, `test_tools.py`, etc. — confirmed in testing. These import without error (no components found), but they add import overhead.
**Why it happens:** `discover_files()` only skips `__init__.py` and `__pycache__`, not `__tests__` directories.
**How to avoid:** This is harmless (no components extracted, no failures). No action needed.
**Warning signs:** N/A — this is expected behavior, not a bug.

### Pitfall 5: Module prefix collision between prompts and tools
**What goes wrong:** A prompt named `boc_get_exchange_rates` conflicts with the existing tool of the same name.
**Why it happens:** MCP tools and prompts occupy separate namespaces, but human-facing names should be distinct to avoid confusion in UX.
**How to avoid:** Use action verbs in prompt names that differ from tool names: `boc_analyze_rates` (prompt) vs `boc_get_exchange_rates` (tool). Prompts are workflow templates; tools are API calls.
**Warning signs:** Claude Desktop showing identically-named slash-commands and tools.

---

## Code Examples

Verified patterns from FastMCP 3.2.0 source and live testing:

### Complete prompts.py skeleton
```python
# Source: Verified via fastmcp.prompts.function_prompt + filesystem_discovery tests
"""MCP prompts for the Bank of Canada module.

Provides guided workflow prompts and quick lookup templates for BoC Valet API data.
All prompts are bilingual (en/fr) and use the boc_ prefix.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


@prompt
async def boc_analyze_rates(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a Bank of Canada exchange rate analysis workflow.

    Chains boc_search_series → boc_get_exchange_rates → boc_get_observations
    for comprehensive rate analysis.
    """
    if lang == "fr":
        return [
            Message("Quelles devises souhaitez-vous analyser?", role="user"),
            Message("Je vais récupérer les taux depuis l'API Valet de la BdC.", role="assistant"),
        ]
    return [
        Message("Which currencies would you like to analyze (e.g., USD, EUR, GBP)?", role="user"),
        Message("I will fetch rates from the Bank of Canada Valet API.", role="assistant"),
    ]


@prompt
async def boc_get_policy_rate(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to retrieve the current Bank of Canada policy rate."""
    if lang == "fr":
        return "Utilisez boc_get_interest_rates avec rate_type='policy' et recent=1."
    return "Use boc_get_interest_rates with rate_type='policy' and recent=1."
```

### Complete resources.py skeleton
```python
# Source: Verified via fastmcp.resources.function_resource + filesystem_discovery tests
"""MCP resources for the Bank of Canada module.

Provides reference catalogs, documentation guides, and response templates.
All resources use type-prefixed URIs: data://, docs://, template://.
"""

import json

from fastmcp.resources import resource


@resource(
    "data://boc/currency-codes",
    mime_type="application/json",
    name="boc_currency_codes",
    title="Bank of Canada Currency Codes",
)
def boc_currency_codes() -> str:
    """Valid currency codes for boc_get_exchange_rates.

    Bilingual catalog: {"CODE": {"en": "...", "fr": "..."}}
    """
    return json.dumps({
        "USD": {"en": "US Dollar", "fr": "Dollar américain"},
        "EUR": {"en": "Euro", "fr": "Euro"},
        "GBP": {"en": "British Pound", "fr": "Livre sterling"},
    }, ensure_ascii=False, indent=2)


@resource(
    "docs://boc/series-naming",
    mime_type="text/markdown",
    name="boc_series_naming_guide",
    title="BoC Series Naming Convention",
)
def boc_series_naming_guide() -> str:
    """Guide to Bank of Canada Valet API series naming and group conventions."""
    return """# Bank of Canada Series Naming

## Exchange Rate Series
Pattern: `FX{CURRENCY}CAD`
- `FXUSDCAD` — US Dollar to Canadian Dollar
- `FXEURCAD` — Euro to Canadian Dollar

## Available Groups
- `FX_RATES_DAILY` — All daily FX rates
- `BCPI_MONTHLY` — Bank of Canada Commodity Price Index

## Discovery
Use `boc_search_series` to search by keyword.
Use `boc_list_groups` to browse all available data groups.
"""


@resource(
    "template://boc/rate-report",
    mime_type="text/markdown",
    name="boc_rate_report_template",
    title="BoC Rate Analysis Report Template",
)
def boc_rate_report_template() -> str:
    """Template for formatting a Bank of Canada rate analysis report."""
    return """# Exchange Rate Report: {currency} / CAD

**Period:** {start_date} to {end_date}
**Source:** Bank of Canada Valet API

## Latest Rate
{latest_value} CAD per {currency} (as of {latest_date})

## Trend
{trend_description}
"""
```

### Unit test for prompts and resources
```python
# Source: Pattern derived from existing test_tools.py conventions
"""Unit tests for Bank of Canada prompts and resources."""
import json
import pytest
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.resources.function_resource import FunctionResource

from mcp_canada.modules.bank_of_canada.prompts import boc_analyze_rates, boc_get_policy_rate
from mcp_canada.modules.bank_of_canada.resources import boc_currency_codes, boc_series_naming_guide


class TestBocPrompts:
    @pytest.mark.asyncio
    async def test_analyze_rates_returns_messages_en(self):
        p = FunctionPrompt.from_function(boc_analyze_rates)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 2
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_analyze_rates_returns_messages_fr(self):
        p = FunctionPrompt.from_function(boc_analyze_rates)
        result = await p.render({"lang": "fr"})
        assert result.messages[0].role == "user"
        # FR content should be French
        assert "devises" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_policy_rate_returns_string_en(self):
        p = FunctionPrompt.from_function(boc_get_policy_rate)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1
        assert "boc_get_interest_rates" in result.messages[0].content.text


class TestBocResources:
    @pytest.mark.asyncio
    async def test_currency_codes_is_valid_json(self):
        r = FunctionResource.from_function(boc_currency_codes, uri="data://boc/currency-codes")
        content = await r.read()
        data = json.loads(content)
        assert "USD" in data
        assert "en" in data["USD"]
        assert "fr" in data["USD"]

    @pytest.mark.asyncio
    async def test_series_guide_is_markdown(self):
        r = FunctionResource.from_function(boc_series_naming_guide, uri="docs://boc/series-naming")
        content = await r.read()
        assert content.startswith("#")  # Markdown heading
        assert "FXUSDCAD" in content
```

### Integration test helper for prompts/resources
```python
# Source: Pattern derived from tests/integration/conftest.py
async def get_prompt(mcp_server, prompt_name: str, arguments: dict | None = None) -> list[dict]:
    """Get a prompt through the MCP Client layer."""
    async with Client(mcp_server) as client:
        result = await client.get_prompt(prompt_name, arguments or {})
        return [{"role": m.role, "text": m.content.text} for m in result.messages]


async def read_resource(mcp_server, uri: str) -> str:
    """Read a resource through the MCP Client layer."""
    async with Client(mcp_server) as client:
        content = await client.read_resource(uri)
        return content[0].text
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `decorator_mode='object'` (decorator returns Prompt/Resource objects) | Decorator attaches `__fastmcp__` metadata to function (returns function) | FastMCP 3.2.0 | `FunctionPrompt.from_function()` called lazily at discovery time, not decorator time |
| `mcp.add_prompt(fn)` / `mcp.add_resource(fn)` only | Standalone `@prompt` / `@resource` + FileSystemProvider | FastMCP 3.2.x | No server.py changes needed per module |

**Deprecated/outdated:**
- `decorator_mode='object'`: raises `FastMCPDeprecationWarning` in 3.2.0. Do not set this.
- `FunctionPrompt.from_function(fn)` called at decoration time: The new behavior attaches `PromptMeta` to the function and defers `Prompt` construction to `extract_components()`. This is internal — our code uses `@prompt` and never calls `from_function` directly in production.

---

## Open Questions

1. **Prompt argument description for `lang: Literal["en", "fr"]`**
   - What we know: FastMCP appends a JSON schema note for non-str Literal params ("Provide as a JSON string matching...")
   - What's unclear: Whether Claude Desktop presents this verbosely to users or simplifies it
   - Recommendation: Use `Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"]` to override the description explicitly

2. **Resource listing pagination at 80-100 resources**
   - What we know: MCP `resources/list` returns all resources; FastMCP does not paginate by default
   - What's unclear: Whether MCP clients handle large resource lists gracefully
   - Recommendation: Proceed with 80-100 resources — MCP spec supports this; content loads on demand so listing is lightweight

3. **FileSystemProvider and `__tests__/` directory import cost**
   - What we know: Test files are imported but produce zero components (confirmed)
   - What's unclear: Whether `conftest.py` imports (which pull in pytest fixtures) cause any side effects
   - Recommendation: Monitor first module implementation; if conftest imports cause issues, consider renaming `__tests__/` to `tests/` (no `__` prefix means FileSystemProvider still scans it but `conftest.py` imports are already handled)

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 with pytest-asyncio |
| Config file | `pyproject.toml` — `asyncio_mode = "auto"`, testpaths = `["tests", "src"]` |
| Quick run command | `uv run pytest src/mcp_canada/modules/{module}/__tests__/test_prompts_resources.py -x -v` |
| Full suite command | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |

### Phase Requirements → Test Map
No formal requirement IDs specified for Phase 40. Testing maps to behavioral expectations:

| Behavior | Test Type | Automated Command |
|----------|-----------|-------------------|
| Prompts auto-discovered by FileSystemProvider | unit | `uv run pytest src/.../test_prompts_resources.py::test_prompts_auto_discovered -x` |
| Prompt returns correct `list[Message]` for en/fr | unit | `uv run pytest src/.../test_prompts_resources.py::test_prompt_returns_messages -x` |
| Quick-lookup prompt returns single `str` | unit | `uv run pytest src/.../test_prompts_resources.py::test_quick_prompt_returns_string -x` |
| Catalog resource returns valid JSON with en+fr keys | unit | `uv run pytest src/.../test_prompts_resources.py::test_catalog_resource_json -x` |
| Docs resource returns markdown starting with `#` | unit | `uv run pytest src/.../test_prompts_resources.py::test_docs_resource_markdown -x` |
| Prompts visible via `client.list_prompts()` | integration | `uv run pytest tests/integration/ -v -m integration -k "prompt"` |
| Resources visible via `client.read_resource(uri)` | integration | `uv run pytest tests/integration/ -v -m integration -k "resource"` |
| Coverage >= 95% after addition | suite | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |

### Sampling Rate
- **Per task commit:** `uv run pytest src/mcp_canada/modules/{module}/__tests__/test_prompts_resources.py -x`
- **Per wave merge:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `src/mcp_canada/modules/{each module}/__tests__/test_prompts_resources.py` — one per module (12 files)
- [ ] `tests/integration/test_prompts_resources_scenarios.py` — integration tests calling prompts/resources through MCP Client

*(All other infrastructure exists: pytest, pytest-asyncio, conftest.py fixtures, coverage config)*

---

## Sources

### Primary (HIGH confidence)
- FastMCP 3.2.0 installed package — `.venv/lib/python3.14/site-packages/fastmcp/`
  - `server/providers/filesystem_discovery.py` — `extract_components()` lines 235-356: confirms Tool, Resource, ResourceTemplate, Prompt all auto-discovered
  - `prompts/function_prompt.py` — standalone `@prompt` decorator behavior
  - `prompts/base.py` — `Message` class, `list[Message]` return type support
  - `resources/function_resource.py` — standalone `@resource(uri)` decorator behavior
  - `server/transforms/search/base.py` + `bm25.py` — confirmed zero interaction with prompts/resources
- Live empirical tests in project `.venv` (all results verified in this session)

### Secondary (MEDIUM confidence)
- FastMCP official docs at gofastmcp.com (referenced in source code comments)

### Tertiary (LOW confidence)
- mcp-brasil pattern (63 prompts + 88 resources via FeatureRegistry) — mentioned in CONTEXT.md; not directly verified

---

## Metadata

**Confidence breakdown:**
- Auto-discovery mechanism: HIGH — verified with `discover_and_import()` live tests
- `@prompt` decorator API: HIGH — read full source + live tested `list[Message]` and `str` returns
- `@resource` decorator API: HIGH — read full source + live tested `data://`, `docs://`, `template://` URIs
- BM25 non-interaction: HIGH — confirmed `BaseSearchTransform` source has zero prompt/resource references
- MCP Client visibility: HIGH — `client.list_prompts()` and `client.read_resource()` live tested
- Parametric resource pitfall: HIGH — `filesystem_discovery.py` `has_func_params` check verified in source
- Resource lang parameter as function param: HIGH — confirmed makes it ResourceTemplate (not FunctionResource)

**Research date:** 2026-04-09
**Valid until:** 2026-05-09 (stable library; FastMCP 3.2.x API unlikely to change in 30 days)
