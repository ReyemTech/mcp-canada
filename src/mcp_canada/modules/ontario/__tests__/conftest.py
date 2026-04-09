"""Test fixtures for Ontario Open Data client tests."""

import pytest
from unittest.mock import MagicMock


# Long description for truncation testing (>500 chars)
LONG_DESCRIPTION = (
    "This dataset contains detailed population projection information for Ontario "
    "municipalities and regions from 2024 to 2051. It includes breakdowns by age group, "
    "gender, and geographic region. The data is updated annually and provides insights "
    "into demographic trends across the province, including growth patterns, aging "
    "population dynamics, migration trends, and urban/rural distribution forecasts. "
    "Additional context about methodology, assumptions, and confidence intervals is also "
    "available through linked resources and supplementary documentation provided by the "
    "Ministry of Finance."
)

# Short description that should NOT be truncated
SHORT_DESCRIPTION = "Ontario population projections by region and age group."

# Sample bilingual Ontario CKAN dataset with title_translated/notes_translated
SAMPLE_ONT_DATASET_BILINGUAL = {
    "id": "f52a6457-fb37-4267-acde-11a1e57c4dc8",
    "name": "population-projections",
    "title": "Population projections",
    "title_translated": {
        "en": "Population projections",
        "fr": "Projections demographiques",
    },
    "notes_translated": {
        "en": LONG_DESCRIPTION,
        "fr": "Projections de la population de l'Ontario par région et groupe d'âge.",
    },
    "organization": {"name": "finance", "title": "Finance"},
    "num_resources": 12,
    "tags": [{"name": "population"}, {"name": "projections"}],
    "resources": [
        {
            "id": f"res-{i:03d}",
            "name": f"Resource {i}",
            "format": "XLSX",
            "size": 244000 * i,
            "url": f"https://data.ontario.ca/resource/{i}",
            "description": f"Resource {i} description",
        }
        for i in range(1, 16)  # 15 resources to test capping at 10
    ],
    "metadata_created": "2020-01-01T00:00:00.000000",
    "metadata_modified": "2025-08-01T00:00:00.000000",
}

# Sample Ontario CKAN dataset without translations (fallback test)
SAMPLE_ONT_DATASET_NO_TRANSLATION = {
    "id": "abc123-no-trans",
    "name": "simple-ontario-dataset",
    "title": "Simple Ontario Dataset",
    "organization": {"name": "health", "title": "Health"},
    "num_resources": 1,
    "tags": [],
    "resources": [
        {
            "id": "res-001",
            "name": "Main CSV",
            "format": "CSV",
            "size": 2048,
            "url": "https://data.ontario.ca/resource/main.csv",
        }
    ],
    "metadata_created": "2022-05-10T08:00:00.000000",
    "metadata_modified": "2023-11-01T12:00:00.000000",
}

# Sample Ontario CKAN package_search response
SAMPLE_PACKAGE_SEARCH_RESPONSE = {
    "success": True,
    "result": {
        "count": 96,
        "results": [
            SAMPLE_ONT_DATASET_BILINGUAL,
            SAMPLE_ONT_DATASET_NO_TRANSLATION,
        ],
    },
}

# Sample Ontario CKAN package_show response
SAMPLE_PACKAGE_SHOW_RESPONSE = {
    "success": True,
    "result": SAMPLE_ONT_DATASET_BILINGUAL,
}

# Sample Ontario CKAN organization_list response
SAMPLE_ORGANIZATION_LIST_RESPONSE = {
    "success": True,
    "result": [
        {
            "id": "org-001",
            "name": "finance",
            "title": "Finance",
            "description": "Ministry of Finance.",
            "package_count": 42,
        },
        {
            "id": "org-002",
            "name": "health",
            "title": "Health",
            "description": "Ministry of Health.",
            "package_count": 115,
        },
    ],
}

# Sample Ontario CKAN resource_show response
SAMPLE_RESOURCE_SHOW_RESPONSE = {
    "success": True,
    "result": {
        "id": "31376797-1e4c-4426-ba75-0d93f4bb9f45",
        "name": "ontario_mof_population_projections_for_2024-2051.xlsx",
        "format": "XLSX",
        "size": 244000,
        "url": "https://data.ontario.ca/dataset/f52a6457-fb37-4267-acde-11a1e57c4dc8/resource/31376797-1e4c-4426-ba75-0d93f4bb9f45/download/ontario_mof_population_projections_for_2024-2051.xlsx",
        "description": "Population projections XLSX file.",
    },
}

# Sample Ontario CKAN package_search with rows=0 for count
SAMPLE_DATASET_COUNT_RESPONSE = {
    "success": True,
    "result": {
        "count": 2946,
        "results": [],
    },
}

# Sample population projection rows (as returned by fetch_and_parse)
SAMPLE_POPULATION_ROWS = [
    {"geography": "Ontario", "year": 2024, "population": 15000000},
    {"geography": "Toronto", "year": 2024, "population": 3000000},
    {"geography": "Ottawa", "year": 2025, "population": 1100000},
]


def make_mock_response(data: dict) -> MagicMock:
    """Create a mock httpx response with the given JSON data."""
    mock = MagicMock()
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


@pytest.fixture
def sample_dataset_bilingual():
    """Sample Ontario CKAN dataset with bilingual translations."""
    return SAMPLE_ONT_DATASET_BILINGUAL


@pytest.fixture
def sample_dataset_no_translation():
    """Sample Ontario CKAN dataset without translation fields."""
    return SAMPLE_ONT_DATASET_NO_TRANSLATION


@pytest.fixture
def sample_package_search():
    """Sample package_search API response."""
    return SAMPLE_PACKAGE_SEARCH_RESPONSE


@pytest.fixture
def sample_package_show():
    """Sample package_show API response."""
    return SAMPLE_PACKAGE_SHOW_RESPONSE


@pytest.fixture
def sample_organization_list():
    """Sample organization_list API response."""
    return SAMPLE_ORGANIZATION_LIST_RESPONSE


@pytest.fixture
def sample_resource_show():
    """Sample resource_show API response."""
    return SAMPLE_RESOURCE_SHOW_RESPONSE


@pytest.fixture
def sample_dataset_count():
    """Sample package_search?rows=0 response for count."""
    return SAMPLE_DATASET_COUNT_RESPONSE


@pytest.fixture
def sample_population_rows():
    """Sample population projection rows."""
    return SAMPLE_POPULATION_ROWS


@pytest.fixture(autouse=False)
async def reset_cache():
    """Clear aiocache between tests to avoid cross-test contamination."""
    from aiocache import SimpleMemoryCache
    cache = SimpleMemoryCache()
    await cache.clear()
    yield
    await cache.clear()
