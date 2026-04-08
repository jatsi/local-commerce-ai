from celery import Celery
from apps.api_gateway.app.core.config import settings

broker = f"redis://{settings.redis_host}:{settings.redis_port}/0"
backend = f"redis://{settings.redis_host}:{settings.redis_port}/1"

celery_app = Celery("local_commerce_ai", broker=broker, backend=backend)
celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
