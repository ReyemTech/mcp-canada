"""WDS API response fixtures for StatCan client tests."""

import pytest
from unittest.mock import MagicMock


# --- Raw WDS response shapes (pre-unwrap) ---

CUBE_LIST_LITE_RESPONSE = [
    {
        "productId": 18100004,
        "cansimId": "326-0021",
        "cubeTitleEn": "Consumer Price Index, monthly",
        "cubeTitleFr": "Indice des prix à la consommation, mensuel",
        "cubeStartDate": "1914-01",
        "cubeEndDate": "2026-03",
        "releaseTime": "2026-03-19 08:30",
        "archived": False,
        "frequencyCode": 5,
        "subjectCode": ["18"],
        "surveyCode": ["2301"],
    },
    {
        "productId": 36100210,
        "cansimId": "380-0064",
        "cubeTitleEn": "Gross domestic product, expenditure-based",
        "cubeTitleFr": "Produit intérieur brut, basé sur les dépenses",
        "cubeStartDate": "1961-01",
        "cubeEndDate": "2025-12",
        "releaseTime": "2026-02-28 08:30",
        "archived": False,
        "frequencyCode": 7,
        "subjectCode": ["36"],
        "surveyCode": ["1901"],
    },
    {
        "productId": 14100287,
        "cansimId": "282-0087",
        "cubeTitleEn": "Labour force characteristics by sex and age group",
        "cubeTitleFr": "Caractéristiques de la population active selon le sexe et le groupe d'âge",
        "cubeStartDate": "1976-01",
        "cubeEndDate": "2026-03",
        "releaseTime": "2026-04-04 08:30",
        "archived": False,
        "frequencyCode": 5,
        "subjectCode": ["14"],
        "surveyCode": ["3701"],
    },
]

CUBE_METADATA_RESPONSE = {
    "status": "SUCCESS",
    "object": {
        "productId": 18100004,
        "cansimId": "326-0021",
        "cubeTitleEn": "Consumer Price Index, monthly",
        "cubeTitleFr": "Indice des prix à la consommation, mensuel",
        "cubeStartDate": "1914-01",
        "cubeEndDate": "2026-03",
        "frequencyCode": 5,
        "nbSeries": 1000,
        "nbDatapoints": 500000,
        "dimension": [
            {
                "dimensionNameEn": "Geography",
                "dimensionNameFr": "Géographie",
                "hasUom": False,
                "member": [
                    {
                        "memberId": 1,
                        "parentMemberId": 0,
                        "memberNameEn": "Canada",
                        "memberNameFr": "Canada",
                        "classificationCode": None,
                        "geoFlag": True,
                    }
                ],
            },
            {
                "dimensionNameEn": "Products and product groups",
                "dimensionNameFr": "Produits et groupes de produits",
                "hasUom": True,
                "member": [
                    {
                        "memberId": 1,
                        "parentMemberId": 0,
                        "memberNameEn": "All-items",
                        "memberNameFr": "Ensemble",
                        "classificationCode": "CP0",
                        "geoFlag": False,
                    }
                ],
            },
        ],
        "footnote": [
            {"footnoteId": 1, "footnoteEn": "Sample footnote", "footnoteFr": "Note de bas de page"}
        ],
    },
}

CODE_SETS_RESPONSE = {
    "status": "SUCCESS",
    "object": {
        "frequency": [
            {"frequencyCode": 1, "frequencyDescEn": "Daily", "frequencyDescFr": "Quotidien"},
            {"frequencyCode": 5, "frequencyDescEn": "Monthly", "frequencyDescFr": "Mensuel"},
        ],
        "scalar": [
            {"scalarFactorCode": 0, "scalarFactorDescEn": "units", "scalarFactorDescFr": "unités"},
            {"scalarFactorCode": 6, "scalarFactorDescEn": "hundreds", "scalarFactorDescFr": "centaines"},
        ],
        "status": [
            {"statusCode": 0, "statusDescEn": "Normal", "statusDescFr": "Normal"},
            {"statusCode": 2, "statusDescEn": "Revised", "statusDescFr": "Révisé"},
        ],
        "symbol": [
            {"symbolCode": 0, "symbolDescEn": "Not applicable", "symbolDescFr": "Sans objet"},
        ],
        "securityLevel": [
            {"securityLevelCode": 0, "securityLevelDescEn": "Public", "securityLevelDescFr": "Public"},
        ],
        "uom": [
            {"uomCode": 239, "uomDescEn": "2002=100", "uomDescFr": "2002=100"},
        ],
    },
}

