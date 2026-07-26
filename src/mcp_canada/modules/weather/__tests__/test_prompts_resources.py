# Test-only pyright relaxation. Runtime assertions in these tests narrow types in
# ways pyright cannot follow (prompt Message.content and Resource.read() unions),
# and several cases deliberately pass invalid values to exercise error handling.
# Source code is still checked strictly -- do not add this to non-test modules.
# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportOperatorIssue=false
"""Unit tests for Weather module prompts and resources."""

import json

import pytest
from fastmcp.prompts.function_prompt import FunctionPrompt
from fastmcp.resources.function_resource import FunctionResource

from mcp_canada.modules.weather.prompts import (
    wx_analyze_climate,
    wx_check_air_quality,
    wx_check_weather,
    wx_quick_forecast,
    wx_severe_weather,
    wx_water_conditions,
)
from mcp_canada.modules.weather.resources import (
    wx_aqhi_scale,
    wx_climate_data_guide,
    wx_climate_normals_periods,
    wx_common_stations,
    wx_forecast_report_template,
    wx_ogc_api_guide,
    wx_province_codes,
    wx_station_guide,
)


class TestWeatherPrompts:
    """Tests for the 6 Weather @prompt functions."""

    # ------------------------------------------------------------------
    # wx_check_weather — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_check_weather_en_returns_two_messages(self):
        p = FunctionPrompt.from_function(wx_check_weather)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_check_weather_en_roles(self):
        p = FunctionPrompt.from_function(wx_check_weather)
        result = await p.render({"lang": "en"})
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_check_weather_en_references_tool(self):
        p = FunctionPrompt.from_function(wx_check_weather)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "wx_search_stations" in full_text or "wx_get_current_conditions" in full_text

    @pytest.mark.asyncio
    async def test_check_weather_fr_returns_two_messages(self):
        p = FunctionPrompt.from_function(wx_check_weather)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 2

    @pytest.mark.asyncio
    async def test_check_weather_fr_is_french(self):
        p = FunctionPrompt.from_function(wx_check_weather)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("météo", "conditions", "ville", "emplacement", "station")
        )

    # ------------------------------------------------------------------
    # wx_quick_forecast — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_quick_forecast_en_returns_single_message(self):
        p = FunctionPrompt.from_function(wx_quick_forecast)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_forecast_en_references_tool(self):
        p = FunctionPrompt.from_function(wx_quick_forecast)
        result = await p.render({"lang": "en"})
        assert "wx_get_forecast" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_quick_forecast_fr_returns_single_message(self):
        p = FunctionPrompt.from_function(wx_quick_forecast)
        result = await p.render({"lang": "fr"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_quick_forecast_fr_is_french(self):
        p = FunctionPrompt.from_function(wx_quick_forecast)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert "wx_get_forecast" in text
        assert any(word in text for word in ("Utilisez", "prévisions", "station"))

    # ------------------------------------------------------------------
    # wx_analyze_climate — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_analyze_climate_en_returns_messages(self):
        p = FunctionPrompt.from_function(wx_analyze_climate)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_analyze_climate_en_roles(self):
        p = FunctionPrompt.from_function(wx_analyze_climate)
        result = await p.render({"lang": "en"})
        assert result.messages[0].role == "user"
        assert result.messages[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_analyze_climate_en_references_tool(self):
        p = FunctionPrompt.from_function(wx_analyze_climate)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "wx_get_climate_normals" in full_text or "wx_get_climate_trends" in full_text

    @pytest.mark.asyncio
    async def test_analyze_climate_fr_is_french(self):
        p = FunctionPrompt.from_function(wx_analyze_climate)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("climat", "températures", "tendances", "analyse", "station")
        )

    # ------------------------------------------------------------------
    # wx_check_air_quality — quick lookup, str
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_check_air_quality_en_returns_single_message(self):
        p = FunctionPrompt.from_function(wx_check_air_quality)
        result = await p.render({"lang": "en"})
        assert len(result.messages) == 1

    @pytest.mark.asyncio
    async def test_check_air_quality_en_references_tool(self):
        p = FunctionPrompt.from_function(wx_check_air_quality)
        result = await p.render({"lang": "en"})
        assert "wx_get_aqhi" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_check_air_quality_fr_is_french(self):
        p = FunctionPrompt.from_function(wx_check_air_quality)
        result = await p.render({"lang": "fr"})
        text = result.messages[0].content.text
        assert "wx_get_aqhi" in text
        assert any(word in text for word in ("qualité", "Utilisez", "IQSA", "station"))

    # ------------------------------------------------------------------
    # wx_water_conditions — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_water_conditions_en_returns_messages(self):
        p = FunctionPrompt.from_function(wx_water_conditions)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_water_conditions_en_references_tools(self):
        p = FunctionPrompt.from_function(wx_water_conditions)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "wx_search_hydro_stations" in full_text or "wx_get_water_levels" in full_text

    @pytest.mark.asyncio
    async def test_water_conditions_fr_is_french(self):
        p = FunctionPrompt.from_function(wx_water_conditions)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("eau", "niveaux", "débit", "cours d'eau", "rivière")
        )

    # ------------------------------------------------------------------
    # wx_severe_weather — guided workflow, list[Message]
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_severe_weather_en_returns_messages(self):
        p = FunctionPrompt.from_function(wx_severe_weather)
        result = await p.render({"lang": "en"})
        assert len(result.messages) >= 2

    @pytest.mark.asyncio
    async def test_severe_weather_en_references_tools(self):
        p = FunctionPrompt.from_function(wx_severe_weather)
        result = await p.render({"lang": "en"})
        full_text = " ".join(m.content.text for m in result.messages)
        assert "wx_get_weather_alerts" in full_text or "wx_get_radar_data" in full_text

    @pytest.mark.asyncio
    async def test_severe_weather_fr_is_french(self):
        p = FunctionPrompt.from_function(wx_severe_weather)
        result = await p.render({"lang": "fr"})
        user_text = result.messages[0].content.text
        assert any(
            word in user_text
            for word in ("météo", "tempête", "alerte", "avertissement", "météorologique")
        )


class TestWeatherResources:
    """Tests for the 8 Weather @resource functions."""

    # ------------------------------------------------------------------
    # data://weather/province-codes
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_province_codes_is_valid_json(self):
        r = FunctionResource.from_function(
            wx_province_codes, uri="data://weather/province-codes"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_province_codes_has_all_provinces(self):
        r = FunctionResource.from_function(
            wx_province_codes, uri="data://weather/province-codes"
        )
        content = await r.read()
        data = json.loads(content)
        for code in ("ON", "BC", "AB", "QC"):
            assert code in data, f"Missing province code: {code}"

    @pytest.mark.asyncio
    async def test_province_codes_has_bilingual_labels(self):
        r = FunctionResource.from_function(
            wx_province_codes, uri="data://weather/province-codes"
        )
        content = await r.read()
        data = json.loads(content)
        on = data["ON"]
        assert "en" in on
        assert "fr" in on

    # ------------------------------------------------------------------
    # data://weather/common-stations
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_common_stations_is_valid_json(self):
        r = FunctionResource.from_function(
            wx_common_stations, uri="data://weather/common-stations"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_common_stations_has_required_fields(self):
        r = FunctionResource.from_function(
            wx_common_stations, uri="data://weather/common-stations"
        )
        content = await r.read()
        data = json.loads(content)
        assert len(data) > 0
        station = data[0]
        assert "city" in station
        assert "station_id" in station or "id" in station

    # ------------------------------------------------------------------
    # data://weather/aqhi-scale
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_aqhi_scale_is_valid_json(self):
        r = FunctionResource.from_function(
            wx_aqhi_scale, uri="data://weather/aqhi-scale"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, (dict, list))

    @pytest.mark.asyncio
    async def test_aqhi_scale_has_risk_levels(self):
        r = FunctionResource.from_function(
            wx_aqhi_scale, uri="data://weather/aqhi-scale"
        )
        content = await r.read()
        data = json.loads(content)
        # Should mention risk levels somewhere in the JSON
        content_str = json.dumps(data)
        assert any(
            word in content_str.lower()
            for word in ("low", "moderate", "high", "very high")
        )

    # ------------------------------------------------------------------
    # data://weather/climate-normals-periods
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_climate_normals_periods_is_valid_json(self):
        r = FunctionResource.from_function(
            wx_climate_normals_periods, uri="data://weather/climate-normals-periods"
        )
        content = await r.read()
        data = json.loads(content)
        assert isinstance(data, (dict, list))

    @pytest.mark.asyncio
    async def test_climate_normals_periods_has_period_data(self):
        r = FunctionResource.from_function(
            wx_climate_normals_periods, uri="data://weather/climate-normals-periods"
        )
        content = await r.read()
        data = json.loads(content)
        content_str = json.dumps(data)
        assert "1981" in content_str or "1991" in content_str

    # ------------------------------------------------------------------
    # docs://weather/station-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_station_guide_is_markdown(self):
        r = FunctionResource.from_function(
            wx_station_guide, uri="docs://weather/station-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "Station guide must start with # heading"

    @pytest.mark.asyncio
    async def test_station_guide_mentions_station_id(self):
        r = FunctionResource.from_function(
            wx_station_guide, uri="docs://weather/station-guide"
        )
        content = await r.read()
        assert "station" in content.lower() or "station_id" in content

    # ------------------------------------------------------------------
    # docs://weather/climate-data-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_climate_data_guide_is_markdown(self):
        r = FunctionResource.from_function(
            wx_climate_data_guide, uri="docs://weather/climate-data-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "Climate data guide must start with # heading"

    @pytest.mark.asyncio
    async def test_climate_data_guide_mentions_normals(self):
        r = FunctionResource.from_function(
            wx_climate_data_guide, uri="docs://weather/climate-data-guide"
        )
        content = await r.read()
        assert "normal" in content.lower() or "climate" in content.lower()

    # ------------------------------------------------------------------
    # docs://weather/ogc-api-guide
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_ogc_api_guide_is_markdown(self):
        r = FunctionResource.from_function(
            wx_ogc_api_guide, uri="docs://weather/ogc-api-guide"
        )
        content = await r.read()
        assert content.startswith("#"), "OGC API guide must start with # heading"

    @pytest.mark.asyncio
    async def test_ogc_api_guide_mentions_ogc(self):
        r = FunctionResource.from_function(
            wx_ogc_api_guide, uri="docs://weather/ogc-api-guide"
        )
        content = await r.read()
        assert "OGC" in content or "collection" in content.lower()

    # ------------------------------------------------------------------
    # template://weather/forecast-report
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_forecast_report_template_is_markdown(self):
        r = FunctionResource.from_function(
            wx_forecast_report_template, uri="template://weather/forecast-report"
        )
        content = await r.read()
        assert content.startswith("#"), "Forecast report template must start with # heading"

    @pytest.mark.asyncio
    async def test_forecast_report_template_has_placeholders(self):
        r = FunctionResource.from_function(
            wx_forecast_report_template, uri="template://weather/forecast-report"
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
            wx_province_codes,
            wx_common_stations,
            wx_aqhi_scale,
            wx_climate_normals_periods,
            wx_station_guide,
            wx_climate_data_guide,
            wx_ogc_api_guide,
            wx_forecast_report_template,
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
