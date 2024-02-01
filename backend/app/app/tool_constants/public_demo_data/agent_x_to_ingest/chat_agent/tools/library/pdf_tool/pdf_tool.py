# -*- coding: utf-8 -*-
import logging
from typing import List, Optional

from langchain.callbacks.manager import AsyncCallbackManagerForToolRun
from langchain.schema import HumanMessage, SystemMessage

from app.core.config import settings
from app.db.vector_db_pdf_ingestion import pdf_pipeline
from app.schemas.streaming_schema import StreamingDataTypeEnum
from app.schemas.tool_schema import ToolConfig
from app.schemas.tool_schemas.pdf_tool_schema import PdfAppendix
from app.services.chat_agent.helpers.llm import get_llm
from app.services.chat_agent.tools.ExtendedBaseTool import ExtendedBaseTool

logger = logging.getLogger(__name__)


class PDFTool(ExtendedBaseTool):
    """PDF Tool."""

    name = "pdf_tool"
    appendix_title = "PDF Appendix"

    @classmethod
    def from_config(cls, config: ToolConfig, **kwargs):
        """Create a PDF tool from a config."""
        llm = kwargs.get("llm", get_llm(config.default_llm))
        fast_llm = kwargs.get("fast_llm", get_llm(config.default_fast_llm))

        if not settings.PDF_TOOL_ENABLED:
            raise ValueError(
                "The PDF Tool is not enabled. Please set the environment"
                "variables to enable it if used in the configuration."
            )

        return cls(
            llm=llm,
            fast_llm=fast_llm,
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
        )

    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        try:
            logger.info("Filtering relevant documents")
            db_pdf_docs = pdf_pipeline.run(load_index=True)

            logger.info("Filtering DB for relevant info...")
            docs = db_pdf_docs.as_retriever(
                search_kwargs={
                    "k": 4,
                }  # tbd search_kwargs
            ).get_relevant_documents(query)
            retrieved_docs = "\n".join([doc.page_content for doc in docs])

            result = await self._aqa_pdf_chunks(query, retrieved_docs, run_manager)

            if run_manager is not None:
                await run_manager.on_text(
                    self.format_appendix(["Found PDFs"]),
                    data_type=StreamingDataTypeEnum.appendix,
                    tool=self.name,
                    title=self.appendix_title,
                    references=self.appendix_context(["Found PDFs"]),
                )
            return result

        except Exception as e:
            if run_manager is not None:
                await run_manager.on_tool_error(e, tool=self.name)
                return repr(e)
            else:
                raise e

    def appendix_context(self, documents: List[str]) -> List[PdfAppendix]:
        """Create the appendix context."""
        return [
            PdfAppendix(
                doc_id=d,
                page_numbers=[],
                reference_text="",
            )
            for d in documents
        ]

    def format_appendix(self, documents: List[str]) -> str:
        """Format the appendix."""
        documents_str = ",".join(documents)
        return f"```pdf\nDocuments: {documents_str}\n```"

    async def _aqa_pdf_chunks(
        self,
        query: str,
        docs: str = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        if run_manager is not None:
            await run_manager.on_text(
                "qa_pdf_docs",
                data_type=StreamingDataTypeEnum.action,
                tool=self.name,
                step=1,
            )
        question_messages = [
            SystemMessage(content=self.system_context),
            HumanMessage(content=self.prompt_message.format(question=query, retrieved_docs=docs)),
        ]
        response = await self._agenerate_response(question_messages)
        logger.info(response)
        return response