SERIES_INFO_RESPONSE = [
    {
        "status": "SUCCESS",
        "object": {
            "productId": 18100004,
            "coordinate": "1.1",
            "vectorId": 41690973,
            "frequencyCode": 5,
            "scalarFactorCode": 0,
            "decimals": 1,
            "terminated": 0,
            "SeriesTitleEn": "Consumer Price Index (CPI), 2002=100; Canada; All-items",
            "SeriesTitleFr": "Indice des prix à la consommation (IPC), 2002=100; Canada; Ensemble",
            "memberUomCode": 239,
        },
    }
]

OBSERVATION_RESPONSE = [
    {
        "status": "SUCCESS",
        "object": {
            "responseStatusCode": 0,
            "vectorId": 41690973,
            "vectorDataPoint": [
                {
                    "refPer": "2026-03",
                    "refPerRaw": "2026-03",
                    "refYear": 2026,
                    "refMonth": 3,
                    "value": 163.4,
                    "decimals": 1,
                    "scalarFactorCode": 0,
                    "frequencyCode": 5,
                    "statusCode": 0,
                    "symbolCode": 0,
                    "releaseTime": "2026-03-19 08:30",
                    "securityLevelCode": 0,
                },
                {
                    "refPer": "2026-02",
                    "refPerRaw": "2026-02",
                    "refYear": 2026,
                    "refMonth": 2,
                    "value": 162.9,
                    "decimals": 1,
                    "scalarFactorCode": 0,
                    "frequencyCode": 5,
                    "statusCode": 0,
                    "symbolCode": 0,
                    "releaseTime": "2026-02-19 08:30",
                    "securityLevelCode": 0,
                },
                {
                    "refPer": "2026-01",
                    "refPerRaw": "2026-01",
                    "refYear": 2026,
                    "refMonth": 1,
                    "value": None,
                    "decimals": 1,
                    "scalarFactorCode": 0,
                    "frequencyCode": 5,
                    "statusCode": 2,
                    "symbolCode": 0,
                    "releaseTime": "2026-01-21 08:30",
                    "securityLevelCode": 0,
                },
            ],
        },
    }
]


def make_mock_response(data) -> MagicMock:
    """Create a mock httpx response with the given JSON data."""
    mock = MagicMock()
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


@pytest.fixture
def cube_list_lite_response():
    """List of 3 cube dicts matching getAllCubesListLite shape."""
    return CUBE_LIST_LITE_RESPONSE


@pytest.fixture
def cube_metadata_response():
    """WDS envelope with SUCCESS + full cube metadata object."""
    return CUBE_METADATA_RESPONSE


@pytest.fixture
def code_sets_response():
    """WDS envelope with all 6 code categories."""
    return CODE_SETS_RESPONSE


@pytest.fixture
def series_info_response():
    """WDS envelope list with SUCCESS + series object."""
    return SERIES_INFO_RESPONSE


@pytest.fixture
def observation_response():
    """WDS envelope list with vectorDataPoint array of 3 observations."""
    return OBSERVATION_RESPONSE


SERIES_INFO_BY_COORD_RESPONSE = [
    {
        "status": "SUCCESS",
        "object": {
            "productId": 35100003,
            "coordinate": "1.12.0.0.0.0.0.0.0.0",
            "vectorId": 32164132,
            "frequencyCode": 9,
            "scalarFactorCode": 6,
            "decimals": 2,
            "terminated": 0,
            "SeriesTitleEn": "GDP at basic prices; Canada; Agriculture",
            "SeriesTitleFr": "PIB aux prix de base; Canada; Agriculture",
            "memberUomCode": 301,
        },
    }
]

LATEST_N_BY_COORD_RESPONSE = [
    {
        "status": "SUCCESS",
        "object": {
            "responseStatusCode": 0,
            "vectorId": 32164132,
            "vectorDataPoint": [
                {
                    "refPer": "2023-01",
                    "refPerRaw": "2023-01",
                    "refYear": 2023,
                    "refMonth": 1,
                    "value": 99.5,
                    "decimals": 1,
                    "scalarFactorCode": 0,
                    "frequencyCode": 9,
                    "statusCode": 0,
                    "symbolCode": 0,
                    "releaseTime": "2023-03-01 08:30",
                    "securityLevelCode": 0,
                },
                {
                    "refPer": "2022-01",
                    "refPerRaw": "2022-01",
                    "refYear": 2022,
                    "refMonth": 1,
                    "value": 95.2,
                    "decimals": 1,
                    "scalarFactorCode": 0,
                    "frequencyCode": 9,
                    "statusCode": 0,
                    "symbolCode": 0,
                    "releaseTime": "2022-03-01 08:30",
                    "securityLevelCode": 0,
                },
            ],
        },
    }
]

