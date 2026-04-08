# Phase 11: Shared File Parsers + IRCC Immigration - Research

**Researched:** 2026-04-08
**Domain:** XLSX/CSV file parsing, IRCC open data, shared utility design
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Shared parser design:**
- Dependencies: `openpyxl` as base dependency; `pandas` as optional extra (`pip install mcp-canada[ircc]`)
- Parser uses pandas when available (better handling of multi-sheet, encoding, types), falls back to openpyxl + stdlib csv
- Return type: `list[dict]` — JSON-serializable, works with `ds_insert_data()`, consistent with all existing patterns
- Caching: Use existing `cached_fetch()` with 24hr TTL (IRCC files update monthly, 24hr is conservative)
- Interface: `async def fetch_and_parse(url: str, sheet: str | int = 0, skip_rows: int = 0) -> (list[dict], bool)`
- Handles XLSX, CSV, XLS (with xlrd if available, otherwise skip legacy)
- No disk cache — memory only via aiocache

**IRCC dataset selection:**
- All 10 actively-updated datasets included: PR, Study Permits, Work Permits (TFWP+IMP), Express Entry PRs, Express Entry Invited, TR-to-PR Transitions, Asylum Claimants, Operational Processing, Afghan Refugees, PR Cards
- Key historical datasets also included: Ad-hoc PR (1980-2023), Ad-hoc Study Permits (2004-2016), Ad-hoc Work Permits, Resettled Refugees (archived)
- Excluded: Facts & Figures HTML reports, Algorithmic Impact Assessments (PDF/JSON, not immigration data), Syrian Refugees family composition (static one-off)

**IRCC tool organization:**
- One tool per dataset category (not one per file): ~10-12 `ircc_` tools total
- Each tool accepts a `breakdown` parameter to select which file variant (e.g., `ircc_get_permanent_residents(breakdown="country")` vs `breakdown="province"`)
- Pre-configured dataset registry maps (dataset, breakdown, lang) -> exact IRCC download URL
- Tools know which CKAN dataset ID each belongs to (for provenance in `_meta.source`)

**IRCC data presentation:**
- Privacy masking: `--` values converted to `null`/None. Clean for SQL, agents see null and know it's suppressed
- Filtering: Both modes — optional `year`, `country`, `province` filter params. No filters = full dataset
- Bilingual: `lang="en"` fetches `EN_ODP-*.xlsx`, `lang="fr"` fetches `FR_ODP-*.xlsx`. Consistent with all modules
- Rounding: IRCC rounds all values to nearest 5. Include a note in tool docstrings so agents know precision limits

### Claude's Discretion
- Exact dataset registry structure (dict of dicts, dataclass, etc.)
- How to handle multi-sheet workbooks (some IRCC files have multiple sheets — which to parse?)
- Column name normalization (snake_case? as-is from XLSX headers?)
- Whether to add an `ircc_list_datasets()` discovery tool in addition to the per-category tools
- How to split the phase into plans (parser first, then IRCC tools, or parallel)

### Deferred Ideas (OUT OF SCOPE)
- Generic CKAN resource parser tool (`ckan_parse_resource(resource_id)`) — powerful but scope creep for this phase. Note for future: shared/parsers.py would make this trivial to add later.
- IRCC data change detection (compare current vs cached XLSX to find new data) — monitoring feature, not core
</user_constraints>

---

## Summary

Phase 11 delivers two tightly coupled artifacts: `shared/parsers.py` (a reusable async XLSX/CSV/XLS fetch-and-parse utility) and `modules/ircc/` (the first consumer, exposing 10+ actively-maintained IRCC immigration datasets as `ircc_` MCP tools).

The parser design is already well-specified: download file bytes via httpx, pass through BytesIO to openpyxl (or pandas if available), return `list[dict]` with header row as keys. The core technical challenge is building a pragmatic openpyxl fallback that handles the three real-world IRCC data complications: files with space-containing URLs (Operational Processing dataset), multi-sheet workbooks, and `--` privacy masking. The IRCC dataset registry in `constants.py` will be the most labor-intensive artifact — mapping ~120+ distinct (dataset, breakdown, lang) combinations to exact download URLs.

The planner should sequence this as: Plan A = shared parser (`shared/parsers.py` + pyproject.toml + unit tests), Plan B = IRCC module skeleton + constants registry, Plan C = IRCC tools + integration tests. Plans A and B have no mutual dependency; Plan C depends on both.

**Primary recommendation:** Use openpyxl `read_only=True` with BytesIO as the canonical fallback path. The `--` masking pass happens as a post-parse step over all dict values before returning. Column names should be normalized to snake_case to satisfy the datastore's `IDENTIFIER_RE` regex (`^[a-zA-Z_][a-zA-Z0-9_]{0,63}$`).

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| openpyxl | 3.1.x | Read XLSX/XLSM files from BytesIO | Project-approved; handles read-only mode, sheet selection, iter_rows |
| stdlib csv | stdlib | Parse CSV content from decoded bytes | Zero deps, handles comma-separated IRCC CSV variants |
| httpx | 0.27+ | Fetch binary XLSX/CSV bytes from IRCC URLs | Already a project dependency; `response.content` gives bytes |
| aiocache | 0.12+ | Cache parsed `list[dict]` by URL for 24hr TTL | Already used via `shared/cache.py`; avoids re-parsing |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pandas | 2.x (optional) | Better multi-sheet handling, auto type inference | When installed via `mcp-canada[ircc]` extra |
| xlrd | 2.x (optional) | Read legacy .xls files (IRCC ad-hoc datasets pre-2016) | Only for XLS files; xlrd 2.x cannot read XLSX |
| io.BytesIO | stdlib | Wrap fetched bytes for openpyxl in-memory parsing | Always needed; avoids temp file disk I/O |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| openpyxl | pandas-only | pandas adds 30MB+ to install size; openpyxl is lighter for simple row iteration |
| openpyxl | xlwings | xlwings requires Excel installation; not suitable for server environments |
| memory cache (aiocache) | disk cache | IRCC files are monthly; in-memory is fine; no filesystem state complexity |

