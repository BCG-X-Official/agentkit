# -*- coding: utf-8 -*-
import logging
from typing import Any, List, Optional, Tuple, Union

import openai
from langchain.agents import BaseMultiActionAgent
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import Callbacks
from langchain.chains.llm import LLMChain
from langchain.prompts.base import BasePromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import AgentAction, AgentFinish
from langchain.tools import BaseTool

from app.schemas.agent_schema import ActionPlan, ActionPlans
from app.schemas.tool_schema import ToolInputSchema

logger = logging.getLogger(__name__)


class SimpleRouterAgent(BaseMultiActionAgent):
    """Simple Router Agent."""

    tools: List[BaseTool]
    llm_chain: LLMChain

    action_plans: ActionPlans(action_plans={})
    action_plan: Optional[ActionPlan] = None

    @property
    def input_keys(self):
        return ["input", "chat_history"]

    def plan(
        self, intermediate_steps: List[Tuple[AgentAction, str]], **kwargs: Any
    ) -> Union[List[AgentAction], AgentFinish]:
        """
        Given input, decided what to do.

        Args:
            intermediate_steps: Steps the LLM has taken to date,
                along with observations
            **kwargs: User inputs.

        Returns:
            Action specifying what tool to use.
        """
        raise NotImplementedError("SimpleRouterAgent does not support sync")

    async def aplan(
        self,
        intermediate_steps: List[Tuple[AgentAction, str]],
        callbacks: Callbacks | None = None,
        **kwargs: Any,
    ) -> Union[List[AgentAction], AgentFinish]:
        """
        Given input, decided what to do.

        Args:
            intermediate_steps: Steps the LLM has taken to date,
                along with observations
            callbacks: Callbacks to run.
            **kwargs: User inputs.

        Returns:
            Action specifying what tool to use.
        """
        # Router agent makes initial template
        retries = 0
        while self.action_plan is None:
            try:
                full_output = await self.llm_chain.apredict(**kwargs)
                action_plan = self.action_plans.action_plans[full_output]
                self.action_plan = action_plan
                logger.info(f"Action plan selected: {full_output}, {str(action_plan)}")
            except openai.error.AuthenticationError as e:
                retries += 1
                if retries > 3:
                    raise ValueError(
                        "Oops! It seems like your OPENAPI key is invalid. Please check your Settings."
                    ) from e
            except Exception as e:
                retries += 1
                if retries > 3:
                    raise ValueError(f"Invalid action plan selected ({retries}x)") from e

        # Router agent follows action plan
        if len(self.action_plan.actions) > 0:
            next_actions = self.action_plan.actions.pop(0)
            tool_input = ToolInputSchema(
                latest_human_message=kwargs["input"],
                chat_history=[],
                user_settings=kwargs["user_settings"],
                intermediate_steps={},
            )
            if len(intermediate_steps) > 0:
                tool_appendix_titles = {tool.name: getattr(tool, "appendix_title", "") for tool in self.tools}
                tool_input.intermediate_steps = {
                    tool_appendix_titles[step[0].tool]: step[1] for step in intermediate_steps
                }
            elif "memory" in next_actions and "chat_history" in kwargs:
                tool_input.chat_history = kwargs["chat_history"]

            tool_input_str = tool_input.json()
            actions = [AgentAction(tool=a, tool_input=tool_input_str, log="") for a in next_actions if a != "memory"]
            return actions
        # Router agent is done
        else:
            output = "\n\n".join([f"{step[0].tool}:\n{step[1]}" for step in intermediate_steps])
            return AgentFinish(return_values={"output": output}, log="")

    @classmethod
    def create_prompt(
        cls,
        prompt_message: str,
        system_context: str,
        action_plans: ActionPlans,
    ) -> BasePromptTemplate:
        """Create a prompt for the router agent."""
        messages = [
            SystemMessagePromptTemplate.from_template(
                system_context.format(
                    action_plans="\n".join([f"{k}: {v.description}" for k, v in action_plans.action_plans.items()])
                )
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template(prompt_message),
        ]
        return ChatPromptTemplate(input_variables=["input", "chat_history"], messages=messages)

    @classmethod
    def from_llm_and_tools(
        cls,
        llm: BaseLanguageModel,
        tools: List[BaseTool],
        prompt_message: str,
        system_context: str,
        action_plans: ActionPlans,
        **kwargs: Any,
    ) -> BaseMultiActionAgent:
        """Construct an agent from an LLM and tools."""
        llm_chain = LLMChain(
            llm=llm,
            prompt=cls.create_prompt(
                prompt_message=prompt_message,
                system_context=system_context,
                action_plans=action_plans,
            ),
        )
        return cls(
            tools=tools,
            llm_chain=llm_chain,
            action_plans=action_plans,
            **kwargs,
        )
