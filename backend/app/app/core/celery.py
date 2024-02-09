# -*- coding: utf-8 -*-
# Celery is good for data-intensive application or some long-running tasks in other simple cases use Fastapi background
# tasks
# Reference https://towardsdatascience.com/deploying-ml-models-in-production-with-fastapi-and-celery-7063e539a5db
from celery import Celery

from app.core.config import settings

celery = Celery(
    "async_task",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    backend=settings.SYNC_CELERY_DATABASE_URI,
    include="app.api.celery_task",  # route where tasks are defined
)

celery.conf.update({"beat_dburi": settings.SYNC_CELERY_BEAT_DATABASE_URI})
celery.autodiscover_tasks()
