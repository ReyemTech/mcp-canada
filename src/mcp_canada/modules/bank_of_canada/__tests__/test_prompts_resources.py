"""Unit tests for Bank of Canada prompts and resources."""

import json

import pytest
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.resources.function_resource import FunctionResource

from mcp_canada.modules.bank_of_canada.prompts import (
    boc_analyze_rates,
    boc_check_inflation,
    boc_compare_currencies,
    boc_explore_commodities,
    boc_get_policy_rate,
)
from mcp_canada.modules.bank_of_canada.resources import (
    boc_api_quirks_guide,
    boc_commodity_types,
    boc_currency_codes,
    boc_inflation_indicators,
    boc_interest_rate_types,
    boc_rate_report_template,
    boc_series_naming_guide,
)


class TestBocPrompts:
    """Tests for the 5 Bank of Canada @prompt functions."""

    # ------------------------------------------------------------------
    # boc_analyze_rates — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_analyze_rates_en_returns_two_messages(self):
        p = FunctionPrompt.from_function(boc_analyze_rates)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_analyze_rates_en_roles(self):
        p = FunctionPrompt.from_function(boc_analyze_rates)
        result = await p.render({"lang": "en"})
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_analyze_rates_en_references_tool(self):
        p = FunctionPrompt.from_function(boc_analyze_rates)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "boc_get_exchange_rates" in full_text

    @pytest.mark.asyncio
    async def test_analyze_rates_fr_returns_two_messages(self):
        p = FunctionPrompt.from_function(boc_analyze_rates)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_analyze_rates_fr_is_french(self):
        p = FunctionPrompt.from_function(boc_analyze_rates)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert "devises" in user_text or "taux" in user_text or "analyser" in user_text

    # ------------------------------------------------------------------
    # boc_get_policy_rate — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_policy_rate_en_returns_single_message(self):
        p = FunctionPrompt.from_function(boc_get_policy_rate)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_policy_rate_en_references_tool(self):
        p = FunctionPrompt.from_function(boc_get_policy_rate)
        result = await p.render({"lang": "en"})
        assert "boc_get_interest_rates" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_policy_rate_fr_returns_single_message(self):
        p = FunctionPrompt.from_function(boc_get_policy_rate)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_policy_rate_fr_is_french(self):
        p = FunctionPrompt.from_function(boc_get_policy_rate)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert "boc_get_interest_rates" in text
        assert "taux" in text or "Utilisez" in text or "directeur" in text

    # ------------------------------------------------------------------
    # boc_compare_currencies — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_compare_currencies_en_returns_messages(self):
        p = FunctionPrompt.from_function(boc_compare_currencies)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_compare_currencies_en_roles(self):
        p = FunctionPrompt.from_function(boc_compare_currencies)
        result = await p.render({"lang": "en"})
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_compare_currencies_en_references_tool(self):
        p = FunctionPrompt.from_function(boc_compare_currencies)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "boc_get_exchange_rates" in full_text

    @pytest.mark.asyncio
    async def test_compare_currencies_fr_is_french(self):
        p = FunctionPrompt.from_function(boc_compare_currencies)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("devises", "comparer", "période", "période", "Quelles")
        )

    # ------------------------------------------------------------------
    # boc_explore_commodities — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_explore_commodities_en_returns_messages(self):
        p = FunctionPrompt.from_function(boc_explore_commodities)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_explore_commodities_en_references_tools(self):
        p = FunctionPrompt.from_function(boc_explore_commodities)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "boc_get_commodity_prices" in full_text

    @pytest.mark.asyncio
    async def test_explore_commodities_fr_is_french(self):
        p = FunctionPrompt.from_function(boc_explore_commodities)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("matières", "produits", "commodités", "explorer", "BCPI")
        )

    # ------------------------------------------------------------------
    # boc_check_inflation — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_check_inflation_en_returns_single_message(self):
        p = FunctionPrompt.from_function(boc_check_inflation)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_check_inflation_en_references_tool(self):
        p = FunctionPrompt.from_function(boc_check_inflation)
        result = await p.render({"lang": "en"})
        assert "boc_get_inflation_data" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_check_inflation_fr_is_french(self):
        p = FunctionPrompt.from_function(boc_check_inflation)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert "boc_get_inflation_data" in text
        assert "inflation" in text or "IPC" in text or "Utilisez" in text


