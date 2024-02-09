# -*- coding: utf-8 -*-
# pylint: disable=no-self-use
import logging
import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector

from app.core.config import settings
from app.utils.config import Config

logger = logging.getLogger(__name__)


class CodeIngestionPipeline:
    """Pipeline for ingesting python code in PGVector DB."""

    db: PGVector | None = None
    embedding: OpenAIEmbeddings

    def __init__(self, db_name: str):
        load_dotenv()
        self.embedding = OpenAIEmbeddings()
        self.connection_str = PGVector.connection_string_from_db_params(
            driver="psycopg2",
            host=settings.DATABASE_HOST,
            port=int(settings.DATABASE_PORT),
            database=db_name,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
        )

    def get_db(self, collection_name: str = "code_indexing_1") -> PGVector:
        """
        Get vector database instance for specified collection name.

        Args:
            collection_name (str): Vector database collection name

        Returns:
            PGVector: Vector database
        """
        db = PGVector(
            embedding_function=self.embedding,
            collection_name=collection_name,
            connection_string=self.connection_str,
        )
        return db

    def run(
        self,
        folder_path: Optional[str] = None,
        load_index: bool = True,
        collection_name: str = "code_indexing_1",
    ) -> PGVector:
        """
        Run the PDF ingestion pipeline.

        Args:
            folder_path (str, optional): Ingest docs from this folder. Defaults to None.
            load_index (bool, optional): Whether to load the index or ingest new docs. Defaults to True.
            collection_name (str, optional): PGVector collection name. Defaults to "pdf_indexing_1".

        Returns:
            PGVector: Vector database
        """
        if load_index:
            logger.info(f"**Getting vectore database collection:{collection_name}...**")
            return self.get_db(collection_name=collection_name)
        if folder_path is None:
            raise ValueError("Please provide a folder_path to ingest documents from.")
        logger.info(f"**Ingesting files from {folder_path} to collection {collection_name}...**")
        return self._ingest_documents(folder_path=folder_path, collection_name=collection_name)

    def _ingest_documents(self, folder_path: str, collection_name: str) -> PGVector:
        """Run documents ingestion pipeline."""
        code_db = self._ingest_code(folder_path=folder_path, collection_name=collection_name)
        return code_db

    def _code_to_docs(self, code_dir_path: str) -> List[Document]:
        tool_prompts = Config(Path(settings.TOOL_PROMPTS_PATH)).read()
        documents = []
        for folder, _, files in os.walk(code_dir_path):
            for file in files:
                if file[-3:] == ".py" and file != "__init__.py":
                    metadata = {"source": file}
                    if file[-7:] == "tool.py":
                        metadata["tool_prompt"] = getattr(tool_prompts.library, file[:-3])
                    else:
                        metadata["tool_prompt"] = None  # type: ignore

                    filepath = os.path.join(folder, file)
                    logger.info(f"Loading code file: {filepath}")
                    with open(filepath, "r", encoding="utf-8") as f:
                        code_file_content = f.read()
                    doc = Document(page_content=code_file_content, metadata=metadata)
                    documents.append(doc)
        return documents

    def _ingest_code(self, folder_path: str, collection_name: str) -> PGVector:
        docs = self._code_to_docs(folder_path)
        logger.info(f"Loading {len(docs)} code files into vectorstore...")
        return PGVector.from_documents(
            embedding=self.embedding,
            documents=docs,
            collection_name=collection_name,
            connection_string=self.connection_str,
            pre_delete_collection=True,
        )


def get_code_pipeline() -> CodeIngestionPipeline:
    pdf_pipeline = CodeIngestionPipeline(
        db_name=settings.CODE_TOOL_DATABASE,
    )
    return pdf_pipeline


def run_code_ingestion_pipeline(load_index: bool = False) -> None:
    """Run the Code ingestion pipeline."""
    get_code_pipeline().run(
        settings.CODE_TOOL_DATA_PATH,
        collection_name="code_indexing_1",
        load_index=load_index,
    )


if __name__ == "__main__":
    run_code_ingestion_pipeline(load_index=False)
