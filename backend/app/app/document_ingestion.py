# -*- coding: utf-8 -*-
from app.core.config import settings
from app.db.vector_db_code_ingestion import run_code_ingestion_pipeline
from app.db.vector_db_pdf_ingestion import run_pdf_ingestion_pipeline


def pdf_pipeline() -> None:
    if settings.PDF_TOOL_ENABLED:
        run_pdf_ingestion_pipeline(load_index=False)
    if settings.CODE_TOOL_ENABLED:
        run_code_ingestion_pipeline(load_index=False)


pdf_pipeline()
