# -*- coding: utf-8 -*-
from typing import List, Optional

from pydantic import BaseModel, Field


class PdfAppendix(BaseModel):
    doc_id: str
    page_numbers: List[int]
    reference_text: str


class MarkdownMetadata(BaseModel):
    type: str
    source: str
    header1: Optional[str] = Field(None, alias="Header 1")
