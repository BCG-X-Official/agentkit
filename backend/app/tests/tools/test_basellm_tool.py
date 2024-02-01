# -*- coding: utf-8 -*-
from unittest.mock import patch

import pytest
from langchain.base_language import BaseLanguageModel

from app.schemas.agent_schema import AgentConfig
from app.services.chat_agent.tools.library.basellm_tool.basellm_tool import BaseLLM


@pytest.fixture(autouse=True)
def mock_llm_call(llm: BaseLanguageModel):  # pylint: disable=redefined-outer-name
    with patch("app.services.chat_agent.tools.library.basellm_tool.basellm_tool.get_llm", return_value=llm):
        yield


@pytest.fixture
def basellm_tool(agent_config: AgentConfig) -> BaseLLM:
    basellm_tool = BaseLLM.from_config(
        config=agent_config.tools_library.library["expert_tool"], common_config=agent_config.common
    )
    return basellm_tool


@pytest.mark.asyncio
async def test_basellm_tool_run(basellm_tool: BaseLLM, tool_input: str):
    query = tool_input
    output = await basellm_tool._arun(query)

    assert output == "0"
