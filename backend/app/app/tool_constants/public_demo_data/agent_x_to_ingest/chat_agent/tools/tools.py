# -*- coding: utf-8 -*-
from langchain.base_language import BaseLanguageModel
from langchain.tools import BaseTool

from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool
from app.services.chat_agent.tools.library.entertainer_tool.entertainer_tool import EntertainerTool
from app.services.chat_agent.tools.library.expert_tool.expert_tool import ExpertTool
from app.services.chat_agent.tools.library.image_gen_with_input_tool.image_gen_with_input_tool import (
    ImageGenerationWithInputTool,
)
from app.services.chat_agent.tools.library.image_generation_tool.image_generation_tool import ImageGenerationTool
from app.services.chat_agent.tools.library.pdf_tool.pdf_tool import PDFTool
from app.services.chat_agent.tools.library.sql_tool.sql_tool import SQLTool
from app.services.chat_agent.tools.library.summarizer_tool.summarizer_tool import SummarizerTool
from app.services.chat_agent.tools.library.visualizer_tool.visualizer_tool import JsxVisualizerTool
from app.utils.config_loader import get_agent_config


def get_tools(tools: list[str], llm: BaseLanguageModel, fast_llm: BaseLanguageModel) -> list[BaseTool]:
    """Get tools from a list of tool names."""
    agent_config = get_agent_config()
    all_tool_classes: list[tuple[str, ExtendedBaseTool]] = [
        ("sql_tool", SQLTool),
        ("visualizer_tool", JsxVisualizerTool),
        ("summarizer_tool", SummarizerTool),
        ("expert_tool", ExpertTool),
        ("entertainer_tool", EntertainerTool),
        ("pdf_tool", PDFTool),
        ("image_generation_tool", ImageGenerationTool),
        ("image_gen_with_input_tool", ImageGenerationWithInputTool),
    ]
    all_tools: list[ExtendedBaseTool] = [
        c.from_config(
            config=agent_config.tools_library.library[name],
            common_config=agent_config.common,
            llm=llm,
            fast_llm=fast_llm,
        )
        for (name, c) in all_tool_classes
        if name in agent_config.tools
    ]
    tools_map = {tool.name: tool for tool in all_tools}

    if any(tool_name not in tools_map for tool_name in tools):
        raise ValueError(f"Invalid tool name(s): {tools}")

    return [tools_map[tool_name] for tool_name in tools]
