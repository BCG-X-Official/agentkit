# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from typing import Any, Optional

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.schema import HumanMessage, SystemMessage

from app.schemas.agent_schema import AgentAndToolsConfig
from app.schemas.streaming_schema import StreamingDataTypeEnum
from app.schemas.tool_schema import ToolConfig, ToolInputSchema
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool

logger = logging.getLogger(__name__)


class JsxVisualizerTool(ExtendedBaseTool):
    """Jsx Visualizer Tool."""

    name = "visualizer_tool"
    appendix_title = "Visualisation Appendix"

    @classmethod
    def from_config(
        cls,
        config: ToolConfig,
        common_config: AgentAndToolsConfig,
        **kwargs: Any,
    ) -> JsxVisualizerTool:
        llm = kwargs.get(
            "llm",
            get_llm(common_config.llm),
        )
        fast_llm = kwargs.get(
            "fast_llm",
            get_llm(common_config.fast_llm),
        )
        fast_llm_token_limit = kwargs.get(
            "fast_llm_token_limit",
            common_config.fast_llm_token_limit,
        )
        return cls(
            llm=llm,
            fast_llm=fast_llm,
            fast_llm_token_limit=fast_llm_token_limit,
            description=config.description.format(**{e.name: e.content for e in config.prompt_inputs}),
            prompt_message=config.prompt_message.format(**{e.name: e.content for e in config.prompt_inputs}),
            system_context=config.system_context.format(**{e.name: e.content for e in config.prompt_inputs}),
        )

    def _run(
        self,
        *args: Any,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> str:
        raise NotImplementedError("Tool does not support sync")

    async def _arun(
        self,
        *args: Any,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> str:
        """Use the tool asynchronously."""
        query = kwargs.get(
            "query",
            args[0],
        )

        try:
            if run_manager is not None:
                await run_manager.on_text(
                    "build_visualization",
                    data_type=StreamingDataTypeEnum.ACTION,
                    tool=self.name,
                    step=1,
                )

            tool_input = ToolInputSchema.parse_raw(query)
            if "sql_tool" in tool_input.intermediate_steps:
                results = tool_input.intermediate_steps["sql_tool"]
            else:  # no intermediate steps when using memory
                results = tool_input.chat_history[-1].content
            messages = [
                SystemMessage(content=self.system_context.format()),
                HumanMessage(
                    content=self.prompt_message.format(
                        question=tool_input.latest_human_message,
                        results=results,
                    )
                ),
            ]
            result = await self._agenerate_response(
                messages,
                discard_fast_llm=True,
            )

            is_valid = "jsx" in result

            if run_manager is not None:
                if is_valid:
                    await run_manager.on_text(
                        result,
                        data_type=StreamingDataTypeEnum.APPENDIX,
                        tool=self.name,
                        step=1,
                        title=self.appendix_title,
                    )
                else:
                    await run_manager.on_text(
                        "no_data",
                        data_type=StreamingDataTypeEnum.ACTION,
                        tool=self.name,
                        step=1,
                        result=result,
                    )
            return result
        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(
                    e,
                    tool=self.name,
                )
                return repr(e)
            raise e
