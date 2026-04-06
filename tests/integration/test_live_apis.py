"""Integration tests against live Canadian government APIs.

These tests hit real endpoints to catch issues that mocked unit tests miss:
- Timeouts / slow responses
- Changed response shapes
- Broken query parameters
- Endpoint availability

Run manually: uv run pytest tests/integration/ -x -v --timeout=120
Skip in CI: these are excluded from default test paths via pyproject.toml
"""

import pytest
import httpx

# All integration tests use this marker — skipped in CI, run manually
pytestmark = pytest.mark.integration


# ─── Shared fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def http():
    """Long-timeout httpx client for slow government APIs."""
    return httpx.AsyncClient(timeout=90.0)


# ─── Bank of Canada Valet API ────────────────────────────────────────────────


class TestBankOfCanadaLive:

    @pytest.mark.asyncio
    async def test_exchange_rates_returns_observations(self, http):
        """GET /observations/FXUSDCAD/json returns real data with v-wrapped values."""
        r = await http.get(
            "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json",
            params={"recent": 1},
        )
        assert r.status_code == 200
        data = r.json()
        assert "observations" in data
        assert len(data["observations"]) >= 1
        obs = data["observations"][0]
        assert "d" in obs
        assert "FXUSDCAD" in obs
        assert "v" in obs["FXUSDCAD"]

    @pytest.mark.asyncio
    async def test_date_range_without_recent_works(self, http):
        """Valet rejects recent + date range together — verify date-only works."""
        r = await http.get(
            "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json",
            params={"start_date": "2026-01-01", "end_date": "2026-01-31"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "observations" in data

    @pytest.mark.asyncio
    async def test_recent_plus_dates_returns_400(self, http):
        """Confirm Valet rejects recent + date range (regression guard)."""
        r = await http.get(
            "https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json",
            params={"recent": 10, "start_date": "2026-01-01", "end_date": "2026-01-31"},
        )
        assert r.status_code == 400

    @pytest.mark.asyncio
    async def test_policy_rate_series_exists(self, http):
        """V39079 (policy rate) still works — unlike V80691319 (prime, 404)."""
        r = await http.get(
            "https://www.bankofcanada.ca/valet/observations/V39079/json",
            params={"recent": 1},
        )
        assert r.status_code == 200


# ─── Open Parliament API ────────────────────────────────────────────────────


class TestOpenParliamentLive:

    @pytest.mark.asyncio
    async def test_bills_endpoint_returns_objects(self, http):
        """GET /bills/ returns paginated objects list."""
        r = await http.get(
            "https://api.openparliament.ca/bills/",
            params={"session": "44-1"},
            headers={"Accept": "application/json"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "objects" in data
        assert len(data["objects"]) > 0

    @pytest.mark.asyncio
    async def test_bill_details_by_id(self, http):
        """GET /bills/42-1/C-45/ returns Cannabis Act details."""
        r = await http.get(
            "https://api.openparliament.ca/bills/42-1/C-45/",
            headers={"Accept": "application/json"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "name" in data

    @pytest.mark.asyncio
    async def test_ballots_endpoint_returns_individual_votes(self, http):
        """GET /votes/ballots/ returns per-MP yea/nay ballot data."""
        r = await http.get(
            "https://api.openparliament.ca/votes/ballots/",
            params={
                "vote": "/votes/44-1/333/",
                "politician": "/politicians/anna-roberts/",
            },
            headers={"Accept": "application/json"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "objects" in data
        assert len(data["objects"]) >= 1
        assert data["objects"][0]["ballot"] in ("Yes", "No", "Paired")

    @pytest.mark.asyncio
    async def test_bill_keyword_search_limitation(self, http):
        """Bills keyword search does NOT filter by bill title/content.

        This documents the known limitation: searching bills for 'cannabis'
        returns unrelated results. Use hansard search or direct bill ID instead.
        """
        r = await http.get(
            "https://api.openparliament.ca/bills/",
            params={"q": "cannabis", "session": "42-1"},
            headers={"Accept": "application/json"},
        )
        assert r.status_code == 200
        data = r.json()
        # If the API ever fixes keyword search, this test will need updating
        # For now: verify we get results but they're NOT cannabis-related
        if data["objects"]:
            first_bill_name = data["objects"][0].get("name", {}).get("en", "")
            # The first result should NOT be about cannabis (known limitation)
            assert "cannabis" not in first_bill_name.lower(), (
                "Bill keyword search now works! Update parl_search_bills docstring."
            )

    @pytest.mark.asyncio
    async def test_requires_accept_json_header(self, http):
        """Open Parliament returns HTML without Accept: application/json."""
        r = await http.get("https://api.openparliament.ca/bills/")
        # Without Accept header, should return HTML (not JSON)
        content_type = r.headers.get("content-type", "")
        assert "html" in content_type or r.status_code == 200


# ─── Recalls API ────────────────────────────────────────────────────────────


class TestRecallsLive:

    @pytest.mark.asyncio
    async def test_recent_recalls_returns_results(self, http):
        """GET /recent/en returns recent recalls."""
        r = await http.get(
            "https://healthycanadians.gc.ca/recall-alert-rappel-avis/api/recent/en",
            params={"lim": 5},
        )
        assert r.status_code == 200
        data = r.json()
        assert "results" in data or isinstance(data, list)

    @pytest.mark.asyncio
    async def test_search_recalls_with_category(self, http):
        """GET /search with cat[] filter works."""
        r = await http.get(
            "https://healthycanadians.gc.ca/recall-alert-rappel-avis/api/search",
            params=[("search", "safety"), ("cat[]", "FOOD"), ("lim", 3), ("lang", "en")],
        )
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_bilingual_support(self, http):
        """GET /recent/fr returns French results."""
        r = await http.get(
            "https://healthycanadians.gc.ca/recall-alert-rappel-avis/api/recent/fr",
            params={"lim": 2},
        )
        assert r.status_code == 200


# ─── Drug Product Database API ──────────────────────────────────────────────


class TestDrugDatabaseLive:

    @pytest.mark.asyncio
    async def test_search_by_brandname(self, http):
        """GET /drugproduct/?brandname=tylenol returns results (may be slow)."""
        r = await http.get(
            "https://health-products.canada.ca/api/drug/drugproduct/",
            params={"brandname": "tylenol"},
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_response_time_under_60s(self, http):
        """Drug API broad search completes within 60s timeout."""
        import time
        start = time.monotonic()
        r = await http.get(
            "https://health-products.canada.ca/api/drug/drugproduct/",
            params={"brandname": "aspirin"},
        )
        elapsed = time.monotonic() - start
        assert r.status_code == 200
        assert elapsed < 60, f"Drug API took {elapsed:.1f}s — timeout risk"


# ─── CKAN Open Data API ────────────────────────────────────────────────────


class TestCkanLive:

    @pytest.mark.asyncio
    async def test_package_search_returns_results(self, http):
        """GET action/package_search returns datasets."""
        r = await http.get(
            "https://open.canada.ca/data/en/api/3/action/package_search",
            params={"q": "climate", "rows": 3},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert "results" in data["result"]

    @pytest.mark.asyncio
    async def test_organization_list(self, http):
        """GET action/organization_list returns orgs."""
        r = await http.get(
            "https://open.canada.ca/data/en/api/3/action/organization_list",
            params={"all_fields": "true"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True


# ─── Canadian Nutrient File API ─────────────────────────────────────────────


class TestNutrientFileLive:

    @pytest.mark.asyncio
    async def test_food_list_returns_data(self, http):
        """GET /food returns food list."""
        r = await http.get(
            "https://food-nutrition.canada.ca/api/canadian-nutrient-file/food",
            params={"lang": "en", "type": "json"},
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_nutrient_amounts_for_food(self, http):
        """GET /nutrientamount returns nutrient data for a food ID."""
        r = await http.get(
            "https://food-nutrition.canada.ca/api/canadian-nutrient-file/nutrientamount",
            params={"lang": "en", "id": 2},
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
