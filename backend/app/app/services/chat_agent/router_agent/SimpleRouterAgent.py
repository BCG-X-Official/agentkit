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
    BaseChatPromptTemplate,
    BaseMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import AgentAction, AgentFinish, BaseMessage
from langchain.tools import BaseTool

from app.schemas.agent_schema import ActionPlan, ActionPlans
from app.schemas.tool_schema import ToolInputSchema, UserSettings
from app.services.chat_agent.helpers.run_helper import is_running
from app.utils.exceptions.common_exceptions import AgentCancelledException

logger = logging.getLogger(__name__)


class SimpleRouterAgent(BaseMultiActionAgent):
    """Agent that, given input, decides what to do."""

    tools: List[BaseTool]
    llm_chain: LLMChain

    action_plans: ActionPlans = ActionPlans(action_plans={})
    action_plan: Optional[ActionPlan] = None

    @property
    def input_keys(
        self,
    ) -> List[str]:
        return [
            "input",
            "chat_history",
        ]

    def plan(
        self,
        intermediate_steps: List[
            Tuple[
                AgentAction,
                str,
            ]
        ],
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> Union[List[AgentAction], AgentFinish,]:
        """
        Given input, decided what to do. (Not implemented for this agent type)

        Args:
            intermediate_steps: Steps the LLM has taken to date,
                along with observations
            callbacks: Callbacks to run.
            **kwargs: User inputs.

        Returns:
            Action specifying what tool to use.
        """
        raise NotImplementedError("SimpleRouterAgent does not support sync")

    async def aplan(
        self,
        intermediate_steps: List[
            Tuple[
                AgentAction,
                str,
            ]
        ],
        callbacks: Callbacks | None = None,
        **kwargs: Any,
    ) -> Union[List[AgentAction], AgentFinish,]:
        """
        Given input, decides what to do.

        This function takes a list of intermediate steps and user inputs, and decides what action to take next.
        It first tries to select an action plan.
        If an action plan is selected, it follows the action plan and returns the next actions.
        If all actions in the action plan are completed, it returns an AgentFinish object.

        Args:
            intermediate_steps (List[Tuple[AgentAction, str]]): Steps the LLM has taken so far, along with observations.
            callbacks (Callbacks | None, optional): Callbacks to run. Defaults to None.
            **kwargs: User inputs.

        Returns:
            Union[List[AgentAction], AgentFinish]: The next actions to take or an AgentFinish object if all
            actions are completed.
        """
        if not await is_running():
            raise AgentCancelledException("The agent is cancelled.")

        # Router agent makes initial template
        retries = 0
        while self.action_plan is None:
            try:
                full_output = await self.llm_chain.apredict(**kwargs)
                action_plan = ActionPlan(**self.action_plans.action_plans[full_output].dict())
                self.action_plan = action_plan
                logger.info(f"Action plan selected: {full_output}, {str(action_plan)}")
            except openai.AuthenticationError as e:
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
            logger.info(f"Next action plan step ({len(self.action_plan.actions)} remaining)")
            next_actions = self.action_plan.actions.pop(0)
            tool_input = ToolInputSchema(
                latest_human_message=kwargs["input"],
                chat_history=[],
                user_settings=UserSettings(**kwargs["user_settings"].dict()) if kwargs["user_settings"] else None,
                intermediate_steps={},
            )
            if len(intermediate_steps) > 0:
                tool_input.intermediate_steps = {step[0].tool: step[1] for step in intermediate_steps}
            elif "memory" in next_actions and "chat_history" in kwargs:
                tool_input.chat_history = kwargs["chat_history"]

            tool_input_str = tool_input.json()  # pydantic v2: model_dump_json
            actions = [
                AgentAction(
                    tool=a,
                    tool_input=tool_input_str,
                    log="",
                )
                for a in next_actions
                if a != "memory"
            ]
            return actions
        # Router agent is done
        output = "\n\n".join([f"{step[0].tool}:\n{step[1]}" for step in intermediate_steps])
        return AgentFinish(
            return_values={"output": output},
            log="",
        )

    @classmethod
    def create_prompt(
        cls,
        prompt_message: str,
        system_context: str,
        action_plans: ActionPlans,
    ) -> BasePromptTemplate:
        """
        Create a prompt for the router agent.

        This function takes a prompt message, system context, and action plans, and returns a BasePromptTemplate object.

        Args:
            prompt_message (str): The prompt message.
            system_context (str): The system context.
            action_plans (ActionPlans): The available action plans.

        Returns:
            BasePromptTemplate: A BasePromptTemplate object.
        """
        messages: list[BaseMessagePromptTemplate | BaseMessage | BaseChatPromptTemplate] = [
            SystemMessagePromptTemplate.from_template(
                system_context.format(
                    action_plans="\n".join([f"{k}: {v.description}" for k, v in action_plans.action_plans.items()])
                )
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template(prompt_message),
        ]
        return ChatPromptTemplate(
            input_variables=[
                "input",
                "chat_history",
            ],
            messages=messages,
        )

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
        """
        Construct an agent from an LLM and tools.

        This function creates a BaseMultiActionAgent object from a language model, a list of tools,
        a prompt message, system context, and action plans.

        Args:
            llm (BaseLanguageModel): The language model.
            tools (List[BaseTool]): The list of tools.
            prompt_message (str): The prompt message.
            system_context (str): The system context.
            action_plans (ActionPlans): The action plans.
            **kwargs: Additional parameters.

        Returns:
            BaseMultiActionAgent: The BaseMultiActionAgent object.
        """
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
