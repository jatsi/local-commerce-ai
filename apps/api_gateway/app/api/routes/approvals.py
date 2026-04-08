from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from apps.api_gateway.app.db.session import get_db
from apps.api_gateway.app.repositories.approval_repository import ApprovalRepository
from apps.api_gateway.app.schemas.approvals import ApprovalDecisionRequest

router = APIRouter()
repo = ApprovalRepository()

@router.get("/{approval_id}")
def get_approval(approval_id: int, db: Session = Depends(get_db)):
    approval = repo.get(db, approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="approval not found")
    return approval

@router.post("/{approval_id}/approve")
def approve(approval_id: int, payload: ApprovalDecisionRequest, db: Session = Depends(get_db)):
    approval = repo.set_status(db, approval_id, "approved", payload.reviewer, payload.comment)
    if not approval:
        raise HTTPException(status_code=404, detail="approval not found")
    return approval

@router.post("/{approval_id}/reject")
def reject(approval_id: int, payload: ApprovalDecisionRequest, db: Session = Depends(get_db)):
    approval = repo.set_status(db, approval_id, "rejected", payload.reviewer, payload.comment)
    if not approval:
        raise HTTPException(status_code=404, detail="approval not found")
    return approval
