# -*- coding: utf-8 -*-
from math import log
from unittest.mock import ANY, patch

import pytest
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun

from app.schemas.streaming_schema import StreamingDataTypeEnum
from app.services.chat_agent.tools.library.visualizer_tool.visualizer_tool import JsxVisualizerTool
from app.utils.config_loader import get_agent_config


@pytest.fixture(autouse=True)
def mock_llm_call(llm: BaseLanguageModel):  # pylint: disable=redefined-outer-name
    # Call the mocked LLM defined in conftest.py that returns a list of 0, 1 ...
    with patch("app.services.chat_agent.tools.library.visualizer_tool.visualizer_tool.get_llm", return_value=llm):
        yield


@pytest.mark.asyncio
async def test_visualizer_tool_arun(tool_input: str, run_manager: AsyncCallbackManagerForToolRun):
    """
    This tests the JsxVisualizerTool._arun() method. The goal of is to check if the tool
    can process input, call a (mocked) LLM and return its (mocked) output.

    Args:
        tool_input (str): Mock input for tools.
    """
    agent_config = get_agent_config()

    # Setup JsxVisualizerTool instance with mocked dependencies
    tool = JsxVisualizerTool.from_config(
        config=agent_config.tools_library.library["visualizer_tool"], common_config=agent_config.common
    )

    result = await tool._arun(tool_input, run_manager=run_manager)
    # Check getting mock LLM output
    assert result == "0"

    # Make sure the tool streams taking an action at least once, does not enforce correct vizualization output
    run_manager.on_text.assert_any_call(
        ANY,  # allow for any string
        data_type=StreamingDataTypeEnum.ACTION,
        tool=tool.name,
        step=ANY,
    )
