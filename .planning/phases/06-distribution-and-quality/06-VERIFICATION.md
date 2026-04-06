---
phase: 06-distribution-and-quality
verified: 2026-04-06T12:45:00Z
status: gaps_found
score: 5/8 must-haves verified
re_verification: false
gaps:
  - truth: "CI enforces lint and type quality (ruff + pyright pass clean)"
    status: failed
    reason: "65 ruff errors and 8 pyright errors currently exist in src/ and tests/. Both tools exit with code 1. CI would fail on every push/PR."
    artifacts:
      - path: "src/mcp_canada/modules/drug_database/tools.py"
        issue: "Unused import: httpx (F401)"
      - path: "src/mcp_canada/modules/open_parliament/schemas.py"
        issue: "Unused import: typing.Any (F401)"
      - path: "src/mcp_canada/modules/weather/current/tools.py"
        issue: "f-string without placeholders (F541)"
      - path: "src/mcp_canada/modules/weather/climate/client.py"
        issue: "Type error: Argument of type 'object' cannot be assigned to parameter of type 'ConvertibleToFloat' (pyright)"
      - path: "src/mcp_canada/modules/ckan/__tests__/test_client.py"
        issue: "Type error: 'endswith' not known attribute of 'None' (pyright)"
      - path: "src/mcp_canada/modules/weather/hydro/__tests__/test_client.py"
        issue: "6 pyright errors: None-subscript and in-operator on Optional types"
    missing:
      - "Fix 65 ruff lint errors (52 are auto-fixable with --fix)"
      - "Fix 8 pyright type errors (7 in test files, 1 in production weather/climate/client.py)"

  - truth: "All modules have >95% test coverage individually"
    status: failed
    reason: "Aggregate coverage is 96.27% (passes threshold), but multiple individual module files are well below 95%. The fail_under=95 in pyproject.toml enforces the aggregate, not per-file."
    artifacts:
      - path: "src/mcp_canada/modules/nutrient_file/client.py"
        issue: "54% coverage (31/68 lines uncovered)"
      - path: "src/mcp_canada/modules/ckan/client.py"
        issue: "55% coverage (32/71 lines uncovered)"
      - path: "src/mcp_canada/modules/drug_database/client.py"
        issue: "74% coverage (12/47 lines uncovered)"
      - path: "src/mcp_canada/modules/open_parliament/client.py"
        issue: "82% coverage (16/88 lines uncovered)"
      - path: "src/mcp_canada/modules/recalls/client.py"
        issue: "82% coverage (8/44 lines uncovered)"
      - path: "src/mcp_canada/modules/open_parliament/tools.py"
        issue: "87% coverage (16/122 lines uncovered)"
    missing:
      - "Add tests for uncovered branches in nutrient_file/client.py (error paths, edge cases)"
      - "Add tests for uncovered branches in ckan/client.py"
      - "Add tests for uncovered branches in drug_database/client.py"
      - "Add tests for uncovered branches in open_parliament/client.py and tools.py"
      - "Add tests for uncovered branches in recalls/client.py"

  - truth: "CI checks that the auto-generated tool catalog (TOOLS.md and README catalog tables) is up to date"
    status: failed
    reason: "scripts/generate_catalog.py exists and works (--check passes locally), but the CI workflow (.github/workflows/ci.yml) has no step that runs 'generate_catalog.py --check'. The catalog can drift from source without CI catching it."
    artifacts:
      - path: ".github/workflows/ci.yml"
        issue: "No step running 'uv run python scripts/generate_catalog.py --check'"
    missing:
      - "Add CI step: 'uv run python scripts/generate_catalog.py --check' to .github/workflows/ci.yml"
---

# Phase 06: Distribution and Quality Verification Report

