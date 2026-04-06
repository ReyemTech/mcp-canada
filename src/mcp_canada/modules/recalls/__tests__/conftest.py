"""Test fixtures for Health Canada Recalls client tests."""

import pytest
from unittest.mock import MagicMock


# Sample recent recalls API response
SAMPLE_RECENT_RECALLS = {
    "warnings": [
        {
            "recallId": "2024-123",
            "title": "Recall of contaminated salad greens",
            "datePublished": "2024-03-01",
            "category": "FOOD",
            "url": "https://healthycanadians.gc.ca/recall/2024-123",
        },
        {
            "recallId": "2024-124",
            "title": "Safety recall for children's toy",
            "datePublished": "2024-03-02",
            "category": "CPS",
            "url": "https://healthycanadians.gc.ca/recall/2024-124",
        },
    ],
    "total": 2,
}

# Sample recall with missing optional fields (edge case)
SAMPLE_RECENT_RECALLS_MISSING_FIELDS = {
    "warnings": [
        {
            "recallId": "2024-125",
            # title missing
            "datePublished": "2024-03-03",
            # category missing
            # url missing
        },
    ],
    "total": 1,
}

# Sample search results response
SAMPLE_SEARCH_RESULTS = {
    "results": [
        {
            "recallId": "2024-200",
            "title": "Food recall - listeria contamination",
            "datePublished": "2024-02-15",
            "category": "FOOD",
            "url": "https://healthycanadians.gc.ca/recall/2024-200",
        },
    ],
    "total": 1,
}

# Sample recall detail response (full fields)
SAMPLE_RECALL_DETAIL = {
    "recallId": "2024-123",
    "title": "Recall of contaminated salad greens",
    "datePublished": "2024-03-01",
    "category": "FOOD",
    "url": "https://healthycanadians.gc.ca/recall/2024-123",
    "affectedProducts": [
        {"name": "Spring Mix", "upc": "012345678901", "size": "142g"},
    ],
    "correctiveAction": "Stop using and dispose of recalled product.",
    "audience": "General Public",
    "summary": "Health Canada is warning consumers not to consume recalled salad greens.",
    "images": [
        {"url": "https://healthycanadians.gc.ca/images/2024-123.jpg", "alt": "Product image"},
    ],
}

# Sample recall detail with missing optional fields (edge case)
SAMPLE_RECALL_DETAIL_MISSING_FIELDS = {
    "recallId": "2024-124",
    "title": "Partial data recall",
    # datePublished missing
    # category missing
    # url missing
    # affectedProducts missing
    # correctiveAction missing
    # audience missing
    # summary missing
    # images missing
}


def make_mock_response(data: dict) -> MagicMock:
    """Create a mock httpx response with the given JSON data."""
    mock = MagicMock()
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


@pytest.fixture
def sample_recent_recalls():
    """Sample recent recalls API response with 2 records."""
    return SAMPLE_RECENT_RECALLS


@pytest.fixture
def sample_recent_recalls_missing_fields():
    """Sample recent recalls response with missing optional fields (edge case)."""
    return SAMPLE_RECENT_RECALLS_MISSING_FIELDS


@pytest.fixture
def sample_search_results():
    """Sample recall search results response."""
    return SAMPLE_SEARCH_RESULTS


@pytest.fixture
def sample_recall_detail():
    """Sample full recall detail with all fields populated."""
    return SAMPLE_RECALL_DETAIL


@pytest.fixture
def sample_recall_detail_missing_fields():
    """Sample recall detail with missing optional fields (edge case)."""
    return SAMPLE_RECALL_DETAIL_MISSING_FIELDS


@pytest.fixture(autouse=False)
async def reset_cache():
    """Clear aiocache between tests to avoid cross-test contamination."""
    from aiocache import SimpleMemoryCache
    cache = SimpleMemoryCache()
    await cache.clear()
    yield
    await cache.clear()
