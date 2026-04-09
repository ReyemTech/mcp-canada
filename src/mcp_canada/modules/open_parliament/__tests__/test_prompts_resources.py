"""Unit tests for Open Parliament prompts and resources."""

import json

import pytest
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.resources.function_resource import FunctionResource

from mcp_canada.modules.open_parliament.prompts import (
    parl_find_mp,
    parl_party_breakdown,
    parl_research_bill,
    parl_search_debates,
    parl_track_voting,
)
from mcp_canada.modules.open_parliament.resources import (
    parl_api_quirks_guide,
    parl_bill_types,
    parl_hansard_guide,
    parl_mp_profile_template,
    parl_party_codes,
    parl_session_format,
    parl_voting_guide,
)


class TestParlPrompts:
    """Tests for the 5 Open Parliament @prompt functions."""

    # ------------------------------------------------------------------
    # parl_research_bill — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_research_bill_en_returns_two_messages(self):
        p = FunctionPrompt.from_function(parl_research_bill)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_research_bill_en_roles(self):
        p = FunctionPrompt.from_function(parl_research_bill)
        result = await p.render({"lang": "en"})
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_research_bill_en_references_tools(self):
        p = FunctionPrompt.from_function(parl_research_bill)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "parl_search_bills" in full_text
        assert "parl_get_bill_details" in full_text

    @pytest.mark.asyncio
    async def test_research_bill_fr_returns_two_messages(self):
        p = FunctionPrompt.from_function(parl_research_bill)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_research_bill_fr_is_french(self):
        p = FunctionPrompt.from_function(parl_research_bill)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("projet", "loi", "rechercher", "Quel", "analyser")
        )

    # ------------------------------------------------------------------
    # parl_find_mp — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_find_mp_en_returns_single_message(self):
        p = FunctionPrompt.from_function(parl_find_mp)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_find_mp_en_references_tool(self):
        p = FunctionPrompt.from_function(parl_find_mp)
        result = await p.render({"lang": "en"})
        text = result.messages[0].content.text
        assert "parl_get_politicians" in text or "parl_search_by_riding" in text

    @pytest.mark.asyncio
    async def test_find_mp_fr_returns_single_message(self):
        p = FunctionPrompt.from_function(parl_find_mp)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_find_mp_fr_is_french(self):
        p = FunctionPrompt.from_function(parl_find_mp)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert any(
            word in text
            for word in ("député", "nom", "Utilisez", "circonscription", "code postal")
        )

    # ------------------------------------------------------------------
    # parl_track_voting — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_track_voting_en_returns_messages(self):
        p = FunctionPrompt.from_function(parl_track_voting)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_track_voting_en_references_tools(self):
        p = FunctionPrompt.from_function(parl_track_voting)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "parl_get_votes" in full_text

    @pytest.mark.asyncio
    async def test_track_voting_fr_is_french(self):
        p = FunctionPrompt.from_function(parl_track_voting)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("vote", "voter", "scrutin", "Quel", "suivi")
        )

    # ------------------------------------------------------------------
    # parl_search_debates — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_search_debates_en_returns_single_message(self):
        p = FunctionPrompt.from_function(parl_search_debates)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_search_debates_en_references_tool(self):
        p = FunctionPrompt.from_function(parl_search_debates)
        result = await p.render({"lang": "en"})
        assert "parl_search_hansard" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_search_debates_fr_is_french(self):
        p = FunctionPrompt.from_function(parl_search_debates)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert any(word in text for word in ("débats", "Hansard", "Utilisez", "mot-clé"))

    # ------------------------------------------------------------------
    # parl_party_breakdown — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_party_breakdown_en_returns_messages(self):
        p = FunctionPrompt.from_function(parl_party_breakdown)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_party_breakdown_en_references_tool(self):
        p = FunctionPrompt.from_function(parl_party_breakdown)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "parl_get_party_members" in full_text

    @pytest.mark.asyncio
    async def test_party_breakdown_fr_is_french(self):
        p = FunctionPrompt.from_function(parl_party_breakdown)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("parti", "partis", "représentation", "membres", "Quels")
        )


