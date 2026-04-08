"""Fixtures for IRCC module unit tests."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def mock_fetch_and_parse():
    """Patch fetch_and_parse used by IRCC client functions.

    Returns sample data: ([{"year": 2024, "value": 100}], False)
    """
    with patch(
        "mcp_canada.modules.ircc.client.fetch_and_parse",
        new_callable=AsyncMock,
        return_value=([{"year": 2024, "value": 100}], False),
    ) as mock:
        yield mock
