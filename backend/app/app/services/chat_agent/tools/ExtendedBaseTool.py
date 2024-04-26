# -*- coding: utf-8 -*-
# mypy: disable-error-code="attr-defined"
from __future__ import annotations

from typing import Any, List, Optional

from box import Box
from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.schema import BaseMessage
from langchain.tools import BaseTool

from app.schemas.agent_schema import AgentAndToolsConfig
from app.schemas.tool_schema import ToolConfig
from app.services.chat_agent.helpers.llm import get_llm, get_token_length


class ExtendedBaseTool(BaseTool):
    """Base tool for all tools in the agent."""

    name: str = "extended_base_tool"
    llm: BaseLanguageModel
    fast_llm: BaseLanguageModel
    fast_llm_token_limit: Optional[int] = None
    max_token_length: Optional[int] = None

    prompt_message: str
    system_context: str

    prompt_selection: Optional[str] = None
    system_context_selection: Optional[str] = None

    prompt_validation: Optional[str] = None
    system_context_validation: Optional[str] = None

    prompt_refinement: Optional[str] = None
    system_context_refinement: Optional[str] = None

    image_description_prompt: Optional[str] = None

    additional: Optional[Box] = None

    @classmethod
    def from_config(
        cls,
        config: ToolConfig,
        common_config: AgentAndToolsConfig,
        **kwargs: Any,
    ) -> ExtendedBaseTool:
        """Create a tool from a config."""
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
        max_token_length = kwargs.get(
            "max_token_length",
            common_config.max_token_length,
        )

        return cls(
            llm=llm,
            fast_llm=fast_llm,
            fast_llm_token_limit=fast_llm_token_limit,
            max_token_length=max_token_length,
            description=config.description.format(**{e.name: e.content for e in config.prompt_inputs}),
            prompt_message=config.prompt_message.format(**{e.name: e.content for e in config.prompt_inputs}),
            image_description_prompt=config.image_description_prompt.format(
                **{e.name: e.content for e in config.prompt_inputs}
            )
            if config.image_description_prompt
            else None,
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
        messages: List[BaseMessage],
        discard_fast_llm: bool = False,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Generate a response asynchronously with the preferential llm."""
        if self.fast_llm_token_limit is None:
            raise ValueError("fast_llm_token_limit must be set in the config, current value `None`")
        llm = (
            self.fast_llm
            if get_token_length("".join([m.content if isinstance(m.content, str) else "" for m in messages]))
            < self.fast_llm_token_limit
            and not discard_fast_llm
            else self.llm
        )
        llm_response = await llm.agenerate([messages], callbacks=run_manager.get_child() if run_manager else None)
        return llm_response.generations[0][0].text

    def _run(
        self,
        *args: Any,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> Any:
        raise NotImplementedError(f"{self.name} does not implement _run")
