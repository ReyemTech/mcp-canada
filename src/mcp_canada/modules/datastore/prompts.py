"""MCP prompts for the Datastore module.

Provides guided workflow prompts and quick lookup templates for the local
SQLite datastore. All prompts are bilingual (en/fr) via the lang parameter.

Guided workflow prompts return list[Message] with user + assistant roles.
Quick lookup prompts return a str instruction.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


@prompt
async def ds_create_and_query(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through creating a table, inserting data, and querying it with SQL.

    Chains ds_create_table -> ds_insert_data -> ds_query for a complete
    store-and-query workflow using the local SQLite datastore.
    """
    if lang == "fr":
        return [
            Message(
                "Souhaitez-vous stocker des données dans le datastore local pour les "
                "analyser avec SQL? Je peux créer une table, y insérer des données, "
                "puis exécuter des requêtes SELECT. Quelles données voulez-vous stocker?",
                role="user",
            ),
            Message(
                "Je vais d'abord utiliser ds_create_table pour créer la table avec "
                "les colonnes appropriées (TEXT, INTEGER, REAL), puis ds_insert_data "
                "pour insérer les lignes de données, et enfin ds_query avec une "
                "requête SELECT pour analyser les résultats. Commençons.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Would you like to store data in the local datastore for SQL analysis? "
            "I can create a table, insert data, then run SELECT queries. "
            "What data would you like to store?",
            role="user",
        ),
        Message(
            "I will first use ds_create_table to create the table with appropriate "
            "columns (TEXT, INTEGER, REAL), then ds_insert_data to insert the data "
            "rows, and finally ds_query with a SELECT statement to analyze the results. "
            "Let's get started.",
            role="assistant",
        ),
    ]


@prompt
async def ds_quick_query(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to query an existing table in the local datastore."""
    if lang == "fr":
        return (
            "Utilisez ds_query avec une requête SELECT (ex: 'SELECT * FROM ma_table LIMIT 10') "
            "pour interroger les données stockées. Utilisez aussi PRAGMA table_info(ma_table) "
            "pour voir le schéma, ou PRAGMA table_list pour lister toutes les tables."
        )
    return (
        "Use ds_query with a SELECT statement (e.g., 'SELECT * FROM my_table LIMIT 10') "
        "to query stored data. Also use PRAGMA table_info(my_table) to see the schema, "
        "or PRAGMA table_list to list all tables."
    )


@prompt
async def ds_explore_tables(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to discover existing tables and their schemas in the datastore."""
    if lang == "fr":
        return (
            "Utilisez ds_list_tables pour voir toutes les tables disponibles dans le "
            "datastore local, puis ds_get_schema avec le nom d'une table pour voir "
            "la structure de ses colonnes (types, noms)."
        )
    return (
        "Use ds_list_tables to see all available tables in the local datastore, "
        "then ds_get_schema with a table name to see its column structure "
        "(names and types)."
    )


@prompt
async def ds_cross_module_join(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through combining data from multiple modules using SQL JOINs.

    Demonstrates the store-multiple-sources-then-JOIN pattern using the datastore
    as a local integration layer across mcp-canada modules.
    """
    if lang == "fr":
        return [
            Message(
                "Souhaitez-vous combiner des données de plusieurs modules en utilisant "
                "SQL JOIN? Par exemple, joindre des données de taux de change (BoC) "
                "avec des données économiques (StatCan) pour une analyse comparative?",
                role="user",
            ),
            Message(
                "Je vais récupérer les données de chaque module et les stocker dans "
                "des tables séparées du datastore local: boc_get_exchange_rates + "
                "ds_insert_data pour les taux, sc_fetch_vectors_to_store pour StatCan, "
                "puis ds_query avec un JOIN SQL pour combiner les deux sources. "
                "Cette approche transforme des APIs isolées en une plateforme unifiée.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Would you like to combine data from multiple modules using SQL JOINs? "
            "For example, joining exchange rate data (BoC) with economic data (StatCan) "
            "for a comparative analysis across datasets?",
            role="user",
        ),
        Message(
            "I will fetch data from each module and store them in separate datastore "
            "tables: boc_get_exchange_rates + ds_insert_data for rates, "
            "sc_fetch_vectors_to_store for StatCan data, then ds_query with a SQL JOIN "
            "to combine both sources. This approach turns isolated APIs into a unified "
            "queryable platform.",
            role="assistant",
        ),
    ]
