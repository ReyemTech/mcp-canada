"""Unit tests for IRCC tool functions.

Tests verify:
- make_response envelope on success
- make_error on invalid input
- Year filtering logic
- lang parameter passthrough
- HTTPStatusError handling
- Docstring quality (Use for: / Keywords: lines)
"""

import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_canada.modules.ircc.constants import DATASET_REGISTRY
from mcp_canada.shared.envelope import make_response, make_error


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_ROWS = [
    {"year": 2024, "country": "India", "admissions": 100},
    {"year": 2023, "country": "Philippines", "admissions": 50},
    {"year": 2022, "country": "China", "admissions": 75},
]

SAMPLE_ROW_FR = [{"annee": 2024, "pays": "Inde", "admissions": 100}]


def _make_client_mock(rows=None, cached=False):
    """Return an AsyncMock that returns (rows, cached)."""
    if rows is None:
        rows = list(SAMPLE_ROWS)
    mock = AsyncMock(return_value=(rows, cached))
    return mock


# ---------------------------------------------------------------------------
# ircc_get_permanent_residents
# ---------------------------------------------------------------------------

class TestIrccGetPermanentResidents:

    @pytest.mark.asyncio
    async def test_returns_make_response_envelope(self):
        """Happy path: returns _meta envelope with data list."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_permanent_residents",
            new_callable=AsyncMock,
            return_value=(list(SAMPLE_ROWS), False),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_permanent_residents
            result = await ircc_get_permanent_residents(breakdown="country")
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "IRCC Open Data"
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_invalid_breakdown_returns_make_error(self):
        """Invalid breakdown returns INVALID_INPUT error."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_permanent_residents",
            new_callable=AsyncMock,
            side_effect=ValueError("Unknown breakdown 'nonexistent'"),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_permanent_residents
            result = await ircc_get_permanent_residents(breakdown="nonexistent")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_year_filter_works(self):
        """year parameter filters rows to matching year only."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_permanent_residents",
            new_callable=AsyncMock,
            return_value=(list(SAMPLE_ROWS), False),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_permanent_residents
            result = await ircc_get_permanent_residents(breakdown="country", year=2024)
        assert "_meta" in result
        assert all(r["year"] == 2024 for r in result["data"])
        assert len(result["data"]) == 1

    @pytest.mark.asyncio
    async def test_year_filter_fr_column(self):
        """year filter works on French column name 'annee'."""
        rows = [{"annee": 2024, "pays": "Inde"}, {"annee": 2023, "pays": "Chine"}]
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_permanent_residents",
            new_callable=AsyncMock,
            return_value=(rows, False),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_permanent_residents
            result = await ircc_get_permanent_residents(breakdown="country", year=2024, lang="fr")
        assert len(result["data"]) == 1

    @pytest.mark.asyncio
    async def test_lang_passthrough(self):
        """lang='fr' is passed through to client and envelope."""
        mock = AsyncMock(return_value=(list(SAMPLE_ROWS), False))
        with patch("mcp_canada.modules.ircc.tools.fetch_permanent_residents", mock):
            from mcp_canada.modules.ircc.tools import ircc_get_permanent_residents
            result = await ircc_get_permanent_residents(breakdown="country", lang="fr")
        mock.assert_called_once_with(breakdown="country", lang="fr")
        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_http_error_returns_upstream_error(self):
        """HTTPStatusError returns UPSTREAM_ERROR."""
        mock_response = MagicMock()
        mock_response.status_code = 503
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_permanent_residents",
            new_callable=AsyncMock,
            side_effect=httpx.HTTPStatusError("503", request=MagicMock(), response=mock_response),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_permanent_residents
            result = await ircc_get_permanent_residents(breakdown="country")
        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


# ---------------------------------------------------------------------------
# ircc_get_study_permits
# ---------------------------------------------------------------------------

class TestIrccGetStudyPermits:

    @pytest.mark.asyncio
    async def test_returns_make_response_envelope(self):
        """Happy path: returns _meta envelope."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_study_permits",
            new_callable=AsyncMock,
            return_value=(list(SAMPLE_ROWS), False),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_study_permits
            result = await ircc_get_study_permits(breakdown="country")
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "IRCC Open Data"

    @pytest.mark.asyncio
    async def test_invalid_breakdown(self):
        """Invalid breakdown returns make_error."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_study_permits",
            new_callable=AsyncMock,
            side_effect=ValueError("Unknown breakdown"),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_study_permits
            result = await ircc_get_study_permits(breakdown="invalid")
        assert result["error"]["code"] == "INVALID_INPUT"


# ---------------------------------------------------------------------------
# ircc_get_work_permits
# ---------------------------------------------------------------------------

class TestIrccGetWorkPermits:

    @pytest.mark.asyncio
    async def test_imp_returns_data(self):
        """permit_type='imp' returns correct data."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_work_permits_imp",
            new_callable=AsyncMock,
            return_value=(list(SAMPLE_ROWS), False),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_work_permits
            result = await ircc_get_work_permits(permit_type="imp", breakdown="country")
        assert "_meta" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_tfwp_returns_data(self):
        """permit_type='tfwp' returns correct data."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_work_permits_tfwp",
            new_callable=AsyncMock,
            return_value=(list(SAMPLE_ROWS), False),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_work_permits
            result = await ircc_get_work_permits(permit_type="tfwp", breakdown="country")
        assert "_meta" in result

    @pytest.mark.asyncio
    async def test_invalid_permit_type(self):
        """Invalid permit_type returns INVALID_INPUT."""
        from mcp_canada.modules.ircc.tools import ircc_get_work_permits
        result = await ircc_get_work_permits(permit_type="invalid", breakdown="country")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_invalid_breakdown_imp(self):
        """Invalid breakdown for IMP returns INVALID_INPUT."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_work_permits_imp",
            new_callable=AsyncMock,
            side_effect=ValueError("Unknown breakdown"),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_work_permits
            result = await ircc_get_work_permits(permit_type="imp", breakdown="nonexistent")
        assert result["error"]["code"] == "INVALID_INPUT"


