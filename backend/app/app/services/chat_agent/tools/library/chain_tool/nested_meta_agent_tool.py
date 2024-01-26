# -*- coding: utf-8 -*-
"""Example of a chain nested inside a tool."""
import logging
from typing import Any, Optional

from langchain.agents import AgentExecutor
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.chains.base import Chain

from app.schemas.agent_schema import ActionPlan, ActionPlans, AgentAndToolsConfig, AgentConfig
from app.schemas.streaming_schema import StreamingDataTypeEnum
from app.schemas.tool_schema import ToolConfig
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.router_agent.SimpleRouterAgent import SimpleRouterAgent
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool
from app.services.chat_agent.tools.tools import get_tools
from app.utils.config_loader import load_agent_config_override


def get_chain(llm: BaseLanguageModel, config: AgentConfig) -> Chain:
    """create an agent executor to run a SimpleRouterAgent (similar to
    create_meta_agent)"""
    tools = get_tools(tools=config.tools, load_nested=False)
    agent = SimpleRouterAgent.from_llm_and_tools(
        tools=tools,
        llm=llm,
        prompt_message=config.prompt_message,
        system_context=config.system_context,
        action_plans=config.action_plans,
    )
    executor = AgentExecutor.from_agent_and_tools(
        agent=agent,  # conv_agent,
        tools=tools,
        verbose=True,
        max_iterations=15,
        max_execution_time=300,
        early_stopping_method="generate",
        handle_parsing_errors=True,
    )
    return executor


class ChainTool(ExtendedBaseTool):
    """Chain Tool to run a nested meta agent as a chain."""

    # define the name of your tool, matching the name in the config
    name = "chain_tool"
    appendix_title = "Chain Appendix"
    agent_config: AgentConfig

    @classmethod
    def from_config(
        cls,
        config: ToolConfig,
        common_config: AgentAndToolsConfig,
        **kwargs: Any,
    ) -> ExtendedBaseTool:
        llm = kwargs.get("llm", get_llm(common_config.llm))
        fast_llm = kwargs.get("fast_llm", get_llm(common_config.fast_llm))
        fast_llm_token_limit = kwargs.get("fast_llm_token_limit", common_config.fast_llm_token_limit)

        if config.additional is None:
            raise ValueError("Chain Tool requires an additional config for the agent")

        agent_config = load_agent_config_override(
            {
                "tools": config.additional.tools,
                "action_plans": ActionPlans(
                    action_plans={k: ActionPlan(**v) for k, v in config.additional.action_plans.items()}
                ),
                "prompt_message": config.prompt_message,
                "system_context": config.system_context,
            }
        )
        # add all custom prompts from your config, below are the standard ones
        return cls(
            agent_config=agent_config,
            llm=llm,
            fast_llm=fast_llm,
            fast_llm_token_limit=fast_llm_token_limit,
            description=config.description.format(**{e.name: e.content for e in config.prompt_inputs}),
            prompt_message="",
            system_context="",
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
            # if you want to stream the action signal to the frontend (appears in 'Steps')
            if run_manager is not None:
                await run_manager.on_text(
                    "chain_action", data_type=StreamingDataTypeEnum.ACTION, tool=self.name, step=1
                )

            chain = get_chain(llm=self.llm, config=self.agent_config)

            response = await chain.acall(
                {
                    "input": query,
                },
                callbacks=run_manager.get_child() if run_manager else None,
            )

            if run_manager is not None:
                # ensure output from second chain is returned to FE
                await run_manager.on_text(response["output"], data_type=StreamingDataTypeEnum.LLM)
                # if you want to stream the response to an Appendix

            return response["output"]

        except Exception as e:
            if run_manager is not None:
                logging.exception(e)
                await run_manager.on_tool_error(e, tool=self.name)
                return repr(e)
            raise e
