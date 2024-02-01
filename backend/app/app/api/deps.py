# -*- coding: utf-8 -*-
"""
This python module provides a set of utility functions which can be used to create and
handle connections and sessions to various services such as Redis, PostgreSQL (via
SQLModel's AsyncSession), and Minio, as well as for handling OAuth2 authentication using
FastAPI's OAuth2PasswordBearer.

Example usage:
from fastapi import Depends
from .db_utils import get_db, get_redis_client, reusable_oauth2

@app.get("/users/")
async def read_users(
    redis=Depends(get_redis_client),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
):
    ...
"""
from collections.abc import AsyncGenerator

import redis.asyncio as aioredis
from fastapi.security import OAuth2PasswordBearer
from fastapi_nextauth_jwt import NextAuthJWT
from langchain_community.storage import RedisStore
from redis import Redis as RedisSync
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.requests import Request

from app.core.config import settings
from app.db.session import SessionLocal, SessionLocalCelery
from app.utils.minio_client import MinioClient

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")


def get_redis_store() -> RedisStore:
    store = RedisStore(
        redis_url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        client_kwargs={"db": 2},
        namespace="embedding_caches",
    )
    return store


def get_redis_client_sync() -> RedisSync:
    """Returns a synchronous Redis client."""
    return RedisSync(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        decode_responses=True,
    )


async def get_redis_client() -> Redis:
    """Returns an asynchronous Redis client as a coroutine function which should be
    awaited."""
    return await aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        max_connections=10,
        encoding="utf8",
        decode_responses=True,
    )


async def get_db() -> AsyncGenerator[
    AsyncSession,
    None,
]:
    """Returns an asynchronous database session as a coroutine function which should be
    awaited."""
    async with SessionLocal() as session:
        yield session


async def get_jobs_db() -> AsyncGenerator[
    AsyncSession,
    None,
]:
    """Returns an asynchronous database session as a coroutine function which should be
    awaited."""
    async with SessionLocalCelery() as session:
        yield session


def minio_auth() -> MinioClient:
    """Returns a MinioClient instance."""
    return MinioClient(
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        bucket_name=settings.MINIO_BUCKET,
        minio_url=settings.MINIO_URL,
    )


def get_jwt(req: Request) -> NextAuthJWT:
    """Returns a NextAuthJWT instance."""
    if not settings.ENABLE_AUTH:
        return None
    if not settings.NEXTAUTH_SECRET:
        raise ValueError("Authentication enabled, but NextAuth secret is not set")

    return NextAuthJWT(
        secret=settings.NEXTAUTH_SECRET,
        csrf_prevention_enabled=False,
    )(req)
