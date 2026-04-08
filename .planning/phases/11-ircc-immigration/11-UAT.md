---
status: complete
phase: 11-ircc-immigration
source: [11-01-SUMMARY.md, 11-02-SUMMARY.md, 11-03-SUMMARY.md, 11-04-SUMMARY.md]
started: 2026-04-08T21:00:00Z
updated: 2026-04-08T22:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Query Permanent Residents — Nested Format
expected: Call `ircc_get_permanent_residents(breakdown="country", lang="en")`. Returns nested format with label at top level and `years` dict containing year > quarter > month hierarchy. Column names are clean (no col_ prefix, no unnamed_*).
result: pass

### 2. Filter by Country
expected: Call `ircc_get_permanent_residents(breakdown="country", filter="Afghanistan")`. Returns only Afghanistan's row. Other countries excluded.
result: pass

### 3. Recent Years Only
expected: Call `ircc_get_permanent_residents(breakdown="country", filter="India", recent=2)`. Returns India's data with only the 2 most recent years (2025, 2026).
result: pass

### 4. Specific Year
expected: Call `ircc_get_permanent_residents(breakdown="country", filter="China", year=2024)`. Returns China's data with only 2024 in the years dict.
result: pass

### 5. Work Permits with Filter
expected: Call `ircc_get_work_permits(permit_type="imp", breakdown="country", filter="India", recent=1)`. Returns IMP work permit data for India, most recent year only. Nested format.
result: pass

### 6. Express Entry with Filter
expected: Call `ircc_get_express_entry(stream="admissions", breakdown="gender", recent=2)`. Returns Express Entry admissions by gender for last 2 years. Nested format with label columns for the 2-label layout.
result: pass

### 7. Ops Data — No Year Param
expected: Call `ircc_get_ops(breakdown="pr_intake", recent=1)`. Returns operational processing data in nested format for most recent year only. No year param exists on this tool (monthly snapshots).
result: pass

### 8. French Language Variant
expected: Call `ircc_get_study_permits(breakdown="country", filter="Inde", lang="fr", recent=1)`. Returns French IRCC data for India (filtered by French name "Inde"), most recent year, nested format. `_meta.lang` is "fr".
result: pass

### 9. Ad-hoc PR English-Only Error
expected: Call `ircc_get_adhoc_pr(breakdown="category_1980", lang="fr")`. Returns `INVALID_INPUT` error explaining English-only. Does not crash.
result: pass

### 10. Full Test Suite Passes
expected: Run `uv run pytest --cov=src/mcp_canada --cov-fail-under=95`. All tests pass, coverage >= 95%.
result: pass

## Summary

total: 10
passed: 10
issues: 0
pending: 0
skipped: 0

## Gaps

[none]
