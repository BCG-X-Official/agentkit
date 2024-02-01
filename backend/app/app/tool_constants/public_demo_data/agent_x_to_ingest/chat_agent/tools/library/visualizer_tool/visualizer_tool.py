# -*- coding: utf-8 -*-
import logging
import re
from typing import List, Optional, Tuple

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
    def from_config(cls, config: ToolConfig, **kwargs):
        llm = kwargs.get("llm", get_llm(config.default_llm))
        fast_llm = kwargs.get("fast_llm", get_llm(config.default_fast_llm))
        return cls(
            llm=llm,
            fast_llm=fast_llm,
            description=config.description.format(**{e.name: e.content for e in config.prompt_inputs}),
            prompt_message=config.prompt_message.format(**{e.name: e.content for e in config.prompt_inputs}),
            system_context=config.system_context.format(**{e.name: e.content for e in config.prompt_inputs}),
        )

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        try:
            if run_manager is not None:
                await run_manager.on_text(
                    "build_visualization",
                    data_type=StreamingDataTypeEnum.action,
                    tool=self.name,
                    step=1,
                )

            tool_input = ToolInputSchema.parse_raw(query)
            outputs = [f"{k}: {v}" for k, v in tool_input.intermediate_steps.items()]
            results = "\n".join(outputs[1:])
            messages = [
                SystemMessage(content=self.system_context.format()),
                HumanMessage(content=self.prompt_message.format(question=outputs[0], results=results)),
            ]
            result = await self._agenerate_response(messages, force_gpt4=True)

            is_valid = "jsx" in result

            if run_manager is not None:
                if is_valid:
                    await run_manager.on_text(
                        result,
                        data_type=StreamingDataTypeEnum.appendix,
                        tool=self.name,
                        step=1,
                        title=self.appendix_title,
                    )
                else:
                    await run_manager.on_text(
                        "no_data",
                        data_type=StreamingDataTypeEnum.action,
                        tool=self.name,
                        step=1,
                        result=result,
                    )
            return result
        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(e, tool=self.name)
                return repr(e)
            else:
                raise e

    async def _parse_inputs(self, response: str) -> Tuple[List[str], str]:
        pattern = r"^fields:\[\s*(?P<fields>.*)\]\s*description:\s*(?P<description>.*)$"
        match = re.search(pattern, response, flags=re.MULTILINE)
        fields = match.group("fields").split(",") if match else []
        description = match.group("description") if match else ""
        return (fields, description)
