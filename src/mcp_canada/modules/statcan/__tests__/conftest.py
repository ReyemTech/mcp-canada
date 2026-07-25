"""WDS API response fixtures for StatCan client tests.

Product IDs and titles are synthetic, but every WDS *code* below is a real
value from StatCan's published code set (getCodeSets). The fixtures
previously used frequencyCode 5 and 7 for monthly/quarterly series — neither
means that upstream (5 is not a StatCan code at all; 7 is Bimonthly). Those
invented codes were what made the shipped FREQUENCY_CODES map look correct.
Keep these aligned with constants.FREQUENCY_CODES / SCALAR_FACTOR_CODES.
"""

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
        "frequencyCode": 6,
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
        "frequencyCode": 9,
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
        "frequencyCode": 6,
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
        "frequencyCode": 6,
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
            {"frequencyCode": 1, "frequencyDescEn": "Daily", "frequencyDescFr": "Quotidienne"},
            {"frequencyCode": 6, "frequencyDescEn": "Monthly", "frequencyDescFr": "Mensuelle"},
        ],
        "scalar": [
            {"scalarFactorCode": 0, "scalarFactorDescEn": "units", "scalarFactorDescFr": "unités"},
            {"scalarFactorCode": 6, "scalarFactorDescEn": "millions", "scalarFactorDescFr": "millions"},
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
            {"memberUomCode": 239, "memberUomEn": "2002=100", "memberUomFr": "2002=100"},
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
            "frequencyCode": 6,
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
                    "frequencyCode": 6,
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
                    "frequencyCode": 6,
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
                    "frequencyCode": 6,
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
            "frequencyCode": 12,
            "scalarFactorCode": 2,
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
                    "frequencyCode": 6,
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


# ---------------------------------------------------------------------------
# Phase 9: SDMX fixtures
# ---------------------------------------------------------------------------

# Valid SDMX 2.1 XML structure for CPI table 18100004
# Two dimensions: Geography (position 1) and Products (position 2)
SDMX_STRUCTURE_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<mes:Structure
    xmlns:mes="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
    xmlns:str="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure"
    xmlns:com="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <mes:Structures>
    <str:Codelists>
      <str:Codelist id="CL_GEO" agencyID="StatCan" version="1.0">
        <com:Name xml:lang="en">Geography</com:Name>
        <com:Name xml:lang="fr">Géographie</com:Name>
        <str:Code id="1">
          <com:Name xml:lang="en">Canada</com:Name>
          <com:Name xml:lang="fr">Canada</com:Name>
        </str:Code>
        <str:Code id="2">
          <com:Name xml:lang="en">Ontario</com:Name>
          <com:Name xml:lang="fr">Ontario</com:Name>
        </str:Code>
      </str:Codelist>
      <str:Codelist id="CL_PRODUCT" agencyID="StatCan" version="1.0">
        <com:Name xml:lang="en">Products and product groups</com:Name>
        <com:Name xml:lang="fr">Produits et groupes de produits</com:Name>
        <str:Code id="1">
          <com:Name xml:lang="en">All-items</com:Name>
          <com:Name xml:lang="fr">Ensemble</com:Name>
        </str:Code>
        <str:Code id="2">
          <com:Name xml:lang="en">Food</com:Name>
          <com:Name xml:lang="fr">Aliments</com:Name>
        </str:Code>
      </str:Codelist>
    </str:Codelists>
    <str:DataStructures>
      <str:DataStructure id="Data_Structure_18100004" agencyID="StatCan" version="1.0">
        <str:DataStructureComponents>
          <str:DimensionList id="DimensionDescriptor">
            <str:Dimension id="GEO" position="1">
              <str:LocalRepresentation>
                <str:Enumeration>
                  <Ref id="CL_GEO" agencyID="StatCan" version="1.0" package="codelist" class="Codelist"/>
                </str:Enumeration>
              </str:LocalRepresentation>
            </str:Dimension>
            <str:Dimension id="PRODUCT" position="2">
              <str:LocalRepresentation>
                <str:Enumeration>
                  <Ref id="CL_PRODUCT" agencyID="StatCan" version="1.0" package="codelist" class="Codelist"/>
                </str:Enumeration>
              </str:LocalRepresentation>
            </str:Dimension>
          </str:DimensionList>
        </str:DataStructureComponents>
      </str:DataStructure>
    </str:DataStructures>
  </mes:Structures>
</mes:Structure>
"""

# Valid SDMX-JSON compact format with 2 series (colon-delimited keys), 3 observations each
SDMX_DATA_JSON = {
    "meta": {"id": "test", "prepared": "2024-01-01"},
    "data": {
        "structures": [
            {
                "dimensions": {
                    "series": [
                        {
                            "id": "GEO",
                            "keyPosition": 0,
                            "values": [
                                {"id": "1", "name": "Canada"},
                                {"id": "2", "name": "Ontario"},
                            ],
                        },
                        {
                            "id": "PRODUCT",
                            "keyPosition": 1,
                            "values": [
                                {"id": "1", "name": "All-items"},
                            ],
                        },
                    ],
                    "observation": [
                        {
                            "id": "TIME_PERIOD",
                            "values": [
                                {"id": "2024-01"},
                                {"id": "2024-02"},
                                {"id": "2024-03"},
                            ],
                        }
                    ],
                }
            }
        ],
        "dataSets": [
            {
                "series": {
                    "0:0": {
                        "observations": {
                            "0": [163.4],
                            "1": [164.1],
                            "2": [None],
                        }
                    },
                    "1:0": {
                        "observations": {
                            "0": [158.2],
                            "1": [159.0],
                            "2": [159.5],
                        }
                    },
                }
            }
        ],
    },
}

# Same SDMX-JSON shape but for a single vector endpoint response
SDMX_VECTOR_JSON = {
    "meta": {"id": "vector-test", "prepared": "2024-01-01"},
    "data": {
        "structures": [
            {
                "dimensions": {
                    "series": [
                        {
                            "id": "GEO",
                            "keyPosition": 0,
                            "values": [
                                {"id": "1", "name": "Canada"},
                            ],
                        },
                    ],
                    "observation": [
                        {
                            "id": "TIME_PERIOD",
                            "values": [
                                {"id": "2024-01"},
                                {"id": "2024-02"},
                            ],
                        }
                    ],
                }
            }
        ],
        "dataSets": [
            {
                "series": {
                    "0": {
                        "observations": {
                            "0": [41690973.0],
                            "1": [41700000.0],
                        }
                    },
                }
            }
        ],
    },
}


@pytest.fixture
def sdmx_structure_xml():
    """Valid SDMX 2.1 XML string for CPI table (2 dimensions, 2 codes each)."""
    return SDMX_STRUCTURE_XML


@pytest.fixture
def sdmx_data_json():
    """SDMX-JSON compact format dict with 2 series, 3 observations each."""
    return SDMX_DATA_JSON


@pytest.fixture
def sdmx_vector_json():
    """SDMX-JSON compact format dict for a single vector endpoint response."""
    return SDMX_VECTOR_JSON
