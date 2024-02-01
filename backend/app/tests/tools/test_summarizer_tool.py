# -*- coding: utf-8 -*-
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain.base_language import BaseLanguageModel

from app.schemas.agent_schema import AgentConfig
from app.schemas.tool_schema import ToolInputSchema
from app.services.chat_agent.tools.library.summarizer_tool.summarizer_tool import SummarizerTool


@pytest.fixture(autouse=True)
def mock_llm_call(llm: BaseLanguageModel):  # pylint: disable=redefined-outer-name
    with patch("app.services.chat_agent.tools.library.summarizer_tool.summarizer_tool.get_llm", return_value=llm):
        yield


@pytest.fixture
def summarizer_tool_input(request) -> str:
    long = request.param
    latest_human_message = "This is a test message. "
    if long:
        latest_human_message *= 10000
    return ToolInputSchema(
        chat_history=[],
        latest_human_message=latest_human_message,
        intermediate_steps={},
    ).json()


@pytest.fixture
def summarizer_tool(agent_config: AgentConfig) -> SummarizerTool:
    summarizer_tool = SummarizerTool.from_config(
        config=agent_config.tools_library.library["summarizer_tool"], common_config=agent_config.common
    )
    return summarizer_tool


@pytest.mark.asyncio
@pytest.mark.parametrize("summarizer_tool_input", [False], indirect=True)
async def test_summarizer_tool_run_short_input(agent_config, summarizer_tool, summarizer_tool_input):
    query = summarizer_tool_input
    output = await summarizer_tool._arun(query)

    assert output == "0"


@pytest.mark.skip(reason="Need to install transformers package to Github workflows env.")
@pytest.mark.asyncio
@pytest.mark.parametrize("summarizer_tool_input", [True], indirect=True)
async def test_summarizer_tool_run_long_input(agent_config, summarizer_tool, summarizer_tool_input):
    query = summarizer_tool_input
    output = await summarizer_tool._arun(query)

    assert output == "0"
