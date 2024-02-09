# -*- coding: utf-8 -*-
# mypy: ignore-errors
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Optional

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.schema import HumanMessage, SystemMessage

from app.schemas.agent_schema import AgentAndToolsConfig
from app.schemas.tool_schema import ToolConfig
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.helpers.utils import get_conversation_id
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool

logger = logging.getLogger(__name__)

OPTIMIZATION_CONFIG_PATH = "./app/opt/project_scheduling/config/"
DEFAULT_OPTIMIZATION_CONFIG_NAME = "optimization_config.json"
DEFAULT_OPTIMIZATION_INPUT_NAME = "optimization_input.json"


class ProjectSchedulingSummarizeConfigChangesTool(ExtendedBaseTool):
    name = "summarize_config_changes_tool"

    @classmethod
    def from_config(
        cls, config: ToolConfig, common_config: AgentAndToolsConfig, **kwargs
    ) -> ProjectSchedulingSummarizeConfigChangesTool:
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

    def _run(self, *args: Any, run_manager: Optional[CallbackManagerForToolRun] = None, **kwargs: Any) -> str:
        """Use the tool."""

        raise NotImplementedError("ProjectSchedulingSummarizeConfigChangesTool does not support sync")

    async def _arun(self, query: str, run_manager: AsyncCallbackManagerForToolRun) -> str:
        """Use the tool asynchronously."""
        try:
            old_parameter_input_path = (
                Path(OPTIMIZATION_CONFIG_PATH) / f"optimization_input_{get_conversation_id(run_manager.tags)}_old.json"
            )

            new_parameter_tasks = self.load_config_file(
                Path(OPTIMIZATION_CONFIG_PATH) / f"optimization_input_{get_conversation_id(run_manager.tags)}_new.json"
            )
            if os.path.isfile(old_parameter_input_path):
                current_parameter_tasks = self.load_config_file(old_parameter_input_path)
            else:
                current_parameter_tasks = self.load_config_file(
                    Path(OPTIMIZATION_CONFIG_PATH) / DEFAULT_OPTIMIZATION_INPUT_NAME
                )

            messages = [
                SystemMessage(content=self.system_context),
                HumanMessage(
                    content=self.prompt_message.format(
                        new_parameter_tasks=new_parameter_tasks,
                        current_parameter_tasks=current_parameter_tasks,
                        question=query,
                    )
                ),
            ]
            response = await self._agenerate_response(messages, discard_fast_llm=True, run_manager=run_manager)
            return response
        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(e, tool=self.name)
                return repr(e)
            else:
                raise e

    @staticmethod
    def load_config_file(file_path: Path) -> Any:
        print(f"Trying to open file at: {file_path}")
        with open(file_path, "r") as file:
            return file.read()