**Phase Goal:** Anyone can install and run mcp-canada with a single command, all modules have >95% test coverage with CI enforcing quality, semantic release auto-publishes to PyPI, and the README includes an auto-generated tool catalog
**Verified:** 2026-04-06T12:45:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Anyone can install and run with a single command (`uvx mcp-canada`) | VERIFIED | README Quick Start shows `uvx mcp-canada`; entry point `mcp-canada = "mcp_canada.server:main"` in pyproject.toml; `uv run mcp-canada --help` works |
| 2 | Package is installable from PyPI | VERIFIED | Build artifacts exist in `dist/`; release.yml publishes via `pypa/gh-action-pypi-publish@release/v1` on merge to main; `python-semantic-release` configured with `upload_to_vcs_release = true` |
| 3 | Semantic release auto-publishes to PyPI on merge to main | VERIFIED | `release.yml` triggers on `push: branches: main`; uses `python-semantic-release/python-semantic-release@v10.5.3`; publishes to PyPI when `released == 'true'`; `pyproject.toml` has complete `[tool.semantic_release]` config |
| 4 | README includes an auto-generated tool catalog | VERIFIED | `scripts/generate_catalog.py` generates TOOLS.md and injects catalog tables into README using `CATALOG:{module}:start/end` markers; `generate_catalog.py --check` confirms catalog is up to date |
| 5 | All modules have unit test suites | VERIFIED | All 7 modules (bank_of_canada, ckan, drug_database, nutrient_file, open_parliament, recalls, weather) have `__tests__/` directories with conftest.py, test_client.py, test_tools.py |
| 6 | CI enforces lint and type quality (ruff + pyright pass clean) | FAILED | CI workflow has `ruff check src/ tests/` and `pyright` steps, but currently 65 ruff errors and 8 pyright errors exist — both tools exit with code 1, CI would fail |
| 7 | All modules have >95% test coverage individually | FAILED | Aggregate is 96.27% (passes `fail_under=95`), but individual files: nutrient_file/client.py 54%, ckan/client.py 55%, drug_database/client.py 74%, open_parliament/client.py 82%, recalls/client.py 82% |
| 8 | CI enforces catalog freshness (auto-generated catalog checked in CI) | FAILED | `generate_catalog.py --check` exists and works, but there is no step in `.github/workflows/ci.yml` that runs it |

**Score:** 5/8 truths verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `pyproject.toml` | Package metadata, entry point, semantic release config | VERIFIED | Entry point `mcp-canada = "mcp_canada.server:main"` present; `[tool.semantic_release]` fully configured; `fail_under = 95` in coverage config |
| `src/mcp_canada/server.py` | `main()` entry point function | VERIFIED | `main()` at line 122 handles all transports; CLI args parsed correctly |
| `.github/workflows/release.yml` | Semantic release + PyPI publish pipeline | VERIFIED | Triggers on main; uses python-semantic-release v10.5.3; publishes via pypa/gh-action-pypi-publish |
| `.github/workflows/ci.yml` | CI with lint, type-check, and coverage | STUB | Has lint and type-check steps but they currently fail (65 ruff + 8 pyright errors); missing catalog freshness check |
| `scripts/generate_catalog.py` | Auto-generates TOOLS.md and updates README catalog tables | VERIFIED | 19.6KB script with `--check` mode; uses AST analysis; `generate_catalog.py --check` exits 0 ("Catalog is up to date") |
| `README.md` | Quick start + auto-generated tool catalog | VERIFIED | `uvx mcp-canada` quick start on line 24; 8 CATALOG: marker sections covering all 7 modules + meta; 422 lines total |
| `TOOLS.md` | Auto-generated full tool reference | VERIFIED | Header states "Auto-generated from source. Do not edit manually."; 84 tools across 8 modules |
| `CHANGELOG.md` | Semantic release changelog with insertion flag | VERIFIED | Contains `<!-- CHANGELOG -->` insertion flag matching `pyproject.toml` `insertion_flag` config |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `release.yml` | PyPI | `pypa/gh-action-pypi-publish@release/v1` | WIRED | Conditional on `steps.release.outputs.released == 'true'`; environment `pypi` configured |
| `release.yml` | `python-semantic-release` | `build_command = "uv build"` | WIRED | `pyproject.toml` sets `build_command = "uv build"`; matches `uv sync --locked --dev` in workflow |
| `pyproject.toml` `[tool.semantic_release]` | `src/mcp_canada/__init__.py` | `version_variables` | WIRED | `version_variables = ["src/mcp_canada/__init__.py:__version__"]`; `__version__ = "0.0.1"` present |
| `scripts/generate_catalog.py` | `README.md` | `CATALOG:{module}:start/end` markers | WIRED | Script injects tables between markers; all 8 module sections present; `--check` passes |
| `ci.yml` | coverage 95% threshold | `fail_under = 95` in pyproject.toml | WIRED | pytest-cov reads `[tool.coverage.report] fail_under = 95` automatically when `--cov` flag used |
| `ci.yml` | lint quality | `ruff check src/ tests/` | NOT_WIRED | Step exists but 65 errors cause exit code 1 — CI would fail every run |
| `ci.yml` | type quality | `pyright` | NOT_WIRED | Step exists but 8 errors cause exit code 1 — CI would fail every run |
| `ci.yml` | catalog freshness | `generate_catalog.py --check` | NOT_WIRED | No such step exists in ci.yml |

---

## Requirements Coverage

