# pyright: reportAttributeAccessIssue=false
"""Unit tests for Calgary module prompts.py and resources.py."""

from __future__ import annotations

import pytest
import pytest_asyncio  # noqa: F401 — ensures asyncio mode available


class TestCalgaryPrompts:
    @pytest.mark.asyncio
    async def test_explore_open_data_returns_list_of_messages(self) -> None:
        from mcp_canada.modules.calgary.prompts import calgary_explore_open_data

        result = await calgary_explore_open_data(lang="en")
        assert isinstance(result, list)
        assert len(result) >= 2

    @pytest.mark.asyncio
    async def test_explore_open_data_roles(self) -> None:
        from mcp_canada.modules.calgary.prompts import calgary_explore_open_data

        result = await calgary_explore_open_data(lang="en")
        assert result[0].role == "user"
        assert result[1].role == "assistant"

    @pytest.mark.asyncio
    async def test_explore_open_data_references_tools(self) -> None:
        from mcp_canada.modules.calgary.prompts import calgary_explore_open_data

        result = await calgary_explore_open_data(lang="en")
        text = result[1].content.text if hasattr(result[1].content, "text") else str(result[1].content)
        assert "calgary_search_datasets" in text
        assert "calgary_get_dataset_details" in text
        assert "calgary_query_dataset" in text

    @pytest.mark.asyncio
    async def test_explore_open_data_bilingual(self) -> None:
        from mcp_canada.modules.calgary.prompts import calgary_explore_open_data

        en = await calgary_explore_open_data(lang="en")
        fr = await calgary_explore_open_data(lang="fr")
        en_text = en[0].content.text if hasattr(en[0].content, "text") else str(en[0].content)
        fr_text = fr[0].content.text if hasattr(fr[0].content, "text") else str(fr[0].content)
        assert en_text != fr_text

    @pytest.mark.asyncio
    async def test_quick_find_dataset_returns_str(self) -> None:
        from mcp_canada.modules.calgary.prompts import calgary_quick_find_dataset

        result = await calgary_quick_find_dataset(lang="en")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_quick_find_dataset_mentions_tool(self) -> None:
        from mcp_canada.modules.calgary.prompts import calgary_quick_find_dataset

        result = await calgary_quick_find_dataset(lang="en")
        assert "calgary_search_datasets" in result

    @pytest.mark.asyncio
    async def test_quick_find_dataset_bilingual(self) -> None:
        from mcp_canada.modules.calgary.prompts import calgary_quick_find_dataset

        en = await calgary_quick_find_dataset(lang="en")
        fr = await calgary_quick_find_dataset(lang="fr")
        assert en != fr


class TestCalgaryResources:
    @pytest.mark.asyncio
    async def test_portal_guide_returns_str(self) -> None:
        from mcp_canada.modules.calgary.resources import calgary_portal_guide

        result = await calgary_portal_guide()
        assert isinstance(result, str)
        assert len(result) > 100

    @pytest.mark.asyncio
    async def test_portal_guide_mentions_soql_params(self) -> None:
        from mcp_canada.modules.calgary.resources import calgary_portal_guide

        result = await calgary_portal_guide()
        assert "$where" in result
        assert "$select" in result
        assert "$order" in result
        assert "$limit" in result

    @pytest.mark.asyncio
    async def test_portal_guide_documents_socrata_not_ckan(self) -> None:
        from mcp_canada.modules.calgary.resources import calgary_portal_guide

        result = await calgary_portal_guide()
        assert "Socrata" in result
        assert "NOT CKAN" in result
