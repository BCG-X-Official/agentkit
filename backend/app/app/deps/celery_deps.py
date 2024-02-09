# -*- coding: utf-8 -*-
from typing import Generator

from celery_sqlalchemy_scheduler.session import SessionManager

from app.core.config import settings


def get_job_db() -> Generator:
    session_manager = SessionManager()
    (
        _,
        _session,
    ) = session_manager.create_session(settings.SYNC_CELERY_BEAT_DATABASE_URI)

    with _session() as session:
        yield session
