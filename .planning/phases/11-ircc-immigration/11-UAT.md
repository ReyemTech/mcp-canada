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
result: issue
reported: "2-label layout (gender + province) has forward-fill bug: label_2 carries last province into summary/total rows and next gender section. Also missing hierarchical nesting (gender > province > years). 1-label datasets work correctly."
severity: minor

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
passed: 9
issues: 1
pending: 0
skipped: 0

## Gaps

- truth: "2-label datasets (EE, TR-to-PR, asylum) nest correctly with gender/group > province hierarchy"
  status: failed
  reason: "User reported: label_2 forward-fills last province into summary rows and next group section. Missing hierarchical nesting for 2-label layout. 1-label datasets work correctly."
  severity: minor
  test: 6
  root_cause: "Forward-fill for label_2 does not reset when label_1 changes to a new group or total row. Also, 2-label data should nest as group > sub-item > years instead of flat labels."
  artifacts:
    - path: "src/mcp_canada/shared/parsers.py"
      issue: "Forward-fill logic for label columns doesn't reset label_2 when label_1 changes"
  missing:
    - "Reset label_2 forward-fill when label_1 changes value"
    - "Add 2-label hierarchical nesting in _reshape_to_nested (gender > province > years)"
  debug_session: ""