**Installation:**
```bash
# Core (adds openpyxl to base dependencies in pyproject.toml)
uv add openpyxl

# Optional: for pandas-enhanced parsing
uv add --optional ircc pandas xlrd
```

---

## Architecture Patterns

### Recommended Project Structure
```
src/mcp_canada/
├── shared/
│   └── parsers.py          # NEW: fetch_and_parse(), _parse_xlsx(), _parse_csv(), _parse_xls()
├── modules/
│   └── ircc/
│       ├── __init__.py     # MODULE_NAME = "ircc", MODULE_DESCRIPTION
│       ├── constants.py    # DATASET_REGISTRY, BASE_URL, CACHE_TTL, RATE_GROUP, RATE_LIMIT
│       ├── schemas.py      # Flat Pydantic models for each dataset type (optional — registry may be enough)
│       ├── client.py       # fetch_permanent_residents(), fetch_study_permits(), etc.
│       ├── tools.py        # ircc_get_permanent_residents(), ircc_get_study_permits(), etc.
│       └── __tests__/
│           ├── __init__.py
│           ├── conftest.py      # Mock XLSX bytes fixtures
│           ├── test_client.py   # Test client functions with mocked fetch_and_parse
│           └── test_tools.py    # Test tool functions with mocked client
```

### Pattern 1: Shared Parser — fetch_and_parse()

**What:** An async function that downloads a file URL to bytes, detects format, parses to `list[dict]`, and caches the result.

**When to use:** Any module needing to consume tabular government file downloads (XLSX, CSV, XLS).

**Example:**
```python
# src/mcp_canada/shared/parsers.py
import csv
import io
from typing import Any

import httpx

from mcp_canada.shared.cache import cached_fetch


def _normalize_key(header: str) -> str:
    """Convert XLSX column header to snake_case safe for SQLite identifiers."""
    import re
    # Replace spaces/hyphens/slashes with underscores, strip leading digits
    key = re.sub(r'[^a-zA-Z0-9]', '_', str(header).strip())
    key = re.sub(r'_+', '_', key).strip('_').lower()
    if key and key[0].isdigit():
        key = f"col_{key}"
    return key or "col"


def _mask_privacy(value: Any) -> Any:
    """Convert IRCC '--' suppressed values to None."""
    if isinstance(value, str) and value.strip() == '--':
        return None
    return value


def _parse_xlsx(content: bytes, sheet: str | int = 0, skip_rows: int = 0) -> list[dict]:
    """Parse XLSX bytes to list[dict] using openpyxl read-only mode."""
    from io import BytesIO
    from openpyxl import load_workbook

    wb = load_workbook(BytesIO(content), read_only=True, data_only=True)
    try:
        if isinstance(sheet, int):
            ws = wb.worksheets[sheet]
        else:
            ws = wb[sheet]

        rows = list(ws.iter_rows(values_only=True))
    finally:
        wb.close()

    if not rows:
        return []

    # Skip metadata rows before header
    rows = rows[skip_rows:]
    if not rows:
        return []

    headers = [_normalize_key(h) if h is not None else f"col_{i}"
               for i, h in enumerate(rows[0])]

    result = []
    for row in rows[1:]:
        d = {headers[i]: _mask_privacy(v) for i, v in enumerate(row) if i < len(headers)}
        result.append(d)
    return result


def _parse_csv(content: bytes, skip_rows: int = 0) -> list[dict]:
    """Parse CSV bytes to list[dict] using stdlib csv."""
    text = content.decode('utf-8-sig', errors='replace')  # Handle BOM
    reader = csv.DictReader(text.splitlines())
    rows = list(reader)
    rows = rows[skip_rows:]
    return [{_normalize_key(k): _mask_privacy(v) for k, v in row.items()} for row in rows]


async def fetch_and_parse(
    url: str,
    sheet: str | int = 0,
    skip_rows: int = 0,
    ttl: int = 86400,
) -> tuple[list[dict], bool]:
    """Fetch a file URL and parse it to list[dict]. Caches for ttl seconds.

    Args:
        url: Direct download URL (XLSX, CSV, or XLS).
        sheet: Sheet name or 0-based index for XLSX (ignored for CSV).
        skip_rows: Number of rows to skip before the header row.
        ttl: Cache TTL in seconds (default 24hr for monthly IRCC files).

    Returns:
        (rows, was_cached) tuple following project convention.
    """
    cache_key = f"parser:{url}:{sheet}:{skip_rows}"

    async def _fetch() -> list[dict]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            content = resp.content

        lower_url = url.lower().split('?')[0]
        if lower_url.endswith('.csv'):
            return _parse_csv(content, skip_rows)
        elif lower_url.endswith('.xls'):
            return _parse_xls(content, sheet, skip_rows)
        else:  # .xlsx or unknown — try openpyxl
            return _parse_xlsx(content, sheet, skip_rows)

    return await cached_fetch(cache_key, ttl, _fetch)
```

