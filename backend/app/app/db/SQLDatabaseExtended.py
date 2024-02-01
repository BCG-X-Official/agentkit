# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from typing import Any, List, Optional, Sequence, Tuple

from langchain.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.result import Row

from app.schemas.tool_schemas.sql_tool_schema import DatabaseInfo

logger = logging.getLogger(__name__)


class SQLDatabaseExtended(SQLDatabase):
    """SQL database wrapper."""

    db_info: Optional[DatabaseInfo]

    def __init__(
        self,
        engine: Engine,
        db_info: Optional[DatabaseInfo] = None,
        **kwargs: Any,
    ):
        """Initialize the SQL database."""
        super().__init__(
            engine,
            **kwargs,
        )
        self.db_info = db_info

    def execute(
        self,
        command: str,
    ) -> Tuple[list[str], list[Row],]:
        with self._engine.begin() as connection:
            if self._schema is not None:
                if self.dialect == "snowflake":
                    connection.exec_driver_sql(f"ALTER SESSION SET search_path='{self._schema}'")
                else:
                    connection.exec_driver_sql(f"SET search_path TO {self._schema}")
            cursor = connection.execute(text(command))
            columns: List[str] = list(cursor.keys())
            rows: List[Row] = cursor.all()  # type: ignore
            return (
                columns,
                rows,
            )

    def run_no_str(
        self,
        command: str,
        fetch: str = "all",
    ) -> Sequence | Row | List[Row] | None:
        """
        Execute a SQL command and return the results.

        If the statement returns rows, the results are returned. If the statement
        returns no rows, None is returned.
        """
        with self._engine.begin() as connection:
            if self._schema is not None:
                if self.dialect == "snowflake":
                    connection.exec_driver_sql(f"ALTER SESSION SET search_path='{self._schema}'")
                else:
                    connection.exec_driver_sql(f"SET search_path TO {self._schema}")
            cursor = connection.execute(text(command))
            if cursor.returns_rows:
                if fetch == "all":
                    result = cursor.fetchall()
                elif fetch == "one":
                    result = cursor.fetchone()[0]  # type: ignore
                else:
                    raise ValueError("Fetch parameter must be either 'one' or 'all'")
                return result
        return None

    @classmethod
    def from_uri(
        cls,
        database_uri: str,
        engine_args: Optional[dict] = None,
        **kwargs: Any,
    ) -> SQLDatabaseExtended:
        """Construct a SQLAlchemy engine from URI."""
        _engine_args = engine_args or {}
        return cls(
            create_engine(
                database_uri,
                **_engine_args,
            ),
            **kwargs,
        )
