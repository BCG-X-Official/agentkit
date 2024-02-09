# -*- coding: utf-8 -*-
from caseconverter import camelcase
from pydantic import BaseModel


class QueryBase(BaseModel):
    """Query base schema."""

    class Config:
        populate_by_name = True

        @staticmethod
        def alias_generator(
            s: str,
        ) -> str:
            return camelcase(s)
