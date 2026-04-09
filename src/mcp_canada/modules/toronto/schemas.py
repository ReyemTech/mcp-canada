"""Pydantic v2 models for Toronto Open Data API responses.

Kept minimal per project convention — flat dicts are preferred for most
datastore responses. Schemas are only defined where type-safety adds value.
"""

from pydantic import BaseModel


class GTFSStop(BaseModel):
    """A single TTC GTFS stop."""

    stop_id: str
    stop_name: str
    stop_lat: str
    stop_lon: str
    location_type: str | None = None


class GTFSRoute(BaseModel):
    """A single TTC GTFS route."""

    route_id: str
    route_short_name: str
    route_long_name: str
    route_type: str