class TestParlResources:
    """Tests for the 7 Open Parliament @resource functions."""

    # ------------------------------------------------------------------
    # data://parliament/party-codes
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_party_codes_is_valid_json(self):
        r = FunctionResource.from_function(
            parl_party_codes, uri="data://parliament/party-codes"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_party_codes_has_major_parties(self):
        r = FunctionResource.from_function(
            parl_party_codes, uri="data://parliament/party-codes"
        )
        content = await r.read()
        data = json.loads(content)
        for code in ("CPC", "LPC", "NDP"):
            assert code in data, f"Missing party code: {code}"

    @pytest.mark.asyncio
    async def test_party_codes_has_bilingual_labels(self):
        r = FunctionResource.from_function(
            parl_party_codes, uri="data://parliament/party-codes"
        )
        content = await r.read()
        data = json.loads(content)
        cpc = data["CPC"]
        assert "en" in cpc
        assert "fr" in cpc

    # ------------------------------------------------------------------
    # data://parliament/session-format
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_session_format_is_valid_json(self):
        r = FunctionResource.from_function(
            parl_session_format, uri="data://parliament/session-format"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_session_format_explains_parliament_session(self):
        r = FunctionResource.from_function(
            parl_session_format, uri="data://parliament/session-format"
        )
        content = await r.read()
        data = json.loads(content)
        # Should explain the "44-1" format
        content_str = json.dumps(data)
        assert "44" in content_str or "parliament" in content_str.lower()

    # ------------------------------------------------------------------
    # data://parliament/bill-types
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_bill_types_is_valid_json(self):
        r = FunctionResource.from_function(
            parl_bill_types, uri="data://parliament/bill-types"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_bill_types_has_c_and_s_prefixes(self):
        r = FunctionResource.from_function(
            parl_bill_types, uri="data://parliament/bill-types"
        )
        content = await r.read()
        data = json.loads(content)
        keys = list(data.keys())
        assert any("C" in k or "House" in str(data[k]) for k in keys)

    # ------------------------------------------------------------------
    # docs://parliament/voting-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_voting_guide_is_markdown(self):
        r = FunctionResource.from_function(
            parl_voting_guide, uri="docs://parliament/voting-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "Markdown guide must start with # heading"

    @pytest.mark.asyncio
    async def test_voting_guide_mentions_ballot_types(self):
        r = FunctionResource.from_function(
            parl_voting_guide, uri="docs://parliament/voting-guide"
        )
        content = await r.read()
        assert "ballot" in content.lower() or "vote" in content.lower()

    # ------------------------------------------------------------------
    # docs://parliament/hansard-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_hansard_guide_is_markdown(self):
        r = FunctionResource.from_function(
            parl_hansard_guide, uri="docs://parliament/hansard-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "Hansard guide must start with # heading"

    @pytest.mark.asyncio
    async def test_hansard_guide_mentions_hansard(self):
        r = FunctionResource.from_function(
            parl_hansard_guide, uri="docs://parliament/hansard-guide"
        )
        content = await r.read()
        assert "Hansard" in content or "hansard" in content.lower()

    # ------------------------------------------------------------------
    # docs://parliament/api-quirks
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_api_quirks_is_markdown(self):
        r = FunctionResource.from_function(
            parl_api_quirks_guide, uri="docs://parliament/api-quirks"
        )
        content = await r.read()
        assert content.startswith("#"), "API quirks guide must start with # heading"

    # ------------------------------------------------------------------
    # template://parliament/mp-profile
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_mp_profile_template_is_markdown(self):
        r = FunctionResource.from_function(
            parl_mp_profile_template, uri="template://parliament/mp-profile"
        )
        content = await r.read()
        assert content.startswith("#"), "MP profile template must start with # heading"

    @pytest.mark.asyncio
    async def test_mp_profile_template_has_placeholders(self):
        r = FunctionResource.from_function(
            parl_mp_profile_template, uri="template://parliament/mp-profile"
        )
        content = await r.read()
        assert "{" in content and "}" in content, "Template must have {placeholder} syntax"

    # ------------------------------------------------------------------
    # Zero-param sanity
    # ------------------------------------------------------------------

    def test_resources_have_zero_parameters(self):
        """All resource functions must be zero-parameter (not ResourceTemplate)."""
        import inspect

        resources = [
            parl_party_codes,
            parl_session_format,
            parl_bill_types,
            parl_voting_guide,
            parl_hansard_guide,
            parl_api_quirks_guide,
            parl_mp_profile_template,
        ]
        for fn in resources:
            sig = inspect.signature(fn)
            params = [
                name
                for name, p in sig.parameters.items()
                if p.default is inspect.Parameter.empty
            ]
            assert params == [], (
                f"{fn.__name__} has required parameters {params}; "
                "resources must be zero-param functions"
            )
