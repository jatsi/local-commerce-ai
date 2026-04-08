from celery import Celery
from apps.api_gateway.app.settings import settings

celery_app = Celery(
    "local_commerce_ai",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_app.autodiscover_tasks(["apps.worker"])
