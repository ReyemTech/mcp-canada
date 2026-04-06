---
description: Rules for writing tests
globs: "**/test_*.py, **/__tests__/**/*.py, tests/**/*.py"
---

# Testing Rules

## TDD: Red → Green → Refactor

1. Write a failing test first (RED)
2. Write minimal code to pass it (GREEN)
3. Improve implementation while keeping tests green (REFACTOR)

Bug fixes require a reproduction test that fails before the fix is applied.

## Red Flags

- Implementing features without tests
- Tests that pass immediately (not testing anything)
- Fixing bugs without a reproduction test
- Disabling tests to make the suite pass
- Testing framework behavior instead of application logic
- Vague test names that don't describe expected outcomes

## Unit Tests (module-specific)

- Go in colocated `__tests__/` directory inside the module folder
- Mock all HTTP calls with `patch("httpx.AsyncClient")`
- Use `conftest.py` with sample API responses
- Test both happy path and error paths (404, generic exceptions)
- Verify `_meta` envelope structure on success responses
- Verify `error.code` and `error.message` on error responses
- Verify `lang` parameter passes through to envelope

## Integration Tests (MANDATORY for every new tool)

After implementing a tool, you MUST add integration tests that call the tool through the MCP layer — the same way an agent would use it. **Do NOT call client functions directly — that's just a unit test without mocks.**

### How to call tools through MCP

```python
from mcp_canada.server import mcp, _build_providers, _MODULES_DIR, _META_DIR
from fastmcp import Client
from fastmcp.server.providers import FileSystemProvider
from fastmcp.server.transforms.search import BM25SearchTransform

# Wire up providers (same as server main() does)
providers = _build_providers('')
for p in providers:
    mcp.add_provider(p)
if _META_DIR.is_dir():
    mcp.add_provider(FileSystemProvider(root=_META_DIR))
mcp.add_transform(BM25SearchTransform(
    max_results=5,
    always_visible=['discover_tools', 'list_modules'],
    search_tool_name='discover_tools',
    call_tool_name='call_tool',
))

async with Client(mcp) as client:
    # Call tool through MCP like an agent would
    result = await client.call_tool('call_tool', {
        'name': 'boc_get_exchange_rates',
        'arguments': {'currency': 'USD', 'recent': 3}
    })
    data = json.loads(result.content[0].text)
    assert "_meta" in data
    assert data["_meta"]["source"]["api"] == "bank-of-canada-valet"
```

### Integration test structure

Every new tool needs these scenarios in `tests/integration/test_tool_scenarios.py`:

1. **Happy path** — tool returns real data with correct `_meta` envelope
2. **Discovery** — `discover_tools` finds the tool with a natural language query
3. **Error handling** — tool returns structured error for bad input (not an exception)
4. **Cross-module** — where applicable, combine with another module's tool

### Think in sample prompts

For every tool, imagine what an agent user would ask. Turn those prompts into test names:

```python
async def test_current_usd_cad_rate(self):
    """'What's the current USD to CAD exchange rate?'"""

async def test_anna_roberts_ballot_on_vote_333(self):
    """'How did Anna Roberts vote on vote 44-1/333?'"""
```

### Rules

- Go in `tests/integration/`
- Mark with `@pytest.mark.integration` (skipped by default in CI)
- Call tools through MCP Client, not client functions directly
- Use long timeouts (90s for Drug API, 30s for others)
- Handle flaky APIs: check `r.content` before `.json()`, check content-type
- Assert on response shape, not specific values (data changes daily)
- Run with: `uv run pytest tests/integration/ -v -m integration --timeout=120`

## Coverage

- Must be ≥95%: `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- `test_quality.py` enforces BM25 docstring quality on ALL tools automatically
