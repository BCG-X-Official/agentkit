# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import datetime
import logging
import os
from typing import Any, List, Optional

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.schema import HumanMessage, SystemMessage

from app.core.config import settings
from app.db.vector_db_pdf_ingestion import PDFExtractionPipeline, get_pdf_pipeline
from app.schemas.agent_schema import AgentAndToolsConfig
from app.schemas.streaming_schema import StreamingDataTypeEnum
from app.schemas.tool_schema import ToolConfig, ToolInputSchema
from app.schemas.tool_schemas.pdf_tool_schema import PdfAppendix
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.helpers.query_formatting import standard_query_format
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool

logger = logging.getLogger(__name__)


class PDFTool(ExtendedBaseTool):
    """PDF Tool."""

    name = "pdf_tool"
    appendix_title = "PDF Appendix"
    pdf_pipeline: PDFExtractionPipeline

    @classmethod
    def from_config(
        cls,
        config: ToolConfig,
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
            pdf_pipeline=get_pdf_pipeline(),
        )

    def _run(
        self,
        *args: Any,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any,
    ) -> str:
        raise NotImplementedError("Tool does not support sync")

    @staticmethod
    def _save_to_csv(query: str, docs: list, result: str) -> None:
        logger.info("Saving data to log file..")
        os.makedirs(settings.PDF_TOOL_LOG_QUERY_PATH, exist_ok=True)
        file_name = datetime.datetime.now().strftime(f"{settings.PDF_TOOL_LOG_QUERY_PATH}/%Y-%m-%d.csv")
        file_exists = os.path.isfile(file_name)

        aggregated_sources = []
        aggregated_urls = []
        for doc in docs:
            source = doc.metadata.get("source", "Not Available")
            index = doc.metadata.get("index", "")
            if index:  # If 'index' is not empty, concat with 'source'
                source_with_index = f"{source} (Index: {index})"
            else:
                source_with_index = source
            aggregated_sources.append(source_with_index)

            # Add URL if exists
            if "url" in doc.metadata:
                aggregated_urls.append(doc.metadata["url"])

        # Joining values to save in an unique cell
        sources = "\n".join(aggregated_sources)
        urls = "\n".join(aggregated_urls)

        with open(file_name, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["data_hora", "pergunta", "resposta", "metadata_source", "metadata_url"])

            data_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            writer.writerow([data_hora, query, result, sources, urls])

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
        # Use standard query formatting
        query = standard_query_format(ToolInputSchema.parse_raw(query))
        try:
            logger.info("Filtering relevant documents")
            db_pdf_docs = self.pdf_pipeline.run(load_index=True)

            logger.info("Filtering DB for relevant info...")
            docs = db_pdf_docs.as_retriever(
                search_kwargs={
                    "k": 4,
                }  # tbd search_kwargs
            ).get_relevant_documents(query)
            retrieved_docs = "\n".join([doc.page_content for doc in docs])

            result = await self._aqa_pdf_chunks(
                query,
                retrieved_docs,
                run_manager,
            )

            last_query = query.split(": ")[1]
            print("\nQuery: ", last_query)

            if settings.PDF_TOOL_LOG_QUERY:
                self._save_to_csv(last_query, docs, result)

            if run_manager is not None:
                await run_manager.on_text(
                    self.format_appendix(["Found PDFs"]),
                    data_type=StreamingDataTypeEnum.APPENDIX,
                    tool=self.name,
                    title=self.appendix_title,
                    references=self.appendix_context(["Found PDFs"]),
                )
            return result

        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(
                    e,
                    tool=self.name,
                )
                return repr(e)
            raise e

    @staticmethod
    def appendix_context(
        documents: List[str],
    ) -> List[PdfAppendix]:
        """Create the appendix context."""
        return [
            PdfAppendix(
                doc_id=d,
                page_numbers=[],
                reference_text="",
            )
            for d in documents
        ]

    @staticmethod
    def format_appendix(
        documents: List[str],
    ) -> str:
        """Format the appendix."""
        documents_str = ",".join(documents)
        return f"```pdf\nDocuments: {documents_str}\n```"

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
        response = await self._agenerate_response(question_messages, discard_fast_llm=True, run_manager=run_manager)
        return response
