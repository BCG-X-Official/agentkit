# -*- coding: utf-8 -*-
import logging
import os
from enum import Enum
from typing import List

from dotenv import load_dotenv
from langchain.document_loaders import (
    PDFMinerLoader,
    PDFMinerPDFasHTMLLoader,
    PyMuPDFLoader,
    PyPDFLoader,
    UnstructuredPDFLoader,
)
from langchain.document_loaders.base import BaseLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores.pgvector import PGVector
from pydantic import BaseModel

from app.core.config import settings
from app.utils.config import Config

logger = logging.getLogger(__name__)


class PDFParserEnum(Enum):
    PyMuPDF = "PyMuPDF"
    PDFMiner_HTML = "PDFMiner_HTML"
    PDFMiner = "PDFMiner"
    PyPDF = "PyPDF"
    Unstructured = "Unstructured"


class IndexingConfig(BaseModel):
    tokenizer_chunk_size: int = 3000
    tokenizer_chunk_overlap: int = 200
    pdf_parser: PDFParserEnum = PDFParserEnum.PyMuPDF.name


LOADER_DICT = {
    PDFParserEnum.PyPDF.name: PyPDFLoader,
    PDFParserEnum.PyMuPDF.name: PyMuPDFLoader,
    PDFParserEnum.PDFMiner.name: PDFMinerLoader,
    PDFParserEnum.PDFMiner_HTML.name: PDFMinerPDFasHTMLLoader,
    PDFParserEnum.Unstructured.name: UnstructuredPDFLoader,
}


class PDFExtractionPipeline:
    """Pipeline for extracting text from PDFs and load them into a vectorstore."""

    pipeline_config: IndexingConfig
    pdf_loader: BaseLoader
    db: PGVector | None = None
    embedding: OpenAIEmbeddings

    def __init__(self, pipeline_config: IndexingConfig):
        load_dotenv()

        self.pipeline_config = pipeline_config
        self.pdf_loader = LOADER_DICT[pipeline_config.pdf_parser]
        self.embedding = OpenAIEmbeddings()
        self.connection_str = PGVector.connection_string_from_db_params(
            driver="psycopg2",
            host=settings.DATABASE_HOST,
            port=int(settings.DATABASE_PORT),
            database=settings.PDF_TOOL_DATABASE,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
        )

    def run(self, folder_path: str = None, load_index: bool = True) -> PGVector:
        """Run the PDF extraction pipeline."""
        if load_index:
            logger.info("Loading index from PSQL")
            db = PGVector(
                embedding_function=self.embedding,
                collection_name="pdf_indexing_1",
                connection_string=self.connection_str,
            )
            return db
        else:
            return self._load_documents(folder_path)

    def _pdf_to_docs(self, pdf_dir_path: str) -> List[Document]:
        """
        Using specified PDF miner to convert PDF documents to raw text chunks.

        Fallback: PyPDF
        """
        documents = []
        for file_name in os.listdir(pdf_dir_path):
            file_extension = os.path.splitext(file_name)[1].lower()
            if file_extension == ".pdf":
                logger.info(f"Loading {file_name} into vectorstore")
                file_path = "{}/{}".format(pdf_dir_path, file_name)
                try:
                    loader: BaseLoader = self.pdf_loader(file_path)
                    file_docs = loader.load()
                    documents.extend(file_docs)
                    logger.info(f"{file_name} loaded successfully")
                except Exception as e:
                    logger.error(
                        "Could not extract text from PDF {} with {}: {}".format(
                            file_name, self.pipeline_config.pdf_parser, repr(e)
                        )
                    )

        return documents

    def _load_documents(self, folder_path: str) -> PGVector:
        """Load documents into vectorstore."""
        text_documents = self._pdf_to_docs(folder_path)
        text_splitter = TokenTextSplitter(
            chunk_size=self.pipeline_config.tokenizer_chunk_size,
            chunk_overlap=self.pipeline_config.tokenizer_chunk_overlap,
        )
        texts = text_splitter.split_documents(text_documents)

        # Add metadata for separate filtering
        for text in texts:
            text.metadata["type"] = "Text"

        docs = [*texts]

        logger.info("Loading {} text-documents into vectorstore".format(len(texts)))
        return PGVector.from_documents(
            embedding=self.embedding,
            documents=docs,
            collection_name="pdf_indexing_1",
            connection_string=self.connection_str,
            pre_delete_collection=True,
        )


def run_pdf_ingestion_pipeline(load_index: bool = True) -> None:
    """Run the PDF ingestion pipeline."""
    pdf_pipeline.run(settings.PDF_TOOL_DATA_PATH, load_index)


if settings.PDF_TOOL_ENABLED:
    extraction_pipeline_config = Config(settings.PDF_TOOL_EXTRACTION_CONFIG_PATH).read()
    pdf_pipeline = PDFExtractionPipeline(pipeline_config=extraction_pipeline_config.indexing)
else:
    pdf_pipeline = PDFExtractionPipeline(pipeline_config=IndexingConfig())


if __name__ == "__main__":
    run_pdf_ingestion_pipeline(load_index=False)
