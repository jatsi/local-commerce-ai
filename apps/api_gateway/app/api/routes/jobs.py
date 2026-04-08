from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from apps.api_gateway.app.schemas.jobs import CreateJobRequest
from apps.api_gateway.app.db.session import get_db
from apps.api_gateway.app.repositories.job_repository import JobRepository
from apps.api_gateway.app.tasks.job_tasks import process_job

router = APIRouter()
repo = JobRepository()

@router.post("/create")
def create_job(payload: CreateJobRequest, db: Session = Depends(get_db)):
    job = repo.create(db, payload.task_type, payload.context, payload.constraints)
    task = process_job.delay(job.id)
    return {
        "message": "job queued",
        "job_id": job.id,
        "celery_task_id": task.id,
        "status": job.status,
    }

@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = repo.get(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return {
        "id": job.id,
        "task_type": job.task_type,
        "status": job.status,
        "context": job.context,
        "constraints": job.constraints,
        "result": job.result,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }
