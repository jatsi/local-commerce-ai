from datetime import datetime
from apps.worker.main import celery_app
from memory.postgres.session import SessionLocal
from memory.postgres.models import AnalyticsSnapshot, Job
from orchestrator.executor import Orchestrator


@celery_app.task(name="run_job_async")
def run_job_async(job_id: str) -> dict:
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        if not job:
            return {"error": "job_not_found", "job_id": job_id}
        job.status = "running"
        db.commit()
        orchestrator = Orchestrator()
        result = orchestrator.run(job.name, job.payload, db=db, job_id=job.id)
        job.status = "completed"
        db.commit()
        return result
    except Exception as exc:  # noqa: BLE001
        job = db.get(Job, job_id)
        if job:
            job.status = "failed"
            db.commit()
        return {"error": str(exc), "job_id": job_id}
    finally:
        db.close()


@celery_app.task(name="apps.worker.tasks.collect_analytics")
def collect_analytics() -> dict:
    db = SessionLocal()
    try:
        snap = AnalyticsSnapshot(source="scheduler", metrics={"heartbeat": 1, "ts": datetime.utcnow().isoformat()})
        db.add(snap)
        db.commit()
        return {"status": "ok", "snapshot_id": snap.id}
    finally:
        db.close()
