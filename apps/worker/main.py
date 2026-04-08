from apps.api_gateway.app.tasks.celery_app import celery_app
import apps.api_gateway.app.tasks.job_tasks  # noqa: F401

if __name__ == "__main__":
    celery_app.worker_main([
        "worker",
        "--loglevel=INFO",
        "--pool=solo",
    ])
