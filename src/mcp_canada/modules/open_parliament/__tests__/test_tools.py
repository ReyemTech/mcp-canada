"""Unit tests for Open Parliament @tool functions.

Tests are structured as:
- Happy path: tool returns make_response envelope with correct data shape
- Error paths: 404 returns make_error NOT_FOUND, generic exception returns UPSTREAM_ERROR
- Docstring quality: Keywords line, Use for line, >= 50 chars for BM25 compliance
- lang parameter: passed through to make_response / make_error
"""

import inspect
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_BILLS = [
    {
        "number": "C-11",
        "name": {"en": "Online Streaming Act"},
        "session": "44-1",
        "introduced": "2022-02-02",
        "sponsor_politician_url": "/politicians/trudeau/",
        "status": {"en": "Royal Assent"},
        "law": True,
    }
]

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

SAMPLE_POLITICIANS = [
    {
        "name": "Justin Trudeau",
        "current_party": {"short_name": {"en": "Liberal"}},
        "riding": {"name": {"en": "Papineau"}},
        "province": "QC",
        "current": True,
        "url": "/politicians/trudeau/",
    }
]

SAMPLE_VOTES = [
    {
        "number": 148,
        "date": "2023-03-28",
        "result": "Passed",
        "bill_url": "/bills/44-1/C-11/",
        "yea_total": 204,
        "nay_total": 117,
        "paired_total": 0,
    }
]

SAMPLE_DEBATES = [
    {
        "date": "2023-03-28",
        "politician_url": "/politicians/trudeau/",
        "content_en": "Mr. Speaker, this bill...",
        "content_fr": "Monsieur le Président, ce projet de loi...",
        "url": "/debates/2023-03-28/en/",
    }
]

SAMPLE_SEARCH = [
    {
        "politician_url": "/politicians/trudeau/",
        "content": "We are investing in...",
        "date": "2023-03-28",
        "url": "/debates/2023-03-28/en/",
    }
]


SAMPLE_BALLOTS = [
    {
        "vote_url": "/votes/44-1/333/",
        "politician_url": "/politicians/anna-roberts/",
        "politician_membership_url": "/politicians/memberships/4622/",
        "ballot": "No",
    },
    {
        "vote_url": "/votes/44-1/333/",
        "politician_url": "/politicians/ziad-aboultaif/",
        "politician_membership_url": "/politicians/memberships/4208/",
        "ballot": "No",
    },
]


def make_http_error(status_code: int) -> httpx.HTTPStatusError:
    """Create a mock httpx.HTTPStatusError."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    return httpx.HTTPStatusError(
        f"HTTP {status_code}",
        request=httpx.Request("GET", "https://api.openparliament.ca/"),
        response=mock_response,
    )


def import_tools():
    import mcp_canada.modules.open_parliament.tools as tools_mod
    return tools_mod


# ===========================================================================
# 1. parl_search_bills
# ===========================================================================

class TestParlSearchBills:

    @pytest.mark.asyncio
    async def test_returns_bill_list_in_envelope(self):
        """parl_search_bills returns make_response envelope with bill list."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_bills",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_BILLS, False)
            result = await tools.parl_search_bills()

        assert "_meta" in result
        assert "data" in result
        assert isinstance(result["data"], list)
        assert result["data"][0]["number"] == "C-11"

    @pytest.mark.asyncio
    async def test_handles_404_with_not_found_error(self):
        """parl_search_bills returns NOT_FOUND error on 404."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_bills",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = make_http_error(404)
            result = await tools.parl_search_bills()

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_handles_generic_exception_with_upstream_error(self):
        """parl_search_bills returns UPSTREAM_ERROR on generic exception."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_bills",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("Network error")
            result = await tools.parl_search_bills()

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passed_through(self):
        """lang parameter is passed through to make_response."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_bills",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_BILLS, False)
            result = await tools.parl_search_bills(lang="fr")

        assert result["_meta"]["lang"] == "fr"


# ===========================================================================
# 2. parl_get_bill_details
# ===========================================================================

class TestParlGetBillDetails:

    @pytest.mark.asyncio
    async def test_returns_bill_detail_in_envelope(self):
        """parl_get_bill_details returns make_response envelope with bill detail."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_bill_details",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_BILL_DETAIL, False)
            result = await tools.parl_get_bill_details(bill_id="44-1/C-11")

        assert "_meta" in result
        assert result["data"]["number"] == "C-11"

    @pytest.mark.asyncio
    async def test_handles_404_with_not_found_error(self):
        """parl_get_bill_details returns NOT_FOUND on 404."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_bill_details",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = make_http_error(404)
            result = await tools.parl_get_bill_details(bill_id="99-9/X-999")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_handles_generic_exception(self):
        """parl_get_bill_details returns UPSTREAM_ERROR on generic exception."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_bill_details",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("Timeout")
            result = await tools.parl_get_bill_details(bill_id="44-1/C-11")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


