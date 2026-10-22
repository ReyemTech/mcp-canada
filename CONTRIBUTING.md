# Contributing

Contributions are welcome: fixes, new data sources, better documentation, and tests.
Keep a pull request focused on one change and explain the behavior it delivers.
For a new data source, open an issue first if the intended scope is unclear.

## Set up and verify

Use Python 3.12 or newer and [uv](https://docs.astral.sh/uv/). CI checks Python
3.12, 3.13, and 3.14. Fork the repository and create a branch from current `main`.

```bash
uv sync --locked --dev
uv run ruff check src/ tests/
uv run pyright
uv run pytest --cov=src/mcp_canada
uv run python scripts/generate_catalog.py --check
```

Coverage must remain at least **95%**. Default unit tests must mock network calls.
Bug fixes need a regression test that fails before the fix and passes afterward.
When changing PR automation, also run the dependency-free Node.js tests:

```bash
node --test .github/scripts/*.test.cjs
```

## Adding or changing a data module

Use `src/mcp_canada/modules/<module>/` with these files:

| File | Responsibility |
| --- | --- |
| `__init__.py` | Module name and bilingual descriptions |
| `constants.py` | Portal URLs, rate limits, cache TTLs, mappings |
| `schemas.py` | Flat Pydantic v2 models |
| `client.py` | Async upstream calls returning `(data, was_cached)` |
| `tools.py` | Standalone `@tool` functions and response envelopes |
| `prompts.py` | Bilingual workflows and quick lookups |
| `resources.py` | Zero-argument resources with bilingual reference content |
| `__tests__/` | Colocated unit tests and fixtures |

Modules register automatically through `FileSystemProvider`; a new module should
not require changes to `server.py`. Reuse clients in `shared/` where appropriate,
but verify their behavior against the new portal instead of assuming compatibility.
Avoid new dependencies and unrelated refactoring.

### Verify the upstream service

Confirm the actual portal technology, API endpoints, authentication requirements,
dataset identifiers, and field names against the live service. Branding, a familiar
URL, and a mocked fixture are not enough. Describe what you verified and when in
the PR. Do not claim live verification when a request failed or was not attempted.

### Complete pagination and truthful parameters

- Search results may be paginated; return an accurate total and effective limits.
- Tools that list all categories, publishers, or counts must fetch every catalog
  page. A single request with `limit=1000` is incomplete when the catalog has 1,421
  datasets. Aggregate across pages, or explicitly expose partial results.
- Test multiple pages, a final short page, and categories/publishers appearing only
  on a later page. Guard against an upstream returning an empty page unexpectedly.
- Every public parameter must affect behavior as documented. For example,
  `include_geometry=False` must actually exclude geometry if that is its contract;
  changing only a cache key does not implement the parameter. Otherwise remove the
  option and document explicit column selection.
- Test both sides of boolean options, filter propagation, limit boundaries, and
  pagination offsets. Inspect the shared helper as well as the calling module.

### Response and error conventions

- Tools use standalone `@tool`, a module-prefixed name, a `lang: Literal["en", "fr"]`
  argument, and docstrings with `Use for:` and `Keywords:` lines.
- Return `make_response()` on success and a structured `make_error()` on failure.
  Use `@upstream_guard(...)` or complete exception handling so timeouts, malformed
  JSON, and unexpected response shapes do not escape as raw tool exceptions.
- Raise `InvalidInput` for caller mistakes, `NotFound` for a missing requested
  record, and `UpstreamData` for unusable upstream responses. Plain `ValueError`
  must not be used to classify caller errors.
- Decode upstream JSON through `decode_json()` / `decode_json_bytes()` from
  `shared/http.py`. Do not call `response.json()` directly in portal clients.
- Use caching and the per-source rate limiter. Keep responses flat and bounded.
- When reading Python source or repository text, use `encoding="utf-8"` explicitly
  so checks also work on Windows locales.

See [CLAUDE.md](CLAUDE.md) for the full project conventions and portal-specific facts.

## Tests through the MCP layer

Add live scenarios in `tests/integration/test_tool_scenarios.py` for each new tool.
Mark them `integration` and call through the MCP Client, rather than calling the
Python client function directly. Include discovery, a real successful call, bad
input/error behavior, and cross-module use when relevant. For a discovery-to-query
workflow, cover dataset details and a query as well as catalog search.

```bash
uv run pytest tests/integration/ -v -m integration --timeout=120
```

Every branch of an integration test must assert something. Use
`assert_live_or_transient` and `assert_rows` from the integration helpers to tolerate
a genuine temporary outage. Do not silently return, skip based on response data,
or accept either success or any error. A permanently broken endpoint is a defect.
Live tests run separately from PR unit checks because upstream availability varies.

## Documentation and generated catalogs

Add or update `docs/modules/<module>.md` and the README module table when a module
changes. Check both English and French descriptions, prompts, and resource content.
Do not manually edit generated `TOOLS.md` sections. After adding, removing, or
renaming tools, changing signatures, or editing tool descriptions:

```bash
uv run python scripts/generate_catalog.py
uv run python scripts/generate_catalog.py --check
```

Commit the generated changes with the implementation. Inspect the diff: generated
changes do not replace a human-written module guide.

## What happens after opening a PR

1. CI runs lint, type checks, unit tests with coverage, and catalog freshness checks.
   Established GitHub accounts can run automatically under the repository policy;
   a first-time contributor with a new GitHub account may need maintainer approval.
   Approval to run checks is separate from approval to merge.
2. After CI completes, **PR Checks** lists failures, reproduction commands, and log
   links. Fix failures and push an update; the existing comment is updated.
3. **PR Review** provides advisory findings with priorities and source links.
   Address relevant findings or explain why a finding does not apply. A missing,
   failed, or size-limited review explicitly requires manual review; it is not a pass.
4. The maintainer decides whether to merge. Passing checks and an automated review
   do not merge or approve the PR automatically.

Automatic reviews run for ready, open PRs after CI; drafts are skipped. Pushing a new revision
reruns checks and invalidates older review results. Maintainers can rerun review
from the **PR Feedback** workflow with a PR number, including drafts. Feedback workflows must be on
the default branch before they can run automatically.

## Commit messages and PR descriptions

Use concise conventional commit titles such as `fix: handle empty catalog pages`
or `feat: add a municipal data module`. Describe the problem, resulting behavior,
validation performed, and any limits. Include a reproduction for bug fixes.

Do not add tool/model attribution, generated-by footers, session links, badges, or
AI `Co-Authored-By` trailers to commits or PR descriptions. Contributors remain
responsible for verifying all submitted changes.

For maintainer setup and troubleshooting, see [PR automation](docs/pr-automation.md).
