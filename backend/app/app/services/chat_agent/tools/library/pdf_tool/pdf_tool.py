# -*- coding: utf-8 -*-
# pylint: disable=no-self-use
# mypy: ignore-errors
from __future__ import annotations

import logging
from typing import Any, Optional

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.schema import Document, HumanMessage, SystemMessage

from app.core.config import settings
from app.db.vector_db_pdf_ingestion import PDFExtractionPipeline, get_pdf_pipeline
from app.schemas.agent_schema import AgentAndToolsConfig
from app.schemas.streaming_schema import StreamingDataTypeEnum
from app.schemas.tool_schema import RetrievalToolConfig, ToolInputSchema
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool
from app.utils.llm import get_token_length

logger = logging.getLogger(__name__)


class PDFTool(ExtendedBaseTool):
    """PDF Tool."""

    name = "pdf_tool"
    appendix_title = "PDF Appendix"
    pdf_pipeline: PDFExtractionPipeline

    n_docs: int = 2

    @classmethod
    def from_config(
        cls,
        config: RetrievalToolConfig,
        common_config: AgentAndToolsConfig,
        **kwargs: Any,
    ) -> PDFTool:
        """Create a PDF tool from a config."""
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

        if not settings.PDF_TOOL_ENABLED:
            raise ValueError(
                "The PDF Tool is not enabled. "
                "Please set the environment variables to enable it if used in the configuration."
            )

        return cls(
            llm=llm,
            fast_llm=fast_llm,
            fast_llm_token_limit=fast_llm_token_limit,
            description=config.description.format(**{e.name: e.content for e in config.prompt_inputs}),
            prompt_message=config.prompt_message.format(**{e.name: e.content for e in config.prompt_inputs}),
            system_context=config.system_context.format(**{e.name: e.content for e in config.prompt_inputs}),
            pdf_pipeline=get_pdf_pipeline(),
            n_docs=config.n_docs,
            max_token_length=max_token_length,
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
            logger.info("Filtering relevant documents")
            db_pdf_docs = self.pdf_pipeline.run(load_index=True)

            # Filter search query to only include user's questions and remove retrieved docs
            tool_input = ToolInputSchema.parse_raw(query)
            chat_history = tool_input.chat_history
            user_question = tool_input.latest_human_message.split("Tool outputs streamed to the user:")[0].strip()
            human_messages = [
                msg.content.split("Tool outputs streamed to the user:")[0].strip()
                for msg in chat_history
                if msg.type == "human"
            ]
            search_query = "\n".join([user_question] + human_messages)

            logger.info("Retrieving documents from DB...")
            logger.info(f"PDF Tool Search Query - {search_query}")
            docs = db_pdf_docs.as_retriever(
                search_kwargs={
                    "k": self.n_docs,
                }  # tbd search_kwargs
            ).get_relevant_documents(search_query)

            retrieved_docs = "\n\n".join([self._format_doc(doc) for doc in docs])
            sources = [self._format_source(doc) for doc in docs]
            uniq_sources = set(sources)

            logger.info(f"PDF Tool {len(sources)} Sources - {sources}")
            logger.info(f"PDF Tool Retreived Docs - {retrieved_docs}")

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

            # Latest chat history: Get as many chat history messages,
            # till `max_number_of_chat_history_messages`
            # # of messages limit, or token limit is reached
            max_number_of_chat_history_messages = 6
            latest_chat_history = []
            current_token_length = get_token_length(retrieved_docs)
            logger.info(f"PDF Tool retreived docs tokens length - {current_token_length}")

            # Iterate backwards through the chat history, adding messages until the token limit is reached
            for i, message in enumerate(reversed(chat_history), start=1):
                message_token_length = get_token_length(message.content)
                if ((current_token_length + message_token_length) > self.max_token_length) or (
                    i > max_number_of_chat_history_messages
                ):
                    break
                latest_chat_history.append(message)
                current_token_length += message_token_length

            logger.info(f"PDF Tool added history messages to chat history with {current_token_length} tokens")

            result = {
                "result": retrieved_docs,
                "metadata": sources,
                "chat_history": latest_chat_history[::-1],  # reverse back the chat history
            }
            return result

        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(
                    e,
                    tool=self.name,
                )
                return repr(e)
            raise e

    def _format_source(self, doc: Document) -> str:
        source = f"{doc.metadata['source']}" if "source" in doc.metadata else ""
        return source

    def _format_doc(self, doc: Document) -> str:
        source_label = "Document Source:"
        content_label = "Document Content:"
        content = doc.page_content

        formatted_doc = f"{source_label} {self._format_source(doc)}\n{content_label}\n{content}"

        return formatted_doc

    async def _aqa_pdf_chunks(
        self,
        query: str,
        docs: str | None = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        if run_manager is not None:
            await run_manager.on_text(
                "qa_pdf_docs",
                data_type=StreamingDataTypeEnum.ACTION,
                tool=self.name,
                step=1,
            )
        question_messages = [
            SystemMessage(content=self.system_context),
            HumanMessage(
                content=self.prompt_message.format(
                    question=query,
                    retrieved_docs=docs,
                )
            ),
        ]
        response = await self._agenerate_response(question_messages)
        logger.info(response)
        return response
