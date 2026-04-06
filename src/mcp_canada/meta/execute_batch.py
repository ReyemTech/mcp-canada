"""execute_batch meta-tool — parallel tool dispatcher with per-step error isolation."""

import asyncio
from typing import Literal

from fastmcp import Context
from fastmcp.tools import tool

from mcp_canada.shared.envelope import make_error, make_response

# Meta-tool names that must not be dispatched through execute_batch
# (would create self-referential or recursive calls)
_META_TOOL_NAMES = frozenset({"call_tool", "discover_tools", "plan_query", "execute_batch"})

# Maximum number of steps allowed per batch
_MAX_BATCH_SIZE = 10


@tool(name="execute_batch", tags={"meta", "batch", "parallel"})
async def execute_batch(
    calls: list[dict] | dict,
    lang: Literal["en", "fr"] = "en",
    ctx: Context = None,  # type: ignore[assignment]
) -> dict:
    """Execute multiple tool calls in parallel and return aggregated results.

    Accepts either a plan_query output (dict with 'steps' key) or a raw list
    of tool call objects. Runs all valid steps in parallel using asyncio.gather
    with per-step error isolation — one failed step does not cancel others.

    Use for: running multiple tool calls at once, executing a plan from
    plan_query, batch queries across multiple APIs, parallel data fetching,
    multi-source aggregation.

    Keywords: batch, execute, parallel, multiple tools, run plan, aggregate,
    multi-step, concurrent, simultaneous, gather, dispatch, bulk, workflow
    """
    # Discriminate input: plan_query output (dict with steps), make_response
    # wrapped plan output (dict with data.steps), or raw list
    steps: list[dict]

    if isinstance(calls, dict):
        # Case 1: make_response-wrapped plan_query output: {"_meta": ..., "data": {"steps": [...]}}
        if "data" in calls and isinstance(calls["data"], dict) and "steps" in calls["data"]:
            steps = calls["data"]["steps"]
        # Case 2: raw plan_query output: {"steps": [...], "explanation": "..."}
        elif "steps" in calls:
            steps = calls["steps"]
        else:
            return make_error(
                "INVALID_INPUT",
                "Expected plan_query output dict with 'steps' key, or a list of tool calls",
                lang=lang,
            )
    elif isinstance(calls, list):
        steps = calls
    else:
        return make_error(
            "INVALID_INPUT",
            "Expected plan_query output dict with 'steps' key, or a list of tool calls",
            lang=lang,
        )

    # Validate batch size
    if len(steps) > _MAX_BATCH_SIZE:
        return make_error(
            "INVALID_INPUT",
            f"Maximum {_MAX_BATCH_SIZE} steps per batch, got {len(steps)}",
            lang=lang,
        )

    # Run all steps in parallel; meta-tool calls get per-step errors
    async def _run_step(step: dict) -> dict:
        tool_name = step.get("tool", "")
        params = step.get("params", {})

        # Filter meta-tools: return per-step error (not silently skip)
        if tool_name in _META_TOOL_NAMES:
            return {
                "tool": tool_name,
                "status": "error",
                "error": (
                    f"'{tool_name}' is a meta-tool and cannot be called via execute_batch"
                ),
            }

        try:
            result = await ctx.fastmcp.call_tool(tool_name, params)
            return {"tool": tool_name, "status": "ok", "data": result}
        except Exception as exc:
            return {"tool": tool_name, "status": "error", "error": str(exc)}

    # asyncio.gather with return_exceptions=True — per Pitfall 3, check BaseException
    raw_results = await asyncio.gather(
        *[_run_step(step) for step in steps],
        return_exceptions=True,
    )

    results: list[dict] = []
    for i, raw in enumerate(raw_results):
        if isinstance(raw, BaseException):
            # Unexpected exception from _run_step itself (not the tool call)
            tool_name = steps[i].get("tool", "unknown") if i < len(steps) else "unknown"
            results.append({
                "tool": tool_name,
                "status": "error",
                "error": str(raw),
            })
        else:
            results.append(raw)

    succeeded = sum(1 for r in results if r["status"] == "ok")
    failed = sum(1 for r in results if r["status"] == "error")

    return make_response(
        {
            "results": results,
            "summary": {
                "total": len(results),
                "succeeded": succeeded,
                "failed": failed,
            },
        },
        api_name="mcp-canada",
        api_url="internal://execute_batch",
        cached=False,
        lang=lang,
    )
