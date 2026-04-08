from pydantic import BaseModel

class ApprovalDecisionRequest(BaseModel):
    reviewer: str
    comment: str | None = None
