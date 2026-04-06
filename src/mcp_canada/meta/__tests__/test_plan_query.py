"""Unit tests for plan_query meta-tool."""

from unittest.mock import MagicMock, patch


class TestPlanQuery:
    """Tests for the plan_query meta-tool."""

    def _make_mock_tool(self, name: str, description: str) -> MagicMock:
        """Create a mock Tool object with name and description."""
        tool = MagicMock()
        tool.name = name
        tool.description = description
        return tool

    def _make_mock_components(self) -> dict:
        """Return a dict of mock tools simulating the modules directory."""
        tools = {
            "boc_get_exchange_rates": self._make_mock_tool(
                "boc_get_exchange_rates",
                "Get current exchange rates from Bank of Canada. "
                "Use for: fetching currency exchange rates, forex, CAD conversion. "
                "Keywords: exchange rates, currency, forex, CAD, USD, Bank of Canada, "
                "inflation, interest rates, monetary policy",
            ),
            "rcll_search_food_recalls": self._make_mock_tool(
                "rcll_search_food_recalls",
                "Search for food recalls from Health Canada. "
                "Use for: finding food safety recalls, contamination alerts, "
                "recall search by keyword. "
                "Keywords: food recall, contamination, health, safety, recall, "
                "allergy, bacteria, listeria",
            ),
            "parl_search_bills": self._make_mock_tool(
                "parl_search_bills",
                "Search parliamentary bills. "
                "Use for: finding legislation, bills, acts in Parliament. "
                "Keywords: parliament, bill, legislation, act, senate, house, law",
            ),
            "drug_search": self._make_mock_tool(
                "drug_search",
                "Search Health Canada drug database. "
                "Use for: finding drug information, medications, DIN numbers. "
                "Keywords: drug, medication, DIN, health canada, pharma, prescription",
            ),
        }
        return tools

    def test_returns_steps_for_valid_query(self) -> None:
        """plan_query('food recalls and inflation') returns steps with recall or boc tools."""
        from fastmcp.tools.base import Tool

        mock_components = self._make_mock_components()

        with patch(
            "mcp_canada.meta.plan_query.FileSystemProvider"
        ) as mock_fsp_class:
            mock_provider = MagicMock()
            mock_provider._components = {
                k: v for k, v in mock_components.items()
                if isinstance(v, MagicMock)
            }
            # Make the values look like Tool instances
            for tool_mock in mock_provider._components.values():
                tool_mock.__class__ = Tool

            mock_fsp_class.return_value = mock_provider

            import asyncio
            from mcp_canada.meta.plan_query import plan_query

            result = asyncio.run(plan_query("food recalls and inflation"))

        assert "_meta" in result
        assert "data" in result
        data = result["data"]
        assert "steps" in data
        assert "explanation" in data
        steps = data["steps"]
        assert isinstance(steps, list)
        # At least one step should contain a recall or boc tool
        tool_names = [s["tool"] for s in steps]
        assert any("recall" in name or "boc" in name for name in tool_names), (
            f"Expected recall or boc tool in steps, got: {tool_names}"
        )

    def test_output_schema(self) -> None:
        """plan_query result has 'steps' list of dicts with 'tool' and 'params' keys."""
        from fastmcp.tools.base import Tool

        mock_components = self._make_mock_components()

        with patch(
            "mcp_canada.meta.plan_query.FileSystemProvider"
        ) as mock_fsp_class:
            mock_provider = MagicMock()
            mock_provider._components = mock_components
            for tool_mock in mock_provider._components.values():
                tool_mock.__class__ = Tool
            mock_fsp_class.return_value = mock_provider

            import asyncio
            from mcp_canada.meta.plan_query import plan_query

            result = asyncio.run(plan_query("exchange rates"))

        data = result["data"]
        assert isinstance(data["steps"], list)
        assert isinstance(data["explanation"], str)
        for step in data["steps"]:
            assert "tool" in step
            assert "params" in step
            assert isinstance(step["tool"], str)
            assert isinstance(step["params"], dict)

    def test_empty_steps_for_unrecognizable_query(self) -> None:
        """plan_query('asdfghjkl gibberish') returns empty steps, not an error."""
        from fastmcp.tools.base import Tool

        mock_components = self._make_mock_components()

        with patch(
            "mcp_canada.meta.plan_query.FileSystemProvider"
        ) as mock_fsp_class:
            mock_provider = MagicMock()
            mock_provider._components = mock_components
            for tool_mock in mock_provider._components.values():
                tool_mock.__class__ = Tool
            mock_fsp_class.return_value = mock_provider

            import asyncio
            from mcp_canada.meta.plan_query import plan_query

            result = asyncio.run(plan_query("asdfghjkl gibberish xyzzy qwerty"))

        # Should return a response envelope (not an error)
        assert "_meta" in result
        assert "data" in result
        data = result["data"]
        assert "steps" in data
        assert isinstance(data["steps"], list)
        assert len(data["steps"]) == 0
        assert "explanation" in data

    def test_respects_top_k(self) -> None:
        """plan_query with top_k=2 returns at most 2 steps."""
        from fastmcp.tools.base import Tool

        mock_components = self._make_mock_components()

        with patch(
            "mcp_canada.meta.plan_query.FileSystemProvider"
        ) as mock_fsp_class:
            mock_provider = MagicMock()
            mock_provider._components = mock_components
            for tool_mock in mock_provider._components.values():
                tool_mock.__class__ = Tool
            mock_fsp_class.return_value = mock_provider

            import asyncio
            from mcp_canada.meta.plan_query import plan_query

            result = asyncio.run(plan_query("drug food recall parliament", top_k=2))

        data = result["data"]
        assert len(data["steps"]) <= 2

    def test_returns_make_response_envelope(self) -> None:
        """plan_query result is wrapped in make_response with _meta containing source and cached."""
        from fastmcp.tools.base import Tool

        mock_components = self._make_mock_components()

        with patch(
            "mcp_canada.meta.plan_query.FileSystemProvider"
        ) as mock_fsp_class:
            mock_provider = MagicMock()
            mock_provider._components = mock_components
            for tool_mock in mock_provider._components.values():
                tool_mock.__class__ = Tool
            mock_fsp_class.return_value = mock_provider

            import asyncio
            from mcp_canada.meta.plan_query import plan_query

            result = asyncio.run(plan_query("exchange rates", lang="fr"))

        assert "_meta" in result
        meta = result["_meta"]
        assert "source" in meta
        assert "api" in meta["source"]
        assert "url" in meta["source"]
        assert "cached" in meta
        assert meta["cached"] is False
        assert meta["lang"] == "fr"
