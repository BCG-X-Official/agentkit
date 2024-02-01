# -*- coding: utf-8 -*-
# mypy: ignore-errors
from __future__ import annotations

import logging
from typing import Any, Optional, Union

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.schema import Document

from app.db.vector_db_code_ingestion import get_code_pipeline
from app.schemas.agent_schema import AgentAndToolsConfig
from app.schemas.streaming_schema import StreamingDataTypeEnum
from app.schemas.tool_schema import RetrievalToolConfig, ToolInputSchema
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool
from app.utils.llm import truncate_to_token_length

logger = logging.getLogger(__name__)


class CodeSearchTool(ExtendedBaseTool):
    """Code search tool."""

    name = "code_search_tool"
    appendix_title = "Code Search Tool"

    n_docs: int = 2
    max_tokens_chat_history: int = 3000

    @classmethod
    def from_config(
        cls,
        config: RetrievalToolConfig,
        common_config: AgentAndToolsConfig,
        **kwargs: Any,
    ) -> CodeSearchTool:
        """Create a code search tool from a config."""
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
        max_token_length = kwargs.get("max_token_length", common_config.max_token_length)

        return cls(
            llm=llm,
            fast_llm=fast_llm,
            fast_llm_token_limit=fast_llm_token_limit,
            description=config.description,
            prompt_message=config.prompt_message.format(**{e.name: e.content for e in config.prompt_inputs}),
            system_context=config.system_context.format(**{e.name: e.content for e in config.prompt_inputs}),
            max_token_length=max_token_length,
            n_docs=config.n_docs,
            max_tokens_chat_history=config.max_tokens_chat_history,
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
    ) -> Union[dict, str]:
        """Use the tool asynchronously."""
        query = kwargs.get(
            "query",
            args[0],
        )
        try:
            logger.info("Get DB...")
            db_code = get_code_pipeline().run(load_index=True)

            # Filter search query to only include user's questions and remove retrieved docs
            tool_input = ToolInputSchema.parse_raw(query)
            chat_history = tool_input.chat_history[-4:]
            user_question = tool_input.latest_human_message.split("Tool outputs streamed to the user:")[0].strip()
            human_messages = [
                msg.content.split("Tool outputs streamed to the user:")[0].strip()
                for msg in chat_history
                if msg.type == "human"
            ]
            search_query = "\n".join([user_question] + human_messages)

            logger.info("Retrieving documents from DB...")
            logger.info(f"Code Tool Search Query - {search_query}")
            docs = db_code.as_retriever(
                search_kwargs={
                    "k": self.n_docs,
                }  # tbd search_kwargs
            ).get_relevant_documents(search_query)

            retrieved_docs = "\n\n".join([self._format_doc(doc) for doc in docs])
            sources = [self._format_source(doc) for doc in docs]
            uniq_sources = set(sources)

            logger.info(f"Code Search Tool {len(sources)} Sources - {sources}")
            logger.info(f"Code Search Tool Retreived Code files - {retrieved_docs}")

            # Add step in steps view with number of sources and sources
            if run_manager is not None:
                await run_manager.on_text(
                    "retreived_sources",
                    data_type=StreamingDataTypeEnum.ACTION,
                    tool=self.name,
                    step=2,
                    number_sources=len(uniq_sources),
                    sources=", ".join(uniq_sources),
                )

            if len(chat_history) == 0:
                truncated_chat_history = chat_history
            else:
                truncated_chat_history = truncate_to_token_length(
                    string=str(chat_history), max_length=self.max_tokens_chat_history
                )

            result = {
                "result": retrieved_docs,
                "metadata": sources,
                "chat_history": truncated_chat_history,
            }
            return result

        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(e, tool=self.name)
                return repr(e)
            else:
                raise e

    def _format_source(self, doc: Document) -> str:
        header = doc.metadata.get("header1", "")
        source = f"{doc.metadata['source']}{f'#{header}' if header else ''}"
        return source

    def _format_doc(self, doc: Document) -> str:
        source_label = "Python file Source:"
        content_label = "Python file Content:"
        content = doc.page_content

        if doc.metadata["tool_prompt"]:
            prompt = doc.metadata["tool_prompt"]
            formatted_doc = (
                f"{source_label} {self._format_source(doc)}\n{content_label}\n{content}\n--prompt for tool:\n{prompt}"
            )
        else:
            formatted_doc = f"{source_label} {self._format_source(doc)}\n{content_label}\n{content}"

        return formatted_doc
