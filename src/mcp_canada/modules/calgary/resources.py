"""Calgary module resources — zero-parameter @resource functions for the MCP server.

IMPORTANT: All functions are ZERO-parameter. Adding any parameter (even `lang`) would
promote them to ResourceTemplate and remove them from resources/list. Bilingual content
is embedded inline (both en and fr in the same markdown body).

URI scheme conventions:
  docs:// — Markdown guides: return raw markdown string. Both languages in same document.

Documentation guides (docs://):
  docs://calgary/portal-guide — Socrata portal facts + SoQL how-to for data.calgary.ca.
"""

from __future__ import annotations

from fastmcp.resources import resource

__all__ = ["calgary_portal_guide"]


@resource(
    "docs://calgary/portal-guide",
    mime_type="text/markdown",
    name="calgary_portal_guide",
    title="Calgary Open Data Portal Guide — Socrata SODA API",
)
async def calgary_portal_guide() -> str:
    """Markdown guide to data.calgary.ca's Socrata SODA API and this module's tools.

    Covers portal facts (live-verified 2026-09-04), the discovery-to-query workflow,
    and SoQL query syntax with Calgary-specific examples.
    """
    return """# Calgary Open Data Portal Guide / Guide du portail de données ouvertes de Calgary

## Portal facts (EN) / Faits sur le portail (FR)

- **Domain:** `data.calgary.ca` — a **Socrata** portal (SODA API), NOT CKAN.
- **Live-verified 2026-09-04:** 418 datasets, keyless catalog and resource reads.
- **Sample dataset:** "Traffic Incidents" (`35ra-9556`), category "Transportation/Transit".
- **Auth:** none required. Set `CALGARY_APP_TOKEN` env var for a higher Socrata
  throttle limit (optional — this module works keyless by default).

## Discovery-to-query workflow

1. `calgary_search_datasets(query=...)` — free-text search, returns dataset `id`
   (4x4 identifier), `name`, `category`, `tags`.
2. `calgary_get_dataset_details(dataset_id=...)` — returns columns (`name`,
   `field_name`, `data_type`, `description`), attribution, license, publication date.
3. `calgary_query_dataset(dataset_id=..., where=..., select=..., order=...)` — runs a
   SoQL query against `/resource/{id}.json` using the `field_name` values from step 2.

## SoQL syntax (SODA Query Language)

- `$select` — comma-separated field names, e.g. `"start_dt,description,quadrant"`.
- `$where` — SQL-like filter, e.g. `"quadrant='NW'"` or `"start_dt > '2026-01-01'"`.
- `$order` — e.g. `"start_dt DESC"`.
- `$q` — full-text search within the dataset (separate from `$where`).
- `$group` — GROUP BY clause for aggregations, paired with a `count(*)`-style `$select`.
- `$limit` / `$offset` — pagination; Socrata's hard cap is 50,000 rows per request.

This module's `calgary_query_dataset` tool exposes these as plain `select`, `where`,
`order`, `q`, `group`, `limit`, `offset` arguments — the `$` prefix is added internally
before the request reaches Socrata.

Geometry (`the_geom`) is returned when `include_geometry=True` or when `select` is
omitted. Pass an explicit `select` naming only the fields you need to exclude it —
large `MultiPolygon`/`Point` geometry payloads can bloat a response significantly.

## FR — Guide rapide

- **Domaine :** `data.calgary.ca` — un portail **Socrata** (API SODA), PAS CKAN.
- **Vérifié en direct le 2026-09-04 :** 418 jeux de données, lectures sans clé.
- **Flux :** `calgary_search_datasets` → `calgary_get_dataset_details` →
  `calgary_query_dataset`, en utilisant les noms `field_name` retournés à l'étape 2.
- **SoQL :** `select`, `where`, `order`, `q`, `group`, `limit`/`offset` — mêmes clauses
  que la version anglaise ci-dessus.
"""
