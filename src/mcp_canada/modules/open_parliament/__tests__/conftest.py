"""Test fixtures for Open Parliament client tests."""

import pytest
from unittest.mock import MagicMock


# Sample paginated bills response
SAMPLE_BILLS_RESPONSE = {
    "objects": [
        {
            "number": "C-11",
            "name": {"en": "Online Streaming Act"},
            "session": "44-1",
            "introduced": "2022-02-02",
            "sponsor_politician_url": "/politicians/trudeau/",
            "status": {"en": "Royal Assent"},
            "law": True,
        },
        {
            "number": "C-18",
            "name": {"en": "Online News Act"},
            "session": "44-1",
            "introduced": "2022-04-05",
            "sponsor_politician_url": "/politicians/heritage-minister/",
            "status": {"en": "Royal Assent"},
            "law": True,
        },
    ],
    "pagination": {"next_url": None, "previous_url": None},
}

# Sample bill with missing optional fields (graceful degradation test)
SAMPLE_BILLS_MISSING_FIELDS = {
    "objects": [
        {
            "number": "S-1",
            # Missing: name, session, introduced, sponsor, status, law
        }
    ],
    "pagination": {"next_url": None},
}

# Sample bill detail response
SAMPLE_BILL_DETAIL = {
    "number": "C-11",
    "name": {"en": "Online Streaming Act"},
    "session": "44-1",
    "introduced": "2022-02-02",
    "sponsor_politician_url": "/politicians/trudeau/",
    "status": {"en": "Royal Assent"},
    "law": True,
    "vote_urls": ["/votes/44-1/148/"],
    "text_url": "/bills/44-1/C-11/text/",
    "summary": "An act to amend the Broadcasting Act...",
}

# Sample politicians response
SAMPLE_POLITICIANS_RESPONSE = {
    "objects": [
        {
            "name": "Justin Trudeau",
            "current_party": {"short_name": {"en": "Liberal"}},
            "riding": {"name": {"en": "Papineau"}},
            "province": "QC",
            "current": True,
            "url": "/politicians/trudeau/",
        },
        {
            "name": "Pierre Poilievre",
            "current_party": {"short_name": {"en": "Conservative"}},
            "riding": {"name": {"en": "Carleton"}},
            "province": "ON",
            "current": True,
            "url": "/politicians/pierre-poilievre/",
        },
    ],
    "pagination": {"next_url": None},
}

# Sample politician with missing fields
SAMPLE_POLITICIANS_MISSING_FIELDS = {
    "objects": [
        {
            "name": "Unknown MP",
            # Missing: current_party, riding, province, current, url
        }
    ],
    "pagination": {"next_url": None},
}

# Sample votes response
SAMPLE_VOTES_RESPONSE = {
    "objects": [
        {
            "number": 148,
            "date": "2023-03-28",
            "result": "Passed",
            "bill_url": "/bills/44-1/C-11/",
            "yea_total": 204,
            "nay_total": 117,
            "paired_total": 0,
        }
    ],
    "pagination": {"next_url": None},
}

# Sample debates response
SAMPLE_DEBATES_RESPONSE = {
    "objects": [
        {
            "date": "2023-03-28",
            "politician_url": "/politicians/trudeau/",
            "content_en": "Mr. Speaker, this bill...",
            "content_fr": "Monsieur le Président, ce projet de loi...",
            "url": "/debates/2023-03-28/en/",
        }
    ],
    "pagination": {"next_url": None},
}

# Sample Hansard search response
SAMPLE_HANSARD_SEARCH = {
    "objects": [
        {
            "politician_url": "/politicians/trudeau/",
            "content": "We are investing in...",
            "date": "2023-03-28",
            "url": "/debates/2023-03-28/en/",
        }
    ],
    "pagination": {"next_url": None},
}


def make_mock_response(data: dict) -> MagicMock:
    """Create a mock httpx response with the given JSON data."""
    mock = MagicMock()
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


@pytest.fixture
def mock_bills_response():
    return SAMPLE_BILLS_RESPONSE


@pytest.fixture
def mock_bill_detail():
    return SAMPLE_BILL_DETAIL


@pytest.fixture
def mock_politicians_response():
    return SAMPLE_POLITICIANS_RESPONSE


@pytest.fixture
def mock_votes_response():
    return SAMPLE_VOTES_RESPONSE


@pytest.fixture
def mock_debates_response():
    return SAMPLE_DEBATES_RESPONSE


@pytest.fixture
def mock_hansard_search():
    return SAMPLE_HANSARD_SEARCH


@pytest.fixture(autouse=False)
async def reset_cache():
    """Clear aiocache between tests to avoid cross-test contamination."""
    from aiocache import SimpleMemoryCache
    cache = SimpleMemoryCache()
    await cache.clear()
    yield
    await cache.clear()