# ---------------------------------------------------------------------------
# ircc_get_express_entry
# ---------------------------------------------------------------------------

class TestIrccGetExpressEntry:

    @pytest.mark.asyncio
    async def test_admissions_returns_data(self):
        """stream='admissions' calls fetch_ee_admissions."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_ee_admissions",
            new_callable=AsyncMock,
            return_value=(list(SAMPLE_ROWS), False),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_express_entry
            result = await ircc_get_express_entry(stream="admissions", breakdown="gender")
        assert "_meta" in result

    @pytest.mark.asyncio
    async def test_invited_returns_data(self):
        """stream='invited' calls fetch_ee_invited."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_ee_invited",
            new_callable=AsyncMock,
            return_value=(list(SAMPLE_ROWS), False),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_express_entry
            result = await ircc_get_express_entry(stream="invited", breakdown="destination")
        assert "_meta" in result

    @pytest.mark.asyncio
    async def test_invalid_stream(self):
        """Invalid stream returns INVALID_INPUT."""
        from mcp_canada.modules.ircc.tools import ircc_get_express_entry
        result = await ircc_get_express_entry(stream="invalid", breakdown="gender")
        assert result["error"]["code"] == "INVALID_INPUT"


# ---------------------------------------------------------------------------
# ircc_get_tr_to_pr
# ---------------------------------------------------------------------------

class TestIrccGetTrToPr:

    @pytest.mark.asyncio
    async def test_returns_data(self):
        """ircc_get_tr_to_pr returns _meta envelope."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_tr_to_pr",
            new_callable=AsyncMock,
            return_value=(list(SAMPLE_ROWS), False),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_tr_to_pr
            result = await ircc_get_tr_to_pr(breakdown="study_permit")
        assert "_meta" in result

    @pytest.mark.asyncio
    async def test_invalid_breakdown(self):
        """Invalid breakdown returns INVALID_INPUT."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_tr_to_pr",
            new_callable=AsyncMock,
            side_effect=ValueError("Unknown breakdown"),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_tr_to_pr
            result = await ircc_get_tr_to_pr(breakdown="bad")
        assert result["error"]["code"] == "INVALID_INPUT"


# ---------------------------------------------------------------------------
# ircc_get_asylum
# ---------------------------------------------------------------------------

class TestIrccGetAsylum:

    @pytest.mark.asyncio
    async def test_returns_data(self):
        """ircc_get_asylum returns _meta envelope."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_asylum",
            new_callable=AsyncMock,
            return_value=(list(SAMPLE_ROWS), False),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_asylum
            result = await ircc_get_asylum(breakdown="province_office")
        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "IRCC Open Data"


# ---------------------------------------------------------------------------
# ircc_get_ops
# ---------------------------------------------------------------------------

class TestIrccGetOps:

    @pytest.mark.asyncio
    async def test_returns_data(self):
        """ircc_get_ops returns _meta envelope (no year filter)."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_ops",
            new_callable=AsyncMock,
            return_value=(list(SAMPLE_ROWS), False),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_ops
            result = await ircc_get_ops(breakdown="pr_intake")
        assert "_meta" in result

    @pytest.mark.asyncio
    async def test_invalid_breakdown(self):
        """Invalid breakdown returns INVALID_INPUT."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_ops",
            new_callable=AsyncMock,
            side_effect=ValueError("Unknown breakdown"),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_ops
            result = await ircc_get_ops(breakdown="bad")
        assert result["error"]["code"] == "INVALID_INPUT"


# ---------------------------------------------------------------------------
# ircc_get_afghan
# ---------------------------------------------------------------------------

class TestIrccGetAfghan:

    @pytest.mark.asyncio
    async def test_returns_data(self):
        """ircc_get_afghan returns _meta envelope."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_afghan",
            new_callable=AsyncMock,
            return_value=(list(SAMPLE_ROWS), False),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_afghan
            result = await ircc_get_afghan(breakdown="gender")
        assert "_meta" in result


