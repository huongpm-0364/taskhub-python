from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.task import TaskStatus


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.todo


class TaskCreate(TaskBase):
    project_id: int
    assignee_id: int | None = None


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    assignee_id: int | None = None
    created_at: datetime
    updated_at: datetime
