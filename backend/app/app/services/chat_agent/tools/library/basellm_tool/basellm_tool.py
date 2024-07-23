# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from typing import Any, Optional

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.schema import HumanMessage, SystemMessage

from app.schemas.agent_schema import AgentAndToolsConfig
from app.schemas.tool_schema import ToolConfig, ToolInputSchema
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.helpers.query_formatting import standard_query_format
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool

logger = logging.getLogger(__name__)


class BaseLLM(ExtendedBaseTool):
    """BaseLLM Tool."""

    name = "basellm_tool"

    @classmethod
    def from_config(
        cls,
        config: ToolConfig,
        common_config: AgentAndToolsConfig,
        **kwargs: Any,
    ) -> BaseLLM:
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
            name=kwargs.get("name", "basellm_tool"),
        )

    def _run(
        self,
        *args: Any,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> str:
        """Use the tool."""

        raise NotImplementedError("BaseLLM does not support sync")

    async def _arun(
        self,
        *args: Any,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> str:
        """Use the tool asynchronously."""
        tool_input_str = kwargs.get(
            "query",
            args[0],
        )

        query = standard_query_format(ToolInputSchema.parse_raw(tool_input_str))

        try:
            messages = [
                SystemMessage(content=self.system_context),
                HumanMessage(content=self.prompt_message.format(question=query)),
            ]
            response = await self._agenerate_response(messages, discard_fast_llm=True, run_manager=run_manager)
            return response
        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(e, tool=self.name)
                return repr(e)
            raise e
