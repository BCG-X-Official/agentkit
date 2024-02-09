# -*- coding: utf-8 -*-
# mypy: disable-error-code="attr-defined"
from fastapi import APIRouter
from fastapi_cache.decorator import cache

from app.db.session import sql_tool_db
from app.schemas.response_schema import IGetResponseBase, create_response
from app.schemas.tool_schemas.sql_tool_schema import ExecutionResult
from app.utils.sql import is_sql_query_safe

router = APIRouter()


@router.get("/execute")
@cache(expire=600)  # -> Bug on POST requests https://github.com/long2ice/fastapi-cache/issues/113
async def execute_sql(
    statement: str,
) -> IGetResponseBase[ExecutionResult]:
    """Executes an SQL query on the database and returns the result."""
    if not is_sql_query_safe(statement):
        return create_response(
            message="SQL query contains forbidden keywords (DML, DDL statements)",
            data=None,
            meta={},
        )
    if sql_tool_db is None:
        return create_response(
            message="SQL query execution is disabled",
            data=None,
            meta={},
        )

    try:
        (
            columns,
            rows,
        ) = sql_tool_db.execute(statement)
        execution_result = ExecutionResult(
            raw_result=[
                dict(
                    zip(
                        columns,
                        row,
                    )
                )
                for row in rows
            ],
            affected_rows=None,
            error=None,
        )
    except Exception as e:
        return create_response(
            message=repr(e),
            data=None,
        )

    return create_response(
        message="Successfully executed SQL query",
        data=execution_result,
    )
