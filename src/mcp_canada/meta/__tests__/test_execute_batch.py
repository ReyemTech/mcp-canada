"""Unit tests for execute_batch meta-tool."""

from unittest.mock import AsyncMock, MagicMock

import pytest


def _make_ctx(tool_results: dict | None = None, raise_for: dict | None = None) -> MagicMock:
    """Create a mock fastmcp context with configurable call_tool behavior."""
    ctx = MagicMock()
    ctx.fastmcp = MagicMock()

    async def mock_call_tool(name: str, arguments: dict) -> dict:
        if raise_for and name in raise_for:
            raise raise_for[name]
        if tool_results and name in tool_results:
            return tool_results[name]
        return {"_meta": {}, "data": f"result_from_{name}"}

    ctx.fastmcp.call_tool = AsyncMock(side_effect=mock_call_tool)
    return ctx


class TestExecuteBatch:
    """Tests for the execute_batch meta-tool."""

    @pytest.mark.asyncio
    async def test_runs_all_steps_returns_results(self) -> None:
        """Given 2 valid tool calls, returns results list with status 'ok' for each."""
        from mcp_canada.meta.execute_batch import execute_batch

        ctx = _make_ctx(
            tool_results={
                "boc_get_exchange_rates": {"_meta": {}, "data": {"rate": 1.35}},
                "rcll_search_food_recalls": {"_meta": {}, "data": []},
            }
        )
        calls = [
            {"tool": "boc_get_exchange_rates", "params": {"currency": "USD"}},
            {"tool": "rcll_search_food_recalls", "params": {"keyword": "listeria"}},
        ]
        result = await execute_batch(calls, ctx=ctx)

        assert "_meta" in result
        assert "data" in result
        data = result["data"]
        assert "results" in data
        assert "summary" in data
        assert len(data["results"]) == 2
        for r in data["results"]:
            assert r["status"] == "ok"

    @pytest.mark.asyncio
    async def test_partial_results_on_failure(self) -> None:
        """Given 1 valid + 1 failing tool call, returns ok for first and error for second."""
        from mcp_canada.meta.execute_batch import execute_batch

        ctx = _make_ctx(
            tool_results={
                "boc_get_exchange_rates": {"_meta": {}, "data": {"rate": 1.35}},
            },
            raise_for={
                "bad_tool_name": ValueError("Tool not found: bad_tool_name"),
            },
        )
        calls = [
            {"tool": "boc_get_exchange_rates", "params": {}},
            {"tool": "bad_tool_name", "params": {}},
        ]
        result = await execute_batch(calls, ctx=ctx)

        data = result["data"]
        results = data["results"]
        assert len(results) == 2

        ok_result = next(r for r in results if r["tool"] == "boc_get_exchange_rates")
        err_result = next(r for r in results if r["tool"] == "bad_tool_name")

        assert ok_result["status"] == "ok"
        assert err_result["status"] == "error"
        assert "error" in err_result

        summary = data["summary"]
        assert summary["succeeded"] == 1
        assert summary["failed"] == 1
        assert summary["total"] == 2

    @pytest.mark.asyncio
    async def test_accepts_plan_query_output(self) -> None:
        """Input is {'steps': [...], 'explanation': '...'} dict — extracts steps and runs them."""
        from mcp_canada.meta.execute_batch import execute_batch

        ctx = _make_ctx(
            tool_results={
                "boc_get_exchange_rates": {"_meta": {}, "data": {"rate": 1.35}},
            }
        )
        # Simulate raw plan_query output (not wrapped in make_response)
        plan_output = {
            "steps": [{"tool": "boc_get_exchange_rates", "params": {}}],
            "explanation": "Fetches exchange rate",
        }
        result = await execute_batch(plan_output, ctx=ctx)

        assert "_meta" in result
        data = result["data"]
        assert len(data["results"]) == 1
        assert data["results"][0]["status"] == "ok"

    @pytest.mark.asyncio
    async def test_accepts_plan_query_make_response_output(self) -> None:
        """Input is make_response-wrapped plan_query output — extracts data.steps."""
        from mcp_canada.meta.execute_batch import execute_batch

        ctx = _make_ctx(
            tool_results={
                "boc_get_exchange_rates": {"_meta": {}, "data": {"rate": 1.35}},
            }
        )
        # Simulate make_response-wrapped plan_query output
        plan_output = {
            "_meta": {"source": {"api": "mcp-canada", "url": "internal://plan_query"}, "cached": False, "lang": "en"},
            "data": {
                "steps": [{"tool": "boc_get_exchange_rates", "params": {}}],
                "explanation": "Fetches exchange rate",
            },
        }
        result = await execute_batch(plan_output, ctx=ctx)

        assert "_meta" in result
        data = result["data"]
        assert len(data["results"]) == 1
        assert data["results"][0]["status"] == "ok"

    @pytest.mark.asyncio
    async def test_accepts_raw_list(self) -> None:
        """Input is [{'tool': '...', 'params': {...}}] list — runs directly."""
        from mcp_canada.meta.execute_batch import execute_batch

        ctx = _make_ctx(
            tool_results={
                "boc_get_exchange_rates": {"_meta": {}, "data": {"rate": 1.35}},
            }
        )
        calls = [{"tool": "boc_get_exchange_rates", "params": {"currency": "USD"}}]
        result = await execute_batch(calls, ctx=ctx)

        assert "_meta" in result
        data = result["data"]
        assert len(data["results"]) == 1
        assert data["results"][0]["status"] == "ok"

    @pytest.mark.asyncio
    async def test_rejects_invalid_input(self) -> None:
        """Input is neither dict-with-steps nor list — returns make_error INVALID_INPUT."""
        from mcp_canada.meta.execute_batch import execute_batch

        ctx = _make_ctx()
        result = await execute_batch("not_a_valid_input", ctx=ctx)  # type: ignore[arg-type]

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_filters_meta_tools(self) -> None:
        """Steps containing meta tool names are rejected with per-step error."""
        from mcp_canada.meta.execute_batch import execute_batch

        ctx = _make_ctx(
            tool_results={
                "boc_get_exchange_rates": {"_meta": {}, "data": {"rate": 1.35}},
            }
        )
        calls = [
            {"tool": "boc_get_exchange_rates", "params": {}},
            {"tool": "call_tool", "params": {}},
            {"tool": "discover_tools", "params": {}},
            {"tool": "plan_query", "params": {}},
            {"tool": "execute_batch", "params": {}},
        ]
        result = await execute_batch(calls, ctx=ctx)

        data = result["data"]
        results = data["results"]
        assert len(results) == 5

        ok_result = next(r for r in results if r["tool"] == "boc_get_exchange_rates")
        assert ok_result["status"] == "ok"

        for meta_tool in ["call_tool", "discover_tools", "plan_query", "execute_batch"]:
            meta_result = next(r for r in results if r["tool"] == meta_tool)
            assert meta_result["status"] == "error", f"{meta_tool} should be rejected"

    @pytest.mark.asyncio
    async def test_max_batch_size(self) -> None:
        """More than 10 steps returns make_error INVALID_INPUT."""
        from mcp_canada.meta.execute_batch import execute_batch

        ctx = _make_ctx()
        calls = [{"tool": f"tool_{i}", "params": {}} for i in range(11)]
        result = await execute_batch(calls, ctx=ctx)

        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"

    @pytest.mark.asyncio
    async def test_returns_summary(self) -> None:
        """Result includes summary with total/succeeded/failed counts."""
        from mcp_canada.meta.execute_batch import execute_batch

        ctx = _make_ctx(
            tool_results={
                "tool_a": {"_meta": {}, "data": "a"},
                "tool_b": {"_meta": {}, "data": "b"},
            },
            raise_for={
                "tool_c": RuntimeError("tool_c failed"),
            },
        )
        calls = [
            {"tool": "tool_a", "params": {}},
            {"tool": "tool_b", "params": {}},
            {"tool": "tool_c", "params": {}},
        ]
        result = await execute_batch(calls, ctx=ctx)

        data = result["data"]
        summary = data["summary"]
        assert summary["total"] == 3
        assert summary["succeeded"] == 2
        assert summary["failed"] == 1
