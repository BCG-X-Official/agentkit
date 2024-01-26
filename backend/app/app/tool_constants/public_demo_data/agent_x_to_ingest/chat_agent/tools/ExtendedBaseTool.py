# -*- coding: utf-8 -*-
from typing import Any, List, Optional, Union

from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.tools import BaseTool

from app.schemas.tool_schema import ToolConfig
from app.services.chat_agent.helpers.llm import get_llm
from app.utils.llm import get_token_length


class ExtendedBaseTool(BaseTool):
    """Base tool for all tools in the agent."""

    llm: BaseLanguageModel
    fast_llm: BaseLanguageModel

    prompt_message: Optional[str]
    image_description_prompt: Optional[str]
    system_context: Optional[str]

    prompt_selection: Optional[str]
    system_context_selection: Optional[str]

    prompt_validation: Optional[str]
    system_context_validation: Optional[str]

    prompt_refinement: Optional[str]
    system_context_refinement: Optional[str]

    @classmethod
    def from_config(cls, config: ToolConfig, **kwargs):
        """Create a tool from a config."""
        llm = kwargs.get("llm", get_llm(config.default_llm))
        fast_llm = kwargs.get("fast_llm", get_llm(config.default_fast_llm))
        return cls(
            llm=llm,
            fast_llm=fast_llm,
            description=config.description.format(**{e.name: e.content for e in config.prompt_inputs}),
            prompt_message=config.prompt_message.format(**{e.name: e.content for e in config.prompt_inputs}),
            image_description_prompt=config.image_description_prompt.format(
                **{e.name: e.content for e in config.prompt_inputs}
            ),
            system_context=config.system_context.format(**{e.name: e.content for e in config.prompt_inputs}),
            prompt_selection=config.prompt_selection.format(**{e.name: e.content for e in config.prompt_inputs})
            if config.prompt_selection
            else None,
            system_context_selection=config.system_context_selection.format(
                **{e.name: e.content for e in config.prompt_inputs}
            )
            if config.system_context_selection
            else None,
            prompt_validation=config.prompt_validation.format(**{e.name: e.content for e in config.prompt_inputs})
            if config.prompt_validation
            else None,
            system_context_validation=config.system_context_validation.format(
                **{e.name: e.content for e in config.prompt_inputs}
            )
            if config.system_context_validation
            else None,
            prompt_refinement=config.prompt_refinement.format(**{e.name: e.content for e in config.prompt_inputs})
            if config.prompt_refinement
            else None,
            system_context_refinement=config.system_context_refinement.format(
                **{e.name: e.content for e in config.prompt_inputs}
            )
            if config.system_context_refinement
            else None,
        )

    async def _agenerate_response(
        self,
        messages: List[Union[HumanMessage, AIMessage, SystemMessage]],
        force_gpt4: bool = False,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Generate a response asynchronously with the preferential llm."""
        llm = (
            self.fast_llm
            if get_token_length("".join([m.content for m in messages])) < 2500 and not force_gpt4
            else self.llm
        )
        llm_response = await llm.agenerate([messages], callbacks=run_manager.get_child() if run_manager else None)
        return llm_response.generations[0][0].text

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError(f"{self.name} does not implement _run")