### Pattern 2: IRCC Dataset Registry (constants.py)

**What:** A nested dict mapping dataset category + breakdown + lang to an exact IRCC download URL.

**When to use:** The single source of truth for all IRCC file locations. Client functions look up URLs from this registry.

**Example:**
```python
# src/mcp_canada/modules/ircc/constants.py

BASE_URL = "https://www.ircc.canada.ca/opendata-donneesouvertes/data/"
CACHE_TTL = 86400  # 24 hours — IRCC files update monthly
RATE_GROUP = "ircc"
RATE_LIMIT = 2.0   # Static file server — be conservative

# CKAN dataset IDs for provenance
CKAN_ID_PR = "f7e5498e-0ad8-4417-85c9-9b8aff9b9eda"
CKAN_ID_STUDY = "90115b00-f9b8-49e8-afa3-b4cff8facaee"
# ... etc.

# Registry: (dataset_key, breakdown_key, lang) -> filename
# Access: DATASET_REGISTRY["pr"]["country"]["en"] -> full URL
DATASET_REGISTRY: dict[str, dict[str, dict[str, str]]] = {
    "pr": {
        "country": {
            "en": BASE_URL + "EN_ODP-PR-Citz.xlsx",
            "fr": BASE_URL + "FR_ODP-PR-Citz.xlsx",
        },
        "province": {
            "en": BASE_URL + "EN_ODP-PR-ProvImmCat.xlsx",
            "fr": BASE_URL + "FR_ODP-PR-ProvImmCat.xlsx",
        },
        "gender": {
            "en": BASE_URL + "EN_ODP-PR-Gender.xlsx",
            "fr": BASE_URL + "FR_ODP-PR-Gender.xlsx",
        },
        # ... more breakdowns
    },
    # ... more dataset categories
}
```

### Pattern 3: IRCC Client Function

**What:** One async function per IRCC dataset category. Looks up URL from registry, calls `fetch_and_parse()`.

**When to use:** Tool functions delegate to these; they are unit-testable by mocking `fetch_and_parse`.

**Example:**
```python
# src/mcp_canada/modules/ircc/client.py
from mcp_canada.modules.ircc.constants import DATASET_REGISTRY
from mcp_canada.shared.parsers import fetch_and_parse


async def fetch_permanent_residents(
    breakdown: str = "country",
    lang: str = "en",
) -> tuple[list[dict], bool]:
    """Fetch and parse IRCC permanent residents data for the given breakdown."""
    try:
        url = DATASET_REGISTRY["pr"][breakdown][lang]
    except KeyError:
        valid = sorted(DATASET_REGISTRY["pr"].keys())
        raise ValueError(f"Unknown breakdown {breakdown!r}. Valid: {valid}")

    return await fetch_and_parse(url)
```

### Pattern 4: IRCC Tool Function

**What:** Standard `@tool` function with `breakdown` + `lang` params, optional filter params.

**Example:**
```python
@tool
async def ircc_get_permanent_residents(
    breakdown: Literal["country", "province", "gender", "age", "cma", "noc", "country_category"] = "country",
    year: int | None = None,
    lang: Literal["en", "fr"] = "en",
) -> dict:
    """Get IRCC permanent resident admissions data by breakdown dimension.

    Note: Values between 0–5 are suppressed (shown as null) and all other
    values are rounded to the nearest multiple of 5 for privacy protection.
    Use for: permanent residents, immigration admissions, PR by country,
    province, gender, age, occupation NOC, IRCC immigration statistics.
    Keywords: permanent residents, PR, immigration, admissions, country,
    province, territory, gender, age, category, IRCC, Canada, citizenship.
    """
    try:
        rows, cached = await fetch_permanent_residents(breakdown=breakdown, lang=lang)
    except ValueError as exc:
        return make_error("INVALID_INPUT", str(exc), lang=lang)
    except httpx.HTTPStatusError as exc:
        return make_error("UPSTREAM_ERROR",
            f"IRCC returned HTTP {exc.response.status_code}.", lang=lang)

    if year is not None:
        rows = [r for r in rows if str(r.get("year", r.get("année", ""))) == str(year)]

    return make_response(
        rows,
        api_name="IRCC Open Data",
        api_url=DATASET_REGISTRY["pr"][breakdown][lang],
        cached=cached,
        lang=lang,
    )
```

### Anti-Patterns to Avoid

