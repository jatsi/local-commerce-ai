from sqlalchemy.orm import Session
from apps.api_gateway.app.models.approval import Approval

class ApprovalRepository:
    def create(self, db: Session, job_id: int, approval_type: str, payload: dict) -> Approval:
        item = Approval(job_id=job_id, approval_type=approval_type, payload=payload, status="pending")
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def get(self, db: Session, approval_id: int) -> Approval | None:
        return db.get(Approval, approval_id)

    def set_status(self, db: Session, approval_id: int, status: str, reviewer: str | None = None, comment: str | None = None) -> Approval | None:
        item = db.get(Approval, approval_id)
        if not item:
            return None
        item.status = status
        item.reviewer = reviewer
        item.comment = comment
        db.commit()
        db.refresh(item)
        return item
