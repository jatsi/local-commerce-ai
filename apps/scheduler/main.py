from apps.worker.main import celery_app


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(1800.0, "apps.worker.tasks.collect_analytics")
