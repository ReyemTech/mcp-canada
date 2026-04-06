"""Unit tests for AQHI @tool functions."""

import pytest
from unittest.mock import AsyncMock, patch


SAMPLE_READINGS = [
    {
        "location_id": "ON106",
        "location_name": "Ottawa",
        "aqhi_value": 3.0,
        "datetime": "2026-04-05T10:00:00Z",
        "lat": 45.4,
        "lon": -75.7,
    }
]

SAMPLE_FORECAST_READINGS = [
    {
        "location_id": "ON106",
        "location_name": "Ottawa",
        "aqhi_value": 2.0,
        "datetime": "2026-04-05T12:00:00Z",
        "lat": 45.4,
        "lon": -75.7,
    }
]


class TestWxGetAqhi:
    """Tests for wx_get_aqhi tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """wx_get_aqhi returns make_response envelope with _meta on success."""
        from mcp_canada.modules.weather.aqhi.tools import wx_get_aqhi

        with patch(
            "mcp_canada.modules.weather.aqhi.tools.fetch_aqhi",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_READINGS, False)
            result = await wx_get_aqhi(lat=45.4, lon=-75.7)

        assert "_meta" in result
        assert result["_meta"]["source"]["api"] == "msc-geomet"
        assert "cached" in result["_meta"]
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_returns_error_when_no_readings(self):
        """wx_get_aqhi returns make_error when no AQHI data found."""
        from mcp_canada.modules.weather.aqhi.tools import wx_get_aqhi

        with patch(
            "mcp_canada.modules.weather.aqhi.tools.fetch_aqhi",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = ([], False)
            result = await wx_get_aqhi(lat=45.4, lon=-75.7)

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_lang_passed_to_envelope(self):
        """wx_get_aqhi passes lang parameter to _meta envelope."""
        from mcp_canada.modules.weather.aqhi.tools import wx_get_aqhi

        with patch(
            "mcp_canada.modules.weather.aqhi.tools.fetch_aqhi",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_READINGS, False)
            result = await wx_get_aqhi(lat=45.4, lon=-75.7, lang="fr")

        assert result["_meta"]["lang"] == "fr"

    @pytest.mark.asyncio
    async def test_no_location_returns_error(self):
        """wx_get_aqhi returns INVALID_INPUT error when no location provided."""
        from mcp_canada.modules.weather.aqhi.tools import wx_get_aqhi

        result = await wx_get_aqhi()

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_exception_returns_upstream_error(self):
        """wx_get_aqhi returns UPSTREAM_ERROR when fetch_aqhi raises."""
        from mcp_canada.modules.weather.aqhi.tools import wx_get_aqhi

        with patch(
            "mcp_canada.modules.weather.aqhi.tools.fetch_aqhi",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.side_effect = Exception("Connection timeout")
            result = await wx_get_aqhi(lat=45.4, lon=-75.7)

        assert "error" in result
        assert result["error"]["code"] == "UPSTREAM_ERROR"


class TestWxGetAqhiForecast:
    """Tests for wx_get_aqhi_forecast tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """wx_get_aqhi_forecast returns make_response envelope on success."""
        from mcp_canada.modules.weather.aqhi.tools import wx_get_aqhi_forecast

        with patch(
            "mcp_canada.modules.weather.aqhi.tools.fetch_aqhi_forecast",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_FORECAST_READINGS, False)
            result = await wx_get_aqhi_forecast(lat=45.4, lon=-75.7)

        assert "_meta" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_returns_error_when_no_readings(self):
        """wx_get_aqhi_forecast returns make_error when no forecast found."""
        from mcp_canada.modules.weather.aqhi.tools import wx_get_aqhi_forecast

        with patch(
            "mcp_canada.modules.weather.aqhi.tools.fetch_aqhi_forecast",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = ([], False)
            result = await wx_get_aqhi_forecast(lat=45.4, lon=-75.7)

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_no_location_returns_error(self):
        """wx_get_aqhi_forecast returns INVALID_INPUT when no location given."""
        from mcp_canada.modules.weather.aqhi.tools import wx_get_aqhi_forecast

        result = await wx_get_aqhi_forecast()

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"


class TestWxGetAqhiHistory:
    """Tests for wx_get_aqhi_history tool."""

    @pytest.mark.asyncio
    async def test_returns_meta_envelope_on_success(self):
        """wx_get_aqhi_history returns make_response envelope with historical data."""
        from mcp_canada.modules.weather.aqhi.tools import wx_get_aqhi_history

        with patch(
            "mcp_canada.modules.weather.aqhi.tools.fetch_aqhi_history",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_READINGS, False)
            result = await wx_get_aqhi_history(location_id="ON106")

        assert "_meta" in result
        assert isinstance(result["data"], list)

    @pytest.mark.asyncio
    async def test_returns_error_when_no_history(self):
        """wx_get_aqhi_history returns NOT_FOUND when no historical data."""
        from mcp_canada.modules.weather.aqhi.tools import wx_get_aqhi_history

        with patch(
            "mcp_canada.modules.weather.aqhi.tools.fetch_aqhi_history",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = ([], False)
            result = await wx_get_aqhi_history(location_id="ON106")

        assert "error" in result
        assert result["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_lang_passed_to_envelope(self):
        """wx_get_aqhi_history passes lang parameter correctly."""
        from mcp_canada.modules.weather.aqhi.tools import wx_get_aqhi_history

        with patch(
            "mcp_canada.modules.weather.aqhi.tools.fetch_aqhi_history",
            new_callable=AsyncMock,
        ) as mock_fetch:
            mock_fetch.return_value = (SAMPLE_READINGS, True)
            result = await wx_get_aqhi_history(location_id="ON106", lang="fr")

        assert result["_meta"]["lang"] == "fr"
        assert result["_meta"]["cached"] is True


class TestDocstringQuality:
    """Verify BM25 docstring quality for all AQHI tools."""

    def _get_tool_functions(self):
        import mcp_canada.modules.weather.aqhi.tools as tools_mod
        import inspect
        return [
            obj for name, obj in inspect.getmembers(tools_mod, inspect.isfunction)
            if name.startswith("wx_")
        ]

    def test_all_tools_have_use_for_line(self):
        """All wx_ tools must have 'Use for:' in their docstring."""
        fns = self._get_tool_functions()
        assert len(fns) >= 3, "Expected at least 3 wx_ tool functions"
        for fn in fns:
            doc = fn.__doc__ or ""
            assert "Use for:" in doc, f"{fn.__name__} missing 'Use for:' in docstring"

    def test_all_tools_have_keywords_line(self):
        """All wx_ tools must have 'Keywords:' in their docstring for BM25."""
        fns = self._get_tool_functions()
        for fn in fns:
            doc = fn.__doc__ or ""
            assert "Keywords:" in doc, f"{fn.__name__} missing 'Keywords:' in docstring"

    def test_all_tools_have_lang_parameter(self):
        """All wx_ tools must accept a lang parameter."""
        import inspect
        import mcp_canada.modules.weather.aqhi.tools as tools_mod
        fns = [
            obj for name, obj in inspect.getmembers(tools_mod, inspect.isfunction)
            if name.startswith("wx_")
        ]
        for fn in fns:
            sig = inspect.signature(fn)
            assert "lang" in sig.parameters, f"{fn.__name__} missing lang parameter"
