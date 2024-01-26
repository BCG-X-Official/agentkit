# -*- coding: utf-8 -*-
import logging
import os
from typing import Any, List

from dotenv import load_dotenv
from langchain.document_loaders.base import BaseLoader
from langchain.embeddings import CacheBackedEmbeddings
from langchain.schema import Document
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores.pgvector import PGVector

from app.core.config import settings
from app.schemas.ingestion_schema import LOADER_DICT, IndexingConfig
from app.schemas.tool_schemas.pdf_tool_schema import CodebaseDocumentationMetadata
from app.services.chat_agent.helpers.embedding_models import get_embedding_model
from app.utils.config_loader import get_ingestion_configs

logger = logging.getLogger(__name__)


class PDFExtractionPipeline:
    """Pipeline for extracting text from PDFs and load them into a vectorstore."""

    pipeline_config: IndexingConfig
    pdf_loader: type[BaseLoader]
    db: PGVector | None = None
    embedding: CacheBackedEmbeddings

    def __init__(self, pipeline_config: IndexingConfig, db_name: str):
        load_dotenv()

        self.pipeline_config = pipeline_config
        self.pdf_loader = LOADER_DICT[pipeline_config.pdf_parser.name]
        self.embedding = get_embedding_model(pipeline_config.embedding_model)
        self.connection_str = PGVector.connection_string_from_db_params(
            driver="psycopg2",
            host=settings.DATABASE_HOST,
            port=int(settings.DATABASE_PORT),
            database=db_name,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
        )

    def run(
        self,
        folder_path: str | None = None,
        collection_name: str = "pdf_indexing_1",
        load_index: bool = True,
    ) -> PGVector:
        """Run the PDF extraction pipeline."""
        if load_index:
            logger.info("Loading index from PSQL")
            db = PGVector(
                embedding_function=self.embedding,
                collection_name=collection_name,
                connection_string=self.connection_str,
            )
            return db
        if folder_path is not None:
            return self._load_documents(folder_path=folder_path, collection_name=collection_name)
        raise ValueError("folder_path must be provided if load_index is False")

    def _pdf_to_docs(
        self,
        pdf_dir_path: str,
    ) -> List[Document]:
        """
        Using specified PDF miner to convert PDF documents to raw text chunks.

        Fallback: PyPDF
        """
        documents = []
        for file_name in os.listdir(pdf_dir_path):
            file_extension = os.path.splitext(file_name)[1].lower()
            if file_extension == ".pdf":
                logger.info(f"Loading {file_name} into vectorstore")
                file_path = f"{pdf_dir_path}/{file_name}"
                try:
                    loader: Any = self.pdf_loader(file_path)  # type: ignore
                    file_docs = loader.load()
                    documents.extend(file_docs)
                    logger.info(f"{file_name} loaded successfully")
                except Exception as e:
                    logger.error(
                        f"Could not extract text from PDF {file_name} with {self.pipeline_config.pdf_parser}: {repr(e)}"
                    )

        return documents

    def _md_to_docs(self, md_dir_path: str) -> List[Document]:
        """
        Load and split markdown files into documents.

        Args:
            md_dir_path (str): Path to markdown files

        Returns:
            List[Document]: List of processed documents
        """
        documents = []

        for file_name in os.listdir(md_dir_path):
            file_extension = os.path.splitext(file_name)[1].lower()

            if file_extension == ".md":
                logger.info(f"Loading data from {file_name} as Document...")
                file_path = f"{md_dir_path}/{file_name}"

                try:
                    # Load md files as single document
                    with open(file_path, "r", encoding="utf-8") as f:
                        md_file = f.read()

                    md_doc = Document(
                        page_content=md_file,
                        metadata=CodebaseDocumentationMetadata.parse_obj({"source": file_name, "type": "text"}).dict(),
                    )

                    # Further split at token-level, when splits are above chunk_size configuration (rare)
                    text_splitter = TokenTextSplitter(
                        chunk_size=self.pipeline_config.tokenizer_chunk_size,
                        chunk_overlap=self.pipeline_config.tokenizer_chunk_overlap,
                    )
                    file_docs = text_splitter.split_documents([md_doc])

                    documents.extend(file_docs)
                    if len(file_docs) > 1:
                        logger.info(
                            f"Split {file_name} to {len(file_docs)} documents due to chunk_size: ({self.pipeline_config.tokenizer_chunk_size})"
                        )

                except Exception as e:
                    logger.error(f"Could not load MD file {file_name}: {repr(e)}")

        return documents

    def _load_documents(self, folder_path: str, collection_name: str = "pdf_indexing_1") -> PGVector:
        """Load documents into vectorstore."""
        docs = self._md_to_docs(folder_path)
        logger.info(f"Adding {len(docs)} codebase documentation docs into vectorstore")

        return PGVector.from_documents(
            embedding=self.embedding,
            documents=docs,
            collection_name=collection_name,
            connection_string=self.connection_str,
            pre_delete_collection=True,
        )


def get_pdf_pipeline() -> PDFExtractionPipeline:
    pdf_pipeline = PDFExtractionPipeline(
        pipeline_config=get_ingestion_configs().indexing_config,
        db_name=settings.PDF_TOOL_DATABASE,
    )
    return pdf_pipeline


def run_pdf_ingestion_pipeline(load_index: bool = True) -> None:
    get_pdf_pipeline().run(
        settings.PDF_TOOL_DATA_PATH,
        collection_name="pdf_indexing_1",
        load_index=load_index,
    )


if __name__ == "__main__":
    run_pdf_ingestion_pipeline(load_index=False)