- **Fetching binary content with `api_get()`:** The shared `api_get()` calls `.json()` on the response. For XLSX/CSV fetching, use `httpx.AsyncClient` directly and read `.content` (bytes).
- **Passing full dataset rows unfiltered into `_meta`:** The `_meta` envelope goes to agents. Keep it slim — only the data slice requested.
- **Non-normalized column keys:** IRCC XLSX headers like "Country of Citizenship" will fail `IDENTIFIER_RE` validation in `insert_rows()`. Always run `_normalize_key()` before returning.
- **Treating `--` as a string value:** Agents and SQL queries expect `null`, not the string `"--"`. Mask at parse time, not at query time.
- **Using `openpyxl.load_workbook()` without `read_only=True`:** IRCC XLSX files can be multi-MB. Read-only mode uses far less memory.
- **Caching per-filter results:** Cache the full parsed file (all rows); apply year/country/province filters in the tool layer. Re-parsing per filter combo wastes memory.
- **Space-containing URLs without URL encoding:** The Operational Processing dataset filenames contain spaces (e.g., `"Open Data - OPS PR Intake en.xlsx"`). httpx handles this correctly with `client.get(url)` — do not manually replace spaces with `%20` as it will double-encode.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| XLSX row iteration | Custom XML parser | openpyxl `iter_rows(values_only=True)` | XLSX is a ZIP of XML; openpyxl handles all the format complexity |
| CSV encoding detection | charset-normalizer | `content.decode('utf-8-sig', errors='replace')` | IRCC CSVs may have BOM; utf-8-sig strips it automatically |
| Column header to snake_case | Custom regex | `re.sub(r'[^a-zA-Z0-9]', '_', header)` pattern | Simple and sufficient for IRCC header patterns |
| Privacy mask detection | Regex scan | Exact string comparison `value.strip() == '--'` | IRCC uses exactly `--`, not ranges or other markers |
| File format detection | MIME type parsing | URL suffix check (`.xlsx`, `.csv`, `.xls`) | IRCC URLs always have explicit suffixes |
| Async file fetching with caching | Custom cache layer | `cached_fetch()` from `shared/cache.py` | Already built, 24hr TTL, aiocache backend |

**Key insight:** The parse logic itself is ~40 lines. The real work in this phase is the dataset registry (120+ URL mappings) and the tool docstrings with correct BM25 keywords.

---

## Common Pitfalls

### Pitfall 1: openpyxl read_only mode and iter_cols()

**What goes wrong:** `ws.iter_cols()` is not available in `read_only=True` mode. Code that tries to extract column names via `iter_cols()` will raise `NotImplementedError`.

**Why it happens:** Read-only mode streams rows; column-based access requires full load.

**How to avoid:** Always extract headers from the first row via `next(ws.iter_rows(values_only=True))` or `list(ws.iter_rows(values_only=True))[0]`.

**Warning signs:** `AttributeError: 'ReadOnlyWorksheet' object has no attribute 'iter_cols'`

### Pitfall 2: openpyxl workbook must be explicitly closed

**What goes wrong:** Not calling `wb.close()` after reading a read-only workbook leaks file handles.

**Why it happens:** Read-only mode uses lazy loading via ZipFile streams; they're not closed by GC reliably.

**How to avoid:** Always use try/finally: `try: ... finally: wb.close()`. Do not use context manager (`with load_workbook(...)`) — openpyxl workbooks do not support the context manager protocol in all versions.

**Warning signs:** ResourceWarning about unclosed files in tests.

### Pitfall 3: Multi-sheet IRCC workbooks — wrong sheet selected

**What goes wrong:** Some IRCC Operational Processing files contain multiple sheets (e.g., one per application type). `sheet=0` returns only the first sheet, which may be a summary or README tab.

**Why it happens:** IRCC uses multi-sheet workbooks for related data in one file.

**How to avoid:** Inspect files before coding. For known multi-sheet files, the `skip_rows` and `sheet` parameters in `fetch_and_parse()` let callers specify the exact sheet. The registry entry can document which sheet contains data rows.

**Warning signs:** Parsed rows contain metadata text, not tabular data. Headers look like "This file contains...".

### Pitfall 4: Spaces in Operational Processing filenames

**What goes wrong:** The Operational Processing dataset uses URLs with literal spaces: `"Open Data - OPS PR Intake en.xlsx"`. These URLs must be percent-encoded or passed raw to httpx.

**Why it happens:** IRCC used legacy filename conventions for this dataset.

**How to avoid:** httpx automatically percent-encodes URLs passed as strings to `.get()`. Store the raw URL in the registry (with spaces). Do NOT pre-encode to `%20` — that would double-encode.

**Warning signs:** HTTP 404 on Operational Processing URLs despite correct filenames.

### Pitfall 5: Column name collisions after normalization

**What goes wrong:** Two different XLSX column headers normalize to the same snake_case key (e.g., "Year" and "Year " both become `year`). The latter overwrites the former in the dict.

**Why it happens:** IRCC files occasionally have trailing spaces in headers.

**How to avoid:** In `_normalize_key()`, deduplicate by appending `_2`, `_3` etc. if a key already exists in headers. Alternatively, strip headers before normalization: `str(header).strip()`.

**Warning signs:** Fewer columns than expected in parsed output.

### Pitfall 6: aiocache caches empty list on fetch failure

**What goes wrong:** If `httpx` raises before returning content and the exception is caught incorrectly, an empty `list` could be cached under the URL key for 24hr.

**Why it happens:** `cached_fetch()` stores whatever the `fetcher()` callable returns. If the fetcher catches exceptions and returns `[]`, that empty list is cached.

**How to avoid:** Let exceptions propagate out of the fetcher. Only catch at the tool layer with `make_error()`. Never return `[]` on error from a client function.