class TestBocResources:
    """Tests for the 7 Bank of Canada @resource functions."""

    # ------------------------------------------------------------------
    # data://boc/currency-codes
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_currency_codes_is_valid_json(self):
        r = FunctionResource.from_function(
            boc_currency_codes, uri="data://boc/currency-codes"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_currency_codes_has_usd_eur_gbp(self):
        r = FunctionResource.from_function(
            boc_currency_codes, uri="data://boc/currency-codes"
        )
        content = await r.read()
        data = json.loads(content)
        for code in ("USD", "EUR", "GBP"):
            assert code in data, f"Missing currency code: {code}"

    @pytest.mark.asyncio
    async def test_currency_codes_has_bilingual_labels(self):
        r = FunctionResource.from_function(
            boc_currency_codes, uri="data://boc/currency-codes"
        )
        content = await r.read()
        data = json.loads(content)
        usd = data["USD"]
        assert "en" in usd
        assert "fr" in usd

    # ------------------------------------------------------------------
    # data://boc/interest-rate-types
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_interest_rate_types_is_valid_json(self):
        r = FunctionResource.from_function(
            boc_interest_rate_types, uri="data://boc/interest-rate-types"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_interest_rate_types_has_policy_key(self):
        r = FunctionResource.from_function(
            boc_interest_rate_types, uri="data://boc/interest-rate-types"
        )
        content = await r.read()
        data = json.loads(content)
        assert "policy" in data
        assert "en" in data["policy"]
        assert "fr" in data["policy"]

    # ------------------------------------------------------------------
    # data://boc/commodity-types
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_commodity_types_is_valid_json(self):
        r = FunctionResource.from_function(
            boc_commodity_types, uri="data://boc/commodity-types"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_commodity_types_has_energy_and_metals(self):
        r = FunctionResource.from_function(
            boc_commodity_types, uri="data://boc/commodity-types"
        )
        content = await r.read()
        data = json.loads(content)
        for key in ("energy", "metals", "agriculture"):
            assert key in data, f"Missing commodity type: {key}"

    # ------------------------------------------------------------------
    # data://boc/inflation-indicators
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_inflation_indicators_is_valid_json(self):
        r = FunctionResource.from_function(
            boc_inflation_indicators, uri="data://boc/inflation-indicators"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_inflation_indicators_has_total_and_trim(self):
        r = FunctionResource.from_function(
            boc_inflation_indicators, uri="data://boc/inflation-indicators"
        )
        content = await r.read()
        data = json.loads(content)
        for key in ("total", "trim", "median"):
            assert key in data, f"Missing indicator: {key}"

    # ------------------------------------------------------------------
    # docs://boc/series-naming
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_series_naming_guide_is_markdown(self):
        r = FunctionResource.from_function(
            boc_series_naming_guide, uri="docs://boc/series-naming"
        )
        content = await r.read()
        assert content.startswith("#"), "Markdown guide must start with # heading"

    @pytest.mark.asyncio
    async def test_series_naming_guide_mentions_fxusdcad(self):
        r = FunctionResource.from_function(
            boc_series_naming_guide, uri="docs://boc/series-naming"
        )
        content = await r.read()
        assert "FXUSDCAD" in content

    # ------------------------------------------------------------------
    # docs://boc/api-quirks
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_api_quirks_is_markdown(self):
        r = FunctionResource.from_function(
            boc_api_quirks_guide, uri="docs://boc/api-quirks"
        )
        content = await r.read()
        assert content.startswith("#"), "API quirks guide must start with # heading"

    @pytest.mark.asyncio
    async def test_api_quirks_mentions_date_format(self):
        r = FunctionResource.from_function(
            boc_api_quirks_guide, uri="docs://boc/api-quirks"
        )
        content = await r.read()
        assert "date" in content.lower() or "YYYY" in content

    # ------------------------------------------------------------------
    # template://boc/rate-report
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_rate_report_template_is_markdown(self):
        r = FunctionResource.from_function(
            boc_rate_report_template, uri="template://boc/rate-report"
        )
        content = await r.read()
        assert content.startswith("#"), "Rate report template must start with # heading"

    @pytest.mark.asyncio
    async def test_rate_report_template_has_placeholders(self):
        r = FunctionResource.from_function(
            boc_rate_report_template, uri="template://boc/rate-report"
        )
        content = await r.read()
        assert "{" in content and "}" in content, "Template must have {placeholder} syntax"

    @pytest.mark.asyncio
    async def test_rate_report_template_has_currency_placeholder(self):
        r = FunctionResource.from_function(
            boc_rate_report_template, uri="template://boc/rate-report"
        )
        content = await r.read()
        assert "{currency}" in content or "{currencies}" in content

    # ------------------------------------------------------------------
    # Zero-param sanity — resources must have no parameters
    # ------------------------------------------------------------------

    def test_resources_have_zero_parameters(self):
        """All resource functions must be zero-parameter (not ResourceTemplate)."""
        import inspect

        resources = [
            boc_currency_codes,
            boc_interest_rate_types,
            boc_commodity_types,
            boc_inflation_indicators,
            boc_series_naming_guide,
            boc_api_quirks_guide,
            boc_rate_report_template,
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
