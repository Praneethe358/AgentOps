from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class TaskSubmitRequest(BaseModel):
    task_description: str = Field(..., example="Write a python function `is_prime(n)` to test if a number is prime.")
    code_context: Optional[str] = Field(default="# Empty context", example="def is_prime(n):\n    pass")

class TaskSubmitResponse(BaseModel):
    task_id: str
    thread_id: str
    message: str

class HumanApprovalRequest(BaseModel):
    approved: bool = Field(..., example=True)

class ThreadStateResponse(BaseModel):
    thread_id: str
    is_paused: bool
    next_node: Optional[List[str]]
    current_values: Dict[str, Any]
    interrupt_payload: Optional[Dict[str, Any]]