# ===========================================================================
# 3. parl_get_politicians
# ===========================================================================

class TestParlGetPoliticians:

    @pytest.mark.asyncio
    async def test_returns_politician_list_in_envelope(self):
        """parl_get_politicians returns make_response with politician list."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_politicians",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_POLITICIANS, False)
            result = await tools.parl_get_politicians()

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert result["data"][0]["name"] == "Justin Trudeau"

    @pytest.mark.asyncio
    async def test_handles_404(self):
        """parl_get_politicians returns NOT_FOUND on 404."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_politicians",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = make_http_error(404)
            result = await tools.parl_get_politicians()

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_handles_generic_exception(self):
        """parl_get_politicians returns UPSTREAM_ERROR on generic exception."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_politicians",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("Server error")
            result = await tools.parl_get_politicians()

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


# ===========================================================================
# 4. parl_search_by_riding
# ===========================================================================

class TestParlSearchByRiding:

    @pytest.mark.asyncio
    async def test_returns_politician_list_filtered_by_riding(self):
        """parl_search_by_riding returns politicians for riding."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_politicians",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_POLITICIANS, False)
            result = await tools.parl_search_by_riding(riding="Papineau")

        assert "_meta" in result
        assert isinstance(result["data"], list)

        # Verify riding was passed to fetch_politicians
        mock_fetch.assert_called_once()
        call_kwargs = mock_fetch.call_args
        assert "riding" in str(call_kwargs) or call_kwargs[1].get("riding") == "Papineau"

    @pytest.mark.asyncio
    async def test_handles_404(self):
        """parl_search_by_riding returns NOT_FOUND on 404."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_politicians",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = make_http_error(404)
            result = await tools.parl_search_by_riding(riding="Unknown")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"


# ===========================================================================
# 5. parl_get_party_members
# ===========================================================================

class TestParlGetPartyMembers:

    @pytest.mark.asyncio
    async def test_returns_current_party_members(self):
        """parl_get_party_members returns current members for party."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_politicians",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_POLITICIANS, False)
            result = await tools.parl_get_party_members(party="Liberal")

        assert "_meta" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_passes_current_true_filter(self):
        """parl_get_party_members passes current=True to fetch_politicians."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_politicians",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_POLITICIANS, False)
            await tools.parl_get_party_members(party="Conservative")

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        # current=True should be passed
        assert call_args[1].get("current") is True or "True" in str(call_args)

    @pytest.mark.asyncio
    async def test_handles_404(self):
        """parl_get_party_members returns NOT_FOUND on 404."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_politicians",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = make_http_error(404)
            result = await tools.parl_get_party_members(party="Unknown")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"


# ===========================================================================
# 6. parl_get_votes
# ===========================================================================

