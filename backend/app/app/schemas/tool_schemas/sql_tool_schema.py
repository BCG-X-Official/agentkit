# -*- coding: utf-8 -*-
from typing import Any, List

from pydantic import BaseModel

from app.schemas.common_schema import QueryBase


class TableInfo(BaseModel):
    """Table information."""

    schema_name: str
    table_name: str
    structure: str

    @property
    def name(
        self,
    ) -> str:
        return self.schema_name + "." + self.table_name


class DatabaseInfo(BaseModel):
    """Database information."""

    tables: List[TableInfo]


class ExecutionResult(QueryBase):
    raw_result: List[
        dict[
            str,
            Any,
        ]
    ]
    affected_rows: int | None = None
    error: str | None = None
