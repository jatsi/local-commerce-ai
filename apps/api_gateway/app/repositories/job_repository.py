from sqlalchemy.orm import Session
from apps.api_gateway.app.models.job import Job

class JobRepository:
    def create(self, db: Session, task_type: str, context: dict, constraints: dict) -> Job:
        job = Job(task_type=task_type, context=context, constraints=constraints, status="queued")
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    def get(self, db: Session, job_id: int) -> Job | None:
        return db.get(Job, job_id)

    def update_status(self, db: Session, job_id: int, status: str, result: dict | None = None, error_message: str | None = None) -> Job | None:
        job = db.get(Job, job_id)
        if not job:
            return None
        job.status = status
        if result is not None:
            job.result = result
        if error_message is not None:
            job.error_message = error_message
        db.commit()
        db.refresh(job)
        return job
