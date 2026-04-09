"""MCP prompts for the Weather module (MSC GeoMet OGC API).

Provides guided workflow prompts and quick lookup templates for Environment Canada
weather, climate, hydrology, air quality, and severe weather data.
All prompts are bilingual (en/fr) via the lang parameter and use the wx_ prefix.

Guided workflow prompts return list[Message] with user + assistant roles.
Quick lookup prompts return a str instruction.

NOTE: This file is at the top-level weather/ directory (not in sub-modules).
FileSystemProvider scans recursively — one prompts.py covers all 8 sub-modules.
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


@prompt
async def wx_check_weather(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a local weather check workflow.

    Chains wx_search_stations -> wx_get_current_conditions -> wx_get_forecast
    to find a weather station and retrieve current conditions and forecast.
    """
    if lang == "fr":
        return [
            Message(
                "Quelle ville ou emplacement souhaitez-vous vérifier? "
                "Je peux trouver la station météorologique la plus proche et récupérer "
                "les conditions actuelles et les prévisions.",
                role="user",
            ),
            Message(
                "Je vais d'abord utiliser wx_search_stations pour trouver les stations "
                "météorologiques proches de votre emplacement, puis wx_get_current_conditions "
                "pour les conditions actuelles, et enfin wx_get_forecast pour les prévisions "
                "des prochains jours. Commençons.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which city or location would you like to check? "
            "I can find the nearest weather station and retrieve current "
            "conditions and the forecast.",
            role="user",
        ),
        Message(
            "I will first use wx_search_stations to find weather stations near your location, "
            "then wx_get_current_conditions for current conditions, "
            "and wx_get_forecast for the next several days. Let's get started.",
            role="assistant",
        ),
    ]


@prompt
async def wx_quick_forecast(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to retrieve a weather forecast for a known station."""
    if lang == "fr":
        return (
            "Utilisez wx_get_forecast avec un station_id pour obtenir les prévisions météo. "
            "Si vous ne connaissez pas l'identifiant de station, utilisez wx_search_stations "
            "avec le nom de la ville pour le trouver d'abord."
        )
    return (
        "Use wx_get_forecast with a station_id to retrieve the weather forecast. "
        "If you don't know the station ID, use wx_search_stations with the city name "
        "to find it first."
    )


@prompt
async def wx_analyze_climate(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a climate analysis workflow.

    Chains wx_get_climate_normals -> wx_get_climate_trends -> wx_compare_climate_periods
    to analyze long-term climate patterns for a location.
    """
    if lang == "fr":
        return [
            Message(
                "Quelle station ou région souhaitez-vous analyser? "
                "Je peux récupérer les normales climatiques, les tendances historiques "
                "et comparer différentes périodes climatiques.",
                role="user",
            ),
            Message(
                "Je vais utiliser wx_get_climate_normals pour les normales de la période "
                "1981-2010 ou 1991-2020, puis wx_get_climate_trends (données AHCCD) pour "
                "les tendances à long terme des températures et précipitations, et enfin "
                "wx_compare_climate_periods pour comparer deux périodes. Commençons.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which station or region would you like to analyze? "
            "I can retrieve climate normals, historical trends, "
            "and compare different climate periods.",
            role="user",
        ),
        Message(
            "I will use wx_get_climate_normals for the 1981-2010 or 1991-2020 period normals, "
            "then wx_get_climate_trends (AHCCD data) for long-term temperature and "
            "precipitation trends, and wx_compare_climate_periods to compare two periods. "
            "Let's get started.",
            role="assistant",
        ),
    ]


@prompt
async def wx_check_air_quality(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to retrieve AQHI (Air Quality Health Index) for a station."""
    if lang == "fr":
        return (
            "Utilisez wx_get_aqhi avec un station_id pour obtenir l'IQSA (Indice de la "
            "qualité de l'air et de la santé) actuel. Pour les prévisions sur 24-48h, "
            "utilisez wx_get_aqhi_forecast. L'IQSA va de 1 (faible) à 10+ (très élevé)."
        )
    return (
        "Use wx_get_aqhi with a station_id to get the current AQHI "
        "(Air Quality Health Index). For a 24-48h forecast, use wx_get_aqhi_forecast. "
        "AQHI ranges from 1 (low risk) to 10+ (very high risk)."
    )


@prompt
async def wx_water_conditions(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a hydrological water conditions workflow.

    Chains wx_search_hydro_stations -> wx_get_water_levels -> wx_get_flood_risk
    to assess water levels and flood risk for a waterway.
    """
    if lang == "fr":
        return [
            Message(
                "Quel cours d'eau ou rivière souhaitez-vous surveiller? "
                "Je peux trouver les stations hydrométriques, récupérer les niveaux d'eau "
                "et les débits actuels, et évaluer le risque d'inondation.",
                role="user",
            ),
            Message(
                "Je vais d'abord utiliser wx_search_hydro_stations pour trouver les stations "
                "hydrométriques dans la zone, puis wx_get_water_levels pour les niveaux d'eau "
                "et wx_get_water_flow pour les débits en temps réel. Si nécessaire, "
                "wx_get_flood_risk peut évaluer les risques d'inondation. Commençons.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which waterway or river would you like to monitor? "
            "I can find hydrometric stations, retrieve current water levels "
            "and flow rates, and assess flood risk.",
            role="user",
        ),
        Message(
            "I will first use wx_search_hydro_stations to find hydrometric stations in the area, "
            "then wx_get_water_levels for current water levels and wx_get_water_flow for "
            "real-time flow rates. If needed, wx_get_flood_risk can assess flood risk. "
            "Let's get started.",
            role="assistant",
        ),
    ]


@prompt
async def wx_severe_weather(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a severe weather monitoring workflow.

    Chains wx_get_weather_alerts -> wx_get_radar_data -> wx_get_lightning
    to provide a comprehensive severe weather situation report.
    """
    if lang == "fr":
        return [
            Message(
                "Quelle région ou province souhaitez-vous surveiller pour les phénomènes "
                "météorologiques sévères? Je peux récupérer les alertes actives, "
                "les données radar et les éclairs.",
                role="user",
            ),
            Message(
                "Je vais utiliser wx_get_weather_alerts pour les avertissements et veilles "
                "météorologiques actifs dans la région, puis wx_get_radar_data pour les "
                "précipitations radar récentes, et wx_get_lightning pour l'activité "
                "orageuse. Commençons.",
                role="assistant",
            ),
        ]
    return [
        Message(
            "Which region or province would you like to monitor for severe weather? "
            "I can retrieve active alerts, radar data, and lightning activity.",
            role="user",
        ),
        Message(
            "I will use wx_get_weather_alerts for active weather warnings and watches "
            "in the region, then wx_get_radar_data for recent radar precipitation data, "
            "and wx_get_lightning for thunderstorm activity. Let's get started.",
            role="assistant",
        ),
    ]
