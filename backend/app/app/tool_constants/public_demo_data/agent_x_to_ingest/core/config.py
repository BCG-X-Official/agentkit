# -*- coding: utf-8 -*-
import os
import secrets
from typing import Any, Optional

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    DEV_MODE_LIGHT: bool = False
    API_VERSION: str = "v1"
    API_V1_STR: str = f"/api/{API_VERSION}"
    PROJECT_NAME: str
    OPENAI_API_KEY: str
    OPENAI_ORGANIZATION: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int | str
    DATABASE_NAME: str
    DATABASE_CELERY_NAME: str = "celery_schedule_jobs"
    REDIS_HOST: str
    REDIS_PORT: str
    DB_POOL_SIZE = 83
    WEB_CONCURRENCY = 9
    POOL_SIZE = max(DB_POOL_SIZE // WEB_CONCURRENCY, 5)
    ASYNC_DATABASE_URI: PostgresDsn | None

    @validator("ASYNC_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("DATABASE_USER"),
            password=values.get("DATABASE_PASSWORD"),
            host=values.get("DATABASE_HOST"),
            port=str(values.get("DATABASE_PORT")),
            path=f"/{values.get('DATABASE_NAME') or ''}",
        )

    SYNC_CELERY_DATABASE_URI: str | None

    @validator("SYNC_CELERY_DATABASE_URI", pre=True)
    def assemble_celery_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="db+postgresql",
            user=values.get("DATABASE_USER"),
            password=values.get("DATABASE_PASSWORD"),
            host=values.get("DATABASE_HOST"),
            port=str(values.get("DATABASE_PORT")),
            path=f"/{values.get('DATABASE_CELERY_NAME') or ''}",
        )

    SYNC_CELERY_BEAT_DATABASE_URI: str | None

    @validator("SYNC_CELERY_BEAT_DATABASE_URI", pre=True)
    def assemble_celery_beat_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            user=values.get("DATABASE_USER"),
            password=values.get("DATABASE_PASSWORD"),
            host=values.get("DATABASE_HOST"),
            port=str(values.get("DATABASE_PORT")),
            path=f"/{values.get('DATABASE_CELERY_NAME') or ''}",
        )

    ASYNC_CELERY_BEAT_DATABASE_URI: str | None

    @validator("ASYNC_CELERY_BEAT_DATABASE_URI", pre=True)
    def assemble_async_celery_beat_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("DATABASE_USER"),
            password=values.get("DATABASE_PASSWORD"),
            host=values.get("DATABASE_HOST"),
            port=str(values.get("DATABASE_PORT")),
            path=f"/{values.get('DATABASE_CELERY_NAME') or ''}",
        )

    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_URL: str
    MINIO_BUCKET: str

    SECRET_KEY: str = secrets.token_urlsafe(32)
    BACKEND_CORS_ORIGINS: list[str] | list[AnyHttpUrl]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PDF_TOOL_EXTRACTION_CONFIG_PATH: str
    AGENT_CONFIG_PATH: str

    ################################
    # Tool specific configuration
    ################################
    SQL_TOOL_DB_ENABLED: bool
    SQL_TOOL_DB_SCHEMAS: list[str] = []
    SQL_TOOL_DB_INFO_PATH: str
    SQL_TOOL_DB_URI: str
    SQL_TOOL_DB_OVERWRITE_ON_START: bool = True

    @validator("SQL_TOOL_DB_URI", pre=True)
    def assemble_sql_tool_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if not values.get("SQL_TOOL_DB_ENABLED"):
            return ""
        if isinstance(v, str):
            return make_url(v).render_as_string(hide_password=False)
        raise ValueError(v)

    PDF_TOOL_ENABLED: bool
    PDF_TOOL_DATA_PATH: str
    PDF_TOOL_DATABASE: str

    class Config:
        case_sensitive = True
        env_file = "./.env" if os.path.isfile("./.env") else os.path.expanduser("~/.env")


settings = Settings()
