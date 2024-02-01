# -*- coding: utf-8 -*-
# mypy: ignore-errors
from __future__ import annotations

import logging
from typing import Any, Optional

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.schema import HumanMessage, SystemMessage

from app.schemas.agent_schema import AgentAndToolsConfig
from app.schemas.tool_schema import ToolConfig, ToolInputSchema
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool
from app.utils.llm import get_token_length

logger = logging.getLogger(__name__)


class CodeExpertTool(ExtendedBaseTool):
    """Expert Tool."""

    name = "code_expert_tool"
    fast_llm_token_threshold: int = 8000

    @classmethod
    def from_config(cls, config: ToolConfig, common_config: AgentAndToolsConfig, **kwargs) -> CodeExpertTool:
        """Create an expert tool from a config."""
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
            fast_llm_token_threshold=config.fast_llm_token_threshold
            if config.fast_llm_token_threshold
            else cls.fast_llm_token_threshold,
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
            tool_input = ToolInputSchema.parse_raw(query)
            user_question = tool_input.latest_human_message

            retrieved_code = tool_input.intermediate_steps["code_search_tool"]["result"]
            latest_chat_history = tool_input.intermediate_steps["code_search_tool"]["chat_history"]
            retrieved_documentation = tool_input.intermediate_steps["pdf_tool"]["result"]

            messages = [
                SystemMessage(content=self.system_context),
                HumanMessage(
                    content=self.prompt_message.format(
                        question=user_question,
                        chat_history=latest_chat_history,
                        retrieved_code=retrieved_code,
                        retrieved_documentation=retrieved_documentation,
                    )
                ),
            ]
            input_token_length = get_token_length("".join([m.content for m in messages]))
            if input_token_length > self.fast_llm_token_threshold:
                logger.info(
                    f"[TOKEN PROBLEM] Code expert tool: Input token length {input_token_length}, using fast_llm"
                )
                response = await self._agenerate_response(messages, discard_fast_llm=False, run_manager=run_manager)
            else:
                response = await self._agenerate_response(messages, discard_fast_llm=True, run_manager=run_manager)

            logger.info(f"Expert Tool response - {response}")

            return response

        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(e, tool=self.name)
                return repr(e)
            else:
                raise e
