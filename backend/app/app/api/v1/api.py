# -*- coding: utf-8 -*-
from fastapi import APIRouter

from app.api.v1.endpoints import chat, sql, statistics

api_router = APIRouter()
api_router.include_router(
    sql.router,
    prefix="/sql",
    tags=["sql"],
)
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"],
)
api_router.include_router(
    statistics.router,
    prefix="/statistics",
    tags=["statistics"],
)
