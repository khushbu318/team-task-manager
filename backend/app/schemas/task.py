from pydantic import BaseModel

from backend.app.models.task import TaskStatus

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assignee_id: int

class TaskUpdate(BaseModel):
    status: TaskStatus | None = None
    current_state: str | None = None
    blocker: str | None = None
    permission_issue: str | None = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    current_state: str | None
    blocker: str | None
    permission_issue: str | None
    assignee_id: int