**Warning signs:** Tool returns empty data and caches persist until TTL expires.

### Pitfall 7: IRCC column headers differ between EN and FR files

**What goes wrong:** English XLSX files use English headers (`"Country of Citizenship"`) and French files use French headers (`"Pays de citoyenneté"`). After normalization, the dict keys differ between languages.

**Why it happens:** IRCC provides fully bilingual workbooks — even the column headers change.

**How to avoid:** This is expected behavior. Document it in tool docstrings. Tools should not attempt to merge EN and FR rows into a single schema. Each lang fetch returns its own key set. For datastore storage, always use one language (default `lang="en"`) to keep column names consistent.

**Warning signs:** SQL JOIN across ircc_ tables with `lang="fr"` data fails due to different column names.

---

## Code Examples

### Verified Pattern: openpyxl BytesIO read-only (confirmed via openpyxl 3.1 docs + WebSearch)

```python
from io import BytesIO
from openpyxl import load_workbook

# content: bytes from httpx response.content
wb = load_workbook(BytesIO(content), read_only=True, data_only=True)
try:
    ws = wb.worksheets[0]  # or wb["Sheet Name"]
    rows = list(ws.iter_rows(values_only=True))
finally:
    wb.close()

# rows[0] = header tuple, rows[1:] = data tuples
headers = [str(h).strip() if h is not None else f"col_{i}"
           for i, h in enumerate(rows[0])]
data = [dict(zip(headers, row)) for row in rows[1:]]
```

### Verified Pattern: CSV with BOM handling (stdlib)

```python
import csv

# content: bytes from httpx response.content
text = content.decode('utf-8-sig', errors='replace')  # utf-8-sig strips BOM
reader = csv.DictReader(text.splitlines())
rows = list(reader)  # Each row is already a dict keyed by header
```

### Verified Pattern: Privacy masking pass

```python
def _mask_privacy(value):
    """IRCC suppresses values 0-5 as '--'. Convert to None."""
    if isinstance(value, str) and value.strip() == '--':
        return None
    return value

# Apply during row construction:
masked_row = {k: _mask_privacy(v) for k, v in row.items()}
```

### Verified Pattern: Optional pandas fallback

```python
def _parse_xlsx_pandas(content: bytes, sheet: str | int = 0, skip_rows: int = 0) -> list[dict]:
    import pandas as pd
    from io import BytesIO
    df = pd.read_excel(BytesIO(content), sheet_name=sheet, skiprows=skip_rows)
    df = df.fillna(value=pd.NA)
    rows = df.to_dict(orient='records')
    # Apply privacy masking and key normalization
    return [{_normalize_key(k): _mask_privacy(v) for k, v in r.items()} for r in rows]
```

---

## IRCC Dataset Registry — Complete URL Map

This section documents all confirmed download URLs to be hardcoded in `constants.py`. Verified against Open Government Portal (open.canada.ca) on 2026-04-08.

### Permanent Residents (CKAN: f7e5498e-0ad8-4417-85c9-9b8aff9b9eda)

| Breakdown Key | EN URL | FR URL |
|---------------|--------|--------|
| `country` | `EN_ODP-PR-Citz.xlsx` | `FR_ODP-PR-Citz.xlsx` |
| `province` | `EN_ODP-PR-ProvImmCat.xlsx` | `FR_ODP-PR-ProvImmCat.xlsx` |
| `gender` | `EN_ODP-PR-Gender.xlsx` | `FR_ODP-PR-Gender.xlsx` |
| `age` | `EN_ODP-PR-AgeGroup.xlsx` | `FR_ODP-PR-AgeGroup.xlsx` |
| `cma` | `EN_ODP-PR-CMA.xlsx` | `FR_ODP-PR-CMA.xlsx` |
| `noc` | `EN_ODP-PR-ProvNOC4.xlsx` | `FR_ODP-PR-ProvNOC4.xlsx` |
| `country_category` | `EN_ODP-PR-CitzImmCat.xlsx` | `FR_ODP-PR-CitzImmCat.xlsx` |
| `csd` | `EN_ODP-PR-CSD.xlsx` | `FR_ODP-PR-CSD.xlsx` |
| `adoptions` | `EN_ODP-PR-AdoptionsCOBGender.xlsx` | `FR_ODP-PR-AdoptionsCOBGender.xlsx` |

All prefixed with `https://www.ircc.canada.ca/opendata-donneesouvertes/data/`

### Study Permits (CKAN: 90115b00-f9b8-49e8-afa3-b4cff8facaee)

| Breakdown Key | EN URL | FR URL |
|---------------|--------|--------|
| `country` | `EN_ODP-TR-Study-IS_CITZ_sign_date.xlsx` | `FR_ODP-TR-Study-IS_CITZ_sign_date.xlsx` |
| `province_level` | `EN_ODP-TR-Study-IS_PT_study_level_sign.xlsx` | `FR_ODP-TR-Study-IS_PT_study_level_sign.xlsx` |
| `gender` | `EN_ODP-TR-Study-IS_PT_gender_sign.xlsx` | `FR_ODP-TR-Study-IS_PT_gender_sign.xlsx` |
| `annual_country` | `EN_ODP_annual-TR-Study-IS_CITZ_year_end.xlsx` | `FR_ODP_annual-TR-Study-IS_CITZ_year_end.xlsx` |
| `annual_province` | `EN_ODP_annual-TR-Study-IS_PT_study_level_year_end.xlsx` | `FR_ODP_annual-TR-Study-IS_PT_study_level_year_end.xlsx` |

