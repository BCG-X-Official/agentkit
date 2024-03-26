# -*- coding: utf-8 -*-
# pylint: disable=cyclic-import
import copy
from typing import List, Tuple, Type

from app.services.chat_agent.tools.library.basellm_tool.basellm_tool import BaseLLM
from langchain.tools import BaseTool

from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool
from app.utils.config_loader import get_agent_config

import importlib

import logging
logger = logging.getLogger(__name__)


STATIC_SET_OF_TOOLS = {
    "sql_tool": ["app.services.chat_agent.tools.library.sql_tool.sql_tool", "SQLTool"],
    "visualizer_tool": ["app.services.chat_agent.tools.library.visualizer_tool.visualizer_tool", "JsxVisualizerTool"],
    "summarizer_tool": ["app.services.chat_agent.tools.library.summarizer_tool.summarizer_tool", "SummarizerTool"],
    "pdf_tool": ["app.services.chat_agent.tools.library.pdf_tool.pdf_tool", "PDFTool"],
    "image_generation_tool": ["app.services.chat_agent.tools.library.image_generation_tool.image_generation_tool", "ImageGenerationTool"],
    "clarify_tool": ["app.services.chat_agent.tools.library.basellm_tool.basellm_tool", "BaseLLM"],
    "expert_tool": ["app.services.chat_agent.tools.library.basellm_tool.basellm_tool", "BaseLLM"],
    "entertainer_tool": ["app.services.chat_agent.tools.library.basellm_tool.basellm_tool", "BaseLLM"],
}


def get_tools(tools: List[str], load_nested: bool = True) -> List[BaseTool]:
    """
    Retrieves the tools based on a list of tool names.

    This function takes a list of tool names and returns a list of BaseTool objects.
    It first gets the agent configuration and a list of all available tool classes. It then creates a list of all tools
    specified in the agent configuration. If any tool name in the input list is not in the list of all tools,
    it raises a ValueError.

    Args:
        tools (list[str]): The list of tool names.
        load_nested (bool): Whether to load nested chains too. Included to avoid circular imports

    Returns:
        list[BaseTool]: The list of BaseTool objects.

    Raises:
        ValueError: If any tool name in the input list is not in the list of all tools.
    """
    agent_config = get_agent_config()
    static_set_of_tools = copy.deepcopy(STATIC_SET_OF_TOOLS)

    if load_nested:
        static_set_of_tools["chain_tool"] = ["app.services.chat_agent.tools.library.chain_tool.nested_meta_agent_tool", "ChainTool"]

    # first consolidate all tools classes.
    all_tool_classes = {}
    for tool_name in tools:
        # if the tool has a class_name definition I pick it, client comes first :) 
        if configured_classname := agent_config.tools_library.library[tool_name].class_name:
            module_name ,class_name = configured_classname.split(":")
            logger.debug("Loading CustomTool %s from module %s with class %s", tool_name, module_name, class_name)

        else:
            # otherwise I pick it from the static set of tools. 
            module_name ,class_name = static_set_of_tools[tool_name]
            logger.debug("Loading AgentKit tool class %s from module %s with class %s", tool_name, module_name, class_name)
        
        # import the module and hook the class

        module = importlib.import_module(f"{module_name}") 
        tool_class = getattr(module, class_name)

        # keep the class in a corner
        all_tool_classes[tool_name] = tool_class

    # then create the tools object by instanciating the classes
    all_tools: list[ExtendedBaseTool] = []
    for name, tool_class in all_tool_classes.items():
        if name in agent_config.tools:
            tool_instance = tool_class.from_config(  # type: ignore
                config=agent_config.tools_library.library[name],
                common_config=agent_config.common,
                **({"name": name} if issubclass(tool_class, BaseLLM) else {}),
            )
            logger.debug("Tool %s loaded, type: %s", name, type(tool_instance))
            all_tools.append(tool_instance)

    return all_tools
