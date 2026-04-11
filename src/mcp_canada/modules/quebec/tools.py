"""Quebec tools — populated in Plans 02/03/04.

Discovery tools (Plan 02):
  quebec_search_datasets, quebec_get_dataset_details, quebec_query_dataset,
  quebec_list_organizations, quebec_list_categories

Health/Transport tools (Plan 03):
  quebec_get_health_installations, quebec_get_er_wait_times,
  quebec_get_population_by_municipality, quebec_get_road_conditions,
  quebec_get_road_works, quebec_get_road_events, quebec_get_bridge_structures

Environment/Energy tools (Plan 04):
  quebec_get_forest_fires_history, quebec_get_air_quality_stations,
  quebec_get_air_quality_index, quebec_get_water_quality_monitoring,
  quebec_get_electricity_data, quebec_get_protected_areas
"""

from typing import Literal

from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_error, make_response

from . import client as _client

__all__: list[str] = []
