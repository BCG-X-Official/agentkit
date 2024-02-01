# -*- coding: utf-8 -*-
from app.core.config import settings
from app.db.vector_db_pdf_ingestion import run_pdf_ingestion_pipeline


def pdf_pipeline() -> None:
    if settings.PDF_TOOL_ENABLED:
        run_pdf_ingestion_pipeline(load_index=False)


pdf_pipeline()
