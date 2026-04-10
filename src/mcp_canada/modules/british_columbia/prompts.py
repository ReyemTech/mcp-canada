"""BC open data prompts — 6 bilingual prompts populated in Plan 04.

Prompts guide agents through BC data exploration workflows:
- bc_explore_wildfires: guided multi-tool wildfire analysis
- bc_explore_forestry: guided multi-tool forestry analysis
- bc_explore_environment: guided multi-tool environment analysis
- bc_quick_dataset_search: quick lookup for dataset discovery
- bc_check_water_quality: quick lookup for water quality data
- bc_wildfire_status_now: quick lookup for current wildfire status
"""

from fastmcp.prompts import prompt  # noqa: F401 — used by Plan 04 implementations
