# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from typing import Any, Optional

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.text_splitter import TokenTextSplitter

from app.schemas.agent_schema import AgentAndToolsConfig
from app.schemas.tool_schema import ToolConfig, ToolInputSchema
from app.services.chat_agent.helpers.llm import get_llm, get_token_length
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool

logger = logging.getLogger(__name__)


class SummarizerTool(ExtendedBaseTool):
    """Summarizer Tool."""

    name = "summarizer_tool"

    summarize_prompt_template: PromptTemplate

    @classmethod
    def from_config(
        cls,
        config: ToolConfig,
        common_config: AgentAndToolsConfig,
        **kwargs: Any,
    ) -> SummarizerTool:
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
        prompt_template_message = config.prompt_message.format(**{e.name: e.content for e in config.prompt_inputs})
        return cls(
            llm=llm,
            fast_llm=fast_llm,
            fast_llm_token_limit=fast_llm_token_limit,
            description=config.description.format(**{e.name: e.content for e in config.prompt_inputs}),
            max_token_length=max_token_length,
            system_context=config.system_context.format(**{e.name: e.content for e in config.prompt_inputs}),
            prompt_message=config.prompt_message.format(**{e.name: e.content for e in config.prompt_inputs}),
            summarize_prompt_template=PromptTemplate(
                template=prompt_template_message,
                input_variables=["text"],
            ),
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
            callbacks = run_manager.get_child() if run_manager else None
            tool_input = ToolInputSchema.parse_raw(query)
            tool_outputs = [f"{k}: {v}" for k, v in tool_input.intermediate_steps.items()]
            assert self.max_token_length is not None, "max_token_length must not be None"
            if get_token_length(query) <= self.max_token_length:
                docs = [Document(page_content=tool_output) for tool_output in tool_outputs]
                chain = load_summarize_chain(
                    self.llm,
                    chain_type="stuff",
                    prompt=self.summarize_prompt_template,
                )
            else:
                logger.info("Splitting text into chunks")
                text_splitter = TokenTextSplitter(
                    chunk_size=10,
                    chunk_overlap=0,
                )
                texts = [text for tool_output in tool_outputs for text in text_splitter.split_text(tool_output)]
                docs = [Document(page_content=t) for t in texts]
                chain = load_summarize_chain(
                    self.llm,
                    chain_type="map_reduce",
                    map_prompt=self.summarize_prompt_template,
                    combine_prompt=self.summarize_prompt_template,
                )

            response = await chain.arun(
                docs,
                callbacks=callbacks,
            )
            return response
        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(
                    e,
                    tool=self.name,
                )
                return repr(e)
            raise e
