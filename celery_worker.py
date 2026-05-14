from celery import Celery
from app.config import REDIS_URL

celery_app = Celery(
    "codebase_assistant",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_max_retries=3
)

from app.indexing import celery_tasks
