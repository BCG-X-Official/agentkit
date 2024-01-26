# -*- coding: utf-8 -*-
import logging
import os
from pathlib import Path
from typing import Optional

import yaml
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.schema import HumanMessage, SystemMessage

from app.schemas.agent_schema import AgentAndToolsConfig
from app.schemas.streaming_schema import StreamingDataTypeEnum
from app.schemas.tool_schema import ToolConfig
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.helpers.utils import get_conversation_id
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool

logger = logging.getLogger(__name__)

OPTIMIZATION_CONFIG_PATH = "./app/opt/project_scheduling/config/"
DEFAULT_OPTIMIZATION_CONFIG_NAME = "optimization_config.json"


class ProjectSchedulingGenConfigTool(ExtendedBaseTool):
    name = "generate_config_tool"
    appendix_title = "Available resources Appendix"

    @classmethod
    def from_config(cls, config: ToolConfig, common_config: AgentAndToolsConfig, **kwargs):
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

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the tool."""

        raise NotImplementedError("ProjectSchedulingGenConfigTool does not support sync")

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        try:
            conv_id = get_conversation_id(run_manager.tags)

            conv_id_config_path_new = Path(OPTIMIZATION_CONFIG_PATH) / f"optimization_config_{conv_id}_new.json"

            if os.path.isfile(conv_id_config_path_new):
                current_parameter_config = self.load_yaml_file(conv_id_config_path_new)
            else:
                current_parameter_config = self.load_yaml_file(
                    Path(OPTIMIZATION_CONFIG_PATH) / DEFAULT_OPTIMIZATION_CONFIG_NAME
                )

            messages = [
                SystemMessage(content=self.system_context),
                HumanMessage(
                    content=self.prompt_message.format(question=query, parameter_config=current_parameter_config)
                ),
            ]
            response = await self._agenerate_response(messages, discard_fast_llm=False)
            is_valid = "json" in response

            if run_manager is not None:
                if is_valid:
                    await run_manager.on_text(
                        response,
                        data_type=StreamingDataTypeEnum.APPENDIX,
                        tool=self.name,
                        step=1,
                        title=self.appendix_title,
                    )

                    self.parse_and_load_output(response=response, conversation_id=conv_id)
                else:
                    await run_manager.on_text(
                        "no_data",
                        data_type=StreamingDataTypeEnum.ACTION,
                        tool=self.name,
                        step=1,
                        result=response,
                    )
            return response
        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(e, tool=self.name)
                return repr(e)
            else:
                raise e

    def parse_and_load_output(self, response: str, conversation_id: str) -> None:
        save_path = Path(OPTIMIZATION_CONFIG_PATH) / f"optimization_config_{conversation_id}_new.json"
        response = response.replace("```json", "").replace("`", "").replace("New parameter configuration:", "")
        old_config_path = Path(OPTIMIZATION_CONFIG_PATH) / f"optimization_config_{conversation_id}_old.json"

        # if config_new exists, rename it to old config and save new config
        if os.path.isfile(save_path):
            if os.path.isfile(old_config_path):
                os.remove(old_config_path)
            os.rename(save_path, old_config_path)
            logger.info("Old parameter configuration renamed to {}".format(old_config_path))
        with open(save_path, "w") as file:
            file.write(response)
        logger.info("New parameter configuration saved to {}".format(save_path))

    @staticmethod
    def load_yaml_file(file_path):
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
