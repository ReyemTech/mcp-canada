"""Saskatchewan tool unit tests.

Plans 02-05 fill tool test bodies. Plan 07 fills the parametrized envelope/lang tests.
Wave 0 defines placeholder classes for all 14 tools (5 discovery + 9 curated)
so downstream plans reference specific node IDs.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from mcp_canada.modules.saskatchewan import tools


# ---------------------------------------------------------------------------
# Discovery tools (Plan 02)
# ---------------------------------------------------------------------------


class TestSaskSearchDatasetsTool:
    """saskatchewan_search_datasets tool tests.

    Plan 02 fills: _meta envelope; error paths (Hub HTTP error → UPSTREAM_ERROR);
    lang parameter passes through to envelope.
    """

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """saskatchewan_search_datasets returns _meta envelope with source api."""
        import json
        payload = {"results": [{"id": "x", "title": "Crop Yields"}], "total": 1}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_search_datasets(query="crops")
        data = json.loads(result) if isinstance(result, str) else result
        assert "_meta" in data, f"Expected '_meta' in result, got keys: {list(data.keys())}"
        assert data["_meta"]["source"]["api"] == "saskatchewan-geohub"

    @pytest.mark.asyncio
    async def test_returns_results_and_total(self):
        """saskatchewan_search_datasets includes results list and total in response data."""
        import json
        payload = {"results": [{"id": "x", "title": "Crop Yields"}], "total": 181}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_search_datasets(query="crops")
        data = json.loads(result) if isinstance(result, str) else result
        # make_response wraps payload under "data" key
        assert data["data"]["results"] == payload["results"]
        assert data["data"]["total"] == 181

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_hub_exception(self):
        """saskatchewan_search_datasets returns UPSTREAM_ERROR when client raises."""
        import json
        import httpx
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "500",
                request=httpx.Request("GET", "https://geohub.saskatchewan.ca"),
                response=httpx.Response(500),
            ),
        ):
            result = await tools.saskatchewan_search_datasets(query="crops")
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data
        assert data["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """saskatchewan_search_datasets passes lang='fr' through to _meta envelope."""
        import json
        payload = {"results": [], "total": 0}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_search_datasets",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_search_datasets(query="cultures", lang="fr")
        data = json.loads(result) if isinstance(result, str) else result
        assert data["_meta"]["lang"] == "fr"


class TestSaskGetDatasetDetailsTool:
    """saskatchewan_get_dataset_details tool tests.

    Plan 02 fills.
    """

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """saskatchewan_get_dataset_details returns _meta envelope."""
        import json
        payload = {
            "details": {
                "id": "abc123",
                "title": "Crop Yields",
                "feature_server_url": "https://services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Crop/FeatureServer",
                "download_urls": [],
            }
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_dataset_details",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_dataset_details(dataset_id="abc123")
        data = json.loads(result) if isinstance(result, str) else result
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "saskatchewan-geohub"

    @pytest.mark.asyncio
    async def test_returns_not_found_on_value_error(self):
        """saskatchewan_get_dataset_details returns NOT_FOUND when client raises ValueError."""
        import json
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_dataset_details",
            new_callable=AsyncMock,
            side_effect=ValueError("Dataset not found: nonexistent-id"),
        ):
            result = await tools.saskatchewan_get_dataset_details(dataset_id="nonexistent-id")
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data
        assert data["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """saskatchewan_get_dataset_details passes lang='fr' through to _meta."""
        import json
        payload = {
            "details": {
                "id": "abc123",
                "title": "Données",
                "feature_server_url": None,
                "download_urls": [],
            }
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_dataset_details",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_dataset_details(dataset_id="abc123", lang="fr")
        data = json.loads(result) if isinstance(result, str) else result
        assert data["_meta"]["lang"] == "fr"


class TestSaskQueryDatasetTool:
    """saskatchewan_query_dataset tool tests.

    Plan 02 fills.
    """

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """saskatchewan_query_dataset returns _meta envelope on success."""
        import json
        payload = {
            "data": [{"Region": "Provincial", "HRSW": 43.0}],
            "url": "https://services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Crop/FeatureServer",
            "rows": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_query_dataset",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_query_dataset(
                dataset_id="https://services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Crop/FeatureServer"
            )
        data = json.loads(result) if isinstance(result, str) else result
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "saskatchewan-geohub"

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """saskatchewan_query_dataset returns UPSTREAM_ERROR when client raises."""
        import json
        import httpx
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_query_dataset",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "500",
                request=httpx.Request("GET", "https://geohub.saskatchewan.ca"),
                response=httpx.Response(500),
            ),
        ):
            result = await tools.saskatchewan_query_dataset(
                dataset_id="https://services3.arcgis.com/zcv98lgAl8xQ04cW/Crop/FeatureServer"
            )
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """saskatchewan_query_dataset passes lang='fr' through to envelope."""
        import json
        payload = {"data": [], "url": "https://example.com/FeatureServer", "rows": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_query_dataset",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_query_dataset(
                dataset_id="https://example.com/FeatureServer",
                lang="fr",
            )
        data = json.loads(result) if isinstance(result, str) else result
        assert data["_meta"]["lang"] == "fr"


class TestSaskListOrganizationsTool:
    """saskatchewan_list_organizations tool tests.

    Plan 02 fills.
    """

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """saskatchewan_list_organizations returns _meta envelope with organizations list."""
        import json
        payload = {"organizations": ["Saskatchewan_Government", "Water Security Agency"]}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_organizations",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_list_organizations()
        data = json.loads(result) if isinstance(result, str) else result
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "saskatchewan-geohub"
        assert "organizations" in data["data"]

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """saskatchewan_list_organizations returns UPSTREAM_ERROR when client raises."""
        import json
        import httpx
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_organizations",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "500",
                request=httpx.Request("GET", "https://geohub.saskatchewan.ca"),
                response=httpx.Response(500),
            ),
        ):
            result = await tools.saskatchewan_list_organizations()
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data
        assert data["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """saskatchewan_list_organizations passes lang='fr' through to envelope."""
        import json
        payload = {"organizations": ["Saskatchewan_Gouvernement"]}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_organizations",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_list_organizations(lang="fr")
        data = json.loads(result) if isinstance(result, str) else result
        assert data["_meta"]["lang"] == "fr"


class TestSaskListCategoriesTool:
    """saskatchewan_list_categories tool tests.

    Plan 02 fills.
    """

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """saskatchewan_list_categories returns _meta envelope with categories list."""
        import json
        payload = {"categories": ["/Categories/Agriculture", "/Categories/Environment"]}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_categories",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_list_categories()
        data = json.loads(result) if isinstance(result, str) else result
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "saskatchewan-geohub"
        assert "categories" in data["data"]

    @pytest.mark.asyncio
    async def test_returns_upstream_error_on_exception(self):
        """saskatchewan_list_categories returns UPSTREAM_ERROR when client raises."""
        import json
        import httpx
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_categories",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "500",
                request=httpx.Request("GET", "https://geohub.saskatchewan.ca"),
                response=httpx.Response(500),
            ),
        ):
            result = await tools.saskatchewan_list_categories()
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data
        assert data["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """saskatchewan_list_categories passes lang='fr' through to envelope."""
        import json
        payload = {"categories": ["/Categories/Agriculture"]}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_categories",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_list_categories(lang="fr")
        data = json.loads(result) if isinstance(result, str) else result
        assert data["_meta"]["lang"] == "fr"


# ---------------------------------------------------------------------------
# Agriculture + Mining tools (Plan 03)
# ---------------------------------------------------------------------------


class TestSaskGetCropYieldsTool:
    """saskatchewan_get_crop_yields tool tests.

    Plan 03 fills: valid region values; invalid region → INVALID_INPUT with valid= list.
    """

    pass


class TestSaskGetGrainElevatorsTool:
    """saskatchewan_get_grain_elevators tool tests.

    Plan 03 fills.
    """

    pass


class TestSaskGetMineralMinesTool:
    """saskatchewan_get_mineral_mines tool tests.

    Plan 03 fills: invalid mineral → INVALID_INPUT with valid=['potash','uranium','helium','coal'].
    """

    pass


# ---------------------------------------------------------------------------
# Environment tools (Plan 04)
# ---------------------------------------------------------------------------


class TestSaskGetFireBansTool:
    """saskatchewan_get_fire_bans tool tests.

    Plan 04 fills: empty features=[] → make_response (not make_error);
    invalid ban_scope → INVALID_INPUT.
    """

    pass


class TestSaskGetHistoricWildfiresTool:
    """saskatchewan_get_historic_wildfires tool tests.

    Plan 04 fills.
    """

    pass


class TestSaskGetAirQualityTool:
    """saskatchewan_get_air_quality tool tests.

    Plan 04 fills: invalid community → INVALID_INPUT with valid=AIR_QUALITY_COMMUNITIES.
    """

    pass


# ---------------------------------------------------------------------------
# Water / WSA tools (Plan 05)
# ---------------------------------------------------------------------------


class TestSaskGetWSAStationsTool:
    """saskatchewan_get_wsa_stations tool tests.

    Plan 05 fills.
    """

    pass


class TestSaskGetWSAReservoirsTool:
    """saskatchewan_get_wsa_reservoirs tool tests.

    Plan 05 fills.
    """

    pass


# ---------------------------------------------------------------------------
# Cross-cutting: envelope + lang parameter (Plan 07)
# ---------------------------------------------------------------------------


class TestSaskEnvelopes:
    """Parametrized: all 14 tools return _meta envelope on success.

    Plan 07 fills: parametrize over ALL_SASKATCHEWAN_TOOLS list; mock client layer;
    assert "_meta" in result and result["_meta"]["source"]["api"] expected.
    """

    pass


class TestSaskLangParam:
    """Parametrized: all 14 tools accept lang='fr' and pass through to envelope.

    Plan 07 fills: parametrize over ALL_SASKATCHEWAN_TOOLS; assert _meta.lang == 'fr'.
    """

    pass
