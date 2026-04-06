"""Test fixtures for Drug Product Database client tests."""

import pytest
from unittest.mock import MagicMock


# Sample drug search response from /drugproduct/
SAMPLE_DRUG_SEARCH = [
    {
        "drug_code": 12345,
        "brand_name": "TYLENOL",
        "din": "00559407",
        "company_name": "JOHNSON & JOHNSON INC",
        "descriptor": None,
        "class_name": "Human",
        "number_of_ais": 1,
        "ai_group_no": "0100",
    },
    {
        "drug_code": 67890,
        "brand_name": "ADVIL",
        "din": "00312150",
        "company_name": "PFIZER CANADA INC",
        "descriptor": None,
        "class_name": "Human",
        "number_of_ais": 1,
        "ai_group_no": "0100",
    },
]

# Sample active ingredients response from /activeingredient/?id=12345
SAMPLE_INGREDIENTS = [
    {
        "ingredient_name": "ACETAMINOPHEN",
        "strength": "500",
        "strength_unit": "MG",
        "dosage_value": "1",
        "dosage_unit": "TABLET",
    }
]

# Sample routes response from /route/?id=12345
SAMPLE_ROUTES = [
    {
        "route_of_administration": "ORAL",
    }
]

# Sample schedule response from /schedule/?id=12345
SAMPLE_SCHEDULE = [
    {
        "schedule_name": "OTC",
    }
]

# Sample therapeutic class response from /therapeuticclass/?id=12345
SAMPLE_THERAPEUTIC_CLASS = [
    {
        "tc_atc_number": "N02BE01",
        "tc_atc": "Anilides",
        "tc_ahfs_number": "28:08.92",
        "tc_ahfs": "ANALGESICS AND ANTIPYRETICS, MISC.",
    }
]

# Sample status response from /status/?id=12345
SAMPLE_STATUS = [
    {
        "status": "MARKETED",
        "history_date": "1993-02-04",
        "lot_number": None,
        "expiration_date": None,
    }
]

# Sample company response from /company/?companyname=johnson
SAMPLE_COMPANIES = [
    {
        "company_code": 100,
        "company_name": "JOHNSON & JOHNSON INC",
        "company_type": "Owner",
        "city": "MARKHAM",
        "province": "ONTARIO",
        "country": "CANADA",
    }
]

# Combined drug details response (flat sections dict)
SAMPLE_DRUG_DETAILS = {
    "ingredients": SAMPLE_INGREDIENTS,
    "routes": SAMPLE_ROUTES,
    "schedule": SAMPLE_SCHEDULE,
    "therapeutic_class": SAMPLE_THERAPEUTIC_CLASS,
    "status": SAMPLE_STATUS,
}


def make_mock_response(data: list | dict) -> MagicMock:
    """Create a mock httpx response with the given JSON data."""
    mock = MagicMock()
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


@pytest.fixture
def sample_drug_search():
    """Sample drug search response."""
    return SAMPLE_DRUG_SEARCH


@pytest.fixture
def sample_drug_details():
    """Sample combined drug details response (flat sections)."""
    return SAMPLE_DRUG_DETAILS


@pytest.fixture
def sample_ingredients():
    return SAMPLE_INGREDIENTS


@pytest.fixture
def sample_routes():
    return SAMPLE_ROUTES


@pytest.fixture
def sample_schedule():
    return SAMPLE_SCHEDULE


@pytest.fixture
def sample_therapeutic_class():
    return SAMPLE_THERAPEUTIC_CLASS


@pytest.fixture
def sample_status():
    return SAMPLE_STATUS


@pytest.fixture
def sample_companies():
    return SAMPLE_COMPANIES


@pytest.fixture(autouse=False)
async def reset_cache():
    """Clear aiocache between tests to avoid cross-test contamination."""
    from aiocache import SimpleMemoryCache
    cache = SimpleMemoryCache()
    await cache.clear()
    yield
    await cache.clear()
