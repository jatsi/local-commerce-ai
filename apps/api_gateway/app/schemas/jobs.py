from pydantic import BaseModel, Field
from typing import Any, Dict

class CreateJobRequest(BaseModel):
    task_type: str = Field(..., examples=["publish_product"])
    context: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
