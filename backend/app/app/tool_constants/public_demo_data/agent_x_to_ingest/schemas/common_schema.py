# -*- coding: utf-8 -*-
from humps.camel import case
from pydantic import BaseModel


class QueryBase(BaseModel):
    """Query base schema."""

    class Config:
        allow_population_by_field_name = True

        @staticmethod
        def alias_generator(s):
            return case(s)
