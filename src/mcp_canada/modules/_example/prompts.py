"""MCP prompts for the _example module — demonstrates the 7-file prompt pattern.

HOW TO USE THIS FILE:
1. Copy this file to your new module: src/mcp_canada/modules/{name}/prompts.py
2. Replace "example_" prefix with your module prefix (e.g., boc_, toronto_, statcan_)
3. Implement real workflows using your module's tools
4. FileSystemProvider auto-discovers @prompt decorated functions — no server.py changes needed

PATTERN OVERVIEW:
- Guided workflow prompts return list[Message] with user + assistant roles
  Use when agents need step-by-step tool chaining (multi-turn conversation setup)
- Quick lookup prompts return str (single instruction)
  Use for common one-shot queries where the agent just needs to know which tool + params

NAMING CONVENTION:
- Use module prefix: boc_analyze_rates, toronto_explore_neighbourhoods, statcan_find_data
- Prefix distinguishes prompts from tools (boc_analyze_rates prompt vs boc_get_exchange_rates tool)
- Prompts are workflow templates; tools are API calls

BILINGUAL REQUIREMENT:
- All prompts must accept lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en"
- Return French content in the if lang == "fr": branch
- French and English content should be semantically equivalent

REAL-WORLD REFERENCE: src/mcp_canada/modules/bank_of_canada/prompts.py
"""

from typing import Annotated, Literal

from fastmcp.prompts import Message, prompt


# ---------------------------------------------------------------------------
# Pattern 1: Guided workflow prompt — returns list[Message]
# ---------------------------------------------------------------------------

@prompt
async def example_guided_workflow(
    # All prompts require this lang parameter with this exact Annotated form.
    # The Annotated description overrides the verbose JSON schema note FastMCP
    # would otherwise generate for Literal types in the agent UI.
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> list[Message]:
    """Guide an agent through a multi-step example data workflow.

    Replace this docstring with a description of what the workflow achieves
    and which tools it chains together.
    """
    if lang == "fr":
        return [
            # user message: ask the opening question to prime the conversation
            Message(
                "Quelle donnée souhaitez-vous explorer? "
                "Je peux récupérer des exemples via example_echo.",
                role="user",
            ),
            # assistant message: confirm the approach and name the tool(s)
            Message(
                "Je vais utiliser example_echo pour récupérer vos données. Commençons.",
                role="assistant",
            ),
        ]
    return [
        # user message: describes what the user is asking for
        Message(
            "What data would you like to explore? "
            "I can retrieve examples using example_echo.",
            role="user",
        ),
        # assistant message: confirms the plan and names the tool(s) to call
        Message(
            "I will use example_echo to retrieve your data. Let's get started.",
            role="assistant",
        ),
    ]


# ---------------------------------------------------------------------------
# Pattern 2: Quick lookup prompt — returns str
# ---------------------------------------------------------------------------

@prompt
async def example_quick_lookup(
    lang: Annotated[Literal["en", "fr"], "Language: 'en' or 'fr'"] = "en",
) -> str:
    """Quick instruction to retrieve a single example result.

    The returned string becomes a single user Message in the MCP protocol.
    It should name the exact tool and parameters the agent should call.
    """
    if lang == "fr":
        # Reference the tool name and key parameters explicitly
        return "Utilisez example_echo avec message='test' pour obtenir un exemple de réponse."
    return "Use example_echo with message='test' to retrieve an example response."