### Work Permits — IMP (CKAN: 360024f2-17e9-4558-bfc1-3616485d65b9)

| Breakdown Key | EN URL | FR URL |
|---------------|--------|--------|
| `province_program` | `EN_ODP-TR-Work-IMP_PT_program_sign.xlsx` | `FR_ODP-TR-Work-IMP_PT_program_sign.xlsx` |
| `gender_skill` | `EN_ODP-TR-Work-IMP_gender_skill.xlsx` | `FR_ODP-TR-Work-IMP_gender_skill.xlsx` |
| `country` | `EN_ODP-TR-Work-IMP CITZ.xlsx` | `FR_ODP-TR-Work-IMP CITZ.xlsx` |
| `noc` | `EN_ODP-TR-Work-IMP_PT_NOC4.xlsx` | `FR_ODP-TR-Work-IMP_PT_NOC4.xlsx` |

### Work Permits — TFWP (CKAN: 360024f2-17e9-4558-bfc1-3616485d65b9)

| Breakdown Key | EN URL | FR URL |
|---------------|--------|--------|
| `province_program` | `EN_ODP-TR-Work-TFWP_PT_program_sign.xlsx` | `FR_ODP-TR-Work-TFWP_PT_program_sign.xlsx` |
| `country` | `EN_ODP-TR-Work-TFWP CITZ.xlsx` | `FR_ODP-TR-Work-TFWP CITZ.xlsx` |
| `gender_skill` | `EN_ODP-TR-Work-TFWP_gender_skill_sign.xlsx` | `FR_ODP-TR-Work-TFWP_gender_skill_sign.xlsx` |
| `noc` | `EN_ODP-TR-Work-TFWP_PT_NOC4_sign.xlsx` | `FR_ODP-TR-Work-TFWP_PT_NOC4_sign.xlsx` |

### Express Entry — Admissions (CKAN: 52e4b14b-597a-4ecf-a184-23a6e69b0d57)

| Breakdown Key | EN URL | FR URL |
|---------------|--------|--------|
| `gender` | `EN_ODP-EE_Admissions-Gender.xlsx` | `FR_ODP-EE_Admissions-Gender.xlsx` |
| `category` | `EN_ODP-EE_Admissions-ImmCat.xlsx` | `FR_ODP-EE_Admissions-ImmCat.xlsx` |
| `country` | `EN_ODP-EE_Admissions-CITZ.xlsx` | `FR_ODP-EE_Admissions-CITZ.xlsx` |
| `age` | `EN_ODP-EE_Admissions-AgeGroup.xlsx` | `FR_ODP-EE_Admissions-AgeGroup.xlsx` |
| `occupation` | `EN_ODP-EE_Admissions-Occ.xlsx` | `FR_ODP-EE_Admissions-Occ.xlsx` |

### Express Entry — Invited Candidates (CKAN: 593e9165-c6ce-4f9b-b519-03d315f92cd4)

| Breakdown Key | EN URL | FR URL |
|---------------|--------|--------|
| `destination` | `EN_ODP-EE_Candidates-IntDest.xlsx` | `FR_ODP-EE_Candidates-IntDest.xlsx` |
| `score` | `EN_ODP-EE_Candidates-ITAScore.xlsx` | `FR_ODP-EE_Candidates-ITAScore.xlsx` |
| `country` | `EN_ODP-EE_Candidates-CITZ.xlsx` | `FR_ODP-EE_Candidates-CITZ.xlsx` |
| `age` | `EN_ODP-EE_Candidates-AgeGroup.xlsx` | `FR_ODP-EE_Candidates-AgeGroup.xlsx` |
| `education` | `EN_ODP-EE_Candidates-FrnEduLevel.xlsx` | `FR_ODP-EE_Candidates-FrnEduLevel.xlsx` |

### TR-to-PR Transitions (CKAN: 1b026aab-edb3-4d5d-8231-270a09ed4e82)

| Breakdown Key | EN URL | FR URL |
|---------------|--------|--------|
| `study_permit` | `EN_ODP-TR_to_PR-IS_PT_immcat.xlsx` | `FR_ODP-TR_to_PR-IS_PT_immcat.xlsx` |
| `imp` | `EN_ODP-TR_to_PR-IMP_PT_immcat.xlsx` | `FR_ODP-TR_to_PR-IMP_PT_immcat.xlsx` |
| `tfwp` | `EN_ODP-TR_to_PR-TFWP_PT_immcat.xlsx` | `FR_ODP-TR_to_PR-TFWP_PT_immcat.xlsx` |
| `pgwp` | `EN_ODP-TR_to_PR-PGWP_PT_immcat.xlsx` | `FR_ODP-TR_to_PR-PGWP_PT_immcat.xlsx` |

### Asylum Claimants (CKAN: b6cbcf4d-f763-4924-a2fb-8cc4a06e3de4)

