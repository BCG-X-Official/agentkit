# -*- coding: utf-8 -*-
# mypy: ignore-errors
from __future__ import annotations

import logging
from typing import Any, Optional, Union

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.schema import HumanMessage, SystemMessage

from app.schemas.agent_schema import AgentAndToolsConfig
from app.schemas.tool_schema import ToolConfig, ToolInputSchema
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool

logger = logging.getLogger(__name__)


class ProjectSchedulingSummarizeKPITool(ExtendedBaseTool):
    name = "summarize_kpi_tool"

    @classmethod
    def from_config(
        cls,
        config: ToolConfig,
        common_config: AgentAndToolsConfig,
        **kwargs: Any,
    ) -> ProjectSchedulingSummarizeKPITool:
        llm = kwargs.get("llm", get_llm(common_config.llm))
        fast_llm = kwargs.get("fast_llm", get_llm(common_config.fast_llm))
        fast_llm_token_limit = kwargs.get("fast_llm_token_limit", common_config.fast_llm_token_limit)
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
    ) -> Any:
        """Use the tool."""

        raise NotImplementedError("ProjectSchedulingSummarizeKPITool does not support sync")

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        try:
            tool_input = ToolInputSchema.parse_raw(query)
            logger.info("tool input summarizer: {}".format(tool_input))
            kpis = tool_input.intermediate_steps["run_optimizer_tool"]

            messages = [
                SystemMessage(content=self.system_context),
                HumanMessage(content=self.prompt_message.format(kpi_table=kpis)),
            ]
            logger.info("Messages generated: {}".format(messages))
            response = await self._agenerate_response(messages, discard_fast_llm=False, run_manager=run_manager)
            return response
        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(e, tool=self.name)
                return repr(e)
            else:
                raise e

    @staticmethod
    def load_yaml_file(file_path: str) -> Union[str, None]:
        try:
            print(f"Trying to open file at: {file_path}")
            with open(file_path, "r") as file:
                return file.read()
        except Exception:
            # if error, optimizer has not created plots because there is not new bundles - this can be because the
            # optimizer was ran with the same config as base
            return None

    @staticmethod
    def get_latest_output() -> str:
        latest_directory = "app/opt/project_scheduling/output_data/optimization_kpis.csv"
        return latest_directory
