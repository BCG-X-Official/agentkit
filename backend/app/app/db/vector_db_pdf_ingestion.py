# -*- coding: utf-8 -*-
import csv
import logging
import os
from typing import Any, List

import psycopg2
from dotenv import load_dotenv
from langchain.document_loaders.base import BaseLoader
from langchain.embeddings import CacheBackedEmbeddings
from langchain.schema import Document
from langchain.text_splitter import TokenTextSplitter
from langchain.vectorstores.pgvector import PGVector

from app.core.config import settings
from app.schemas.ingestion_schema import LOADER_DICT, IndexingConfig
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
        self.db_connection = psycopg2.connect(
            dbname=db_name,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
        )
        self.db_cursor = self.db_connection.cursor()

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

    def _file_already_loaded(self, file_path: str, collection_name: str) -> bool:
        """Check if file is already loaded based on its path using direct SQL query."""
        try:
            query = """
            SELECT EXISTS(
                SELECT 1
                FROM langchain_pg_embedding e
                JOIN langchain_pg_collection c on c.uuid = e.collection_id
                WHERE c.name = %s AND e.cmetadata->>'source' = %s
            );
            """
            self.db_cursor.execute(query, (collection_name, file_path))
            return self.db_cursor.fetchone()[0]
        except Exception as e:
            logger.error("Error checking if file is already loaded.")
            logger.error(repr(e))
            return False

    def _load_docs(
        self,
        dir_path: str,
        collection_name: str,
    ) -> List[Document]:
        """
        Using specified PDF miner to convert PDF documents into raw text chunks.
        Also supports loading .txt (plain text) files and loads files from subfolders.
        Only loads files not already in the database.

        Fallback: PyPDF
        """
        documents = []
        for root, _, files in os.walk(dir_path):
            for file_name in files:
                file_extension = os.path.splitext(file_name)[1].lower()
                file_path = os.path.join(root, file_name)

                if not self._file_already_loaded(file_path, collection_name):
                    # Load PDF files
                    if file_extension == ".pdf":
                        logger.info(f"Loading {file_name} into vectorstore")
                        try:
                            loader: Any = self.pdf_loader(file_path)  # type: ignore
                            file_docs = loader.load()
                            documents.extend(file_docs)
                            logger.info(f"{file_name} loaded successfully")
                        except Exception as e:
                            logger.error(
                                f"Could not extract text from PDF {file_name} with {self.pipeline_config.pdf_parser}: {repr(e)}"  # noqa: E501
                            )

                    # Load Markdown or Plain Text files
                    elif file_extension in (".md", ".txt"):
                        file_type = "markdown" if file_extension == ".md" else "plain text"
                        logger.info(f"Loading data from {file_name} as Document ({file_type})...")
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                file_content = f.read()

                            file_doc = Document(
                                page_content=file_content,
                                metadata={"source": file_path, "type": file_type},
                            )

                            text_splitter = TokenTextSplitter(
                                chunk_size=self.pipeline_config.tokenizer_chunk_size,
                                chunk_overlap=self.pipeline_config.tokenizer_chunk_overlap,
                            )
                            file_docs = text_splitter.split_documents([file_doc])

                            documents.extend(file_docs)
                            if len(file_docs) > 1:
                                logger.info(
                                    f"Split {file_name} into {len(file_docs)} documents due to chunk size: ({self.pipeline_config.tokenizer_chunk_size})"  # noqa: E501
                                )
                        except Exception as e:
                            logger.error(f"Could not load {file_type} file {file_name}: {repr(e)}")

                    # Load CSV files
                    elif file_extension == ".csv":
                        logger.info(f"Loading data from {file_name} as CSV Document...")
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                csv_reader = csv.DictReader(f)
                                for row in csv_reader:
                                    text = row["text"]
                                    metadata = {key: value for key, value in row.items() if key != "text"}
                                    metadata["source"] = file_path
                                    metadata["type"] = "csv"

                                    file_doc = Document(
                                        page_content=text,
                                        metadata=metadata,
                                    )

                                    text_splitter = TokenTextSplitter(
                                        chunk_size=self.pipeline_config.tokenizer_chunk_size,
                                        chunk_overlap=self.pipeline_config.tokenizer_chunk_overlap,
                                    )
                                    file_docs = text_splitter.split_documents([file_doc])

                                    documents.extend(file_docs)
                                    if len(file_docs) > 1:
                                        logger.info(
                                            f"Split {file_name} into {len(file_docs)} documents due to chunk size: ({self.pipeline_config.tokenizer_chunk_size})"  # noqa: E501
                                        )
                        except Exception as e:
                            logger.error(f"Could not load CSV file {file_name}: {repr(e)}")

                else:
                    logger.info(f"File {file_name} already loaded, skipping.")

        return documents

    def _load_documents(
        self,
        folder_path: str,
        collection_name: str,
    ) -> PGVector:
        """Load documents into vectorstore."""
        text_documents = self._load_docs(folder_path, collection_name)
        text_splitter = TokenTextSplitter(
            chunk_size=self.pipeline_config.tokenizer_chunk_size,
            chunk_overlap=self.pipeline_config.tokenizer_chunk_overlap,
        )
        texts = text_splitter.split_documents(text_documents)

        # Add metadata for separate filtering
        for text in texts:
            text.metadata["type"] = "Text"

        docs = [*texts]

        logger.info(f"Loading {len(texts)} text-documents into vectorstore")
        return PGVector.from_documents(
            embedding=self.embedding,
            documents=docs,
            collection_name=collection_name,
            connection_string=self.connection_str,
            pre_delete_collection=False,
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
