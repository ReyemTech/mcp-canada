# Phase 11: Shared File Parsers + IRCC Immigration - Context

**Gathered:** 2026-04-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Two deliverables: (1) a shared XLSX/CSV parser library in `shared/parsers.py` reusable by any module, and (2) an IRCC immigration module with pre-configured knowledge of all 10 actively-updated IRCC datasets plus key historical datasets. The parser is the foundation; the IRCC module is the first consumer.

</domain>

<decisions>
## Implementation Decisions

### Shared parser design
- **Dependencies:** `openpyxl` as base dependency; `pandas` as optional extra (`pip install mcp-canada[ircc]`)
- Parser uses pandas when available (better handling of multi-sheet, encoding, types), falls back to openpyxl + stdlib csv
- **Return type:** `list[dict]` — JSON-serializable, works with `ds_insert_data()`, consistent with all existing patterns
- **Caching:** Use existing `cached_fetch()` with 24hr TTL (IRCC files update monthly, 24hr is conservative)
- **Interface:** `async def fetch_and_parse(url: str, sheet: str | int = 0, skip_rows: int = 0) -> (list[dict], bool)`
- Handles XLSX, CSV, XLS (with xlrd if available, otherwise skip legacy)
- No disk cache — memory only via aiocache

### IRCC dataset selection
- **All 10 actively-updated datasets** included: PR, Study Permits, Work Permits (TFWP+IMP), Express Entry PRs, Express Entry Invited, TR-to-PR Transitions, Asylum Claimants, Operational Processing, Afghan Refugees, PR Cards
- **Key historical datasets** also included: Ad-hoc PR (1980-2023), Ad-hoc Study Permits (2004-2016), Ad-hoc Work Permits, Resettled Refugees (archived)
- **Excluded:** Facts & Figures HTML reports, Algorithmic Impact Assessments (PDF/JSON, not immigration data), Syrian Refugees family composition (static one-off)

### IRCC tool organization
- **One tool per dataset category** (not one per file): ~10-12 `ircc_` tools total
- Each tool accepts a `breakdown` parameter to select which file variant (e.g., `ircc_get_permanent_residents(breakdown="country")` vs `breakdown="province"`)
- Pre-configured dataset registry maps (dataset, breakdown, lang) → exact IRCC download URL
- Tools know which CKAN dataset ID each belongs to (for provenance in `_meta.source`)

### IRCC data presentation
- **Privacy masking:** `--` values converted to `null`/None. Clean for SQL, agents see null and know it's suppressed
- **Filtering:** Both modes — optional `year`, `country`, `province` filter params. No filters = full dataset
- **Bilingual:** `lang="en"` fetches `EN_ODP-*.xlsx`, `lang="fr"` fetches `FR_ODP-*.xlsx`. Consistent with all modules
- **Rounding:** IRCC rounds all values to nearest 5. Include a note in tool docstrings so agents know precision limits

### Claude's Discretion
- Exact dataset registry structure (dict of dicts, dataclass, etc.)
- How to handle multi-sheet workbooks (some IRCC files have multiple sheets — which to parse?)
- Column name normalization (snake_case? as-is from XLSX headers?)
- Whether to add an `ircc_list_datasets()` discovery tool in addition to the per-category tools
- How to split the phase into plans (parser first, then IRCC tools, or parallel)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `shared/cache.py`: `cached_fetch(key, ttl, fetcher)` — use for downloaded files with 24hr TTL
- `shared/rate_limiter.py`: May not be needed (IRCC files are static downloads, not an API)
- `shared/envelope.py`: `make_response()` / `make_error()` for all tools
- `datastore/client.py`: `create_table()`, `insert_rows()` — IRCC tools can store parsed data
- `statcan/client.py`: Pattern reference for how to build a module that fetches and flattens external data

### Established Patterns
- 5-file module pattern (constants, schemas, client, tools, __init__)
- `ircc_` prefix for all IRCC tools
- All tools accept `lang: Literal["en", "fr"]`
- Client functions return `(data, was_cached)` tuples
- Flat Pydantic schemas

### Integration Points
- `shared/parsers.py` — new shared utility (like cache.py, envelope.py)
- `modules/ircc/` — new module directory
- `modules/ircc/constants.py` — dataset registry mapping (dataset, breakdown, lang) → URL
- `pyproject.toml` — add `openpyxl` to dependencies, `pandas` to optional `[ircc]` extra

</code_context>

<specifics>
## Specific Ideas

- IRCC open data index: `https://search.open.canada.ca/opendata/?owner_org=cic` (62 records)
- Base download URL: `https://www.ircc.canada.ca/opendata-donneesouvertes/data/`
- All actively-updated files are XLSX format with EN/FR variants
- Historical/ad-hoc files may be XLS (legacy) or CSV
- IRCC data uses `--` for values 0-5 (privacy protection) and rounds all other values to nearest 5

</specifics>

<deferred>
## Deferred Ideas

- Generic CKAN resource parser tool (`ckan_parse_resource(resource_id)`) — powerful but scope creep for this phase. Note for future: shared/parsers.py would make this trivial to add later.
- IRCC data change detection (compare current vs cached XLSX to find new data) — monitoring feature, not core

</deferred>

---

*Phase: 11-ircc-immigration*
*Context gathered: 2026-04-08*