# For Task 2 fixtures
REF_PERIOD_RESPONSE = [
    {
        "status": "SUCCESS",
        "object": {
            "responseStatusCode": 0,
            "vectorId": 32164132,
            "vectorDataPoint": [
                {
                    "refPer": "2023-01",
                    "refPerRaw": "2023-01",
                    "refYear": 2023,
                    "refMonth": 1,
                    "value": 99.5,
                    "decimals": 1,
                    "scalarFactorCode": 0,
                    "frequencyCode": 9,
                    "statusCode": 0,
                    "symbolCode": 0,
                    "releaseTime": "2023-03-01 08:30",
                    "securityLevelCode": 0,
                },
                {
                    "refPer": "2022-01",
                    "refPerRaw": "2022-01",
                    "refYear": 2022,
                    "refMonth": 1,
                    "value": 95.2,
                    "decimals": 1,
                    "scalarFactorCode": 0,
                    "frequencyCode": 9,
                    "statusCode": 0,
                    "symbolCode": 0,
                    "releaseTime": "2022-03-01 08:30",
                    "securityLevelCode": 0,
                },
            ],
        },
    }
]

BULK_VECTOR_RESPONSE = [
    {
        "status": "SUCCESS",
        "object": {
            "responseStatusCode": 0,
            "vectorId": 74804,
            "vectorDataPoint": [
                {
                    "refPer": "2024-01",
                    "refPerRaw": "2024-01",
                    "refYear": 2024,
                    "refMonth": 1,
                    "value": 150.2,
                    "decimals": 1,
                    "scalarFactorCode": 0,
                    "frequencyCode": 5,
                    "statusCode": 0,
                    "symbolCode": 0,
                    "releaseTime": "2024-02-15 08:30",
                    "securityLevelCode": 0,
                },
            ],
        },
    },
    {
        "status": "FAILED",
        "object": "Vector 32164132 not found in release range",
    },
]

CHANGED_SERIES_RESPONSE = {
    "status": "SUCCESS",
    "object": [
        {
            "vectorId": 41690973,
            "productId": 18100004,
            "coordinate": "1.1",
            "releaseTime": "2026-04-07 08:30",
        },
        {
            "vectorId": 32164132,
            "productId": 35100003,
            "coordinate": "1.12",
            "releaseTime": "2026-04-07 08:30",
        },
    ],
}

CHANGED_CUBES_RESPONSE = {
    "status": "SUCCESS",
    "object": [
        {
            "productId": 18100004,
            "releaseTime": "2026-04-07 08:30",
        },
        {
            "productId": 35100003,
            "releaseTime": "2026-04-07 08:30",
        },
    ],
}


@pytest.fixture
def series_info_by_coord_response():
    """WDS envelope list with SUCCESS + series info from coord lookup."""
    return SERIES_INFO_BY_COORD_RESPONSE


@pytest.fixture
def latest_n_by_coord_response():
    """WDS envelope list with SUCCESS + 2 observation data points."""
    return LATEST_N_BY_COORD_RESPONSE


@pytest.fixture
def ref_period_response():
    """WDS envelope list for getDataFromVectorByReferencePeriodRange."""
    return REF_PERIOD_RESPONSE


@pytest.fixture
def bulk_vector_response():
    """WDS response list with 2 vectors: one SUCCESS, one FAILED."""
    return BULK_VECTOR_RESPONSE


@pytest.fixture
def changed_series_response():
    """WDS envelope with list of changed series."""
    return CHANGED_SERIES_RESPONSE


@pytest.fixture
def changed_cubes_response():
    """WDS envelope with list of changed cubes."""
    return CHANGED_CUBES_RESPONSE


@pytest.fixture(autouse=True)
async def reset_cache():
    """Clear aiocache between tests to avoid cross-test contamination."""
    from mcp_canada.shared.cache import _cache
    await _cache.clear()
    yield
    await _cache.clear()
