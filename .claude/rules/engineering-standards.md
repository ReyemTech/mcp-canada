---
description: Engineering standards for code quality, simplification, and review. Loaded on demand when reviewing code, refactoring, or making architectural decisions.
globs: "**/*.py"
---

# Engineering Standards

## Code Simplification

Before simplifying, understand why the code exists (Chesterton's Fence — check git blame).

### When to Simplify

| Pattern | Signal | Fix |
|---------|--------|-----|
| Deep nesting (3+ levels) | Hard to follow control flow | Extract guard clauses or helper functions |
| Long functions (50+ lines) | Multiple responsibilities | Split into focused functions |
| Generic names (`data`, `result`, `temp`) | Unclear purpose | Rename to describe content |
| Duplicated logic (5+ lines, 2+ places) | Copy-paste | Extract shared function |
| Dead code | Unreachable branches, commented blocks | Remove after confirming unused |
| Unnecessary wrappers | Adds no value | Inline the wrapper |
| Boolean flag params | `do_thing(true, false, true)` | Options object or separate functions |
| Nested ternaries | Mental stack to parse | Use if/else |

### When NOT to Simplify

- Code you don't fully understand
- Code outside your current task scope (no drive-by refactors)
- Performance-critical code where simpler is measurably slower
- Abstractions designed for testability or extensibility
- Code about to be entirely rewritten

### Rules

- Simplicity = comprehension speed, not line count
- Separate refactoring from feature work — never mix in one commit
- All existing tests must pass without modification
- If touching 500+ lines, use automation not manual editing
- Don't preserve speculative abstractions — remove if unused, re-add when needed

## Code Review (5-Axis)

| Axis | What to check |
|------|---------------|
| **Correctness** | Edge cases handled? Error paths covered? Tests meaningful? |
| **Readability** | Understandable without explanation? No generic names, no deep nesting? |
| **Architecture** | Follows 5-file module pattern? Module boundaries respected? |
| **Security** | No hardcoded credentials, proper input validation? |
| **Performance** | Appropriate cache TTLs? No unbounded fetches? Rate limiting configured? |

### Change Sizing

- ~100 lines: ideal
- ~300 lines: acceptable if cohesive
- 1000+ lines: must be split

### Severity Labels

- **(no prefix)** — required change
- **Critical:** — blocks merge (security, data loss, broken functionality)
- **Nit:** — optional minor improvement
- **FYI** — informational only

## Anti-Rationalization

| Excuse | Reality |
|--------|---------|
| "I'll add tests later" | Tests define the contract. Write them first. |
| "This is too simple to test" | Simple code evolves. Tests document expected behavior. |
| "I can skip the Keywords line" | BM25 discovery depends on it. Agents won't find your tool. |
| "I'll use @mcp.tool directly" | FileSystemProvider requires standalone @tool. Silently won't register. |
| "I don't need make_response" | Every tool must return the _meta envelope. Agents depend on it. |
| "Rate limiting isn't needed" | Government APIs will block the server IP. Always rate limit. |
| "I'll flatten the response later" | Nested responses waste agent context tokens now. Flatten immediately. |
| "It's working, no need to touch it" | Hard-to-read code is hard to fix when it breaks. |
| "Fewer lines is always simpler" | A 1-line nested ternary is not simpler than a 5-line if/else. |
| "I'll quickly simplify unrelated code too" | Unscoped simplification creates noisy diffs and regression risk. |
| "Abstraction might be useful later" | Don't preserve speculative abstractions. Re-add when needed. |
| "I'll refactor while adding features" | Mixed changes are harder to review, revert, and understand. |

## Dependency Policy

Don't add dependencies. The stack is complete:
- `fastmcp` — MCP server framework
- `httpx` — async HTTP client
- `pydantic` — data validation
- `aiocache` — async TTL cache
- `tenacity` — retry with backoff

If you think you need a new dependency, the existing stack likely solves it. `difflib` (stdlib) handles fuzzy matching. `asyncio.gather` handles parallel fetches.
