# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Unit tests (fast, mocked — default)
uv run pytest

# Single test file
uv run pytest src/mcp_canada/modules/bank_of_canada/__tests__/test_tools.py -x -v

# Single test
uv run pytest src/mcp_canada/modules/bank_of_canada/__tests__/test_tools.py::TestBocGetExchangeRates::test_returns_exchange_rates -x

# Integration tests (live APIs, ~2min)
uv run pytest tests/integration/ -v -m integration --timeout=120

# Coverage (must be ≥95%)
uv run pytest --cov=src/mcp_canada --cov-fail-under=95

# Start server
uv run mcp-canada                                    # stdio
uv run mcp-canada --transport sse --port 8000         # SSE
uv run mcp-canada --transport http --port 8000        # Streamable HTTP
uv run mcp-canada --modules bank_of_canada,recalls    # selective

# Type check & lint
uv run pyright
uv run ruff check src/ tests/
```

## Architecture

**FastMCP 3.2.x** with FileSystemProvider auto-discovery. Drop a module folder into `src/mcp_canada/modules/` — it registers automatically.

**BM25SearchTransform** hides all tools behind `discover_tools` + `call_tool`. Agents see 3 always-visible tools; the ~50 underlying tools are found via BM25 search.

**Lifespan** creates a shared `httpx.AsyncClient`. Supports stdio, SSE, and Streamable HTTP.

### Module Pattern (7 files + tests)

Every module in `src/mcp_canada/modules/{name}/`:

| File | Purpose |
|------|---------|
| `__init__.py` | `MODULE_NAME` and `MODULE_DESCRIPTION` |
| `constants.py` | `BASE_URL`, `RATE_GROUP`, `RATE_LIMIT`, `CACHE_TTL`, mappings |
| `schemas.py` | Pydantic v2 models — always flat |
| `client.py` | Async functions returning `(data, was_cached)` tuples |
| `tools.py` | `@tool` functions (standalone, NOT `@mcp.tool`) |
| `prompts.py` | `@prompt` functions — guided workflows + quick lookups |
| `resources.py` | `@resource` functions — catalogs, docs, templates |
| `__tests__/` | `conftest.py`, `test_client.py`, `test_tools.py`, `test_prompts_resources.py` |

### Shared Utilities (`src/mcp_canada/shared/`)

- `cache.py` — `cached_fetch(key, ttl, fetcher)` → `(data, was_cached)`
- `envelope.py` — `make_response()` / `make_error()` for _meta envelope
- `rate_limiter.py` — `get_limiter(source, rate)` per-source TokenBucket
- `http.py` — `api_get(url, params, headers)` with retry on 429/5xx
- `i18n.py` — `t(key, lang)` bilingual error messages

## Core Rules

**TDD: Red → Green → Refactor.** Write failing tests first. Bug fixes require a reproduction test.

**Every `@tool` must:** use standalone `@tool` from `fastmcp.tools`, include `lang: Literal["en", "fr"]`, return `make_response()`/`make_error()`, have `Use for:` + `Keywords:` in docstring, use module prefix (`boc_`, `parl_`, etc.).

**Every client function must:** return `(data, was_cached)`, use `cached_fetch()` + `get_limiter()`, flatten responses aggressively.

**Don't:** add dependencies, modify `server.py` for new modules, put module tests in top-level `tests/`, skip rate limiting, mix refactoring with feature work.

**After implementing any tool:** add integration tests in `tests/integration/test_tool_scenarios.py` that call the tool through the MCP Client layer (not client functions directly). Think in sample prompts — what would an agent ask? See `.claude/rules/tests.md` for the pattern.

**Docstring quality is enforced by `test_quality.py` — it will fail your tests if Keywords/Use-for lines are missing.**

## Prompt and Resource Rules

### Every `@prompt` must:
- Use standalone `@prompt` from `fastmcp.prompts` — never `@mcp.prompt`
- Include `lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en"` parameter
- Use module prefix naming: `boc_`, `parl_`, `wx_`, `rcll_`, `drug_`, `ckan_`, etc.
- Have a docstring describing when agents should use this prompt

**Guided workflow prompts** chain multiple tools for complex analysis:
- Return `list[Message]` with user + assistant roles (at least 2 messages)
- First message (user role): asks what the agent wants to analyze
- Second message (assistant role): gives step-by-step instructions with specific tool calls

**Quick lookup prompts** guide a single-tool call:
- Return `str` with tool name and parameter instructions
- Result is treated as a single user message by FastMCP

### Every `@resource` must:
- Use standalone `@resource` from `fastmcp.resources` — never `@mcp.resource`
- Have ZERO function parameters — any parameter (including `lang`) promotes the function to ResourceTemplate and removes it from `resources/list`
- Use type-prefixed URI scheme: `data://`, `docs://`, or `template://`
- Use module-prefixed URI path: e.g., `data://boc/currency-codes`

**URI scheme conventions:**
- `data://` — JSON catalogs: return `json.dumps(...)`. Bilingual content embedded inline (both `en`/`fr` in same JSON).
- `docs://` — Markdown guides: return raw markdown string. Both languages can be in the same document.
- `template://` — Markdown templates: return markdown with `{placeholder}` syntax for agents to fill in.

**Resource content rules:**
- `data://` resources must be valid JSON — never return Python dict directly
- Bilingual content belongs inline, not behind a `lang` parameter
- Static reference data (e.g., neighbourhood lists) should be embedded, not fetched via HTTP

### Weather module exception:
- `prompts.py` lives at the top-level `weather/` (not in sub-modules). FileSystemProvider scans recursively — one file covers all 8 sub-modules and avoids duplicates.
