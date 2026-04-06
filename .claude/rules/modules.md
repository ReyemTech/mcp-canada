---
description: Rules for creating or modifying API modules in src/mcp_canada/modules/
globs: src/mcp_canada/modules/**/*.py
---

# Module Development Rules

## Tool Function Requirements

Every `@tool` function must:

1. Use standalone `@tool` from `fastmcp.tools` — never `@mcp.tool` (FileSystemProvider won't register it)
2. Include `lang: Literal["en", "fr"] = "en"` parameter
3. Return `make_response(data, api_name=..., api_url=..., cached=..., lang=...)` on success
4. Return `make_error(code, message, lang=..., **extras)` on failure — never raise exceptions
5. Have a docstring with:
   - First line: what the tool does
   - `Use for:` line describing when agents should use it
   - `Keywords:` line with BM25 search terms (minimum 8 keywords)
6. Use module prefix naming: `boc_`, `parl_`, `wx_`, `rcll_`, `drug_`, `ckan_`, `nutrient_`

## Client Function Requirements

1. All public functions return `(data, was_cached)` tuples
2. Use `cached_fetch()` from shared/cache.py
3. Use `get_limiter()` from shared/rate_limiter.py
4. Flatten API responses aggressively — Pydantic models should be flat, not mirror API nesting
5. Convert string values to proper types (e.g., `{"v": "1.35"}` → `float`)
6. Sort observations newest-first
7. On 404 from invalid input, include `suggestions` via `difflib.get_close_matches()`

## Error Codes

Use these in `make_error()`:
- `INVALID_SERIES` / `INVALID_INPUT` — bad user input, include suggestions
- `NOT_FOUND` — resource doesn't exist
- `UPSTREAM_ERROR` — API returned unexpected error
- `RATE_LIMITED` — include `retry_after`

## Response Envelope

```python
# Success
{"_meta": {"source": {"api": "...", "url": "..."}, "cached": bool, "lang": "en", "timestamp": "ISO8601"}, "data": [...]}

# Error
{"error": {"code": "INVALID_SERIES", "message": "...", "suggestions": [...]}}
```

## API Limitations Go in Docstrings

Don't document API quirks in code comments — put them in the tool docstring where agents will see them. Example: "Note: the API returns house-wide totals, NOT individual MP votes."

## README Must Stay in Sync

When you create, update, or remove a tool, you MUST update `README.md`:

- **Adding a tool:** Add it to the module's section in the Tool Catalog with the first line of its docstring
- **Updating a tool:** If the name or description changed, update the README entry
- **Removing a tool:** Remove it from the README
- **Adding a module:** Add a new section with all its tools
- **Removing a module:** Remove the entire section

Also update the tool count in the README header (currently "47 tools across 6 APIs").

The README is the first thing potential users see. Stale tool catalogs erode trust.
