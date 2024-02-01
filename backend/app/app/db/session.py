# -*- coding: utf-8 -*-
import logging
import os.path
from typing import List

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.db.SQLDatabaseExtended import SQLDatabaseExtended
from app.schemas.tool_schemas.sql_tool_schema import DatabaseInfo, TableInfo

DB_POOL_SIZE = 83
WEB_CONCURRENCY = 9
POOL_SIZE = max(
    DB_POOL_SIZE // WEB_CONCURRENCY,
    5,
)

logger = logging.getLogger(__name__)


def _get_local_session() -> sessionmaker:
    engine = (
        create_async_engine(
            url=settings.ASYNC_DATABASE_URI,
            future=True,
            pool_size=POOL_SIZE,
            max_overflow=64,
        )
        if settings.ASYNC_DATABASE_URI is not None
        else None
    )
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,  # type: ignore
        class_=AsyncSession,
        expire_on_commit=False,
    )


def _get_local_celery_session() -> sessionmaker:
    engine_celery = (
        create_async_engine(
            url=settings.ASYNC_CELERY_BEAT_DATABASE_URI,
            future=True,
            pool_size=POOL_SIZE,
            max_overflow=64,
        )
        if settings.ASYNC_CELERY_BEAT_DATABASE_URI is not None
        else None
    )
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine_celery,  # type: ignore
        class_=AsyncSession,
        expire_on_commit=False,
    )


def get_sql_tool_db() -> SQLDatabaseExtended:
    """Get the SQL database."""
    if os.path.isfile(settings.SQL_TOOL_DB_INFO_PATH) and settings.SQL_TOOL_DB_OVERWRITE_ON_START is False:
        db_info = DatabaseInfo.parse_file(settings.SQL_TOOL_DB_INFO_PATH)
    else:
        os.makedirs(
            "app/tool_constants",
            exist_ok=True,
        )
        db_info = _get_table_infos_multi_db(settings.SQL_TOOL_DB_SCHEMAS)
        with open(
            settings.SQL_TOOL_DB_INFO_PATH,
            "w",
            encoding="utf-8",
        ) as f:
            f.write(db_info.model_dump_json(indent=4))

    return SQLDatabaseExtended.from_uri(
        settings.SQL_TOOL_DB_URI,
        db_info=db_info,
    )


def _get_table_infos_multi_db(
    schema_names: List[str],
) -> DatabaseInfo:
    """Get the table information for multiple databases."""
    tables = []
    for schema_name in schema_names:
        database = SQLDatabaseExtended.from_uri(
            settings.SQL_TOOL_DB_URI,
            schema=schema_name,
        )
        table_names = list(set(database.get_usable_table_names()))
        for table_name in table_names:
            try:
                table_info = database.get_table_info_no_throw([table_name])
            except Exception as e:
                logger.error(f"Failed to get table info for {table_name}: {e}")
                table_info = f"Failed to get table info for {table_name}: {e}"
            tables.append(
                TableInfo(
                    schema_name=schema_name,
                    table_name=table_name,
                    structure=table_info,
                )
            )

    return DatabaseInfo(tables=tables)


sql_tool_db = get_sql_tool_db() if settings.SQL_TOOL_DB_ENABLED else None

SessionLocal = _get_local_session()
SessionLocalCelery = _get_local_celery_session()
