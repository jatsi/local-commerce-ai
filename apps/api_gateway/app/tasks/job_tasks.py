from apps.api_gateway.app.tasks.celery_app import celery_app
from apps.api_gateway.app.db.session import SessionLocal
from apps.api_gateway.app.repositories.job_repository import JobRepository
from orchestrator.executor import run_job

@celery_app.task(name="process_job")
def process_job(job_id: int) -> dict:
    db = SessionLocal()
    repo = JobRepository()
    try:
        job = repo.get(db, job_id)
        if not job:
            return {"status": "error", "message": "job not found"}

        repo.update_status(db, job_id, "running")
        result = run_job({
            "id": job.id,
            "task_type": job.task_type,
            "context": job.context,
            "constraints": job.constraints,
        })
        repo.update_status(db, job_id, "completed", result=result)
        return result
    except Exception as exc:
        repo.update_status(db, job_id, "failed", error_message=str(exc))
        raise
    finally:
        db.close()
