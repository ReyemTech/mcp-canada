"""Alberta prompts — 6 bilingual prompts (3 guided + 3 quick lookups) — Plan 08 fills bodies.

Guided workflows (list[Message]) — multi-step tool chaining:
  alberta_explore_energy            — AER well/pipeline/production workflow
  alberta_explore_wildfires         — active fires + perimeters + bans workflow
  alberta_explore_health_or_transport — hospitals/EMS/AHS zones + 511 events

Quick lookups (str) — single-tool instructions:
  alberta_quick_dataset_search      — search.alberta.ca catalogue
  alberta_check_road_conditions     — 511 Alberta winter road conditions
  alberta_active_fires_now          — current wildfire status

IMPORTANT: All prompts accept `lang: Literal["en", "fr"] = "en"` via Annotated.
ZERO-parameter resources are in resources.py — see CLAUDE.md rule.
"""

from typing import Annotated, Literal

from fastmcp.prompts import prompt
from fastmcp.prompts.prompt import Message  # noqa: F401 — used by Plan 08 guided workflows


__all__ = [
    # Guided workflows (list[Message]) — Plan 08
    "alberta_explore_energy",
    "alberta_explore_wildfires",
    "alberta_explore_health_or_transport",
    # Quick lookups (str) — Plan 08
    "alberta_quick_dataset_search",
    "alberta_check_road_conditions",
    "alberta_active_fires_now",
]


# ---------------------------------------------------------------------------
# Guided workflows — Plan 08
# ---------------------------------------------------------------------------


@prompt
async def alberta_explore_energy(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Alberta energy data exploration — AER wells, pipelines, production.

    Chains alberta_get_well_licences_today -> alberta_get_pipeline_statistics ->
    alberta_get_production_volumes for a comprehensive AER energy sector overview.
    """
    raise NotImplementedError("Plan 08 implements")


@prompt
async def alberta_explore_wildfires(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Alberta wildfire situational awareness — active fires, perimeters, bans.

    Chains alberta_get_active_fires -> alberta_get_fire_perimeters ->
    alberta_get_fire_bans -> alberta_get_fire_control_orders for wildfire emergency context.
    """
    raise NotImplementedError("Plan 08 implements")


@prompt
async def alberta_explore_health_or_transport(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through Alberta health facilities or transport network exploration.

    Branches between health (alberta_get_hospitals -> alberta_get_ahs_zones ->
    alberta_get_health_facilities) and transport (alberta_get_road_events ->
    alberta_get_winter_road_conditions -> alberta_get_traffic_cameras).
    """
    raise NotImplementedError("Plan 08 implements")


# ---------------------------------------------------------------------------
# Quick lookups — Plan 08
# ---------------------------------------------------------------------------


@prompt
async def alberta_quick_dataset_search(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to search the open.alberta.ca CKAN catalogue and query a dataset.

    Use for: one-shot Alberta open data discovery — search, inspect dataset details, and
    query records from the best available resource via the auto-routing query tool.
    """
    raise NotImplementedError("Plan 08 implements")


@prompt
async def alberta_check_road_conditions(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to check current Alberta road events and winter road conditions.

    Use for: quick lookup of 511 Alberta highway events, winter road conditions, and
    traffic cameras on Alberta's provincial road network.
    """
    raise NotImplementedError("Plan 08 implements")


@prompt
async def alberta_active_fires_now(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to check current Alberta active wildfires from WMBappServices.

    Use for: quick wildfire situational awareness during fire season (May-October).
    Returns instruction to call alberta_get_active_fires with an optional status filter.
    """
    raise NotImplementedError("Plan 08 implements")