| Breakdown Key | EN URL | FR URL |
|---------------|--------|--------|
| `province_office` | `EN_ODP-Asylum-OfficeType_Prov.xlsx` | `FR_ODP-Asylum-OfficeType_Prov.xlsx` |
| `province_age` | `EN_ODP-Asylum-PT_Age.xlsx` | `FR_ODP-Asylum-PT_Age.xlsx` |
| `province_gender` | `EN_ODP-Asylum-PT_Gender.xlsx` | `FR_ODP-Asylum-PT_Gender.xlsx` |

### Operational Processing (CKAN: 9b34e712-513f-44e9-babf-9df4f7256550)

Note: These filenames contain literal spaces. httpx handles them correctly.

| Breakdown Key | EN URL | FR URL |
|---------------|--------|--------|
| `pr_intake` | `Open Data - OPS PR Intake en.xlsx` | `Open Data - OPS PR Intake fr.xlsx` |
| `copr_issued` | `Open Data - OPS COPR Issued en.xlsx` | `Open Data - OPS COPR Issued fr.xlsx` |
| `study_processed` | `Open Data - OPS SP Processed en.xlsx` | `Open Data - OPS SP Processed fr.xlsx` |
| `tr_processed` | `Open Data - OPS TR Processed en.xlsx` | `Open Data - OPS TR Processed fr.xlsx` |
| `trv_intake` | `Open Data - OPS TRV Intake en.xlsx` | `Open Data - OPS TRV Intake fr.xlsx` |
| `tr_approved` | `Open Data - OPS TR Approved en.xlsx` | `Open Data - OPS TR Approved fr.xlsx` |

### Afghan Refugees (CKAN: 53520aa7-f2a3-4593-952e-574432a4acd0)

| Breakdown Key | EN URL | FR URL |
|---------------|--------|--------|
| `gender` | `EN_ODP-Afghan-Gender.xlsx` | `FR_ODP-Afghan-Gender.xlsx` |
| `age` | `EN_ODP-Afghan-AgeGroup.xlsx` | `FR_ODP-Afghan-AgeGroup.xlsx` |
| `education` | `EN_ODP-Afghan-Edu.xlsx` | `FR_ODP-Afghan-Edu.xlsx` |
| `language` | `EN_ODP-Afghan-OL.xlsx` | `FR_ODP-Afghan-OL.xlsx` |

### Ad-hoc PR (CKAN: ad975a26-df23-456a-8ada-756191a23695) — Historical, XLS format

| Breakdown Key | URL |
|---------------|-----|
| `category_1980` | `IRCC_PRadmiss_0002_E.xls` |
| `country_1980` | `IRCC_PRadmiss_0004_E.xls` |
| `province_cat_2000` | `IRCC_PRadmiss_0007_E.xls` |
| `province_citz_2000` | `IRCC_PRadmiss_0008_E.xls` |

Note: Ad-hoc XLS files are English-only and require xlrd (optional) or a note that XLS is unsupported.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| xlrd for all Excel files | xlrd for XLS only; openpyxl for XLSX | xlrd 2.0 (2020) | xlrd 2.x intentionally dropped XLSX support; must use openpyxl for .xlsx |
| pandas as only option | openpyxl as base, pandas optional | 2022+ | openpyxl is lighter; pandas is heavy for simple row iteration |
| Disk temp files for XLSX parsing | BytesIO in-memory | Always best practice | Avoids filesystem I/O in server environments |

**Deprecated/outdated:**
- xlrd >= 2.0 for XLSX: Raises explicit error. Only use xlrd for `.xls` legacy files.
- `wb.active` for multi-sheet workbooks: Only safe for single-sheet files. Use `wb.worksheets[0]` or `wb[sheet_name]`.

---

## Open Questions

1. **Which sheet index contains data in Operational Processing multi-sheet files?**
   - What we know: Operational Processing XLSX files likely have multiple sheets (different application types)
   - What's unclear: Whether sheet 0 is a data sheet or a metadata/README tab
   - Recommendation: Default `sheet=0` with the ability to override via registry. The planner should note that Operational Processing tool tasks should verify sheet selection against a live file download.

2. **Are PR Cards and Resettled Refugees datasets in scope?**
   - What we know: CONTEXT.md mentions them in the selected list but no URLs were researched
   - What's unclear: Current URL format — they may have been discontinued or merged
   - Recommendation: Add a Wave 0 task to confirm these datasets exist and are downloadable before implementing tools for them.

3. **Column name stability across IRCC updates**
   - What we know: IRCC updates files monthly and has been known to rename columns
   - What's unclear: How frequently headers change
   - Recommendation: Do not hardcode column names in tool schemas. Parse dynamically at runtime and let the `_normalize_key()` function handle variations.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x + pytest-asyncio (asyncio_mode = "auto") |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| Quick run command | `uv run pytest src/mcp_canada/shared/__tests__/ src/mcp_canada/modules/ircc/__tests__/ -x -v` |
