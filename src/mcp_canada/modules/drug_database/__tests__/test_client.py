"""Unit tests for Drug Product Database client functions.

Tests verify:
- Each fetch function calls the correct endpoint with correct params
- fetch_drug_details uses asyncio.gather for 5 parallel calls
- drug_code (not DIN) is used for detail lookups
- Cached and non-cached paths work correctly
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch

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

SAMPLE_INGREDIENTS = [
    {
        "ingredient_name": "ACETAMINOPHEN",
        "strength": "500",
        "strength_unit": "MG",
        "dosage_value": "1",
        "dosage_unit": "TABLET",
    }
]

SAMPLE_ROUTES = [{"route_of_administration": "ORAL"}]
SAMPLE_SCHEDULE = [{"schedule_name": "OTC"}]
SAMPLE_THERAPEUTIC_CLASS = [
    {
        "tc_atc_number": "N02BE01",
        "tc_atc": "Anilides",
        "tc_ahfs_number": "28:08.92",
        "tc_ahfs": "ANALGESICS AND ANTIPYRETICS, MISC.",
    }
]
SAMPLE_STATUS = [
    {
        "status": "MARKETED",
        "history_date": "1993-02-04",
        "lot_number": None,
        "expiration_date": None,
    }
]
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


# ===========================================================================
# Tests for fetch_drug_search
# ===========================================================================

class TestFetchDrugSearch:

    @pytest.mark.asyncio
    async def test_search_by_brandname(self):
        """fetch_drug_search with brandname calls /drugproduct/ with brandname param."""
        from mcp_canada.modules.drug_database.client import fetch_drug_search

        with patch("mcp_canada.modules.drug_database.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (SAMPLE_DRUG_SEARCH, False)
            result, cached = await fetch_drug_search(brandname="TYLENOL")

        mock_api.assert_called_once()
        call_args = mock_api.call_args
        assert "drugproduct" in call_args[0][0]
        assert call_args[0][1].get("brandname") == "TYLENOL"
        assert isinstance(result, list)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_search_by_din(self):
        """fetch_drug_search with din calls /drugproduct/ with din param."""
        from mcp_canada.modules.drug_database.client import fetch_drug_search

        with patch("mcp_canada.modules.drug_database.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = ([SAMPLE_DRUG_SEARCH[0]], True)
            result, cached = await fetch_drug_search(din="00559407")

        mock_api.assert_called_once()
        call_args = mock_api.call_args
        assert call_args[0][1].get("din") == "00559407"
        assert cached is True

    @pytest.mark.asyncio
    async def test_search_by_company(self):
        """fetch_drug_search with company calls /drugproduct/ with company param."""
        from mcp_canada.modules.drug_database.client import fetch_drug_search

        with patch("mcp_canada.modules.drug_database.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (SAMPLE_DRUG_SEARCH, False)
            result, cached = await fetch_drug_search(company="PFIZER")

        mock_api.assert_called_once()
        call_args = mock_api.call_args
        assert call_args[0][1].get("company") == "PFIZER"


# ===========================================================================
# Tests for individual detail fetch functions
# (all use drug_code as the id param, NOT DIN)
# ===========================================================================

class TestFetchIngredients:

    @pytest.mark.asyncio
    async def test_uses_drug_code_not_din(self):
        """fetch_ingredients uses drug_code as 'id' param, not DIN."""
        from mcp_canada.modules.drug_database.client import fetch_ingredients

        drug_code = 12345  # drug_code is internal ID, not the DIN (00559407)
        with patch("mcp_canada.modules.drug_database.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (SAMPLE_INGREDIENTS, False)
            result, cached = await fetch_ingredients(drug_code)

        mock_api.assert_called_once()
        call_args = mock_api.call_args
        assert "activeingredient" in call_args[0][0]
        assert call_args[0][1].get("id") == drug_code
        assert isinstance(result, list)


class TestFetchRoutes:

    @pytest.mark.asyncio
    async def test_uses_drug_code_as_id(self):
        """fetch_routes uses drug_code as 'id' param, calls /route/ endpoint."""
        from mcp_canada.modules.drug_database.client import fetch_routes

        drug_code = 12345
        with patch("mcp_canada.modules.drug_database.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (SAMPLE_ROUTES, False)
            result, cached = await fetch_routes(drug_code)

        mock_api.assert_called_once()
        call_args = mock_api.call_args
        assert "route" in call_args[0][0]
        assert call_args[0][1].get("id") == drug_code


class TestFetchSchedule:

    @pytest.mark.asyncio
    async def test_uses_drug_code_as_id(self):
        """fetch_schedule uses drug_code as 'id' param, calls /schedule/ endpoint."""
        from mcp_canada.modules.drug_database.client import fetch_schedule

        drug_code = 12345
        with patch("mcp_canada.modules.drug_database.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (SAMPLE_SCHEDULE, False)
            result, cached = await fetch_schedule(drug_code)

        mock_api.assert_called_once()
        call_args = mock_api.call_args
        assert "schedule" in call_args[0][0]
        assert call_args[0][1].get("id") == drug_code


class TestFetchTherapeuticClass:

    @pytest.mark.asyncio
    async def test_uses_drug_code_as_id(self):
        """fetch_therapeutic_class uses drug_code as 'id' param, calls /therapeuticclass/."""
        from mcp_canada.modules.drug_database.client import fetch_therapeutic_class

        drug_code = 12345
        with patch("mcp_canada.modules.drug_database.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (SAMPLE_THERAPEUTIC_CLASS, False)
            result, cached = await fetch_therapeutic_class(drug_code)

        mock_api.assert_called_once()
        call_args = mock_api.call_args
        assert "therapeuticclass" in call_args[0][0]
        assert call_args[0][1].get("id") == drug_code


class TestFetchStatus:

    @pytest.mark.asyncio
    async def test_uses_drug_code_as_id(self):
        """fetch_status uses drug_code as 'id' param, calls /status/ endpoint."""
        from mcp_canada.modules.drug_database.client import fetch_status

        drug_code = 12345
        with patch("mcp_canada.modules.drug_database.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (SAMPLE_STATUS, False)
            result, cached = await fetch_status(drug_code)

        mock_api.assert_called_once()
        call_args = mock_api.call_args
        assert "status" in call_args[0][0]
        assert call_args[0][1].get("id") == drug_code


class TestFetchCompanies:

    @pytest.mark.asyncio
    async def test_search_by_company_name(self):
        """fetch_companies searches by companyname param."""
        from mcp_canada.modules.drug_database.client import fetch_companies

        with patch("mcp_canada.modules.drug_database.client._api_get",
                   new_callable=AsyncMock) as mock_api:
            mock_api.return_value = (SAMPLE_COMPANIES, False)
            result, cached = await fetch_companies("JOHNSON")

        mock_api.assert_called_once()
        call_args = mock_api.call_args
        assert "company" in call_args[0][0]
        assert call_args[0][1].get("companyname") == "JOHNSON"


# ===========================================================================
# Tests for fetch_drug_details — the key parallel fetch function
# ===========================================================================

class TestFetchDrugDetails:

    @pytest.mark.asyncio
    async def test_uses_asyncio_gather_for_5_parallel_calls(self):
        """fetch_drug_details uses asyncio.gather to fetch 5 endpoints in parallel."""
        from mcp_canada.modules.drug_database import client

        drug_code = 12345
        gather_calls = []

        async def mock_ingredients(dc): return (SAMPLE_INGREDIENTS, False)
        async def mock_routes(dc): return (SAMPLE_ROUTES, False)
        async def mock_schedule(dc): return (SAMPLE_SCHEDULE, False)
        async def mock_therapeutic_class(dc): return (SAMPLE_THERAPEUTIC_CLASS, False)
        async def mock_status(dc): return (SAMPLE_STATUS, False)

        original_gather = asyncio.gather

        async def spy_gather(*coros, **kwargs):
            gather_calls.append(len(coros))
            return await original_gather(*coros, **kwargs)

        with patch.object(client, "fetch_ingredients", side_effect=mock_ingredients), \
             patch.object(client, "fetch_routes", side_effect=mock_routes), \
             patch.object(client, "fetch_schedule", side_effect=mock_schedule), \
             patch.object(client, "fetch_therapeutic_class", side_effect=mock_therapeutic_class), \
             patch.object(client, "fetch_status", side_effect=mock_status), \
             patch("asyncio.gather", side_effect=spy_gather):
            result, cached = await client.fetch_drug_details(drug_code)

        # asyncio.gather should have been called with 5 coroutines
        assert len(gather_calls) > 0, "asyncio.gather was not called"
        assert gather_calls[0] == 5, f"Expected 5 parallel calls, got {gather_calls[0]}"

    @pytest.mark.asyncio
    async def test_returns_flat_sections_dict(self):
        """fetch_drug_details returns flat sections dict with 5 keys."""
        from mcp_canada.modules.drug_database import client

        drug_code = 12345

        async def mock_ingredients(dc): return (SAMPLE_INGREDIENTS, False)
        async def mock_routes(dc): return (SAMPLE_ROUTES, False)
        async def mock_schedule(dc): return (SAMPLE_SCHEDULE, False)
        async def mock_therapeutic_class(dc): return (SAMPLE_THERAPEUTIC_CLASS, False)
        async def mock_status(dc): return (SAMPLE_STATUS, False)

        with patch.object(client, "fetch_ingredients", side_effect=mock_ingredients), \
             patch.object(client, "fetch_routes", side_effect=mock_routes), \
             patch.object(client, "fetch_schedule", side_effect=mock_schedule), \
             patch.object(client, "fetch_therapeutic_class", side_effect=mock_therapeutic_class), \
             patch.object(client, "fetch_status", side_effect=mock_status):
            result, cached = await client.fetch_drug_details(drug_code)

        assert isinstance(result, dict), "fetch_drug_details should return a dict"
        assert "ingredients" in result, "Result should have 'ingredients' key"
        assert "routes" in result, "Result should have 'routes' key"
        assert "schedule" in result, "Result should have 'schedule' key"
        assert "therapeutic_class" in result, "Result should have 'therapeutic_class' key"
        assert "status" in result, "Result should have 'status' key"
        assert len(result) == 5, f"Expected 5 sections, got {len(result)}"

    @pytest.mark.asyncio
    async def test_drug_code_not_din(self):
        """fetch_drug_details uses drug_code (int), not DIN (str), for all lookups."""
        from mcp_canada.modules.drug_database import client

        drug_code = 12345  # This is the internal drug_code, NOT the DIN like "00559407"
        received_codes = []

        async def spy_ingredients(dc):
            received_codes.append(("ingredients", dc))
            return (SAMPLE_INGREDIENTS, False)

        async def spy_routes(dc):
            received_codes.append(("routes", dc))
            return (SAMPLE_ROUTES, False)

        async def spy_schedule(dc):
            received_codes.append(("schedule", dc))
            return (SAMPLE_SCHEDULE, False)

        async def spy_therapeutic_class(dc):
            received_codes.append(("therapeutic_class", dc))
            return (SAMPLE_THERAPEUTIC_CLASS, False)

        async def spy_status(dc):
            received_codes.append(("status", dc))
            return (SAMPLE_STATUS, False)

        with patch.object(client, "fetch_ingredients", side_effect=spy_ingredients), \
             patch.object(client, "fetch_routes", side_effect=spy_routes), \
             patch.object(client, "fetch_schedule", side_effect=spy_schedule), \
             patch.object(client, "fetch_therapeutic_class", side_effect=spy_therapeutic_class), \
             patch.object(client, "fetch_status", side_effect=spy_status):
            result, cached = await client.fetch_drug_details(drug_code)

        # All 5 detail functions should receive the drug_code (integer)
        for name, code in received_codes:
            assert code == 12345, f"{name} received {code!r} instead of drug_code 12345"
            assert isinstance(code, int), f"{name} should receive int drug_code, got {type(code)}"

    @pytest.mark.asyncio
    async def test_cached_is_true_when_all_cached(self):
        """cached flag is True when all sub-responses are cached."""
        from mcp_canada.modules.drug_database import client

        drug_code = 12345

        async def mock_ingredients(dc): return (SAMPLE_INGREDIENTS, True)
        async def mock_routes(dc): return (SAMPLE_ROUTES, True)
        async def mock_schedule(dc): return (SAMPLE_SCHEDULE, True)
        async def mock_therapeutic_class(dc): return (SAMPLE_THERAPEUTIC_CLASS, True)
        async def mock_status(dc): return (SAMPLE_STATUS, True)

        with patch.object(client, "fetch_ingredients", side_effect=mock_ingredients), \
             patch.object(client, "fetch_routes", side_effect=mock_routes), \
             patch.object(client, "fetch_schedule", side_effect=mock_schedule), \
             patch.object(client, "fetch_therapeutic_class", side_effect=mock_therapeutic_class), \
             patch.object(client, "fetch_status", side_effect=mock_status):
            result, cached = await client.fetch_drug_details(drug_code)

        assert cached is True, "Should be cached when all sub-responses are cached"

    @pytest.mark.asyncio
    async def test_cached_is_false_when_any_not_cached(self):
        """cached flag is False when any sub-response is not cached."""
        from mcp_canada.modules.drug_database import client

        drug_code = 12345

        async def mock_ingredients(dc): return (SAMPLE_INGREDIENTS, True)
        async def mock_routes(dc): return (SAMPLE_ROUTES, False)  # Not cached
        async def mock_schedule(dc): return (SAMPLE_SCHEDULE, True)
        async def mock_therapeutic_class(dc): return (SAMPLE_THERAPEUTIC_CLASS, True)
        async def mock_status(dc): return (SAMPLE_STATUS, True)

        with patch.object(client, "fetch_ingredients", side_effect=mock_ingredients), \
             patch.object(client, "fetch_routes", side_effect=mock_routes), \
             patch.object(client, "fetch_schedule", side_effect=mock_schedule), \
             patch.object(client, "fetch_therapeutic_class", side_effect=mock_therapeutic_class), \
             patch.object(client, "fetch_status", side_effect=mock_status):
            result, cached = await client.fetch_drug_details(drug_code)

        assert cached is False, "Should not be cached when any sub-response is not cached"
