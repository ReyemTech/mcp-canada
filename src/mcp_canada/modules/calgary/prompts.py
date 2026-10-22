"""Calgary module prompts — bilingual @prompt functions for the MCP server.

All prompts use standalone @prompt from fastmcp.prompts (NEVER @mcp.prompt).
All prompts include lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en".
All prompts use the "calgary_" prefix.

Guided workflow (list[Message]) — multi-step tool chaining:
  calgary_explore_open_data — search -> dataset details -> SoQL query

Quick lookup (str) — single-tool instructions:
  calgary_quick_find_dataset — guide calgary_search_datasets
"""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt

__all__ = [
    "calgary_explore_open_data",
    "calgary_quick_find_dataset",
]


@prompt
async def calgary_explore_open_data(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through discovering and querying a Calgary open dataset end to end.

    Chains calgary_search_datasets -> calgary_get_dataset_details -> calgary_query_dataset
    for a full discovery-to-data workflow against data.calgary.ca (Socrata SODA API,
    keyless, 418+ datasets as of 2026-09-04).
    """
    if lang == "fr":
        return [
            Message(
                "Je veux trouver et interroger un jeu de données ouvertes de la "
                "ville de Calgary, mais je ne connais pas son identifiant.",
                role="user",
            ),
            Message(
                "Je vais vous guider à travers le portail de données ouvertes de "
                "Calgary (data.calgary.ca, portail Socrata) en trois étapes :\n\n"
                "**Étape 1 — Rechercher :**\n"
                "Appelez `calgary_search_datasets` avec un mot-clé (ex. `query='traffic'`). "
                "Retourne une liste de jeux de données avec leur `id` (identifiant 4x4, "
                "ex. `35ra-9556`), `name`, `category` et `tags`.\n\n"
                "**Étape 2 — Inspecter le schéma :**\n"
                "Appelez `calgary_get_dataset_details` avec l'`id` choisi à l'étape 1. "
                "Retourne les colonnes (`name`, `field_name`, `data_type`), l'attribution, "
                "la licence et la date de publication.\n\n"
                "**Étape 3 — Interroger les données :**\n"
                "Appelez `calgary_query_dataset` avec le même `id`, en utilisant les noms "
                "de colonnes (`field_name`) de l'étape 2 dans `select`/`where`/`order`. "
                "La géométrie (`the_geom`) est incluse par défaut — utilisez `select` "
                "explicitement pour l'exclure si elle n'est pas nécessaire.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "I want to find and query a City of Calgary open dataset, but I don't "
            "know its dataset ID.",
            role="user",
        ),
        Message(
            "I'll guide you through Calgary's open data portal (data.calgary.ca, "
            "a Socrata portal) in three steps:\n\n"
            "**Step 1 — Search:**\n"
            "Call `calgary_search_datasets` with a keyword (e.g. `query='traffic'`). "
            "Returns a list of datasets with their `id` (4x4 identifier, e.g. "
            "`35ra-9556`), `name`, `category`, and `tags`.\n\n"
            "**Step 2 — Inspect the schema:**\n"
            "Call `calgary_get_dataset_details` with the `id` chosen in step 1. "
            "Returns columns (`name`, `field_name`, `data_type`), attribution, "
            "license, and publication date.\n\n"
            "**Step 3 — Query the data:**\n"
            "Call `calgary_query_dataset` with the same `id`, using the `field_name` "
            "values from step 2 in `select`/`where`/`order`. Geometry (`the_geom`) is "
            "included by default — pass an explicit `select` to exclude it if not needed.",
            role="assistant",
        ),
    ]


@prompt
async def calgary_quick_find_dataset(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick lookup guiding a single call to calgary_search_datasets."""
    if lang == "fr":
        return (
            "Appelez `calgary_search_datasets` avec `query=<mot-clé>` pour rechercher "
            "dans le catalogue Socrata de Calgary (data.calgary.ca). Laissez `query` "
            "vide pour lister les jeux de données les plus récents. Utilisez `limit` "
            "et `offset` pour paginer (max 1000 par page)."
        )
    return (
        "Call `calgary_search_datasets` with `query=<keyword>` to search Calgary's "
        "Socrata catalogue (data.calgary.ca). Leave `query` empty to list the most "
        "recent datasets. Use `limit` and `offset` to paginate (max 1000 per page)."
    )