| Full suite command | `uv run pytest --cov=src/mcp_canada --cov-fail-under=95` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| IRCC-01 | Shared parser fetches and parses XLSX bytes to list[dict] | unit | `uv run pytest src/mcp_canada/shared/__tests__/test_parsers.py -x` | Wave 0 |
| IRCC-02 | Shared parser handles CSV bytes correctly | unit | `uv run pytest src/mcp_canada/shared/__tests__/test_parsers.py -x` | Wave 0 |
| IRCC-03 | Privacy masking converts `--` to None | unit | `uv run pytest src/mcp_canada/shared/__tests__/test_parsers.py -x` | Wave 0 |
| IRCC-04 | ircc_get_permanent_residents returns rows with _meta envelope | unit | `uv run pytest src/mcp_canada/modules/ircc/__tests__/test_tools.py -x` | Wave 0 |
| IRCC-05 | ircc_get_study_permits returns rows for valid breakdown | unit | `uv run pytest src/mcp_canada/modules/ircc/__tests__/test_tools.py -x` | Wave 0 |
| IRCC-06 | All ircc_ tools return INVALID_INPUT for unknown breakdown | unit | `uv run pytest src/mcp_canada/modules/ircc/__tests__/test_tools.py -x` | Wave 0 |
| IRCC-07 | ircc_get_permanent_residents live data via MCP Client | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestIrccScenarios -v -m integration` | Wave 0 |
| IRCC-08 | discover_tools finds ircc_ tools via BM25 keywords | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestIrccScenarios::test_discover_ircc_tools -v -m integration` | Wave 0 |
| IRCC-09 | Parsed IRCC data can be stored to shared datastore | integration | `uv run pytest tests/integration/test_tool_scenarios.py::TestIrccScenarios::test_store_pr_data_to_datastore -v -m integration` | Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest src/mcp_canada/shared/__tests__/ src/mcp_canada/modules/ircc/__tests__/ -x`
- **Per wave merge:** `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `src/mcp_canada/shared/__tests__/test_parsers.py` — unit tests for `fetch_and_parse()`, `_parse_xlsx()`, `_parse_csv()`, `_mask_privacy()`
- [ ] `src/mcp_canada/modules/ircc/__tests__/__init__.py` — empty init
- [ ] `src/mcp_canada/modules/ircc/__tests__/conftest.py` — sample XLSX bytes fixtures (minimal synthetic workbook via openpyxl)
- [ ] `src/mcp_canada/modules/ircc/__tests__/test_client.py` — client function tests with mocked `fetch_and_parse`
- [ ] `src/mcp_canada/modules/ircc/__tests__/test_tools.py` — tool tests with mocked client functions
- [ ] `tests/integration/test_tool_scenarios.py::TestIrccScenarios` — integration tests class (append to existing file)
- [ ] Framework install: `uv add openpyxl` — add to base dependencies in `pyproject.toml`

---

## Sources

### Primary (HIGH confidence)
- Open Government Portal — IRCC datasets (2026-04-08): exact resource URLs verified for PR, Study Permits, Work Permits (TFWP+IMP), Express Entry Admissions, Express Entry Invited, TR-to-PR Transitions, Asylum Claimants, Afghan Refugees, Operational Processing, Ad-hoc PR
  - https://open.canada.ca/data/en/dataset/f7e5498e-0ad8-4417-85c9-9b8aff9b9eda
  - https://open.canada.ca/data/en/dataset/90115b00-f9b8-49e8-afa3-b4cff8facaee
  - https://open.canada.ca/data/en/dataset/360024f2-17e9-4558-bfc1-3616485d65b9
  - https://open.canada.ca/data/en/dataset/52e4b14b-597a-4ecf-a184-23a6e69b0d57
  - https://open.canada.ca/data/en/dataset/593e9165-c6ce-4f9b-b519-03d315f92cd4
  - https://open.canada.ca/data/en/dataset/1b026aab-edb3-4d5d-8231-270a09ed4e82
  - https://open.canada.ca/data/en/dataset/b6cbcf4d-f763-4924-a2fb-8cc4a06e3de4
  - https://open.canada.ca/data/en/dataset/9b34e712-513f-44e9-babf-9df4f7256550
  - https://open.canada.ca/data/en/dataset/53520aa7-f2a3-4593-952e-574432a4acd0
  - https://open.canada.ca/data/en/dataset/ad975a26-df23-456a-8ada-756191a23695
- openpyxl docs (WebSearch, multiple sources, cross-verified): `read_only=True` + BytesIO + `iter_rows(values_only=True)` + explicit `wb.close()` pattern

### Secondary (MEDIUM confidence)
- WebSearch results (multiple openpyxl tutorial sources): `load_workbook(BytesIO(content), read_only=True)` confirmed by 4+ independent sources including openpyxl RTD
- xlrd 2.x XLSX exclusion: confirmed by xlrd release notes (xlrd intentionally removed XLSX support in 2.0)

### Tertiary (LOW confidence)
- IRCC Operational Processing multi-sheet structure: inferred from dataset description; actual sheet names not verified without downloading a file
- PR Cards and Resettled Refugees URLs: not fetched — open questions flagged above

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — openpyxl and stdlib csv are verified; BytesIO + read_only pattern confirmed by multiple sources
- IRCC dataset registry: HIGH — all 10 primary dataset URLs verified directly from Open Government Portal on 2026-04-08
- Architecture: HIGH — follows identical patterns to existing ckan/, statcan/, datastore/ modules
- Pitfalls: MEDIUM — openpyxl read-only limitations confirmed; multi-sheet behavior inferred from IRCC dataset descriptions
- Operational Processing filenames: HIGH — confirmed spaces in filenames from live portal

**Research date:** 2026-04-08
**Valid until:** 2026-05-08 (IRCC updates monthly — URLs stable but filenames could change at next dataset release)
