"""Quebec prompts — populated in Plan 04.

Guided workflows (Plan 04):
  quebec_explore_health, quebec_explore_transport_conditions, quebec_explore_environment

Quick lookups (Plan 04):
  quebec_quick_dataset_search, quebec_check_road_conditions, quebec_active_fires_now
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt

__all__: list[str] = []
