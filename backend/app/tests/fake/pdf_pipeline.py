# -*- coding: utf-8 -*-
from langchain.vectorstores import VectorStore

from app.db.vector_db_pdf_ingestion import PDFExtractionPipeline


class FakePDFExtractionPipeline(PDFExtractionPipeline):
    def __init__(self, vector_db: VectorStore):
        self.vector_db = vector_db

    def run(self, **kwargs):
        return self.vector_db