# ---------------------------------------------------------------------------
# ircc_get_adhoc_pr
# ---------------------------------------------------------------------------

class TestIrccGetAdhocPr:

    @pytest.mark.asyncio
    async def test_returns_data(self):
        """ircc_get_adhoc_pr returns _meta envelope."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_adhoc_pr",
            new_callable=AsyncMock,
            return_value=(list(SAMPLE_ROWS), False),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_adhoc_pr
            result = await ircc_get_adhoc_pr(breakdown="category_1980")
        assert "_meta" in result

    @pytest.mark.asyncio
    async def test_fr_lang_returns_error(self):
        """lang='fr' returns INVALID_INPUT (English-only dataset)."""
        with patch(
            "mcp_canada.modules.ircc.tools.fetch_adhoc_pr",
            new_callable=AsyncMock,
            side_effect=ValueError("Language 'fr' not available"),
        ):
            from mcp_canada.modules.ircc.tools import ircc_get_adhoc_pr
            result = await ircc_get_adhoc_pr(breakdown="category_1980", lang="fr")
        assert result["error"]["code"] == "INVALID_INPUT"


# ---------------------------------------------------------------------------
# ircc_list_datasets
# ---------------------------------------------------------------------------

class TestIrccListDatasets:

    @pytest.mark.asyncio
    async def test_returns_dataset_list(self):
        """ircc_list_datasets returns _meta with list of datasets."""
        from mcp_canada.modules.ircc.tools import ircc_list_datasets
        result = await ircc_list_datasets()
        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) >= 10

    @pytest.mark.asyncio
    async def test_each_entry_has_required_fields(self):
        """Each dataset entry has dataset, breakdowns, and description."""
        from mcp_canada.modules.ircc.tools import ircc_list_datasets
        result = await ircc_list_datasets()
        for entry in result["data"]:
            assert "dataset" in entry
            assert "breakdowns" in entry
            assert isinstance(entry["breakdowns"], list)


# ---------------------------------------------------------------------------
# Docstring quality
# ---------------------------------------------------------------------------

class TestDocstringQuality:

    def _import_tools(self):
        import mcp_canada.modules.ircc.tools as m
        return m

    def _get_tool_names(self):
        return [
            "ircc_get_permanent_residents",
            "ircc_get_study_permits",
            "ircc_get_work_permits",
            "ircc_get_express_entry",
            "ircc_get_tr_to_pr",
            "ircc_get_asylum",
            "ircc_get_ops",
            "ircc_get_afghan",
            "ircc_get_adhoc_pr",
            "ircc_list_datasets",
        ]

    def test_all_tools_have_use_for_line(self):
        """All ircc_ tools have 'Use for:' in docstring."""
        m = self._import_tools()
        for name in self._get_tool_names():
            fn = getattr(m, name)
            doc = fn.__doc__ or ""
            assert "Use for:" in doc, f"{name} missing 'Use for:' in docstring"

    def test_all_tools_have_keywords_line(self):
        """All ircc_ tools have 'Keywords:' in docstring."""
        m = self._import_tools()
        for name in self._get_tool_names():
            fn = getattr(m, name)
            doc = fn.__doc__ or ""
            assert "Keywords:" in doc, f"{name} missing 'Keywords:' in docstring"

    def test_keywords_have_minimum_8_terms(self):
        """All ircc_ tools have at least 8 keywords."""
        m = self._import_tools()
        for name in self._get_tool_names():
            fn = getattr(m, name)
            doc = fn.__doc__ or ""
            kw_start = doc.find("Keywords:")
            if kw_start == -1:
                continue
            # Extract the keywords line (up to next line or end)
            kw_line = doc[kw_start + len("Keywords:"):].split("\n")[0].strip()
            # Remove trailing period if present
            kw_line = kw_line.rstrip(".")
            terms = [t.strip() for t in kw_line.split(",") if t.strip()]
            assert len(terms) >= 8, (
                f"{name} has only {len(terms)} keywords (need >=8): {terms}"
            )
