"""Test fixtures for Bank of Canada client tests."""

import pytest
from unittest.mock import MagicMock


# Sample Valet API observations response (FX rates)
SAMPLE_FX_OBSERVATIONS = {
    "seriesDetail": {
        "FXUSDCAD": {
            "label": "USD/CAD",
            "description": "US dollar to Canadian dollar daily exchange rate",
            "link": "/valet/series/FXUSDCAD/json",
        }
    },
    "observations": [
        {"d": "2026-04-02", "FXUSDCAD": {"v": "1.3900"}},
        {"d": "2026-04-01", "FXUSDCAD": {"v": "1.3850"}},
        {"d": "2026-03-31", "FXUSDCAD": {"v": None}},
    ],
}

# Sample multi-series observations (group response)
SAMPLE_GROUP_OBSERVATIONS = {
    "seriesDetail": {
        "FXUSDCAD": {
            "label": "USD/CAD",
            "description": "US dollar to Canadian dollar daily exchange rate",
            "link": "/valet/series/FXUSDCAD/json",
        },
        "FXEURCAD": {
            "label": "EUR/CAD",
            "description": "Euro to Canadian dollar daily exchange rate",
            "link": "/valet/series/FXEURCAD/json",
        },
    },
    "observations": [
        {"d": "2026-04-02", "FXUSDCAD": {"v": "1.3900"}, "FXEURCAD": {"v": "1.5200"}},
        {"d": "2026-04-01", "FXUSDCAD": {"v": "1.3850"}, "FXEURCAD": {"v": "1.5180"}},
    ],
}

# Sample /lists/series response
SAMPLE_SERIES_LIST = {
    "series": {
        "FXUSDCAD": {
            "label": "USD/CAD",
            "description": "US dollar to Canadian dollar daily exchange rate",
            "link": "/valet/series/FXUSDCAD/json",
        },
        "FXEURCAD": {
            "label": "EUR/CAD",
            "description": "Euro to Canadian dollar daily exchange rate",
            "link": "/valet/series/FXEURCAD/json",
        },
        "V39079": {
            "label": "Target for the overnight rate",
            "description": "Bank of Canada target for the overnight rate",
            "link": "/valet/series/V39079/json",
        },
    }
}

# Sample /lists/groups response
SAMPLE_GROUPS_LIST = {
    "groups": {
        "FX_RATES_DAILY": {
            "label": "Foreign Exchange Rates Daily",
            "description": "Daily foreign exchange rates published by the Bank of Canada",
            "link": "/valet/observations/group/FX_RATES_DAILY/json",
        },
        "BCPI_MONTHLY": {
            "label": "Bank of Canada Commodity Price Index Monthly",
            "description": "Monthly commodity price index components",
            "link": "/valet/observations/group/BCPI_MONTHLY/json",
        },
    }
}

# Sample /series/FXUSDCAD/json response (note: seriesDetails with trailing S)
SAMPLE_SERIES_METADATA = {
    "seriesDetails": {
        "FXUSDCAD": {
            "label": "USD/CAD",
            "description": "US dollar to Canadian dollar daily exchange rate",
            "link": "/valet/series/FXUSDCAD/json",
        }
    }
}


def make_mock_response(data: dict) -> MagicMock:
    """Create a mock httpx response with the given JSON data."""
    mock = MagicMock()
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


@pytest.fixture
def mock_valet_response():
    """Sample Valet API observations responses for various series types."""
    return {
        "fx": SAMPLE_FX_OBSERVATIONS,
        "group": SAMPLE_GROUP_OBSERVATIONS,
    }


@pytest.fixture
def mock_series_list():
    """Sample /lists/series response."""
    return SAMPLE_SERIES_LIST


@pytest.fixture
def mock_groups_list():
    """Sample /lists/groups response."""
    return SAMPLE_GROUPS_LIST


@pytest.fixture
def mock_series_metadata():
    """Sample /series/FXUSDCAD/json response (uses seriesDetails with trailing S)."""
    return SAMPLE_SERIES_METADATA


@pytest.fixture(autouse=False)
async def reset_cache():
    """Clear aiocache between tests to avoid cross-test contamination."""
    from aiocache import SimpleMemoryCache
    cache = SimpleMemoryCache()
    await cache.clear()
    yield
    await cache.clear()