class TestParlGetVotes:

    @pytest.mark.asyncio
    async def test_returns_vote_list_in_envelope(self):
        """parl_get_votes returns make_response with vote list."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_votes",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_VOTES, False)
            result = await tools.parl_get_votes()

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert result["data"][0]["number"] == 148

    @pytest.mark.asyncio
    async def test_handles_404(self):
        """parl_get_votes returns NOT_FOUND on 404."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_votes",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = make_http_error(404)
            result = await tools.parl_get_votes()

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_handles_generic_exception(self):
        """parl_get_votes returns UPSTREAM_ERROR on generic exception."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_votes",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("API error")
            result = await tools.parl_get_votes()

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


# ===========================================================================
# 7. parl_get_voting_record
# ===========================================================================

class TestParlGetVotingRecord:

    @pytest.mark.asyncio
    async def test_returns_voting_record_for_mp(self):
        """parl_get_voting_record returns votes for specified politician."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_votes",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_VOTES, False)
            result = await tools.parl_get_voting_record(politician="/politicians/trudeau/")

        assert "_meta" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_passes_politician_to_fetch_votes(self):
        """parl_get_voting_record passes politician param to fetch_votes."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_votes",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_VOTES, False)
            await tools.parl_get_voting_record(politician="/politicians/trudeau/")

        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "/politicians/trudeau/" in str(call_args)

    @pytest.mark.asyncio
    async def test_handles_404(self):
        """parl_get_voting_record returns NOT_FOUND on 404."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_votes",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = make_http_error(404)
            result = await tools.parl_get_voting_record(politician="/politicians/unknown/")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"


# ===========================================================================
# 8. parl_get_debates
# ===========================================================================

class TestParlGetDebates:

    @pytest.mark.asyncio
    async def test_returns_debate_list_in_envelope(self):
        """parl_get_debates returns make_response with debate list."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_debates",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_DEBATES, False)
            result = await tools.parl_get_debates()

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert result["data"][0]["date"] == "2023-03-28"

    @pytest.mark.asyncio
    async def test_handles_404(self):
        """parl_get_debates returns NOT_FOUND on 404."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_debates",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = make_http_error(404)
            result = await tools.parl_get_debates()

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_handles_generic_exception(self):
        """parl_get_debates returns UPSTREAM_ERROR on generic exception."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_debates",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("Timeout")
            result = await tools.parl_get_debates()

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


# ===========================================================================
# 9. parl_search_hansard
# ===========================================================================

class TestParlSearchHansard:

    @pytest.mark.asyncio
    async def test_returns_search_results_in_envelope(self):
        """parl_search_hansard returns make_response with search results."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_hansard_search",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_SEARCH, False)
            result = await tools.parl_search_hansard(query="climate")

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert result["data"][0]["content"] == "We are investing in..."

    @pytest.mark.asyncio
    async def test_handles_404(self):
        """parl_search_hansard returns NOT_FOUND on 404."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_hansard_search",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = make_http_error(404)
            result = await tools.parl_search_hansard(query="climate")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_handles_generic_exception(self):
        """parl_search_hansard returns UPSTREAM_ERROR on generic exception."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_hansard_search",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("API unavailable")
            result = await tools.parl_search_hansard(query="housing")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_lang_passed_through(self):
        """lang parameter is passed through to make_response."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_hansard_search",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_SEARCH, False)
            result = await tools.parl_search_hansard(query="budget", lang="fr")

        assert result["_meta"]["lang"] == "fr"


# ===========================================================================
# 10. parl_get_ballots
# ===========================================================================

class TestParlGetBallots:

    @pytest.mark.asyncio
    async def test_returns_ballots_in_envelope(self):
        """parl_get_ballots returns make_response with ballot list."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_ballots",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_BALLOTS, False)
            result = await tools.parl_get_ballots(vote_id="44-1/333")

        assert "_meta" in result
        assert isinstance(result["data"], list)
        assert result["data"][0]["ballot"] == "No"
        assert result["data"][0]["politician_url"] == "/politicians/anna-roberts/"

    @pytest.mark.asyncio
    async def test_passes_vote_url_and_politician(self):
        """parl_get_ballots constructs correct vote_url and politician_url."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_ballots",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = ([SAMPLE_BALLOTS[0]], False)
            await tools.parl_get_ballots(vote_id="44-1/333", politician="anna-roberts")

        mock_fetch.assert_called_once()
        call_kwargs = mock_fetch.call_args
        assert "/votes/44-1/333/" in str(call_kwargs)
        assert "/politicians/anna-roberts/" in str(call_kwargs)

    @pytest.mark.asyncio
    async def test_handles_404(self):
        """parl_get_ballots returns NOT_FOUND on 404."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_ballots",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = make_http_error(404)
            result = await tools.parl_get_ballots(vote_id="99-99/999")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_handles_generic_exception(self):
        """parl_get_ballots returns UPSTREAM_ERROR on generic exception."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_ballots",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("API down")
            result = await tools.parl_get_ballots(vote_id="44-1/333")

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"

    @pytest.mark.asyncio
    async def test_without_politician_returns_all_ballots(self):
        """parl_get_ballots without politician returns all ballots for a vote."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_ballots",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_BALLOTS, False)
            result = await tools.parl_get_ballots(vote_id="44-1/333")

        assert len(result["data"]) == 2


