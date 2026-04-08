from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from apps.api_gateway.app.deps import get_db
from apps.api_gateway.app.schemas import JobCreate, ApprovalUpdate
from memory.postgres.models import Approval, Job
from orchestrator.executor import Orchestrator
from apps.worker.tasks import run_job_async

app = FastAPI(title="Local Commerce AI API Gateway")
orchestrator = Orchestrator()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/jobs")
def create_job(job_data: JobCreate, db: Session = Depends(get_db)) -> dict:
    job = Job(name=job_data.name, payload=job_data.payload, status="queued")
    db.add(job)
    db.commit()
    db.refresh(job)
    run_job_async.delay(job.id)
    return {"job_id": job.id, "status": job.status}


@app.get("/jobs")
def list_jobs(db: Session = Depends(get_db)) -> list[dict]:
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(100).all()
    return [{"id": j.id, "name": j.name, "status": j.status} for j in jobs]


@app.post("/approvals/{approval_id}")
def resolve_approval(approval_id: str, data: ApprovalUpdate, db: Session = Depends(get_db)) -> dict:
    approval = db.get(Approval, approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="approval_not_found")
    approval.status = "approved" if data.approved else "rejected"
    approval.reviewer = data.reviewer
    approval.comment = data.comment
    db.commit()
    return {"approval_id": approval.id, "status": approval.status}


@app.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)) -> dict:
    return {
        "jobs": db.query(Job).count(),
        "pending_approvals": db.query(Approval).filter(Approval.status == "pending").count(),
    }
