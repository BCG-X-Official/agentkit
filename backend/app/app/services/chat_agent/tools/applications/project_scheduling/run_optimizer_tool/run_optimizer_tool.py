# -*- coding: utf-8 -*-
import logging
from typing import Any, Optional

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun

from app.opt.project_scheduling.run_schedule_optimization import run_scheduling_opt
from app.schemas.agent_schema import AgentAndToolsConfig
from app.schemas.streaming_schema import StreamingDataTypeEnum
from app.schemas.tool_schema import ToolConfig, ToolInputSchema
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.helpers.query_formatting import standard_query_format
from app.services.chat_agent.helpers.utils import get_conversation_id
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool

logger = logging.getLogger(__name__)


class ProjectSchedulingRunOptimizerTool(ExtendedBaseTool):
    name = "run_optimizer_tool"
    appendix_title = "KPIs of optimization run"

    @classmethod
    def from_config(cls, config: ToolConfig, common_config: AgentAndToolsConfig, **kwargs):
        llm = kwargs.get("llm", get_llm(common_config.llm))
        fast_llm = kwargs.get("fast_llm", get_llm(common_config.fast_llm))
        return cls(
            llm=llm,
            fast_llm=fast_llm,
            description=config.description.format(**{e.name: e.content for e in config.prompt_inputs}),
            prompt_message=config.prompt_message.format(**{e.name: e.content for e in config.prompt_inputs}),
            system_context=config.system_context.format(**{e.name: e.content for e in config.prompt_inputs}),
        )

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""

        raise NotImplementedError("ProjectSchedulingRunOptimizerTool does not support sync")

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
        query = standard_query_format(ToolInputSchema.parse_raw(query))
        try:
            if run_manager is not None:
                logger.info(f"Running Optimization model for {get_conversation_id(run_manager.tags)}")
                kpis, graphJSON = run_scheduling_opt(conversationId=get_conversation_id(run_manager.tags))

                # return kpis as str as input for summarize_kpi_tool
                response = str(kpis)
                logger.info("KPIs generated: {}".format(response))
                graphJSON = "```plotly" + graphJSON + "```"

                await run_manager.on_text(
                    graphJSON,
                    data_type=StreamingDataTypeEnum.APPENDIX,
                    tool=self.name,
                    step=1,
                    title="Visualization of optimization results",
                )
            return response
        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(e, tool=self.name)
                return repr(e)
            else:
                raise e
