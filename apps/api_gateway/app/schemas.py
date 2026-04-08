from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    name: str = Field(..., examples=["launch_product"])
    payload: dict = Field(default_factory=dict)


class ApprovalUpdate(BaseModel):
    reviewer: str
    approved: bool
    comment: str | None = None
