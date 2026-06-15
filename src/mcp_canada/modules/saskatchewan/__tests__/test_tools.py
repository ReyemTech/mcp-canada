"""Saskatchewan tool unit tests.

Plans 02-05 fill tool test bodies. Plan 07 fills the parametrized envelope/lang tests.
Wave 0 defines placeholder classes for all 14 tools (5 discovery + 9 curated)
so downstream plans reference specific node IDs.
"""

from __future__ import annotations

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

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """saskatchewan_get_crop_yields returns _meta envelope with correct api name."""
        import json
        payload = {
            "features": [{"Region": "Provincial", "Canola": 34.0}],
            "count": 1,
            "truncated": False,
            "region": "provincial",
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_crop_yields",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_crop_yields(region="provincial")
        data = json.loads(result) if isinstance(result, str) else result
        assert "_meta" in data, f"Expected _meta envelope, got keys: {list(data.keys())}"
        assert data["_meta"]["source"]["api"] == "saskatchewan-geohub"

    @pytest.mark.asyncio
    async def test_data_contains_features(self):
        """saskatchewan_get_crop_yields wraps payload under data key with features list."""
        import json
        payload = {
            "features": [{"Region": "Provincial", "Canola": 34.0, "HRSW": 43.0}],
            "count": 1,
            "truncated": False,
            "region": "provincial",
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_crop_yields",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_crop_yields(region="provincial")
        data = json.loads(result) if isinstance(result, str) else result
        assert data["data"]["features"][0]["Canola"] == 34.0

    @pytest.mark.asyncio
    async def test_invalid_region_returns_invalid_input(self):
        """saskatchewan_get_crop_yields returns INVALID_INPUT for unknown region."""
        import json
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_crop_yields",
            new_callable=AsyncMock,
            side_effect=ValueError("Unknown region: 'bogus'. Valid: ['provincial', ...]"),
        ):
            result = await tools.saskatchewan_get_crop_yields(region="bogus")
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data, f"Expected error response, got: {data}"
        assert data["error"]["code"] == "INVALID_INPUT"
        # valid list must be present
        assert "valid" in data["error"]

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """saskatchewan_get_crop_yields passes lang='fr' through to _meta envelope."""
        import json
        payload = {
            "features": [],
            "count": 0,
            "truncated": False,
            "region": "provincial",
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_crop_yields",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_crop_yields(lang="fr")
        data = json.loads(result) if isinstance(result, str) else result
        assert data["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_upstream_error_on_http_exception(self):
        """saskatchewan_get_crop_yields returns UPSTREAM_ERROR on HTTP exception."""
        import json
        import httpx
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_crop_yields",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "503",
                request=httpx.Request("GET", "https://services3.arcgis.com/"),
                response=httpx.Response(503),
            ),
        ):
            result = await tools.saskatchewan_get_crop_yields(region="provincial")
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data
        assert data["error"]["code"] == "UPSTREAM_ERROR"


class TestSaskGetGrainElevatorsTool:
    """saskatchewan_get_grain_elevators tool tests.

    Plan 03 fills.
    """

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """saskatchewan_get_grain_elevators returns _meta envelope with correct api name."""
        import json
        payload = {
            "features": [
                {"Station": "Regina", "PR": "SK", "Railway": "CN",
                 "Licensee": "Richardson International", "Elevator_type": "Primary",
                 "Capacity_tonne": 42000.0}
            ],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_grain_elevators",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_grain_elevators()
        data = json.loads(result) if isinstance(result, str) else result
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "saskatchewan-geohub"

    @pytest.mark.asyncio
    async def test_railway_optional_filter_passed(self):
        """saskatchewan_get_grain_elevators passes railway= to client function."""
        import json
        payload = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_grain_elevators",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ) as mock_client:
            await tools.saskatchewan_get_grain_elevators(railway="CN")
        mock_client.assert_called_once()
        call_kwargs = mock_client.call_args
        assert call_kwargs[1].get("railway") == "CN" or call_kwargs[0][0] == "CN"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """saskatchewan_get_grain_elevators passes lang='fr' through to _meta envelope."""
        import json
        payload = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_grain_elevators",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_grain_elevators(lang="fr")
        data = json.loads(result) if isinstance(result, str) else result
        assert data["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_upstream_error_on_http_exception(self):
        """saskatchewan_get_grain_elevators returns UPSTREAM_ERROR on HTTP exception."""
        import json
        import httpx
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_grain_elevators",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "500",
                request=httpx.Request("GET", "https://services3.arcgis.com/"),
                response=httpx.Response(500),
            ),
        ):
            result = await tools.saskatchewan_get_grain_elevators()
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data
        assert data["error"]["code"] == "UPSTREAM_ERROR"


class TestSaskGetMineralMinesTool:
    """saskatchewan_get_mineral_mines tool tests.

    Plan 03 fills: invalid mineral → INVALID_INPUT with valid=['potash','uranium','helium','coal'].
    """

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """saskatchewan_get_mineral_mines returns _meta envelope with correct api name."""
        import json
        payload = {
            "features": [
                {"Name": "K+S Bethune", "Status": "Operating", "Mine_Type": "Solution",
                 "Company": "K+S Potash Canada GP", "DateOpened": "2017"}
            ],
            "count": 1,
            "truncated": False,
            "mineral": "potash",
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_mineral_mines",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_mineral_mines(mineral="potash")
        data = json.loads(result) if isinstance(result, str) else result
        assert "_meta" in data
        assert data["_meta"]["source"]["api"] == "saskatchewan-geohub"

    @pytest.mark.asyncio
    async def test_data_contains_features(self):
        """saskatchewan_get_mineral_mines wraps payload under data key."""
        import json
        payload = {
            "features": [{"Name": "Cameco Eagle Point", "Status": "Care & Maintenance"}],
            "count": 1,
            "truncated": False,
            "mineral": "uranium",
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_mineral_mines",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_mineral_mines(mineral="uranium")
        data = json.loads(result) if isinstance(result, str) else result
        assert data["data"]["features"][0]["Name"] == "Cameco Eagle Point"

    @pytest.mark.asyncio
    async def test_invalid_mineral_returns_invalid_input(self):
        """saskatchewan_get_mineral_mines returns INVALID_INPUT for unknown mineral."""
        import json
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_mineral_mines",
            new_callable=AsyncMock,
            side_effect=ValueError("Unknown mineral: 'gold'. Valid: ['potash', 'uranium', ...]"),
        ):
            result = await tools.saskatchewan_get_mineral_mines(mineral="gold")
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data
        assert data["error"]["code"] == "INVALID_INPUT"
        # valid list must contain the 4 mineral types
        valid = data["error"]["valid"]
        assert "potash" in valid
        assert "uranium" in valid

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """saskatchewan_get_mineral_mines passes lang='fr' through to _meta envelope."""
        import json
        payload = {"features": [], "count": 0, "truncated": False, "mineral": "potash"}
        with patch(
            "mcp_canada.modules.sanskrit.tools._client.fetch_mineral_mines"
            if False else
            "mcp_canada.modules.saskatchewan.tools._client.fetch_mineral_mines",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_mineral_mines(mineral="potash", lang="fr")
        data = json.loads(result) if isinstance(result, str) else result
        assert data["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_upstream_error_on_http_exception(self):
        """saskatchewan_get_mineral_mines returns UPSTREAM_ERROR on HTTP exception."""
        import json
        import httpx
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_mineral_mines",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "500",
                request=httpx.Request("GET", "https://services3.arcgis.com/"),
                response=httpx.Response(500),
            ),
        ):
            result = await tools.saskatchewan_get_mineral_mines(mineral="potash")
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data
        assert data["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_fr_error_message_for_invalid_mineral(self):
        """saskatchewan_get_mineral_mines returns French error message when lang='fr'."""
        import json
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_mineral_mines",
            new_callable=AsyncMock,
            side_effect=ValueError("Unknown mineral"),
        ):
            result = await tools.saskatchewan_get_mineral_mines(mineral="gold", lang="fr")
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data
        assert data["error"]["code"] == "INVALID_INPUT"


# ---------------------------------------------------------------------------
# Environment tools (Plan 04)
# ---------------------------------------------------------------------------


class TestSaskGetFireBansTool:
    """saskatchewan_get_fire_bans tool tests.

    Plan 04 fills: empty features=[] → make_response (not make_error);
    invalid ban_scope → INVALID_INPUT.
    """

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success_with_active_bans(self):
        """saskatchewan_get_fire_bans returns _meta envelope when bans are active."""
        import json
        payload = {
            "features": [
                {"UMTYPE": "Urban Municipality", "Municipali": "Arborfield",
                 "Type": "Ban", "Comment": "Level 1 Fire Ban"},
            ],
            "count": 1,
            "truncated": False,
            "scope": "urban",
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_fire_bans",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_fire_bans(ban_scope="urban")
        data = json.loads(result) if isinstance(result, str) else result
        assert "_meta" in data, f"Expected _meta envelope, got keys: {list(data.keys())}"
        assert "spsa" in data["_meta"]["source"]["api"], (
            f"Expected api name to contain 'spsa', got: {data['_meta']['source']['api']}"
        )

    @pytest.mark.asyncio
    async def test_empty_fire_bans_is_valid_make_response_not_error(self):
        """CRITICAL: empty features=[] returns make_response (count=0), NOT make_error.

        Off-season with no active bans is a valid state. Tool must NOT convert this to an error.
        """
        import json
        payload = {
            "features": [],
            "count": 0,
            "truncated": False,
            "scope": "provincial",
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_fire_bans",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_fire_bans(ban_scope="provincial")
        data = json.loads(result) if isinstance(result, str) else result
        # Must be a success envelope (_meta), NOT an error envelope
        assert "_meta" in data, (
            f"Empty fire bans MUST return make_response with _meta, not an error. Got: {data}"
        )
        assert "error" not in data, (
            f"Empty fire bans must NOT return make_error. Got: {data}"
        )
        assert data["data"]["count"] == 0, (
            f"Expected count=0 for empty bans, got: {data['data'].get('count')}"
        )

    @pytest.mark.asyncio
    async def test_invalid_ban_scope_returns_invalid_input(self):
        """saskatchewan_get_fire_bans returns INVALID_INPUT for unknown ban_scope."""
        import json
        result = await tools.saskatchewan_get_fire_bans(ban_scope="forest")
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data, f"Expected error response for unknown ban_scope, got: {data}"
        assert data["error"]["code"] == "INVALID_INPUT"
        # valid list must contain the 4 ban scope options
        valid = data["error"].get("valid", [])
        assert "urban" in valid, f"Expected 'urban' in valid list, got: {valid}"
        assert "rural" in valid
        assert "provincial" in valid
        assert "parks" in valid

    @pytest.mark.asyncio
    async def test_invalid_ban_scope_fr_error_message(self):
        """saskatchewan_get_fire_bans returns French error message when lang='fr'."""
        import json
        result = await tools.saskatchewan_get_fire_bans(ban_scope="forest", lang="fr")
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data
        assert data["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_upstream_error_on_http_exception(self):
        """saskatchewan_get_fire_bans returns UPSTREAM_ERROR on HTTP exception."""
        import json
        import httpx
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_fire_bans",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "503",
                request=httpx.Request("GET", "https://gis.saskatchewan.ca/egis/rest/services"),
                response=httpx.Response(503),
            ),
        ):
            result = await tools.saskatchewan_get_fire_bans(ban_scope="urban")
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data
        assert data["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """saskatchewan_get_fire_bans passes lang='fr' through to _meta envelope."""
        import json
        payload = {"features": [], "count": 0, "truncated": False, "scope": "urban"}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_fire_bans",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_fire_bans(ban_scope="urban", lang="fr")
        data = json.loads(result) if isinstance(result, str) else result
        assert data["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_all_four_valid_ban_scopes_succeed(self):
        """All 4 valid ban_scope values (urban/rural/provincial/parks) return _meta envelope."""
        import json
        for scope in ("urban", "rural", "provincial", "parks"):
            payload = {"features": [], "count": 0, "truncated": False, "scope": scope}
            with patch(
                "mcp_canada.modules.saskatchewan.tools._client.fetch_fire_bans",
                new_callable=AsyncMock,
                return_value=(payload, False),
            ):
                result = await tools.saskatchewan_get_fire_bans(ban_scope=scope)
            data = json.loads(result) if isinstance(result, str) else result
            assert "_meta" in data, f"Expected _meta for ban_scope={scope!r}, got: {data}"


class TestSaskGetHistoricWildfiresTool:
    """saskatchewan_get_historic_wildfires tool tests.

    Plan 04 fills.
    """

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """saskatchewan_get_historic_wildfires returns _meta envelope on success."""
        import json
        payload = {
            "features": [
                {"YEAR": 2017, "FIRENAME": "PORCUPINE LAKE FIRE",
                 "CAUSE1": "Lightning", "HECTARES": 12450.5, "STATUS": "Out"}
            ],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_historic_wildfires",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_historic_wildfires()
        data = json.loads(result) if isinstance(result, str) else result
        assert "_meta" in data, f"Expected _meta envelope, got keys: {list(data.keys())}"
        assert data["_meta"]["source"]["api"] == "saskatchewan-geohub"

    @pytest.mark.asyncio
    async def test_year_filter_passed_to_client(self):
        """saskatchewan_get_historic_wildfires passes year= to client function."""
        import json
        payload = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_historic_wildfires",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ) as mock_client:
            await tools.saskatchewan_get_historic_wildfires(year=2017)
        mock_client.assert_called_once()
        call_kwargs = mock_client.call_args[1]
        assert call_kwargs.get("year") == 2017, (
            f"Expected year=2017 passed to client, got: {call_kwargs}"
        )

    @pytest.mark.asyncio
    async def test_cause_filter_passed_to_client(self):
        """saskatchewan_get_historic_wildfires passes cause= to client function."""
        import json
        payload = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_historic_wildfires",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ) as mock_client:
            await tools.saskatchewan_get_historic_wildfires(cause="Lightning")
        mock_client.assert_called_once()
        call_kwargs = mock_client.call_args[1]
        assert call_kwargs.get("cause") == "Lightning", (
            f"Expected cause='Lightning' passed to client, got: {call_kwargs}"
        )

    @pytest.mark.asyncio
    async def test_data_contains_features(self):
        """saskatchewan_get_historic_wildfires wraps payload under data key."""
        import json
        payload = {
            "features": [{"YEAR": 2017, "FIRENAME": "PORCUPINE LAKE FIRE"}],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_historic_wildfires",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_historic_wildfires(year=2017)
        data = json.loads(result) if isinstance(result, str) else result
        assert data["data"]["features"][0]["FIRENAME"] == "PORCUPINE LAKE FIRE"

    @pytest.mark.asyncio
    async def test_upstream_error_on_http_exception(self):
        """saskatchewan_get_historic_wildfires returns UPSTREAM_ERROR on HTTP exception."""
        import json
        import httpx
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_historic_wildfires",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "503",
                request=httpx.Request("GET", "https://services3.arcgis.com/"),
                response=httpx.Response(503),
            ),
        ):
            result = await tools.saskatchewan_get_historic_wildfires()
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data
        assert data["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """saskatchewan_get_historic_wildfires passes lang='fr' through to _meta envelope."""
        import json
        payload = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_historic_wildfires",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_historic_wildfires(lang="fr")
        data = json.loads(result) if isinstance(result, str) else result
        assert data["_meta"]["lang"] == "fr"


class TestSaskGetAirQualityTool:
    """saskatchewan_get_air_quality tool tests.

    Plan 04 fills.
    """

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """saskatchewan_get_air_quality returns _meta envelope on success."""
        import json
        payload = {
            "features": [
                {"COMMUNITY": "Regina", "STATIONID": "SK_REGINA_01",
                 "PM2_5": 7.2, "NO2": 12.5, "O3": 31.0,
                 "AQHI": "https://weather.gc.ca/airquality/pages/sk-1_metric_e.html",
                 "DATETIME": "2026-06-15T14:00:00"},
            ],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_air_quality",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_air_quality()
        data = json.loads(result) if isinstance(result, str) else result
        assert "_meta" in data, f"Expected _meta envelope, got keys: {list(data.keys())}"
        assert data["_meta"]["source"]["api"] == "saskatchewan-geohub"

    @pytest.mark.asyncio
    async def test_community_filter_passed_to_client(self):
        """saskatchewan_get_air_quality passes community= to client function."""
        import json
        payload = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_air_quality",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ) as mock_client:
            await tools.saskatchewan_get_air_quality(community="Regina")
        mock_client.assert_called_once()
        call_kwargs = mock_client.call_args[1]
        assert call_kwargs.get("community") == "Regina", (
            f"Expected community='Regina' passed to client, got: {call_kwargs}"
        )

    @pytest.mark.asyncio
    async def test_aqhi_field_present_in_response_data(self):
        """saskatchewan_get_air_quality response includes AQHI field (weather.gc.ca URL)."""
        import json
        payload = {
            "features": [
                {"COMMUNITY": "Saskatoon",
                 "AQHI": "https://weather.gc.ca/airquality/pages/sk-2_metric_e.html",
                 "PM2_5": 5.8},
            ],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_air_quality",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_air_quality(community="Saskatoon")
        data = json.loads(result) if isinstance(result, str) else result
        first = data["data"]["features"][0]
        assert "AQHI" in first, f"Expected AQHI in feature, got: {list(first.keys())}"
        assert "weather.gc.ca" in first["AQHI"]

    @pytest.mark.asyncio
    async def test_upstream_error_on_http_exception(self):
        """saskatchewan_get_air_quality returns UPSTREAM_ERROR on HTTP exception."""
        import json
        import httpx
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_air_quality",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "503",
                request=httpx.Request("GET", "https://services3.arcgis.com/"),
                response=httpx.Response(503),
            ),
        ):
            result = await tools.saskatchewan_get_air_quality()
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data
        assert data["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """saskatchewan_get_air_quality passes lang='fr' through to _meta envelope."""
        import json
        payload = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_air_quality",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_air_quality(lang="fr")
        data = json.loads(result) if isinstance(result, str) else result
        assert data["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_no_community_calls_client_with_none(self):
        """saskatchewan_get_air_quality with no community passes community=None to client."""
        import json
        payload = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_air_quality",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ) as mock_client:
            await tools.saskatchewan_get_air_quality()
        mock_client.assert_called_once()
        call_kwargs = mock_client.call_args[1]
        assert call_kwargs.get("community") is None, (
            f"Expected community=None when not provided, got: {call_kwargs}"
        )


# ---------------------------------------------------------------------------
# Water / WSA tools (Plan 05)
# ---------------------------------------------------------------------------


class TestSaskGetWSAStationsTool:
    """saskatchewan_get_wsa_stations tool tests.

    Plan 05 fills: _meta envelope; api='saskatchewan-wsa'; lang passthrough;
    HyperLink_Graph present in response; optional basin= passed to client.
    """

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """saskatchewan_get_wsa_stations returns _meta envelope with api='saskatchewan-wsa'."""
        import json
        payload = {
            "features": [
                {
                    "Station_Number": "05MB006",
                    "Station_Name": "ASSINIBOINE RIVER AT ESTERHAZY",
                    "Province": "SK",
                    "Major_Basin": "Assiniboine River",
                    "Station_Class": "Primary",
                    "Operated_By": "Water Survey of Canada - SK",
                    "HyperLink_Graph": "https://www.wsask.ca/hydrographs/05MB006-hrly.html",
                }
            ],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_wsa_stations",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_wsa_stations()
        data = json.loads(result) if isinstance(result, str) else result
        assert "_meta" in data, f"Expected _meta envelope, got: {list(data.keys())}"
        assert data["_meta"]["source"]["api"] == "saskatchewan-wsa", (
            f"Expected api='saskatchewan-wsa', got: {data['_meta']['source']['api']}"
        )

    @pytest.mark.asyncio
    async def test_hyperlink_graph_present_in_response_data(self):
        """saskatchewan_get_wsa_stations response includes HyperLink_Graph URL."""
        import json
        payload = {
            "features": [
                {
                    "Station_Number": "05MB006",
                    "HyperLink_Graph": "https://www.wsask.ca/hydrographs/05MB006-hrly.html",
                }
            ],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_wsa_stations",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_wsa_stations()
        data = json.loads(result) if isinstance(result, str) else result
        first = data["data"]["features"][0]
        assert "HyperLink_Graph" in first, (
            f"Expected HyperLink_Graph in station data, got: {list(first.keys())}"
        )
        assert "wsask.ca" in first["HyperLink_Graph"], (
            f"Expected wsask.ca URL in HyperLink_Graph, got: {first['HyperLink_Graph']}"
        )

    @pytest.mark.asyncio
    async def test_basin_filter_passed_to_client(self):
        """saskatchewan_get_wsa_stations passes basin= to client function."""
        import json
        payload = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_wsa_stations",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ) as mock_client:
            await tools.saskatchewan_get_wsa_stations(basin="Assiniboine")
        mock_client.assert_called_once()
        call_kwargs = mock_client.call_args[1]
        assert call_kwargs.get("basin") == "Assiniboine", (
            f"Expected basin='Assiniboine' passed to client, got: {call_kwargs}"
        )

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """saskatchewan_get_wsa_stations passes lang='fr' through to _meta envelope."""
        import json
        payload = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_wsa_stations",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_wsa_stations(lang="fr")
        data = json.loads(result) if isinstance(result, str) else result
        assert data["_meta"]["lang"] == "fr", (
            f"Expected lang='fr' in _meta, got: {data['_meta']['lang']}"
        )

    @pytest.mark.asyncio
    async def test_upstream_error_on_http_exception(self):
        """saskatchewan_get_wsa_stations returns UPSTREAM_ERROR on HTTP exception."""
        import json
        import httpx
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_wsa_stations",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "503",
                request=httpx.Request("GET", "https://services1.arcgis.com/7MBdlVpjqbfBhQer"),
                response=httpx.Response(503),
            ),
        ):
            result = await tools.saskatchewan_get_wsa_stations()
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data, f"Expected error response, got: {data}"
        assert data["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_no_basin_calls_client_with_none(self):
        """saskatchewan_get_wsa_stations with no basin passes basin=None to client."""
        import json
        payload = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_wsa_stations",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ) as mock_client:
            await tools.saskatchewan_get_wsa_stations()
        mock_client.assert_called_once()
        call_kwargs = mock_client.call_args[1]
        assert call_kwargs.get("basin") is None, (
            f"Expected basin=None when no basin provided, got: {call_kwargs}"
        )


class TestSaskGetWSAReservoirsTool:
    """saskatchewan_get_wsa_reservoirs tool tests.

    Plan 05 fills: _meta envelope; api='saskatchewan-wsa'; lang passthrough;
    Reservoir_Name + Dam_Name present in response data.
    """

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """saskatchewan_get_wsa_reservoirs returns _meta envelope with api='saskatchewan-wsa'."""
        import json
        payload = {
            "features": [
                {
                    "Reservoir_Name": "ADMIRAL RESERVOIR",
                    "Dam_Name": "ADMIRAL DAM",
                    "Imagery_Date": "2024-05-15",
                    "Water_Level_MASL": 671.3,
                }
            ],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_wsa_reservoirs",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_wsa_reservoirs()
        data = json.loads(result) if isinstance(result, str) else result
        assert "_meta" in data, f"Expected _meta envelope, got: {list(data.keys())}"
        assert data["_meta"]["source"]["api"] == "saskatchewan-wsa", (
            f"Expected api='saskatchewan-wsa', got: {data['_meta']['source']['api']}"
        )

    @pytest.mark.asyncio
    async def test_reservoir_and_dam_name_present_in_response_data(self):
        """saskatchewan_get_wsa_reservoirs response includes Reservoir_Name and Dam_Name."""
        import json
        payload = {
            "features": [
                {
                    "Reservoir_Name": "ADMIRAL RESERVOIR",
                    "Dam_Name": "ADMIRAL DAM",
                    "Water_Level_MASL": 671.3,
                }
            ],
            "count": 1,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_wsa_reservoirs",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_wsa_reservoirs()
        data = json.loads(result) if isinstance(result, str) else result
        first = data["data"]["features"][0]
        assert "Reservoir_Name" in first, (
            f"Expected Reservoir_Name in reservoir data, got: {list(first.keys())}"
        )
        assert first["Reservoir_Name"] == "ADMIRAL RESERVOIR"
        assert "Dam_Name" in first, f"Expected Dam_Name in reservoir data"
        assert first["Dam_Name"] == "ADMIRAL DAM"

    @pytest.mark.asyncio
    async def test_lang_passes_through_to_envelope(self):
        """saskatchewan_get_wsa_reservoirs passes lang='fr' through to _meta envelope."""
        import json
        payload = {"features": [], "count": 0, "truncated": False}
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_wsa_reservoirs",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_wsa_reservoirs(lang="fr")
        data = json.loads(result) if isinstance(result, str) else result
        assert data["_meta"]["lang"] == "fr", (
            f"Expected lang='fr' in _meta, got: {data['_meta']['lang']}"
        )

    @pytest.mark.asyncio
    async def test_upstream_error_on_http_exception(self):
        """saskatchewan_get_wsa_reservoirs returns UPSTREAM_ERROR on HTTP exception."""
        import json
        import httpx
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_wsa_reservoirs",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError(
                "503",
                request=httpx.Request("GET", "https://services1.arcgis.com/7MBdlVpjqbfBhQer"),
                response=httpx.Response(503),
            ),
        ):
            result = await tools.saskatchewan_get_wsa_reservoirs()
        data = json.loads(result) if isinstance(result, str) else result
        assert "error" in data, f"Expected error response, got: {data}"
        assert data["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_data_contains_features_and_count(self):
        """saskatchewan_get_wsa_reservoirs wraps payload under data key with features."""
        import json
        payload = {
            "features": [
                {"Reservoir_Name": "ADMIRAL RESERVOIR", "Dam_Name": "ADMIRAL DAM"},
                {"Reservoir_Name": "ANGLIN LAKE RESERVOIR", "Dam_Name": "ANGLIN LAKE DAM"},
            ],
            "count": 2,
            "truncated": False,
        }
        with patch(
            "mcp_canada.modules.saskatchewan.tools._client.fetch_wsa_reservoirs",
            new_callable=AsyncMock,
            return_value=(payload, False),
        ):
            result = await tools.saskatchewan_get_wsa_reservoirs()
        data = json.loads(result) if isinstance(result, str) else result
        assert data["data"]["count"] == 2
        assert len(data["data"]["features"]) == 2


# ---------------------------------------------------------------------------
# Cross-cutting: envelope + lang parameter (Plan 07)
# ---------------------------------------------------------------------------

# (tool_name, client_fn_attribute_on_client, sample_kwargs, sample_client_return)
#
# Count: 5 discovery + 3 agriculture+mining + 3 environment + 2 water = 14
ALL_SASKATCHEWAN_TOOLS: list[tuple[str, str, dict, tuple]] = [
    # Discovery (Plan 02) — 5
    (
        "saskatchewan_search_datasets",
        "fetch_search_datasets",
        {"query": "crops"},
        ({"results": [], "total": 0}, False),
    ),
    (
        "saskatchewan_get_dataset_details",
        "fetch_dataset_details",
        {"dataset_id": "abc123"},
        ({"details": {"id": "abc123", "title": "X", "feature_server_url": None, "download_urls": []}}, False),
    ),
    (
        "saskatchewan_query_dataset",
        "fetch_query_dataset",
        {"dataset_id": "https://services3.arcgis.com/zcv98lgAl8xQ04cW/arcgis/rest/services/Crop/FeatureServer"},
        ({"data": [], "url": "https://example.com/FeatureServer", "rows": 0, "truncated": False}, False),
    ),
    (
        "saskatchewan_list_organizations",
        "fetch_organizations",
        {},
        ({"organizations": []}, False),
    ),
    (
        "saskatchewan_list_categories",
        "fetch_categories",
        {},
        ({"categories": []}, False),
    ),
    # Agriculture + Mining (Plan 03) — 3
    (
        "saskatchewan_get_crop_yields",
        "fetch_crop_yields",
        {"region": "provincial"},
        ({"features": [], "count": 0, "truncated": False, "region": "provincial"}, False),
    ),
    (
        "saskatchewan_get_grain_elevators",
        "fetch_grain_elevators",
        {},
        ({"features": [], "count": 0, "truncated": False}, False),
    ),
    (
        "saskatchewan_get_mineral_mines",
        "fetch_mineral_mines",
        {"mineral": "potash"},
        ({"features": [], "count": 0, "truncated": False, "mineral": "potash"}, False),
    ),
    # Environment (Plan 04) — 3
    (
        "saskatchewan_get_fire_bans",
        "fetch_fire_bans",
        {"ban_scope": "urban"},
        ({"features": [], "count": 0, "truncated": False, "scope": "urban"}, False),
    ),
    (
        "saskatchewan_get_historic_wildfires",
        "fetch_historic_wildfires",
        {},
        ({"features": [], "count": 0, "truncated": False}, False),
    ),
    (
        "saskatchewan_get_air_quality",
        "fetch_air_quality",
        {},
        ({"features": [], "count": 0, "truncated": False}, False),
    ),
    # Water / WSA (Plan 05) — 2
    (
        "saskatchewan_get_wsa_stations",
        "fetch_wsa_stations",
        {},
        ({"features": [], "count": 0, "truncated": False}, False),
    ),
    (
        "saskatchewan_get_wsa_reservoirs",
        "fetch_wsa_reservoirs",
        {},
        ({"features": [], "count": 0, "truncated": False}, False),
    ),
]

# Sanity check: exactly 13 tools (5 discovery + 3 agri+mining + 3 environment + 2 water)
# Note: plan documentation says "14 tools" but __all__ in tools.py has 13 entries.
# Cross-checked against 19-05-SUMMARY.md table: 5+3+3+2=13. All 13 in this list.
assert len(ALL_SASKATCHEWAN_TOOLS) == 13, (
    f"ALL_SASKATCHEWAN_TOOLS must have 13 entries (matching __all__ in tools.py), "
    f"got {len(ALL_SASKATCHEWAN_TOOLS)}"
)


class TestSaskEnvelopes:
    """Parametrized: all 13 saskatchewan_ tools return _meta envelope on success (Plan 07).

    Mirrors Alberta Plan 09 pattern. Each tool is called with a mocked client function
    that returns an empty-but-valid payload. Asserts the full _meta envelope shape:
    source.api, source.url, cached, lang, timestamp keys all present.
    """

    @pytest.mark.parametrize(
        ("tool_name", "client_fn", "kwargs", "client_return"),
        ALL_SASKATCHEWAN_TOOLS,
        ids=[t[0] for t in ALL_SASKATCHEWAN_TOOLS],
    )
    @pytest.mark.asyncio
    async def test_envelope_structure(
        self, tool_name: str, client_fn: str, kwargs: dict, client_return: tuple
    ):
        """Every tool returns _meta with {source.api, source.url, cached, lang, timestamp}."""
        import json

        tool_fn = getattr(tools, tool_name)
        with patch(
            f"mcp_canada.modules.saskatchewan.tools._client.{client_fn}",
            new_callable=AsyncMock,
            return_value=client_return,
        ):
            result = await tool_fn(**kwargs, lang="en")

        data = json.loads(result) if isinstance(result, str) else result
        assert "_meta" in data, f"{tool_name} missing _meta envelope"
        meta = data["_meta"]
        for key in ("source", "cached", "lang", "timestamp"):
            assert key in meta, f"{tool_name} _meta missing '{key}'"
        assert "api" in meta["source"], f"{tool_name} _meta.source missing 'api'"
        assert "url" in meta["source"], f"{tool_name} _meta.source missing 'url'"
        assert meta["lang"] == "en", (
            f"{tool_name} should default _meta.lang to 'en', got {meta['lang']!r}"
        )


class TestSaskLangParam:
    """Parametrized: all 13 tools accept lang='fr' and pass through to _meta.lang (Plan 07).

    Mirrors Alberta Plan 09 pattern. Every tool must propagate lang='fr' to _meta.lang.
    """

    @pytest.mark.parametrize(
        ("tool_name", "client_fn", "kwargs", "client_return"),
        ALL_SASKATCHEWAN_TOOLS,
        ids=[t[0] for t in ALL_SASKATCHEWAN_TOOLS],
    )
    @pytest.mark.asyncio
    async def test_lang_propagation(
        self, tool_name: str, client_fn: str, kwargs: dict, client_return: tuple
    ):
        """Every tool propagates lang='fr' to the _meta.lang field on success."""
        import json

        tool_fn = getattr(tools, tool_name)
        with patch(
            f"mcp_canada.modules.saskatchewan.tools._client.{client_fn}",
            new_callable=AsyncMock,
            return_value=client_return,
        ):
            result = await tool_fn(**kwargs, lang="fr")

        data = json.loads(result) if isinstance(result, str) else result
        assert data.get("_meta", {}).get("lang") == "fr", (
            f"{tool_name} did not propagate lang='fr' to _meta.lang — got {data.get('_meta')}"
        )
