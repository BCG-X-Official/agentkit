# -*- coding: utf-8 -*-
from typing import List

from pydantic import BaseModel


class PdfAppendix(BaseModel):
    doc_id: str
    page_numbers: List[int]
    reference_text: str
