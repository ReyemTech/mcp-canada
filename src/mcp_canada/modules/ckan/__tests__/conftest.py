"""Test fixtures for CKAN Open Data client tests."""

import pytest
from unittest.mock import MagicMock


# Long description for truncation testing (>500 chars)
LONG_DESCRIPTION = (
    "This dataset contains detailed information about Canadian government spending "
    "programs across all federal departments. It includes breakdowns by category, "
    "region, and fiscal year. The data is updated quarterly and provides insights "
    "into how public funds are allocated across healthcare, infrastructure, defence, "
    "education, environmental programs, and social services. Additional context about "
    "program objectives, outcomes, and performance metrics is also available through "
    "linked resources and supplementary documentation found in the related datasets."
)

# Short description that should NOT be truncated
SHORT_DESCRIPTION = "Government spending data by department and category."

# Sample bilingual CKAN dataset with title_translated/notes_translated
SAMPLE_CKAN_DATASET_BILINGUAL = {
    "id": "abc123",
    "name": "government-spending-data",
    "title": "Government Spending Data",
    "title_translated": {
        "en": "Government Spending Data",
        "fr": "Données de dépenses gouvernementales",
    },
    "notes_translated": {
        "en": LONG_DESCRIPTION,
        "fr": "Description en français des dépenses gouvernementales.",
    },
    "organization": {"title": "Treasury Board of Canada"},
    "num_resources": 3,
    "tags": [{"name": "spending"}, {"name": "budget"}],
    "resources": [
        {
            "id": f"res-{i:03d}",
            "name": f"Resource {i}",
            "format": "CSV",
            "size": 1024 * i,
            "url": f"https://open.canada.ca/resource/{i}",
            "description": f"Resource {i} description",
        }
        for i in range(1, 16)  # 15 resources to test capping at 10
    ],
    "metadata_created": "2023-01-15T10:00:00.000000",
    "metadata_modified": "2024-06-20T14:30:00.000000",
}

# Sample CKAN dataset without translations (fallback test)
SAMPLE_CKAN_DATASET_NO_TRANSLATION = {
    "id": "def456",
    "name": "simple-dataset",
    "title": "Simple Dataset",
    "organization": {"title": "Statistics Canada"},
    "num_resources": 1,
    "tags": [],
    "resources": [
        {
            "id": "res-001",
            "name": "Main CSV",
            "format": "CSV",
            "size": 2048,
            "url": "https://open.canada.ca/resource/main.csv",
        }
    ],
    "metadata_created": "2022-05-10T08:00:00.000000",
    "metadata_modified": "2023-11-01T12:00:00.000000",
}

# Sample CKAN package_search response
SAMPLE_PACKAGE_SEARCH_RESPONSE = {
    "success": True,
    "result": {
        "count": 2,
        "results": [
            SAMPLE_CKAN_DATASET_BILINGUAL,
            SAMPLE_CKAN_DATASET_NO_TRANSLATION,
        ],
    },
}

# Sample CKAN package_show response
SAMPLE_PACKAGE_SHOW_RESPONSE = {
    "success": True,
    "result": SAMPLE_CKAN_DATASET_BILINGUAL,
}

# Sample CKAN organization_list response
SAMPLE_ORGANIZATION_LIST_RESPONSE = {
    "success": True,
    "result": [
        {
            "id": "org-001",
            "name": "treasury-board",
            "title": "Treasury Board of Canada",
            "description": "Central agency responsible for financial management.",
            "package_count": 150,
        },
        {
            "id": "org-002",
            "name": "statistics-canada",
            "title": "Statistics Canada",
            "description": "National statistical agency.",
            "package_count": 3200,
        },
    ],
}

# Sample CKAN group_list response
SAMPLE_GROUP_LIST_RESPONSE = {
    "success": True,
    "result": [
        {
            "id": "grp-001",
            "name": "environment",
            "title": "Environment",
            "description": "Environmental datasets.",
            "package_count": 450,
        },
        {
            "id": "grp-002",
            "name": "economy",
            "title": "Economy",
            "description": "Economic datasets.",
            "package_count": 800,
        },
    ],
}

# Sample CKAN resource_show response
SAMPLE_RESOURCE_SHOW_RESPONSE = {
    "success": True,
    "result": {
        "id": "res-001",
        "name": "Main CSV File",
        "format": "CSV",
        "size": 204800,
        "url": "https://open.canada.ca/data/resource/main.csv",
        "description": "Primary data file in CSV format.",
    },
}

# Sample CKAN package_search with rows=0 for count
SAMPLE_DATASET_COUNT_RESPONSE = {
    "success": True,
    "result": {
        "count": 83421,
        "results": [],
    },
}


def make_mock_response(data: dict) -> MagicMock:
    """Create a mock httpx response with the given JSON data."""
    mock = MagicMock()
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


@pytest.fixture
def sample_dataset_bilingual():
    """Sample CKAN dataset with bilingual translations."""
    return SAMPLE_CKAN_DATASET_BILINGUAL


@pytest.fixture
def sample_dataset_no_translation():
    """Sample CKAN dataset without translation fields."""
    return SAMPLE_CKAN_DATASET_NO_TRANSLATION


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
def sample_group_list():
    """Sample group_list API response."""
    return SAMPLE_GROUP_LIST_RESPONSE


@pytest.fixture
def sample_resource_show():
    """Sample resource_show API response."""
    return SAMPLE_RESOURCE_SHOW_RESPONSE


@pytest.fixture
def sample_dataset_count():
    """Sample package_search?rows=0 response for count."""
    return SAMPLE_DATASET_COUNT_RESPONSE


@pytest.fixture(autouse=False)
async def reset_cache():
    """Clear aiocache between tests to avoid cross-test contamination."""
    from aiocache import SimpleMemoryCache
    cache = SimpleMemoryCache()
    await cache.clear()
    yield
    await cache.clear()