| Requirement | Description | Status | Evidence |
|-------------|-------------|--------|----------|
| DIST-01 | Single-command install and run | SATISFIED | `uvx mcp-canada` in README Quick Start; entry point registered in pyproject.toml; binary works |
| DIST-02 | Package published to PyPI | SATISFIED | release.yml with pypa/gh-action-pypi-publish; dist/ artifacts built; semantic release configured |
| DIST-03 | Semantic release auto-publishes | SATISFIED | python-semantic-release v10.5.3 in release.yml; full `[tool.semantic_release]` config in pyproject.toml |
| DIST-04 | README with auto-generated tool catalog | SATISFIED | generate_catalog.py generates TOOLS.md + injects README tables; catalog verified up-to-date |
| QA-01 | All modules >95% test coverage | BLOCKED | Aggregate 96.27% passes, but individual client files at 54-82% in multiple modules |
| QA-02 | CI enforces quality | BLOCKED | CI workflow exists but ruff (65 errors) and pyright (8 errors) both fail — CI cannot pass in current state |
| QA-03 | All modules have tests | SATISFIED | All 7 data modules + weather submodules have __tests__/ directories with test files |
| QA-05 | Catalog freshness enforced in CI | BLOCKED | generate_catalog.py --check works locally but is not a CI step — catalog can drift undetected |

---

## Anti-Patterns Found

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| `src/mcp_canada/modules/drug_database/tools.py:21` | `import httpx` unused (F401) | Warning | Ruff fails CI |
| `src/mcp_canada/modules/open_parliament/schemas.py:7` | `from typing import Any` unused (F401) | Warning | Ruff fails CI |
| `src/mcp_canada/modules/weather/current/tools.py:51` | f-string without placeholders (F541) | Warning | Ruff fails CI |
| `src/mcp_canada/modules/weather/climate/client.py:38` | Type error: object not assignable to ConvertibleToFloat | Blocker | Pyright fails CI; production code has type unsafety |
| `src/mcp_canada/modules/weather/hydro/__tests__/test_client.py:232-271` | 6x None-subscript/in-operator errors | Warning | Pyright fails CI (test files) |
| `src/mcp_canada/modules/ckan/__tests__/test_client.py:62` | endswith on Optional[str] | Warning | Pyright fails CI (test files) |
| Multiple `__tests__/conftest.py` files | Unused imports (pytest, json, AsyncMock, MagicMock, patch, call, importlib) | Warning | Ruff fails CI; 60 of 65 errors are in test/conftest files |

The single production type error (`weather/climate/client.py:38`) is a blocker — it indicates real type unsafety in production code that pyright correctly flags.

---

## Human Verification Required

### 1. PyPI Package Accessibility

**Test:** Install `mcp-canada` from PyPI: `pip install mcp-canada` or `uvx mcp-canada`
**Expected:** Package installs successfully and `mcp-canada --help` shows CLI help
**Why human:** Requires verifying actual PyPI publication occurred (automated checks can only confirm the workflow is wired, not that the package exists on PyPI at the published version)

### 2. Semantic Release Commit Parsing

**Test:** Make a conventional commit (`feat: add X` or `fix: resolve Y`) and push to a branch, then merge to main
**Expected:** semantic-release bumps version, creates GitHub release, publishes to PyPI
**Why human:** Cannot verify release pipeline behavior without an actual commit cycle and live GitHub Actions run

### 3. Claude Desktop Integration

**Test:** Add `{"command": "uvx", "args": ["mcp-canada"]}` to claude_desktop_config.json and restart Claude Desktop
**Expected:** mcp-canada appears as a connected MCP server with tools available
**Why human:** Requires a live Claude Desktop instance to verify the uvx single-command install works end-to-end for the user-facing scenario

---

## Gaps Summary

Three gaps block full goal achievement:

**Gap 1 — CI is broken (QA-02):** The CI workflow has the right structure (ruff, pyright, pytest with coverage) but the codebase has accumulated 65 ruff lint errors and 8 pyright type errors. Every push would fail CI. Most errors (60/65 ruff, 7/8 pyright) are in test and conftest files with unused imports and missing None guards. One production error exists in `weather/climate/client.py`. This is the highest-priority gap — a CI that always fails provides no quality enforcement.

**Gap 2 — Per-module coverage below 95% (QA-01):** The aggregate 96.27% masks severe under-testing in specific clients. `nutrient_file/client.py` (54%) and `ckan/client.py` (55%) have more than half their code untested. `drug_database`, `open_parliament`, and `recalls` clients are in the 74-82% range. The requirement says "all modules have >95% test coverage" — the aggregate threshold alone does not satisfy this. Error paths, edge cases, and alternative branches in these clients need test coverage.

**Gap 3 — Catalog staleness not enforced in CI (QA-05):** The `generate_catalog.py --check` tool works correctly and confirms the catalog is currently fresh. However, no CI step runs this check. Any future tool addition or docstring change that is not followed by `python scripts/generate_catalog.py` will silently produce a stale README without CI catching it. Adding a single CI step fixes this.

Root cause pattern: Gaps 1 and 3 share the same root cause — the CI workflow was structured correctly but not validated against the actual codebase state (lint errors in test files) and is missing one enforcement step.

---

_Verified: 2026-04-06T12:45:00Z_
_Verifier: Claude (gsd-verifier)_