# ===========================================================================
# Docstring quality checks (BM25 compliance)
# ===========================================================================

class TestDocstringQuality:
    """Verify all 10 tools have BM25-optimized docstrings."""

    TOOL_NAMES = [
        "parl_search_bills",
        "parl_get_bill_details",
        "parl_get_politicians",
        "parl_search_by_riding",
        "parl_get_party_members",
        "parl_get_votes",
        "parl_get_voting_record",
        "parl_get_debates",
        "parl_search_hansard",
        "parl_get_ballots",
    ]

    def _get_tool_func(self, name: str):
        tools = import_tools()
        return getattr(tools, name)

    def test_all_tools_have_keywords_line(self):
        """All 9 tools must have 'Keywords:' in their docstring for BM25 indexing."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            doc = inspect.getdoc(func) or ""
            assert "Keywords:" in doc, f"{name} missing 'Keywords:' line in docstring"

    def test_all_tools_have_use_for_line(self):
        """All 9 tools must have 'Use for:' in their docstring."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            doc = inspect.getdoc(func) or ""
            assert "Use for:" in doc, f"{name} missing 'Use for:' line in docstring"

    def test_all_tool_docstrings_at_least_50_chars(self):
        """All 9 tool docstrings must be >= 50 characters."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            doc = inspect.getdoc(func) or ""
            assert len(doc) >= 50, f"{name} docstring too short ({len(doc)} chars)"

    def test_all_tools_have_lang_parameter(self):
        """All 9 tools must accept lang: Literal['en', 'fr'] = 'en' parameter."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            sig = inspect.signature(func)
            assert "lang" in sig.parameters, f"{name} missing 'lang' parameter"
            param = sig.parameters["lang"]
            assert param.default == "en", f"{name} lang default should be 'en'"

    def test_all_tools_are_callable_async(self):
        """All 9 tool functions exist and are callable."""
        for name in self.TOOL_NAMES:
            func = self._get_tool_func(name)
            assert callable(func), f"{name} is not callable"


# ===========================================================================
# Envelope structure
# ===========================================================================

class TestEnvelopeStructure:

    @pytest.mark.asyncio
    async def test_success_response_has_meta_source_and_cached(self):
        """Success responses must have _meta.source and _meta.cached."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_bills",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_BILLS, False)
            result = await tools.parl_search_bills()

        assert "_meta" in result
        assert "source" in result["_meta"]
        assert "cached" in result["_meta"]

    @pytest.mark.asyncio
    async def test_error_response_has_code_and_message(self):
        """Error responses must have error.code and error.message."""
        tools = import_tools()
        with patch("mcp_canada.modules.open_parliament.tools.fetch_bills",
                   new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = make_http_error(404)
            result = await tools.parl_search_bills()

        assert "error" in result
        assert "code" in result["error"]
        assert "message" in result["error"]
