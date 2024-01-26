# -*- coding: utf-8 -*-
# pylint: disable=cyclic-import
from typing import List, Tuple, Type

from langchain.tools import BaseTool

from app.services.chat_agent.tools.applications.project_scheduling.clarify_tool.clarify_tool import (
    ProjectSchedulingClarifyTool,
)
from app.services.chat_agent.tools.applications.project_scheduling.code_expert_tool.code_expert_tool import (
    CodeExpertTool,
)
from app.services.chat_agent.tools.applications.project_scheduling.code_search_tool.code_search_tool import (
    CodeSearchTool,
)
from app.services.chat_agent.tools.applications.project_scheduling.generate_config_tool.generate_config_tool import (
    ProjectSchedulingGenConfigTool,
)
from app.services.chat_agent.tools.applications.project_scheduling.generate_optim_input_tool.generate_optim_input_tool import (
    ProjectSchedulingGenOptimInputTool,
)
from app.services.chat_agent.tools.applications.project_scheduling.run_optimizer_tool.run_optimizer_tool import (
    ProjectSchedulingRunOptimizerTool,
)
from app.services.chat_agent.tools.applications.project_scheduling.sql_expert_tool.sql_expert_tool import SQLExpertTool
from app.services.chat_agent.tools.applications.project_scheduling.summarize_config_changes_tool.summarize_config_changes_tool import (
    ProjectSchedulingSummarizeConfigChangesTool,
)
from app.services.chat_agent.tools.applications.project_scheduling.summarize_kpi_tool.summarize_kpi_tool import (
    ProjectSchedulingSummarizeKPITool,
)
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool
from app.services.chat_agent.tools.library.basellm_tool.basellm_tool import BaseLLM
from app.services.chat_agent.tools.library.image_generation_tool.image_generation_tool import ImageGenerationTool
from app.services.chat_agent.tools.library.pdf_tool.pdf_tool import PDFTool
from app.services.chat_agent.tools.library.sql_tool.sql_tool import SQLTool
from app.services.chat_agent.tools.library.summarizer_tool.summarizer_tool import SummarizerTool
from app.services.chat_agent.tools.library.visualizer_tool.visualizer_tool import JsxVisualizerTool
from app.utils.config_loader import get_agent_config


def get_nested_classes() -> List[Tuple[str, Type[ExtendedBaseTool]]]:
    """separated to avoid circular imports."""
    from app.services.chat_agent.tools.library.chain_tool.nested_meta_agent_tool import (  # pylint: disable=import-outside-toplevel  # noqa:E501
        ChainTool,
    )

    nested_classes = [
        ("chain_tool", ChainTool),
    ]
    return nested_classes  # type: ignore


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
    all_tool_classes = [
        (
            "sql_tool",
            SQLTool,
        ),
        (
            "visualizer_tool",
            JsxVisualizerTool,
        ),
        (
            "summarizer_tool",
            SummarizerTool,
        ),
        (
            "pdf_tool",
            PDFTool,
        ),
        (
            "image_generation_tool",
            ImageGenerationTool,
        ),
        ("clarify_tool", BaseLLM),
        ("visualizer_tool", JsxVisualizerTool),
        ("summarizer_tool", SummarizerTool),
        ("expert_tool", BaseLLM),
        ("entertainer_tool", BaseLLM),
        ("generate_config_tool", ProjectSchedulingGenConfigTool),
        ("generate_optim_input_tool", ProjectSchedulingGenOptimInputTool),
        ("run_optimizer_tool", ProjectSchedulingRunOptimizerTool),
        ("summarize_config_changes_tool", ProjectSchedulingSummarizeConfigChangesTool),
        ("summarize_kpi_tool", ProjectSchedulingSummarizeKPITool),
        ("clarify_tool", ProjectSchedulingClarifyTool),
        ("pdf_tool", PDFTool),
        ("sql_tool", SQLTool),
        ("sql_expert_tool", SQLExpertTool),
        ("visualizer_tool", JsxVisualizerTool),
        ("code_search_tool", CodeSearchTool),
        ("code_expert_tool", CodeExpertTool),
    ]
    if load_nested:
        all_tool_classes.extend(get_nested_classes())
    all_tools: list[ExtendedBaseTool] = [
        c.from_config(  # type: ignore
            config=agent_config.tools_library.library[name],
            common_config=agent_config.common,
            **({"name": name} if issubclass(c, BaseLLM) else {}),
        )
        for (
            name,
            c,
        ) in all_tool_classes
        if name in agent_config.tools
    ]
    tools_map = {tool.name: tool for tool in all_tools}

    if any(tool_name not in tools_map for tool_name in tools):
        raise ValueError(f"Invalid tool name(s): {[tool_name for tool_name in tools if tool_name not in tools_map]}")

    return [tools_map[tool_name] for tool_name in tools]
